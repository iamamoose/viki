# scripts — the glue

The whole project is mostly joining existing pieces together with a few glue
scripts. These are the Python bits referenced in the talk, for training VIKI's
custom [Text-to-Speech](../docs/voice.md) voice. They run on a PC with a
modest GPU (an NVIDIA 3060 here), not on the Home Assistant server.

| File | Chain step | What it does |
|---|---|---|
| [`voice_design.py`](./voice_design.py) | 1 — design | Renders a sample WAV from a text prompt with **Qwen3-TTS-VoiceDesign**. No seed, so re-run until you like one, then keep the WAV. |
| [`metadata.csv`](./metadata.csv) | 3 — dataset | Pipe-delimited `id\|text` phrase list the trainer wants. |
| [`generate_samples.py`](./generate_samples.py) | 3 — dataset | Clones the designed voice into one WAV per `metadata.csv` line with **IndexTTS2**, dialed to *melancholic + calm*, fixed seed. |
| [`trim_gaps.py`](./trim_gaps.py) | 3 — dataset | Punctuation-aware pass that collapses IndexTTS's spurious mid-utterance gaps while protecting deliberate comma / full-stop pauses. |

Step 2 (clone + set expression) and step 4 (train with **TextyMcSpeechy**, then
install into the Piper add-on) are covered in
[voice.md](../docs/voice.md).

## metadata.csv

The actual ~180-line phrase list used to train VIKI: pangrams and
phonetically-loaded sentences for sound coverage, a pile of everyday questions
and interjections for natural prosody, and the Home-Assistant-specific lines
she actually says (170+, including the moose joke and the washing-machine nag).
The `id` is just the WAV filename, so the odd gap in the numbering doesn't
matter.

## Rough order

```bash
python voice_design.py                 # -> voice_design.wav (repeat until happy)
python generate_samples.py             # metadata.csv -> <id>.wav for each line
# ...listen to EVERY wav, regenerate any that don't match the text...
python trim_gaps.py metadata.csv . trimmed/   # collapse spurious gaps -> trimmed/
# ...then feed trimmed/ + metadata.csv to TextyMcSpeechy to train.
```
