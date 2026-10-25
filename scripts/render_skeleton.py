#!/usr/bin/env python3
# Copyright (c) 2026 Link Liu (https://github.com/seelink-creet) — MIT License, see LICENSE
"""逐帧确定性渲染骨架：每一帧只由时间 t 决定（frame(t) 是纯函数），随机数全部带种子。
复制这个文件做新片，只改 CONFIG 和 draw()。

  python3 render_skeleton.py still 0 2.5 6            # 渲几张关键帧 → out/still_*.png（lookdev / 自查）
  python3 render_skeleton.py sheet 1.0                 # 每 1.0 秒一格的联系表 → out/sheet.png
  python3 render_skeleton.py render --workers 6        # 全片：多进程分块渲染 → out/picture.mp4（无声母版）
  python3 render_skeleton.py render --scale 0.5 --start 6 --end 9   # 低分辨率只渲某一段（快速试错）

规则：不用 time.time()/全局随机数；不从上一帧继承状态（有状态的模拟先离线算好、按帧存 npz，或每 N 帧存快照）；
分辨率相关量（线宽、字号、模糊半径、粒子尺寸）都乘 S（= 实际宽 / 设计宽），换分辨率不变样。
"""
import argparse, math, os, subprocess, sys, tempfile
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont

CONFIG = dict(W=1080, H=1920, FPS=30, DUR=10.0, SEED=7, DESIGN_W=1080,
              PAPER=(242, 236, 222), INK=(30, 30, 34), ACCENT=(205, 48, 42),
              FONT=None)  # FONT: 字体文件路径（建议 OFL 字体）；None 用 PIL 默认字体
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

def smoothstep(a, b, x):
    u = np.clip((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u)

def ease_out(x): x = min(max(x, 0.0), 1.0); return 1 - (1 - x) ** 3

class Film:
    def __init__(self, scale=1.0):
        c = CONFIG; self.W, self.H = int(c["W"] * scale) // 2 * 2, int(c["H"] * scale) // 2 * 2
        self.S = self.W / c["DESIGN_W"]
        rng = np.random.default_rng(c["SEED"])                      # 只在初始化时取随机数 → 每帧可复现
        self.paper = self._paper(rng)
        self.pts = rng.random((400, 2)) * [self.W, self.H]           # 示例：400 个尘点
        self.ph = rng.random(400) * 2 * np.pi
        self.font = self._font(int(96 * self.S))

    def _font(self, size):
        f = CONFIG["FONT"]
        try: return ImageFont.truetype(f, size) if f else ImageFont.load_default(size=size)
        except Exception: return ImageFont.load_default()

    def _paper(self, rng):
        base = np.array(CONFIG["PAPER"], np.float32)
        lo = rng.random((self.H // 64 + 2, self.W // 64 + 2)).astype(np.float32)
        lo = np.asarray(Image.fromarray((lo * 255).astype(np.uint8)).resize((self.W, self.H), Image.BICUBIC), np.float32) / 255
        hi = rng.random((self.H, self.W)).astype(np.float32)
        return np.clip(base[None, None] * (0.97 + 0.04 * lo[..., None] + 0.02 * hi[..., None]), 0, 255)

    def frame(self, t):
        """纯函数：t（秒）→ HxWx3 uint8。在这里写你的画面。"""
        img = self.paper.copy()
        # 示例层 1：尘点随时间漂浮（无状态：位置 = f(初始值, t)）
        p = self.pts + np.c_[np.sin(t * 0.7 + self.ph) * 12, np.full(len(self.ph), -t * 18)] * self.S
        p[:, 1] %= self.H
        im = Image.fromarray(img.astype(np.uint8)); d = ImageDraw.Draw(im)
        r = 2 * self.S
        for x, y in p: d.ellipse([x - r, y - r, x + r, y + r], fill=CONFIG["INK"])
        # 示例层 2：标题按 ease-out 落位（预备动作 + 过冲可在这里加）
        k = ease_out((t - 0.3) / 1.2)
        y = self.H * (0.45 + 0.05 * (1 - k))
        d.text((self.W / 2, y), "Hello", font=self.font, fill=CONFIG["INK"], anchor="mm")
        # 示例层 3：固定署名印（全片不动）
        s = 52 * self.S; x0, y0 = 110 * self.S, 160 * self.S
        d.rectangle([x0, y0, x0 + s, y0 + s], fill=CONFIG["ACCENT"])
        return np.asarray(im)

def _chunk(args):
    a, b, scale, path = args
    F = Film(scale); fps = CONFIG["FPS"]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{F.W}x{F.H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "14", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(a, b): p.stdin.write(np.ascontiguousarray(F.frame(i / fps)).tobytes())
    p.stdin.close(); p.wait(); return path

def render(args):
    fps = CONFIG["FPS"]; n0 = int(round(args.start * fps)); n1 = int(round((args.end or CONFIG["DUR"]) * fps))
    tmp = tempfile.mkdtemp(prefix="chunks_"); nw = max(1, args.workers)
    edges = np.linspace(n0, n1, nw + 1).astype(int)
    jobs = [(edges[i], edges[i + 1], args.scale, os.path.join(tmp, f"c{i:03d}.mp4")) for i in range(nw) if edges[i + 1] > edges[i]]
    with Pool(len(jobs)) as pool: parts = pool.map(_chunk, jobs)
    lst = os.path.join(tmp, "list.txt"); open(lst, "w").write("".join(f"file '{q}'\n" for q in parts))
    out = args.out or os.path.join(OUT, "picture.mp4"); os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    "-movflags", "+faststart", out], check=True)
    print("画面母版 →", out, f"({n1 - n0} 帧)")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["still", "sheet", "render"]); ap.add_argument("vals", nargs="*", type=float)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2); ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--start", type=float, default=0.0); ap.add_argument("--end", type=float, default=None); ap.add_argument("--out")
    a = ap.parse_args(); os.makedirs(OUT, exist_ok=True)
    if a.mode == "still":
        F = Film(a.scale)
        for t in a.vals or [0.0]:
            p = os.path.join(OUT, f"still_{t:07.3f}.png"); Image.fromarray(F.frame(t)).save(p); print(p)
    elif a.mode == "sheet":
        step = a.vals[0] if a.vals else 1.0; ts = list(np.arange(0, CONFIG["DUR"], step))
        F = Film(0.25); ims = [F.frame(t) for t in ts]
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from contact_sheet import make_sheet
        make_sheet(ims, [f"{t:.1f}s" for t in ts], os.path.join(OUT, "sheet.png"))
    else:
        render(a)

if __name__ == "__main__":
    main()
