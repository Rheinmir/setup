---
schema_version: 0
frame_id: frame-n04-storage-file-first
created_by: human
kind: frame
parent_br: br/lume/br/BR.md
clause_ids: [N04]
parent_br_hash: 1666843d0326e46cbb4d38a75756b0487bdb569a3054f00b7cb82ac6db025e63
muc_tieu: "Lưu trữ file-first: nội dung memo là file .md trên đĩa (nguồn chân lý), SQL chỉ còn là index"
scope_code: ["lume/store/file/mdstore.go","lume/store/memo.go","lume/store/store.go"]
scope_test: ["lume/store/file/mdstore_test.go"]
acceptance_test: "cd lume && go test ./store/file/... -count=1"
depends_on: []
ui_role: none
ui_screen:
---
# frame-n04-storage-file-first

## Nghiệp vụ

Nội dung memo phải là **file `.md` người-đọc-được trên đĩa** (`<data>/memos-md/<uid>.md`), không phải
blob trong DB. Người dùng sở hữu dữ liệu của mình: grep được, sửa bằng editor được, đưa vào git được,
backup bằng `cp` được. SQL còn lại làm **INDEX** (id/uid/thời gian/visibility/quan hệ) để lọc nhanh.

## Input / Output

- **Input:** memo do người dùng gõ trên UI (qua API) HOẶC file `.md` người dùng sửa tay trên đĩa.
- **Output:** `<data>/memos-md/<uid>.md` (frontmatter + body) = nguồn chân lý; DB giữ index để lọc.

## Thiết kế (design-twice)

- **PA-A — Driver file thuần:** viết `store.Driver` mới đọc/ghi hoàn toàn bằng file.
  ❌ Loại: `Driver` là interface khổng lồ, khoá cứng SQL (`GetDB() *sql.DB` + migrator SQL). Phải cài
  lại toàn bộ filter/tìm kiếm đang chạy → rủi ro rất lớn, giá trị thêm rất ít.
- **PA-B — Export sidecar:** DB vẫn là chân lý, định kỳ xuất ra `.md`.
  ❌ Loại: file chỉ là *bản sao*. Sửa tay file không có tác dụng ⇒ **không phải file-first**, chỉ là backup.
- **PA-C — Nội dung ra file, metadata làm index (CHỌN):** chèn tầng file-first vào 5 hàm memo của
  `store` (chỗ nghẽn duy nhất mọi memo đi qua). **Ghi ⇒ phải ra file. Đọc ⇒ FILE THẮNG DB.**
  ✅ Vì: giữ nguyên sức mạnh lọc/tìm kiếm của SQL, mà thứ người dùng thật sự sở hữu (nội dung) thì nằm
  trên đĩa dạng người đọc được. Mất DB → dựng lại index từ frontmatter. Mất `.md` → mất nội dung ⇒ đúng
  định nghĩa "file là nguồn chân lý".
- **GHÉP từ PA-B:** frontmatter mang đủ metadata (id/uid/creator/ts/visibility/row_status) để dựng lại
  index — tức là vẫn có tính năng "export đầy đủ" của PA-B, miễn phí.

## Tiêu chí nghiệm thu (máy chấm)

`go test ./store/file/...` — 7 bất biến, đỏ một cái là file-first hỏng:
1. **Ghi ⇒ có file `.md` thật** (frontmatter + body).
2. **Round-trip lossless** — nội dung ra đúng như vào.
3. **Frontmatter dựng lại được record** (mất DB vẫn khôi phục được index).
4. **Sửa tay file → đọc ra bản sửa tay** ← cốt lõi; hỏng cái này thì DB vẫn là chân lý.
5. **List từ ĐĨA**, không hỏi DB.
6. **Xoá memo ⇒ file biến mất**; xoá 2 lần vẫn idempotent (không để file mồ côi).
7. **uid độc hại không thoát khỏi thư mục** (path traversal).

Bằng chứng đầu-cuối (ngoài unit-test): gõ memo trên UI → `data/memos-md/<uid>.md` xuất hiện; sửa tay
file bằng editor → app hiện đúng bản sửa tay (ảnh: `br/lume/qa-final/file-first.png`).

## Ngoài phạm vi

- Không viết lại `store.Driver` (PA-A đã loại). Attachment/user/setting vẫn ở SQL.
- Chưa có watcher: sửa file lúc app đang chạy thì thấy ngay ở lần đọc kế, nhưng **index (thời gian/
  visibility) không tự cập nhật theo frontmatter** — muốn đổi metadata thì sửa qua app.

## UI hoạt động ra sao
- Không UI (tầng lưu trữ).
