---
type: issue
kind: foundation
title: "orca-graph không có allow-listed write paths per-task — lock chỉ kiểm soát dispatch"
status: in-progress
assignee: claude-sonnet-5
dispatch: human
entry: /fdk
priority: P3
tags: [issue, orca-graph, sandbox, write-paths, dispatch]
timestamp: 2026-09-17
id: 170926-orca-graph-no-write-sandbox
source_session: So sánh /orca-graph với ảnh kiến trúc "Atlas dispatch pipeline" (Claude orchestrator + Qwen3.8-27B LAN worker pool + DeepSeek-V4-Pro QC cloud relay) user cung cấp
---

# Issue: orca-graph không có allow-listed write paths per-task

## Vấn đề (một câu)
`/orca-graph` chỉ khoá QUYỀN NHẬN VIỆC (dispatch) của một node, không khoá PHẠM VI GHI FILE của agent đã nhận việc đó — một worker kém tin cậy có thể ghi ngoài `files` khai trong PLAN.md mà không gì chặn ở tầng graph engine.

## Bối cảnh & bằng chứng
- `skills/orca-graph/SKILL.md` tự khai rõ trong mục "Rules": *"Lock chỉ kiểm soát DISPATCH, không kiểm soát side-effect của agent đã chạy. Muốn cách ly thật → worktree riêng mỗi task."* — đây là giới hạn ĐÃ BIẾT, không phải phát hiện mới, nhưng chưa có issue nào ghi lại để cân nhắc nâng cấp.
- `[[ADR-018-orca-graph-file-based-graph-engine]]` (`fdk/wiki/sources/adr/ADR-018-orca-graph-file-based-graph-engine.md`) ghi nguyên tắc thiết kế: *"Vay luật, không vay hạ tầng"* — orca-graph cố tình chỉ vay LUẬT STATE của Reprise PRD, không vay hạ tầng sandbox/isolation. Việc thiếu allow-path là hệ quả trực tiếp của quyết định thiết kế này, không phải sơ suất.
- Ảnh so sánh (phiên 2026-09-17): pipeline "Atlas dispatch" của một hệ khác có bước **"Apply allowed paths"** ngay sau khi worker trả file — chunk ghi ngoài danh sách `Files` của task packet bị **DROP CỨNG tại nguồn**, trước khi tới Verify. Đây là compensating control cho việc dispatch cho model yếu hơn/kém steerable hơn (worker LAN là Qwen3.8-27B chạy "thinking off").
- Council/phiên hiện tại suy luận (nhãn gợi-ý, chưa audit bằng evidence-chain): lỗ hổng này chỉ thực sự đáng lo khi orca-graph dispatch cho agent KHÔNG đủ tin cậy (model yếu, CLI ngoài không steerable) — hiện tại orca-graph chủ yếu dispatch cho Claude Code subagent/CLI đã tương đối tin cậy, nên rủi ro CHƯA cao, nhưng sẽ tăng nếu tương lai orca-graph được dùng để điều phối worker rẻ/yếu hơn (tương tự động lực GPU-nhà của Atlas).

## Phạm vi
- `harness/scripts/orca-graph.py` (đặc biệt `cmd_run`, `emit`, `Store`) — nơi cần thêm bước lọc write-path nếu làm.
- `skills/orca-graph/SKILL.md` — cần cập nhật máy state + Rules nếu thêm cơ chế.
- PLAN.md schema (`**Files:**`) đã có sẵn danh sách file mỗi node khai — có thể tái dùng làm allow-list, không cần thêm trường mới.

## Không thuộc phạm vi
- KHÔNG phải sandbox chạy lệnh (process isolation) — chỉ nói về phạm vi GHI FILE.
- KHÔNG đề xuất thay thế worktree-isolation hiện có — allow-path là lớp BỔ SUNG, không phải thay thế.
- KHÔNG bao gồm việc tách vai QC khỏi Verify — xem issue riêng [[170926-orca-graph-no-separate-qc-role]].

## Hướng gợi ý (không bắt buộc)
Sau khi agent chạy xong (`cmd_run`), diff `git diff --name-only` với danh sách `files` của node; file ngoài danh sách → cảnh báo (mềm) hoặc `git checkout` phục hồi (cứng, cần `--strict`) trước khi cho `verify` chạy. Không bắt buộc chặn cứng ngay — có thể bắt đầu bằng cảnh báo trong log + note trong event, để dev quyết định mức độ nghiêm khắc.

## Tiêu chí HOÀN THÀNH
- Có cơ chế (dù mềm hay cứng) phát hiện/khai báo khi agent ghi ngoài `files` khai trong node — kiểm chứng bằng test: node có `files: [a.py]`, agent (giả lập) ghi thêm `b.py`, chạy `run`/`reconcile` → thấy cảnh báo hoặc bị chặn tuỳ mức triển khai.
- `SKILL.md` mục "Rules"/"Không làm được" cập nhật đúng thực tế mới (không còn nói "không kiểm soát side-effect" nếu đã làm).

## Assign & lý do
Chưa gán người cụ thể — đây là quyết định kiến trúc (có nên thêm allow-path vào graph engine, hay để nguyên và dựa vào worktree) cần người quyết trước khi một agent làm, nên `dispatch: human`, `entry: /fdk`.

## Origin
Raised bởi phiên Claude Code (2026-09-17) khi user đưa ảnh kiến trúc "Atlas dispatch pipeline" để so sánh với `/orca-graph`. Bằng chứng: `skills/orca-graph/SKILL.md` (đọc trực tiếp trong phiên), `fdk/wiki/sources/adr/ADR-018-orca-graph-file-based-graph-engine.md`. Không có council/report riêng cho việc này — suy luận từ so sánh kiến trúc, gắn nhãn gợi-ý.

## Thi hành (2026-09-17)
User dùng `/goal` chỉ thị trực tiếp implement (quyết định human đã có). Theo PLAN [[170926-orca-graph-write-sandbox-qc-gate-PLAN]], node `t1` trong graph `170926-orca-graph-write-sandbox-qc-gate` — `harness/scripts/orca-graph.py` (`_git_root`, `_changed_files`, `enforce_allowed_paths`, cờ `run --strict`). Test: `harness/tests/test_orca_graph.py::test_run_allowed_paths_warn` + `::test_run_allowed_paths_strict_revert`, cả 2 xanh (pytest 22/22 toàn suite). Sơ đồ thiết kế: `llmwiki/html/170926-orca-graph-gates-architecture.html` (archify workflow).
