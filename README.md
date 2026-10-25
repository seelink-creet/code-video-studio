# code-video-studio · 用代码做短片的 AI 技能包

让 AI 编程助手和你一起，从一个主题做出完整短片：聊需求 → 给 2–3 个风格方向和可改的分镜 → 出样张 → 你同意后渲全片 → 自动质检 → 诚实自评 → 按你的意见修改 → 交付（聊天版、高清版、封面、带署名的发布文案）。画面全部由代码逐帧生成。

## 目录
```
code-video-studio/
├── SKILL.md                 入口：分阶段工作流、每阶段问用户的问题和闸门
├── references/              菜单与规则（AI 按需读取）
│   ├── techniques_catalog.md   技术路线（已验证/未验证、难度）
│   ├── style_menu.md           视觉风格
│   ├── story_templates.md      节拍表模板
│   ├── animation_principles.md 动画 12 法则 + 代码做法
│   ├── music_sound.md          配乐、音效、许可、混音
│   ├── qc_checklist.md         质检清单
│   ├── review_template.md      自评模板
│   └── tech_pitfalls.md        已验证的技术坑
├── templates/               STORYBOARD / STYLE / PUBLISH / NOTES 模板
├── scripts/                 通用脚本（只依赖 Python + ffmpeg）
├── examples/hello-film/     10 秒完整示例（可选）：python3 run_all.py
├── en/                      English version（可选）
├── LICENSE                  双许可（文档 CC BY 4.0 / 代码 MIT）
└── AUTHORS.md               作者占位符与替换命令
```

## 安装
先装依赖：Python ≥3.9、ffmpeg；`pip install numpy pillow scipy opencv-python-headless soundfile matplotlib pyloudnorm librosa pretty_midi`。然后运行 `python3 scripts/check_env.py` 检查。

| 工具 | 放哪里 |
|---|---|
| Claude Code | 复制整个文件夹到 `~/.claude/skills/code-video-studio/`（全局）或项目内 `.claude/skills/code-video-studio/`；SKILL.md 的 frontmatter 会被自动识别 |
| Codex（CLI/IDE） | 放到 `~/.codex/skills/code-video-studio/`（若你的版本支持 skills）；否则放进项目目录，并在项目 `AGENTS.md` 里加一句：“做代码视频时，先读 `code-video-studio/SKILL.md` 并按它执行。” |
| Cursor | 放进项目目录，在 `.cursor/rules/` 新建一条规则（或 `AGENTS.md`）写：“当用户要求用代码做视频/动画时，读取并遵循 `code-video-studio/SKILL.md`。” |
| WorkBuddy / 其他国内 AI 编程工具 | 若支持“技能/知识库/自定义指令”，导入 SKILL.md 和 references；否则把文件夹放进工作区，开场对 AI 说：“请先阅读 code-video-studio/SKILL.md，按里面的流程和我一起做视频。” |
| 任何聊天型 AI | 上传 SKILL.md（和需要的 references 文件），让它按流程走；脚本需要能在本机运行 Python 的环境 |

> 各工具的技能目录约定会变，以工具当前文档为准。

## 脚本速查
| 脚本 | 用途 |
|---|---|
| `check_env.py` | 检查依赖，给缺失时的替代方案 |
| `render_skeleton.py` | 逐帧确定性渲染骨架：`still`（关键帧）、`sheet`（联系表）、`render`（多进程全片） |
| `timeremap.py` | 变速曲线（真慢镜），事件时刻换算，画速度曲线 |
| `contact_sheet.py` | 联系表 / 动作条 / 全分辨率裁切 |
| `qc_motion.py` | 帧差 + 音频电平 + 变速曲线 + 事件线；突变、黑白帧、静止过久、首尾呼应检查 |
| `sfx_synth.py` | 程序合成音效并按事件表放置（同类轮换、固定音高无滑音） |
| `music_fit.py` | 库曲分析段落入口；让入口落在画面节拍；小节线多段拼接 |
| `master_audio.py` | 两遍响度标准化 + 封装 + AAC 后复测真峰值并自动回退 |
| `deliver.py` | 高清版 / 聊天版（按目标体积算码率）/ 封面 |

快速试跑（约 1 分钟）：
```
cp scripts/render_skeleton.py scripts/contact_sheet.py my_film/ && cd my_film
python3 render_skeleton.py still 0 2 && python3 render_skeleton.py render --scale 0.5
python3 ../scripts/master_audio.py out/picture.mp4 some.wav final.mp4
python3 ../scripts/deliver.py final.mp4 --name demo --cover-at 1
```

## 作者与许可 / Credits & licence
- 作者 Author：Link Liu（https://github.com/seelink-creet），© 2026
- 文档与文字（SKILL.md、references/、templates/、en/ 等 .md 文件）：CC BY 4.0（https://creativecommons.org/licenses/by/4.0/）。转载或改编请署名：“code-video-studio，作者 Link Liu”。
  Docs and text (all .md files): CC BY 4.0. Please credit “code-video-studio by Link Liu”.
- 代码（scripts/、examples/）：MIT，全文见 `LICENSE`。Code (scripts/, examples/): MIT, full text in `LICENSE`.
- 你在片子里用到的第三方音乐、音效、字体、采样不在本许可内，请按 `references/music_sound.md` 逐条核对并署名。
  Third-party music, SFX, fonts and samples used in your films are not covered; verify and credit each one.
- 占位符与一键替换方法见 `AUTHORS.md`（也可在那里把文档许可改为 CC BY-NC 4.0）。
  Placeholders and the one-line replace command are in `AUTHORS.md` (including switching the docs to CC BY-NC 4.0).
