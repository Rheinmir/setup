---
schema_version: 0
frame_id: frame-p10-tach-dieu-dong
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.1.3]
parent_br_hash: bd8b0c1092b3518507e218bdafbdb5dc39535405ea63f7a591e410a3c114e81d
muc_tieu: "Đếm ngày công tại TỪNG bộ phận khi điều động giữa kỳ, tách theo loại ngày (làm việc/lễ/phép/nghỉ hưởng lương/không lương) tại mỗi nơi, kèm ngày điều động"
scope_code: ["app/p10_dieudong.py"]
scope_test: ["tests/test_p10.py"]
acceptance_test: "python3 -m tests.test_p10"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p10-tach-dieu-dong.run.json
---
# frame-p10-tach-dieu-dong

## Nghiệp vụ
Điều động là ca phức tạp nhất PRD vì mọi phụ cấp gắn địa điểm phải chia và BỔ CHI PHÍ theo từng bộ phận. Nguồn sự thật là cột bộ phận trên từng dòng công thô (Workday ghi NV làm ở đâu ngày nào). Frame này gom về ma trận bộ_phận × loại_ngày — đầu vào trực tiếp của quy tắc <14 ngày (Ví dụ 2 PRD) và suất ăn theo nơi (Ví dụ 1).

## Input / Output
- **Input:** Công thô phân loại của 1 NV trong kỳ (đã có bộ phận từng ngày)
- **Output:** Dict bo_phan → {lam_viec, le, phep, nghi_huong_luong, khong_luong, tong}, + ngay_dieu_dong

## Tiêu chí nghiệm thu
- Tái lập Ví dụ 2 PRD: A={LV 3, lễ 1, phép 6}, B={LV 3, phép 7, R 2, Ro 1, lễ 2}
- NV001: VP HCM 10 ngày + Quan Lạn 6 ngày, ngày điều động 05/07
- NV không điều động → dict 1 bộ phận

## Ngoài phạm vi
Không tính tiền phụ cấp (p13). Không tra định mức.
