---
schema_version: 0
frame_id: frame-n08-mount-ui
created_by: human
kind: frame
parent_br: br/lume/br/BR.md
clause_ids: [N06, N07]
parent_br_hash: 1666843d0326e46cbb4d38a75756b0487bdb569a3054f00b7cb82ac6db025e63
muc_tieu: "Bấm nút trong app chọn thư mục bất kỳ trên máy → thêm vào danh sách view (cộng dồn nhiều folder), mỗi folder có nút Sync đẩy nguyên cụm lên remote"
scope_code: ["lume/server/router/mount/mount_service.go","lume/server/router/mount/mount_crud.go","lume/web/src/components/MountFolders.tsx"]
scope_test: ["lume/server/router/mount/mount_service_test.go"]
acceptance_test: "cd lume && go test ./server/router/mount/... -count=1"
ui_role: panel
ui_screen: home
---
# frame-n08-mount-ui

## Nghiệp vụ

Lume là app local. Người dùng **bấm nút trong app** → **chọn một thư mục bất kỳ trên máy**
(llmwiki hoặc folder `.md` nào cũng được) → folder đó **thêm vào danh sách view**. Chọn được
**nhiều lần, mỗi lần cộng thêm một folder** (không thay thế). Danh sách **sống qua restart**.
Mỗi folder có nút **Sync** → đẩy **nguyên cụm** folder đó lên một Lume ở xa.

## Input / Output

- **Input:** cú bấm nút → hộp thoại duyệt thư mục (server duyệt hộ) → chọn thư mục.
- **Output:** memo của folder hiện trong feed (thư mục = tag); `<data>/mounts.json` lưu danh sách.

## Thiết kế (design-twice)

Vấn đề cốt lõi: **trình duyệt CỐ TÌNH không cho JS biết đường dẫn tuyệt đối trên máy.**

- **PA-C — File System Access API (`showDirectoryPicker`) / kéo-thả:** dùng hộp thoại của HĐH.
  ❌ Loại: API này trả **NỘI DUNG**, không trả đường dẫn ⇒ server không có path ⇒ **fsnotify chết**
  (mất "file đổi → app hiện ngay"), buộc phải **upload nội dung** ⇒ mount đọc-thẳng biến thành
  **import có copy** (đẻ lại bản thứ hai — đúng thứ vừa loại ở n06). Thêm nữa: **Firefox/Safari
  không hỗ trợ**, và phải cấp quyền lại mỗi lần mở tab.
- **PA-B — user tự dán đường dẫn:** an toàn nhất, bề mặt tấn công nhỏ nhất (server không có API
  liệt kê thư mục).
  ❌ Loại: **không phải "ấn nút chọn folder"** — bắt user sang Finder bấm Cmd+Option+C copy path.
- **PA-A — SERVER duyệt hộ (CHỌN):** server Go chạy ngay trên máy này, nên nó liệt kê thư mục và
  trả về **đường dẫn tuyệt đối thật**; app hiện hộp thoại kiểu Finder. Giữ nguyên kiến trúc n06:
  mount đọc-thẳng, read-only, fsnotify sống.
  ✅ Vì: đúng thứ user yêu cầu (bấm nút, chọn folder) mà **không phá** mount/stream/read-only.

**GHÉP từ PA-B (bắt buộc, không thương lượng):** API đọc filesystem là mặt tấn công thật — bất kỳ
trang web nào đang mở cũng `fetch("http://localhost:5230/...")` được. Nó chỉ được phép tồn tại kèm
**4 PHANH**:
1. **Chỉ loopback** — server bind ra LAN ⇒ tắt thẳng (người cùng wifi đọc được cây thư mục).
2. **Whitelist gốc `$HOME`** + `EvalSymlinks` trước khi so (symlink là cách kinh điển để trỏ ra ngoài).
3. **Chỉ trả THƯ MỤC** — không nội dung, không size/mtime; bỏ dotfile; cap 500 entry.
4. **Chỉ ADMIN + chốt CSRF `X-Lume-Mount`** — cấm cookie hoàn toàn thì SPA chết (token httpOnly),
   nên: cho cookie **nhưng** bắt header tuỳ biến mà **trang khác origin không gửi được** (CORS chặn
   preflight).

Validate khi thêm (cũng từ PA-B): path tuyệt đối · tồn tại · là thư mục · **không lồng** với mount
đã có (cùng file → 2 uid → memo trùng) · **không phải thư mục data của chính Lume** (vòng lặp) ·
**phải có ≥1 file `.md`** (chống chọn nhầm chỗ).

## Tiêu chí nghiệm thu (máy chấm)

`go test ./server/router/mount/...`:
1. Ẩn danh / thiếu header CSRF ⇒ **chặn**.
2. Duyệt ra ngoài `$HOME` (vd `/etc`) ⇒ **403**, kể cả path tuyệt đối hợp lệ.
3. Symlink trỏ ra ngoài whitelist ⇒ **403** (resolve trước khi so).
4. Thêm folder lồng nhau ⇒ **409**.
5. Thêm folder không có `.md` ⇒ **400**.
6. Thêm 2 folder ⇒ danh sách **cộng dồn** (không thay thế); ghi `mounts.json`.
7. Bind ngoài loopback ⇒ API duyệt thư mục **tắt**.

Bằng chứng đầu-cuối: sidebar mục **Thư mục** có `wiki (202)` + `frames (17)`; bấm nút mở hộp thoại
duyệt `$HOME` (ảnh `br/lume/qa-final/mount-picker.png`); restart server → cả 2 folder vẫn còn
(log: "mount đã gắn (read-only) mount=wiki / mount=frames").

## Ngoài phạm vi

- Không có picker của HĐH (đã loại PA-C — nó phá kiến trúc).
- Nút Sync hiện hỏi remote/token bằng `prompt()` — chưa có form đẹp.
- Bỏ folder khỏi app KHÔNG xoá index memo cũ (dọn ở lần Scan sau).

## UI hoạt động ra sao

- **Tương tác:** sidebar → mục **Thư mục** → nút `+` → hộp thoại duyệt (breadcrumb, `..`, chấm ●
  đánh dấu thư mục có `.md`) → **Chọn thư mục này** → memo hiện ngay trong feed.
- Mỗi hàng folder: tên · số file · nút **Sync** (đẩy cả cụm) · nút **×** (bỏ khỏi danh sách,
  **không xoá file trên đĩa** — nói rõ trong confirm, nếu không user không dám bấm).
- **Trạng thái:** lỗi validate hiện đỏ ngay trong hộp thoại (vd "thư mục này không có file .md nào").
- Hộp thoại phải render qua **portal ra `document.body`**: nằm trong sidebar thì sidebar tạo
  stacking context riêng ⇒ `z-index` vô nghĩa ⇒ memo card đè lên (đã dính).
