---
type: draft
title: orca_guard.py — L1 PreToolUse guard cho orca orchestration CLI
tags: [harness, hook, L1-adapter, orca, guard]
timestamp: 2026-06-23
---

# Proposal: orca_guard.py — chặn lỗi orca CLI bằng máy, không bằng prose

**Status:** implemented (2026-06-23 — T1+T2 claude-cli, T3 opencode smoke 4/4 PASS)

## Bối cảnh

Phiên 2026-06-23 vấp 2 lỗi orca orchestration CLI: (1) `task-update --status done` trả
`ok:false` lặng lẽ vì status hợp lệ là `completed`; (2) bẫy 2 id — `task-create --json` trả
cả envelope `id` lẫn `result.task.id`, dùng nhầm khiến task kẹt `ready`. Đã ghi "bài học 230626"
vào skill, nhưng prose note lệ thuộc model ĐỌC nó — đúng cái pattern "tin model nhớ" mà harness
sinh ra để chống. Quyết định: chuyển sang **harness inject/chặn đúng khoảnh khắc** (giống [[R10]] docs-gate).

**Phạm vi tầng:** đây là **L1 adapter** (vendor=orca), KHÔNG đụng `policy.yaml` (L0 trung lập vendor).

## Plan

- [ ] **T1** — Viết `llmwiki/.claude/hooks/orca_guard.py`: BLOCK `task-update --status <invalid>` (exit 2), INJECT nhắc id-trap khi thấy `task-create`, còn lại exit 0 fail-open
- [ ] **T2** — Đăng ký PreToolUse(Bash) cạnh `pre_tool_use.py`: settings template + install-harness.sh (global tpl + ROOT tpl)
- [ ] **T3** — Smoke-test 4 nhánh (done→block, completed→pass, task-create→inject, non-orca→im) + verify-before-commit

**Sequence diagram**: [230626-orca-guard-hook-seq.html](../../../html/230626-orca-guard-hook-seq.html)

## Agent Task Assignment

| Task | Agent CLI | Lý do chọn | Status |
|------|-----------|-----------|--------|
| T1 — viết orca_guard.py | claude-cli | Logic chặn/inject hook-critical, ngữ nghĩa exit-2 | done |
| T2 — đăng ký PreToolUse | claude-cli | Harness-critical: nối hook không đè, exit-2 dễ vỡ | done |
| T3 — smoke + verify | opencode | Cơ học: feed command, đọc exit code + stdout | done |

## Tiêu chí hoàn thành

- `task-update --status done` bị chặn (exit 2) kèm hint enum đúng.
- `task-update --status completed` cho qua (exit 0).
- `task-create` → stdout có nhắc `result.task.id`.
- Lệnh non-orca (vd `git status`) không bị đụng (exit 0, im).
- `pre_tool_use.py` vẫn chạy đủ (2 hook nối tiếp, không hook nào bị đè).

## Origin

- **Source:** `wiki/sources/draft/230626-orca-guard-hook.md` — đề xuất phiên 2026-06-23 sau 2 lỗi orca CLI thật; user chốt "harness inject đáng tin hơn prose note".
- **Date:** 2026-06-23
