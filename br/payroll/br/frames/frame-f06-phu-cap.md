---
schema_version: 0
frame_id: frame-f06-phu-cap
created_by: slicer
parent_br: br/BR.md
clause_ids: [C8.3, C8.4, C8.5, C8.6, C8.7, C8.8, C17.4]
parent_br_hash: 8ce24f08a35438423ae90ef63b0fa7fdb648327f745a94d791f713c44984b856
muc_tieu: "Phụ cấp cố định theo tháng — pro-rata theo ngày công, quy tắc dưới 14 ngày chỉ tính ngày làm việc thực tế cộng ngày lễ, chia theo từng bộ phận khi điều động, tờ trình duyệt riêng ghi đè định mức chung, cộng phụ cấp truy thu/truy lĩnh hồi tố (FE-06) khi định mức thay đổi có hiệu lực ngược"
scope_code: ["app/phucap.py"]
scope_test: ["tests/test_f06.py"]
acceptance_test: "python3 -m tests.test_f06"
ui_role: none
ui_screen: 
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-f06-phu-cap.run.json
---
# frame-f06-phu-cap

## Nghiệp vụ

Đây là 'linh hồn' của PRD và là lý do khách hàng muốn bỏ Excel. Ba luật chồng lên nhau: (1) pro-rata thường — định mức chia công chuẩn nhân ngày hưởng; (2) **luật dưới 14 ngày** — nếu cả kỳ đi làm thực tế chưa tới 14 ngày thì chỉ được tính (ngày làm việc + ngày lễ), phép và nghỉ không lương bị loại; (3) **điều động** — mỗi bộ phận có định mức riêng, phải chia ngày thực tế ở từng nơi rồi áp định mức của nơi đó.

Cạm bẫy: luật <14 ngày xét trên TỔNG ngày làm việc cả kỳ, không xét riêng từng bộ phận. Người làm 3 ngày ở A và 3 ngày ở B là 6 ngày (<14), cả hai bộ phận đều bị áp luật — chứ không phải xét 3<14 rồi 3<14 riêng lẻ.

Frame này hiện thực AC-2 — ví dụ thứ hai chốt tại họp 23/03/2026.

## Input / Output

- **Input:** các đoạn công tác (mỗi đoạn: ngày làm việc, ngày lễ, ngày phép, ngày không lương, định mức), công chuẩn, tờ trình (nếu có)
- **Output:** `ngay_huong`, `prorata`, `phu_cap_dieu_dong` → `Decimal`; `dinh_muc(loại, level, khối, tờ_trình)` → `Decimal`

## Tiêu chí nghiệm thu

- Pro-rata thường: định mức 1tr, hưởng 11/22 công → 500.000
- Đủ 14 ngày làm việc → ngày hưởng tính CẢ phép (14+2+4 = 20)
- Dưới 14 ngày → chỉ (làm việc + lễ), bỏ phép: 3 làm việc + 1 lễ + 6 phép → 4
- **AC-2**: bộ phận A (3 làm việc + 1 lễ) và B (3 làm việc + 2 lễ), tổng 6 < 14 → PC = (3+1)/CC × ĐM_A + (3+2)/CC × ĐM_B
- Luật <14 xét trên TỔNG cả kỳ, không xét riêng từng bộ phận
- Tờ trình ghi đè định mức chung
- Khối văn phòng KHÔNG có định mức chung phụ cấp xăng (= 0, chỉ theo tờ trình); công trường thì có 1tr
- **C8.8/FE-06**: không có ca truy thu (không khai `RETRO_OLD_RATE`/`RETRO_NEW_RATE`) → `truy_thu()` trả `0`; có ca → `(mới−cũ)/công_chuẩn×số_ngày` (vd 500k→1tr, 11/22 ngày → 250.000); thiếu `RETRO_REASON` hoặc `RETRO_DAYS` khi có ca → `ValueError` (bắt buộc, không âm thầm bỏ qua)

## Ngoài phạm vi

Không tính tiền cơm (frame f05 — cơm tính theo SUẤT, không theo định mức tháng). Không quản lý màn hình nhập tờ trình (UI, lô sau). Không truy thu/truy lĩnh hồi tố.
