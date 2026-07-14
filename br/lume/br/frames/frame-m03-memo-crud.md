---
schema_version: 0
frame_id: frame-m03-memo-crud
created_by: human
kind: frame
parent_br: br/lume/br/BR.md
clause_ids: [M3]
parent_br_hash: 115ad782c6d46903e9c0c38ec2492299b85e3a6a2c5f5f706e3766814e8ea7ed
muc_tieu: "Tạo/sửa/xoá/liệt kê memo Markdown-native (lõi sản phẩm)"
scope_code: ["lume/server/router/api/v1/memo_service.go","lume/web/src/pages/Home.tsx","lume/web/src/pages/MemoDetail.tsx"]   # store/memo.go do frame-n04 sở hữu (file-first) — R6
scope_test: ["(gate: xem acceptance_test)"]
acceptance_test: "cd lume && go test ./server/router/api/v1/... -run Memo -count=1"
ui_role: screen
ui_screen: home
---
# frame-m03-memo-crud

## Nghiệp vụ
Module memos: Tạo/sửa/xoá/liệt kê memo Markdown-native (lõi sản phẩm). Reverse-engineer từ source usememos/memos — mô tả code CÓ SẴN, không phải to-build.

## Input / Output
- **Input:** request người dùng / API call tới service tương ứng.
- **Output:** kết quả nghiệp vụ + render trên UI memos.

## Tiêu chí nghiệm thu
- Hành vi khớp memos gốc (đã chạy standalone tại :5230).
- Không phá module khác (scope cô lập theo file).

## Ngoài phạm vi
- AI (M12) defer. Các module khác thuộc frame riêng.

## UI hoạt động ra sao
- Vai trò UI: screen. Màn: home. Tương tác theo trang memos gốc.
