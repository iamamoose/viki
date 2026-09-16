# scripts

Glue scripts, kept by the version of VIKI_ they belong to.

The current voice pipeline is Qwen3-TTS end to end:

| File | What it does |
|---|---|
| [`gen_voices.py`](gen_voices.py) | Invents candidate voices from a written description. Seeded, so a voice you like can be regenerated. |
| [`metadata.csv`](metadata.csv) | The 416-line phrase list, pipe-delimited `id\|text`. |
| [`gen_dataset.py`](gen_dataset.py) | Has a reference clip read every line, trims the silence, and writes a training set. |

Training itself is TextyMcSpeechy — see [voice.md](../docs/voice.md) and the
full walkthrough in
[viki-assets](https://github.com/iamamoose/viki-assets/blob/main/docs/voice.md).

```bash
python gen_voices.py                              # -> candidates, pick one
python gen_dataset.py --voices viki --ref-dir <dir with viki.wav>
# ...then train with TextyMcSpeechy
```

The reference clip VIKI_ was cloned from is
[`voices/viki/reference.wav`](https://github.com/iamamoose/viki-assets/blob/main/voices/viki/reference.wav)
in viki-assets — it's audio, so it lives with the assets. Rename it to
`viki.wav` for `--ref-dir`, or pass whatever name matches `--voices`.

## Older versions

- [`emf2026/`](emf2026/) — the scripts as presented at EMF Camp 2026,
  built around IndexTTS. Frozen.
