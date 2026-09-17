---
type: issue
kind: feature-gap
title: "orca-graph không tách vai QC khỏi Verify — verify: chỉ là 1 lệnh shell, không có reviewer độc lập"
status: in-progress
assignee: claude-sonnet-5
dispatch: human
entry: /fdk
priority: P3
tags: [issue, orca-graph, qc, verify, review, separation-of-duties]
timestamp: 2026-09-17
id: 170926-orca-graph-no-separate-qc-role
source_session: So sánh /orca-graph với ảnh kiến trúc "Atlas dispatch pipeline" (Claude orchestrator + Qwen3.8-27B LAN worker pool + DeepSeek-V4-Pro QC cloud relay) user cung cấp
---

# Issue: orca-graph không tách vai QC khỏi Verify

## Vấn đề (một câu)
`verify:` trong PLAN.md/orca-graph chỉ là MỘT lệnh shell (rc 0/khác 0) chạy bởi bất kỳ ai reconcile — không có khái niệm bắt buộc "người/model thứ hai, KHÁC agent đã viết code, review diff rồi mới cho `done`", nên worker về lý thuyết có thể tự chấm bài của chính nó.

## Bối cảnh & bằng chứng
- `skills/orca-graph/SKILL.md` § "Máy state mỗi node": *"Ba chiều tách nhau: `state` (vòng đời) · `verified` (verify rc 0?) · `fresh`..."* — `verified` chỉ là rc code của MỘT lệnh, không phân biệt AI chạy lệnh đó, không có trường ghi "ai review, review cái gì".
- `harness/scripts/orca-graph.py` `cmd_run`/`emit`: kết quả `verify` do CHÍNH quá trình `run <id> <node> -- <lệnh agent>` sinh ra (rc 0 → `done`) — không có bước riêng gửi diff cho một actor khác trước khi commit.
- Framework NGOÀI orca-graph đã có `/qc-code`, `/qc-uiux`, `/code-review` (review 4-mục senior, sinh test tái hiện) — nhưng các skill này KHÔNG được wire như một GATE bắt buộc trong state machine của orca-graph; dùng hay không là tuỳ agent/người, không bị ép.
- Ảnh so sánh (phiên 2026-09-17): pipeline "Atlas dispatch" tách hẳn 2 vai — **Verify** (orchestrator: acceptance+test+lint) khác **QC relay** (DeepSeek-V4-Pro, "reviews, never writes", nhận diff+checklist, trả PASS|FAIL) — worker (Qwen pool) không có quyền tự quyết mình đã xong, phải qua QC độc lập mới tới `Commit on green`.
- Suy luận (nhãn gợi-ý): separation-of-duties (người viết ≠ người duyệt) là nguyên tắc quality/security cơ bản; orca-graph hiện KHÔNG có ràng buộc này ở tầng graph engine — nó tồn tại (nếu có) chỉ nhờ kỷ luật của người vận hành gọi thêm `/qc-code` thủ công, không phải invariant của hệ.

## Phạm vi
- `harness/scripts/orca-graph.py` — máy state (`STATES`, `TERMINAL_OK`, `emit`, `cmd_run`, `reconcile`).
- `skills/orca-graph/SKILL.md` § "Máy state mỗi node" — cần mô tả lại nếu thêm vai QC.
- Khả năng liên quan: `/qc-code`, `/code-review` (skill review đã có, có thể là ứng viên để wire vào, không cần xây mới).

## Không thuộc phạm vi
- KHÔNG đề xuất bắt buộc MỌI node phải qua QC model riêng (chi phí/độ trễ) — chỉ ghi nhận orca-graph THIẾU khả năng làm việc đó KHI CẦN.
- KHÔNG đề xuất tích hợp cụ thể model nào (DeepSeek hay khác) — đó là chi tiết triển khai, không phải phạm vi issue.
- KHÔNG trùng với [[170926-orca-graph-no-write-sandbox]] (issue kia về phạm vi GHI, issue này về vai REVIEW).

## Hướng gợi ý (không bắt buộc)
Thêm một trường tuỳ chọn trong PLAN.md node, vd `**QC:** <lệnh hoặc skill>`, chạy SAU `verify` rc=0 và TRƯỚC khi `emit(..., "done", ...)` — nếu QC fail thì node về `ready` (giống `verify` fail hiện tại) kèm note lý do. Có thể tái dùng `/qc-code`/`/code-review` làm lệnh QC mặc định cho node `kind: build`.

## Tiêu chí HOÀN THÀNH
- Có cách (opt-in, không phá node cũ không khai `QC:`) để một node yêu cầu review độc lập trước khi `done` — kiểm chứng bằng test: node có `QC:` trỏ lệnh luôn fail → node không bao giờ đạt `done` dù `verify` rc=0.
- `SKILL.md` cập nhật máy state nếu thêm chiều mới.

## Assign & lý do
Chưa gán người cụ thể — quyết định kiến trúc (thêm chiều review vào graph engine hay để nguyên, dựa `/qc-code` gọi tay) cần người cân nhắc chi phí/độ trễ trước khi giao agent code, nên `dispatch: human`, `entry: /fdk`.

## Origin
Raised bởi phiên Claude Code (2026-09-17) khi user đưa ảnh kiến trúc "Atlas dispatch pipeline" để so sánh với `/orca-graph`. Bằng chứng: `skills/orca-graph/SKILL.md` (đọc trực tiếp trong phiên), `harness/scripts/orca-graph.py` (đọc trực tiếp). Không có council/report riêng — suy luận từ so sánh kiến trúc, gắn nhãn gợi-ý.

## Thi hành (2026-09-17)
User dùng `/goal` chỉ thị trực tiếp implement (quyết định human đã có). Theo PLAN [[170926-orca-graph-write-sandbox-qc-gate-PLAN]], node `t2` trong graph `170926-orca-graph-write-sandbox-qc-gate` — trường `**QC:**` trong `parse_plan`, gate trong `emit()` (guard `by != "reconcile"`, giống pattern `verify`) + `cmd_reconcile` (quyết `ready` khi qc fail). Test: `harness/tests/test_orca_graph.py::test_qc_field_parsed_and_in_spec_hash`, `::test_qc_gate_blocks_done_via_run`, `::test_qc_gate_blocks_done_via_reconcile`, cả 3 xanh (pytest 22/22 toàn suite). Sơ đồ thiết kế: `llmwiki/html/170926-orca-graph-gates-architecture.html` (archify workflow).
