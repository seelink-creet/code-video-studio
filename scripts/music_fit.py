#!/usr/bin/env python3
# Copyright (c) 2026 Link Liu (https://github.com/seelink-creet) — MIT License, see LICENSE
"""把一首库曲（CC BY 等）贴到画面上：选一个偏移，让曲子自己的段落入口落在画面的关键节拍上。
不在曲子内部乱剪；需要剪时只在小节线上剪、并做 20–30 ms 交叉淡化。

  python3 music_fit.py analyse track.mp3                       # 列出节拍/小节线和能量突变点（候选“段落入口”），需要 librosa
  python3 music_fit.py fit track.mp3 out.wav --dur 44 --entry 39.33 --beat 30.8 [--fade-in 0.8] [--fade-out 3] [--trim-after -5]
      → 曲子时间 39.33s 落在画面 30.8s；从曲子 8.53s 开始播放；淡入/淡出；入口后整体 −5 dB
  python3 music_fit.py splice track.mp3 out.wav --dur 45 --seg 0:25.3@0 --seg 129.4:139.45@25.95 --seg 233.5:236.5@39.3
      → 多段拼接：曲子 a:b 放在画面时间 @t；每个接缝 25 ms 等功率交叉淡化（请让接缝落在小节线上）
可以先出 2–3 个候选预览（同一画面 + 不同曲子），让用户直接看着选。
"""
import argparse, subprocess
import numpy as np
SR = 48000

def load(path, ss=0.0, t=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(max(0, ss)), "-i", path] + (["-t", str(t)] if t else []) + ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).astype(np.float64)

def ss(a, b, x): u = np.clip((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u)

def write(path, y):
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", path], stdin=subprocess.PIPE)
    p.stdin.write(y.astype(np.float32).tobytes()); p.stdin.close(); p.wait(); print("→", path, f"{len(y) / SR:.2f}s")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["analyse", "fit", "splice"]); ap.add_argument("track"); ap.add_argument("out", nargs="?")
    ap.add_argument("--dur", type=float); ap.add_argument("--entry", type=float); ap.add_argument("--beat", type=float)
    ap.add_argument("--fade-in", type=float, default=0.8); ap.add_argument("--fade-out", type=float, default=3.0); ap.add_argument("--trim-after", type=float, default=0.0)
    ap.add_argument("--seg", action="append", default=[])
    a = ap.parse_args()
    if a.mode == "analyse":
        import librosa
        y, sr = librosa.load(a.track, sr=22050, mono=True)
        oenv = librosa.onset.onset_strength(y=y, sr=sr); tempo, bfr = librosa.beat.beat_track(onset_envelope=oenv, sr=sr)
        beats = librosa.frames_to_time(bfr, sr=sr)
        if len(beats) >= 8: ph = int(np.argmax([oenv[bfr[p::4]].mean() for p in range(4)])); bars = beats[ph::4]
        else: print("没检测到稳定节拍（氛围/无鼓曲目），改用每 1 秒网格"); bars = np.arange(0, len(y) / sr, 1.0)
        rms = librosa.feature.rms(y=y, hop_length=512)[0]; tt = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512)
        e = np.interp(bars, tt, 20 * np.log10(rms + 1e-6)); jump = np.diff(e)
        print(f"时长 {len(y) / sr:.1f}s  速度约 {float(np.atleast_1d(tempo)[0]):.1f} BPM  小节数 {len(bars)}")
        print("能量上升最大的小节线（候选段落入口，曲子时间）：")
        for i in np.argsort(-jump)[:8]: print(f"  {bars[i + 1]:7.2f}s  (+{jump[i]:.1f} dB)")
        print("能量下降最大的小节线（候选“呼吸/近静音”，适合放定格）：")
        for i in np.argsort(jump)[:5]: print(f"  {bars[i + 1]:7.2f}s  ({jump[i]:.1f} dB)")
    elif a.mode == "fit":
        start = a.entry - a.beat; y = load(a.track, start, a.dur); pad = int(max(0, -start) * SR)
        y = np.r_[np.zeros((pad, 2)), y][: int(a.dur * SR)]; t = np.arange(len(y)) / SR
        g = 10 ** (a.trim_after * ss(a.beat - 0.05, a.beat + 0.6, t) / 20) * ss(0, a.fade_in, t) * (1 - ss(a.dur - a.fade_out, a.dur - 0.05, t)) ** 1.5
        print(f"曲子从 {start:.2f}s 开始播放；曲子 {a.entry}s → 画面 {a.beat}s"); write(a.out, y * g[:, None])
    else:
        out = np.zeros((int(a.dur * SR), 2)); XF = int(0.025 * SR)
        for s in a.seg:
            rng, at = s.split("@"); s0, s1 = [float(v) for v in rng.split(":")]; at = float(at)
            y = load(a.track, s0 - 0.025, s1 - s0 + 0.05); n = len(y); w = np.ones(n)
            w[:XF] = np.sin(np.linspace(0, np.pi / 2, XF)); w[-XF:] = np.cos(np.linspace(0, np.pi / 2, XF))
            i0 = int((at - 0.025) * SR); i1 = min(len(out), i0 + n); out[max(0, i0):i1] += (y * w[:, None])[max(0, -i0):i1 - i0]
        write(a.out, out)
