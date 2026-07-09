---
schema_version: 0
frame_id: frame-p12-suat-an
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.1.5, C5.3.1, C5.4]
parent_br_hash: 19d405e59625a1192e74e53a7e1bc00778cbf92f9fe223f000d8d40994ab610e
muc_tieu: "Tổng hợp suất ăn theo từng bộ phận: quy tắc bữa (VP 1 · CT<30km 2 · CT≥30km 3 · ≤4h 0), cộng cơm TC đêm + CN/lễ thư ký chấm + cơm bổ sung tháng trước — phải tái lập đúng Ví dụ 1 = 65 suất"
scope_code: ["app/p12_suatan.py"]
scope_test: ["tests/test_p12.py"]
acceptance_test: "python3 -m tests.test_p12"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p12-suat-an.run.json
---
# frame-p12-suat-an

## Nghiệp vụ
Suất ăn đếm theo NƠI làm việc từng ngày: số bữa/ngày phụ thuộc khối và khoảng cách của bộ phận hôm đó, ngày làm ≤4 tiếng bị loại. Thư ký công trường chấm bổ sung cơm Chủ nhật/ca đêm gửi về, hệ cộng vào bộ phận tương ứng. Ví dụ 1 PRD là acceptance chốt tại họp 23/03/2026: 5 ngày VP ×1 + 20 ngày dự án ≥30km ×3 = 65.

## Input / Output
- **Input:** Công thô phân loại + bộ phận/ngày (p10), dải khoảng cách bộ phận (p02), data-draft/suat_an_bo_sung.csv
- **Output:** Dict bo_phan → {suat_thuong, suat_tc_dem, suat_cn_le, tong}

## Tiêu chí nghiệm thu
- Tái lập Ví dụ 1: 5×1 + 20×3 = 65 suất
- Ngày 3.5 giờ (NV004 08/07) → 0 suất
- Cơm CN thư ký gửi cộng đúng vào bộ phận của ngày đó (NV008 Quan Lạn +6)
- Điều động: suất tách riêng theo từng bộ phận, không gộp

## Ngoài phạm vi
Không nhân tiền/tách thuế (p14). Điều kiện an ninh <30km bỏ qua v0 (assumed G9).
