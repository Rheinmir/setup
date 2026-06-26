# PoC — harness vendor-neutral (1 lõi, nhiều dây cắm)

Chứng minh kiến trúc trong `llmwiki/html/250626-harness-architecture-vs-current.html`:
**logic chặn KHÔNG nằm trong MCP, cũng KHÔNG nhúng vào 1 vendor — nó là 1 CLI lõi đọc
`policy.yaml`, và mỗi vendor chỉ là caller mỏng gọi vào (hoặc đọc config sinh ra từ policy).**

## Chạy thử

```bash
bash demo.sh         # 13 assertion: lõi chặn đúng + sinh wiring 9 file
bash test-broad.sh   # 54 assertion: false-positive, normalize, bash, biên require_origin, files-mode, fail-open, GAPS
```

### Test rộng phát hiện gì (đáng chú ý)
- **False-positive guard PASS**: `coleslaw.md`, `draw.md`, `raws/`, `myraw/` (chứa chuỗi "raw") **không** bị chặn nhầm — glob khớp segment `raw/`, không khớp substring.
- **KNOWN GAPS (mục C, có chủ đích)**: lõi session soi *bề mặt* lệnh bash nên **KHÔNG** bắt: `python3 -c "open('…/raw/…','w')"`, `rm …/raw/…`, `sed -i <script> …/raw/…` (script chen giữa `-i` và file). Đây đúng là lý do **sàn đảm bảo phải ở CI/sandbox**, không phải regex hook — khớp kết quả verify 2026-06-25.
- **layer**: `raw/` bị chặn ở session nhưng **được phép** ở repo (con người commit raw/ hợp lệ) — do `enforce_at` trong policy, không hard-code.

## Cài vào dự án (1 lệnh)

```bash
bash harness/poc-vendor-neutral/install.sh /đường-dẫn/dự-án
#   [--vendor claude,opencode,cursor,codex,kiro]   # bỏ → tự dò
#   [--no-verify]
```
Tự làm B0–B4: copy lõi → dò vendor → `gen-converters.py` → **merge** `.claude/settings.json` + `opencode.json` (backup `.bak`), thả `harness.yml` vào `.github/workflows/`, tạo `.pre-commit-config.yaml`, copy advisory cho Cursor/Kiro → chạy `demo.sh` + `test-broad.sh`. Idempotent. CI + pre-commit luôn cài (sàn); adapter chỉ cài cho vendor có mặt. Sau đó mở session Claude mới để hook có hiệu lực.

## Gỡ / cài lại

```bash
bash harness/poc-vendor-neutral/uninstall.sh /đường-dẫn/dự-án   # gỡ ĐÚNG phần harness, giữ config của bạn
bash harness/poc-vendor-neutral/install.sh   /đường-dẫn/dự-án --clean   # cài MỚI = gỡ cũ rồi cài
```
`uninstall.sh` đảo ngược: gỡ CI, gỡ hook harness khỏi `.claude/settings.json` (giữ hook khác của bạn), gỡ glob deny harness khỏi `opencode.json` (giữ rule khác), gỡ pre-commit hook + advisory, xoá lõi. Có backup `.bak`. Cờ: `--keep-core` (chỉ gỡ wiring) · `--purge-bak`.

## Thành phần

| File | Vai trò |
|---|---|
| `policy.yaml` | **NGUỒN CHÂN LÝ DUY NHẤT** — luật (glob, layer). Dày tùy ý. Sửa ở đây. |
| `bin/llmwiki-validate.py` | **LÕI** vendor-neutral. Đọc policy, áp luật. Modes: `path` / `files` / `claude-hook`. exit 2=chặn (session), 1=fail (repo), 0=ok. fail-open khi lỗi hạ tầng. |
| `gen-converters.py` | Đọc policy → **sinh wiring** mọi vendor vào `out/`. Đây là "luồng cài đặt" B2/B3. |
| `out/…` | Wiring sinh ra (xem dưới). |

## Hai layer (policy quyết định, không phải code)

`enforce_at` trong policy lái hành vi:
- `session` (agent định ghi): `path` + `claude-hook` áp. `no_write_raw` ở đây → agent bị chặn ghi `raw/`.
- `repo` (commit/PR): `files` áp. `no_write_raw` **KHÔNG** ở repo → con người commit `raw/` vẫn hợp lệ; chỉ `require_origin` chạy. Demo mục 3 chứng minh điều này.

## Vendor wiring (sinh ra trong `out/`)

| Vendor | Cơ chế (đã kiểm chứng 2026-06-25) | File sinh ra | Gọi CLI? |
|---|---|---|---|
| Claude | PreToolUse hook → CLI `claude-hook` | `claude/settings.snippet.json` | ✅ |
| opencode | `permission.edit:deny` (native) + plugin gọi CLI | `opencode/opencode.json`, `opencode/plugin/harness.js` | native + (plugin ✅) |
| Antigravity | Permission Deny-rule theo path | `antigravity/permissions.snippet.txt` | native |
| Cursor | rules advisory (KHÔNG chặn ghi) | `cursor/.cursor/rules/harness.mdc` | — (nhắc) |
| Codex | AGENTS.md advisory | `codex/AGENTS.snippet.md` | — (nhắc) |
| Kiro | steering advisory | `kiro/.kiro/steering/harness.md` | — (nhắc) |
| **MỌI vendor** | **CI + pre-commit → CLI `files`** | `ci/harness.yml`, `pre-commit-snippet.yaml` | ✅ |

> **Sàn đảm bảo = CI + pre-commit**, vì rules advisory bị lờ ở mọi vendor non-Claude
> (opencode #29329, Cursor/Kiro/Antigravity tương tự). Session hook chỉ là phản hồi
> nhanh ở nơi vendor cho phép deny. MCP không cần ở đâu cả.

## Thêm luật mới

Sửa `policy.yaml` (thêm 1 rule) → `python3 gen-converters.py`. Mọi vendor cập nhật theo,
không đụng code adapter. Thêm *vendor* mới = thêm 1 nhánh ~15 dòng trong `gen-converters.py`.

## Lên production

- Gộp `policy.yaml` này vào `harness/policy.yaml` (đã cùng tinh thần R1/R2).
- Đóng gói `bin/llmwiki-validate.py` thành release pin version (xoá copy editable + sync hash-3-mốc).
- `gen-converters.py` gọi từ `install-harness.sh --vendor claude,opencode,…`.
