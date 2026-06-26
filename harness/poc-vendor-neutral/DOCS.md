# Harness vendor-neutral — tài liệu chi tiết (cách hoạt động + cách cài đặt)

> Tóm tắt 1 dòng: **luật ở `policy.yaml` → 1 lõi `llmwiki-validate.py` đọc & áp luật → mỗi
> vendor là dây nối mỏng gọi vào (hoặc đọc config sinh từ policy) → sàn đảm bảo là CI.**
> Không có MCP ở bất kỳ đâu trong đường enforce.

Mục lục: [1. Mô hình](#1-mô-hình) · [2. Thành phần](#2-thành-phần) · [3. policy.yaml](#3-policyyaml-nguồn-chân-lý)
· [4. Lõi CLI](#4-lõi-llmwiki-validatepy) · [5. CI](#5-ci-sàn-đảm-bảo) · [6. Cài đặt](#6-cài-đặt-luồng-b0b4)
· [7. Mở rộng](#7-mở-rộng) · [8. Giới hạn](#8-giới-hạn-đã-biết-known-gaps) · [9. Production](#9-lên-production)

---

## 1. Mô hình

```
        ┌─────────────────┐
        │  policy.yaml    │  ← NGUỒN CHÂN LÝ (luật, glob, layer). Dày tùy ý. Chỉ sửa ở đây.
        └────────┬────────┘
                 │ đọc
        ┌────────▼────────────────┐
        │ llmwiki-validate.py     │  ← LÕI vendor-neutral. exit 2=chặn(session) · 1=fail(repo) · 0=ok.
        │ modes: path/files/      │     Hỏng/thiếu policy ⇒ fail-open (0).
        │        claude-hook      │
        └───┬───────┬───────┬─────┘
   gọi/đọc │       │       │ gọi
   ┌───────▼─┐ ┌───▼────┐ ┌▼──────────────┐
   │ session │ │  repo  │ │ vendor config │
   │ adapters│ │  CI +  │ │ sinh từ policy│
   │ (hook)  │ │precommit│ │ (gen-converters)
   └─────────┘ └────────┘ └───────────────┘
```

Hai tầng (do `enforce_at` trong policy quyết định, KHÔNG hard-code):

| layer | khi nào | mode dùng | ai chạy |
|---|---|---|---|
| `session` | agent ĐỊNH ghi | `path`, `claude-hook` | hook/plugin của vendor → gọi lõi |
| `repo` | lúc commit / PR | `files` | pre-commit (local) + CI (server) |

Ví dụ: `no_write_raw` `enforce_at: [session]` → agent bị chặn ghi `raw/`, nhưng **con người vẫn commit `raw/` hợp lệ** (repo không áp). `require_origin` `[session, repo]` → áp cả hai.

---

## 2. Thành phần

| File | Vai trò |
|---|---|
| `policy.yaml` | Nguồn chân lý: danh sách rule (id, kind, enforce_at, glob…). |
| `bin/llmwiki-validate.py` | Lõi. Đọc policy, áp luật theo `kind`, lọc theo layer. |
| `gen-converters.py` | Đọc policy → sinh wiring mọi vendor vào `out/` (không commit; `.gitignore`). |
| `demo.sh` | 13 assertion happy-path. |
| `test-broad.sh` | 68 assertion: false-positive, normalize, bash, biên, files-mode, fail-open, GAPS, R5/R7/R9-nới. |
| `.github/workflows/harness.yml` | CI: job `selftest` (67 assertion) + `validate-content` (file .md đổi). |

---

## 3. `policy.yaml` (nguồn chân lý)

```yaml
version: 1
rules:
  <tên_rule>:
    id: R1                      # mã hiển thị trong thông báo
    name: no-write-raw          # nhãn
    kind: deny_write            # LOẠI luật → quyết định handler nào trong lõi áp
    statement: "..."            # câu giải thích (in ra khi vi phạm + đưa vào advisory rules)
    enforce_at: [session]       # [session] và/hoặc [repo] — lái tầng nào áp
    deny_write_globs:           # (kind=deny_write) các glob path bị cấm ghi
      - "**/raw/**"
      - "raw/**"
```

```yaml
  require_origin:
    id: R2
    kind: require_section       # LOẠI: file khớp glob phải chứa 1 heading
    enforce_at: [session, repo]
    require_section: "## Origin" # heading bắt buộc (khớp linh hoạt khoảng trắng, chặt biên)
    target_globs:               # chỉ áp cho file khớp các glob này
      - "**/wiki/concepts/**/*.md"
      - "**/wiki/entities/**/*.md"
      - "**/wiki/sources/**/*.md"
      - "**/wiki/draft/**/*.md"
    exclude_basenames: ["README.md", "_template.md", "index.md", "log.md"]
```

**Hai `kind` lõi hiện hỗ trợ:**
- `deny_write` — chặn ghi vào path khớp `deny_write_globs` (và lệnh bash ghi vào đó).
- `require_section` — file khớp `target_globs` (trừ `exclude_basenames`) phải chứa `require_section`.

Thêm **instance** luật mới cùng kind = chỉ sửa YAML. Thêm **kind** mới = thêm 1 handler trong lõi.

---

## 4. Lõi `llmwiki-validate.py`

### Modes & exit code

| Lệnh | Layer | Input | Exit |
|---|---|---|---|
| `path <FILE>` | session | 1 path ghi | **2** = chặn · 0 = ok |
| `claude-hook` | session | PreToolUse JSON qua stdin | **2** = chặn · 0 = ok |
| `files <F...>` | repo | nhiều path trên disk | **1** = có vi phạm · 0 = ok |

`--policy <P>` đổi đường policy (mặc định `../policy.yaml` cạnh lõi).

### Quy ước quan trọng
- **exit 2** cho session vì Claude PreToolUse coi exit 2 = "block tool", stderr hiện cho agent đọc.
- **exit 1** cho repo vì pre-commit/CI coi non-zero = fail (1 đủ; tách khỏi 2 để phân biệt nguồn).
- **fail-open (exit 0)** khi: thiếu pyyaml, không đọc được policy, JSON stdin hỏng, mode lạ → lỗi hạ tầng KHÔNG được chặn người dùng; sàn repo (CI) vẫn đỡ.

### `claude-hook` là "converter" của Claude
Đọc JSON PreToolUse thật của Claude (`{"tool_name","tool_input":{...}}`), map:
- `Write`/`Edit`/`MultiEdit` → kiểm `file_path` (deny_write) + `content` (require_section).
- `Bash` → kiểm `command` (deny_write bash).
Các vendor khác có converter tương tự (xem §6).

### Glob engine
`glob_to_regex` hỗ trợ `**` (xuyên thư mục), `*` (trong 1 segment), `?`. Vì khớp theo **segment** nên `coleslaw.md`/`draw.md`/`raws/`/`myraw/` **không** dính `**/raw/**` (đã test).

### Bash deny là soi BỀ MẶT
Chỉ bắt redirect `>`/`>>`, `tee`, `touch`, `sed -i<suffix> <file>`, và `cp/mv/rsync` đích `raw/`. **Không** bắt `python -c open(w)`, `rm`, `sed -i <script> <file>`. Đây là giới hạn có chủ đích (§8).

---

## 5. CI (sàn đảm bảo)

`.github/workflows/harness.yml`, chạy trên PR + push orca:

- **job `selftest`** — `pip install pyyaml` rồi chạy `demo.sh` + `test-broad.sh`. 67 assertion. Đây là cái "mỗi PR tự chạy". Xanh tất định.
- **job `validate-content`** — `git diff` base↔HEAD lấy file `.md` đổi → `llmwiki-validate.py files <files>` (layer=repo → chỉ `require_origin`). PR thêm/sửa wiki content thiếu `## Origin` sẽ **fail merge**.

Vì sao CI là sàn: rules advisory (AGENTS.md, .cursor/rules, steering) bị lờ ở mọi vendor non-Claude (verify 2026-06-25); session hook lệch nhau + có lỗ. **CI là nơi duy nhất nói "không" mà agent không sửa được khi merge.**

---

## 6. Cài đặt (luồng B0–B4)

### Nhanh nhất — 1 dòng, không cần clone repo
```bash
curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash
#   | bash -s -- --vendor claude,opencode   (ép vendor)   ·   | bash -s -- --clean   (cài mới = gỡ cũ rồi cài)
```
Chạy trong thư mục dự án; `bootstrap.sh` tải lõi từ GitHub rồi gọi `install.sh`. Dán được vào system prompt AI.

### Bên dưới làm gì (B0–B4)
```
B0. Đặt lõi vào repo (1 lần): harness/poc-vendor-neutral/{policy.yaml,bin/llmwiki-validate.py}
B1. DETECT vendor đang dùng (có .claude/ ? .cursor/ ? .opencode/ ? .kiro/ ?)
B2. Mỗi vendor → ghi WIRING native (idempotent). Sinh sẵn bằng: python3 gen-converters.py
B3. LUÔN cài tầng repo: .github/workflows/harness.yml + .pre-commit-config (gọi lõi)
B4. VERIFY: bash demo.sh && bash test-broad.sh
```

### Wiring từng vendor (sinh trong `out/`, copy vào đúng chỗ)

| Vendor | File sinh ra | Copy tới | Cơ chế |
|---|---|---|---|
| Claude | `out/claude/settings.snippet.json` | merge vào `.claude/settings.json` | PreToolUse hook → `claude-hook` (DENY) |
| opencode | `out/opencode/opencode.json` | `opencode.json` | `permission.edit:deny` theo glob (DENY native) |
| opencode (tùy) | `out/opencode/plugin/harness.js` | `.opencode/plugin/` | hook `tool.execute.before` gọi lõi (cho luật glob không tả được) |
| Antigravity | `out/antigravity/permissions.snippet.txt` | Permissions của project | Deny-rule `write_file(<glob>)` (DENY) |
| Cursor | `out/cursor/.cursor/rules/harness.mdc` | `.cursor/rules/` | advisory (NHẮC — Cursor không chặn ghi-file) |
| Codex | `out/codex/AGENTS.snippet.md` | `AGENTS.md` | advisory (NHẮC) |
| Kiro | `out/kiro/.kiro/steering/harness.md` | `.kiro/steering/` | advisory (NHẮC) |
| MỌI vendor | `out/ci/harness.yml`, `out/pre-commit-snippet.yaml` | `.github/workflows/`, `.pre-commit-config.yaml` | SÀN — gọi lõi `files` |

> **Quy tắc đọc bảng:** DENY = chặn thật trong phiên. NHẮC = chỉ gợi ý, hay bị lờ → dựa CI.
> Mỗi file sinh ra có header `GENERATED FROM policy.yaml` — đừng sửa tay.

### Chạy — 1 lệnh (khuyến nghị)
```bash
bash harness/poc-vendor-neutral/install.sh /dự-án            # tự làm trọn B0–B4 + verify
bash harness/poc-vendor-neutral/install.sh /dự-án --clean    # cài MỚI = gỡ cũ rồi cài
bash harness/poc-vendor-neutral/uninstall.sh /dự-án          # gỡ (giữ config khác của bạn, có .bak)
```
`install.sh` tự dò vendor → `gen-converters.py` → **merge** `.claude/settings.json` + `opencode.json` → thả CI + pre-commit → copy advisory Cursor/Kiro → verify. Idempotent. `--vendor a,b` để ép; `--no-verify` để bỏ test.

> ⚠️ KHÔNG nhầm với `harness/scripts/install-harness.sh` — đó là **harness chính (validators/hooks)**, khác PoC này.

### Hoặc thủ công (xem dưới mui xe)
```bash
python3 harness/poc-vendor-neutral/gen-converters.py   # chỉ sinh out/ rồi tự copy vào chỗ từng vendor
```

---

## 7. Mở rộng

- **Thêm luật** (cùng kind): sửa `policy.yaml` → `python3 gen-converters.py`. Mọi vendor + advisory + CI cập nhật theo, KHÔNG đụng code adapter.
- **Thêm kind luật mới**: thêm 1 handler `check_<kind>()` trong lõi + nhánh trong `mode_*`.
- **Thêm vendor mới**: thêm ~15 dòng trong `gen-converters.py` (1 hàm sinh wiring). Lõi không đổi.

---

## 8. Giới hạn đã biết (KNOWN GAPS)

Lõi session soi **bề mặt** lệnh bash → **không** bắt: `python3 -c "open('…/raw','w')"`, `rm …/raw/`, `sed -i <script> …/raw/`, ghi qua symlink. Đây KHÔNG phải bug — nó là lý do kiến trúc: **đảm bảo thật nằm ở CI** (và sandbox nếu cần threat đối kháng). Threat model hiện tại = agent hợp tác, nên CI là đủ; session hook chỉ là phản hồi nhanh. `test-broad.sh` mục C assert đúng các gap này để nếu hành vi đổi thì biết ngay.

---

## 9. Lên production

- Gộp `policy.yaml` này vào `harness/policy.yaml` (cùng tinh thần R1/R2; thêm `kind`+glob cho R5… nếu muốn).
- Đóng gói `bin/llmwiki-validate.py` thành **release pin version** (`validator_cli: "llmwiki-validate@x.y"`) → xoá copy editable + sync hash-3-mốc + bug `remote_synced`. Customize đẩy hết vào `policy.yaml`.
- Gọi `gen-converters.py` từ `install-harness.sh --vendor claude,opencode,…` (luồng B2/B3).
