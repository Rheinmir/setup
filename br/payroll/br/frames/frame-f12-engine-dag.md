---
schema_version: 0
frame_id: frame-f12-engine-dag
created_by: slicer
parent_br: br/BR.md
clause_ids: [C3.1, C3.2, C3.3, C14.1, C8.8]
parent_br_hash: d4405e637a83f254824170838c8292807a704edb143ff9912a9dbd033cd77d6c
muc_tieu: "Bộ máy công thức — mỗi mã field là một nút trong đồ thị phụ thuộc; gọi một lần cho lương thực nhận thì tự kéo theo cả chuỗi, và trả về vết truy ngược tới tận công thức, tham số và điều khoản BR"
scope_code: ["app/engine.py"]
scope_test: ["tests/test_f12.py"]
acceptance_test: "python3 -m tests.test_f12"
ui_role: none
ui_screen: 
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-f12-engine-dag.run.json
---
# frame-f12-engine-dag

## Nghiệp vụ

Đây là trái tim và cũng là lý do dự án tồn tại. Yêu cầu phi chức năng số 1 của khách hàng: *'mọi con số trên báo cáo phải truy vết được về công thức + số ngày + định mức + nguồn định mức'*. Và câu hỏi mà chính HR tự đặt ra trong file bàn giao mà chưa ai trả lời được: *'khi bảng lương ra số sai thì làm sao ai biết?'*

Cách làm: mỗi mã field (`BASIC_SAL`, `PAID_DAYS`, `GROSS`, `PIT`, `NET_PAY`…) là một nút, khai báo phụ thuộc của nó và hàm tính. `compute("NET_PAY_HOME")` resolve đệ quy — không ai phải nhớ thứ tự tính. Mỗi nút trả kèm: công thức nguyên văn, giá trị các biến vào, tham số đã dùng, và `clause_id` trong BR. Từ một con số sai, người ta đi ngược được tới đúng dòng Excel gốc.

## Input / Output

- **Input:** bản ghi nhân viên (các field `input`) + tham số kỳ
- **Output:** `CODES` (registry); `compute(mã, rec, params)` → `Decimal`; `bang_luong(rec, params)` → (kết quả, vết truy); `kiem_tra_dag()` → ném lỗi nếu có phụ thuộc vòng

## Tiêu chí nghiệm thu

- Gọi một lần `compute("NET_PAY_HOME")` → 189.930.161 (tự kéo cả chuỗi)
- Field vắng mặt trong input coi như 0 (đúng hành vi ô Excel trống)
- `bang_luong` trả kết quả + vết truy dài hơn 20 field
- Mỗi vết truy có: công thức, giá trị, phụ thuộc, và `clause_id` bắt đầu bằng C
- Đi ngược từ lương thực nhận xuống được tới lương cơ bản
- Đồ thị không có chu trình
- Registry phủ đủ 17 mã field kết quả của ground-truth
- **C8.8/FE-06**: `PC_TRUY_THU` là một node trong registry, deps khai đủ `RETRO_OLD_RATE/RETRO_NEW_RATE/RETRO_DAYS/STD_DAYS` (hiện trong cây trace); không có ca truy thu → ground-truth `NET_PAY_HOME` không đổi; có ca → chảy đúng vào `GROSS` qua `_GROSS_CODES`

## Ngoài phạm vi

Không tự tính lại logic nghiệp vụ (gọi các module domain đã có). Không render giao diện. Không đọc/ghi file.
