---
type: draft
title: Output report — trang docs harness 23/06 (docs-gate + orca_guard)
tags: [docs-site-macos, output-report, harness]
timestamp: 2026-06-23
---

# 230626-harness-docs-gate-orca-guard-report

**Status:** report

## What

Tạo 1 trang HTML single-file (docs-site-macos, liquid-glass) tổng hợp đợt việc harness 2026-06-23.

## Output

Trang 4 section + SVG kéo-thả + copy code + ripple + sidebar scroll-spy:
1. docs-gate hook R10 (UserPromptSubmit, mỗi 5 prompt)
2. orca_guard.py (L1 PreToolUse: block status sai + inject id-trap)
3. Bug + bài học orca CLI (2 id, status enum)
4. 15 golden questions promptfoo

## Files

| File | Action |
|------|--------|
| `llmwiki/html/230626-harness-docs-gate-orca-guard.html` | created |

## Notes

- Invoked via: `/docs-site-macos` skill (Claude fallback trong chuỗi opencode→agy→claude — nội dung nằm trong context, skill Claude-native).

## Origin

- **Source:** `wiki/sources/draft/230626-harness-docs-gate-orca-guard-report.md` — output report của skill docs-site-macos, phiên 2026-06-23.
- **Date:** 2026-06-23
