---
schema_version: 0
frame_id: frame-m05-share-explore
created_by: human
kind: frame
parent_br: br/BR.md
clause_ids: [M5]
parent_br_hash: reverse-no-hash
muc_tieu: "Chia sẻ public + feed Explore"
scope_code: ["store/memo_share.go","web/src/pages/Explore.tsx"]
scope_test: ["(reverse: test là suite memos gốc)"]
acceptance_test: "(reverse: mô tả code có sẵn — không test-first)"
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
