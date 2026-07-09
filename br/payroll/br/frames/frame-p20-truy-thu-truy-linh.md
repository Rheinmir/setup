---
schema_version: 0
frame_id: frame-p20-truy-thu-truy-linh
created_by: slicer
parent_br: br/BR.md
clause_ids: [C4.3]
parent_br_hash: 06f8501d7472387c48709eed1947a0118c170e31ddc23c5b4e4282caca8bb9de
muc_tieu: "Truy thu/truy lĩnh trong kỳ CHƯA khóa: định mức đổi hồi tố (trình độ, nơi tuyển, chức danh, tờ trình mới) → chênh = (mới − cũ) × ngày công tương ứng, cột riêng (3) kèm lý do"
scope_code: ["app/p20_truythu.py"]
scope_test: ["tests/test_p20.py"]
acceptance_test: "python3 -m tests.test_p20"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p20-truy-thu-truy-linh.run.json
---
# frame-p20-truy-thu-truy-linh

## Nghiệp vụ
Khi HR cập nhật thông tin có hiệu lực lùi (tờ trình ký muộn nhưng hiệu lực từ đầu kỳ), hệ không sửa đè con số cũ mà tính CHÊNH LỆCH thành dòng truy lĩnh riêng — đúng cột (3) và sheet 'Truy lãnh' file HR hiện hành. Chỉ áp trong kỳ chưa khóa; kỳ đã khóa thì C4.3 cấm tuyệt đối.

## Input / Output
- **Input:** Snapshot định mức cũ/mới + ngày hiệu lực hồi tố, ngày công tương ứng (p10), trạng thái khóa kỳ (p22)
- **Output:** List {msnv, loai_pc, chenh_lech, ly_do, so_to_trinh} — cột (3)

## Tiêu chí nghiệm thu
- NV008 TT-2026/029 hiệu lực 21/06 nhập ngày 07/07 → truy lĩnh = mức mới × ngày công từ 21/06
- Định mức giảm hồi tố → chênh ÂM (truy thu)
- Kỳ đã khóa → từ chối tính, báo rõ 'kỳ đã khóa — không truy thu tháng sau'

## Ngoài phạm vi
Không tự đổi hồ sơ. Không sửa số kỳ đã khóa.
