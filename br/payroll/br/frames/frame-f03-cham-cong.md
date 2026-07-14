---
schema_version: 0
frame_id: frame-f03-cham-cong
created_by: slicer
parent_br: br/BR.md
clause_ids: [C6.1, C6.2, C6.3]
parent_br_hash: 2332e28da09ebdd69a6e153974fd7a58dabd8cc667294de676e350f1a05eb70a
muc_tieu: "Bộ ký hiệu chấm công và tổng ngày công hưởng lương PAID_DAYS theo đúng công thức đang chạy thật — đơn chờ duyệt không được cộng, ngày ốm BHXH và ngày điều chỉnh KHÔNG cộng"
scope_code: ["app/chamcong.py"]
scope_test: ["tests/test_f03.py"]
acceptance_test: "python3 -m tests.test_f03"
ui_role: none
ui_screen: 
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-f03-cham-cong.run.json
---
# frame-f03-cham-cong

## Nghiệp vụ

`PAID_DAYS` (tổng số ngày làm việc hưởng lương) là mẫu số/tử số của gần như mọi công thức phía sau. Đây cũng là một trong 10 field mà chính HR đã chấm 'lệch' giữa công thức họ ĐỊNH làm và công thức ĐANG chạy: bản định làm có cộng thêm ngày ốm BHXH và ngày công điều chỉnh, bản đang chạy thì KHÔNG. Engine bám bản đang chạy (BR C3.1) — vì đó là số nhân viên thực sự nhận được tiền.

Đơn nghỉ ở trạng thái chờ duyệt (`?P`) tuyệt đối không được cộng vào công hưởng lương: đó là kỷ luật chống 'duyệt muộn ăn gian công'.

## Input / Output

- **Input:** bản ghi nhân viên (loại hợp đồng + các loại ngày công trong kỳ)
- **Output:** `KY_HIEU` (bảng ký hiệu); `tinh_cong_huong_luong(ký_hiệu)` → bool; `paid_days(rec)` → `Decimal`

## Tiêu chí nghiệm thu

- Đủ bộ ký hiệu tối thiểu: x, x1, OL, P, L, NB, Ts, ON, Ro, ?P
- Ký hiệu `?P` (chờ duyệt) → KHÔNG tính công hưởng lương
- Ground-truth dòng 9: chính thức 19,5 công + 2,5 lễ → PAID_DAYS = 22
- Có 5 ngày ốm BHXH và 3 ngày điều chỉnh → VẪN không cộng (as-is), kết quả không đổi
- Thử việc → lấy ngày công thử việc thay cho ngày chính thức

## Ngoài phạm vi

Không parse file chấm công thô từ Workday (đó là adapter). Không tính tiền.
