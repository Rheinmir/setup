---
schema_version: 0
frame_id: frame-m02-user-settings
created_by: human
kind: frame
parent_br: br/BR.md
clause_ids: [M2]
parent_br_hash: reverse-no-hash
muc_tieu: "Hồ sơ người dùng + cài đặt cá nhân + vai trò"
scope_code: ["store/user_setting.go","web/src/pages/Setting.tsx"]
scope_test: ["(reverse: test là suite memos gốc)"]
acceptance_test: "(reverse: mô tả code có sẵn — không test-first)"
ui_role: screen
ui_screen: settings
---
# frame-m02-user-settings

## Nghiệp vụ
Module memos: Hồ sơ người dùng + cài đặt cá nhân + vai trò. Reverse-engineer từ source usememos/memos — mô tả code CÓ SẴN, không phải to-build.

## Input / Output
- **Input:** request người dùng / API call tới service tương ứng.
- **Output:** kết quả nghiệp vụ + render trên UI memos.

## Tiêu chí nghiệm thu
- Hành vi khớp memos gốc (đã chạy standalone tại :5230).
- Không phá module khác (scope cô lập theo file).

## Ngoài phạm vi
- AI (M12) defer. Các module khác thuộc frame riêng.

## UI hoạt động ra sao
- Vai trò UI: screen. Màn: settings. Tương tác theo trang memos gốc.
