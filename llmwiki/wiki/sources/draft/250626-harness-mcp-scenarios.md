---
type: draft
title: 250626-harness-mcp-scenarios
status: proposed
tags: [docs-site-macos, output-report]
timestamp: 2026-06-25
---

# 250626-harness-mcp-scenarios

**Status:** proposed

## What
Docs site (macOS glass, single-file HTML) giải thích việc biến harness thành MCP server, ranh giới hook vs MCP, cơ chế sync-template tự khai báo server, tự check/update từ xa, và 2 kịch bản triển khai (mới trắng vs đang dở).

## Output
- Trang HTML self-contained 6 section: (01) Harness ≠ MCP — lớp chặn phải ở hook; (02) kiến trúc hybrid; (03) sync-template tự khai báo `.mcp.json` + llmwiki tự add; (04) tự check liên tục ≠ tự apply; (05) KB mới trắng (NEW); (06) KB đang dở (MIGRATE) + bẫy legacy thiếu `remote_synced`.
- Diagram kéo-thả, code-copy, ripple liquid-glass, sidebar collapse, scroll spy.

## Files
| File | Action |
|------|--------|
| `llmwiki/html/250626-harness-mcp-scenarios.html` | created |

## Notes
- Invoked via: `/docs-site-macos` skill
- Preview: `http://localhost:8765/llmwiki/html/250626-harness-mcp-scenarios.html`
- Nội dung distill từ thảo luận: lớp chặn (L1 hooks/validators) không chuyển MCP được; phần công cụ/đọc (sync, health, okf, wiki query) + check-drift nền thì nên là MCP.

## Origin
- **Draft:** `wiki/sources/draft/250626-harness-mcp-scenarios.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
