# code-video-studio (English)

An AI-agent skill for making short films entirely with code: talk through the brief → 2–3 style directions with an editable beat sheet → lookdev → full render after approval → automatic QC → honest self-review → revisions → delivery (chat version, HD, covers, post copy with credits). The Chinese `SKILL.md` at the package root is primary; this folder is the English version (`en/SKILL.md`, `en/references/`). Scripts, templates and the example are shared.

## Install
Dependencies: Python ≥3.9, ffmpeg; `pip install numpy pillow scipy opencv-python-headless soundfile matplotlib pyloudnorm librosa pretty_midi`; then `python3 scripts/check_env.py`.

| Tool | Where |
|---|---|
| Claude Code | copy the whole package to `~/.claude/skills/code-video-studio/` or `.claude/skills/` in a project; for English, rename `en/SKILL.md` to replace the root SKILL.md (keep the paths it references) |
| Codex | `~/.codex/skills/code-video-studio/` if your version supports skills; otherwise put it in the project and add to `AGENTS.md`: "When asked to make a video with code, read code-video-studio/en/SKILL.md and follow it." |
| Cursor | put it in the project and add a rule in `.cursor/rules/` (or `AGENTS.md`) pointing to `code-video-studio/en/SKILL.md` |
| Other AI coding tools | import SKILL.md and references as skills/knowledge/custom instructions, or tell the agent at the start: "Read code-video-studio/en/SKILL.md first and follow it." |
Skill folder conventions change; check your tool's current docs.

## Quick test
`cd examples/hello-film && python3 run_all.py` renders a ~10 s demo end to end (seeded render, speed ramp, synthesized SFX, master after AAC, QC plots, contact sheet, HD/chat/cover).

## Credits & licence
Author: Link Liu (https://github.com/seelink-creet), © 2026. Docs and text (all .md files): CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/); please credit "code-video-studio by Link Liu". Code (scripts/, examples/): MIT, see `LICENSE`. Third-party music, SFX, fonts and samples used in your films are not covered; verify and credit each one.
