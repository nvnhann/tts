"""Thử nghiệm VieNeu-TTS v3 Turbo trên N file txt đầu tiên của một thư mục truyện."""
import argparse
import subprocess
import time
from pathlib import Path

from vieneu import Vieneu

SR = 48000

p = argparse.ArgumentParser()
p.add_argument("--src", default="/content/drive/MyDrive/audio/1. Ngã dục phong thiên")
p.add_argument("--out", default="output")
p.add_argument("--n", type=int, default=10)
p.add_argument("--voice", default="Hải Đăng", help='tên giọng, hoặc "all" để chạy mọi giọng (mỗi giọng 1 thư mục con)')
args = p.parse_args()

files = sorted(Path(args.src).glob("*.txt"))[: args.n]

tts = Vieneu()
if args.voice == "all":
    jobs = [(name, Path(args.out) / name) for _, name in tts.list_preset_voices()]
else:
    jobs = [(args.voice, Path(args.out))]

total_t = total_d = 0.0
for voice, out in jobs:
    out.mkdir(parents=True, exist_ok=True)
    for f in files:
        mp3 = out / f"{f.stem}.mp3"
        if mp3.exists():
            print(f"skip {voice}/{mp3.name}")
            continue
        text = f.read_text(encoding="utf-8").strip()
        t0 = time.time()
        audio = tts.infer(text, voice=voice)
        dt = time.time() - t0
        dur = len(audio) / SR
        wav = out / f"{f.stem}.wav"
        tts.save(audio, str(wav))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-b:a", "128k", str(mp3)], check=True)
        wav.unlink()
        total_t += dt
        total_d += dur
        print(f"[{voice}] {f.name}: {len(text)} ký tự -> {dur/60:.1f} phút audio, {dt:.1f}s, RTF {dt/dur:.3f}", flush=True)

if total_d:
    print(f"TỔNG: {total_d/60:.1f} phút audio trong {total_t:.0f}s, RTF {total_t/total_d:.3f}")
