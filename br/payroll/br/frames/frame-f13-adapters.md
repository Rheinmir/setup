---
schema_version: 0
frame_id: frame-f13-adapters
created_by: slicer
parent_br: br/BR.md
clause_ids: [C18.1, C18.2, C18.3, C14.2]
parent_br_hash: d4405e637a83f254824170838c8292807a704edb143ff9912a9dbd033cd77d6c
muc_tieu: "Ranh giới vào-ra duy nhất — bốn hàm đọc nhân sự, đọc chấm công, đẩy phiếu lương, xuất file ngân hàng, cộng hàm thứ năm ghi dữ liệu mass-upload và hàm thứ sáu xuất Payroll Master (FE-20); lô này đọc/ghi file JSON, lô sau thay ruột bằng Workday mà không đụng engine. Cộng sổ audit (FE-17): mọi lần ghi phải qua log_action ghi giá-trị-cũ → giá-trị-mới, người, thời gian, lý do bắt buộc"
scope_code: ["app/adapters.py", "app/audit.py"]
scope_test: ["tests/test_f13.py", "tests/test_f13_audit.py"]
acceptance_test: "python3 -m tests.test_f13 && python3 -m tests.test_f13_audit"
ui_role: none
ui_screen: 
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-f13-adapters.run.json
---
# frame-f13-adapters

## Nghiệp vụ

Ba API Workday sống còn (giờ tăng ca thật, dữ liệu nghỉ phép) hiện đang BỊ CHẶN QUYỀN — viết client Workday bây giờ là viết code chết, không test được. Nhưng cũng không được để engine gọi thẳng file JSON, vì như thế thì khi có credential lại phải mổ khắp nơi.

Giải pháp: nhốt toàn bộ thế giới bên ngoài sau đúng bốn hàm. Engine chỉ biết bốn hàm này. Lô sau, đổi ruột từng hàm — engine không biết gì và không cần biết.

## Input / Output

- **Input:** mã kỳ lương
- **Output:** `fetch_employees` → list dict; `fetch_timesheet` → list dict; `push_payslip` → ghi ra thư mục out; `export_bank_file` → đường dẫn file CSV

## Tiêu chí nghiệm thu

- Đủ đúng bốn hàm ranh giới gốc, cộng hàm thứ năm `save_uploaded_employees`
- `fetch_employees("2026-03")` đọc được từ file JSON, trả danh sách có khoá `employee_id`
- `save_uploaded_employees("2099-01", rows)` ghi đúng `data/inputs/2099-01/employees.json`; `fetch_employees("2099-01")` ngay sau đó đọc lại được ĐÚNG `rows` đã ghi
- `save_uploaded_employees` không đụng dữ liệu của kỳ khác (ghi kỳ `2099-01` không đổi `data/inputs/2026-03/employees.json`)
- **Zero network**: mã nguồn không được import `requests`/`socket`/`urllib.request`/`http.client`
- Mỗi hàm ghi rõ trong mã nguồn nó sẽ nối vào đâu ở lô sau (nhắc tên Workday) — chỗ nối không được mất dấu
- **FE-17/C14.2**: `audit.log_action(...)` ghi đúng 7 trường (`timestamp`, `action`, `period`, `performed_by`, `reason`, `old_employee_ids`, `new_employee_ids`); thiếu `performed_by` hoặc `reason` (rỗng/chỉ khoảng trắng) PHẢI ném `ValueError` — không âm thầm bỏ qua bắt buộc; `read_log()` đọc lại đúng thứ tự đã ghi (append-only, không sửa dòng cũ)
- **C18.3/FE-20**: `export_payroll_master("2026-03", p)` ra file CSV có ĐÚNG 1 dòng (GT-ROW9), `NET_PAY_HOME=189.930.161` và `GROSS=225.010.000` khớp ground-truth; 3 cột kế toán (`profit_cost_center`/`wbs`/`funds_center`) LUÔN rỗng — không bịa số

## Ngoài phạm vi

Không gọi mạng, không xác thực, không SFTP, không sinh template ngân hàng thật (chỉ CSV phẳng).
