---
schema_version: 0
frame_id: frame-p02-master-data-store
created_by: slicer
parent_br: br/BR.md
clause_ids: [C7]
parent_br_hash: 06f8501d7472387c48709eed1947a0118c170e31ddc23c5b4e4282caca8bb9de
muc_tieu: "Nạp và tra cứu 3 danh mục nền từ CSV: DM Bộ phận (→tỉnh/khối/vùng có ngày hiệu lực), DM Nơi cư trú, DM Khoảng cách (cặp nơi tuyển–tỉnh → dải)"
scope_code: ["app/p02_masterdata.py"]
scope_test: ["tests/test_p02.py"]
acceptance_test: "python3 -m tests.test_p02"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p02-master-data-store.run.json
---
# frame-p02-master-data-store

## Nghiệp vụ
PC đi lại và công tác xa đều tra chuỗi: nơi tuyển dụng × tỉnh của bộ phận → số km → dải khoảng cách. Ba danh mục này PRD yêu cầu 'phải quản trị được' và có ngày hiệu lực (ví dụ Kho miền Nam đổi về Bình Dương từ 06/2025 — tra tại thời điểm nào phải ra tỉnh đúng thời điểm đó). Frame này là kho tra cứu duy nhất, mọi frame phụ cấp gọi qua đây, không frame nào tự đọc CSV.

## Input / Output
- **Input:** 3 file CSV trong br/data-draft/ (dm_bo_phan, dm_noi_cu_tru, dm_khoang_cach), ngày tra cứu
- **Output:** API: bo_phan_info(ten, ngay)→(tinh,khoi,vung); dai_khoang_cach(noi_tuyen, tinh_bp)→dải; khu_vuc(tinh)→miền

## Tiêu chí nghiệm thu
- bo_phan_info('Kho miền Nam','2025-07-01') → Bình Dương; trước 06/2025 → TP.HCM
- dai_khoang_cach('TP.HCM','Quảng Ninh') → khac_mien
- Bộ phận không tồn tại → raise lỗi rõ nghĩa, không trả None câm

## Ngoài phạm vi
Không chứa bảng ĐỊNH MỨC (p03). Không có UI quản trị.
