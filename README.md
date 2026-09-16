# VIKI_

VIKI_ is a [Home Assistant](https://www.home-assistant.io/) voice
assistant with a tsundere personality. Fully local custom wake-word,
custom-trained voice, and opinions of her own.

[Watch the Video from **EMF Camp 2026**](https://media.ccc.de/v/emf2026-88-1-building-a-mostly-local-mildly-judgemental-home-assistant)

If you were at the talk: the [companion notes](docs/emf2026/emf-talk-notes.md)
collect everything I waved at on slides.

## Software

We split Home Assistant's voice stack into four stages. The whole talk
was just replacing each one with something better (or at least
funnier). Each stage has its own page:

1. [Wake word](docs/wakeword.md): We create "hey viki" as a wake word
2. [Speech to text](docs/stt.md): We use Microsoft Azure STT and test handling of regional dialects
3. [Processing & personality](docs/personality.md): A mixture of automations and optional Gemini LLM
4. [Text to speech](docs/voice.md): We create a custom anime voice to use with Piper.

## Hardware

The devices the EMF Camp talk build runs on are off-the-shelf ESP32 voice
satellites running ESPHome: a Home Assistant Voice PE, an M5Stack ATOM Echo, or the
AtomS3R "pyramid". See [Hardware](docs/hardware.md) for each option and where to buy.

## Licence

[Apache-2.0](LICENSE)
