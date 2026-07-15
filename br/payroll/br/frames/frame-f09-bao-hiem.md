---
schema_version: 0
frame_id: frame-f09-bao-hiem
created_by: slicer
parent_br: br/BR.md
clause_ids: [C4.2, C4.5, C11.1, C11.2, C11.3, C11.4]
parent_br_hash: 20c2df3e9bee61a36f153ad8b9e19a0fdadc5bb8d38b25bae7d90a089f9630b1
muc_tieu: "BHXH/BHYT/BHTN và kinh phí công đoàn — hai trần cùng tồn tại (hiển thị 50,6tr, tính thật 46,8tr), miễn đóng khi nghỉ từ 14 ngày, người nước ngoài không đóng thất nghiệp, phí công đoàn có trần 253 nghìn"
scope_code: ["app/baohiem.py"]
scope_test: ["tests/test_f09.py"]
acceptance_test: "python3 -m tests.test_f09"
ui_role: none
ui_screen: 
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-f09-bao-hiem.run.json
---
# frame-f09-bao-hiem

## Nghiệp vụ

Đây là frame nhiều cạm bẫy nhất, và mọi cạm bẫy đều lấy từ mâu thuẫn CÓ THẬT trong file bàn giao:

1. **Hai trần**: cột `INS_SAL_BH` hiển thị trần 50,6tr, nhưng bảy công thức tính bảo hiểm lại ăn trần 46,8tr. Chính Excel tự phát hiện: ô kiểm của nó ra 8.602.000 trong khi số thật là 7.956.000. Engine phải giữ CẢ HAI, không được quy về một.
2. **Bảo hiểm tai nạn lao động** dùng trần BHXH (46,8tr), KHÔNG dùng trần thất nghiệp (106,2tr) — bản 'định làm' sai chỗ này, ra 531.000 thay vì 234.000.
3. **Luật 14 ngày**: đếm theo THÁNG DƯƠNG LỊCH (mùng 1 → cuối tháng), lệch trục với kỳ lương (21→20). Nghỉ không lương + ốm + thử việc từ 14 ngày trở lên thì tháng đó không đóng đồng nào, cả phần nhân viên lẫn phần công ty.

## Input / Output

- **Input:** bản ghi (loại HĐ, quốc tịch, lương hợp đồng, các loại ngày nghỉ, các cột điều chỉnh) + tham số
- **Output:** `ins_sal_bh` (hiển thị), `ins_base_bh` (tính thật), `ins_sal_ui`; `si_emp/hi_emp/ui_emp/total_ins`; `si_cty/tnld_cty/hi_cty/ui_cty/total_ins_cty/kpcd_cty/union_fee`; `mien_dong_bhxh` → bool

## Tiêu chí nghiệm thu

- Hai trần: hiển thị 50.600.000, tính thật 46.800.000, thất nghiệp 106.200.000
- Ground-truth dòng 9 phần nhân viên: BHXH 3.744.000 · BHYT 702.000 · BHTN 1.062.000 · tổng 5.508.000
- Ground-truth dòng 9 phần công ty: 7.956.000 · 234.000 · 1.404.000 · 1.062.000 · tổng 10.656.000 · KPCĐ 936.000
- Tai nạn lao động dùng trần BHXH → 234.000 (không phải 531.000)
- Phí công đoàn 234.000, và lương rất cao vẫn không vượt trần 253.000
- Thử việc → không đóng gì
- Người nước ngoài → BHTN = 0 nhưng BHXH vẫn đóng
- Nghỉ không lương 14 ngày → miễn đóng, cả nhân viên lẫn công ty = 0; 13 ngày → vẫn đóng đủ

## Ngoài phạm vi

Không xử lý truy thu/thoái thu BHXH theo lô và lãi nộp chậm (lô sau). Không tự cập nhật trần theo công báo Nhà nước.
