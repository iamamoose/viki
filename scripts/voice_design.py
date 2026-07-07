#!/usr/bin/env python3
"""
Step 1 of the custom-voice chain: DESIGN a voice from a text prompt.

Uses Qwen3-TTS-VoiceDesign (https://github.com/QwenLM/Qwen3-TTS) to render a
sample WAV from a natural-language voice description. This is a *voice-design*
model: there is no seed, so you get a different voice every run — keep running
until you like one, and KEEP THE WAV, you clone it in step 2 (see
generate_samples.py / IndexTTS2).

Ran fine on a modest NVIDIA 3060 — minutes, not hours.

    pip install torch soundfile
    # plus the qwen_tts package per the Qwen3-TTS repo instructions
"""

import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

# The line VIKI says while you audition voices. Pick text with a bit of the
# personality in it so you can hear whether the voice fits the character.
SAMPLE_TEXT = (
    "Oh, you're finally back. I already turned the lights on and "
    "started the kettle. Not because I was waiting or anything. Welcome Home."
)

# The design prompt. Written to suit this model — more verbose than the
# one-line brief ("a bright, expressive, light anime-style, gender-neutral
# voice") you'd hand to an LLM to draft it.
INSTRUCT = (
    "Gender: gender-neutral. Age: early 20s. Accent: clear British English. "
    "Pitch: neutral mid-range, sitting between alto and tenor. "
    "Pace: brisk and lively. Emotion: sharp, witty, with a playful tsundere "
    "edge. Characteristics: bright, expressive, light and agile timbre, "
    "anime-style. Use case: quick-tempered AI home assistant."
)


def main() -> None:
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
        device_map="cuda:0",
        dtype=torch.bfloat16,
        attn_implementation="flash_attention_2",
    )
    wavs, sr = model.generate_voice_design(
        language="English",
        text=SAMPLE_TEXT,
        instruct=INSTRUCT,
    )
    sf.write("voice_design.wav", wavs[0], sr)
    print("Wrote voice_design.wav — have a listen; re-run until you like one.")


if __name__ == "__main__":
    main()
