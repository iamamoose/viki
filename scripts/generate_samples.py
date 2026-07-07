#!/usr/bin/env python3
"""
Step 3 of the custom-voice chain: build the TRAINING DATASET.

Reads metadata.csv (pipe-delimited `id|text`, the same file the trainer wants)
and, for every line, clones the designed voice from step 1 into a spoken WAV
using IndexTTS2 (https://github.com/index-tts/index-tts). IndexTTS2 lets you
dial the expression — we go melancholic + calm, because "super happy and
enthusiastic" tires you out fast; we want competent, not exhausting.

Generates all ~176 WAVs in a few minutes on a modest GPU.

    ⚠️ You MUST listen to every one afterwards. If the audio doesn't match the
    text, training silently fails — and that takes far longer to discover than
    generating them did. IndexTTS also sometimes leaves a gap at the start that
    turns into. Strange. Gaps. In your. Output. — run trim_silence.py after
    this to clean those up.

    pip install soundfile
    # plus index-tts per its repo instructions (checkpoints in ./checkpoints)
"""

import csv
from pathlib import Path

from indextts.infer_v2 import IndexTTS2

# The reference WAV produced by voice_design.py — the voice we're cloning.
VOICE_PROMPT = "voice_design.wav"
METADATA = Path("metadata.csv")
OUT_DIR = Path("wavs")

# IndexTTS2 emotion vector, one weight per emotion. Order:
#   [happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]
# Melancholic + calm gives VIKI a composed, faintly weary delivery.
EMO_VECTOR = [0.0, 0.0, 0.0, 0.0, 0.0, 0.55, 0.0, 0.45]


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    tts = IndexTTS2(
        cfg_path="checkpoints/config.yaml",
        model_dir="checkpoints",
        use_fp16=True,
    )

    with METADATA.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh, delimiter="|"))

    for idx, row in enumerate(rows, start=1):
        if not row or row[0].startswith("#"):
            continue
        clip_id, text = row[0].strip(), row[1].strip()
        out_path = OUT_DIR / f"{clip_id}.wav"
        print(f"[{idx}/{len(rows)}] {clip_id}: {text}")
        tts.infer(
            spk_audio_prompt=VOICE_PROMPT,
            text=text,
            output_path=str(out_path),
            emo_vector=EMO_VECTOR,
            emo_alpha=0.8,
        )

    print(f"\nDone. Now LISTEN to every file in {OUT_DIR}/ before training.")


if __name__ == "__main__":
    main()
