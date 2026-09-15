---
name: tc-run
description: Có MỘT file test case đầy đủ (.xlsx nhiều sheet, cột Test Case ID/Description/Steps/Expected/Priority/Type) → bóc thành JSON, phân loại tất định ui|calc|perf|security|gap, sinh PLAN theo LÔ, chạy qua orca-graph trên phiên trình duyệt ĐÃ đăng nhập của user (claude-in-chrome), ghi PASS/FAIL/BLOCK + ảnh từng TC, xuất mỗi lô một report .xlsx tester-kit (tao_report_test). Gọi khi user nói "chạy bộ test case này", "file test case xlsx", "SIT/UAT theo file", "xuất report tester-kit", "/tc-run".
---

# Skill: tc-run — từ file test case đầy đủ đến report từng lô

Bóc từ phiên Payroll SIT 15/09/2026 (335 TC, 7 sheet). Tool tất định: `harness/scripts/tc-xlsx.py`
(extract · classify · plan · report). Runtime chạy lô: `/orca-graph`. Trình duyệt: claude-in-chrome
trên phiên user đã đăng nhập (SSO). Report: MCP `tester-kit` → `tao_report_test`.

## When to use
- User đưa một file test case .xlsx (SIT/UAT/regression) và muốn "chạy xem", "break nhỏ", "xuất report".
- KHÔNG dùng để viết test case mới (đó là `/uat-nonit-testcase`), không dùng cho unit test code.

## Steps
1. **Bóc + phân loại (0 token):**
   ```
   python3 harness/scripts/tc-xlsx.py extract <file.xlsx> -o scratchpad/<tên>/tcs.json
   python3 harness/scripts/tc-xlsx.py classify scratchpad/<tên>/tcs.json
   ```
   Báo user bảng theo sheet: bao nhiêu `ui` (chạy được bằng trình duyệt), `calc` (cần dữ liệu đầu vào, kiểm số), `perf`, `security` (SSO/đăng nhập, không tự động hoá an toàn), `gap` (steps rỗng/chờ nghiệp vụ). Heuristic sai thì **sửa nhãn `auto` trong tcs.json và nói rõ đã sửa TC nào**.
2. **Sinh PLAN theo lô rồi dựng graph:**
   ```
   python3 harness/scripts/tc-xlsx.py plan tcs.json --app "<tên app (URL)>" --batch 8 --only ui -o llmwiki/wiki/sources/draft/DDMMYY-<tên>-PLAN.md
   python3 harness/scripts/orca-graph.py build <PLAN> --strict && orca-graph.py ask <id> parallel
   ```
   Task 1 luôn là `hitl` (khảo sát app + phiên đăng nhập); các lô song song; task cuối xuất report. Mỗi lô là một node có `verify` = file results đủ số TC.
3. **Phiên đăng nhập — HITL, không được vượt:** mở URL trong tab claude-in-chrome; thấy trang login/SSO → **dừng, nhờ user bấm đăng nhập trong chính tab đó**. Không nhập mật khẩu, không bấm nút SSO thay user. Đăng nhập xong → ghi `app.json` (`logged_in: true`, menu thật) → `set t1 done_user_reported`.
4. **Chạy từng lô** (`lock` → `dispatched` → làm → `set done`): mỗi TC theo Test Steps bằng `find`/`computer`/`read_page`, chụp ảnh `shots/<id>.png`, so Expected → `PASS|FAIL|BLOCK` + `actual` + `evidence`. **Dừng trước mọi Lưu/Xoá/Cập nhật trên dữ liệu thật → BLOCK "cần môi trường SIT riêng"**, trừ khi user cho phép rõ. Ghi `results/<lô>.json`.
5. **Report mỗi lô:** `tc-xlsx.py report results/<lô>.json --tcs tcs.json --url <URL>` → payload → gọi MCP `tao_report_test` → chép xlsx về `report-<lô>.xlsx`. Cuối cùng `summary.md`: PASS/FAIL/BLOCK theo lô, TC cần người, TC calc/perf/security còn lại.
6. Theo dõi tiến độ trên cockpit (`control-room.html`); `audit` câu trả lời model như orca-graph.

## Rules
- Kết quả từng TC phải có **ảnh thật + actual quan sát được**; không có ảnh thì không được PASS.
- `calc` chỉ chạy khi có dữ liệu đầu vào (persona/kỳ lương) do user chuẩn bị; không tự bịa số.
- `security` và `perf` ghi rõ "ngoài phạm vi tự động" trong summary, không lặng lẽ bỏ.
- Lô ≤ 8 TC để ảnh và context không phình; graph ≤ 20 node (giới hạn orca-graph) → file > ~150 TC ui thì chia nhiều PLAN (graph mẹ → con).
- Report đúng schema tester-kit: `priority` High/Medium/Low (P0,P1→High, P2→Medium, P3→Low), `description` gồm STEPS/EXPECTED/ACTUAL/STATUS.

## Recap
`/tc-run` = xlsx → `tc-xlsx.py extract/classify` → PLAN theo lô → orca-graph → chạy trên phiên đã login → results JSON + ảnh → `tao_report_test` mỗi lô → summary.
Use-case bất ngờ: chạy `classify` trên file test case của team để thấy ngay bao nhiêu % là gap/chờ nghiệp vụ trước khi ai đó hứa ngày xong.
