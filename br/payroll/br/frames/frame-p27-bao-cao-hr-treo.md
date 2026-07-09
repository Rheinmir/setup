---
schema_version: 0
frame_id: frame-p27-bao-cao-hr-treo
created_by: slicer
parent_br: br/BR.md
clause_ids: [C6.4, C6.5]
parent_br_hash: 19d405e59625a1192e74e53a7e1bc00778cbf92f9fe223f000d8d40994ab610e
muc_tieu: "Bộ báo cáo bảo mật HR C&B (ma trận công 21–20, bảng cơm P1/P2, tổng hợp PC (1)–(8) + cột (2)(3), danh sách duyệt riêng so kỳ) + báo cáo đơn treo lãnh đạo tại cut-off; MỌI lượt xuất ghi log"
scope_code: ["app/p27_baocao_hr.py"]
scope_test: ["tests/test_p27.py"]
acceptance_test: "python3 -m tests.test_p27"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p27-bao-cao-hr-treo.run.json
---
# frame-p27-bao-cao-hr-treo

## Nghiệp vụ
File 02__HR C&B hằng tháng là hợp đồng đầu ra quan trọng nhất với HR — 4 sheet phải đúng cấu trúc để họ bỏ Excel thủ công. Kèm báo cáo đơn treo: danh sách quản lý chậm + số đơn + treo bao lâu, gửi lãnh đạo ngày cut-off (mock notify ghi file thay Teams/Email thật). Vì dữ liệu nhạy cảm, mọi lời gọi xuất phải khai user và bị ghi log — không có đường xuất nặc danh.

## Input / Output
- **Input:** Kết quả mọi engine, audit/notify sink, user gọi xuất
- **Output:** 4 cấu trúc sheet + báo cáo treo; log xuất {user, lúc, báo cáo}

## Tiêu chí nghiệm thu
- Bảng tổng hợp PC có đủ cột (1)→(8) + PC bộ phận trước (2) + truy lĩnh (3)
- Bảng cơm tách P1/P2/TC đêm/CN đúng số p12
- Xuất không truyền user → từ chối; xuất hợp lệ → log ghi 1 dòng
- Đơn treo: NV012 ?P xuất hiện, đếm số ngày treo đúng

## Ngoài phạm vi
Không gửi Teams/Email thật. Không phân quyền SSO thật (p28 mock role).
