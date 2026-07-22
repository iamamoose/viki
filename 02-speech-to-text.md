# 2. Speech-to-Text — is local good enough?

[← Wakeword](01-wakeword.md) · [Back to README](./README.md) · Next: [Processing →](03-processing.md)

---

By default Home Assistant gives you phrase-to-text (fine on low-end hardware, but limited to token-named phrases) and speech-to-text. We want to talk to VIKI_ more freely, so it's speech-to-text.

The default is faster-whisper in a container, with a choice of model. `tiny-int8` is the one recommended for a Pi 4; `base-int8` is more accurate and okay on a Pi 5.

You can also pay for the Home Assistant cloud subscription, which is a Microsoft speech service covering both STT and TTS. Do we need it? Two things to check: accuracy, then speed.

## Accuracy — the "what's that person saying?" quiz

| Phrase | tiny-int8 | base-int8 | azure |
|---|---|---|---|
| "Turn on the lights" | ✅ Turn on the lights | ✅ Turn on the lights | ✅ Turn on the lights |
| "Eleven minute timer" | ❌ A loving minute timer | ✅ 11 minute timer | ✅ 11 minute timer |
| "Boil the kettle" | ❌ Oil the kettle | ❌ Boil the cattle | ✅ Boil the kettle |

`tiny-int8` barely understands me, and doesn't get my Scottish wife at all. `base-int8` is closer but still trips on "boil the cattle". Azure gets it right. So the cloud's accurate. What about speed?

## Benchmark — *"What is the bedroom temperature?"*

| Engine | Time |
|---|---:|
| rpi5 (base-int8) | 1.7 s |
| rpi5 (tiny-int8) | 1.2 s |
| i7-6700 (base-int8) | 1.0 s |
| i7-6700 (tiny-int8) | 0.6 s |
| 🏆 **Microsoft / Azure STT** | **0.1 s** |

`tiny-int8` is much faster than `base-int8`, as you'd expect, but we need `base` for accuracy unless we go cloud, and 1.7 s on a Pi 5 is annoying when it's on top of everything else the pipeline has to do. The cloud wins here too.

## Self-hosting Microsoft STT (no full HA Cloud subscription)

You can run Azure Speech-to-Text as a Home Assistant add-on yourself, over the Wyoming protocol, without the rest of an HA Cloud subscription. I used hugobloem's Wyoming Microsoft STT:

- Add-on repository (add this under Settings → Add-ons → ⋮ → Repositories): <https://github.com/hugobloem/homeassistant-addons>
- The server project and full option reference: <https://github.com/hugobloem/wyoming-microsoft-stt>

Create the Azure Speech resource. You only do this once, and the same resource works for STT and TTS:

1. Sign in at <https://portal.azure.com> and create a Speech resource.
2. Pick a resource group, a region (I use `ukwest`), a name, and the Free F0 pricing tier.
3. From the resource's Keys and Endpoint page, copy a key and note the region.

Configure the add-on: install Wyoming Microsoft STT, set the subscription key, region (`ukwest`) and default language (`en-GB`), then start it. Add it under Settings → Devices & Services → Wyoming Protocol if it doesn't appear on its own, and select it as the Speech-to-Text engine in your voice pipeline.

Cost and free tier:
- The Free F0 tier gives 5 audio hours a month. Beyond that Azure charges about $0.36 an audio hour.
- Mine came to about 16 minutes over 24 days, under a minute a day, roughly 10% of the free allowance. Nowhere near the cap.
- I set a £1/month spend cap anyway, in case something changes or goes wrong.

### Privacy

Per Microsoft's policy at the time of speaking: for real-time speech-to-text, audio is processed only in server memory with nothing stored at rest, Microsoft doesn't retain the data customers provide, and doesn't use it to train AI.

> 📄 Microsoft's policy: [Data, privacy, and security for Speech to text](https://learn.microsoft.com/en-gb/azure/ai-foundry/responsible-ai/speech-service/speech-to-text/data-privacy-security) (Microsoft Learn). The wording is specific to real-time STT, which is what the HA voice pipeline uses. Batch transcription, which we don't use, stores things differently.

Free, fast, accurate and private. You just need an internet connection.

---

[← Wakeword](01-wakeword.md) · [Back to README](./README.md) · Next: [Processing →](03-processing.md)
