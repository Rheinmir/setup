---
schema_version: 0
frame_id: frame-m08-shortcut
created_by: human
kind: frame
parent_br: br/lume/br/BR.md
clause_ids: [M8]
parent_br_hash: 115ad782c6d46903e9c0c38ec2492299b85e3a6a2c5f5f706e3766814e8ea7ed
muc_tieu: "Người dùng lưu bộ lọc hay dùng thành shortcut để mở lại nhanh, không phải gõ lại điều kiện"
scope_code: ["lume/store/shortcut.go","lume/web/src/pages/Shortcuts.tsx"]
scope_test: ["(gate: xem acceptance_test)"]
acceptance_test: "bash br/lume/scripts/api-smoke.sh shortcut"
ui_role: screen
ui_screen: shortcuts
---
# frame-m08-shortcut

## Nghiệp vụ
Module memos: Lưu bộ lọc/shortcut. Reverse-engineer từ source usememos/memos — mô tả code CÓ SẴN, không phải to-build.

## Input / Output
- **Input:** request người dùng / API call tới service tương ứng.
- **Output:** kết quả nghiệp vụ + render trên UI memos.

## Tiêu chí nghiệm thu
- Hành vi khớp memos gốc (đã chạy standalone tại :5230).
- Không phá module khác (scope cô lập theo file).

## Ngoài phạm vi
- AI (M12) defer. Các module khác thuộc frame riêng.

## UI hoạt động ra sao
- Vai trò UI: screen. Màn: shortcuts. Tương tác theo trang memos gốc.
