---
schema_version: 0
frame_id: frame-p23-mat-bao
created_by: slicer
parent_br: br/BR.md
clause_ids: [C6.1]
parent_br_hash: 19d405e59625a1192e74e53a7e1bc00778cbf92f9fe223f000d8d40994ab610e
muc_tieu: "Nhánh Mắt Bão: nhận diện EmployeeType từ adapter, áp lịch chốt công sớm (assumed ngày 15), lấy định mức từ grid riêng trên Payroll thay vì bảng chung"
scope_code: ["app/p23_matbao.py"]
scope_test: ["tests/test_p23.py"]
acceptance_test: "python3 -m tests.test_p23"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p23-mat-bao.run.json
---
# frame-p23-mat-bao

## Nghiệp vụ
Nhân sự thuê ngoài Mắt Bão đi chung đường ống tổng hợp công nhưng rẽ nhánh ở 3 điểm: chốt sớm hơn (sau mốc chốt thì công của họ đóng băng dù kỳ chung còn mở), định mức phụ cấp lấy từ grid admin tự nhập trên Payroll (không dính Quy định chung), và multiplier OT cột riêng. Frame này cài 3 điểm rẽ đó thành policy tra theo employee_type.

## Input / Output
- **Input:** employee_type từ hồ sơ (p06), matbao_dinh_muc_grid.csv, tham_so lịch chốt, ngày hiện tại
- **Output:** Policy object: {la_mat_bao, da_qua_chot, dinh_muc_grid(loai_pc)}

## Tiêu chí nghiệm thu
- NV005 → la_mat_bao=True, định mức điện thoại lấy từ grid (200k) không phải bảng ngạch
- Sau ngày 15 (assumed G4): công NV005 đóng băng, sửa bị từ chối
- NV chính thức → policy trong suốt, không đổi hành vi

## Ngoài phạm vi
Grid + lịch chốt toàn bộ assumed G4 — chờ HR; không tính lương Mắt Bão khác biệt ngoài 3 điểm rẽ.
