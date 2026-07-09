---
schema_version: 0
frame_id: frame-p08-tach-thu-viec
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.1.1]
parent_br_hash: 19d405e59625a1192e74e53a7e1bc00778cbf92f9fe223f000d8d40994ab610e
muc_tieu: "Đếm tách ngày công giai đoạn thử việc / sau thử việc theo 'Ngày kết thúc thử việc', gồm cả ngày nghỉ hưởng lương của từng giai đoạn — nền tính lương 85%/100%"
scope_code: ["app/p08_thuviec.py"]
scope_test: ["tests/test_p08.py"]
acceptance_test: "python3 -m tests.test_p08"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p08-tach-thu-viec.run.json
---
# frame-p08-tach-thu-viec

## Nghiệp vụ
Workday chỉ cho 'ngày kết thúc thử việc', không chia sẵn. Khi mốc này rơi giữa kỳ (NV004: 10/07 trong kỳ 21/06–20/07), hệ phải cắt kỳ làm hai đoạn và đếm riêng từng đoạn — mỗi đoạn gồm ngày đi làm cộng ngày nghỉ hưởng lương của chính đoạn đó. Kế toán lấy 2 con số này nhân đơn giá 85%/100%.

## Input / Output
- **Input:** Công thô đã phân loại (p06+p07), ngay_ket_thuc_thu_viec từ hồ sơ, biên kỳ (p01)
- **Output:** {ngay_tv, ngay_sau_tv} — mỗi cái tách {lam_viec, nghi_huong_luong}

## Tiêu chí nghiệm thu
- NV004 mốc 10/07: ngày ≤ 09/07 vào giai đoạn TV, từ 10/07 vào chính thức
- Ngày phép P nằm trong đoạn TV được đếm vào nghỉ hưởng lương của TV
- NV không có mốc (đã chính thức từ lâu) → toàn bộ vào sau_tv
- Mắt Bão không có mốc thử việc → không vỡ

## Ngoài phạm vi
Không tính tiền (p26). Không xử lý bổ nhiệm (p09).
