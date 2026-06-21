# Operation Log

## 2026-04-28 — init — Knowledge Base initialized
- Created folder structure: concepts/, entities/, sources/, sources/draft/
- Created wiki/index.md, wiki/log.md
- Created AGENT.md

## 2026-06-15 — docs-site-macos — okf-docs-site
- last30days research on Google Open Knowledge Format (OKF) v0.1
- Built llmwiki/html/150626-open-knowledge-format.html
- 2026-06-15 08:01 — session `7b1793e9` — 2 tool calls — files: 150626-okf-docs-site.md, 150626-open-knowledge-format.html
- 2026-06-15 08:02 — session `7b1793e9` — 2 tool calls — files: 150626-okf-docs-site.md, 150626-open-knowledge-format.html
- Added Vietnamese version: llmwiki/html/150626-open-knowledge-format-vi.html (cross-linked EN↔VI)

## 2026-06-19 — install-harness — mode=migrate
- Cài harness L0–L4 (validators, hooks, pre-commit, wiki-health, health-check, evals)

## 2026-06-19 — harness-update — migrate xong, nợ đã backfill: 0 file
- Source: branch `orca` (template v1.0.0, newest 2026-06-18). rc=0 → wiki sạch, không có nợ R2/R3.
- 3 hàng rào tự kiểm: R1 ghi raw/, R2 thiếu ## Origin, R5 lạc wiki/ root → đều BỊ CHẶN ✓.

## 2026-06-19 — orca-workflow/propose — kế hoạch refactor OKF v0.1
- Tạo draft `sources/draft/190626-okf-refactor-llmwiki.md` (5 task: convert files, templates, skills, validator R8, conformance) + seq HTML `html/190626-okf-refactor-seq.html`.
- Nguồn chuẩn: `html/150626-open-knowledge-format-vi.html`. STOP — chờ gate duyệt trước khi thực thi.

## 2026-06-19 — orca-workflow/execute — refactor OKF v0.1 (approved)
- T1 convert `150626-okf-docs-site.md` → YAML frontmatter. T2 4× `_template.md` → frontmatter.
- T3 skill ingest/propose/query thêm rule OKF (R9). T4 validator **R9 `okf_frontmatter.py`** + wire policy.yaml + post_tool_use hook + pre-commit (R8 đã dùng cho pattern-sync → đặt R9).
- T5 concept `concepts/okf-conformance.md`. 3 tiêu chí OKF v0.1 đều pass.

## 2026-06-20 — docs-site-macos — okf-refactor-report
- Tạo `html/200626-okf-refactor-report.html` (6 section, 6 SVG kéo-thả, self-contained) báo cáo toàn chuỗi migrate + OKF refactor.
- Draft output-report `sources/draft/200626-okf-refactor-report.md`. Preview cổng 8765.
