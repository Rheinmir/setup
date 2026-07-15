---
schema_version: 0
frame_id: frame-f08-thuong-trich-quy
created_by: slicer
parent_br: br/BR.md
clause_ids: [C10.1, C10.2]
parent_br_hash: 2d6165cbe2e2ae63778ff892f883df1ccb749b2242ef3a57a4b381a8b66e9ec5
muc_tieu: "Thưởng là các khoản input cộng lại; trích quỹ thưởng hàng tháng thì có công thức thật — du lịch 500k, KPI một phần tư lương, tháng 13 một phần mười hai, Tết bị chặn trần 15 triệu chia 12"
scope_code: ["app/thuong.py"]
scope_test: ["tests/test_f08.py"]
acceptance_test: "python3 -m tests.test_f08"
ui_role: none
ui_screen: 
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-f08-thuong-trich-quy.run.json
---
# frame-f08-thuong-trich-quy

## Nghiệp vụ

Mỗi tháng công ty trích trước một phần chi phí để dành trả thưởng cuối năm (đây là chi phí công ty, không phải tiền nhân viên nhận). Bốn khoản trích này CÓ công thức thật và CÓ số đối chiếu trong dòng 9 ground-truth, nên bắt buộc phải đúng: du lịch = 6tr/12, KPI = lương HĐ/4, tháng 13 = lương HĐ/12, Tết = min(lương HĐ/12, 15tr/12).

Điều kiện chặn: người đã có ngày nghỉ việc thì không trích nữa; người không có ngày hưởng lương nào cũng không trích. Riêng việc XÉT thưởng (ai được nhận) có luật loại trừ: nghỉ thai sản/ốm dài/không lương lũy kế từ 10 ngày trở lên thì thời gian đó không tính vào thời gian xét thưởng.

## Input / Output

- **Input:** bản ghi (lương hợp đồng, PAID_DAYS, ngày nghỉ việc, ngày nghỉ lũy kế, các khoản thưởng input) + tham số
- **Output:** `bonus_total`; `bonus_save_travel/kpi/13m/tet` → `Decimal`; `du_dieu_kien_thuong` → bool

## Tiêu chí nghiệm thu

- Ground-truth dòng 9 (lương HĐ 200tr): du lịch 500.000 · KPI 50.000.000 · tháng 13 16.666.667 · Tết 1.250.000
- Thưởng Tết bị chặn trần: min(200tr/12, 15tr/12) = 1.250.000
- Lương thấp (12tr) → Tết = 1.000.000, không bị chặn
- Có ngày nghỉ việc → mọi khoản trích = 0
- Không có ngày hưởng lương → không trích
- Nghỉ lũy kế ≥ 10 ngày → loại khỏi diện xét thưởng; 9 ngày thì vẫn được

## Ngoài phạm vi

Không tính lương bình quân 12 tháng (cần lịch sử lương nhiều kỳ — lô sau). Không xử lý thưởng dự án/vượt lợi nhuận theo quy chế riêng.
