# 4. Text-to-Speech — a custom voice for VIKI_

[← Processing](personality.md) · [Back to talk notes](emf-talk-notes.md)

---

Piper does local, phoneme-based TTS — fast enough even on a Pi. There are
heavier local models that do real-time TTS, but they want GPUs or fast
processors. We stick with Piper, which has a selection of voices across
languages.

You can also train your own. Some people have done the Enterprise
computer or Commander Data; we watch a lot of anime, so we wanted
something more endearing.

> 🎙️ Make your own VIKI, not ours. Honestly, you don't want our VIKI,
> you want *yours*. The whole recipe is published, so keep generating
> voices until you land on one you love, then train that one.

## The voice, and how to build your own

Everything lives in
**[viki-assets](https://github.com/iamamoose/viki-assets)**:

- the trained Piper voice, ready to drop into Home Assistant
- her non-speech noises, like the `mhm` she answers with
- the full recipe — scripts, phrase list, and the reference clip she was
  cloned from

Short version: describe a voice in words, let Qwen3-TTS invent someone
who sounds like that, have it read a few hundred lines, then fine-tune
Piper on the result. No human voice donor anywhere in the chain, which
is why we can licence her CC BY-SA.

## What changed since the talk

The EMF version used IndexTTS to clone the voice and set its expression,
and a smaller phrase list. It worked, but the phrase list was too short
and the result warbled — more audio turned out to matter far more than
more training.

The pipeline is now Qwen3-TTS end to end, with a phrase list about two
and a half times the size.

> 📻 The version as presented, unchanged: [EMF 2026
> notes](emf2026/voice.md).

---

[← Processing](personality.md) · [Back to talk notes](emf-talk-notes.md)
