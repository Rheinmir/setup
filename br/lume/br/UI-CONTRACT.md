# UI CONTRACT — issue-15-br-k

> Contract chốt thực hiện — sinh tự động từ frames + `br/ui-layout.yaml` (`br-contract.py`). Trục code (frame) và trục hiển thị (screen/route) tách nhau.

**Tổng:** 14 frame · 8 màn hình · 8 route thật · nav_style `sidebar`

## Bảng contract

| frame | làm gì | ui_role | màn hình | route | clause | acceptance (điều kiện chốt) | trạng thái |
|---|---|---|---|---|---|---|---|
| `frame-m01-auth` | Đăng nhập/đăng ký + session + admin sign-in cho memos | form | Sign in / Sign up | `/auth` | M1 | `(reverse: mô tả code có sẵn — không test-first)` | chưa chạy |
| `frame-m02-user-settings` | Hồ sơ người dùng + cài đặt cá nhân + vai trò | screen | Settings & Admin | `/setting` | M2 | `(reverse: mô tả code có sẵn — không test-first)` | chưa chạy |
| `frame-m03-memo-crud` | Tạo/sửa/xoá/liệt kê memo Markdown-native (lõi sản phẩm) | screen | Home (memo list + editor) | `/` | M3 | `(reverse: mô tả code có sẵn — không test-first)` | chưa chạy |
| `frame-m04-memo-organize` | Tag/pin/archive/quan hệ memo | panel | Archived | `/archived` | M4 | `(reverse: mô tả code có sẵn — không test-first)` | chưa chạy |
| `frame-m05-share-explore` | Chia sẻ public + feed Explore | screen | Explore (feed công khai) | `/explore` | M5 | `(reverse: mô tả code có sẵn — không test-first)` | chưa chạy |
| `frame-m06-attachment` | Upload file đính kèm vào memo | screen | Attachments | `/attachments` | M6 | `(reverse: mô tả code có sẵn — không test-first)` | chưa chạy |
| `frame-m07-reaction` | Thả emoji reaction lên memo | widget | Home (memo list + editor) | `/` | M7 | `(reverse: mô tả code có sẵn — không test-first)` | chưa chạy |
| `frame-m08-shortcut` | Lưu bộ lọc/shortcut | screen | Shortcuts | `/shortcuts` | M8 | `(reverse: mô tả code có sẵn — không test-first)` | chưa chạy |
| `frame-m09-inbox` | Hộp thư/thông báo | screen | Inbox | `/inbox` | M9 | `(reverse: mô tả code có sẵn — không test-first)` | chưa chạy |
| `frame-m10-sso-idp` | Đăng nhập ngoài (SSO/IdP) + callback | form | Sign in / Sign up | `/auth` | M10 | `(reverse: mô tả code có sẵn — không test-first)` | chưa chạy |
| `frame-m11-instance-admin` | Cấu hình instance/admin | panel | Settings & Admin | `/setting` | M11 | `(reverse: mô tả code có sẵn — không test-first)` | chưa chạy |
| `frame-n01-microservice-path` | Mount memos dưới /memos/ (Vite base + reverse-proxy) — giá t… | none | — | `—` | N01 | `(reverse: mô tả code có sẵn — không test-first)` | chưa chạy |
| `frame-n03-theme-neumorphism` | Build lại UI memos theo system theme neumorphism của dây chu… | none | — | `—` | N03 | `(reverse)` | chưa chạy |
| `frame-n04-storage-file-first` | Đổi lưu trữ memos từ DB sang file-first (mỗi memo 1 file .md) | none | — | `—` | N04 | `(reverse)` | chưa chạy |

## Màn hình → frame
- **Home (memo list + editor)** (`/`): `frame-m03-memo-crud`, `frame-m07-reaction`
- **Explore (feed công khai)** (`/explore`): `frame-m05-share-explore`
- **Archived** (`/archived`): `frame-m04-memo-organize`
- **Attachments** (`/attachments`): `frame-m06-attachment`
- **Inbox** (`/inbox`): `frame-m09-inbox`
- **Shortcuts** (`/shortcuts`): `frame-m08-shortcut`
- **Settings & Admin** (`/setting`): `frame-m02-user-settings`, `frame-m11-instance-admin`
- **Sign in / Sign up** (`/auth`): `frame-m01-auth`, `frame-m10-sso-idp`
**Logic thuần (không UI):** `frame-n01-microservice-path`, `frame-n03-theme-neumorphism`, `frame-n04-storage-file-first`
