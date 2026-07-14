---
schema_version: 0
frame_id: frame-m04-memo-organize
created_by: human
kind: frame
parent_br: br/lume/br/BR.md
clause_ids: [M4]
parent_br_hash: a55735359c5b5a75ec4feae592db42d489dfc649646bb247cd198e9d3f9a80dd
muc_tieu: "Tag/pin/archive/quan hệ memo"
scope_code: ["lume/store/memo_relation.go","lume/web/src/pages/Archived.tsx"]
scope_test: ["(gate: xem acceptance_test)"]
acceptance_test: 'cd lume && go test ./server/router/api/v1/... -run MemoFilter -count=1'
ui_role: panel
ui_screen: archived
---
# frame-m04-memo-organize

## Nghiệp vụ
Module memos: Tag/pin/archive/quan hệ memo. Reverse-engineer từ source usememos/memos — mô tả code CÓ SẴN, không phải to-build.

## Input / Output
- **Input:** request người dùng / API call tới service tương ứng.
- **Output:** kết quả nghiệp vụ + render trên UI memos.

## Tiêu chí nghiệm thu
- Hành vi khớp memos gốc (đã chạy standalone tại :5230).
- Không phá module khác (scope cô lập theo file).

## Ngoài phạm vi
- AI (M12) defer. Các module khác thuộc frame riêng.

## UI hoạt động ra sao
- Vai trò UI: panel. Màn: archived. Tương tác theo trang memos gốc.
