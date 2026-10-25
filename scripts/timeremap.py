#!/usr/bin/env python3
# Copyright (c) 2026 Link Liu (https://github.com/seelink-creet) — MIT License, see LICENSE
"""时间重映射（变速）。关键帧是 (故事时间 tau, 速度 s=dτ/dT)，相邻关键帧之间在【输出时间】里做 smoothstep 过渡，
所以每段时长 = Δτ / mean(s0, s1)，总时长可预知。渲染时画 frame(tau_of(T))：真正的慢动作，不复制帧。

用法（库）：
    from timeremap import Remap
    R = Remap([(0, 1), (4.9, 1), (5.0, 0.07), (5.1, 0.07), (5.3, 3.6), (8, 1)])
    R.duration            # 输出总时长（秒）
    R.tau_of(T)           # 输出时间 → 故事时间
    R.speed(T)            # 输出时间的瞬时速度（可用来缩放运动模糊/拖影）
    R.T_of(tau)           # 故事时间的事件 → 输出时间（给配乐/音效对点）
命令行：python3 timeremap.py keys.json [plot.png]    keys.json = [[tau, speed], ...]
"""
import json, sys
import numpy as np

class Remap:
    def __init__(self, keys, res=20000):
        k = np.asarray(keys, float)
        assert np.all(np.diff(k[:, 0]) > 0) and np.all(k[:, 1] > 0), "tau 必须递增，速度必须 > 0"
        self.ktau, self.kv = k[:, 0], k[:, 1]
        self.kt = np.r_[0, np.cumsum(np.diff(self.ktau) / (0.5 * (self.kv[1:] + self.kv[:-1])))]
        self.duration = float(self.kt[-1])
        T = np.linspace(0, self.duration, int(self.duration * res) + 2)
        s = self.speed(T)
        self._T, self._tau = T, self.ktau[0] + np.r_[0, np.cumsum(np.diff(T) * 0.5 * (s[1:] + s[:-1]))]

    def speed(self, T):
        T = np.atleast_1d(np.asarray(T, float))
        i = np.clip(np.searchsorted(self.kt, T, side="right") - 1, 0, len(self.kt) - 2)
        u = np.clip((T - self.kt[i]) / (self.kt[i + 1] - self.kt[i]), 0, 1)
        u = u * u * (3 - 2 * u)
        return self.kv[i] * (1 - u) + self.kv[i + 1] * u

    def tau_of(self, T): return np.interp(T, self._T, self._tau)
    def T_of(self, tau): return np.interp(tau, self._tau, self._T)

def shutter_len(speed, base=1 / 48, k=0.55):
    """拖影/快门长度（故事时间秒）随瞬时速度变化：定格时是清晰的点，冲刺时是长拖影。"""
    return speed * (1 + k * np.maximum(speed - 1, 0)) * base

if __name__ == "__main__":
    R = Remap(json.load(open(sys.argv[1])))
    print(f"输出时长 {R.duration:.3f}s")
    for tau, s in zip(R.ktau, R.kv): print(f"  tau={tau:7.3f}  speed={s:5.2f}  → T={float(R.T_of(tau)):7.3f}s")
    if len(sys.argv) > 2:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        T = np.linspace(0, R.duration, 3000)
        fig, ax = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
        ax[0].plot(T, R.speed(T) * 100); ax[0].set_yscale("log"); ax[0].set_ylabel("speed %"); ax[0].grid(alpha=.3)
        ax[1].plot(T, R.tau_of(T)); ax[1].set_ylabel("story time τ"); ax[1].set_xlabel("output time T (s)"); ax[1].grid(alpha=.3)
        plt.tight_layout(); plt.savefig(sys.argv[2], dpi=100); print("曲线图 →", sys.argv[2])
