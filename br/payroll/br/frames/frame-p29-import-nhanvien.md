---
schema_version: 0
frame_id: frame-p29-import-nhanvien
created_by: slicer
parent_br: br/BR.md
clause_ids: [C7.1]
parent_br_hash: 06f8501d7472387c48709eed1947a0118c170e31ddc23c5b4e4282caca8bb9de
muc_tieu: "Validate + import file CSV nhân viên upload từ UI — kiểm header đúng schema, từ chối file thiếu/thừa cột hoặc rỗng, chỉ ghi đè khi hợp lệ"
scope_code: ["app/p29_import.py"]
scope_test: ["tests/test_p29.py"]
acceptance_test: "python3 -m tests.test_p29"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p29-import-nhanvien.run.json
---
# frame-p29-import-nhanvien

## Nghiệp vụ
UI hiện tại không có chỗ nhập dữ liệu ngoài sửa CSV bằng tay — HR phải mở file trên đĩa, dễ gõ sai cột, không có validate trước khi ghi đè (feedback user 09/07, gap C7.1). Frame này là lớp validate: nhận nội dung CSV (dạng text, từ form upload), kiểm header khớp đúng 13 cột `nhan_vien.csv`, từ chối nếu thiếu/thừa cột hoặc không có dòng dữ liệu nào, chỉ khi hợp lệ mới cho phép ghi đè. Tách bạch việc "kiểm dữ liệu" (thuần, dễ test) khỏi việc "nhận HTTP upload" (thuộc `app/p28_ui.py`, nối dây sau khi frame này xanh — giống cách p26 nối p06-p19).

## Input / Output
- **Input:** `noi_dung_csv` (str) — toàn bộ nội dung file CSV dạng text; `duong_dan_dich` (str) — nơi ghi nếu hợp lệ (mặc định `br/data-draft/nhan_vien.csv`)
- **Output:** `(hop_le: bool, so_dong: int, loi: str|None)` — hop_le=True kèm so_dong>0 nghĩa là đã ghi đè xong; hop_le=False thì KHÔNG đụng file đích, loi giải thích lý do

## Tiêu chí nghiệm thu
- CSV đúng 13 cột header + 2 dòng dữ liệu hợp lệ → hop_le=True, so_dong=2, file đích được ghi đè đúng nội dung mới
- CSV thiếu 1 cột bắt buộc (vd thiếu `msnv`) → hop_le=False, loi nêu rõ cột thiếu, file đích GIỮ NGUYÊN không bị ghi đè
- CSV chỉ có header, không có dòng dữ liệu nào → hop_le=False, loi nêu "rỗng"
- CSV thừa cột lạ không có trong schema → hop_le=False, loi nêu rõ cột thừa

## Ngoài phạm vi
Không nhận HTTP request trực tiếp (đó là app/p28_ui.py, nối sau). Chưa hỗ trợ import bang_cong_tho.csv/các CSV khác (G11 trong BR.md) — chỉ nhan_vien.csv đợt này.
