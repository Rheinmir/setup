---
type: unknown-ledger
title: "unknown — 280926-overstack-strands-wrapper"
status: open
source_task: T-260928-01
source_spec: wiki/sources/draft/280926-overstack-strands-wrapper.md
timestamp: 2026-09-28
---

# Unknown ledger — 280926-overstack-strands-wrapper

> **Nợ unknown** — model đã *fill-first* (điền default để không chặn việc), *find-out-later* (chờ thông tin thật để trả nợ). KHÔNG chặn cổng; hiện ra ở `/lint` để không chìm. Đóng khoảng hở giữa `(default)` và `[CẦN LÀM RÕ]`. Xem `[[150726-unknown-ledger]]`.
>
> Thêm/đóng mục bằng `python3 harness/scripts/unknown-ledger.py` — đừng sửa số U-NN bằng tay.

## U-01 — Sự kiện Strands nào tương đương Stop của Claude cho luật hook_event (R3 index-sync)?
- **Trace:** FR-003 · SPEC `wiki/sources/draft/280926-overstack-strands-wrapper.md` · task `T-260928-01`
- **Đã fill (default):** AfterInvocationEvent
- **Cần verify:** đọc hook registry của strands + chạy T3 với R3
- **Rủi ro nếu default sai:** R3 không cắn hoặc cắn sai thời điểm
- **Status:** resolved
- **Resolved:** AfterInvocationEvent + resume (strands-agents 1.57.1, hooks/events.py:70-110); trần 2 lần · fix: SPEC bản 2 mục T2 + Assumptions; PLAN Task 3 · 2026-09-28

## U-02 — Ngưỡng SC-003 (chặn nhầm dưới 2%, pass^k tụt không quá 5 điểm) có hợp lý?
- **Trace:** FR-007 · SPEC `wiki/sources/draft/280926-overstack-strands-wrapper.md` · task `T-260928-01`
- **Đã fill (default):** 2% / 5 điểm
- **Cần verify:** chỉnh sau lượt đo E1/E2 đầu tiên
- **Rủi ro nếu default sai:** cổng quá lỏng hoặc quá chặt
- **Status:** open
- **Resolved:** _(chưa)_

## U-03 — Đường OpenRouter nào chạy tool calling ổn với Strands: litellm/openrouter/* hay openai/* + OPENAI_BASE_URL (Responses API)?
- **Trace:** FR-009 · SPEC `wiki/sources/draft/280926-overstack-strands-wrapper.md` · task `T-260928-01`
- **Đã fill (default):** litellm/openrouter/*
- **Cần verify:** mỗi đường 1 lượt gọi thật có tool call, ghi rc
- **Rủi ro nếu default sai:** E1/E2 không chạy được
- **Status:** open
- **Resolved:** _(chưa)_

## U-04 — Trần ngân sách mỗi lượt đo E1/E2 bằng bao nhiêu?
- **Trace:** FR-009 · SPEC `wiki/sources/draft/280926-overstack-strands-wrapper.md` · task `T-260928-01`
- **Đã fill (default):** 2 USD mỗi lượt (model Trung Quốc rẻ qua OpenRouter)
- **Cần verify:** user xác nhận hoặc chỉnh sau lượt đo đầu
- **Rủi ro nếu default sai:** tốn tiền quá mức hoặc dừng quá sớm
- **Status:** open
- **Resolved:** _(chưa)_

## Origin
- Sinh bởi `/propose` khi user chọn "fill-first, find-out-later" cho một unknown của SPEC nguồn.
- Trả nợ: `unknown-ledger.py --resolve <file> <U-id> --value … --fixed … --date …`.
- **Commit:** _(verify-before-commit điền)_
