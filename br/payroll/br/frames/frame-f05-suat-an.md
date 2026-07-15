---
schema_version: 0
frame_id: frame-f05-suat-an
created_by: slicer
parent_br: br/BR.md
clause_ids: [C8.1, C8.2, C17.4]
parent_br_hash: 2d6165cbe2e2ae63778ff892f883df1ccb749b2242ef3a57a4b381a8b66e9ec5
muc_tieu: "Suất ăn theo nơi làm việc — văn phòng 1 bữa, công trường gần 2 bữa, công trường xa từ 30km 3 bữa; làm dưới 4 tiếng không được suất nào; tách phần cơm chịu thuế và miễn thuế"
scope_code: ["app/com.py"]
scope_test: ["tests/test_f05.py"]
acceptance_test: "python3 -m tests.test_f05"
ui_role: none
ui_screen: 
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-f05-suat-an.run.json
---
# frame-f05-suat-an

## Nghiệp vụ

Tiền cơm là khoản HR mất nhiều thời gian nhất và sai nhiều nhất, vì nó phụ thuộc vào việc hôm đó nhân viên ngồi ở đâu — chứ không phải anh ta thuộc phòng nào. Một người điều động giữa kỳ có thể ăn 1 bữa/ngày ở văn phòng rồi 3 bữa/ngày khi ra công trường xa.

Đây là frame hiện thực AC-1 — ví dụ chốt tại biên bản họp 23/03/2026 với khách hàng, nên nó là hợp đồng, không phải phỏng đoán. Phần cơm vượt 730.000đ/tháng phải chịu thuế TNCN, phần dưới ngưỡng thì không.

## Input / Output

- **Input:** danh sách ngày làm việc, mỗi ngày `{noi: "VP"|"CT_GAN"|"CT_XA", gio: số giờ}` + tham số kỳ
- **Output:** `so_bua(ngày)` → int; `tong_suat_an(danh sách)` → int; `meal_allow/meal_nontax/meal_tax` → `Decimal`

## Tiêu chí nghiệm thu

- Văn phòng 1 bữa, công trường <30km 2 bữa, công trường ≥30km 3 bữa
- Làm đúng 4 tiếng hoặc ít hơn → 0 bữa (mọi đối tượng); 4,5 tiếng → có bữa
- **AC-1**: 5 ngày văn phòng + 20 ngày dự án xa = 5×1 + 20×3 = **65 suất**
- Trong đó có ngày làm 2 tiếng → ngày ấy không tính, tổng còn 62
- 78 suất × 45.000 = 3.510.000 → miễn thuế 730.000, chịu thuế 2.780.000
- Cơm ít hơn ngưỡng → toàn bộ miễn thuế, phần chịu thuế = 0

## Ngoài phạm vi

Không tự đọc bảng chấm công từ Workday. Không xử lý cơm tăng ca đêm/Chủ nhật do thư ký chấm tay (nhập liệu, lô sau).
