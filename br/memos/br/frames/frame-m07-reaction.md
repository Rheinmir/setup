---
schema_version: 0
frame_id: frame-m07-reaction
created_by: human
kind: frame
parent_br: br/BR.md
clause_ids: [M7]
parent_br_hash: reverse-no-hash
muc_tieu: "Thả emoji reaction lên memo"
scope_code: ["store/reaction.go"]
scope_test: ["(reverse: test là suite memos gốc)"]
acceptance_test: "(reverse: mô tả code có sẵn — không test-first)"
ui_role: widget
ui_screen: home
---
# frame-m07-reaction

## Nghiệp vụ
Module memos: Thả emoji reaction lên memo. Reverse-engineer từ source usememos/memos — mô tả code CÓ SẴN, không phải to-build.

## Input / Output
- **Input:** request người dùng / API call tới service tương ứng.
- **Output:** kết quả nghiệp vụ + render trên UI memos.

## Tiêu chí nghiệm thu
- Hành vi khớp memos gốc (đã chạy standalone tại :5230).
- Không phá module khác (scope cô lập theo file).

## Ngoài phạm vi
- AI (M12) defer. Các module khác thuộc frame riêng.

## UI hoạt động ra sao
- Vai trò UI: widget. Màn: home. Tương tác theo trang memos gốc.
