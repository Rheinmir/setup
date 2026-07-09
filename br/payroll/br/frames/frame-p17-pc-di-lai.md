---
schema_version: 0
frame_id: frame-p17-pc-di-lai
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.3.4]
parent_br_hash: 06f8501d7472387c48709eed1947a0118c170e31ddc23c5b4e4282caca8bb9de
muc_tieu: "PC đi lại: xác định nhóm đối tượng (CHT/CHT ME · ĐH+ · CĐ/TC/Nghề · NV.02), tra nơi tuyển dụng × tỉnh bộ phận → dải khoảng cách → định mức; pro-rata + <14 ngày + chia bộ phận"
scope_code: ["app/p17_pcdilai.py"]
scope_test: ["tests/test_p17.py"]
acceptance_test: "python3 -m tests.test_p17"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p17-pc-di-lai.run.json
---
# frame-p17-pc-di-lai

## Nghiệp vụ
Đi lại là PC tra chuỗi dài nhất: hồ sơ cho nơi tuyển dụng, bộ phận cho tỉnh, DM Khoảng cách cho dải, bảng định mức cho tiền theo dải × nhóm. Nhóm đối tượng có bẫy: CHT xếp riêng bất kể trình độ, NV.02 xếp riêng bất kể trình độ, còn lại chia theo bằng cấp. GĐDA bị loại (p04). Đây là PC nhạy nhất với điều động vì đổi bộ phận là đổi cả dải khoảng cách.

## Input / Output
- **Input:** Hồ sơ (nơi tuyển, trình độ, chức danh, ngạch), p02 (dải), p03 (định mức), p04 (loại trừ GĐDA), p13
- **Output:** Tiền PC đi lại theo bộ phận + tổng + trace đủ chuỗi tra

## Tiêu chí nghiệm thu
- NV001 CHT tuyển HCM làm Quan Lạn → dải khac_mien → 11.200.000 pro-rata đoạn Quan Lạn
- Đoạn VP HCM của NV001: dải <30 → 0
- NV009 NV.02: dải 30-100 → 250.000, áp quy tắc <14 ngày như Ví dụ 2
- NV007 GĐDA → 0, nguồn 'GĐDA loại trừ'

## Ngoài phạm vi
Không sửa DM khoảng cách (assumed G3 dải 400-1000).
