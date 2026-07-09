---
schema_version: 0
frame_id: frame-p14-pc-com
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.3.1]
parent_br_hash: 19d405e59625a1192e74e53a7e1bc00778cbf92f9fe223f000d8d40994ab610e
muc_tieu: "PC cơm = tổng suất ăn × đơn giá 45.000 (cấu hình); tách Non-tax ≤730.000 đ/tháng, phần vượt vào Taxable"
scope_code: ["app/p14_pccom.py"]
scope_test: ["tests/test_p14.py"]
acceptance_test: "python3 -m tests.test_p14"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p14-pc-com.run.json
---
# frame-p14-pc-com

## Nghiệp vụ
Cơm là phụ cấp duy nhất tính theo SUẤT chứ không pro-rata. Luật thuế TNCN miễn tối đa 730.000 đ/tháng cho tiền ăn — hệ tách hai cột ngay tại nguồn để Template 2 và bảng 6.4 dùng thẳng. Đơn giá là tham số cấu hình (tham_so_he_thong.csv), không hard-code.

## Input / Output
- **Input:** Tổng suất theo bộ phận (p12), đơn giá + trần miễn thuế từ tham_so_he_thong.csv
- **Output:** {thanh_tien, non_tax, taxable} theo bộ phận và tổng

## Tiêu chí nghiệm thu
- 65 suất × 45.000 = 2.925.000 → non_tax 730.000, taxable 2.195.000
- 16 suất × 45.000 = 720.000 → non_tax 720.000, taxable 0
- Đổi đơn giá trong config → kết quả đổi theo, không sửa code

## Ngoài phạm vi
Không đếm suất (p12). Không tính thuế TNCN cuối cùng (p26).
