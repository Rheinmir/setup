---
schema_version: 0
frame_id: frame-f07-tang-ca
created_by: slicer
parent_br: br/BR.md
clause_ids: [C9.1, C9.2, C9.3]
parent_br_hash: 2332e28da09ebdd69a6e153974fd7a58dabd8cc667294de676e350f1a05eb70a
muc_tieu: "Tăng ca vào engine là SỐ TIỀN đã tính sẵn, KHÔNG tự chế công thức quy giờ ra tiền; hệ số nào tài liệu không nói thì để trống chứ không bịa; ghi nhận ngày nghỉ bù khi đi làm ngày lễ"
scope_code: ["app/tangca.py"]
scope_test: ["tests/test_f07.py"]
acceptance_test: "python3 -m tests.test_f07"
ui_role: none
ui_screen: 
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-f07-tang-ca.run.json
---
# frame-f07-tang-ca

## Nghiệp vụ

Đây là frame mà việc KHÔNG làm quan trọng hơn việc làm. Không tài liệu nào — kể cả Excel bàn giao — có công thức quy số giờ tăng ca ra tiền. Excel khai `OT_TAX`/`OT_NONTAX` là input, và API Workday trả giờ tăng ca thật (`Get_Calculated_Time_Blocks`) hiện đang BỊ CHẶN QUYỀN, nên kể cả muốn tính từ giờ cũng không có giờ mà tính.

Nếu engine tự bịa hệ số 150%/300%, nó sẽ ra số khác bảng lương thật ngay ở nhân viên đầu tiên có tăng ca, và sai số đó lẫn vào thuế + bảo hiểm + lương thực nhận khiến không ai truy được lỗi ở đâu. Hệ số nào tài liệu nói thẳng (Chủ nhật 200%) thì điền; còn lại để `null` và bật cờ `ot_from_hours: false`.

Riêng ngày nghỉ bù thì có luật rõ: làm ngày Lễ/Tết được 2 ngày nghỉ bù, làm ngày truyền thống công ty được 1 ngày.

## Input / Output

- **Input:** bản ghi (OT_TAX, OT_NONTAX là tiền; số ngày làm lễ / làm ngày truyền thống) + tham số
- **Output:** `ot_tax`, `ot_nontax` → `Decimal` (đi thẳng qua); `ngay_nghi_bu` → `Decimal`; `ot_tu_gio` → ném `ValueError` nếu thiếu hệ số

## Tiêu chí nghiệm thu

- OT là tiền input, đi thẳng vào engine không nhân hệ số
- Tham số `ot_from_hours` mặc định TẮT
- Hệ số chưa biết để `None` (ngày thường, ban đêm, mức 300%) — không bịa
- Bật `ot_from_hours` mà thiếu hệ số → ném `ValueError`, KHÔNG đoán bừa
- Làm 2 ngày lễ → 4 ngày nghỉ bù; làm 3 ngày truyền thống → 3 ngày nghỉ bù

## Ngoài phạm vi

Không quy giờ ra tiền (chưa có luật). Không tự chọn hệ số thay HR. Không đọc giờ tăng ca từ Workday.
