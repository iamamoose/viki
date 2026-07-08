# 1. Wakeword — train your own

[← Back to README](./README.md) · Next: [Speech-to-Text →](02-speech-to-text.md)

---

There are only three default wakewords ("Hey Mycroft / Hey Jarvis / Okay Nabu"), because it's genuinely hard to get a model that works across all accents while staying under a defined level of acceptable false positives — a lot of effort goes into making sure random TV noise doesn't set them off. **microWakeWord** runs locally on the ESP32, listening all the time. But you *can* train your own, from a set of recordings of the wake word plus a set of background-noise recordings.

## Tooling — TaterTotterson

**tatertotterson** has done a lot of work making the training painless — the **microWakeWord Trainer Studio** is a local web UI that walks you through phrase → sample review → train, with prebuilt satellite firmware too:

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

## Tuning — the sensitivity picker

My training didn't produce a perfect model, so I wanted to tweak the cutoff *live* rather than reflash each time.

**First, find the right value.** Run a live debug in ESPHome (Logs) and watch the detection probabilities — every wake attempt logs its sliding-average probability, e.g.:

```text
[D][micro_wake_word] Detected 'hey viki' with sliding average probability is 0.94 and max probability is 0.98
```

Say the wake word a few times, note where real triggers land vs. the false ones off the telly, and pick a cutoff that sits between them.

**Then expose it in Home Assistant.** Rather than a raw slider I use a template `select` with named steps — friendlier to pick from, and the `on_value` lambda pokes the cutoff straight into the running model (no recompile). The cutoffs are on microWakeWord's 0–255 scale, so `250 ≈ 0.98`, `180 ≈ 0.70`:

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

`i` is the index of the chosen option (ESPHome's select `on_value` gives you both `x`, the label, and `i`), so each step maps to its matching cutoff. Now you drag it in **Settings → Devices & Services**, live, without reflashing.

(Letting her occasionally interject at the telly is a feature, not a bug. Just sometimes.)

---

[← Back to README](./README.md) · Next: [Speech-to-Text →](02-speech-to-text.md)
