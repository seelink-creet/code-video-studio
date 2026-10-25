# 作者与许可 / Authorship & licence

| 项目 Field | 值 Value |
|---|---|
| 作者 Author | Link Liu |
| 链接 Link | https://github.com/seelink-creet |
| 版权年份 Year | 2026 |
| 文档与文字 Docs & text（全部 .md） | CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/ |
| 代码 Code（scripts/、examples/） | MIT（全文见 / full text in `LICENSE`） |

署名格式 / Credit line：“code-video-studio by Link Liu (https://github.com/seelink-creet), CC BY 4.0”

## 若要把文档许可改为非商用 / To switch the docs to non-commercial (CC BY-NC 4.0)
只改许可声明所在的文件（`references/` 里讲音乐许可的 “CC BY 4.0” 不能动）。
Only touch the licence-statement files (the "CC BY 4.0" mentions about music licences in `references/` must stay).
```bash
cd code-video-studio
sed -i -e 's|CC BY 4.0|CC BY-NC 4.0|g' -e 's|licenses/by/4.0/|licenses/by-nc/4.0/|g' \
  LICENSE AUTHORS.md README.md en/README.md
sed -i -e 's|Docs CC BY 4.0|Docs CC BY-NC 4.0|' SKILL.md en/SKILL.md
```
（macOS 用 `sed -i ''`。On macOS use `sed -i ''`.）代码始终是 MIT。The code stays MIT.
