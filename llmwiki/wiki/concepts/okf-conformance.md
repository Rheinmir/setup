---
type: concept
title: OKF v0.1 conformance của llmwiki
tags: [okf, conformance, harness, frontmatter]
timestamp: 2026-06-19
---

# OKF v0.1 Conformance

Ánh xạ giữa knowledge base `llmwiki/wiki/` và **Open Knowledge Format (OKF) v0.1** (Google Cloud, 2026-06-12). Sau refactor [[190626-okf-refactor-llmwiki]], bộ wiki này là một **OKF bundle hợp lệ**: mỗi concept là một file Markdown có YAML frontmatter parse được với trường `type` không rỗng.

## 3 tiêu chí hợp lệ OKF v0.1
| # | Tiêu chí OKF | Thực thi trong llmwiki |
|---|--------------|------------------------|
| 1 | Mọi file .md không-dành-riêng có frontmatter parse được | Validator **R9** `okf_frontmatter.py` (pre-tool + post-tool + pre-commit) |
| 2 | Mọi frontmatter có `type` không rỗng | R9 kiểm `type` qua `yaml.safe_load` (fallback regex nếu thiếu pyyaml) |
| 3 | File dành riêng theo cấu trúc spec | Reserved set bên dưới; R5 `folder_structure.py` giữ vị trí file |

## Trường frontmatter
- **Bắt buộc:** `type` — chuỗi ngắn (`concept`, `entity`, `source`, `draft`, …).
- **Tùy chọn (nên có):** `title`, `description`, `resource`, `tags`, `timestamp`.
- **Tương thích về sau:** khóa lạ được dung thứ (vd `status` ở draft) — R9 KHÔNG fail vì khóa ngoài spec.

## Reserved filenames (miễn yêu cầu concept)
File cấu trúc/chỉ mục, không phải concept: `index.md`, `log.md`, `README.md`, `decisions.md`, `active-context.md`, `_template.md`. Khớp `R5 allow_root_files` + `SKIP_BASENAMES` của R9.

## Notes
- Nguồn chuẩn: [[150626-okf-docs-site]] + `llmwiki/html/150626-open-knowledge-format-vi.html`.
- OKF xếp tầng với llms.txt (signpost) + MCP (tool sống) — chỉ chuẩn hóa lớp lưu trữ tri thức, không thay thế chúng.

## Origin
- **Source:** `wiki/sources/draft/190626-okf-refactor-llmwiki.md` (task T5)
- **Commit:** _(if created from code change)_
- **Date:** 2026-06-19
