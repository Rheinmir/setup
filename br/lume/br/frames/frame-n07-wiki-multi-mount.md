---
schema_version: 0
frame_id: frame-n07-wiki-multi-mount
created_by: human
kind: frame
parent_br: br/lume/br/BR.md
clause_ids: [N07]
parent_br_hash: 5c7f64350a7d0bffced5cd1b77902cf85f5f7592c03b348423f41985a4d20a79
muc_tieu: "Trỏ Lume vào nhiều folder llmwiki trên máy ngay trong app, đặt tên cho từng cái, mỗi wiki một tab chuyển qua lại được — đổi tên KHÔNG được phá UID memo"
scope_code: ["lume/store/mountregistry.go","lume/server/router/api/v1/wiki_mount_service.go","lume/server/router/api/v1/v1.go","lume/internal/pick/pick.go","lume/web/src/components/WikiTabs.tsx"]
scope_test: ["lume/store/mountregistry_test.go"]
acceptance_test: "cd lume && go test ./store/... -run MountRegistry -count=1"
depends_on: [frame-n06-wiki-mount]
ui_role: panel
ui_screen: home
guards:
  max_iter: 3
  budget_seconds: 600
  no_progress_k: 2
  escalate_after_iter: 3
---
# frame-n07-wiki-multi-mount — Nhiều wiki, mỗi wiki một tab

## Nghiệp vụ

Frame n06 đã cho Lume stream **một** thư mục `llmwiki` lên app, nhưng thư mục đó phải khai bằng
cờ `--mount name=path` lúc khởi động server. Người dùng thật có **nhiều** kho tri thức trên máy —
mỗi dự án một `llmwiki` — và muốn mở chúng cùng lúc, mỗi cái một tab, chuyển qua lại như tab trình
duyệt. Bắt họ sửa cờ rồi khởi động lại server mỗi lần đổi wiki là hỏng luồng làm việc.

Frame này cho phép: bấm `+` ngay trong app → chọn folder → đặt tên → wiki hiện thành tab, ngay lập
tức, không restart. Tên gợi ý sẵn là tên folder **bọc ngoài** `llmwiki` (vì bản thân folder luôn tên
`llmwiki`, nên tên đó vô nghĩa để phân biệt; cái phân biệt là dự án chứa nó).

Mount vẫn **READ-ONLY tuyệt đối** như n06 — Lume không bao giờ ghi vào kho tri thức.

## Input / Output
- **Input:** người dùng bấm `+` → BE mở hộp thoại chọn folder của HĐH → trả về đường dẫn tuyệt đối
  thật (vd `/Users/x/orca/workspaces/setup/issue-15-br-k/llmwiki`) + nhãn gợi ý (`issue-15-br-k`).
  Người dùng sửa nhãn nếu muốn rồi Enter.
- **Output:** một tab wiki mới hiện ngay trên tab-strip, đã quét index và đang watch; danh sách mount
  được ghi xuống `<data>/mounts.json` nên sống qua restart. Chuyển tab = đổi wiki đang xem.

## Tiêu chí nghiệm thu
- Gắn được ≥2 wiki trong một phiên, không restart server; cả hai đều watch (sửa file bằng editor →
  app hiện ngay).
- **Đổi tên (label) một wiki KHÔNG làm đổi một UID nào** — không đẻ memo mới, không bỏ lại memo mồ côi.
  Đây là bất biến quan trọng nhất của frame; test phải khoá nó.
- `mounts.json` mất/hỏng → server vẫn lên, chỉ mất tab, không chết (fail-open).
- Path không tồn tại / không phải thư mục / không có file `.md` nào → từ chối ở BE kèm lý do đọc được,
  không gắn tab rỗng.
- Ổ ngoài rút ra (path biến mất) → tab hiện trạng thái lỗi, **index giữ nguyên**, không im lặng xoá memo
  (kế thừa phanh scan-0-file của n06).
- Mount cũ khai bằng cờ `--mount` vẫn chạy y như trước (không phá n06).

## Ngoài phạm vi
- Không làm directory-browser server-side (API đọc cây thư mục của máy) — xem mục Thiết kế, PA-B bị loại.
- Không tìm kiếm xuyên wiki, không xem 2 wiki cạnh nhau trong cùng một khung.
- Không đồng bộ hai chiều (Lume vẫn không bao giờ ghi vào kho tri thức — N06 giữ nguyên).
- Không sửa `mount.go`, `mountsync.go`, `store.go`, `main.go` (thuộc frame n04/n06 — R6 exclusive-scope).
  Thiết kế dưới đây cố ý né hoàn toàn 4 file đó.

## UI hoạt động ra sao
Một **tab-strip** mỏng ngay trên danh sách memo ở Home: `Memos │ issue-15-br-k ● │ co2-be ⚠ │ +`.
Tab `Memos` là memo riêng của người dùng (như cũ). Mỗi tab wiki có chấm trạng thái (● đang watch,
⚠ mất kết nối). Tab đang mở hiện một dòng meta: `🔒 read-only · 201 file · <full-path>`. Bấm `+` mở
hộp thoại native. Hover tab → `×` để gỡ (chỉ xoá index, **không đụng file gốc**).

## Thiết kế (design-twice)

Chạy `/design-twice`, 3 phương án song song, mỗi phương án bị ép một ràng buộc khác nhau tận gốc.

**PA-A — ít phần tử nhất.** Tab-strip + một hàng inline hai ô (path, tên) để dán đường dẫn. Không màn
settings, không dialog, không API duyệt thư mục. 3 RPC. Thừa nhận thẳng: người không quen ⌘⌥C (copy
as pathname trong Finder) sẽ đứng hình ở bước đầu, và cố ý không vá chỗ đó.

**PA-B — trạm điều khiển.** BE phục vụ API duyệt cây thư mục để người dùng browse ngay trong app, thấy
trước mỗi folder có bao nhiêu file `.md`; kèm màn Settings hiển thị trạng thái, số file, sync cuối, va
chạm UID. Mạnh nhất, nhưng đẻ ra một **API đọc cây thư mục của máy** — phải jail root, resolve symlink
trước khi so prefix, chặn DNS-rebinding, cap tài nguyên. PA-B tự liệt kê 7 biện pháp phòng thủ, tức là
nó tự thấy đây là phần đắt nhất.

**PA-C — vault switcher kiểu Obsidian.** Bỏ tab ngang, thay bằng `⌘O` switcher + danh sách recent, một
vault mở tại một thời điểm. Nhảy wiki nhanh nhất, chịu được 30+ wiki. Nhưng bán mất khả năng xem hai
wiki cạnh nhau. **Đóng góp lớn nhất của PA-C không phải hình dạng mà là hai insight kỹ thuật** (xem dưới).

### Chọn: TỔNG HỢP A + C

Hình dạng lấy của **A** (tab-strip tối giản, không màn settings riêng) vì yêu cầu gốc nói rõ "mỗi wiki
là một tab" — nên switcher độc quyền của C bị loại về mặt hình dạng.

Nhưng lấy hai thứ then chốt của **C**:

1. **Chọn folder bằng hộp thoại native do BE mở** (osascript trên macOS), không phải dán path tay.
   Ràng buộc "browser không trả đường dẫn tuyệt đối" là thật, nhưng nó **chỉ cấm web picker** — nó không
   hề buộc người dùng phải dán path. BE là process local, nó mở được dialog của HĐH. Cả A lẫn B đều bỏ
   sót lối này: A cam chịu dán tay, B xây hẳn directory-browser để né việc dán tay. Native dialog cho
   kết quả của B mà không đẻ ra API đọc ổ đĩa nào cả. Dán path giữ lại làm **đường lùi** khi native lỗi
   (headless/CI/Linux không có zenity).

2. **Tách `id` bất biến khỏi `label`.** Đây là phát hiện đắt nhất của cả vòng thiết kế: `mount.go:46`
   có `UIDFor(rel) = m.Name + "-" + sha1(rel)[:12]`, tức `Mount.Name` **vừa là tên hiển thị vừa là khoá
   UID vừa là tag gốc**. Làm đúng yêu cầu "đặt tên được" mà không tách hai thứ này thì mỗi lần đổi tên:
   201 UID đổi → `SyncMount` không thấy UID cũ → **tạo mới 201 memo** → 201 memo cũ nằm lại DB thành xác
   không có file phía sau, kéo theo mọi reaction/shortcut trỏ vào chúng. Tính năng sẽ tự phá dữ liệu ngay
   lần đổi tên đầu tiên. Cách chữa: `id` opaque sinh một lần lúc gắn (bất biến, dùng làm prefix UID, không
   bao giờ hiện lên UI) tách khỏi `label` (tên tab, đổi tự do, **chỉ ghi vào `mounts.json`, không chạm một
   dòng DB nào**). Migration cho `--mount name=path` đang có: coi `name` cũ **chính là** `id` → UID hiện hữu
   giữ nguyên, zero migration.

**Loại PA-B** (directory-browser): native dialog cho cùng trải nghiệm với chi phí gần bằng 0 và không mở
ra bề mặt tấn công nào. Chỉ **ghép lại một ý của B**: chấm trạng thái mount trên tab (● watching / ⚠ mất
kết nối) — B chỉ ra đúng rằng đây là chỗ đau nhất mà A bỏ (ổ ngoài rút ra thì tab vẫn đứng im, lỗi chỉ
nằm trong log server).

### Hệ quả kiến trúc: né R6 exclusive-scope

Thiết kế cố ý **không sửa** `mount.go`/`mountsync.go`/`store.go`/`main.go` (đã thuộc frame n04/n06).
Làm được vì `Mount.Name` được **giữ nguyên nghĩa** làm `id` bất biến — nên `UIDFor`/`TagsFor` không phải
đổi một dòng nào. `label` + persist + gắn nóng sống ở file **mới** `store/mountregistry.go` (cùng package
`store`, thêm method vào `*Store` — Go cho phép). Service gRPC mới nằm ở file mới, đăng ký trong `v1.go`
(file duy nhất trong luồng này chưa thuộc frame nào). Registry được nạp lười từ `v1.go` lúc dựng service,
nên không cần chạm `main.go`.

### Trần còn lại (không giả vờ đã sửa)
UID vẫn `= f(id, relpath)`. Di chuyển **cả folder** wiki → an toàn (relpath không đổi). Đổi tên/di chuyển
**file bên trong** wiki → vẫn re-key và bỏ lại memo cũ — đây là hành vi sẵn có của n06, frame này không
làm tệ hơn nhưng cũng không sửa. Diệt hẳn thì phải neo UID vào một id nằm trong frontmatter file, mà thế
là **ghi vào kho tri thức** — phá ràng buộc READ-ONLY. Nên: để nguyên, và log cảnh báo khi thấy memo có
index nhưng `Read()` trả `false` (mồ côi thì phải kêu, đừng im).
