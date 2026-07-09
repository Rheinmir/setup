---
schema_version: 0
frame_id: frame-p01-lich-ky-cong
created_by: slicer
parent_br: br/BR.md
clause_ids: [C4.1]
parent_br_hash: 19d405e59625a1192e74e53a7e1bc00778cbf92f9fe223f000d8d40994ab610e
muc_tieu: "Sinh lịch kỳ công 21–20 và kỳ BHXH 01–cuối tháng chạy song song, tính ngày công chuẩn VP (trừ CN + chiều T7) và CT (trừ CN) cho từng kỳ"
scope_code: ["app/p01_lichky.py"]
scope_test: ["tests/test_p01.py"]
acceptance_test: "python3 -m tests.test_p01"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p01-lich-ky-cong.run.json
---
# frame-p01-lich-ky-cong

## Nghiệp vụ
Mọi phép tính lương/phụ cấp đều chia cho 'ngày công chuẩn' và đều phải biết một ngày bất kỳ thuộc kỳ công nào, đồng thời thuộc tháng BHXH nào. Kỳ công chạy 21 tháng trước → 20 tháng này trong khi BHXH tính theo tháng dương lịch, nên một ngày luôn nằm trên HAI trục. Frame này là nền móng: cho một tháng kỳ, trả về danh sách ngày, loại ngày (thường/T7/CN), công chuẩn VP và CT — sai ở đây thì mọi frame sau sai dây chuyền.

## Input / Output
- **Input:** Tháng kỳ (vd '2026-07'), danh mục lễ từ data-draft/ngay_le.csv
- **Output:** Dict: khoảng kỳ (2026-06-21→2026-07-20), list ngày kèm loại, cong_chuan_vp, cong_chuan_ct, map ngày→tháng BHXH

## Tiêu chí nghiệm thu
- Kỳ 07/2026 = 21/06→20/07 đúng như ví dụ PRD C4.1
- Công chuẩn VP loại CN và tính chiều T7 = 0.5 công; CT chỉ loại CN
- Ngày 25/06 thuộc kỳ công 07/2026 nhưng tháng BHXH 06/2026
- Ngày lễ trong danh mục được gắn cờ le=True

## Ngoài phạm vi
Không đếm công của nhân viên (frame p08+). Không xử lý lễ 300% (p21).
