---
schema_version: 0
frame_id: frame-p25-template0-trinh-ky
created_by: slicer
parent_br: br/BR.md
clause_ids: [C6.3]
parent_br_hash: 06f8501d7472387c48709eed1947a0118c170e31ddc23c5b4e4282caca8bb9de
muc_tieu: "Template 0 trình ký: định dạng chung Chính thức + Mắt Bão; NV điều động gộp TOÀN BỘ công tháng vào bảng của dự án nơi làm việc ngày 20 để CHT tại đó ký"
scope_code: ["app/p25_template0.py"]
scope_test: ["tests/test_p25.py"]
acceptance_test: "python3 -m tests.test_p25"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p25-template0-trinh-ky.run.json
---
# frame-p25-template0-trinh-ky

## Nghiệp vụ
Bảng trình ký in theo TỪNG dự án cho chỉ huy trưởng ký xác nhận công. Quy tắc điều động dễ sai nhất: không chia bảng theo đoạn mà GỘP cả tháng về dự án cuối — nơi NV có mặt ngày 20. Frame xuất cấu trúc dữ liệu bảng (render CSV/HTML ở p28), chỉ chứa NGÀY CÔNG không chứa tiền vì CHT không được thấy tiền (C3).

## Input / Output
- **Input:** Tổng hợp công theo NV (p08–p10), bộ phận ngày 20 của từng NV, employee_type
- **Output:** Dict du_an → bảng [{msnv, ho_ten, chuc_danh, cong_thuong, cong_cn, phep_le, tong}]

## Tiêu chí nghiệm thu
- NV001 (điều động 05/07, ngày 20 ở Quan Lạn) → xuất hiện DUY NHẤT ở bảng Quan Lạn với đủ 16 công cả tháng
- Bảng có cả Mắt Bão (NV005) chung định dạng
- Không cột nào chứa tiền — assert từ khóa lương/phụ cấp vắng mặt

## Ngoài phạm vi
Không ký số thật. Không render HTML (p28).
