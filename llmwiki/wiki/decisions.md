# Decisions Log

> Ghi lại các quyết định quan trọng (approve/reject proposal, chọn hướng kỹ thuật).

| Date | Decision | Type | Context | Outcome |
|------|----------|------|---------|---------|
| 2026-06-27 | Thêm R11 seq-html-glass-style | rule | Style glass chỉ ở prose skill → bị bỏ qua | policy.yaml `conditional_require`, enforce_at session; shipped |
| 2026-06-27 | R12 chỉ (B) orchestrator sweep + (C) pre-push; BỎ (A) per-edit | architecture | Đa-vendor: chỉ git-level + orchestrator phủ hết | gỡ per-edit PreToolUse; [[ADR-002-pull-before-change-gates]] |
| 2026-06-27 | Duyệt + ship R12 v3 workspace-aware | gate | gate_16a0e503882d; nhiều subrepo/1 workspace | T1-T5 done, test 4/4; commit 076f970 |
| 2026-06-27 | T2 gộp vào discovery dùng chung | design | list-subrepos cần cho sweep + installer (≥2 use case) | 1 file `list-subrepos.py` thay parser riêng |
| 2026-06-27 | Backfill rule-registry + ADR | docs | Bus-factor=1: luật/lý do trong đầu | [[rule-registry]] + ADR-001/002; decisions.md lấp |
| 2026-06-27 | T1 reconcile policy.yaml | rule | R3/R4/R8/R10 enforce bằng hook, vắng khỏi policy | thêm dạng hook_event (11 rule); R3/R8 điều tra ra KHÔNG drift |
| 2026-06-27 | T5 drift-test gen-converters↔policy | test | out/ gitignored → bắt 'gen DROP/lệch policy' | drift-test 28/28, negative proven, wire pre-commit |
| 2026-06-27 | T4 + đóng gap-backfill | docs | Runbook thiếu → người mới phải đọc đầu tác giả | CONTRIBUTING-harness.md; T1-T5 done |
