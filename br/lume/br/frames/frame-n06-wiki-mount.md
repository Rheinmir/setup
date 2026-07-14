---
schema_version: 0
frame_id: frame-n06-wiki-mount
created_by: human
kind: frame
parent_br: br/lume/br/BR.md
clause_ids: [N06]
parent_br_hash: 5c7f64350a7d0bffced5cd1b77902cf85f5f7592c03b348423f41985a4d20a79
muc_tieu: "Stream nguyên cấu trúc thư mục llmwiki từ máy lên app: mỗi .md = 1 memo, thư mục = tag, file đổi thì app hiện ngay"
scope_code: ["lume/store/file/mount.go","lume/store/mountsync.go","lume/internal/profile/profile.go","lume/cmd/lume/main.go"]
scope_test: ["lume/store/file/mount_test.go"]
acceptance_test: "cd lume && go test ./store/file/... -count=1"
depends_on: [frame-n04-storage-file-first]
ui_role: none
ui_screen:
---
# frame-n06-wiki-mount

## Nghiệp vụ

Lume là **app local**. Nó nhận một thư mục trên máy (`llmwiki/wiki/`, 201 file `.md`, có cây con
`concepts/ entities/ sources/ draft/ skills/`) và **stream nguyên cấu trúc thư mục đó lên app**:
mỗi `.md` = một memo, **đường dẫn thư mục = tag**. Sửa file bằng vim/agent/git → app hiện **ngay**.

Chiều ngược (memo gõ trong Lume → ghi ra llmwiki) là **THỦ CÔNG** — người bấm mới đẩy. App **không
tự ghi** vào kho tri thức.

## Input / Output

- **Input:** thư mục wiki trên máy (flag `--mount wiki=<path>`), read-only đối với Lume.
- **Output:** 201 memo trong app, tag theo cây thư mục; nội dung đọc **thẳng từ file gốc**.

## Thiết kế (design-twice)

- **PA-A — Mirror/import:** copy wiki vào kho memo (`memos-md/` + DB), watcher đồng bộ lại.
  ❌ Loại: **hai bản ⇒ nguồn chân lý mờ**. Sửa memo trong Lume sẽ bị lần sync sau đè mất; xoá nhầm
  `--mount` trỏ sai → reconcile xoá sạch 201 memo. Đúng bệnh "hai nguồn sự thật" vừa trả nợ xong.
- **PA-C — Đổi gốc (llmwiki CHÍNH LÀ kho memo):** bỏ `memos-md/`, trỏ gốc file-first vào wiki.
  ❌ Loại: hết lệch thật, nhưng **app được quyền ghi thẳng vào git repo tri thức** (có harness/rule/
  ledger): xoá memo trong UI = `os.Remove` file wiki thật; frontmatter memo mọc lên mọi file OKF →
  diff bẩn cả repo. Rủi ro không che được, đổi lại lợi ích nhỏ.
- **PA-B — MOUNT read-only + index (CHỌN):** DB chỉ giữ **index** (uid/ts/tag), **KHÔNG lưu content,
  KHÔNG lưu đường dẫn**. Nội dung đọc **thẳng từ file gốc tại chỗ** mỗi lần list. Map `uid ↔ relpath`
  sống trong RAM, dựng lại bằng một lần walk lúc boot (201 file ≈ vài ms). Ghi/xoá vào uid thuộc
  mount ⇒ **`ErrReadOnly`**, chặn ở tầng store (không phải chỉ ẩn nút trên UI).
  ✅ Vì: **không có bản thứ hai để lệch**, và **Lume không bao giờ ghi vào llmwiki**.

- **GHÉP từ PA-A:** phanh reconcile — walk ra **0 file** (mount chưa gắn / trỏ sai / ổ chưa mount)
  thì **KHÔNG xoá index**; debounce gom event (một `git checkout` sinh ~200 event một lúc).
- **GHÉP từ PA-C:** file wiki có frontmatter OKF → `split()` cắt head, UI chỉ hiện **body sạch**,
  không phơi YAML.

## Tiêu chí nghiệm thu (máy chấm)

`go test ./store/file/...`:
1. Scan cây thư mục → mỗi `.md` một uid **tất định theo relpath** (chạy 2 lần ra cùng uid).
2. **Thư mục = tag** (`concepts/okf.md` → tag `wiki`, `concepts`).
3. Đọc uid của mount ⇒ **nội dung lấy từ file gốc**; sửa file → đọc lại ra bản mới (stream thật).
4. **Ghi/xoá vào mount ⇒ `ErrReadOnly`** (app không được đụng kho tri thức).
5. Frontmatter OKF của wiki bị cắt, UI chỉ thấy body.
6. **Walk ra 0 file ⇒ KHÔNG coi là "mọi thứ đã bị xoá"** (phanh chống xoá sạch index).
7. Va chạm uid (`a/b.md` vs `a-b.md`) phải phát hiện được, không im lặng nuốt file.

## Ngoài phạm vi

- Chiều Lume → llmwiki (thủ công) là frame riêng — frame này chỉ làm chiều **đọc/stream**.
- Không sửa/xoá được memo wiki từ UI (đúng thiết kế: wiki là chủ sở hữu file của nó).

## UI hoạt động ra sao
- Không thêm màn mới: memo wiki hiện trong feed như memo thường, lọc bằng tag = duyệt cây thư mục.
