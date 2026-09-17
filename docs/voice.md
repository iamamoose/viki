# 4. Text-to-Speech — a custom voice for VIKI_

[← Processing](personality.md) · [Back to VIKI](../README.md)

---

Piper does local, phoneme-based TTS which is fast enough even on a
Raspberry PI. There are
heavier local models that do real-time TTS, but they want GPUs or fast
processors. We stick with Piper.

We stick with Piper which comes with many voices but you can also train your own.
Some people have done the Enterprise computer or Commander Data; we watch a lot of anime, so we wanted something more endearing.

## Using our VIKI_

The trained voice, her non-speech noises and install instructions are in
**[viki-assets](https://github.com/iamamoose/viki-assets)**. Download the
release, drop two files into the Piper add-on, done.

## Or make your own

Describe a voice in words, let Qwen3-TTS invent someone who sounds like
that, have it read a few hundred lines, then fine-tune Piper on the
result. No human voice donor anywhere in the chain, which is why we can
licence ours CC BY-SA — and yours is yours.

> 🎛️ Full recipe, including the mistakes that cost us days:
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

## Scotland Tomato DLC

The US voice mispronounces things. The grapheme→phoneme step is espeak,
but it runs *inside* the Piper container, and I'm trying not to fork a
container. The bodge: feed Home Assistant the phonemes directly.

> 🔧 She used to be en-US, and this section existed because of it.
> TextyMcSpeechy's en-GB config sets an espeak voice piper rejects, so
> en-GB training silently did nothing — see [Make your own VIKI_
> voice](make-your-own-voice.md) and [TextyMcSpeechy#68](https://github.com/domesticatedviking/TextyMcSpeechy/pull/68). With
> `en-gb-x-rp` she trains properly and says "garage" and "tomato"
> correctly on her own, so this is now a party trick rather than a fix.

Still the trick for doing accents deliberately, mind.

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

You can also clone the whole voice and just edit the JSON from `en-us`
to `en-gb-x-rp` (or `en-gb-scotland`) for an instant English / American
/ Scottish VIKI_. The phonemes won't be perfect — you'd have to train
with rolling R's etc. — but it's close.

### The HUMF fix

espeak says "hmph" and "baka" badly. Rather than fork the container to
add custom rules for them, the [LLM system
prompt](personality.md#adding-an-llm--google-gemini) rewrites them: no
need for baka, and "hmph" becomes "humf", which comes out as a passable
*HUMPH!*

---

## What changed since the talk

The EMF version used IndexTTS to clone the voice and set its expression,
and a smaller phrase list. It worked, but the phrase list was a little
too short and IndexTTS created voices have license conditions.

The pipeline is now Qwen3-TTS end to end, with a phrase list about two
and a half times the size.

She's also en-GB now rather than en-US, trained from `en_GB/alba` instead
of `en_US/ljspeech`, which is what fixed the pronunciation.

> 📻 The version as presented, unchanged: [EMF 2026
> notes](emf2026/voice.md).

---

[← Processing](personality.md) · [Back to VIKI](../README.md)
