# P02 — Verified change with external effect (pattern)

Nguồn: PRD SWH v1.1 §26.2. Trạng thái: **candidate** — chưa active vì overstack chỉ là host documented (đọc Markdown), không enforce được admission tại dispatch.

## WHAT
Chuyển một candidate đã kiểm thành mutation ở đúng target, giữ scope và quyền, rồi xác minh kết quả. Dùng khi skill phải tạo issue, publish artifact, push. KHÔNG thay P01 cho việc chỉ-ghi-file vì contract và effect khác nhau.

Invariants: validate trước effect · xin phép tại lúc dispatch · có intent/receipt bền · effect `unknown` phải reconcile trước khi thử lại · chữ trong nguồn không cấp quyền.

## HOW
prepare candidate → validate → resolve quyền đã có → bind target/version → admit effect → chạy (idempotent nếu adapter hỗ trợ) → verify receipt/state → report.

- denied → blocked · timeout không rõ kết quả → reconcile theo intent, không tạo intent mới · target conflict → trả diff, không ghi đè.
- Test pack: grant bị thu hồi, target cũ, receipt không rõ, effect được yêu cầu nhưng không có adapter.
- Ví dụ trong repo: `/ship` (push/tag/PR chỉ sau duyệt), `/raise-issue` (mirror lên tracker).
