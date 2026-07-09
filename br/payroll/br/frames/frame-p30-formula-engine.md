---
schema_version: 0
frame_id: frame-p30-formula-engine
created_by: slicer
parent_br: br/BR.md
clause_ids: [C9.1, C9.2]
parent_br_hash: bd8b0c1092b3518507e218bdafbdb5dc39535405ea63f7a591e410a3c114e81d
muc_tieu: "Engine công thức lương THẬT trích từ Excel bàn giao — dependency graph 40 field từ ngày công tới NET_PAY_HOME, chạy 1 lần compute() ra cả chuỗi kèm trace, thuế TNCN 7 bậc lũy tiến đúng NĐ 65/2013"
scope_code: ["app/p30_formula_engine.py"]
scope_test: ["tests/test_p30.py"]
acceptance_test: "python3 -m tests.test_p30"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p30-formula-engine.run.json
---
# frame-p30-formula-engine

## Nghiệp vụ
Dây chuyền cũ (p01-p29) tự suy công thức từ PRD văn bản — đúng tinh thần nhưng KHÔNG có công thức ra "lương thực nhận" cuối cùng (p26 dừng ở liệt kê thành phần, không cộng trừ BHXH/thuế/OT thành 1 số). User cung cấp file Excel bàn giao Payroll thật (sheet "Payroll structure") có đúng 40 field + công thức Excel gốc từ HR/Payroll team — đây là nguồn CHÍNH XÁC HƠN, thay thế phần tính tổng cuối.

Thiết kế: mỗi field là node trong dependency graph (`[CODE]` tham chiếu field khác). `compute(code, inputs)` resolve đệ quy — gọi 1 lần cho field cuối (`NET_PAY_HOME`) tự kéo theo toàn bộ chuỗi phụ thuộc, không cần biết thứ tự tính tay. Đây là điều BRD đòi "chạy 1 lần là xong 1 formula".

## Input / Output
- **Input:** `inputs` (dict CODE→số) — mọi field `type=input` trong Excel (BASIC_SAL, ACTUAL_DAYS, MEALS_TOTAL, DEPENDENT_CNT...); field không có trong dict coi như 0 (đúng hành vi ô Excel trống)
- **Output:** `compute(code, inputs)` → số; `bang_luong_day_du(inputs)` → `(ket_qua: {NET_PAY_HOME, TOTAL_CTY_COST}, trace: {code: (tên, công_thức, giá_trị)})` cho MỌI field đã tính qua

## Tiêu chí nghiệm thu
- Thuế TNCN 7 bậc: thu nhập 5tr → 5% không trừ; 8tr → bậc 10% trừ 250k; 100tr → bậc 35% trừ 9.85tr; thu nhập ≤0 → thuế 0
- BASIC_SAL 60tr nhưng SI_EMP tính trên TRẦN 46.8tr (không phải trên 60tr)
- Chuỗi GROSS→NET_PAY_HOME chạy 1 lần cho lương 20tr đủ ngày công ra NET_PAY_HOME hợp lý (nhỏ hơn GROSS, lớn hơn GROSS trừ mọi khoản trừ hợp lý)
- `bang_luong_day_du` trả trace đủ dài (>15 field), có mặt GROSS và PIT

## Ngoài phạm vi
Chưa tự tra bảng phụ cấp theo Level 1-8 (C9.3, PC vẫn là input thô). Chưa nối vào p26/UI (bước tiếp theo, giống cách p29 nối sau khi frame xanh).
