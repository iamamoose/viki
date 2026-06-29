# 2. Speech-to-Text — is local good enough?

[← Wakeword](01-wakeword.md) · [Back to README](../README.md) · Next: [Processing →](03-processing.md)

---

By default Home Assistant offers **phrase-to-text** (great for low-end hardware, but limited to token-named phrases) and **speech-to-text**. Since we want to interact with Viki more freely, we use speech-to-text.

The default is **faster-whisper** in a container, with a choice of model — `tiny-int8` is recommended for a Pi 4.

## Benchmark — *"What is the bedroom temperature?"*

| Engine | Time |
|---|---|
| rpi5 (base-int8) | 1.7 s |
| rpi5 (tiny-int8) | 1.2 s |
| i7-6700 (base-int8) | 1.0 s |
| i7-6700 (tiny-int8) | 0.6 s |
| **Microsoft / Azure STT** | **0.1 s** |

`tiny-int8` is the default — quick but inaccurate, bad at even simple things. `base-int8` is better but not recommended below a Pi 5, and 1.7 s is annoying when it's *on top of* everything else the pipeline does. The cloud just makes things feel more responsive.

### Accuracy — the "what's that person saying?" quiz

| Phrase | tiny-int8 | base-int8 | azure |
|---|---|---|---|
| "Turn on the lights" | Turn on the lights | Turn on the lights | Turn on the lights |
| "Eleven minute timer" | A loving minute timer | 11 minute timer | 11 minute timer |
| "Boil the kettle" | Oil the kettle | Boil the cattle | Boil the kettle |

`tiny-int8` barely understands me, and not my (Scottish) wife at all. Azure gets it right.

## Self-hosting Microsoft STT (no full HA Cloud subscription)

You can run Azure Speech-to-Text as a Home Assistant add-on yourself, over the Wyoming protocol, without the rest of an HA Cloud subscription. The add-on I used is **hugobloem's Wyoming Microsoft STT**:

- Add-on repository (add this under **Settings → Add-ons → ⋮ → Repositories**): <https://github.com/hugobloem/homeassistant-addons>
- The server project / full option reference: <https://github.com/hugobloem/wyoming-microsoft-stt>
- A good end-to-end walkthrough (STT + TTS + wake word): <https://fixtse.com/blog/azure-tts-stt>

**Create the Azure Speech resource** (once — the same resource works for STT and TTS):

1. Sign in at <https://portal.azure.com> and create a **Speech** resource.
2. Pick a resource group, a **region** (I use `ukwest`), a name, and the **Free F0** pricing tier.
3. From the resource's **Keys and Endpoint** page, copy a **key** and note the **region**.

**Configure the add-on:** install *Wyoming Microsoft STT*, set the subscription **key**, **region** (`ukwest`), and default **language** (`en-GB`), then start it. Add it under **Settings → Devices & Services → Wyoming Protocol** if it doesn't appear automatically, and select it as the Speech-to-Text engine in your voice pipeline.

**Cost / free tier:**
- The Free F0 tier gives **5 audio hours/month**. Beyond that, Azure charges ~**$0.36/audio hour**.
- My usage: **~16 minutes over 24 days** — under a minute a day. Nowhere near the cap.
- Set a **£1/month spend cap** as insurance in case something changes or goes wrong.

### Privacy

Per Microsoft's policy *at time of speaking*: for real-time speech-to-text, audio is processed only in **server memory** with **nothing stored at rest**, and Microsoft **does not retain or store** the data customers provide.

> 📄 **Microsoft's policy:** [Data, privacy, and security for Speech to text](https://learn.microsoft.com/en-gb/azure/ai-foundry/responsible-ai/speech-service/speech-to-text/data-privacy-security) (Microsoft Learn). Note the wording is specific to **real-time** STT — which is what the HA voice pipeline uses. (Batch transcription, which we don't use, has different storage behaviour.)

Free, fast, accurate and private — the only catch is you need an internet connection.

## Links

| What | Where |
|---|---|
| Wyoming Microsoft STT — add-on repo | <https://github.com/hugobloem/homeassistant-addons> |
| Wyoming Microsoft STT — server / options | <https://github.com/hugobloem/wyoming-microsoft-stt> |
| Azure / TTS + STT walkthrough | <https://fixtse.com/blog/azure-tts-stt> |
| Azure portal (create Speech resource) | <https://portal.azure.com> |
| Microsoft STT data/privacy policy | [Microsoft Learn](https://learn.microsoft.com/en-gb/azure/ai-foundry/responsible-ai/speech-service/speech-to-text/data-privacy-security) |

---

[← Wakeword](01-wakeword.md) · [Back to README](../README.md) · Next: [Processing →](03-processing.md)
