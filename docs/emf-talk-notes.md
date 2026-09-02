# Meet VIKI_: a mostly-local, mildly judgemental voice assistant

> Companion notes for the Electromagnetic Fields July 2026 talk *"Building a mostly-local, mildly judgemental home assistant (aka VIKI_'s origin story)"*. [Watch the Video](https://media.ccc.de/v/emf2026-88-1-building-a-mostly-local-mildly-judgemental-home-assistant)

This is the story (and the links, configs and bodges) behind replacing my Home Assistant plus Alexa setup with a custom-voiced, slightly tsundere Home Assistant voice personality. Kept local and cheap where possible, without local LLMs.

If you were in the room: thanks for coming. Everything I waved at on slides is collected here so you can actually build your own, including the few [glue Python scripts](../scripts/) that hold it all together. Questions → **mark@esoom.com**.

A few of the samples didn't play on stage, and it turns out these were ones that I saved in 22kHz format. While they play through the speakers and through my HDMI Amp just fine, the HDMI sink used on stage didn't support that format, and a known issue with the Macbook means rather than resample and send a working sample, it just gets dropped.  

---

## The pipeline

We split Home Assistant's voice stack into four stages. The whole talk was just replacing each one with something better (or at least funnier). Each stage has its own page:

| Stage | Default | VIKI_ June 2026 | Page |
|---|---|---|---|
| 🔔 **Wakeword** | microWakeWord (ESPHome) | Trained my own `"hey_viki"` | [./wakeword.md](./wakeword.md) |
| 🗣️ **Speech-to-Text** | faster-whisper (tiny-int8) | Switched to Azure STT (Microsoft) | [./stt.md](./stt.md) |
| 🧠 **Processing** | HA intents | Personality automations + optional Gemini LLM | [./personality.md](./personality.md) |
| 🔊 **Text-to-Speech** | Piper (default voice) | Piper (Trained a custom anime `viki` voice) | [./voice.md](./voice.md) |

The hardware is the easy part: see [Hardware](./hardware.md) for the voice satellites and where to buy them.

Where it lands: mostly local, no local LLM, about £2 a month. Microsoft for STT is an easy win, being free, fast, accurate and private. A cloud LLM isn't essential and carries privacy trade-offs, but only the bits that can't be handled locally go to Google, for a couple of quid a month. I can live with that.

Character arc: VIKI_ started tsundere (cold, prickly — *"I-it's not like I wanted to help you"*), and I'm experimenting with deredere (warmer, more helpful, a one-word prompt change). The trade-off is that deredere keeps inventing pet names (sweetie, poppet), but at least they're for everyone. LLM sessions are short and she doesn't remember across them; this is a fun voice assistant, not a companion.

*Built by joining a lot of existing pieces together. I didn't find anything else that went quite this far. Questions welcome mark@esoom.com.*


---

