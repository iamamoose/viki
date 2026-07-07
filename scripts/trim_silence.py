#!/usr/bin/env python3
"""
The "second tiny Python script" from the talk.

IndexTTS2 sometimes leaves a gap of near-silence at the start (and occasionally
the end) of a generated clip. Left in, those gaps turn into. Strange. Gaps. In
your. Output. — and they also hurt training. This walks a directory of WAVs and
trims leading/trailing silence in place using a simple amplitude threshold.

    pip install soundfile numpy

    python trim_silence.py wavs/            # trim in place
    python trim_silence.py wavs/ --out trimmed/   # write to a new dir
"""

import argparse
from pathlib import Path

import numpy as np
import soundfile as sf

# Anything quieter than this (relative to full scale) counts as silence.
THRESHOLD = 0.01
# Leave a little breathing room so we don't clip the first/last phoneme.
PAD_SECONDS = 0.02


def trim(data: np.ndarray, sr: int) -> np.ndarray:
    mono = data if data.ndim == 1 else data.mean(axis=1)
    loud = np.where(np.abs(mono) > THRESHOLD)[0]
    if loud.size == 0:
        return data  # entirely silent — leave it for you to inspect/regenerate
    pad = int(PAD_SECONDS * sr)
    start = max(0, loud[0] - pad)
    end = min(len(mono), loud[-1] + pad)
    return data[start:end]


def main() -> None:
    ap = argparse.ArgumentParser(description="Trim silence from WAV clips.")
    ap.add_argument("directory", type=Path, help="folder of .wav files")
    ap.add_argument("--out", type=Path, help="output folder (default: in place)")
    args = ap.parse_args()

    out_dir = args.out or args.directory
    out_dir.mkdir(parents=True, exist_ok=True)

    for wav in sorted(args.directory.glob("*.wav")):
        data, sr = sf.read(wav)
        before = len(data)
        data = trim(data, sr)
        sf.write(out_dir / wav.name, data, sr)
        print(f"{wav.name}: {before} -> {len(data)} samples")


if __name__ == "__main__":
    main()
