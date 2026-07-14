---
schema_version: 0
frame_id: frame-f11-tong-hop
created_by: slicer
parent_br: br/BR.md
clause_ids: [C13.1, C13.2, C13.3, C13.4, C13.5]
parent_br_hash: 5aa1c47fb9bc720f40479854a5a5f1bdd49da2a2366b9fdbe72b8bacf59d1d95
muc_tieu: "Cộng chuỗi cuối cùng ra LƯƠNG THỰC NHẬN — tổng thu nhập, thu nhập chịu thuế, lương thực nhận, chi phí công ty; giữ đúng hai điểm quái dị của bảng lương thật"
scope_code: ["app/tonghop.py"]
scope_test: ["tests/test_f11.py"]
acceptance_test: "python3 -m tests.test_f11"
ui_role: none
ui_screen: 
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-f11-tong-hop.run.json
---
# frame-f11-tong-hop

## Nghiệp vụ

Frame đích: mọi thứ phía trước đổ vào đây để ra con số nhân viên thực sự nhận. Hai điểm 'quái dị' phải giữ NGUYÊN vì bảng lương thật đang chạy như vậy (BR C3.1 — engine mới phải tái lập được bảng lương cũ trước khi được phép sửa nó):

1. **Điều chỉnh trừ đang bị CỘNG**: công thức sống là `SUM(...)` quét cả cột 'điều chỉnh trừ', nên HR nhập số ÂM khi muốn trừ. Nếu engine 'sửa cho đúng' thành phép trừ, mọi trường hợp có điều chỉnh sẽ sai dấu.
2. **Chi phí công ty tính trên LƯƠNG THỰC NHẬN**, không phải trên tổng thu nhập — bản 'định làm' dùng tổng thu nhập và ra 236.602.000 thay vì 201.522.161.

## Input / Output

- **Input:** bản ghi đã có lương thực tế + phụ cấp + OT + thưởng; các tổng bảo hiểm/thuế đã tính
- **Output:** `gross`, `taxable_gross`, `net_income`, `net_pay`, `total_cty_cost`, `budget_save` → `Decimal`

## Tiêu chí nghiệm thu

- Ground-truth dòng 9: tổng thu nhập 225.010.000; thu nhập chịu thuế 225.000.000
- Điều chỉnh trừ được CỘNG (nhập −1tr → tổng giảm 1tr, đúng dấu)
- **Lương thực nhận = 189.930.161** (đích cuối)
- Thu nhập thuần 169.114.800
- Chi phí công ty 201.522.161 — tính trên lương thực nhận, KHÔNG phải tổng thu nhập
- Quỹ dự phòng 305.018.667

## Ngoài phạm vi

Không tự tính bảo hiểm/thuế (nhận vào từ frame khác). Không xuất báo cáo.
