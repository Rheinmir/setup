---
schema_version: 0
frame_id: frame-m06-attachment
created_by: human
kind: frame
parent_br: br/lume/br/BR.md
clause_ids: [M6]
parent_br_hash: 5c7f64350a7d0bffced5cd1b77902cf85f5f7592c03b348423f41985a4d20a79
muc_tieu: "Upload file đính kèm vào memo"
scope_code: ["lume/store/attachment.go","lume/web/src/pages/Attachments.tsx"]
scope_test: ["(gate: xem acceptance_test)"]
acceptance_test: "cd lume && go test ./server/router/api/v1/... -run Attachment -count=1"
depends_on: [frame-m03-memo-crud]
ui_role: screen
ui_screen: attachments
---
# frame-m06-attachment

## Nghiệp vụ
Module memos: Upload file đính kèm vào memo. Reverse-engineer từ source usememos/memos — mô tả code CÓ SẴN, không phải to-build.

## Input / Output
- **Input:** request người dùng / API call tới service tương ứng.
- **Output:** kết quả nghiệp vụ + render trên UI memos.

## Tiêu chí nghiệm thu
- Hành vi khớp memos gốc (đã chạy standalone tại :5230).
- Không phá module khác (scope cô lập theo file).

## Ngoài phạm vi
- AI (M12) defer. Các module khác thuộc frame riêng.

## UI hoạt động ra sao
- Vai trò UI: screen. Màn: attachments. Tương tác theo trang memos gốc.
