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
                        Piper fine-tune from en_GB/alba
                                              │
                                en_GB-viki-medium.onnx
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

From the `en_GB/alba/medium` checkpoint — British and female already,
so there's less distance to travel than from the en_US default:

```
python -m piper_train \
  --dataset-dir <dojo>/training_folder/ \
  --accelerator gpu --devices 1 \
  --batch-size 5 \
  --validation-split 0.0 --num-test-examples 0 \
  --max_epochs 5180 \
  --resume_from_checkpoint <base checkpoint> \
  --checkpoint-epochs 5 \
  --precision 32 --quality medium
```

VIKI is epoch 5179. Alba's own checkpoint is epoch 4179, so that's about
1,000 epochs of fine-tuning on top — roughly 8 hours on a 3060. Starting
from a voice that's already close to your target buys you a lot; the
earlier en_US/ljspeech attempt needed 3,400 epochs and 26 hours to get
somewhere comparable.

Export with `piper_train.export_onnx`, copy `training_folder/config.json`
next to it as `<model>.onnx.json`, and set `dataset`, `length_scale`.

## Give her a mhm

She needs a noise to answer with, and it has to be cloned from *your*
reference clip or it'll sound like a stranger acknowledging you. Same
tool as the training set, just one line of text:

```python
wavs, sr = model.generate_voice_clone(
    text="Mhm?", language="English", voice_clone_prompt=prompt
)
```

Generate a few dozen. The spread between seeds is far wider than you'd
expect — ours ranged from 0.3 to 2 seconds across the same spelling —
and the first take is almost never the best. We ran 72 across six
spellings and twelve seeds.

Pick by measuring, not just by ear. Duration and pitch contour are what
decide whether it reads as an acknowledgement or a flat grunt; a rising
contour is the thing that makes it work. Then match its loudness to the
voice model's own output, or it'll sound oddly timid played straight
after a sentence.

The same method does a sigh, a sniff, an "ahem".

### Why it's a file and not TTS

Don't be tempted to have the voice say "mhm" instead. espeak, which
Piper uses to turn text into phonemes, doesn't recognise most spellings
of a hum and reads them out as letters:

```
mhm     ->  ,Em,eItS'Em      "em aitch em"
mhmm    ->  ,Em,eItS,Em'Em   "em aitch em em"
Mm      ->  ,Em'Em           "em em"
Hm      ->  ,eItS'Em         "aitch em"
```

Three spellings actually hum:

```
Hmm     ->  h'@m
Uh-huh  ->  'Vh'V
M-hmm   ->  'Emh@m           the letter M, then a hum
```

So `Hmm.` works if you want one generated live. Everything that looks
more like the noise you want gets spelled out. A recorded file sidesteps
it entirely.

Note the spelling we fed the *cloning* model was `Mhm?` — one espeak
would have spelled out, which doesn't matter because Qwen doesn't use
espeak.

## Things that cost us a day each

**en-GB silently trains nothing.** TextyMcSpeechy's `en-gb.conf` sets
`ESPEAK_LANGUAGE="en-gb"`, which `piper_phonemize` rejects — it only
accepts the regional variants, `en-gb-x-rp` and friends. Preprocessing
dies, but a zero-byte `dataset.jsonl` is written anyway, so training
starts, says `No training batches` and exits 0. Nothing mentions the
language. It just looks like it didn't work, which is why VIKI_ shipped
as en-US and needed the [tomato bodge](voice.md#scotland-tomato-dlc).

Set `ESPEAK_LANGUAGE="en-gb-x-rp"` and it trains fine. Patch submitted
upstream: [domesticatedviking/TextyMcSpeechy#68](https://github.com/domesticatedviking/TextyMcSpeechy/pull/68).

Confusingly the wrong value looks right — `espeak-ng --voices` does list
`en-gb`, exactly as the comment in that file tells you to check. Piper
bundles its own espeak-ng-data, which doesn't.

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
