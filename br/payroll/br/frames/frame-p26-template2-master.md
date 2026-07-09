---
schema_version: 0
frame_id: frame-p26-template2-master
created_by: slicer
parent_br: br/BR.md
clause_ids: [C6.3]
parent_br_hash: bd8b0c1092b3518507e218bdafbdb5dc39535405ea63f7a591e410a3c114e81d
muc_tieu: "Template 2 Payroll Master: file phẳng đầy đủ cho kế toán — ngày công các loại, lương TV 85%/CT 100%/PC trách nhiệm, 8 cột phụ cấp tách Taxable/Non-tax, OT, BHXH 2 phía, thuế TNCN, thực nhận, Profit/Cost Center-WBS"
scope_code: ["app/p26_template2.py"]
scope_test: ["tests/test_p26.py"]
acceptance_test: "python3 -m tests.test_p26"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p26-template2-master.run.json
---
# frame-p26-template2-master

## Nghiệp vụ
Đây là điểm hội tụ: mọi engine đổ số vào MỘT dòng phẳng mỗi NV cho kế toán import. Thuế TNCN v0 tính tối giản (thu nhập chịu thuế = lương + PC taxable + OT taxable − giảm trừ bản thân 11tr − BHXH NV) theo biểu lũy tiến — đủ để dòng tiền khớp logic, chưa phải quyết toán thật. Cột cost center lấy từ SAP allocation (mock đọc CSV nếu có, không có thì để trống).

## Input / Output
- **Input:** Kết quả p08–p21, giảm trừ + biểu thuế từ tham_so (assumed), hồ sơ
- **Output:** List dòng phẳng ~40 cột/NV, xuất được CSV

## Tiêu chí nghiệm thu
- NV004: lương = ngày_TV×85% + ngày_CT×100% đơn giá — tách đúng mốc 10/07
- Tổng (8) trên dòng = đúng tổng 7 cột PC thành phần
- Cột Non-tax cơm ≤ 730.000 với mọi NV
- Thuế NV thai sản (thu nhập 0) = 0, không âm

## Ngoài phạm vi
Không quyết toán thuế năm. Không đẩy SAP thật.
