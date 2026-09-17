# 4. Text-to-Speech — a custom voice for VIKI_

[← Processing](personality.md) · [Back to VIKI](../README.md)

---

Piper does local, phoneme-based TTS which is fast enough even on a
Raspberry PI. There are heavier local models that do real-time TTS,
but they want GPUs or fast processors. We stick with Piper.

We stick with Piper which comes with many voices but you can also
train your own.  Some people have done the Enterprise computer or
Commander Data; we watch a lot of anime, so we wanted something more
endearing.

## Using our VIKI_

The trained voice, her non-speech noises and install instructions are in
**[viki-assets](https://github.com/iamamoose/viki-assets)**.

- You need to put the two files (.onnx and .onnx.json) into the
/share/piper/ directory on your home assistant server (use Samba or
the File Editor add-on). In "applications" reload Piper, in "devices"
"Wyoming" reload Piper, and then you can select the new voice in
"Voice Assistants".

- Newer versions of Piper that have a Web-UI may be able to upload
voices from the GUI. It's worth a try first.

## Or make your own

Describe a voice in words, let Qwen3-TTS invent someone who sounds like
that, have it read a few hundred lines, then fine-tune Piper on the
result. 

> 🎛️ Full instructions, including the mistakes that cost us days:
> [Make your own VIKI_ voice](make-your-own-voice.md).

## Replace the "bing" with a "mhm"

Once you have a voice, swap that wake-acknowledgement bing for a custom
WAV. I made a `mhm` (which, I'm reliably informed, is also the noise my
wife makes when I ask her anything). Simple ESPHome substitution:

```yaml
substitutions:
  wake_word_triggered_sound_file: https://raw.githubusercontent.com/iamamoose/viki-assets/main/voices/viki/mhmm.wav
```

Rebuild, push, done.

That's the same shape as the stock Voice PE config, which points at a
GitHub raw URL too, so ours drops straight in. Swap it for your own
server if you'd rather not depend on GitHub. It's in the release zip as
well, alongside the voice, if you're grabbing that anyway.

This one is generated from VIKI_'s own voice, so she sounds like herself
acknowledging you.

---

## Tweaking pronunciations (Humph!)

When we first made VIKI_ we hit a bug in training and couldn't make a
en-GB voice, so we ended up with American versions of 'tomato' being
added to our shopping list.  We've since fixed that.

However because Piper runs in a container in Home Assistant we can't
give it any espeak rules to fix other words without forking and
maintaining our own container.  So we can do it with a hack instead.

Firstly, if you want to have automations have different pronunciations
you can feed Home Assistant the phonemes directly.

Generate IPA per accent on the command line:

```bash
$ espeak-ng -q --ipa -v en-us "tomato"
təmˈeɪɾoʊ

$ espeak-ng -q --ipa -v en-gb-x-rp "tomato"
təmˈɑːtəʊ

$ espeak-ng -q --ipa -v en-gb-scotland "tomato"
təmˈa:toː
```

Then wrap phonemes in double square brackets anywhere in a Home
Assistant response and they'll be spoken as-is:

```text
USA is [[təmˈeɪɾoʊ]]. UK is [[təmˈɑːtəʊ]]. Scotland is [[təmˈa:toː]].
```

You can also clone the whole voice and just edit the JSON from `en-gb-x-rp`
to `en-us` (or `en-gb-scotland`) for an instant English / American
/ Scottish VIKI_. The phonemes won't be perfect but it's close!

Secondly, espeak says "hmph" by spelling out the letters, and says
"baka" badly. We fix this by altering our [LLM system
prompt](personality.md#adding-an-llm--google-gemini) to rewrite them: no
need for baka, and "hmph" becomes "humf", which comes out as a
passable *HUMPH!*

---

## What changed since the talk

- The EMF version used IndexTTS to clone the voice and set its expression,
and a smaller phrase list. It worked, but the phrase list was a little
too short and IndexTTS created voices have license conditions.
The pipeline is now Qwen3-TTS end to end, with a phrase list about two
and a half times the size.

- She's also en-GB now rather than en-US, trained from `en_GB/alba` instead
of `en_US/ljspeech`, which is what fixed the pronunciation.

> 📻 The version as presented, unchanged: [EMF 2026
> notes](emf2026/voice.md).

---

[← Processing](personality.md) · [Back to VIKI](../README.md)
