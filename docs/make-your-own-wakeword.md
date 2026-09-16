# Make your own wakeword

[← Wakeword](wakeword.md) · [Back to VIKI](../README.md)

---

A good wakeword model has to fire for every accent while ignoring the
telly. Ours is tuned to two voices in one living room, so if it doesn't
hear you, train your own — it's an afternoon's work.

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


Once you have the pair, wiring them into ESPHome and tuning the cutoff
is the same as for ours: see [Wakeword](wakeword.md).

---

[← Wakeword](wakeword.md) · [Back to VIKI](../README.md)
