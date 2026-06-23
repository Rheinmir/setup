---
type: source
title: sync-template
status: stub
tags: [sync-template, harness, pattern-version]
timestamp: 2026-06-24
---

# sync-template

**Type:** skill-reference
**Tags:** sync-template, harness, pattern-version

Skill đồng bộ template harness từ remote (`rheinmir/setup` nhánh `orca`) về project local.
Khi `health-check.py` phát hiện version local < remote, lời nhắc `/sync-template` được hiển thị cuối phiên.

## Luồng

1. Step 0 (health-check trước): chạy `health-check.py` xác nhận baseline
2. Sync core files từ remote về local
3. Step 6b (refresh version.json sau sync)

## Liên quan

- [[150626-health-check-pattern-sync]] — session-start health-check tích hợp với sync-template

## Origin

- Skill file: `llmwiki/skills/utils/sync-template.md`
- legacy backfill (harness-update) — stub tạo để giải broken wikilink
