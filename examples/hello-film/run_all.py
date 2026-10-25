#!/usr/bin/env python3
# Copyright (c) 2026 Link Liu (https://github.com/seelink-creet) — MIT License, see LICENSE
"""一键跑完整个示例：渲染 → 音效 → 母带（AAC 后实测）→ 质检 → 联系表 → 交付。约 1–3 分钟。"""
import os, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(H, "..", "..", "scripts"); O = os.path.join(H, "out")
py = sys.executable
def run(*a): print("$", " ".join(os.path.basename(x) if os.sep in x else x for x in a), flush=True); subprocess.run(a, check=True, cwd=O if os.path.isdir(O) else H)
os.makedirs(O, exist_ok=True)
run(py, os.path.join(H, "film.py"), "still", "0.8", "2.0", "5.0", "9.0")
run(py, os.path.join(H, "film.py"), "render")
run(py, os.path.join(H, "film.py"), "events")
import json; dur = sum(1 for _ in [0]) and float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                                                os.path.join(O, "picture.mp4")], capture_output=True, text=True).stdout)
run(py, os.path.join(S, "sfx_synth.py"), os.path.join(O, "sfx_events.json"), os.path.join(O, "sfx.wav"), "--dur", f"{dur:.3f}", "--key", "293.66", "--seed", "3")
run(py, os.path.join(S, "master_audio.py"), os.path.join(O, "picture.mp4"), os.path.join(O, "sfx.wav"), os.path.join(O, "final.mp4"), "--lufs", "-14", "--tp", "-1")
run(py, os.path.join(S, "qc_motion.py"), os.path.join(O, "final.mp4"), os.path.join(O, "qc_motion.png"), "--keys", os.path.join(O, "keys.json"),
    "--events", os.path.join(O, "qc_events.json"))
run(py, os.path.join(S, "contact_sheet.py"), "sheet", os.path.join(O, "final.mp4"), os.path.join(O, "sheet.png"), "--every", "0.5", "--width", "160")
run(py, os.path.join(S, "deliver.py"), os.path.join(O, "final.mp4"), "--name", "hello", "--chat-mb", "3", "--chat-height", "960", "--cover-at", "9.0")
print("\n完成。看 out/sheet.png、out/qc_motion.png，播放 out/hello_chat.mp4。")
