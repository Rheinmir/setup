---
schema_version: 0
frame_id: frame-p09-tach-bo-nhiem
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.1.2]
parent_br_hash: 06f8501d7472387c48709eed1947a0118c170e31ddc23c5b4e4282caca8bb9de
muc_tieu: "Tách 2 giai đoạn trước/sau bổ nhiệm khi có thay đổi lương hoặc PC trách nhiệm giữa kỳ; PC trách nhiệm = ngày hưởng × (định mức / công chuẩn) theo từng giai đoạn"
scope_code: ["app/p09_bonhiem.py"]
scope_test: ["tests/test_p09.py"]
acceptance_test: "python3 -m tests.test_p09"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p09-tach-bo-nhiem.run.json
---
# frame-p09-tach-bo-nhiem

## Nghiệp vụ
Bổ nhiệm giữa kỳ (NV003 lên GS chính 01/07) sinh 2 mức trong cùng kỳ lương. PRD cấm xử lý tay: hệ tự tách dòng theo ngày hiệu lực và tính từng giai đoạn theo thời gian làm việc thực tế. Cùng cơ chế áp cho điều chỉnh lương giữa kỳ.

## Input / Output
- **Input:** Công thô phân loại, danh sách hiệu lực bổ nhiệm {msnv, ngay_hieu_luc, muc_cu, muc_moi}, công chuẩn kỳ
- **Output:** List giai đoạn {tu, den, ngay_huong, muc} + tiền PC trách nhiệm từng đoạn

## Tiêu chí nghiệm thu
- NV003 hiệu lực 01/07: đoạn 21/06–30/06 mức cũ, 01/07–20/07 mức mới
- PC trách nhiệm mỗi đoạn = ngày hưởng đoạn × mức đoạn / công chuẩn
- Không có bổ nhiệm → 1 giai đoạn duy nhất, số khớp cách tính thường

## Ngoài phạm vi
Không quyết ai được bổ nhiệm. Không đụng PC khác (p13+).
