---
schema_version: 0
frame_id: frame-p06-workday-adapter
created_by: slicer
parent_br: br/BR.md
clause_ids: [C4.2]
parent_br_hash: 19d405e59625a1192e74e53a7e1bc00778cbf92f9fe223f000d8d40994ab610e
muc_tieu: "Adapter Workday mock (ranh giới BNAL verified:false): đọc bảng công thô ngày×NV + hồ sơ + EmployeeType + ngày kết thúc thử việc từ CSV thay cho API thật"
scope_code: ["app/p06_workday.py"]
scope_test: ["tests/test_p06.py"]
acceptance_test: "python3 -m tests.test_p06"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p06-workday-adapter.run.json
---
# frame-p06-workday-adapter

## Nghiệp vụ
PRD chốt Workday là nguồn tích hợp duy nhất nhưng ta chưa có API thật — đây chính là ranh giới build-now-adapt-later: toàn hệ chỉ nói chuyện với adapter này, sau này thay ruột (CSV → REST Workday) mà không chạm frame nào khác. Adapter trả dữ liệu THÔ đúng như Workday: từng ngày từng NV một ký hiệu, không tổng hợp gì (đó là việc của nhóm T).

## Input / Output
- **Input:** data-draft/bang_cong_tho.csv + nhan_vien.csv, tháng kỳ
- **Output:** cong_tho(ky) → list bản ghi {msnv, ngay, ky_hieu, bo_phan, so_gio}; ho_so(msnv) → dict hồ sơ; verified:false flag trên module

## Tiêu chí nghiệm thu
- Đọc đủ mọi bản ghi của kỳ 07/2026 trong CSV, lọc đúng biên 21/06–20/07
- Bản ghi ?P được trả về NGUYÊN TRẠNG (không tự cộng công)
- ho_so('NV005').employee_type == 'MatBao'
- Module khai VERIFIED=False và mọi hàm đi qua một cửa duy nhất

## Ngoài phạm vi
Không gọi HTTP thật. Không tổng hợp công. Không sync-back (p24).
