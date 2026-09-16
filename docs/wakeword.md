# 1. Wakeword

[← Back to VIKI](../README.md) · Next: [Speech-to-Text →](stt.md)

---

Home Assistant ships with three wakewords: "Hey Mycroft", "Hey Jarvis" and "Okay Nabu". There aren't more because a good wakeword model is hard work. It has to fire for every accent while ignoring the telly, and keeping the false positives down to something sensible takes a lot of tuning. The model, microWakeWord, runs on the ESP32 itself and listens all the time. But you can train your own, given a set of recordings of the wake word and some background noise to train against.

## Using ours

`hey_viki` is in [viki-assets](https://github.com/iamamoose/viki-assets) —
a `.json` and a `.tflite`, 63KB the pair. Trained on about 40 recordings
of me and my wife saying it.

Drop both in `/config/models/`, keeping them together — the JSON
references the `.tflite` beside it by name. Or point ESPHome straight at
the raw URLs.

Fair warning: it's tuned to our voices and our living room. If it misses
you, [make your own](make-your-own-wakeword.md) — it's an afternoon.

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

[← Back to VIKI](../README.md) · Next: [Speech-to-Text →](stt.md)
