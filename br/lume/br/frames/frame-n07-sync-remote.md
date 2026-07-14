---
schema_version: 0
frame_id: frame-n07-sync-remote
created_by: human
kind: frame
parent_br: br/lume/br/BR.md
clause_ids: [N07]
parent_br_hash: 1666843d0326e46cbb4d38a75756b0487bdb569a3054f00b7cb82ac6db025e63
muc_tieu: "Đẩy memo người dùng gõ trong Lume local lên một instance Lume ở xa — thủ công, idempotent, không đụng memo từ llmwiki"
scope_code: ["lume/internal/remotesync/sync.go","lume/cmd/lume/sync.go"]
scope_test: ["lume/internal/remotesync/sync_test.go"]
acceptance_test: "cd lume && go test ./internal/remotesync/... -count=1"
ui_role: none
ui_screen:
---
# frame-n07-sync-remote

## Nghiệp vụ

Lume chạy **local**. Memo người dùng gõ trong app nằm ở kho của Lume (`<data>/memos-md/`). Khi muốn
lưu lên server, người dùng **bấm/gõ lệnh** để đẩy lên một **instance Lume ở xa**. Không tự động,
không chạy nền — đẩy dữ liệu ra khỏi máy là việc người quyết, không phải app tự quyết.

**RANH GIỚI CỨNG:** memo đến từ **mount `llmwiki`** (frame-n06) **KHÔNG được đẩy**. llmwiki là
**nguồn chân lý ở máy local**, không phải nội dung của Lume; đẩy nó lên remote = nhân bản kho tri
thức ra một nơi không ai quản. Lọc bằng chính sự tồn tại của file trong `memos-md/` — memo mount
không có file ở đó, nên không bao giờ lọt vào danh sách đẩy.

## Input / Output

- **Input:** memo trong `<data>/memos-md/*.md` + `--remote <url>` + token (`--token` hoặc `LUME_TOKEN`).
- **Output:** memo tương ứng trên remote; sổ `<data>/sync-state.json` (localUID → {remote name, hash}).

## Tiêu chí nghiệm thu (máy chấm)

`go test ./internal/remotesync/...`:
1. Lần đầu → **POST tạo** trên remote, có gửi `Authorization: Bearer`.
2. **IDEMPOTENT:** chạy lại khi nội dung không đổi → **BỎ QUA**, không đẻ bản trùng.
3. Sửa nội dung → **PATCH đúng memo cũ** (không POST bản thứ hai).
4. `--dry-run` → nói sẽ làm gì, **không gọi mạng**.
5. **Đổi remote ⇒ bỏ sổ cũ** — id của server khác không được dùng cho server này (dùng nhầm là
   **ghi đè lên memo của người khác**).
6. Remote lỗi → báo `failed`, **KHÔNG ghi sổ** (không thì lần sau tưởng đã đẩy, memo mất luôn).

Bằng chứng đầu-cuối (2 instance thật): local `:5230` (đang mount 201 memo wiki) → remote `:5231`.
- sync lần 1: `tạo 1` — **chỉ 1 memo của Lume, 201 memo wiki KHÔNG bị đẩy**.
- sync lần 2: `bỏ qua 1` (idempotent).
- sửa nội dung rồi sync: `cập nhật 1`, remote vẫn **1 memo** (không nhân đôi).

## Ngoài phạm vi

- Chiều remote → local (kéo về) — chưa làm.
- Không có nút trên UI: hiện là lệnh CLI `lume sync`. Nút bấm là frame UI riêng.
- Không tự động/nền: đúng chủ ý (người quyết khi nào dữ liệu rời máy).

## UI hoạt động ra sao
- Không UI (CLI).
