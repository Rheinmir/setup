---
schema_version: 0
frame_id: frame-f10-thue-tncn
created_by: slicer
parent_br: br/BR.md
clause_ids: [C4.4, C4.6, C12.1, C12.2, C12.3]
parent_br_hash: 20c2df3e9bee61a36f153ad8b9e19a0fdadc5bb8d38b25bae7d90a089f9630b1
muc_tieu: "Thuế thu nhập cá nhân theo biểu 5 bậc lũy tiến, giảm trừ bản thân và người phụ thuộc, riêng thử việc người Việt chịu 10% và thử việc người nước ngoài chịu 20%"
scope_code: ["app/thue.py"]
scope_test: ["tests/test_f10.py"]
acceptance_test: "python3 -m tests.test_f10"
ui_role: none
ui_screen: 
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-f10-thue-tncn.run.json
---
# frame-f10-thue-tncn

## Nghiệp vụ

Biểu thuế là thứ mà BA nguồn tài liệu văn bản đều KHÔNG có — chúng chỉ viện dẫn 'theo quy định pháp luật hiện hành'. Chỉ có công thức sống trong Excel là nói thật: 5 bậc 5/10/20/30/35%. Sheet tham chiếu của chính file đó còn kèm một bảng 7 bậc CŨ, thiếu 4 dòng — bẫy. Engine bám công thức sống, và Excel tự kiểm bằng cách tính thuế theo hai cách khác nhau rồi so sánh (ô EX9 = TRUE).

Thu nhập tính thuế không bao giờ âm: `MAX(0, thu nhập chịu thuế − bảo hiểm − giảm trừ)`. Người thử việc không được giảm trừ bản thân.

## Input / Output

- **Input:** thu nhập tính thuế (`Decimal`), bản ghi (loại HĐ, quốc tịch, số người phụ thuộc), tham số kỳ
- **Output:** `pit` → `Decimal`; `total_ded` → `Decimal`; `taxable_inc(chịu thuế, bảo hiểm, giảm trừ)` → `Decimal` (không âm)

## Tiêu chí nghiệm thu

- Ground-truth dòng 9: 185.392.000 → thuế 50.387.200 (bậc 35% trừ 14,5tr)
- Bậc 1: 8tr → 400.000 · Bậc 2: 20tr → 1.500.000 · Bậc 3: 50tr → 6.500.000 · Bậc 4: 80tr → 14.500.000
- Biên bậc liên tục, không nhảy bậc sai ở đúng mốc 10.000.000
- Thu nhập 0 hoặc âm → thuế 0
- Thử việc + Việt Nam + từ 2tr → 10%; dưới 2tr → 0
- Thử việc + nước ngoài → 20%
- Giảm trừ dòng 9: 15,5tr + 3 × 6,2tr = 34.100.000; thử việc → 0
- Thu nhập tính thuế không âm
- Đổi sang bộ tham số kỳ cũ → giảm trừ 24,2tr, thuế 53.852.200 (chứng minh ngày hiệu lực hoạt động)

## Ngoài phạm vi

Không quyết toán thuế cuối năm. Không xử lý đăng ký người phụ thuộc với cơ quan thuế. Không tính lũy kế thu nhập nhiều kỳ.
