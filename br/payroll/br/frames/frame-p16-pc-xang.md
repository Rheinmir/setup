---
schema_version: 0
frame_id: frame-p16-pc-xang
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.3.3]
parent_br_hash: bd8b0c1092b3518507e218bdafbdb5dc39535405ea63f7a591e410a3c114e81d
muc_tieu: "PC nhiên liệu/xăng/ô tô: CT chuẩn 1.000.000 cho L2–L6; VP không mức chung — chỉ qua tờ trình (kể cả 02 tài xế HN đích danh, GĐDA, Ban TGĐ); pro-rata + <14 ngày"
scope_code: ["app/p16_pcxang.py"]
scope_test: ["tests/test_p16.py"]
acceptance_test: "python3 -m tests.test_p16"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p16-pc-xang.run.json
---
# frame-p16-pc-xang

## Nghiệp vụ
Xăng có cấu trúc nguồn kép: khối công trường ăn mức chuẩn theo Quy định, khối văn phòng mặc định KHÔNG có gì — chỉ ai nằm trong tờ trình mới hưởng, và mức tờ trình ghi đè tuyệt đối. Hai tài xế Hà Nội cấu hình đích danh theo MSNV. Frame này resolve nguồn qua p04 rồi pro-rata qua p13.

## Input / Output
- **Input:** Hồ sơ + level, khối bộ phận, resolver tờ trình (p04), engine (p13)
- **Output:** Tiền PC xăng theo bộ phận + tổng + nguồn định mức trong trace

## Tiêu chí nghiệm thu
- NV level L3 tại CT không tờ trình → 1.000.000 pro-rata, nguồn 'QĐ chung'
- NV002 VP không tờ trình → 0
- NV006 tài xế HN → mức TT-2026/031, trace ghi số tờ trình
- NV007 GĐDA → 10.000.000 pro-rata nguồn TT-2026/018

## Ngoài phạm vi
Không quản trị màn hình tờ trình. Mức tài xế là assumed G1 — chờ HR.
