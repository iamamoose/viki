# 1. Wakeword — train your own

[← Back to README](./README.md) · Next: [Speech-to-Text →](02-speech-to-text.md)

---

The three default wakewords ("Hey Mycroft / Hey Jarvis / Okay Nabu") exist because wakeword training is hard to do without false positives — a lot of effort goes into making sure random TV noise doesn't set them off. **microWakeWord** runs locally on the ESP32, listening all the time. But you *can* train your own.

## Tooling — TaterTotterson

**tatertotterson** has done a lot of work making the training painless, with a local web-UI trainer and prebuilt satellite firmware:

- **Apple Silicon trainer** (what I used — full GPU/Metal acceleration on an M-series Mac): <https://github.com/TaterTotterson/microWakeWord-Trainer-AppleSilicon>
- NVIDIA / CUDA Docker trainer (if you've a decent GPU instead): <https://github.com/TaterTotterson/microWakeWord-Trainer-Nvidia-Docker>
- Firmware + model assets for VoicePE / Satellite1 / ReSpeaker: <https://github.com/TaterTotterson/microWakeWords>

## How I did it

- Recorded **~40 samples** of me and my wife saying *"hey Viki"* — a reasonable, distinct name, and the extra "hey" cuts false triggers — plus a set of background-noise / hard-negative recordings.
- Setup takes a few minutes and pops up a local web UI.
- Run the trainer and wait. On a MacBook it took **under 2 hours**.
- Output: a `.json` + a `.tflite` file → drop them somewhere ESPHome can see them (e.g. `/config/models/`, or reference a raw URL).

## The ESPHome change

It's just a `micro_wake_word:` block pointing `model:` at your trained JSON (the JSON in turn references the `.tflite`). Compile + install **OTA** in the browser:

```yaml
micro_wake_word:
  vad:                      # optional voice-activity model — cuts non-speech false accepts
  models:
    - model: /config/models/hey_viki.json   # local path, or a full https:// URL to the JSON
      id: hey_viki
      probability_cutoff: 0.97              # 0.0–1.0; higher = stricter (fewer false wakes, more misses)
      sliding_window_size: 5                # optional; smaller = lower latency, more false accepts
```

`probability_cutoff` and `sliding_window_size` are baked into the JSON by the trainer, but **you can override them here in YAML**. Once flashed, select the wake word in Home Assistant under **Settings → Voice assistants** for your pipeline.

## Tuning — the sensitivity slider

My training didn't produce a perfect model, so I wanted to tweak the cutoff *live* rather than reflash each time.

**First, find the right value.** Run a live debug in ESPHome (Logs) and watch the detection probabilities — every wake attempt logs its sliding-average probability, e.g.:

```text
[D][micro_wake_word] Detected 'hey viki' with sliding average probability is 0.94 and max probability is 0.98
```

Say the wake word a few times, note where real triggers land vs. the false ones off the telly, and pick a `probability_cutoff` that sits between them.

**Then expose it as a slider.** A template `number` surfaces the value to Home Assistant so you can drag it live:

```yaml
number:
  - platform: template
    name: "Wake Word Sensitivity"
    id: ww_sensitivity
    optimistic: true
    mode: slider
    min_value: 0.50
    max_value: 0.99
    step: 0.01
    initial_value: 0.97
    restore_value: true
```

> ⚠️ **Wiring caveat:** stock `micro_wake_word` reads `probability_cutoff` at model load, so there's no built-in action to change it on the fly — the slider above is the HA-facing control, but applying a new value cleanly means either re-baking it in YAML (and reflashing) or using firmware that re-applies it at runtime (the TaterTotterson firmware exposes its own sensitivity entity with `wake_cutoff_*` presets). Adapt this to whichever firmware you're running. *(My slide showed the live slider but not its YAML — this is the working pattern to drop your exact wiring into.)*

(Letting her occasionally interject at the telly is a feature, not a bug. Just sometimes.)

## Links

| What | Where |
|---|---|
| microWakeWord trainer — Apple Silicon | <https://github.com/TaterTotterson/microWakeWord-Trainer-AppleSilicon> |
| microWakeWord trainer — NVIDIA Docker | <https://github.com/TaterTotterson/microWakeWord-Trainer-Nvidia-Docker> |
| Tater firmware + model assets | <https://github.com/TaterTotterson/microWakeWords> |
| ESPHome `micro_wake_word` component docs | <https://esphome.io/components/micro_wake_word/> |

---

[← Back to README](../README.md) · Next: [Speech-to-Text →](02-speech-to-text.md)
