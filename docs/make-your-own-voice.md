# Make your own VIKI_ voice

[← Text-to-Speech](voice.md) · [Back to VIKI](../README.md)

---

How we built VIKI's voice, and the bits that wasted our time.

Nobody recorded anything. We described a voice in words, Qwen3-TTS
invented someone who sounds like that, we had it read 416 lines in that
voice, and trained Piper on the result.

```
description ──▶ Qwen3-TTS VoiceDesign ──▶ reference clip
                                              │
                            Qwen3-TTS cloning, 416 lines
                                              │
                                    ~22 minutes of audio
                                              │
                          Piper fine-tune from LJSpeech
                                              │
                                en_US-viki-medium.onnx
```

You need an NVIDIA GPU — we used a 12GB 3060 and training sits at about
10.5GB — plus [qwen-tts](https://github.com/Qwen/Qwen3-TTS) and
[TextyMcSpeechy](https://github.com/domesticatedviking/TextyMcSpeechy).

## 1. Invent a voice

[`gen_voices.py`](../scripts/gen_voices.py) turns a written description into candidates:

```
Accent: British English, southern England — distinctly British, never
American. Gender: female. Age: late teens to early 20s, youthful voice.
Pitch: higher female range, light, slightly breathy. Pace: quick and
fluent, clipped, no drawl. Emotion: playful, teasing, quietly confident.
Use case: a quick-witted AI home assistant, young and a little cheeky.
```

Generate a lot of them. Most are unusable, and the survivors sound more
alike than you'd expect — we measured 24 and they sat within 0.975–0.995
cosine of each other in speaker-embedding space, which is "same person"
territory. If none of them grab you, change the description rather than
generating more.

VIKI's clip was made before that prompt was last edited, so running it
now gives you a similar voice, not hers. [`reference.wav`](https://github.com/iamamoose/viki-assets/blob/main/voices/viki/reference.wav) is
the actual clip — use that if you want *this* voice.

## 2. Make the training set

[`gen_dataset.py`](../scripts/gen_dataset.py) has the reference read every line of
[`metadata.csv`](../scripts/metadata.csv):

```bash
python gen_dataset.py --voices viki --ref-dir <dir with viki.wav>
```

Leave it at 24kHz. Piper's tooling derives 22.05k and 16k from whatever
you give it, so resampling first loses quality twice. The script trims
the half-second of silence Qwen pads onto everything, and seeds each
line so you can regenerate any clip identically.

416 lines, about 22 minutes.

## 3. Train Piper

From the `en_US/ljspeech/medium` checkpoint:

```
python -m piper_train \
  --dataset-dir <dojo>/training_folder/ \
  --accelerator gpu --devices 1 \
  --batch-size 5 \
  --validation-split 0.0 --num-test-examples 0 \
  --max_epochs 5000 \
  --resume_from_checkpoint <base checkpoint> \
  --checkpoint-epochs 5 \
  --precision 32 --quality medium
```

VIKI is epoch 4999, roughly 3,400 epochs on the full dataset, about 26
hours on a 3060.

Export with `piper_train.export_onnx`, copy `training_folder/config.json`
next to it as `<model>.onnx.json`, and set `dataset`, `length_scale`.

## Things that cost us a day each

**More audio beats more epochs.** Our first attempt was 166 short lines
— 4.2 minutes — and it warbled after seven hours of training. Going to
416 longer lines (22 minutes) fixed what more epochs couldn't. If it
warbles, the dataset is too small.

**Asking for a quick delivery shrinks your dataset.** We asked for
"quick and clipped" and got it: the same script came out a third shorter
than a slower voice would have. Write longer sentences to compensate.
Ours average 11.3 words.

**Cloning has no emotion control.** `generate_voice_clone()` takes no
instruct argument — only VoiceDesign and CustomVoice do, and neither can
clone. Whatever mood is in the reference clip is the mood you get.

**Don't set `do_sample=False`.** Greedy decoding never emits an end
token. It ran to `max_new_tokens` and gave us 82 seconds of audio for a
two-second line. Keep sampling and fix the seed — that's reproducible
down to the byte.

---

[← Text-to-Speech](voice.md) · [Back to VIKI](../README.md)
