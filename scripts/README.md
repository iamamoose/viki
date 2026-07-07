# scripts — the glue

The whole project is mostly joining existing pieces together with a few glue
scripts. These are the Python bits referenced in the talk, for training VIKI's
custom [Text-to-Speech](../04-text-to-speech.md) voice. They run on a PC with a
modest GPU (an NVIDIA 3060 here), not on the Home Assistant server.

| File | Chain step | What it does |
|---|---|---|
| [`voice_design.py`](./voice_design.py) | 1 — design | Renders a sample WAV from a text prompt with **Qwen3-TTS-VoiceDesign**. No seed, so re-run until you like one, then keep the WAV. |
| [`metadata.csv`](./metadata.csv) | 3 — dataset | Pipe-delimited `id\|text` phrase list the trainer wants. |
| [`generate_samples.py`](./generate_samples.py) | 3 — dataset | Clones the designed voice into one WAV per `metadata.csv` line with **IndexTTS2**, dialed to *melancholic + calm*, fixed seed. |
| [`trim_gaps.py`](./trim_gaps.py) | 3 — dataset | Punctuation-aware pass that collapses IndexTTS's spurious mid-utterance gaps while protecting deliberate comma / full-stop pauses. |

Step 2 (clone + set expression) and step 4 (train with **TextyMcSpeechy**, then
install into the Piper add-on) are covered in
[04-text-to-speech.md](../04-text-to-speech.md).

## metadata.csv

This is a **starter set**, not the exact file used for the shipped voice: the
nine pangrams from the slide, a run of phonetically-balanced Harvard sentences
(public domain), and the Home-Assistant-specific lines VIKI actually says
(numbered 170+ to match the talk). Grow it to ~170–200 lines — more balanced
coverage of sounds gives a better model. The `id` becomes the WAV filename, so
gaps in the numbering are fine.

## Rough order

```bash
python voice_design.py                 # -> voice_design.wav (repeat until happy)
python generate_samples.py             # metadata.csv -> <id>.wav for each line
# ...listen to EVERY wav, regenerate any that don't match the text...
python trim_gaps.py metadata.csv . trimmed/   # collapse spurious gaps -> trimmed/
# ...then feed trimmed/ + metadata.csv to TextyMcSpeechy to train.
```
