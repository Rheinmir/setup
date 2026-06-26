---
type: draft
title: 250626-harness-poc-vendor-neutral
status: proposed
tags: [harness, poc, output-report]
timestamp: 2026-06-25
---

# 250626-harness-poc-vendor-neutral

**Status:** proposed

## What
PoC chạy được: lõi gác cổng vendor-neutral (1 CLI đọc policy.yaml) + sinh wiring cho 6 vendor + CI/pre-commit, KHÔNG dùng MCP. Chứng minh kiến trúc trong 250626-harness-architecture-vs-current.html.

## Output
- `bin/llmwiki-validate.py` — lõi: modes path/files/claude-hook, exit 2=chặn(session)/1=fail(repo)/0=ok, fail-open.
- `policy.yaml` — nguồn chân lý (R1 no_write_raw session-only, R2 require_origin session+repo).
- `gen-converters.py` — sinh 9 file wiring (Claude hook→CLI, opencode permission.edit:deny + plugin, Antigravity Deny-rule, Cursor/Codex/Kiro advisory, CI, pre-commit).
- `demo.sh` — 13 assertion, tất cả PASS: chặn raw/ ở session, cho phép con người commit raw/ ở repo, require_origin, fail-open.
- `test-broad.sh` — 54/54 PASS: false-positive guard (coleslaw/draw/raws/myraw không chặn nhầm), path normalize, bash detect + hợp lệ, require_origin biên (## 2-space ok, ## Origins/h3 chặn, excluded, ngoài target glob), files-mode lô, claude-hook hỏng, fail-open, reason đúng [R1]/[R2].
- **KNOWN GAPS (có chủ đích):** lõi session KHÔNG bắt `python -c open(w)`, `rm raw/`, `sed -i <script> raw/` → khẳng định sàn đảm bảo ở CI/sandbox.

## Files
| File | Action |
|------|--------|
| `harness/poc-vendor-neutral/policy.yaml` | created |
| `harness/poc-vendor-neutral/bin/llmwiki-validate.py` | created |
| `harness/poc-vendor-neutral/gen-converters.py` | created |
| `harness/poc-vendor-neutral/demo.sh` | created |
| `harness/poc-vendor-neutral/README.md` | created |
| `harness/poc-vendor-neutral/out/*` | generated (9 file) |

## Notes
- Chạy: `bash harness/poc-vendor-neutral/demo.sh` → 13 PASS · 0 FAIL.
- layer session vs repo do policy `enforce_at` lái, không hard-code.
- Sàn đảm bảo = CI + pre-commit (advisory bị lờ ở mọi vendor non-Claude — đã verify).

## Origin
- **Draft:** `wiki/sources/draft/250626-harness-poc-vendor-neutral.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
