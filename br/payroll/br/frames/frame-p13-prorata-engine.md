---
schema_version: 0
frame_id: frame-p13-prorata-engine
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.2, C5.4]
parent_br_hash: 06f8501d7472387c48709eed1947a0118c170e31ddc23c5b4e4282caca8bb9de
muc_tieu: "Engine pro-rata dùng chung: (định mức/công chuẩn)×ngày hưởng; tự kích hoạt quy tắc <14 ngày (ngày hưởng = LV thực tế + lễ) và chia theo bộ phận với định mức từng nơi — tái lập đúng Ví dụ 2 PRD"
scope_code: ["app/p13_prorata.py"]
scope_test: ["tests/test_p13.py"]
acceptance_test: "python3 -m tests.test_p13"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p13-prorata-engine.run.json
---
# frame-p13-prorata-engine

## Nghiệp vụ
Mọi phụ cấp cố định tháng đi qua đúng một công thức pro-rata, khác nhau chỉ ở định mức. Khi tổng ngày làm việc thực tế trong kỳ dưới 14, ngày hưởng co lại còn 'LV thực tế + lễ' (loại phép, nghỉ hưởng lương khác, không lương). Khi điều động, tách phép tính theo từng bộ phận với định mức của từng nơi. Đặt thành engine chung để 5 loại PC sau chỉ truyền định mức vào, không lặp logic.

## Input / Output
- **Input:** Ma trận bộ_phận×loại_ngày (p10), công chuẩn (p01), hàm định_mức(bộ_phận)→tiền (p03/p04)
- **Output:** Dict bo_phan → tiền PC + tổng, kèm vết tính (ngày hưởng, định mức, nguồn) cho C8 truy vết

## Tiêu chí nghiệm thu
- Tái lập Ví dụ 2: LV 3+3=6 <14 → PC = (3+1)/chuẩn×ĐM_A + (3+2)/chuẩn×ĐM_B
- NV đủ ≥14 ngày → ngày hưởng đếm đủ theo quy tắc thường
- Mỗi kết quả kèm trace string đủ 4 yếu tố: công thức + ngày + định mức + nguồn

## Ngoài phạm vi
Không biết loại PC cụ thể. Không tách thuế (từng PC tự khai).
