---
schema_version: 0
frame_id: frame-p07-parser-ky-hieu
created_by: slicer
parent_br: br/BR.md
clause_ids: [C4.2]
parent_br_hash: 06f8501d7472387c48709eed1947a0118c170e31ddc23c5b4e4282caca8bb9de
muc_tieu: "Parser ký hiệu công: phân loại 15+ ký hiệu (x, x1, OL, P/F, R/Fo, L, NB, Ts/TS, TSN, ON/OD, TN, Ro, TC100/200/300, ?P) thành thuộc tính máy hiểu"
scope_code: ["app/p07_kyhieu.py"]
scope_test: ["tests/test_p07.py"]
acceptance_test: "python3 -m tests.test_p07"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p07-parser-ky-hieu.run.json
---
# frame-p07-parser-ky-hieu

## Nghiệp vụ
Mỗi ô bảng công là một ký hiệu quy ước của HR. Toàn bộ logic sau (đếm công, suất ăn, BHXH, OT) rẽ nhánh theo thuộc tính của ký hiệu: có phải ngày làm việc thực tế không, có hưởng lương không, có tính đóng BHXH không, có phải chờ duyệt không. Frame này là bảng tra duy nhất ký_hiệu → thuộc tính; thêm ký hiệu mới chỉ sửa một chỗ.

## Input / Output
- **Input:** Chuỗi ký hiệu (kể cả biến thể hoa/thường P/F, Ts/TS)
- **Output:** phan_loai(kh) → {lam_viec_thuc_te, huong_luong, tinh_bhxh, cho_duyet, he_so_tc, loai}

## Tiêu chí nghiệm thu
- 'x' → lam_viec_thuc_te=True, huong_luong=True, tinh_bhxh=True
- 'Ro' → cả 3 False; 'Ts' → không làm việc, không tính đóng BHXH
- '?P' → cho_duyet=True, KHÔNG cộng công hưởng lương (C6.2)
- 'TC200' → he_so_tc=200; ký hiệu lạ → raise, fail-closed

## Ngoài phạm vi
Không đếm tổng (p08). Không tính tiền OT (p21).
