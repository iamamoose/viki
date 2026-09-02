# VIKI

VIKI is a [Home Assistant](https://www.home-assistant.io/) voice
assistant with a tsundere personality. Fully local custom wake-word,
custom-trained voice, and opinions of her own.

[Watch the Video from **EMF Camp 2026**](https://media.ccc.de/v/emf2026-88-1-building-a-mostly-local-mildly-judgemental-home-assistant)

If you were at the talk: the [companion notes](docs/emf-talk-notes.md)
collect everything waved at on slides.

> 🚧 This repo is being reorganised — expect things to move around.

## The software pipeline:

We split Home Assistant's voice stack into four stages. The whole talk
was just replacing each one with something better (or at least
funnier). Each stage has its own page:

1. [Wake word](docs/wakeword.md): We train "hey viki" as a wake word
2. [Speech to text](docs/stt.md): We use Microsoft Azure STT and test handling of regional dialects
3. [Processing & personality](docs/personality.md): A mixture of automations and optional Gemini LLM
4. [Text to speech](docs/voice.md): We train a custom anime voice to use with Piper

## Hardware

The devices the talk build runs on are off-the-shelf ESP32 voice
satellites: a Home Assistant Voice PE, an M5Stack ATOM Echo, or the
AtomS3R "pyramid". They all run ESPHome and work out of the box, so we
just take over the bits we want to change. The cheapest is the ATOM
Echo, the "$13 voice assistant".

See [Hardware](docs/hardware.md) for each option and where to buy.

## Licence

[Apache-2.0](LICENSE)
