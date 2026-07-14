---
schema_version: 0
frame_id: frame-m05-share-explore
created_by: human
kind: frame
parent_br: br/lume/br/BR.md
clause_ids: [M5]
parent_br_hash: 5c7f64350a7d0bffced5cd1b77902cf85f5f7592c03b348423f41985a4d20a79
muc_tieu: "Chia sẻ public + feed Explore"
scope_code: ["lume/store/memo_share.go","lume/web/src/pages/Explore.tsx"]
scope_test: ["(gate: xem acceptance_test)"]
acceptance_test: "node skills/visual-qa/assets/route-shots.mjs --base http://localhost:5230 --route /explore --assert --user demo --pass demo --out br/lume/qa-m05"
depends_on: [frame-m03-memo-crud]
ui_role: screen
ui_screen: explore
---
# frame-m05-share-explore

## Nghiệp vụ
Module memos: Chia sẻ public + feed Explore. Reverse-engineer từ source usememos/memos — mô tả code CÓ SẴN, không phải to-build.

## Input / Output
- **Input:** request người dùng / API call tới service tương ứng.
- **Output:** kết quả nghiệp vụ + render trên UI memos.

## Tiêu chí nghiệm thu
- Hành vi khớp memos gốc (đã chạy standalone tại :5230).
- Không phá module khác (scope cô lập theo file).

## Ngoài phạm vi
- AI (M12) defer. Các module khác thuộc frame riêng.

## UI hoạt động ra sao
- Vai trò UI: screen. Màn: explore. Tương tác theo trang memos gốc.
