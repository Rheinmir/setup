---
type: draft
title: 250626-harness-arch-vs-current
status: proposed
tags: [docs-site-macos, output-report]
timestamp: 2026-06-25
---

# 250626-harness-arch-vs-current

**Status:** proposed

## What
Docs site trực quan đối chiếu kiến trúc harness ĐỀ XUẤT (1 lõi validator CLI vendor-free + policy.yaml + caller mỏng + CI gate) với LUỒNG HIỆN TẠI (validators .py copy per-project, hook Claude-only, sync-template hash 3 mốc).

## Output
- HTML self-contained 6 section: (01) luồng hiện tại + 3 cái đau; (02) luồng đề xuất 1-lõi-nhiều-caller; (03) đối chiếu trực diện + bảng; (04) sequence "1 lệnh ghi raw/ đi đâu" current vs new; (05) phân phối copy+sync vs release pin version; (06) ma trận quyết định 2 trục (đa-vendor + hợp tác).
- Diagram kéo-thả, code-copy, ripple, sidebar collapse, scroll spy.

## Files
| File | Action |
|------|--------|
| `llmwiki/html/250626-harness-architecture-vs-current.html` | created |

## Notes
- Invoked via: `/docs-site-macos` skill
- Quyết định người dùng: đa-vendor thật + agent hợp tác → CLI vendor-free + CI, không sandbox.
- Preview: http://localhost:8765/llmwiki/html/250626-harness-architecture-vs-current.html

## Origin
- **Draft:** `wiki/sources/draft/250626-harness-arch-vs-current.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
