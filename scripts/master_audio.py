#!/usr/bin/env python3
# Copyright (c) 2026 Link Liu (https://github.com/seelink-creet) — MIT License, see LICENSE
"""混音母带 + 封装 + 【AAC 编码后】实测响度/真峰值，不达标就回退增益重编（AAC 会抬高真峰值）。
  python3 master_audio.py picture.mp4 mix.wav final.mp4 [--lufs -14] [--tp -1.0] [--abr 192k]
推荐默认：网络平台 −14 LUFS（安静、动态大的片子可用 −16），真峰值 ≤ −1 dBTP。
两遍 loudnorm（线性模式）+ 限幅；编码后用 ebur128 复测，超标则降增益最多 6 轮。
"""
import argparse, json, re, subprocess

def measure(path):
    e = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    s = e[e.rfind("Summary:"):]
    I = float(re.search(r"I:\s*(-?[\d.]+) LUFS", s).group(1)); tp = re.search(r"Peak:\s*(-?[\d.]+|-inf)", s.split("True peak:")[-1]).group(1)
    return I, float(tp) if tp != "-inf" else -99.0

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("audio"); ap.add_argument("out")
    ap.add_argument("--lufs", type=float, default=-14.0); ap.add_argument("--tp", type=float, default=-1.0); ap.add_argument("--abr", default="192k")
    a = ap.parse_args()
    p1 = subprocess.run(["ffmpeg", "-hide_banner", "-i", a.audio, "-af", f"loudnorm=I={a.lufs}:TP={a.tp - 0.5}:LRA=11:print_format=json",
                         "-f", "null", "-"], capture_output=True, text=True).stderr
    js = json.loads(p1[p1.rfind("{"):p1.rfind("}") + 1]); g = 0.0
    for it in range(6):
        lim = 10 ** ((a.tp - 0.7 + min(g, 0)) / 20)
        af = (f"loudnorm=I={a.lufs}:TP={a.tp - 0.5}:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
              f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true,"
              f"volume={g}dB,alimiter=limit={lim:.4f}:level=false:attack=2:release=60,aresample=48000")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.video, "-i", a.audio, "-filter_complex", f"[1:a]{af}[a]", "-map", "0:v",
                        "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", a.abr, "-ar", "48000", "-shortest", "-movflags", "+faststart", a.out], check=True)
        I, TP = measure(a.out); print(f"第 {it + 1} 轮（AAC 后实测）：{I:.1f} LUFS，真峰值 {TP:.1f} dBTP")
        if TP <= a.tp and abs(I - a.lufs) <= 1.0: print("达标 →", a.out); return
        g += min(-0.3, a.tp - TP - 0.2) if TP > a.tp else (a.lufs - I) * 0.8
    print("警告：6 轮未完全达标，请检查混音里是否有尖锐瞬态（可先对音效总线做限幅）。")

if __name__ == "__main__":
    main()
