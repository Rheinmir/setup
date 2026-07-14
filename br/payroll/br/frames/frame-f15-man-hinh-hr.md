---
schema_version: 0
frame_id: frame-f15-man-hinh-hr
created_by: slicer
parent_br: br/BR.md
clause_ids: [C15.1, C15.2, C15.4, C14.1]
parent_br_hash: 2332e28da09ebdd69a6e153974fd7a58dabd8cc667294de676e350f1a05eb70a
muc_tieu: "Bốn màn hình cho HR — bảng lương toàn kỳ, phiếu lương từng người theo đúng mẫu thật, cây truy vết công thức bấm ngược được từ lương thực nhận xuống tận lương cơ bản, và MỘT tab tối giản tải Excel mass-upload thay nhập tay"
scope_code: ["app/ui.py", "app/upload.py"]
scope_test: ["tests/test_f15.py"]
acceptance_test: "python3 -m tests.test_f15"
ui_role: screen
ui_screen: payroll
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-f15-man-hinh-hr.run.json
---
# frame-f15-man-hinh-hr

## Nghiệp vụ

HR không đọc JSON. Họ cần nhìn thấy bảng lương như trong Excel họ đang dùng, và khi thấy một con số lạ thì bấm vào nó để hỏi 'số này ở đâu ra?'. Màn truy vết là màn đắt nhất và cũng là màn duy nhất mà Excel không làm được — đó là toàn bộ giá trị của việc bỏ Excel.

Màn phiếu lương phải dựng đúng mẫu thật: kỳ ghi 'Từ ngày 21 tháng trước đến ngày 20 tháng này', các khối thông tin nhân viên / ngày công / lương và phụ cấp / khấu trừ / thực nhận. In được ra giấy.

Giao diện phải có công tắc sáng-tối, nhớ lựa chọn, và không được nháy trắng khi tải (chống FOUC).

## Input / Output

- **Input:** cổng HTTP; riêng `/upload` nhận thêm **POST** — body là bytes thô của file `.xlsx` (không multipart, không field khác — tối giản), kỳ lương truyền qua query string `?period=YYYY-MM`
- **Output:** `build_server(port)` → server đã gắn 4 route: `/` (bảng lương), `/payslip/<mã NV>`, `/trace/<mã NV>/<mã field>`, `/upload` (GET: form tối giản 1 ô chọn kỳ + 1 ô chọn file; POST: parse + ghi + trang xác nhận)

## Tiêu chí nghiệm thu

- Trang chủ hiện đúng lương thực nhận của ground-truth: **189.930.161** (số phải HIỆN trên màn, không chỉ đúng trong test)
- Phiếu lương hiện đúng số, có mục 'Lương thực nhận' và 'Thuế TNCN', có mốc ngày 21 của kỳ
- Trang truy vết `NET_PAY` hiện ra phụ thuộc (GROSS) và mã điều khoản BR (C13)
- Trang truy vết `SI_EMP` hiện đúng trần bảo hiểm đã dùng: 46.800.000
- Có `localStorage` + `prefers-color-scheme` (toggle sáng/tối, không ép mode, chống FOUC)
- Số tiền dùng `tabular-nums` (căn cột thẳng hàng)
- `GET /upload` trả form HTML có `<input type="file">` + trường kỳ lương — ĐÚNG 1 tab, không có field nhập lương/phụ cấp/chấm công tay nào khác
- `POST /upload?period=<kỳ demo>` với bytes một file `.xlsx` hợp lệ (header hàng 1 = tên field `employees.json`, ≥1 hàng dữ liệu) → ghi được `data/inputs/<kỳ demo>/employees.json`, trang xác nhận hiện đúng số nhân sự đã nạp + link `/`
- Kỳ dùng để test upload PHẢI KHÁC `2026-03` (không ghi đè ground-truth)

## Ngoài phạm vi

Không đăng nhập, không phân quyền theo vai (lô sau). Không có dashboard lãnh đạo, không có màn khoá kỳ, không có màn nhập tờ trình. Không sửa dữ liệu từng-field qua giao diện (3 màn gốc vẫn chỉ xem); `/upload` CHỈ mass-upload nguyên file, không có ô sửa tay từng dòng/từng field.
