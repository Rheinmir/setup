---
schema_version: 0
frame_id: frame-f01-params
created_by: slicer
parent_br: br/BR.md
clause_ids: [C4.1, C4.2, C4.3, C4.4, C4.5, C4.6]
parent_br_hash: b859c2b5c4dc70c65391f61a3eb1ad9c883359d3c3f1c2e11714b3d3112f9f6c
muc_tieu: "Tham số lương ở MỘT chỗ duy nhất, chọn theo ngày hiệu lực — trần BHXH, tỷ lệ đóng, biểu thuế 5 bậc, giảm trừ gia cảnh, đơn giá cơm; đổi số không được sửa code"
scope_code: ["app/params.py"]
scope_test: ["tests/test_f01.py"]
acceptance_test: "python3 -m tests.test_f01"
ui_role: none
ui_screen: 
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
---
# frame-f01-params

## Nghiệp vụ

Mọi con số 'ma thuật' của payroll (trần đóng bảo hiểm 46,8tr, giảm trừ bản thân 15,5tr, đơn giá cơm 45k, 5 bậc thuế) nằm trong `data/params.json`, KHÔNG được viết cứng trong code. Mỗi bộ tham số có `effective_from`: kỳ lương cũ phải chạy lại được ra đúng số cũ (payslip cũ dùng giảm trừ 11tr, bảng lương nay dùng 15,5tr — cùng một engine). Nhà nước tăng lương cơ sở thì HR sửa 1 file JSON, không gọi dev.

Hai trần BHXH cùng tồn tại và đó KHÔNG phải lỗi: cột `INS_SAL_BH` hiển thị trần 50,6tr, nhưng mọi công thức tính bảo hiểm lại ăn trần 46,8tr. Excel bàn giao tự tố cáo mâu thuẫn này bằng ô kiểm của chính nó. Engine phải giữ cả hai.

## Input / Output

- **Input:** mã kỳ lương dạng `"YYYY-MM"` (vd `"2026-03"`) và (tuỳ chọn) đường dẫn file params
- **Output:** dict tham số của bộ có `effective_from` lớn nhất mà vẫn ≤ kỳ đang tính; `ValueError` nếu không bộ nào áp được

## Tiêu chí nghiệm thu

- Kỳ 2026-03 → giảm trừ bản thân 15.500.000, NPT 6.200.000
- Kỳ 2024-06 → giảm trừ bản thân 11.000.000, NPT 4.400.000 (bộ cũ)
- Trả về CẢ HAI trần: `ins_cap_bh_display` = 50.600.000 và `ins_cap_bh` = 46.800.000
- Biểu thuế đúng 5 bậc; `ot_from_hours` = false
- Kỳ trước mọi bộ tham số (1999-01) → ném `ValueError`, không im lặng lấy bừa

## Ngoài phạm vi

Không đọc từ DB, không gọi mạng. Không tự suy tham số thiếu. Không xử lý logic nghiệp vụ nào — chỉ tra cứu.
