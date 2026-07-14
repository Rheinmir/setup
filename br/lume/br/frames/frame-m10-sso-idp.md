---
schema_version: 0
frame_id: frame-m10-sso-idp
created_by: human
kind: frame
parent_br: br/lume/br/BR.md
clause_ids: [M10]
parent_br_hash: 5c7f64350a7d0bffced5cd1b77902cf85f5f7592c03b348423f41985a4d20a79
muc_tieu: "Đăng nhập ngoài (SSO/IdP) + callback"
scope_code: ["lume/store/idp.go","lume/web/src/pages/AuthCallback.tsx"]
scope_test: ["(gate: xem acceptance_test)"]
acceptance_test: "bash br/lume/scripts/api-smoke.sh idp"
depends_on: [frame-m01-auth]
ui_role: form
ui_screen: auth
---
# frame-m10-sso-idp

## Nghiệp vụ
Module memos: Đăng nhập ngoài (SSO/IdP) + callback. Reverse-engineer từ source usememos/memos — mô tả code CÓ SẴN, không phải to-build.

## Input / Output
- **Input:** request người dùng / API call tới service tương ứng.
- **Output:** kết quả nghiệp vụ + render trên UI memos.

## Tiêu chí nghiệm thu
- Hành vi khớp memos gốc (đã chạy standalone tại :5230).
- Không phá module khác (scope cô lập theo file).

## Ngoài phạm vi
- AI (M12) defer. Các module khác thuộc frame riêng.

## UI hoạt động ra sao
- Vai trò UI: form. Màn: auth. Tương tác theo trang memos gốc.
