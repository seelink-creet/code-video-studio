#!/usr/bin/env python3
# Copyright (c) 2026 Link Liu (https://github.com/seelink-creet) — MIT License, see LICENSE
"""交付：从已封装好声音的成片出【高清版】【聊天/预览版】【封面】，并按目标体积自动算码率。
  python3 deliver.py final.mp4 --name myfilm [--hd-mb 95] [--chat-mb 7] [--chat-height 1280] [--cover-at 3.2]
- 高清：H.264 High, yuv420p, +faststart；若原文件超过 --hd-mb（很多网盘/平台单文件上限 100MB）就按体积算码率两遍编码。
- 聊天版：常见即时通讯附件 4–8MB，按目标体积算码率，缩到 --chat-height（竖屏 1280 或 960；像素画请选整数缩放）。
- 封面：截取 --cover-at 秒的帧，另存 3:4（1080x1440）与原画幅两张（文字标题请另行设计，不剧透）。
"""
import argparse, json, os, subprocess

def dur(p):
    return float(json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", p],
                                           capture_output=True, text=True).stdout)["format"]["duration"])

def enc(src, out, vkbps, scale=None, abr="128k"):
    vf = ["-vf", f"scale=-2:{scale}:flags=lanczos"] if scale else []
    base = ["ffmpeg", "-y", "-v", "error", "-i", src, *vf, "-c:v", "libx264", "-profile:v", "high", "-preset", "slow",
            "-pix_fmt", "yuv420p", "-b:v", f"{vkbps}k", "-maxrate", f"{int(vkbps * 1.5)}k", "-bufsize", f"{vkbps * 2}k"]
    log = out + ".2pass"
    subprocess.run(base + ["-pass", "1", "-passlogfile", log, "-an", "-f", "mp4", os.devnull], check=True)
    subprocess.run(base + ["-pass", "2", "-passlogfile", log, "-c:a", "aac", "-b:a", abr, "-movflags", "+faststart", out], check=True)
    for f in os.listdir(os.path.dirname(os.path.abspath(out))):
        if f.startswith(os.path.basename(log)): os.remove(os.path.join(os.path.dirname(os.path.abspath(out)), f))
    print(f"→ {out}  {os.path.getsize(out) / 1e6:.1f} MB")

def kbps_for(mb, seconds, abr_k): return max(300, int(mb * 8e3 * 0.96 / seconds - abr_k))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("--name", default="film")
    ap.add_argument("--hd-mb", type=float, default=95); ap.add_argument("--chat-mb", type=float, default=7)
    ap.add_argument("--chat-height", type=int, default=1280); ap.add_argument("--cover-at", type=float, default=None)
    a = ap.parse_args(); D = dur(a.src)
    hd = f"{a.name}_HD.mp4"
    if os.path.getsize(a.src) / 1e6 > a.hd_mb: enc(a.src, hd, kbps_for(a.hd_mb, D, 192), abr="192k")
    else:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.src, "-c", "copy", "-movflags", "+faststart", hd], check=True); print("→", hd, "(直接拷贝)")
    enc(a.src, f"{a.name}_chat.mp4", kbps_for(a.chat_mb, D, 128), scale=a.chat_height)
    if a.cover_at is not None:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(a.cover_at), "-i", a.src, "-frames:v", "1", f"{a.name}_cover.png"], check=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"{a.name}_cover.png", "-vf",
                        "scale=1080:1440:force_original_aspect_ratio=increase,crop=1080:1440", f"{a.name}_cover_3x4.png"], check=True)
        print("→ 封面", f"{a.name}_cover.png", f"{a.name}_cover_3x4.png")
