# 1. Wakeword — train your own

[← Back to talk notes](emf-talk-notes.md) · Next: [Speech-to-Text →](stt.md)

---

Home Assistant ships with three wakewords: "Hey Mycroft", "Hey Jarvis" and "Okay Nabu". There aren't more because a good wakeword model is hard work. It has to fire for every accent while ignoring the telly, and keeping the false positives down to something sensible takes a lot of tuning. The model, microWakeWord, runs on the ESP32 itself and listens all the time. But you can train your own, given a set of recordings of the wake word and some background noise to train against.

## Tooling — TaterTotterson

tatertotterson has done the hard part. The microWakeWord Trainer Studio is a local web UI that takes you from phrase, through reviewing your samples, to a trained model, and there's prebuilt satellite firmware too:

- Apple Silicon trainer, the one I used, with GPU/Metal acceleration on an M-series Mac: <https://github.com/TaterTotterson/microWakeWord-Trainer-AppleSilicon>
- NVIDIA / CUDA Docker trainer if you have a decent GPU instead: <https://github.com/TaterTotterson/microWakeWord-Trainer-Nvidia-Docker>
- Firmware and model assets for VoicePE / Satellite1 / ReSpeaker: <https://github.com/TaterTotterson/microWakeWords>

## How I did it

- I recorded about 40 samples of me and my wife saying *"hey Viki"*. It's a distinct enough name, and the extra "hey" keeps the false triggers down. Then a set of background-noise and hard-negative recordings to train against.
- Setup is a couple of minutes and opens a local web UI.
- Start the trainer and wait. On my MacBook it took under two hours.
- You get a `.json` and a `.tflite` out. Drop them somewhere ESPHome can reach, for example `/config/models/`, or point at a raw URL.

## The ESPHome change

It's a `micro_wake_word:` block with `model:` pointing at your trained JSON, which in turn references the `.tflite`. Compile and install over the air from the browser:

```yaml
micro_wake_word:
  vad:                      # optional voice-activity model — cuts non-speech false accepts
  models:
    - model: /config/models/hey_viki.json   # local path, or a full https:// URL to the JSON
      id: hey_viki
      probability_cutoff: 0.97              # 0.0–1.0; higher = stricter (fewer false wakes, more misses)
      sliding_window_size: 5                # optional; smaller = lower latency, more false accepts
```

The trainer bakes `probability_cutoff` and `sliding_window_size` into the JSON, but you can override them here in the YAML. Once it's flashed, pick the wake word in Home Assistant under Settings → Voice assistants for your pipeline.

## Tuning — the sensitivity picker

My model wasn't perfect, so I wanted to change the cutoff live rather than reflash every time.

First, find the value you want. Run a live debug in ESPHome (Logs) and watch the probabilities. Every wake attempt logs its sliding average, like this:

```text
[D][micro_wake_word] Detected 'hey viki' with sliding average probability is 0.94 and max probability is 0.98
```

Say the wake word a few times, see where the real triggers land against the false ones off the telly, and pick a cutoff in between.

Then expose it in Home Assistant. Rather than a raw slider I use a template `select` with named steps, which is nicer to pick from, and the `on_value` lambda writes the cutoff straight into the running model with no recompile. The cutoffs use microWakeWord's 0–255 scale, so 250 is about 0.98 and 180 about 0.70:

```yaml
select:
  - platform: template
    name: "Viki sensitivity"
    optimistic: true
    initial_option: Slightly sensitive
    restore_value: true
    entity_category: config
    options:
      - Slightly sensitive    # .98
      - Moderately sensitive  # .96
      - Very sensitive        # .87
      - Even more sensitive   # .80
      - The most sensitive    # .70
    on_value:
      lambda: |-
        static const uint16_t cutoffs[] = {250, 245, 222, 204, 180};
        id(hey_viki).set_probability_cutoff(cutoffs[i]);
```

`i` is the index of the option you picked. ESPHome's select `on_value` hands you both `x`, the label, and `i`, so each step maps to its cutoff. Now I drag it in Settings → Devices & Services, live, without reflashing.

VIKI_ still pipes up at the telly now and then. That's on purpose, mostly.

---

[← Back to talk notes](emf-talk-notes.md) · Next: [Speech-to-Text →](stt.md)
