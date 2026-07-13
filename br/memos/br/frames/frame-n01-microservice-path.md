---
schema_version: 0
frame_id: frame-n01-microservice-path
created_by: human
kind: frame
parent_br: br/BR.md
clause_ids: [N01]
parent_br_hash: reverse-no-hash
muc_tieu: "Mount memos dưới /memos/ (Vite base + reverse-proxy) — giá trị đóng-gói của dây chuyền"
scope_code: ["web/vite.config.ts","scripts/proxy.conf"]
scope_test: ["(reverse: test là suite memos gốc)"]
acceptance_test: "(reverse: mô tả code có sẵn — không test-first)"
ui_role: none
ui_screen: 
---
# frame-n01-microservice-path

## Nghiệp vụ
Module memos: Mount memos dưới /memos/ (Vite base + reverse-proxy) — giá trị đóng-gói của dây chuyền. Reverse-engineer từ source usememos/memos — mô tả code CÓ SẴN, không phải to-build.

## Input / Output
- **Input:** request người dùng / API call tới service tương ứng.
- **Output:** kết quả nghiệp vụ + render trên UI memos.

## Tiêu chí nghiệm thu
- Hành vi khớp memos gốc (đã chạy standalone tại :5230).
- Không phá module khác (scope cô lập theo file).

## Ngoài phạm vi
- AI (M12) defer. Các module khác thuộc frame riêng.

## UI hoạt động ra sao
- Vai trò UI: action. Màn: —. Tương tác theo trang memos gốc.
