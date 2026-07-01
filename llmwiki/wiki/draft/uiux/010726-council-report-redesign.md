---
title: council-report-redesign
type: draft
status: proposed
tags: [redesign-existing-projects, output-report]
proposed: 2026-07-01
---

# 010726-council-report-redesign
**Type:** draft
**Status:** proposed
**Tags:** redesign-existing-projects, output-report
**Proposed:** 2026-07-01

## What
Redesign file `council.report.html` (Council Stage-4) — gỡ vân tay AI (purple/blue gradient, font hệ thống, 0 state) theo audit skill redesign-existing-projects.

## Output
Audit phát hiện & sửa 7 nhóm lỗi generic. Fix theo thứ tự ưu tiên:
1. **Font** — thay `-apple-system` → Fraunces (display serif) + Outfit (body) + JetBrains Mono (data), tabular-nums cho số.
2. **Palette** — bỏ nền "AI blue gradient" (`#d6e6ff`) → nền giấy warm-neutral (`#f4f1ea`) + radial ambient; gom về **1 accent brass** (`#8a6d2f`); 3 màu persona desaturate thành data-hue (plum/teal/amber).
3. **Surface** — thêm grain overlay (feTurbulence), tinted shadow theo hue nền.
4. **States** — hover lift trên card/kpi/row, transition 200–280ms, focus-visible ring, smooth-scroll.
5. **Semantic** — `<header>/<section>/<footer>` thay div soup; section header đánh số Fraunces sentence-case.
6. **Meta** — favicon SVG inline, meta description.
7. **Giữ nguyên** — escape HTML (fix Taleb), warning box verified:false (fix Kahneman), 100% số liệu từ transcript.

## Files
| File | Action |
|------|--------|
| `scratchpad/council-run/render_report.py` | modified (renderer) |
| `scratchpad/council-run/council.report.html` | regenerated (16.5 KB) |

## Notes
- Invoked via: `/redesign-existing-projects` skill
- Stack giữ nguyên: vanilla CSS trong template Python (không đổi framework).
- Deterministic: chạy lại `render_report.py` ra byte giống nhau.

## Origin
- **Draft:** `wiki/draft/uiux/010726-council-report-redesign.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
