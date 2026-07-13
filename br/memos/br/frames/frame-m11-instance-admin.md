---
schema_version: 0
frame_id: frame-m11-instance-admin
created_by: human
kind: frame
parent_br: br/BR.md
clause_ids: [M11]
parent_br_hash: reverse-no-hash
muc_tieu: "Cấu hình instance/admin"
scope_code: ["store/instance_setting.go"]
scope_test: ["(reverse: test là suite memos gốc)"]
acceptance_test: "(reverse: mô tả code có sẵn — không test-first)"
ui_role: panel
ui_screen: settings
---
# frame-m11-instance-admin

## Nghiệp vụ
Module memos: Cấu hình instance/admin. Reverse-engineer từ source usememos/memos — mô tả code CÓ SẴN, không phải to-build.

## Input / Output
- **Input:** request người dùng / API call tới service tương ứng.
- **Output:** kết quả nghiệp vụ + render trên UI memos.

## Tiêu chí nghiệm thu
- Hành vi khớp memos gốc (đã chạy standalone tại :5230).
- Không phá module khác (scope cô lập theo file).

## Ngoài phạm vi
- AI (M12) defer. Các module khác thuộc frame riêng.

## UI hoạt động ra sao
- Vai trò UI: panel. Màn: settings. Tương tác theo trang memos gốc.
