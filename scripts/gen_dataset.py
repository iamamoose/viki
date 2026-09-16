import argparse
import os
import shutil
import time

import librosa
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

METADATA = "metadata.csv"
REF_DIR = "."          # directory holding <voice>.wav (see viki-assets)
OUT_ROOT = "./trainingdata"   # one subdir per voice is created here

# Written at qwen3-tts's native 24000 Hz on purpose. TextyMcSpeechy's
# create_dataset.sh resamples with ffmpeg to both wav_22050/ and wav_16000/ from
# the highest rate it is given, so handing it 24000 lets it derive both from the
# best source; pre-resampling to 22050 here would degrade the 16000 set too.

# create_dataset.sh does NOT trim silence (its only "trim" is blank metadata.csv
# lines), so the ~0.5s of padding the model adds has to come off here -- this is
# what the old trimmed/ dir and trim-gaps.py were doing.
TRIM_TOP_DB = 30
TRIM_PAD_S = 0.03

# Must match what the reference clip actually says (ICL conditions on it).
REF_TEXT = "Oh, you're finally back. I already turned the lights on and started the kettle. Not because I was waiting or anything.  Welcome Home."

# Default voice name; pass --voices to override.
DEFAULT_VOICES = ["viki"]


def load_metadata():
    rows = []
    with open(METADATA, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            fid, text = line.split("|", 1)
            rows.append((fid, text.strip()))
    return rows


def trim_silence(wav, sr):
    _, (lo, hi) = librosa.effects.trim(wav, top_db=TRIM_TOP_DB)
    if hi <= lo:
        return wav
    pad = int(TRIM_PAD_S * sr)
    return wav[max(0, lo - pad):min(len(wav), hi + pad)]


def main():
    ap = argparse.ArgumentParser(description="Generate a full piper training set per voice")
    ap.add_argument("--voices", help="comma-separated (default: the 10 rated yes)")
    ap.add_argument("--ref-dir", default=REF_DIR)
    ap.add_argument("--out-root", default=OUT_ROOT)
    ap.add_argument("--limit", type=int, help="only the first N lines (for a quick trial)")
    ap.add_argument("--force", action="store_true", help="overwrite existing wavs")
    args = ap.parse_args()

    names = args.voices.split(",") if args.voices else DEFAULT_VOICES
    rows = load_metadata()
    if args.limit:
        rows = rows[:args.limit]

    missing = [n for n in names if not os.path.exists(os.path.join(args.ref_dir, f"{n}.wav"))]
    if missing:
        raise SystemExit(f"no reference wav for: {', '.join(missing)} (looked in {args.ref_dir}/)")

    print(f"{len(names)} voices x {len(rows)} lines = {len(names)*len(rows)} clips -> {args.out_root}/", flush=True)

    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        device_map="cuda:0",
        dtype=torch.bfloat16,
        attn_implementation="flash_attention_2",
    )

    start = time.time()
    for vi, name in enumerate(names, 1):
        outdir = os.path.join(args.out_root, f"trainingdata-{name}")
        os.makedirs(outdir, exist_ok=True)
        shutil.copyfile(METADATA, os.path.join(outdir, "metadata.csv"))

        prompt = model.create_voice_clone_prompt(
            ref_audio=os.path.join(args.ref_dir, f"{name}.wav"), ref_text=REF_TEXT
        )

        v0, made, skipped, failed = time.time(), 0, 0, 0
        for fid, text in rows:
            path = os.path.join(outdir, f"{fid}.wav")
            if os.path.exists(path) and not args.force:
                skipped += 1
                continue
            # Seed by line id so a clip can be regenerated identically later, and so
            # the same line is directly comparable across voices.
            torch.manual_seed(int(fid))
            try:
                wavs, sr = model.generate_voice_clone(
                    text=text, language="English", voice_clone_prompt=prompt
                )
            except Exception as e:
                print(f"  [{name}] FAILED {fid}: {type(e).__name__}: {e}", flush=True)
                failed += 1
                continue
            wav = trim_silence(wavs[0], sr)
            sf.write(path, wav, sr, subtype="PCM_16")
            made += 1
            if made % 25 == 0:
                print(f"  [{vi}/{len(names)} {name}] {made} made, {time.time()-v0:.0f}s", flush=True)

        print(f"[{vi}/{len(names)}] {name}: {made} made, {skipped} skipped, {failed} failed "
              f"in {time.time()-v0:.0f}s -> {outdir}/", flush=True)

    print(f"done in {time.time()-start:.0f}s", flush=True)


if __name__ == "__main__":
    main()
