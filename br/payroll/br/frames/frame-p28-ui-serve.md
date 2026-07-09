---
schema_version: 0
frame_id: frame-p28-ui-serve
created_by: slicer
parent_br: br/BR.md
clause_ids: [C3, C8]
parent_br_hash: bd8b0c1092b3518507e218bdafbdb5dc39535405ea63f7a591e410a3c114e81d
muc_tieu: "Web UI stdlib theo mockup.html: 10 màn hình (dashboard, bảng công, suất ăn, phụ cấp, OT, master data, tờ trình, khóa kỳ 2 bước, báo cáo, đơn treo), role-based ẩn TIỀN với thư ký/CHT, dark/light toggle"
scope_code: ["app/p28_ui.py", "serve.py", "app/__init__.py"]
scope_test: ["tests/test_p28.py"]
acceptance_test: "python3 -m tests.test_p28"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p28-ui-serve.run.json
---
# frame-p28-ui-serve

## Nghiệp vụ
Màn cuối wire mọi engine vào giao diện đúng như mockup đã duyệt. Ràng buộc bảo mật C3 thể hiện ở UI: đăng nhập vai thư ký/CHT thì mọi cột tiền biến mất khỏi mọi màn (không phải giấu bằng CSS mà không render). Nút khóa kỳ đòi xác nhận 2 bước + lý do rồi mới gọi p22. Mọi ô phụ cấp click ra popover trace (công thức + ngày + định mức + nguồn) — hiện thực yêu cầu Kiểm chứng được C8.

## Input / Output
- **Input:** Mọi module p01–p27, mockup.html làm spec giao diện
- **Output:** serve.py chạy http://localhost:8791, render server-side, không CDN

## Tiêu chí nghiệm thu
- GET / trả 200, đủ 10 mục sidebar như mockup
- Login vai 'thuky' → trang phụ cấp không chứa bất kỳ chuỗi số tiền nào
- Nút khóa kỳ: bước 1 confirm → bước 2 nhập lý do → mới đổi trạng thái
- Ô PC điện thoại NV001 có data-trace chứa 'định mức' và 'nguồn'
- Toggle dark/light + localStorage hoạt động (test HTML chứa data-theme hook)

## Ngoài phạm vi
Không Azure AD SSO thật (mock 3 role). Không realtime websocket.
