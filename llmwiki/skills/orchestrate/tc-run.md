---
name: tc-run
description: Có MỘT file test case đầy đủ (.xlsx nhiều sheet, cột Test Case ID/Description/Steps/Expected/Priority/Type) → bóc thành JSON, phân loại tất định ui|calc|perf|security|gap, sinh PLAN theo LÔ, chạy qua orca-graph trên phiên trình duyệt ĐÃ đăng nhập của user (claude-in-chrome), ghi PASS/FAIL/BLOCK + ảnh từng TC, xuất mỗi lô một report .xlsx tester-kit (tao_report_test). Gọi khi user nói "chạy bộ test case này", "file test case xlsx", "SIT/UAT theo file", "xuất report tester-kit", "/tc-run".
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: tc-run — từ file test case đầy đủ đến report từng lô

Bóc từ phiên Payroll SIT 15/09/2026 (335 TC, 7 sheet). Tool tất định: `harness/scripts/tc-xlsx.py`
(extract · classify · plan · report). Runtime chạy lô: `/orca-graph`. Trình duyệt: claude-in-chrome
trên phiên user đã đăng nhập (SSO). Report: MCP `tester-kit` → `tao_report_test`.

## WHAT

### Purpose và context
- **Purpose:** biến MỘT file test case .xlsx đầy đủ thành kết quả PASS/FAIL/BLOCK có ảnh từng TC và mỗi lô một report .xlsx tester-kit.
- **Trigger (when to use):** User đưa một file test case .xlsx (SIT/UAT/regression) và muốn "chạy xem", "break nhỏ", "xuất report".
- **Non-goals:** KHÔNG dùng để viết test case mới (đó là `/uat-nonit-testcase`), không dùng cho unit test code.

### Mental model
`xlsx → tcs.json (extract) → nhãn ui|calc|perf|security|gap (classify) → PLAN theo lô → orca-graph (t1 hitl đăng nhập → các lô song song → report) → results/<lô>.json + shots/<id>.png → report-<lô>.xlsx → summary.md`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | file test case .xlsx | có | nhiều sheet, cột Test Case ID/Description/Steps/Expected/Priority/Type |
| In | URL app + phiên đăng nhập | có | user tự đăng nhập trong tab claude-in-chrome (HITL) |
| In | dữ liệu đầu vào calc | không | persona/kỳ lương do user chuẩn bị; thiếu thì TC `calc` không chạy |
| Out | `tcs.json` + bảng phân loại theo sheet | có | số `ui`/`calc`/`perf`/`security`/`gap` |
| Out | PLAN.md + graph | có | lô ≤ 8 TC, graph ≤ 20 node |
| Out | `results/<lô>.json` + `shots/<id>.png` | có | PASS/FAIL/BLOCK + actual + evidence từng TC |
| Out | `report-<lô>.xlsx` + `summary.md` | có | report tester-kit mỗi lô; tổng hợp theo lô |

### Rules và capabilities
- RULE-01 (MUST): Kết quả từng TC phải có **ảnh thật + actual quan sát được**; không có ảnh thì không được PASS.
- RULE-02 (MUST): `calc` chỉ chạy khi có dữ liệu đầu vào (persona/kỳ lương) do user chuẩn bị; không tự bịa số.
- RULE-03 (MUST): `security` và `perf` ghi rõ "ngoài phạm vi tự động" trong summary, không lặng lẽ bỏ.
- RULE-04 (MUST): Lô ≤ 8 TC để ảnh và context không phình; graph ≤ 20 node (giới hạn orca-graph) → file > ~150 TC ui thì chia nhiều PLAN (graph mẹ → con).
- RULE-05 (MUST): Report đúng schema tester-kit: `priority` High/Medium/Low (P0,P1→High, P2→Medium, P3→Low), `description` gồm STEPS/EXPECTED/ACTUAL/STATUS.
- Capabilities: đọc xlsx + phân loại tất định; điều khiển trình duyệt trên phiên user đã đăng nhập; ghi file kết quả/ảnh cục bộ; gọi dịch vụ xuất report.

### Failure boundaries
- Gặp trang login/SSO → **blocked** chờ user đăng nhập trong chính tab; không nhập mật khẩu, không bấm SSO thay user.
- Bước cần Lưu/Xoá/Cập nhật trên dữ liệu thật → TC đó **BLOCK** "cần môi trường SIT riêng", trừ khi user cho phép rõ.
- TC `calc` thiếu dữ liệu đầu vào, `gap` steps rỗng → không chạy, liệt kê trong summary (**partial**).
- Không chụp được ảnh → TC không được PASS.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | file .xlsx | Bóc + phân loại (`tc-xlsx.py extract` rồi `classify`), báo bảng theo sheet | `tcs.json` + bảng | heuristic sai → sửa nhãn `auto`, nói rõ TC nào |
| W02 | deterministic | `tcs.json` | Sinh PLAN theo lô rồi dựng graph (`orca-graph.py build --strict`) | PLAN + graph | build lỗi → sửa PLAN rồi lặp |
| W03 | effect | URL app | Phiên đăng nhập HITL, ghi `app.json` → `set t1 done_user_reported` | đã login | thấy login/SSO → dừng nhờ user |
| W04 | effect | lô | Chạy từng lô: lock → dispatched → làm → set done, chụp ảnh, so Expected | `results/<lô>.json` | ghi dữ liệu thật → BLOCK TC đó |
| W05 | effect | results | Report mỗi lô qua `tao_report_test` + `summary.md` | `report-<lô>.xlsx`, summary | — |
| W06 | deterministic | graph | Theo dõi tiến độ trên cockpit, `audit` câu trả lời model | tiến độ | — |

Chi tiết từng bước (nguồn chân lý cho W01–W06):

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

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | recovery | heuristic classify gán nhãn sai | sửa nhãn `auto` trong tcs.json, nói rõ đã sửa TC nào | — | W02 |
| B02 | conditional_required | file > ~150 TC ui (vượt 20 node) | chia nhiều PLAN (graph mẹ → con) | — | W03 |
| B03 | user_optional | user cho phép rõ ghi dữ liệu thật | chạy cả bước Lưu/Xoá/Cập nhật | không cho phép → BLOCK "cần môi trường SIT riêng" | W04 |
| B04 | conditional_required | có TC `calc` và user đã chuẩn bị persona/kỳ lương | chạy TC calc, kiểm số | thiếu dữ liệu → không chạy, ghi summary | W05 |

### Validation và stopping
Mỗi lô là một node có `verify` = file results đủ số TC; PASS chỉ khi có ảnh thật + actual. Dừng khi mọi node lô done và mỗi lô có report; TC còn lại (calc/perf/security/gap, BLOCK) liệt kê trong `summary.md`.

### Examples
- **Positive:** file SIT Payroll 335 TC, 7 sheet → classify ra phần `ui` → `plan --batch 8 --only ui` → user đăng nhập SSO trong tab → mỗi lô 8 TC có `shots/<id>.png` + `results/<lô>.json` → `report-<lô>.xlsx` + `summary.md` PASS/FAIL/BLOCK theo lô.
- **Boundary/failure:** TC yêu cầu bấm "Lưu" bảng lương trên dữ liệu thật, user chưa cho phép → TC đó BLOCK "cần môi trường SIT riêng", không bấm; TC không chụp được ảnh → không PASS.

### Recap
`/tc-run` = xlsx → `tc-xlsx.py extract/classify` → PLAN theo lô → orca-graph → chạy trên phiên đã login → results JSON + ảnh → `tao_report_test` mỗi lô → summary.
Use-case bất ngờ: chạy `classify` trên file test case của team để thấy ngay bao nhiêu % là gap/chờ nghiệp vụ trước khi ai đó hứa ngày xong.
