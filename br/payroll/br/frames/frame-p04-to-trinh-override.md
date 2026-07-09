---
schema_version: 0
frame_id: frame-p04-to-trinh-override
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.2, C5.3.3, C5.3.7]
parent_br_hash: 19d405e59625a1192e74e53a7e1bc00778cbf92f9fe223f000d8d40994ab610e
muc_tieu: "Danh sách Tờ trình duyệt riêng ghi đè định mức chung theo MSNV/nhóm/dự án kể từ ngày hiệu lực; GĐDA bị loại khỏi PC công trường/đi lại chung"
scope_code: ["app/p04_totrinh.py"]
scope_test: ["tests/test_p04.py"]
acceptance_test: "python3 -m tests.test_p04"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p04-to-trinh-override.run.json
---
# frame-p04-to-trinh-override

## Nghiệp vụ
Nhiều khoản không theo bảng chung: xăng VP chỉ có qua tờ trình, 02 tài xế HN đích danh, GĐDA 10tr, Ban TGĐ ô tô, Làng Tây khó khăn 2tr, thủ kho 1.5–2tr. Quy tắc PRD: định mức tờ trình GHI ĐÈ định mức chung kể từ ngày hiệu lực nhưng vẫn chịu pro-rata/<14 ngày. Frame này resolve định mức CUỐI CÙNG: hỏi p03 lấy mức chung, rồi phủ tờ trình nếu khớp (MSNV > nhóm > dự án), và chặn GĐDA khỏi PC (4)(5) theo bảng chung.

## Input / Output
- **Input:** data-draft/to_trinh_duyet_rieng.csv, MSNV + hồ sơ + bộ phận + ngày
- **Output:** dinh_muc_cuoi(loai_pc, msnv, ngay) → (số tiền, nguồn: 'QĐ chung'|'TT-2026/xxx')

## Tiêu chí nghiệm thu
- NV007 GĐDA: xăng → 10.000.000 nguồn TT-2026/018; PC đi lại → 0 kèm nguồn 'GĐDA loại trừ'
- NV006 tài xế HN → 2.600.000 nguồn TT-2026/031 (assumed)
- NV008 trước 21/06 mức khác(7)=0, từ 21/06 → 1.500.000 (ngày hiệu lực)
- NV thường không có tờ trình → trả mức p03 nguồn 'QĐ chung'

## Ngoài phạm vi
Không tính truy lĩnh do đổi hồi tố (p20). Không có màn hình nhập tờ trình.
