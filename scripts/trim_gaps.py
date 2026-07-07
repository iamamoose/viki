#!/usr/bin/env python3
"""
Punctuation-aware silence trimmer for IndexTTS2 output.

Collapses the spurious mid-utterance gaps (the standalone "▁" tokenization
pauses) WITHOUT flattening deliberate comma / full-stop pauses, and without
clipping word onsets or releases.

How it decides what's deliberate
--------------------------------
For each metadata.csv line we count the text's internal pause punctuation
(commas, semicolons, colons, dashes, ellipses, and any terminator with text
after it). That count, N, is how many real pauses the line should have. In
the audio we find every internal silence, PROTECT the N longest, and
COLLAPSE the rest to a floor. Leading/trailing silence is trimmed to a pad.

Edge preservation
-----------------
Energy-based detection tends to end a segment slightly early on quiet
releases (e.g. the "g" in "dog."), which clips the word. We expand every
detected speech segment by KEEP_MS on each side before cutting, so onsets
and releases are retained.

Honest caveat: this is a heuristic, not forced alignment. It assumes the
deliberate pauses are the longest silences in the clip. Spot-check outputs.

Requirements
------------
    python -m pip install pydub audioop-lts   # audioop-lts only needed on Py 3.13+
    # ffmpeg must be on PATH

Usage
-----
    python trim_gaps.py                       # ./metadata.csv, wavs in .
    python trim_gaps.py metadata.csv ./wavs ./trimmed
"""

import os
import sys

from pydub import AudioSegment
from pydub.silence import detect_nonsilent

# ---- tunables -------------------------------------------------------------
KEEP_MS         = 45     # margin kept around each speech segment (anti-clip)
FLOOR_MS        = 70     # spurious gaps collapsed to this
PAD_MS          = 60     # leading silence kept to this
TRAIL_PAD_MS    = 120    # trailing silence kept to this (protect final release)
PROTECT_CAP_MS  = 400    # protected pauses capped here (None = leave untouched)
MIN_GAP_MS      = 60     # silences shorter than this are ignored
SILENCE_MARGIN  = 16     # "silent" if below (clip mean dBFS - this)
DELIM           = "|"
# ---------------------------------------------------------------------------

PAUSE_CHARS = set(",，;；:：.。!！?？—…")


def internal_pause_count(text: str) -> int:
    text = text.strip()
    count = 0
    for i, ch in enumerate(text):
        if ch not in PAUSE_CHARS:
            continue
        if i > 0 and text[i - 1] in PAUSE_CHARS:
            continue  # collapse runs like "..." or "?!"
        if any(c.isalnum() for c in text[i + 1:]):
            count += 1
    return count


def trim_one(in_path: str, out_path: str, n_protect: int) -> dict:
    audio = AudioSegment.from_file(in_path)
    n = len(audio)
    thresh = audio.dBFS - SILENCE_MARGIN
    ns = detect_nonsilent(audio, min_silence_len=MIN_GAP_MS, silence_thresh=thresh)

    if not ns:
        audio.export(out_path, format="wav")
        return {"segments": 0, "internal_gaps": 0, "protected": 0, "collapsed": 0}

    # expand each speech segment by KEEP_MS so quiet onsets/releases survive
    segs = [[max(0, s - KEEP_MS), min(n, e + KEEP_MS)] for s, e in ns]

    # merge any segments that now overlap because of the expansion
    merged = [segs[0]]
    for s, e in segs[1:]:
        if s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    segs = merged

    # gaps between the (expanded) segments
    gaps = [(i, segs[i][0] - segs[i - 1][1]) for i in range(1, len(segs))]
    protected = {
        idx for idx, _ in sorted(gaps, key=lambda g: g[1], reverse=True)[:max(0, n_protect)]
    }

    out = audio[segs[0][0]:segs[0][1]]
    collapsed = 0
    for i in range(1, len(segs)):
        gap = segs[i][0] - segs[i - 1][1]
        if i in protected:
            keep = gap if PROTECT_CAP_MS is None else min(gap, PROTECT_CAP_MS)
        else:
            keep = min(gap, FLOOR_MS)
            if gap > FLOOR_MS:
                collapsed += 1
        out += AudioSegment.silent(duration=keep, frame_rate=audio.frame_rate)
        out += audio[segs[i][0]:segs[i][1]]

    out = (AudioSegment.silent(PAD_MS, audio.frame_rate)
           + out
           + AudioSegment.silent(TRAIL_PAD_MS, audio.frame_rate))
    out.export(out_path, format="wav")
    return {
        "segments": len(segs),
        "internal_gaps": len(gaps),
        "protected": len(protected),
        "collapsed": collapsed,
    }


def main():
    metadata = sys.argv[1] if len(sys.argv) > 1 else "metadata.csv"
    wav_dir  = sys.argv[2] if len(sys.argv) > 2 else "."
    out_dir  = sys.argv[3] if len(sys.argv) > 3 else "trimmed"
    os.makedirs(out_dir, exist_ok=True)

    total = collapsed_total = missing = 0
    with open(metadata, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            file_id, text = line.split(DELIM, 1)
            in_path = os.path.join(wav_dir, f"{file_id}.wav")
            if not os.path.isfile(in_path):
                print(f"  [skip] {in_path} not found")
                missing += 1
                continue

            n = internal_pause_count(text)
            out_path = os.path.join(out_dir, f"{file_id}.wav")
            stats = trim_one(in_path, out_path, n_protect=n)
            total += 1
            collapsed_total += stats["collapsed"]
            print(
                f"  [{file_id}] punct_pauses={n} "
                f"gaps={stats['internal_gaps']} kept={stats['protected']} "
                f"collapsed={stats['collapsed']}"
            )

    print(f"\nProcessed {total} files, collapsed {collapsed_total} spurious gaps, "
          f"{missing} missing. Output in {out_dir}/")


if __name__ == "__main__":
    main()
