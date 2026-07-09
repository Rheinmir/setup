---
schema_version: 0
frame_id: frame-p22-khoa-ky
created_by: slicer
parent_br: br/BR.md
clause_ids: [C4.3]
parent_br_hash: 06f8501d7472387c48709eed1947a0118c170e31ddc23c5b4e4282caca8bb9de
muc_tieu: "Khóa kỳ manual lock (tier: compensable): HR khóa → ngừng sync API tháng đó, chặn mọi biến động; đơn muộn/sửa công sau chốt không cập nhật và KHÔNG truy thu tháng sau"
scope_code: ["app/p22_khoaky.py"]
scope_test: ["tests/test_p22.py"]
acceptance_test: "python3 -m tests.test_p22"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
tier: compensable
run_log_ref: br/frames/frame-p22-khoa-ky.run.json
---
# frame-p22-khoa-ky

## Nghiệp vụ
Khóa kỳ là hành động một chiều về nghiệp vụ: sau khóa mọi cửa ghi của kỳ đó đóng vĩnh viễn (adapter ngừng sync, truy thu bị cấm, override bị cấm). Vì là effect khó đảo (mở khóa lại đòi quy trình riêng), frame khai tier compensable — br-run sẽ tier-gate hỏi người trước khi chạy. Trạng thái khóa là cờ mọi frame ghi-dữ-liệu phải hỏi trước khi ghi.

## Input / Output
- **Input:** Lệnh khóa {ky, nguoi, ly_do}, sổ trạng thái kỳ
- **Output:** Sổ kỳ {ky → DANG_MO|DA_KHOA, nguoi, luc, ly_do}; API is_locked(ky) cho frame khác

## Tiêu chí nghiệm thu
- Khóa 07/2026 → is_locked trả True, ghi người + thời điểm + lý do
- Sau khóa: p06 sync từ chối kỳ đó; p20 truy thu từ chối; p24 override từ chối
- Khóa lại kỳ đã khóa → idempotent, không ghi đè audit cũ
- Khóa mà thiếu lý do → từ chối (audit bắt buộc C6.2)

## Ngoài phạm vi
Không có nút mở khóa (ngoài phạm vi PRD). UI xác nhận 2 bước ở p28.
