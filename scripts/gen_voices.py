import os
import sys
import time

import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

N = int(sys.argv[1]) if len(sys.argv) > 1 else 50
OUTDIR = "voices"

TEXT = "Oh, you're finally back. I already turned the lights on and started the kettle. Not because I was waiting or anything.  Welcome Home."
#INSTRUCT = "Gender: Female. Age: early 20s. Accent: clear UK British English. Pitch: neutral mid-range, sitting between alto and tenor. Pace: brisk and lively. Emotion: sharp, witty, with a playful tsundere edge. Characteristics: bright, expressive, competent, light and agile timbre, anime-style. Use case: quick-tempered AI home assistant."
INSTRUCT="Accent: British English, southern England — distinctly British, never American. Gender: female. Age: late teens to early 20s, youthful voice. Pitch: higher female range, light, slightly breathy. Pace: quick and fluent, clipped, no drawl. Emotion: playful, teasing, quietly confident. Use case: a quick-witted AI home assistant, young and a little cheeky."

os.makedirs(OUTDIR, exist_ok=True)

model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
    device_map="cuda:0",
    dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
)

start = time.time()
for i in range(1, N + 1):
    path = os.path.join(OUTDIR, f"voice_{i:03d}.wav")
    if os.path.exists(path):
        print(f"[{i}/{N}] skip (exists) {path}", flush=True)
        continue
    # seed per-take so a voice you pick can be regenerated later
    torch.manual_seed(i)
    t0 = time.time()
    try:
        wavs, sr = model.generate_voice_design(
            text=TEXT, language="English", instruct=INSTRUCT
        )
    except Exception as e:
        print(f"[{i}/{N}] FAILED: {type(e).__name__}: {e}", flush=True)
        continue
    sf.write(path, wavs[0], sr)
    print(f"[{i}/{N}] {path}  seed={i}  {time.time() - t0:.1f}s", flush=True)

print(f"done in {time.time() - start:.0f}s -> {OUTDIR}/", flush=True)
