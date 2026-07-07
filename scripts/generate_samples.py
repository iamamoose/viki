#!/usr/bin/env python3
"""
Step 3 of the custom-voice chain: build the TRAINING DATASET.

Reads metadata.csv (pipe-delimited `id|text`, the file the trainer wants) and,
for every line, clones the designed voice from step 1 into a spoken WAV using
IndexTTS2 (https://github.com/index-tts/index-tts). Generates all ~176 WAVs in
a few minutes on a modest GPU.

Two settings do the heavy lifting for clean output — no separate trimming pass
needed:
  * interval_silence=0             kills the gaps IndexTTS leaves between segments
  * max_text_tokens_per_segment=200 stops it splitting short lines at all
A fixed seed keeps runs reproducible, and emo_vector sets the expression: a
touch of melancholic + calm, so VIKI sounds composed rather than exhausting.

    ⚠️ Still listen to every clip afterwards. If the audio doesn't match the
    text, training silently fails — far slower to discover than to just
    regenerate the stragglers.

    pip install torch numpy transformers
    # plus index-tts per its repo instructions (checkpoints in ./checkpoints)
"""

import random, numpy as np, torch
from transformers import set_seed
from indextts.infer_v2 import IndexTTS2

metadata_path = "metadata.csv"
# The reference WAV from voice_design.py — the designed voice we're cloning.
speaker_prompt = "voice_design.wav"

# IndexTTS2 emotion vector, one weight per emotion:
#   [happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]
emo_vector = [0, 0, 0, 0, 0, .1, 0, .5]

tts = IndexTTS2(
    cfg_path="checkpoints/config.yaml", model_dir="checkpoints",
    use_fp16=False, use_cuda_kernel=False, use_deepspeed=False
)

with open(metadata_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        file_id, text = line.split("|", 1)
        output_file = f"{file_id}.wav"
        print(f"Generating {output_file}...")
        set_seed(4242)
        tts.infer(
            spk_audio_prompt=speaker_prompt,
            text=text,
            output_path=output_file,
            verbose=True,
            interval_silence=0,              # <- kills the inter-segment gaps
            max_text_tokens_per_segment=200, # <- fewer/no splits on short lines
            emo_vector=emo_vector, use_random=False,
            do_sample=False
        )
