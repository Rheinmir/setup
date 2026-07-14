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
- **N07 — Nút SYNC: đẩy NGUYÊN CỤM folder lên remote** (`nfr`): người dùng bấm **Sync** trên một folder đã thêm → **toàn bộ memo của cụm folder đó** được đẩy lên một instance Lume ở xa. Thủ công (người bấm mới đẩy), idempotent (bấm 2 lần không đẻ bản trùng), có thể chọn đẩy từng folder riêng.
- **N06 — Thêm folder vào app bằng NÚT, xem được nhiều folder cùng lúc** (`nfr`): Lume là app local. Người dùng **bấm nút trong app** → **chọn một thư mục trên máy** (llmwiki hoặc BẤT KỲ folder .md nào) → folder đó **thêm vào DANH SÁCH view** của app (mỗi .md = 1 memo, đường dẫn thư mục = tag). **Chọn được NHIỀU LẦN, mỗi lần cộng thêm 1 folder** (không thay thế). Danh sách folder **lưu lại** (khởi động lại vẫn còn). File đổi trên đĩa → app hiện ngay. App **KHÔNG ghi** vào folder của người dùng (read-only).
- **N07 — Nhiều wiki, mỗi wiki một tab, đặt tên được** (`nfr`, mở rộng N06): N06 stream ĐÚNG MỘT thư mục, gắn bằng cờ `--mount` lúc khởi động. N07: người dùng **trỏ Lume vào một folder `llmwiki` bất kỳ trên máy ngay trong app** (không phải sửa cờ rồi khởi động lại), **đặt tên cho nó**, và **mỗi wiki là một tab** để chuyển qua lại. Tên mặc định gợi ý = tên folder **BỌC NGOÀI** `llmwiki` (vd `…/issue-15-br-k/llmwiki` → `issue-15-br-k`). Vẫn READ-ONLY tuyệt đối (N06). **Ràng buộc hình dạng**: trình duyệt KHÔNG trả đường dẫn tuyệt đối (`showDirectoryPicker()` trả handle, không trả path) ⇒ việc chọn folder phải do **BE mở hộp thoại native của HĐH**, không phải web picker; dán path là đường lùi khi native lỗi. **Ràng buộc dữ liệu (bẫy đã biết)**: `Mount.Name` hiện là prefix của UID (`mount.go:UIDFor`) ⇒ tên hiển thị **KHÔNG được** dùng làm khoá — phải tách `id` bất biến (khoá, prefix UID) khỏi `label` (tên tab, đổi tự do), nếu không mỗi lần đổi tên sẽ re-key toàn bộ memo và bỏ lại memo mồ côi.
- **N01 — Microservice-by-path** (`nfr`): memos phải chạy được (a) **standalone** 1 binary (đã có: `go run ./cmd/memos` serve SPA nhúng), và (b) **mount dưới `/memos/`** từ app khác qua Vite `base=/memos/` + reverse-proxy. *(assumed A1)*
- **N02 — Đóng gói 1 khối** (`code:cmd/memos`): `pnpm release` nhúng SPA vào `server/router/frontend/dist` → 1 Go binary serve cả API + UI.
- **N03 — Theme neumorphism (system theme dây chuyền)** (`nfr`): giao diện memos build LẠI theo design-system mặc định của dây chuyền = **Neumorphism** (`skills/br/assets/design-template.md` §3.6): mặt đơn sắc, cặp bóng sáng+tối, không viền, chữ đạt WCAG AA. Override token shadcn trong `web/src/themes/`, KHÔNG sửa component logic.
- **N05 — Rebrand "Lume" + UI cao cấp** (`nfr`): bỏ hoàn toàn tên "Memos" + logo con vẹt → thương hiệu **Lume** (logo neumorphic "nguồn sáng" SVG inline, favicon mới, title). Áp neumorphism ĐÚNG SPEC (superdesign 6-moves): dual-shadow thật `9px/18px` màu dẫn xuất `#bec3c9`/`#ffffff`, inset input/pressed, CTA phẳng accent `#4d6bfe`, focus-ring, text AA `#2d3436` — nhắm class thật (`.bg-card`, `[data-slot=button]`, `input`), không chỉ đổi nền.
- **N04 — Lưu trữ file-first** (`nfr`, thay M-storage): **ĐÃ LÀM (14/07/26)**. Nội dung memo là file `.md` trên đĩa (`<data>/memos-md/<uid>.md`, frontmatter + body) = **nguồn chân lý**; SQL còn lại làm **index** để lọc/tìm. Ghi ⇒ phải ra file; đọc ⇒ **file thắng DB** (sửa tay file bằng editor thì app hiện ngay). Không rewrite `store.Driver` — chèn tầng vào 5 hàm memo của `store`. Gate: `go test ./store/file/...` (7 bất biến).
