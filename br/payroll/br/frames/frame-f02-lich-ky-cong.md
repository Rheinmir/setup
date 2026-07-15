---
schema_version: 0
frame_id: frame-f02-lich-ky-cong
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.1, C5.2, C5.4]
parent_br_hash: 8d9fbb9d5f6efe5260ac72537c6d6aac516cdbd2891ed98ce053c3fbfee40fab
muc_tieu: "Lịch kỳ lương 21→20 và ngày công chuẩn — Văn phòng trừ Chủ nhật và nửa ngày thứ 7, Công trường chỉ trừ Chủ nhật; kèm danh mục ngày lễ"
scope_code: ["app/lichky.py"]
scope_test: ["tests/test_f02.py"]
acceptance_test: "python3 -m tests.test_f02"
ui_role: none
ui_screen: 
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-f02-lich-ky-cong.run.json
---
# frame-f02-lich-ky-cong

## Nghiệp vụ

Kỳ lương của Coteccons KHÔNG trùng tháng dương lịch: kỳ tháng 3/2026 chạy từ 21/02 đến 20/03. Mọi phép chia pro-rata đều lấy mẫu số là 'ngày công chuẩn' của kỳ, mà công chuẩn lại khác nhau giữa hai khối: khối Văn phòng làm việc nửa ngày thứ 7 (nên thứ 7 tính 0,5 công), khối Công trường làm cả thứ 7 (chỉ nghỉ Chủ nhật). Sai mẫu số này thì sai TOÀN BỘ lương và phụ cấp của mọi nhân sự.

Excel gốc tính bằng `NETWORKDAYS.INTL`; frame này tái lập bằng Python thuần.

## Input / Output

- **Input:** mã kỳ `"YYYY-MM"`, khối làm việc (`"VP"` | `"CT"`), năm (cho danh mục lễ)
- **Output:** `ky_cong()` → cặp ngày (đầu kỳ, cuối kỳ); `cong_chuan()` → `Decimal` số công chuẩn; `ngay_le()` → danh sách ngày lễ dương lịch

## Tiêu chí nghiệm thu

- Kỳ 2026-03 → 21/02/2026 đến 20/03/2026
- Kỳ 2026-01 bắt qua năm → 21/12/2025 đến 20/01/2026
- Công chuẩn Công trường kỳ 2026-03 = 24 (28 ngày − 4 Chủ nhật)
- Công chuẩn Văn phòng kỳ 2026-03 = 22 (24 − 4 thứ 7 × 0,5)
- Công chuẩn VP luôn nhỏ hơn CT ở mọi kỳ
- Ngày lễ cố định có 01/01, 30/04, 01/05, 02/09

## Ngoài phạm vi

Không tính ngày lễ ÂM lịch (Tết, Giỗ Tổ) — đó là bảng HR nhập tay, để lô sau. Không đọc lịch nghỉ của từng nhân sự.
