---
schema_version: 0
frame_id: frame-f04-luong-chinh
created_by: slicer
parent_br: br/BR.md
clause_ids: [C7.1, C7.2, C7.3, C7.4, C13.5]
parent_br_hash: b859c2b5c4dc70c65391f61a3eb1ad9c883359d3c3f1c2e11714b3d3112f9f6c
muc_tieu: "Lương chính pro-rata theo ngày công — tách lương thử việc và lương chính thức, cộng phụ cấp trách nhiệm và lương phép tồn, làm tròn kiểu Excel (half-up) chứ không phải kiểu Python"
scope_code: ["app/luong.py"]
scope_test: ["tests/test_f04.py"]
acceptance_test: "python3 -m tests.test_f04"
ui_role: none
ui_screen: 
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-f04-luong-chinh.run.json
---
# frame-f04-luong-chinh

## Nghiệp vụ

Lương thực tế trong tháng = đơn giá ngày × số ngày hưởng lương. Người ký hợp đồng chính thức giữa kỳ thì phải tách hai giai đoạn và tính hai đơn giá khác nhau (thử việc hưởng 85%). `EARNED_SAL` theo lớp as-is gồm BỐN thành phần (lương thử việc + lương chính thức + phụ cấp trách nhiệm + lương phép tồn) — bản 'định làm' chỉ có ba, thiếu lương phép tồn.

Cạm bẫy chết người: `round()` của Python làm tròn về số chẵn (banker's rounding), còn `ROUND()` của Excel làm tròn lên. Lệch 1 đồng là HR bắt được ngay, và một khi họ bắt được thì họ không tin engine nữa.

## Input / Output

- **Input:** bản ghi (loại HĐ, lương cơ bản, lương thử việc, PC trách nhiệm, công chuẩn, PAID_DAYS, lương phép tồn) + tham số kỳ
- **Output:** `prob_earned`, `official_earned`, `resp_earned`, `earned_sal` — đều trả `Decimal` đã làm tròn

## Tiêu chí nghiệm thu

- Ground-truth dòng 9: 200tr, công chuẩn 22, PAID_DAYS 22 → lương chính thức = 200.000.000
- Đang thử việc → lương chính thức = 0 (và ngược lại)
- Làm nửa kỳ (11/22) → hưởng đúng một nửa
- Làm tròn HALF-UP: 3 ÷ 2 × 1 = 1,5 → 2 (nếu ra 1 là dùng nhầm round() của Python)
- EARNED_SAL cộng đủ 4 thành phần, gồm cả lương phép tồn

## Ngoài phạm vi

Không tính phụ cấp (frame khác). Không tính OT. Không xử lý quyết toán phép năm khi nghỉ việc.
