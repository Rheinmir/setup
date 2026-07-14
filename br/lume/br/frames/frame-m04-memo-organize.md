---
schema_version: 0
frame_id: frame-m04-memo-organize
created_by: human
kind: frame
parent_br: br/lume/br/BR.md
clause_ids: [M4]
parent_br_hash: 5c7f64350a7d0bffced5cd1b77902cf85f5f7592c03b348423f41985a4d20a79
muc_tieu: "Tag/pin/archive/quan hệ memo"
scope_code: ["lume/store/memo_relation.go","lume/web/src/pages/Archived.tsx"]
scope_test: ["(gate: xem acceptance_test)"]
acceptance_test: 'cd lume && go test ./server/router/api/v1/... -run MemoFilter -count=1'
depends_on: [frame-m03-memo-crud]
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
