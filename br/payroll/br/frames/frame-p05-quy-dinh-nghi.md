---
schema_version: 0
frame_id: frame-p05-quy-dinh-nghi
created_by: slicer
parent_br: br/BR.md
clause_ids: [C7]
parent_br_hash: bd8b0c1092b3518507e218bdafbdb5dc39535405ea63f7a591e410a3c114e81d
muc_tieu: "Quy định ngày nghỉ: phép năm 12 ngày +1/5 năm thâm niên, tháng đạt ≥50% công chuẩn mới tính phép, phép tồn dùng đến 31/12 năm kế, ốm Cty 3 ngày/năm"
scope_code: ["app/p05_nghiphep.py"]
scope_test: ["tests/test_p05.py"]
acceptance_test: "python3 -m tests.test_p05"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p05-quy-dinh-nghi.run.json
---
# frame-p05-quy-dinh-nghi

## Nghiệp vụ
Bảng công chi tiết HR đòi cột 'phép năm hiện tại và phép còn lại'. Quyền phép sinh theo tháng làm việc (tháng nào đạt từ nửa công chuẩn trở lên mới cộng phép tháng đó), cộng thâm niên mỗi 5 năm. Phép tồn năm trước còn giá trị đến hết 31/12 năm kế tiếp, hệ trừ phép tồn trước rồi mới trừ phép năm nay. Frame này tính số dư phép tại một ngày bất kỳ để báo cáo và để loop nghiệm thu.

## Input / Output
- **Input:** Hồ sơ NV (ngày vào), lịch sử công theo tháng, số phép đã dùng (từ bảng công ký hiệu P/F)
- **Output:** so_du_phep(msnv, ngay) → (phep_ton_nam_truoc, phep_nam_nay, da_dung, con_lai)

## Tiêu chí nghiệm thu
- NV vào 2021 → thâm niên 5 năm 2026 → quyền 13 ngày/năm
- Tháng chỉ đạt 40% công chuẩn → không cộng phép tháng đó
- Phép tồn 2025 dùng được đến 31/12/2026, sang 01/01/2027 = 0
- Trừ phép: tồn cũ trước, phép năm nay sau

## Ngoài phạm vi
Không duyệt đơn nghỉ (p24). Không tính tiền lương phép (p26).
