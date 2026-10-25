#!/usr/bin/env python3
# Copyright (c) 2026 Link Liu (https://github.com/seelink-creet) — MIT License, see LICENSE
"""联系表（contact sheet）/ 动作条（strip）/ 全分辨率裁切（crop）三种检查图。
  python3 contact_sheet.py sheet film.mp4 sheet.png --every 1.0 [--cols 8]     # 看整体节奏（每 0.5–1.5 s 一格）
  python3 contact_sheet.py strip film.mp4 strip.png --start 12.0 --end 13.0     # 看一个瞬间的每一帧（转身、冲击、转场）
  python3 contact_sheet.py crop  film.mp4 crop.png --at 20.0 --box 0.3,0.4,0.4,0.2   # 全分辨率看细节（x,y,w,h 为画面比例）
注意：有些 AI 工具按文件路径缓存图片，重渲后请换一个新文件名再看。
"""
import argparse, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                        "-show_entries", "format=duration", "-of", "json", path], capture_output=True, text=True, check=True)
    j = json.loads(r.stdout); s = j["streams"][0]; n, d = s["r_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), float(n) / float(d), float(j["format"]["duration"])

def grab(path, t, w=None):
    vf = ["-vf", f"scale={w}:-2"] if w else []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.4f}", "-i", path, "-frames:v", "1", *vf, "-f", "image2pipe",
                          "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    import io; return np.asarray(Image.open(io.BytesIO(raw)).convert("RGB"))

def make_sheet(images, labels, out, cols=None, pad=8, bg=(236, 232, 222)):
    n = len(images); cols = cols or min(8, n); rows = (n + cols - 1) // cols
    h, w = images[0].shape[:2]; lab = 22
    sheet = Image.new("RGB", (cols * (w + pad) + pad, rows * (h + lab + pad) + pad), bg); d = ImageDraw.Draw(sheet)
    try: f = ImageFont.load_default(size=16)
    except Exception: f = ImageFont.load_default()
    for i, (im, lb) in enumerate(zip(images, labels)):
        r, c = divmod(i, cols); x, y = pad + c * (w + pad), pad + r * (h + lab + pad)
        sheet.paste(Image.fromarray(np.asarray(im)[..., :3].astype(np.uint8)), (x, y + lab)); d.text((x + 2, y + 2), lb, fill=(40, 40, 40), font=f)
    sheet.save(out); print("→", out, f"{n} 格"); return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["sheet", "strip", "crop"]); ap.add_argument("video"); ap.add_argument("out")
    ap.add_argument("--every", type=float, default=1.0); ap.add_argument("--cols", type=int); ap.add_argument("--width", type=int, default=240)
    ap.add_argument("--start", type=float); ap.add_argument("--end", type=float); ap.add_argument("--at", type=float); ap.add_argument("--box", default="0.25,0.25,0.5,0.5")
    a = ap.parse_args(); W, H, fps, dur = probe(a.video)
    if a.mode == "sheet":
        ts = list(np.arange(0, dur - 1e-3, a.every)) + [max(0, dur - 1.5 / fps)]   # 最后一帧也要看（结尾/首尾呼应）
        make_sheet([grab(a.video, t, a.width) for t in ts], [f"{t:.2f}s" for t in ts], a.out, a.cols)
    elif a.mode == "strip":
        ts = [a.start + i / fps for i in range(int(round((a.end - a.start) * fps)) + 1)]
        make_sheet([grab(a.video, t, a.width) for t in ts], [f"{t:.3f}" for t in ts], a.out, a.cols or 10)
    else:
        x, y, w, h = [float(v) for v in a.box.split(",")]; im = grab(a.video, a.at)
        Image.fromarray(im[int(y * H):int((y + h) * H), int(x * W):int((x + w) * W)]).save(a.out); print("→", a.out)
