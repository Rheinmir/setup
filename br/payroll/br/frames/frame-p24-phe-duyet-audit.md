---
schema_version: 0
frame_id: frame-p24-phe-duyet-audit
created_by: slicer
parent_br: br/BR.md
clause_ids: [C6.2]
parent_br_hash: 06f8501d7472387c48709eed1947a0118c170e31ddc23c5b4e4282caca8bb9de
muc_tieu: "Vòng phê duyệt: đơn ?P không cộng công; HR Override có lý do bắt buộc; sync-back trạng thái 'Đã duyệt' về Workday (mock); audit log bất biến cũ→mới+người+lúc+lý do"
scope_code: ["app/p24_pheduyet.py"]
scope_test: ["tests/test_p24.py"]
acceptance_test: "python3 -m tests.test_p24"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p24-phe-duyet-audit.run.json
---
# frame-p24-phe-duyet-audit

## Nghiệp vụ
Đơn treo ?P là trạng thái chặn lương — chỉ thoát khi quản lý duyệt hoặc HR override. Override là quyền mạnh nên PRD trói bằng audit bắt buộc và sync-back để Workday không lệch Payroll. Sync-back đi qua adapter p06 (ranh giới verified:false). Audit log là append-only — không API sửa/xóa.

## Input / Output
- **Input:** Đơn ?P từ công thô, hành động duyệt {nguoi, ly_do}, adapter p06
- **Output:** Trạng thái đơn mới + bản ghi audit + lệnh sync-back (mock ghi file)

## Tiêu chí nghiệm thu
- Duyệt đơn NV012 → ký hiệu ?P thành công thật, công được cộng lại
- Override thiếu lý do → từ chối
- Mỗi override sinh đúng 2 bản ghi: audit + sync-back 'Đã duyệt'
- Audit không có API delete/update — thử gọi → AttributeError

## Ngoài phạm vi
Không gửi Teams thật (p27 mock notify). Không màn hình duyệt (p28).
