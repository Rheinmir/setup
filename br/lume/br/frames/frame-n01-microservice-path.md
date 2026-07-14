---
schema_version: 0
frame_id: frame-n01-microservice-path
created_by: human
kind: frame
parent_br: br/lume/br/BR.md
clause_ids: [N01]
parent_br_hash: a55735359c5b5a75ec4feae592db42d489dfc649646bb247cd198e9d3f9a80dd
muc_tieu: "Mount memos dưới /memos/ (Vite base + reverse-proxy) — giá trị đóng-gói của dây chuyền"
scope_code: ["lume/web/vite.config.mts"]   # proxy.conf chưa tồn tại — không khai file ma
scope_test: ["(gate: xem acceptance_test)"]
acceptance_test: "bash br/lume/scripts/api-smoke.sh instance"
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
