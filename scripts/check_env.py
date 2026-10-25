#!/usr/bin/env python3
# Copyright (c) 2026 Link Liu (https://github.com/seelink-creet) — MIT License, see LICENSE
"""检查做代码视频需要的工具，并给出缺失时的替代方案。用法: python3 check_env.py"""
import importlib, shutil, subprocess, sys

def ver(cmd):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return (out.stdout or out.stderr).strip().splitlines()[0][:80]
    except Exception:
        return None

print(f"Python {sys.version.split()[0]}", "OK" if sys.version_info >= (3, 9) else "（建议 ≥3.9）")
rows = [
    # (模块, 是否必需, 用途, 缺失时)
    ("numpy", True, "逐帧数组运算", "pip install numpy"),
    ("PIL", True, "绘制/字体/合成 (Pillow)", "pip install pillow"),
    ("scipy", False, "滤波、插值、KD 树、音频滤波", "pip install scipy；没有时用 numpy 简化"),
    ("cv2", False, "快速线条/重映射/模糊 (opencv-python)", "pip install opencv-python-headless；没有时用 PIL"),
    ("soundfile", False, "读写 wav", "pip install soundfile；没有时用标准库 wave"),
    ("matplotlib", False, "QC 曲线图", "pip install matplotlib；没有时只输出 CSV"),
    ("pyloudnorm", False, "响度测量", "pip install pyloudnorm；没有时只用 ffmpeg ebur128"),
    ("librosa", False, "库曲节拍/段落分析", "pip install librosa；没有时手动听段落时间"),
    ("pretty_midi", False, "写 MIDI 乐谱", "pip install pretty_midi"),
    ("cairosvg", False, "SVG/矢量角色光栅化", "pip install cairosvg（需系统 cairo）"),
    ("colour", False, "色彩科学计算 (colour-science)", "pip install colour-science"),
]
missing_req = []
for mod, req, use, fix in rows:
    try:
        importlib.import_module(mod); st = "OK"
    except Exception:
        st = "缺失"; missing_req += [mod] if req else []
    print(f"  [{st:>2}] {mod:<12} {'必需' if req else '可选'}  {use}" + ("" if st == "OK" else f"  → {fix}"))

print("\n命令行工具：")
tools = [
    ("ffmpeg", ["ffmpeg", "-version"], True, "编码/混音/测响度。必须安装：apt/brew/winget install ffmpeg"),
    ("ffprobe", ["ffprobe", "-version"], True, "读视频信息，随 ffmpeg 安装"),
    ("node", ["node", "--version"], False, "Remotion / Motion Canvas / p5 / three.js 路线需要；没有时走 Python 路线"),
    ("manim", ["manim", "--version"], False, "数学讲解路线（pip install manim，需 LaTeX 可选）；没有时用 PIL 画公式"),
    ("blender", ["blender", "--version"], False, "真 3D 路线（blender -b -P script.py）；没有时用 numpy 透视投影 2.5D"),
    ("fluidsynth", ["fluidsynth", "--version"], False, "SoundFont 渲染 MIDI；没有时用纯 numpy 合成或库曲"),
    ("chrome", None, False, "浏览器逐帧截图（HTML/three.js/p5 路线）；可用 Playwright 自带 Chromium"),
]
for name, cmd, req, note in tools:
    if cmd is None:
        p = next((shutil.which(x) for x in ("google-chrome", "chromium", "chromium-browser", "chrome") if shutil.which(x)), None)
        v = p
    else:
        v = ver(cmd) if shutil.which(cmd[0]) else None
    print(f"  [{'OK' if v else '缺失':>2}] {name:<10} {'必需' if req else '可选'}  {v or note}")
    if req and not v: missing_req.append(name)

if shutil.which("ffmpeg"):
    enc = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    for e in ("libx264", "aac"):
        print(f"  ffmpeg 编码器 {e}: {'OK' if e in enc else '缺失（换一个完整版 ffmpeg）'}")
print("\n结论：", "可以开始。" if not missing_req else f"先安装：{', '.join(missing_req)}")
