# VIKI

Notes to accompany the **EMF Camp 2026 talk** on building VIKI, a
[Home Assistant](https://www.home-assistant.io/) voice assistant with
a tsundere personality. Fully local custom wake-word, custom-trained
voice, and opinions of her own.

[Watch the Video](https://media.ccc.de/v/emf2026-88-1-building-a-mostly-local-mildly-judgemental-home-assistant)

> 🚧 This repo is being reorganised — expect things to move around.

## The pipeline:

We split Home Assistant's voice stack into four stages. The whole talk
was just replacing each one with something better (or at least
funnier). Each stage has its own page:

1. [Wake word](docs/wakeword.md): We train "hey viki"
2. [Speech to text](docs/stt.md): We use Microsoft Azure STT and test handling of regional dialects
3. [Processing & personality](docs/personality.md): A mixture of automations and optional Gemini LLM
4. [Text to speech](docs/voice.md): We train a custom anime voice to use with Piper

## Licence

[Apache-2.0](LICENSE)
