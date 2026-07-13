---
schema_version: 0
frame_id: frame-f99-lap-rap
created_by: human
kind: assemble
parent_br: br/BR.md
clause_ids: [C17.1, C17.2, C17.3, C17.6]
parent_br_hash: b859c2b5c4dc70c65391f61a3eb1ad9c883359d3c3f1c2e11714b3d3112f9f6c
muc_tieu: "Lắp toàn bộ engine chạy trên dòng dữ liệu THẬT của HR rồi đối chiếu từng đồng với 30 cột kết quả trong bảng lương đang dùng — sai một đồng là đỏ"
scope_code: ["app/pipeline.py"]
scope_test: ["tests/test_f99.py"]
acceptance_test: "python3 -m tests.test_f99"
ui_role: none
ui_screen: 
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
---
# frame-f99-lap-rap

## Nghiệp vụ

Frame LẮP RÁP: nó không sửa một module nào, chỉ nối chúng lại và đem so với sự thật. Đây là cổng nghiệm thu của cả dự án — HR sẽ không tin engine nào không tái lập được bảng lương họ đang trả.

Ba lớp kiểm: (1) đối chiếu 30 cột kết quả của dòng 9 — từ tổng thu nhập, bảo hiểm, thuế, tới lương thực nhận 189.930.161 và chi phí công ty; (2) hai ô TỰ KIỂM mà chính Excel mang sẵn — sổ phải cân về 0, và hai cách tính thuế khác nhau phải ra cùng kết quả; (3) đổi sang bộ tham số kỳ cũ thì số phải đổi theo — chứng minh 'cấu hình được' là thật.

Cuối cùng là bài đo hiệu năng: nhân bản thành 4.179 nhân sự (đúng bằng roster thật ở Workday) và phải chạy dưới 5 phút.

## Input / Output

- **Input:** fixture ground-truth `tests/fixtures/gt1_row9.json` (input + 30 cột kết quả thật)
- **Output:** `tinh(inputs, period)` → dict kết quả; `doi_chieu(gt)` → danh sách dòng lệch (rỗng = khớp); `chay_roster(rows, period)`; `pit_sumproduct(x)` (cách tính thuế thứ hai để tự kiểm)

## Tiêu chí nghiệm thu

- Đối chiếu 30 cột của ground-truth: **rỗng** — không một đồng lệch
- Đích cuối: lương thực chi = 189.930.161
- Ô tự kiểm cân sổ: tổng thu nhập − bảo hiểm − thuế + cộng sau thuế − trừ sau thuế − lương thực nhận = **0**
- Ô tự kiểm thuế: tính theo bậc thang ≡ tính theo cách tích lũy → cùng kết quả
- Đổi sang bộ tham số kỳ cũ → giảm trừ 24,2tr, thuế 53.852.200, lương thực nhận KHÁC đi
- 4.179 nhân sự chạy dưới 5 phút

## Ngoài phạm vi

KHÔNG sửa bất kỳ module nào của engine (đó là việc của frame chủ). Nếu số lệch thì báo đúng field lệch, không tự vá.
