---
type: draft
title: Báo cáo HTML — harness migrate + OKF v0.1 refactor
status: proposed
tags: [docs-site-macos, output-report, okf, harness]
timestamp: 2026-06-20
---

# 200626-okf-refactor-report

**Status:** proposed

## What
Dựng một docs site macOS liquid-glass (single-file, self-contained) báo cáo kết quả chuỗi `/sync-template` → `/harness-update` (migrate harness L0–L4) → `/orca-workflow` (refactor llmwiki sang chuẩn OKF v0.1, validator R9).

## Output
- Site 6 section: Tổng quan · Audit & quyết định · Harness migrate · OKF v0.1 refactor · Hàng rào R9 · Nghiệm thu.
- 6 SVG diagram kéo-thả từng node, nav sidebar collapse + ripple, scrollbar overlay tự ẩn, code-copy, scroll-spy — 0 dependency, mở offline được.
- Đính chính số hiệu: validator mới là **R9** (R8 đã dùng cho pattern-sync-health).

## Files
| File | Action |
|------|--------|
| `llmwiki/html/200626-okf-refactor-report.html` | created |

## Notes
- Invoked via: `/docs-site-macos` skill
- Preview: http://localhost:8765/llmwiki/html/200626-okf-refactor-report.html
- Nguồn dữ liệu: [[190626-okf-refactor-llmwiki]], [[okf-conformance]], [[150626-okf-docs-site]]

## Origin
- **Draft:** `wiki/sources/draft/200626-okf-refactor-report.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
