#!/usr/bin/env python3
# Copyright (c) 2026 Link Liu (https://github.com/seelink-creet) — MIT License, see LICENSE
"""程序合成音效 + 按事件表放置（按动作类型分家、同类轮换变体、固定音高无滑音）。
  python3 sfx_synth.py events.json sfx.wav --dur 44 [--key 277.18] [--seed 1] [--stems stems_dir]
events.json: [{"t": 1.2, "type": "whoosh", "dur": 0.6, "gain": -6, "pan": 0.2}, ...]
type: whoosh / thump / tick / click / chime / sparkle / shatter / swell / riser_pad / breath_noise / drone
规则（来自多次修改）：不用弹簧滑音、卡通多普勒（音高抖动 ≤ ±0.5 半音）；“充能”用持续音不用上行滑音；
带音高的音效对位音乐的调（--key 给主音频率，用五声音阶）；同类音效轮换 3 个以上变体、不连用同一款；
画面变速时声音跟着：近定格 → 收成持续音/吸气/近乎无声；猛冲 → 涌起（swell）+ 低频气浪。
"""
import argparse, json, os
import numpy as np
SR = 48000

def _filt(x, lo=None, hi=None):
    try:
        from scipy import signal
        if lo and hi: return signal.sosfilt(signal.butter(2, [lo, hi], "band", fs=SR, output="sos"), x)
        if hi: return signal.sosfilt(signal.butter(2, hi, "low", fs=SR, output="sos"), x)
        if lo: return signal.sosfilt(signal.butter(2, lo, "high", fs=SR, output="sos"), x)
    except ImportError:  # 没有 scipy：一阶滤波近似
        y = np.copy(x)
        if hi:
            k = np.exp(-2 * np.pi * hi / SR)
            for i in range(1, len(y)): y[i] = (1 - k) * y[i] + k * y[i - 1]
        if lo: y = y - _filt(y, hi=lo)
        return y
    return x

def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(r, 1e-4))

def tt(d): return np.arange(int(SR * d)) / SR

class Synth:
    def __init__(self, seed=1, key=261.63):
        self.rng = np.random.default_rng(seed); self.key = key; self.count = {}
        self.pent = [key * 2 ** (s / 12) for s in (0, 2, 4, 7, 9)]
    def var(self, kind): i = self.count.get(kind, 0); self.count[kind] = i + 1; return i % 3      # 轮换 3 个变体
    def note(self, i): return self.pent[i % 5] * 2 ** (i // 5)
    def whoosh(self, d=0.6, v=0):
        n = int(SR * d); x = self.rng.standard_normal(n); c = [900, 1400, 600][v]
        y = _filt(x, c * 0.5, c * 2) * np.sin(np.pi * np.linspace(0, 1, n)) ** [1.5, 2.2, 1.2][v]
        return y + 0.6 * _filt(self.rng.standard_normal(n), hi=180) * np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    def thump(self, d=0.5, v=0):
        t = tt(d); f = [55, 62, 48][v]; return np.sin(2 * np.pi * f * t) * env(len(t), 0.003, 0.12) + 0.3 * _filt(self.rng.standard_normal(len(t)), hi=300) * env(len(t), 0.001, 0.04)
    def tick(self, d=0.08, v=0):
        n = int(SR * d); return _filt(self.rng.standard_normal(n), [2500, 3500, 1800][v], [6000, 8000, 5000][v]) * env(n, 0.0005, 0.012)
    def click(self, d=0.05, v=0):
        t = tt(d); return np.sin(2 * np.pi * [1800, 2400, 1500][v] * t) * env(len(t), 0.0003, 0.008)
    def chime(self, d=1.6, v=0, deg=None):
        t = tt(d); f = self.note(deg if deg is not None else [5, 7, 9][v]); y = 0 * t
        for k, (m, a) in enumerate([(1, 1), (2.76, .4), (5.4, .2), (8.9, .08)]): y += a * np.sin(2 * np.pi * f * m * t) * env(len(t), 0.002, 0.5 / (k + 1))
        return y
    def sparkle(self, d=0.9, v=0):
        y = np.zeros(int(SR * d))
        for j in range(8):
            c = self.chime(0.35, deg=10 + (j * 2 + v) % 7) * 0.25; i = int(self.rng.uniform(0, 0.5) * SR); y[i:i + len(c)] += c[:len(y) - i]
        return y
    def shatter(self, d=1.2, v=0):
        n = int(SR * d); y = _filt(self.rng.standard_normal(n), 2000, 9000) * env(n, 0.001, 0.25)
        for _ in range(30):
            i = int(self.rng.uniform(0, 0.6) * SR); c = self.tick(0.05, self.rng.integers(3)) * self.rng.uniform(.2, .8); y[i:i + len(c)] += c[:n - i]
        th = self.thump(0.5)[:n]; y[:len(th)] += th * 0.6
        return y
    def swell(self, d=2.0, v=0):
        t = tt(d); s = (t / d) ** 2; y = _filt(self.rng.standard_normal(len(t)), 200, 2500) * s
        for i in (0, 2, 4): y += 0.15 * np.sin(2 * np.pi * self.note(i) / 2 * t) * s
        return y * (1 - np.clip((t - d + 0.05) / 0.05, 0, 1))
    def riser_pad(self, d=3.0, v=0):            # “充能”：持续音，不滑音，亮度随时间打开
        t = tt(d); y = sum(np.sin(2 * np.pi * self.note(i) * t + k) for k, i in enumerate((0, 2, 4)))
        return _filt(y, hi=3000) * np.minimum(1, t / 0.5) * (0.4 + 0.6 * t / d)
    def breath_noise(self, d=1.0, v=0):
        n = int(SR * d); return _filt(self.rng.standard_normal(n), 300, 2500) * np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5 * 0.5
    def drone(self, d=4.0, v=0):
        t = tt(d); return (np.sin(2 * np.pi * self.key / 4 * t) + 0.4 * np.sin(2 * np.pi * self.key / 2 * t)) * np.minimum(1, t / 0.8) * np.minimum(1, (d - t) / 0.8)

def place(events, dur, seed=1, key=261.63):
    S = Synth(seed, key); out = np.zeros((int(SR * dur), 2)); stems = {}
    for e in sorted(events, key=lambda e: e["t"]):
        k = e["type"]; v = S.var(k); x = getattr(S, k)(e.get("dur", None) or getattr(S, k).__defaults__[0], v)
        x = x / (np.abs(x).max() + 1e-9) * 10 ** (e.get("gain", -6) / 20); p = e.get("pan", 0.0)
        st = np.c_[x * np.sqrt((1 - p) / 2), x * np.sqrt((1 + p) / 2)]; i = int(e["t"] * SR); j = min(len(out), i + len(st))
        if i >= len(out): continue
        out[i:j] += st[: j - i]; stems.setdefault(k, np.zeros_like(out))[i:j] += st[: j - i]
    return out, stems

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("events"); ap.add_argument("out"); ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--seed", type=int, default=1); ap.add_argument("--key", type=float, default=261.63); ap.add_argument("--stems")
    a = ap.parse_args(); out, stems = place(json.load(open(a.events)), a.dur, a.seed, a.key)
    import wave
    def save(p, y):
        y = np.clip(y, -1, 1); w = wave.open(p, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype("<i2").tobytes()); w.close()
    save(a.out, out); print("→", a.out, f"峰值 {20 * np.log10(np.abs(out).max() + 1e-9):.1f} dBFS（混音时整条总线再调）")
    if a.stems:
        os.makedirs(a.stems, exist_ok=True)
        for k, y in stems.items(): save(os.path.join(a.stems, f"stem_{k}.wav"), y)
