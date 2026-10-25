#!/usr/bin/env python3
# Copyright (c) 2026 Link Liu (https://github.com/seelink-creet) — MIT License, see LICENSE
"""运动/节奏 QC：一张图上画【帧差（画面运动量）+ 音频电平 + 可选变速曲线 + 事件竖线】，并自动找“跳帧/突变”。
  python3 qc_motion.py film.mp4 qc.png [--audio mix.wav] [--keys keys.json] [--events events.json]
  python3 qc_motion.py film.mp4 --bookend 0 28.5          # 首尾呼应检查：两个时刻的画面差（越接近 0 越一致）
events.json: [["名字", 秒], ...]   keys.json: timeremap 关键帧
报告：相对邻域的突变帧（静止段里的小跳在绝对值上很小，所以用相对值）、黑帧/白帧、静止过久的区段。
"""
import argparse, json, os, subprocess, sys
import numpy as np

def frames_gray(path, w=135):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                        "-of", "json", path], capture_output=True, text=True, check=True)
    s = json.loads(r.stdout)["streams"][0]; n, d = s["r_frame_rate"].split("/"); fps = float(n) / float(d)
    h = int(round(s["height"] * w / s["width"] / 2) * 2)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32), fps

def audio_db(path, fps):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "48000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32); hop = int(48000 / fps); n = len(a) // hop
    return 20 * np.log10(np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-6)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("out", nargs="?")
    ap.add_argument("--audio"); ap.add_argument("--keys"); ap.add_argument("--events"); ap.add_argument("--bookend", nargs=2, type=float)
    ap.add_argument("--still-max", type=float, default=2.5, help="超过多少秒几乎不动就报警")
    a = ap.parse_args(); F, fps = frames_gray(a.video)
    if a.bookend:
        i, j = [min(len(F) - 1, int(round(t * fps))) for t in a.bookend]
        print(f"首尾差 |f({a.bookend[0]})-f({a.bookend[1]})| 平均 = {np.abs(F[i] - F[j]).mean():.2f}/255（<2 基本一致）"); return
    d = np.abs(np.diff(F, axis=0)).mean((1, 2)); t = np.arange(1, len(F)) / fps
    k = 7; pad = np.pad(d, k, mode="edge"); med = np.array([np.median(pad[i:i + 2 * k + 1]) for i in range(len(d))])
    jumps = np.where((d > 3 * med + 0.6) & (d > 1.0))[0]
    print(f"{len(F)} 帧 @ {fps:g} fps")
    print("相对突变帧（检查是否是有意的冲击/切点）：", ", ".join(f"{t[i]:.2f}s" for i in jumps[:40]) or "无")
    mean = F.reshape(len(F), -1).mean(1)
    print("近黑/近白帧：", ", ".join(f"{i / fps:.2f}s" for i in np.where((mean < 6) | (mean > 250))[0][:20]) or "无")
    still = d < 0.15; run = 0; longs = []
    for i, s in enumerate(still):
        run = run + 1 if s else 0
        if run == int(a.still_max * fps): longs.append(t[i] - a.still_max)
    print(f"静止 > {a.still_max}s 的起点：", ", ".join(f"{x:.2f}s" for x in longs) or "无")
    if not a.out: return
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    rows = 2 + bool(a.keys); fig, ax = plt.subplots(rows, 1, figsize=(13, 3 * rows), sharex=True); r = 0
    if a.keys:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from timeremap import Remap
        R = Remap(json.load(open(a.keys))); T = np.linspace(0, R.duration, 3000)
        ax[0].plot(T, R.speed(T) * 100, "m"); ax[0].set_yscale("log"); ax[0].set_ylabel("speed %"); r = 1
    ax[r].plot(t, d, "k", lw=.8); ax[r].scatter(t[jumps], d[jumps], c="r", s=12); ax[r].set_ylabel("frame diff")
    if a.audio or True:
        try:
            db = audio_db(a.audio or a.video, fps); ax[r + 1].plot(np.arange(len(db)) / fps, db, "b", lw=.8); ax[r + 1].set_ylim(-70, 0)
        except Exception: ax[r + 1].text(0.5, 0.5, "no audio", transform=ax[r + 1].transAxes)
    ax[r + 1].set_ylabel("audio dB"); ax[-1].set_xlabel("output time (s)")
    if a.events:
        for name, x in json.load(open(a.events)):
            for q in ax: q.axvline(x, c="gray", lw=.6, ls=":")
            ax[0].text(x, ax[0].get_ylim()[1], name, rotation=90, fontsize=7, va="top")
    for q in ax: q.grid(alpha=.3)
    plt.tight_layout(); plt.savefig(a.out, dpi=100); print("→", a.out)

if __name__ == "__main__":
    main()
