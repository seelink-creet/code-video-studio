#!/usr/bin/env python3
# Copyright (c) 2026 Link Liu (https://github.com/seelink-creet) — MIT License, see LICENSE
"""hello-film：约 10 秒的完整示例（内容是虚构的通用演示）。
一个墨点从上方落下 → 落地挤压 → 近定格蓄力 → 炸成粒子 → 粒子沿弧线聚成 “HELLO” → 安静定格。
演示：确定性逐帧渲染（种子）、时间重映射变速（真慢镜）、拖影随速度、挤压拉伸/预备动作/弧线/慢入慢出、
同一份时间线驱动画面和音效。

  python3 film.py still 0 3 6          # 关键帧（按输出时间）
  python3 film.py render [--scale 0.5] # → out/picture.mp4（无声）
  python3 film.py events               # → out/sfx_events.json（音效事件，已换算成输出时间）
"""
import json, os, subprocess, sys, tempfile
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))
from timeremap import Remap, shutter_len  # noqa: E402

W, H, FPS, SEED = 720, 1280, 30, 11
PAPER, INK, ACCENT = np.array([243, 238, 226], np.float32), np.array([28, 28, 34], np.float32), (200, 60, 50)
OUT = os.path.join(HERE, "out")

# ---- 故事时间 τ 的事件（画面与声音共用这一份）----
T_LAND, T_FREEZE0, T_FREEZE1, T_BURST, T_GATHER0, T_GATHER1, T_END = 1.0, 1.12, 1.27, 1.32, 2.2, 4.2, 7.9
# 变速关键帧 (τ, speed)：落地后近定格 → 爆发 3× → 聚字时放慢 → 定格段正常
KEYS = [(0, 1.0), (0.95, 1.0), (T_FREEZE0, 0.15), (T_FREEZE1, 0.1), (T_BURST, 2.8), (1.9, 2.8), (T_GATHER0, 1.0),
        (3.6, 0.6), (T_GATHER1, 0.9), (T_END, 1.0)]
R = Remap(KEYS)
DUR = R.duration

def ss(a, b, x): u = np.clip((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u)

def _targets(n, rng):
    """把 “HELLO” 栅格化成掩膜，在掩膜内随机取 n 个目标点（种子固定）。"""
    im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
    try: f = ImageFont.load_default(size=int(W * 0.24))
    except Exception: f = None
    if f is not None:
        d.text((W / 2, H * 0.46), "HELLO", font=f, fill=255, anchor="mm")
    else:  # 很旧的 Pillow：小字放大
        sm = Image.new("L", (60, 16), 0); ImageDraw.Draw(sm).text((2, 2), "HELLO", fill=255); im.paste(sm.resize((600, 160)), (60, int(H * 0.40)))
    ys, xs = np.nonzero(np.asarray(im) > 128); idx = rng.choice(len(xs), n, replace=len(xs) < n)
    return np.c_[xs[idx], ys[idx]].astype(np.float32)

class Film:
    def __init__(self, scale=1.0):
        self.s = scale; self.w, self.h = int(W * scale) // 2 * 2, int(H * scale) // 2 * 2
        rng = np.random.default_rng(SEED); n = 260
        self.ground = H * 0.62; self.center = np.array([W / 2, self.ground - 26], np.float32)
        ang = rng.uniform(0, 2 * np.pi, n); spd = rng.uniform(380, 900, n)
        self.vel = np.c_[np.cos(ang), np.sin(ang) * 0.8 - 0.35] * spd[:, None]          # 爆发初速度（夸张：偏向上）
        self.tgt = _targets(n, rng); self.size = rng.uniform(3.0, 6.5, n); self.swirl = rng.uniform(-1, 1, n)
        self.delay = rng.uniform(0, 0.5, n)                                              # 错开到达（避免齐步）
        lo = rng.random((H // 40 + 2, W // 40 + 2)).astype(np.float32)
        lo = np.asarray(Image.fromarray((lo * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
        self.paper = PAPER[None, None] * (0.965 + 0.05 * lo[..., None]) + rng.normal(0, 1.6, (H, W, 1))

    def particles(self, tau):
        """τ → 粒子位置（无状态，可随意跳帧）。"""
        e = max(0.0, tau - T_BURST); g = np.array([0, 520.0])
        fly = self.center + self.vel * (1 - np.exp(-2.2 * e))[..., None] / 2.2 + g * min(e, 0.8) ** 2 * 0.5
        flyend = self.center + self.vel * (1 - np.exp(-2.2 * (T_GATHER0 - T_BURST))) / 2.2 + g * 0.8 ** 2 * 0.5
        if tau < T_GATHER0: return fly
        u = ss(T_GATHER0 + self.delay, T_GATHER1 - 0.5 + self.delay, tau)[:, None]
        mid = (flyend + self.tgt) / 2 + np.c_[self.swirl * 220, -np.abs(self.swirl) * 160]   # 二次贝塞尔控制点 → 弧线
        pos = (1 - u) ** 2 * flyend + 2 * (1 - u) * u * mid + u ** 2 * self.tgt
        b = ss(T_GATHER1 - 0.3, T_GATHER1 + 0.5, tau)                                    # 定格段轻微呼吸，画面不死
        return pos + b * 1.6 * np.c_[np.sin(tau * 2.1 + self.swirl * 6), np.cos(tau * 1.7 + self.delay * 12)]

    def frame(self, T):
        tau = float(R.tau_of(T)); sp = float(R.speed(T)[0])
        img = Image.fromarray(np.clip(self.paper, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img, "RGBA")
        ink = tuple(int(c) for c in INK)
        d.line([(W * 0.18, self.ground + 2), (W * 0.82, self.ground + 2)], fill=ink + (40,), width=2)   # 地面线
        if tau < T_BURST:
            r = 26.0
            if tau < T_LAND:   # 下落：ease-in + 按速度拉伸
                k = (tau / T_LAND) ** 2; y = H * 0.08 + (self.ground - r - H * 0.08) * k
                st = 1 + 0.5 * k; sx, sy = 1 / st ** 0.5, st
            else:              # 落地挤压 → 预备动作：继续压扁蓄力，近定格
                q = ss(T_LAND, T_LAND + 0.08, tau) * (1 - ss(T_LAND + 0.08, T_FREEZE0, tau)) * 0.45 + ss(T_FREEZE0, T_BURST, tau) * 0.35
                sy = 1 - q; sx = 1 / sy; y = self.ground - r * sy
            d.ellipse([W / 2 - r * sx, y - r * sy, W / 2 + r * sx, y + r * sy], fill=ink)
            if tau > T_FREEZE0:  # 蓄力时一圈细光环
                a = ss(T_FREEZE0, T_BURST, tau); rr = 40 + 30 * a
                d.ellipse([W / 2 - rr, y - rr, W / 2 + rr, y + rr], outline=ACCENT + (int(140 * a),), width=2)
        else:
            p = self.particles(tau); trail = shutter_len(sp) * 0.9                       # 拖影长度随瞬时速度
            q = self.particles(max(T_BURST, tau - trail))
            for (x, y), (x0, y0), s in zip(p, q, self.size):
                d.line([(x0, y0), (x, y)], fill=ink + (110,), width=max(1, int(s * 0.8)))
                d.ellipse([x - s / 2, y - s / 2, x + s / 2, y + s / 2], fill=ink)
            if tau > T_GATHER1 - 0.2:   # 定格段：一条朱红下划线慢入
                k = ss(T_GATHER1 - 0.2, T_GATHER1 + 0.8, tau)
                d.line([(W / 2 - 200 * k, H * 0.55), (W / 2 + 200 * k, H * 0.55)], fill=ACCENT, width=5)
        flash = 0.07 * np.exp(-max(0.0, tau - T_BURST) * 9) if tau >= T_BURST else 0.0      # 爆发提亮 ≤0.07，不白屏
        a = np.asarray(img, np.float32) * (1 + flash) + 255 * flash * 0.3
        # 暗角
        yy, xx = np.ogrid[:H, :W]; v = 1 - 0.10 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        out = np.clip(a * v[..., None], 0, 255).astype(np.uint8)
        if self.s != 1.0: out = np.asarray(Image.fromarray(out).resize((self.w, self.h), Image.LANCZOS))
        return out

def _chunk(job):
    a, b, scale, path = job; F = Film(scale)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{F.w}x{F.h}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(a, b): p.stdin.write(F.frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); return path

def render(scale=1.0, workers=None):
    n = int(round(DUR * FPS)); nw = workers or min(8, os.cpu_count() or 2); tmp = tempfile.mkdtemp(prefix="hello_")
    e = np.linspace(0, n, nw + 1).astype(int); jobs = [(e[i], e[i + 1], scale, os.path.join(tmp, f"c{i:02d}.mp4")) for i in range(nw)]
    with Pool(nw) as pool: parts = pool.map(_chunk, jobs)
    lst = os.path.join(tmp, "l.txt"); open(lst, "w").write("".join(f"file '{q}'\n" for q in parts))
    os.makedirs(OUT, exist_ok=True); out = os.path.join(OUT, "picture.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", out], check=True)
    print(f"画面 → {out}  {n} 帧  {DUR:.2f}s")

def events():
    T = lambda tau: round(float(R.T_of(tau)), 3)
    ev = [{"t": 0.0, "type": "drone", "dur": round(DUR, 2), "gain": -20},
          {"t": 0.05, "type": "whoosh", "dur": 0.9, "gain": -14},
          {"t": T(T_LAND), "type": "thump", "gain": -6},
          {"t": T(T_FREEZE0), "type": "riser_pad", "dur": round(T(T_BURST) - T(T_FREEZE0), 2), "gain": -16},
          {"t": T(T_BURST), "type": "shatter", "gain": -8},
          {"t": T(T_BURST) + 0.02, "type": "whoosh", "dur": 0.7, "gain": -10, "pan": -0.3},
          {"t": T(T_GATHER0) + 0.3, "type": "whoosh", "dur": 1.2, "gain": -14, "pan": 0.3},
          {"t": T(T_GATHER1) - 0.1, "type": "sparkle", "gain": -12},
          {"t": T(T_GATHER1), "type": "chime", "gain": -8}]
    os.makedirs(OUT, exist_ok=True); p = os.path.join(OUT, "sfx_events.json"); json.dump(ev, open(p, "w"), indent=1)
    json.dump([["land", T(T_LAND)], ["freeze", T(T_FREEZE0)], ["burst", T(T_BURST)], ["gathered", T(T_GATHER1)]],
              open(os.path.join(OUT, "qc_events.json"), "w"))
    json.dump(KEYS, open(os.path.join(OUT, "keys.json"), "w")); print("音效事件 →", p)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "render"
    if cmd == "still":
        F = Film(); os.makedirs(OUT, exist_ok=True)
        for t in [float(x) for x in sys.argv[2:]] or [0.0]:
            p = os.path.join(OUT, f"still_{t:05.2f}.png"); Image.fromarray(F.frame(t)).save(p); print(p)
    elif cmd == "events": events()
    else:
        sc = float(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 1.0; render(sc)
