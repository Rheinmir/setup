---
schema_version: 0
frame_id: frame-f13-adapters
created_by: slicer
parent_br: br/BR.md
clause_ids: [C18.1]
parent_br_hash: 5aa1c47fb9bc720f40479854a5a5f1bdd49da2a2366b9fdbe72b8bacf59d1d95
muc_tieu: "Ranh giới vào-ra duy nhất — bốn hàm đọc nhân sự, đọc chấm công, đẩy phiếu lương, xuất file ngân hàng; lô này đọc từ file JSON, lô sau thay ruột bằng Workday mà không đụng engine"
scope_code: ["app/adapters.py"]
scope_test: ["tests/test_f13.py"]
acceptance_test: "python3 -m tests.test_f13"
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

- Đủ đúng bốn hàm ranh giới
- `fetch_employees("2026-03")` đọc được từ file JSON, trả danh sách có khoá `employee_id`
- **Zero network**: mã nguồn không được import `requests`/`socket`/`urllib.request`/`http.client`
- Mỗi hàm ghi rõ trong mã nguồn nó sẽ nối vào đâu ở lô sau (nhắc tên Workday) — chỗ nối không được mất dấu

## Ngoài phạm vi

Không gọi mạng, không xác thực, không SFTP, không sinh template ngân hàng thật (chỉ CSV phẳng).
