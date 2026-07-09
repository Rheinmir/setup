---
schema_version: 0
frame_id: frame-p21-ot-engine
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.5]
parent_br_hash: 06f8501d7472387c48709eed1947a0118c170e31ddc23c5b4e4282caca8bb9de
muc_tieu: "OT engine: multiplier cấu hình tách Chính thức/Mắt Bão (CN 200%, lễ luật +100% & +2 nghỉ bù/ngày, danh sách 300%, truyền thống +1 nghỉ bù), tách OT thuế/không thuế"
scope_code: ["app/p21_ot.py"]
scope_test: ["tests/test_p21.py"]
acceptance_test: "python3 -m tests.test_p21"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p21-ot-engine.run.json
---
# frame-p21-ot-engine

## Nghiệp vụ
Loại giờ đến từ Workday, Payroll chỉ nhân hệ số — nhưng hệ số phải cấu hình được và tách riêng hai nhóm nhân sự. Đi làm lễ theo luật sinh thêm 2 ngày nghỉ bù mỗi ngày làm, ngày truyền thống sinh 1 — nghỉ bù là 'tiền tệ' riêng phải ghi sổ. Phần vượt mức luật của tiền OT chịu thuế TNCN, hệ tách 2 cột ngay tại đây.

## Input / Output
- **Input:** Bản ghi TC từ công thô (p07 cho hệ số), ot_multiplier.csv, employee_type, lương giờ
- **Output:** {tien_ot, ot_taxable, ot_non_tax, ngay_nghi_bu_sinh_them} theo NV

## Tiêu chí nghiệm thu
- NV008 2 ngày TC200 → tiền = 2 × lương ngày × 200%
- 1 ngày lễ luật → +100% tiền và +2 nghỉ bù ghi sổ
- Ngày trong danh sách 300% (config) → 300%; danh sách rỗng (assumed G5) → cảnh báo trace
- Mắt Bão dùng cột multiplier riêng

## Ngoài phạm vi
Không duyệt đơn đi làm lễ (p24). Không tính thuế cuối (p26).
