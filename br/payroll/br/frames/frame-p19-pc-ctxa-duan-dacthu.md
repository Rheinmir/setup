---
schema_version: 0
frame_id: frame-p19-pc-ctxa-duan-dacthu
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.3.6, C5.3.7]
parent_br_hash: 06f8501d7472387c48709eed1947a0118c170e31ddc23c5b4e4282caca8bb9de
muc_tieu: "PC công trường xa/khó khăn theo dự án đặc thù × chức danh (Quan Lạn, Chingluh) + PC khó khăn Làng Tây – Hòn Thơm theo tờ trình dự án; cộng PC khác (7) từ danh sách duyệt riêng"
scope_code: ["app/p19_pcctxa.py"]
scope_test: ["tests/test_p19.py"]
acceptance_test: "python3 -m tests.test_p19"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p19-pc-ctxa-duan-dacthu.run.json
---
# frame-p19-pc-ctxa-duan-dacthu

## Nghiệp vụ
Khác các PC trên, khoản này chỉ áp cho DANH SÁCH dự án đặc thù, mức theo chức danh tại dự án. Làng Tây – Hòn Thơm là biến thể theo tờ trình gắn dự án với ngày hiệu lực. Cột (7) 'khác' lấy thẳng từ danh sách theo dõi duyệt riêng. Frame này đóng nốt 3 cột cuối (6)(7) của bảng phụ cấp.

## Input / Output
- **Input:** Bộ phận/dự án theo đoạn (p10), chức danh, dinh_muc_ct_xa_du_an.csv, p04 (tờ trình), p13
- **Output:** Tiền PC (6) và (7) theo bộ phận + tổng + trace

## Tiêu chí nghiệm thu
- NV008 Thủ kho Quan Lạn đủ công → (6) 2.000.000 pro-rata + (7) 1.500.000 từ TT-2026/029
- NV012 gói 2B-6BL Làng Tây → (6) 2.000.000 hiệu lực từ 01/06 nguồn TT-2026/044
- NV tại CT thường (Long An) → (6)=(7)=0
- Chingluh GS → 1.000.000 kèm cờ assumed G2 trong trace

## Ngoài phạm vi
Không tự thêm dự án vào danh sách đặc thù (quản trị làm).
