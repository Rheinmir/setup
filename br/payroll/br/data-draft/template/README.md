# Draft — điền dữ liệu công ty thật

5 file CSV này là **mẫu trống** (chỉ có header + 1 dòng ví dụ) cho phần dữ liệu THUỘC VỀ CÔNG TY (khác các bảng định mức PRD đã cố định sẵn trong `br/data-draft/dinh_muc_*.csv`, `ot_multiplier.csv`, `ngay_le.csv`... — những bảng đó không cần điền lại).

## Cách dùng

1. Mở từng file bằng Excel/Google Sheets.
2. Xoá dòng "VÍ DỤ", điền dữ liệu thật (một dòng = một nhân viên/một ngày công/một tờ trình...).
3. Lưu lại dạng CSV (UTF-8), copy đè vào `br/data-draft/<tên file>.csv` (bỏ qua thư mục `template/`).
4. Chạy lại test: `python3 -m tests.test_p01` ... `test_p28` để xác nhận không lỗi.

## 5 file cần điền

| File | Một dòng là gì | Cột bắt buộc chú ý |
|---|---|---|
| `nhan_vien.csv` | Một nhân viên | `msnv` duy nhất, `employee_type` chỉ nhận `Official`/`MatBao`, `bo_phan_hien_tai` phải khớp tên trong `dm_bo_phan.csv` |
| `bang_cong_tho.csv` | Một ngày công của một nhân viên | `ky_hieu` phải nằm trong danh sách hợp lệ (xem comment trong file), `bo_phan_trong_ngay` khớp `dm_bo_phan.csv` |
| `dm_bo_phan.csv` | Một bộ phận/dự án | `khoi` chỉ nhận `VP` hoặc `CT`, `tinh` phải khớp tên tỉnh dùng trong `dm_khoang_cach.csv` |
| `to_trinh_duyet_rieng.csv` | Một tờ trình duyệt riêng | `loai_pc` chỉ nhận `xang_xe`/`di_lai`/`kho_khan`/`khac` |
| `suat_an_bo_sung.csv` | Một lượt cơm bổ sung thư ký chấm | `loai` chỉ nhận `com_chu_nhat`/`com_tang_ca_dem` |

## Origin
Tạo theo yêu cầu user 2026-07-09 — mẫu trống để nhập dữ liệu thật thay 12 NV mẫu hiện có.
