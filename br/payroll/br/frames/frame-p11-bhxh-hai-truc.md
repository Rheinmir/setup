---
schema_version: 0
frame_id: frame-p11-bhxh-hai-truc
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.1.4]
parent_br_hash: 06f8501d7472387c48709eed1947a0118c170e31ddc23c5b4e4282caca8bb9de
muc_tieu: "Quy đổi kỳ công 21–20 sang tháng dương lịch để đếm ngày tính/không tính đóng BHXH, xác định diện đóng, và tính các khoản trích NV 8/1.5/1 + Cty 17/0.5/3/1 + 2% KPCĐ"
scope_code: ["app/p11_bhxh.py"]
scope_test: ["tests/test_p11.py"]
acceptance_test: "python3 -m tests.test_p11"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p11-bhxh-hai-truc.run.json
---
# frame-p11-bhxh-hai-truc

## Nghiệp vụ
BHXH tính theo tháng dương lịch trong khi công chốt theo kỳ 21–20, nên một kỳ lương chứa đuôi tháng trước và đầu tháng này. Ngày thử việc, Ro, thai sản, ốm BHXH không tính đóng — đếm riêng để quyết tháng đó NV có thuộc diện đóng không, rồi nhân tỷ lệ trích 2 phía. Có cột Đ/C khi truy đóng/hoàn trả.

## Input / Output
- **Input:** Công thô phân loại (thuộc tính tinh_bhxh từ p07), map ngày→tháng BHXH (p01), lương đóng BHXH
- **Output:** Theo tháng dương lịch: {ngay_tinh, ngay_khong_tinh, dien_dong: bool, trich_nv, trich_cty, dc}

## Tiêu chí nghiệm thu
- NV010 thai sản cả tháng → dien_dong=False, trích = 0
- NV004: 8 ngày TV không tính + 9 ngày tính trong T7 (giả định đủ diện — theo ngưỡng cấu hình)
- Trích NV = lương × (8+1.5+1)%; Cty = lương × (17+0.5+3+1)% + 2% KPCĐ
- Ngày 25/06 của kỳ 07 phải rơi vào tháng BHXH 06

## Ngoài phạm vi
Không nộp hồ sơ BHXH thật. Ngưỡng 'diện đóng' đọc từ tham_so (assumed G6).
