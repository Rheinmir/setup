# harness-local/ — harness RIÊNG của dự án này

Nơi **dự án này** tự phát triển rule/validator riêng, chạy **song song** với harness framework
(R1–R13) mà KHÔNG giẫm chân nó. Folder này **thuộc về dự án** — `sync-template`/framework-update
**không bao giờ đụng** (không nằm trong `.template-manifest.json`).

## Cách thêm một rule (3 bước)
1. `cp harness-local/validators/_template.py harness-local/validators/<ten>.py` rồi viết logic.
2. Khai rule vào `harness-local/policy.yaml` với id **`P<n>`** (P = project; **KHÔNG** dùng `R<n>` — đụng framework).
3. Xong. Rule tự chạy ở: write-time (PreToolUse hook), commit (pre-commit), merge (CI) — y như framework.

## Contract của một project validator (API ỔN ĐỊNH — framework cam kết không đổi)
Một validator = 1 file `.py` trong `harness-local/validators/` (KHÔNG bắt đầu bằng `_`):

- **Input** — nhận event qua **stdin JSON** *hoặc* **argv là đường dẫn file**:
  - `{"action":"write","file_path":"...","content":"..."}` — khi agent ghi file (PreToolUse)
  - `{"action":"bash","command":"..."}` — khi agent chạy Bash
  - `{"action":"stop"}` — cuối lượt
  - hoặc `validator.py <file1> <file2> ...` — pre-commit/CI truyền file đổi
- **Output / exit code:**
  - `exit 0` = PASS (cho qua)
  - `exit 2` = BLOCK (chặn) — in lý do ra **stderr**
- **Fail-open:** lỗi bất ngờ → exit 0 (đừng làm gãy phiên/commit của người khác).

Vì cùng contract, bạn có thể copy một validator framework (`harness/validators/*.py`) làm mẫu.

## Vì sao không giẫm chân (sandbox các case fail)
- **Không đụng framework:** id `P<n>` ≠ `R<n>`; validator nằm dir riêng; framework không đọc folder này để quyết định gì.
- **Sống sót framework-update:** ngoài manifest → `sync-template` bỏ qua. Contract ổn định → validator cũ vẫn chạy khi framework lên version.
- **Độc lập:** rule project + rule framework đều phải pass (AND). Project KHÔNG tắt được rule framework.
- **An toàn khi vắng:** không có rule nào → runner no-op, dự án chạy như thường.

## Đăng ký (policy.yaml)
Mỗi rule một block (xem `policy.yaml`). Dùng `harness-local/run.py --list` để xem rule hiện có,
`harness-local/run.py --check` để self-test (id hợp lệ + validator chạy được).
