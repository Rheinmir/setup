---
schema_version: 0
frame_id: frame-p15-pc-dien-thoai
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.3.2]
parent_br_hash: bd8b0c1092b3518507e218bdafbdb5dc39535405ea63f7a591e410a3c114e81d
muc_tieu: "PC điện thoại: tra bảng ngạch × VP/CT (kể cả thử việc VP=0, CT=300k), áp engine pro-rata + <14 ngày + chia bộ phận theo định mức từng nơi"
scope_code: ["app/p15_pcdienthoai.py"]
scope_test: ["tests/test_p15.py"]
acceptance_test: "python3 -m tests.test_p15"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p15-pc-dien-thoai.run.json
---
# frame-p15-pc-dien-thoai

## Nghiệp vụ
Điện thoại là PC 'mẫu chuẩn' của pattern: định mức 2 chiều ngạch×khối, NV điều động giữa VP và CT hưởng mức khác nhau ở mỗi đoạn. Người thử việc đặc biệt: VP không có, CT có 300k. Frame này chỉ là lớp mỏng: chọn định mức đúng theo bộ phận từng đoạn rồi ném vào p13.

## Input / Output
- **Input:** Hồ sơ NV (ngạch, trạng thái TV theo đoạn từ p08), khối của bộ phận (p02), engine p13
- **Output:** Tiền PC điện thoại theo bộ phận + tổng + trace

## Tiêu chí nghiệm thu
- QL.02 cả kỳ ở CT đủ công → 1.000.000
- NV001 điều động VP(800k)→CT Quan Lạn(1.000k): mỗi đoạn định mức riêng qua p13
- NV004 thử việc tại CT → dùng mức TV-CT 300k đến 09/07, NV.01-CT 400k từ 10/07

## Ngoài phạm vi
Không lặp lại logic <14 ngày (đã ở p13).
