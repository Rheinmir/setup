# BR — Memos (clone thành module qua dây chuyền /br)

> **Reverse-engineered** từ source `usememos/memos` (kéo về 12/07/2026). Đây là BR đi
> NGƯỢC: quan sát app có sẵn → clause. Provenance `code:<path>` = suy từ code thật;
> `nfr` = yêu cầu đóng-gói-module do dây chuyền thêm vào (không có trong memos gốc).
> Nguồn feature: proto/api/v1 (8 service) + store/ (13 entity) + web/src/pages (16 page).

## ⚠️ GIẢ ĐỊNH ĐANG GÁNH
| # | Clause | Giả định | verified |
|---|--------|----------|----------|
| A1 | N01 | Mount `/memos/` chỉ cần Vite `base` + proxy rewrite; memos không có native sub-path | false |
| A2 | M12 | AIService bỏ qua ở bản clone tối thiểu (cần API key ngoài) | false |
| A3 | N04 | ~~file-first là rewrite lớn → chỉ PoC export~~ **BÁC BỎ 14/07/26**: không cần rewrite Driver. Chèn tầng file-first vào 5 hàm memo của `store` (ghi⇒ra file, đọc⇒file thắng DB) → ĐÃ CHẠY THẬT, 7 bất biến xanh | **true (đã kiểm)** |

## Chức năng (clause quan sát từ code)
- **M1 — Auth** (`code:proto/.../auth_service.proto`, `store/user`): đăng nhập/đăng ký, session, admin sign-in. Trang SignIn/SignUp/AdminSignIn.
- **M2 — User & Settings** (`code:.../user_service`, `store/user_setting`): hồ sơ, cài đặt cá nhân, vai trò. Trang UserProfile/Setting.
- **M3 — Memo CRUD** (`code:.../memo_service`, `store/memo`): tạo/sửa/xoá/liệt kê memo, Markdown-native. Trang Home/MemoDetail.
- **M4 — Tổ chức memo** (`store/memo_relation`): tag, pin, archive, quan hệ memo. Trang Archived.
- **M5 — Chia sẻ memo** (`store/memo_share`): public share, visibility. Trang Explore.
- **M6 — Đính kèm/Resource** (`code:.../attachment_service`, `store/attachment`): upload file vào memo. Trang Attachments.
- **M7 — Reaction** (`store/reaction`): thả emoji lên memo.
- **M8 — Shortcut/Filter** (`code:.../shortcut_service`): lưu bộ lọc. Trang Shortcuts.
- **M9 — Inbox** (`store/inbox`): thông báo/hộp thư. Trang Inboxes.
- **M10 — SSO/IdP** (`code:.../identity_provider_service`, `store/idp`): đăng nhập ngoài. Trang AuthCallback.
- **M11 — Instance/Admin** (`code:.../instance_service`, `store/instance_setting`): cấu hình hệ thống.
- **M12 — AI** (`code:.../ai_service`): tính năng AI *(assumed A2 — defer)*.
- **M13 — Explore** (`web/src/pages/Explore.tsx`): feed công khai.

## NFR — giá trị dây chuyền thêm vào
- **N06 — Stream thư mục llmwiki vào app (local-first)** (`nfr`): Lume là **app local**, nhận một thư mục trên máy (mặc định `llmwiki/wiki/`) và **stream nguyên cấu trúc thư mục** đó lên app: mỗi `.md` = một memo, **đường dẫn thư mục = tag** (giữ nguyên cây `concepts/`, `entities/`, `sources/`, `draft/`…). File đổi trên đĩa (editor/git/agent) → app hiện **ngay**, không phải import lại. Chiều ngược (memo gõ trong Lume → ghi ra llmwiki) là **THỦ CÔNG** (người bấm), không tự đẩy — tránh app tự ý ghi vào kho tri thức.
- **N01 — Microservice-by-path** (`nfr`): memos phải chạy được (a) **standalone** 1 binary (đã có: `go run ./cmd/memos` serve SPA nhúng), và (b) **mount dưới `/memos/`** từ app khác qua Vite `base=/memos/` + reverse-proxy. *(assumed A1)*
- **N02 — Đóng gói 1 khối** (`code:cmd/memos`): `pnpm release` nhúng SPA vào `server/router/frontend/dist` → 1 Go binary serve cả API + UI.
- **N03 — Theme neumorphism (system theme dây chuyền)** (`nfr`): giao diện memos build LẠI theo design-system mặc định của dây chuyền = **Neumorphism** (`skills/br/assets/design-template.md` §3.6): mặt đơn sắc, cặp bóng sáng+tối, không viền, chữ đạt WCAG AA. Override token shadcn trong `web/src/themes/`, KHÔNG sửa component logic.
- **N05 — Rebrand "Lume" + UI cao cấp** (`nfr`): bỏ hoàn toàn tên "Memos" + logo con vẹt → thương hiệu **Lume** (logo neumorphic "nguồn sáng" SVG inline, favicon mới, title). Áp neumorphism ĐÚNG SPEC (superdesign 6-moves): dual-shadow thật `9px/18px` màu dẫn xuất `#bec3c9`/`#ffffff`, inset input/pressed, CTA phẳng accent `#4d6bfe`, focus-ring, text AA `#2d3436` — nhắm class thật (`.bg-card`, `[data-slot=button]`, `input`), không chỉ đổi nền.
- **N04 — Lưu trữ file-first** (`nfr`, thay M-storage): **ĐÃ LÀM (14/07/26)**. Nội dung memo là file `.md` trên đĩa (`<data>/memos-md/<uid>.md`, frontmatter + body) = **nguồn chân lý**; SQL còn lại làm **index** để lọc/tìm. Ghi ⇒ phải ra file; đọc ⇒ **file thắng DB** (sửa tay file bằng editor thì app hiện ngay). Không rewrite `store.Driver` — chèn tầng vào 5 hàm memo của `store`. Gate: `go test ./store/file/...` (7 bất biến).
