# Getting VIKI_ onto a Home Assistant Voice PE

[← Back to VIKI](../README.md) · [Hardware](hardware.md)

---

The four stage guides each explain one piece. This is the order to do them in
for one specific device, a [Home Assistant Voice
PE](https://www.home-assistant.io/voice-pe/).

## 0. Get it working as itself first

Set the Voice PE up with Home Assistant's own instructions: [Voice PE
docs](https://voice-pe.home-assistant.io/), or the [Assist
getting-started guide](https://www.home-assistant.io/voice_control/).

Get it onboarded and answering to "okay nabu" in its stock voice
before you change anything. Everything below replaces one piece at a
time, and each piece is much easier to debug when you know the rest
already worked.

## 1. Her voice

Start here rather than with the wake word. It is the biggest change to how she
feels, it needs no firmware work, and it is the easiest to undo.

Two files into `/share/piper/` on your home assistant server, reload
Piper App, reload Piper in Wyoming device, pick the voice in your
pipeline: **[Text-to-speech →](voice.md)**

At this point she is still "okay nabu", but she sounds like herself.

## 2. Take control in ESPHome

The next two steps both change the firmware.  Voice PE is an ESP32
running ESPHome, and adopting it in the ESPHome add-on lets you
compile and install over the air from the browser. From then on the
firmware is yours: you get to change it, and you also own keeping it
current, because it no longer takes the official updates.

## 3. Her wake word

Stock firmware offers Hey Jarvis, Hey Mycroft and Okay Nabu, and there is no way
to add a fourth from the Home Assistant UI — it is a `micro_wake_word:` block and
a reflash.

The YAML, the raw-URL trick so ESPHome fetches the model straight from
viki-assets, and the live sensitivity picker: **[Wake word →](wakeword.md)**

`hey_viki` is tuned to us. If it will not hear you, drop the cutoff
before assuming it is broken — and if that is not enough, [make your
own](make-your-own-wakeword.md).

## 4. Her "mhm"

Swap the wake-acknowledgement bing for her own noise. It is an ESPHome
substitution, so you are already in the right place from step 2 — the WAV is in
[viki-assets](https://github.com/iamamoose/viki-assets) beside the voice.

Covered at the end of **[Text-to-speech →](voice.md)**.

## 5. Speech to text

Nothing from here on is device-specific — it is all on the Home
Assistant side, so it applies whatever you are talking to. And there is
nothing VIKI_-specific in this step at all: she just understands you
better, and faster.

faster-whisper runs locally and free, and is where to start. Azure STT
is quicker and more accurate if you do not mind the cloud, and the free
tier is plenty: **[Speech-to-text →](stt.md)**

## 6. Her personality — automations and notifications

The step that makes her her, and it is fully local. Conversation
triggers catch the things you ask often and answer with character
instead of "Turned on the kettle". Notifications let her start the
conversation — the doorbell, or the washing machine she nags you about
until you empty it: **[Processing & personality →](personality.md)**

A Voice PE with her voice and wake word but a stock pipeline sounds
like VIKI_ and does not act like her. Skip this one and you'll wonder
why she is polite.

## 7. Adding an LLM

Optional, and last for a reason: the automations already cover what you
ask most. An LLM covers everything else, and can do web lookups. We use
Google Gemini: **[Adding an LLM →](personality.md#adding-an-llm--google-gemini)**
as it's fast, cheap, and can act tsundere with the right prompt!

---

[← Back to VIKI](../README.md) · [Hardware](hardware.md)
