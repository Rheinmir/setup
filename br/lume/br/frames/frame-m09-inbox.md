---
schema_version: 0
frame_id: frame-m09-inbox
created_by: human
kind: frame
parent_br: br/lume/br/BR.md
clause_ids: [M9]
parent_br_hash: 1666843d0326e46cbb4d38a75756b0487bdb569a3054f00b7cb82ac6db025e63
muc_tieu: "Hộp thư hiển thị thông báo gửi tới người dùng (nhắc, phản hồi) và cho đánh dấu đã đọc/lưu trữ"
scope_code: ["lume/store/inbox.go","lume/web/src/pages/Inboxes.tsx"]
scope_test: ["(gate: xem acceptance_test)"]
acceptance_test: "node skills/visual-qa/assets/route-shots.mjs --base http://localhost:5230 --route /inbox --assert --user demo --pass demo --out br/lume/qa-m09"
depends_on: [frame-m01-auth]
ui_role: screen
ui_screen: inbox
---
# frame-m09-inbox

## Nghiệp vụ
Module memos: Hộp thư/thông báo. Reverse-engineer từ source usememos/memos — mô tả code CÓ SẴN, không phải to-build.

## Input / Output
- **Input:** request người dùng / API call tới service tương ứng.
- **Output:** kết quả nghiệp vụ + render trên UI memos.

## Tiêu chí nghiệm thu
- Hành vi khớp memos gốc (đã chạy standalone tại :5230).
- Không phá module khác (scope cô lập theo file).

## Ngoài phạm vi
- AI (M12) defer. Các module khác thuộc frame riêng.

## UI hoạt động ra sao
- Vai trò UI: screen. Màn: inbox. Tương tác theo trang memos gốc.
