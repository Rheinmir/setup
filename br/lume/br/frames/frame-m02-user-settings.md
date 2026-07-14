---
schema_version: 0
frame_id: frame-m02-user-settings
created_by: human
kind: frame
parent_br: br/lume/br/BR.md
clause_ids: [M2]
parent_br_hash: a55735359c5b5a75ec4feae592db42d489dfc649646bb247cd198e9d3f9a80dd
muc_tieu: "Hồ sơ người dùng + cài đặt cá nhân + vai trò"
scope_code: ["lume/store/user_setting.go","lume/web/src/pages/Setting.tsx"]
scope_test: ["(gate: xem acceptance_test)"]
acceptance_test: "cd lume && go test ./server/router/api/v1/... -run User -count=1"
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
