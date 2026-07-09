---
schema_version: 0
frame_id: frame-p18-pc-ct-ctx
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.3.5]
parent_br_hash: bd8b0c1092b3518507e218bdafbdb5dc39535405ea63f7a591e410a3c114e81d
muc_tieu: "PC công trường + công tác xa: bảng khối (CT/VP) × dải khoảng cách × 2 đối tượng (ĐH+ / CĐ-TC-Nghề); pro-rata + <14 ngày + chia bộ phận"
scope_code: ["app/p18_pcctctx.py"]
scope_test: ["tests/test_p18.py"]
acceptance_test: "python3 -m tests.test_p18"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p18-pc-ct-ctx.run.json
---
# frame-p18-pc-ct-ctx

## Nghiệp vụ
Khoản này đi cùng cặp với đi lại nhưng bảng khác: chỉ 2 nhóm đối tượng theo trình độ và có định mức cho cả khối VP khi làm xa. Dùng chung chuỗi tra dải của p02 và engine p13; GĐDA cũng bị loại theo C5.3.7.

## Input / Output
- **Input:** Như p17 nhưng bảng dinh_muc_ct_congtacxa.csv
- **Output:** Tiền PC (4) theo bộ phận + tổng + trace

## Tiêu chí nghiệm thu
- CT + khac_mien + ĐH → 3.000.000; VP + 30-100 + CĐ → 700.000
- CT <30km → 1.000.000 (ĐH) — khác đi lại (=0) là ĐÚNG thiết kế
- GĐDA → 0

## Ngoài phạm vi
Không đụng PC CT xa theo dự án (p19).
