# 4. Text-to-Speech — a custom voice for VIKI_

[← Processing](03-processing.md) · [Back to README](./README.md)

---

Piper does local, phoneme-based TTS — fast enough even on a Pi. There are heavier local models that do real-time TTS, but they want GPUs or fast processors. We stick with Piper, which has a selection of voices across languages.

You can also **train your own**. Some people have done the Enterprise computer or Commander Data — we watch a lot of anime, so we wanted something more endearing: a custom anime-style voice.

## The chain (runs backwards from what Piper needs)

> Piper needs phonemes ← train a model on hundreds of sample phrases ← in a cloned, expression-tweaked voice ← generated from a designed voice ← from a prompt (written by an LLM).

### Step 1 — Design the voice — Qwen3-TTS
**<https://github.com/QwenLM/Qwen3-TTS>**

Used to use ElevenLabs; Qwen3-TTS does the job now. Ask ChatGPT for a voice-design prompt ("a bright, expressive, light anime-style, gender-neutral voice…"), tweak it, then run a few lines of Python to render a sample WAV. Ran fine on a modest **NVIDIA 3060** — minutes, not hours.

It's a *voice-design* model: no seed, a different voice every run, so keep generating until you like one — **and keep the WAV**, you'll clone it next.

```python
import torch, soundfile as sf
from qwen_tts import Qwen3TTSModel

model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
    device_map="cuda:0", dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
)
wavs, sr = model.generate_voice_design(
    language="English",
    text="Oh, you're finally back. I already turned the lights on and "
         "started the kettle. Not because I was waiting or anything. Welcome Home.",
    instruct="Gender: gender-neutral. Age: early 20s. Accent: clear British "
             "English. Pitch: neutral mid-range, sitting between alto and tenor. "
             "Pace: brisk and lively. Emotion: sharp, witty, with a playful "
             "tsundere edge. Characteristics: bright, expressive, light and agile "
             "timbre, anime-style. Use case: quick-tempered AI home assistant.",
)
sf.write("voice_design.wav", wavs[0], sr)
```

### Step 2 — Clone + expression — IndexTTS2
**<https://github.com/index-tts/index-tts>**

Clones your designed voice and lets you dial the **expression**, which is great. "Super happy and enthusiastic" tires you out fast — I want competent, not exhausting — so I went **melancholic and calm**. Needs a modest GPU.

### Step 3 — Build the training dataset

Training needs a couple of hundred phrases + audio for each. There's a sample `metadata.csv` (pipe-delimited `id|text`); I added Home-Assistant-specific lines:

```text
1|The quick brown fox jumps over the lazy dog.
2|She sells seashells by the seashore.
3|How much wood would a woodchuck chuck?
...
171|Your kettle has boiled.
172|The outside temperature is 10 degrees.
173|Hello from Home Assistant.
174|I've turned on the kitchen kettle.
175|I've turned off the living room lights.
176|You have seven items on your shopping list.
```

A small Python script generates all ~176 WAVs via IndexTTS in a few minutes.

> ⚠️ **You must listen to every one.** If the audio doesn't match the text, training fails — and that takes far longer than generating them. Two regenerated wrong the first time. IndexTTS also sometimes leaves a gap at the start of a sentence that turns into. Strange. Gaps. In your. Output. — a second tiny Python script trims those.

### Step 4 — Train + install — TextyMcSpeechy
**<https://github.com/domesticatedviking/TextyMcSpeechy>**

Ships a container + scripts that do the heavy lifting. Feed it the dataset and it trains, getting better over time — you can listen as it goes. On my PC there was little benefit past **~6 hours**. You end up with an `.onnx` + `.json`, **under 100 MB**.

Installing it into the Piper add-on has a few exact requirements (see the [official Piper add-on docs](https://github.com/home-assistant/addons/blob/master/piper/DOCS.md) and TextyMcSpeechy's [HA OS guide](https://github.com/domesticatedviking/TextyMcSpeechy/blob/main/docs/using_custom_voices_in_home_assistant_os.md)):

1. **Name the files** to Piper's scheme `<language>_<REGION>-<name>-<quality>` (quality is one of `x_low`, `low`, `medium`, `high`) — e.g. `en_US-viki-medium.onnx` and `en_US-viki-medium.onnx.json`. The two names must match exactly.
2. **Edit the `dataset` field** inside the `.onnx.json` to match that name, or it shows up wrong:

   ```jsonc
   {
     "dataset": "en_US-viki-medium",
     "audio": { "sample_rate": 22050, "quality": "Medium" },
     "espeak": { "voice": "en-us" },
     ...
   }
   ```
3. **Drop both files in `/share/piper/`** (create the folder if it doesn't exist). On HAOS the web UI can't write there — use the **FTP**, **Samba**, or **SSH** add-on to upload.
4. **Restart the Piper add-on** *and* **reload the Wyoming Protocol integration** — otherwise neither picks up the new model.

```bash
# After renaming + editing the dataset field, upload to:
/share/piper/en_US-viki-medium.onnx
/share/piper/en_US-viki-medium.onnx.json
# Then: restart Piper add-on, and reload Settings → Devices & Services → Wyoming Protocol
```

> ⚠️ **Where the voice appears:** due to how the Piper add-on builds its list, your custom voice will **not** show in *Settings → Add-ons → Piper → Configuration* dropdown. It only appears under **Settings → Voice assistants** when you create/edit an assistant using Piper as the TTS engine — use the **Try voice** button there to test it. (Known limitation, [issue #3914](https://github.com/home-assistant/addons/issues/3914).)

You don't have to pick just one voice — different speakers (or whoever's home) can use different voices, and you can set up different pipelines too.

> ⚠️ I couldn't get **en-GB** to train properly, so the shipped voice is **en-US** — which is why she says "gare-aaj" not "garage" and adds American tomatoes to the shopping list. The fix is the [Scotland Tomato DLC](#scotland-tomato-dlc) below.

## Replace the "bing" with a "mhm"

Once you have a voice, swap that wake-acknowledgement bing for a custom WAV. I made a `mhm` (which, I'm reliably informed, is also the noise my wife makes when I ask her anything). Simple ESPHome substitution:

```yaml
substitutions:
  wake_word_triggered_sound_file: https://esoom.com/viki/mhm.flac
```

Rebuild, push, done.

---

## Scotland Tomato DLC

The US voice mispronounces things. The grapheme→phoneme step is **espeak**, but it runs *inside* the Piper container — and I'm trying not to fork a container. The bodge: feed Home Assistant the phonemes directly.

Generate IPA per accent on the command line:

```bash
$ espeak-ng -q --ipa -v en-us "tomato"
təmˈeɪɾoʊ

$ espeak-ng -q --ipa -v en-gb-x-rp "tomato"
təmˈɑːtəʊ

$ espeak-ng -q --ipa -v en-gb-scotland "tomato"
təmˈa:toː
```

Then wrap phonemes in **double square brackets** anywhere in a Home Assistant response and they'll be spoken as-is:

```text
USA is [[təmˈeɪɾoʊ]]. UK is [[təmˈɑːtəʊ]]. Scotland is [[təmˈa:toː]].
```

You can also clone the whole voice and just edit the JSON from `en-us` to `en-gb-x-rp` (or `en-gb-scotland`) for an instant English / American / Scottish Viki. The phonemes won't be perfect — you'd have to train with rolling R's etc. — but it's close.

### The HUMF fix

espeak says "hmph" and "baka" badly. Rather than fork the container to add custom rules for them, the [LLM system prompt](03-processing.md#adding-an-llm--google-gemini) rewrites them: no need for baka, and **"hmph" → "humf"**, which comes out as a passable *HUMPH!*

## Links

| What | Where |
|---|---|
| Qwen3-TTS — voice design | <https://github.com/QwenLM/Qwen3-TTS> |
| IndexTTS2 — voice cloning + expression | <https://github.com/index-tts/index-tts> |
| TextyMcSpeechy — Piper training | <https://github.com/domesticatedviking/TextyMcSpeechy> |
| Piper add-on docs (naming + `/share/piper`) | <https://github.com/home-assistant/addons/blob/master/piper/DOCS.md> |

---

[← Processing](03-processing.md) · [Back to README](../README.md)
