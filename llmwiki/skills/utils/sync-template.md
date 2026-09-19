---
name: sync-template
disable-model-invocation: true
description: Sync structural improvements between project and master template repo
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: sync-template

## WHAT

### Purpose và context
- **Purpose:** Sync structural/template improvements between project and `https://github.com/Rheinmir/setup.git`.
- **Trigger (when to use):**
  - **Upstream**: Improved template locally → save to Master.
  - **Downstream**: Master has newer fixes → bring into project.
- **Non-goals:** không sync `.env`, credentials, business docs; không tự `--strategy pull` để rút ngắn thời gian; không `git clone` template; không tự kích hoạt (`disable-model-invocation: true`); Antigravity không chạy được skill này (sandbox chặn tool).

### Mental model
Downstream mặc định: `version.json + manifest remote → phân loại hash 3 mốc (disk ↔ R0 remote_synced ↔ remote hiện tại) → NEW/UPDATE tự PULL · KEPT giữ · CONFLICT giữ local + lưu bản remote → OKF backfill → fingerprint → cài skill 3 chỗ → verify 3 vị trí → log`. Upstream / migrate / debug đi MANUAL STEPS 0–8 với điểm STOP hỏi user ở Step 5.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | hướng sync | có | downstream (mặc định, FAST PATH) hoặc upstream (MANUAL) |
| In | `.template-manifest.json` + `harness/version.json` | có | inclusion list, remote URL, `branch`, `remote_synced` |
| In | `--branch`, `--strategy pull`, `--dry-run`, `--json` | không | đổi branch, lấy remote cho CONFLICT, xem trước, output máy đọc |
| In | quyết định user | khi CONFLICT hoặc Step 5 | lấy remote hay giữ local; pull/push file nào |
| Out | file template đã sync + OKF backfill | có | file wiki cũ convert bold→YAML |
| Out | `harness/version.json` refresh | có | fingerprint sau OKF + `template_version` + `remote_synced` |
| Out | skill cài ở `.claude/commands/`, `~/.claude/skills/`, `~/.claude/commands/` | downstream | verify 3 vị trí |
| Out | report + exit code | có | 0 sạch, 1 lỗi tải/OKF/verify, 3 CONFLICT cần quyết |
| Out | dòng `wiki/log.md` + draft output report | có | script tự ghi log khi `--full` |

### Rules và capabilities
- RULE-01 (MUST): NEVER sync `.env`, credentials, business docs.
- RULE-02 (MUST): ALWAYS audit remote branches — non-default may be newest.
- RULE-03 (MUST): ALWAYS show diff for `[CONFLICT]` → wait for instruction.
- RULE-04 (MUST): NEVER `cp -R` — file by file.
- RULE-05 (MUST): **Step 3 every sync** — detect old `skills/`, offer migrate.
- RULE-06 (MUST): **Step 7 every downstream sync** — install all 3 Claude Code locations.
- RULE-07 (MUST): `[NEW]`: add to manifest BEFORE upstream commit.
- RULE-08 (MUST): `[MISSING]`: add to manifest AFTER downstream copy.
- RULE-09 (MUST): Frontmatter: `name:` + `description:` for skills; `description:` only for slash commands.
- RULE-10 (MUST): Skip `README.md`, `index.md`, `log.md`, no-Purpose/Steps files.
- Capabilities: đọc remote template (HTTP/GitHub API); ghi file trong project + thư mục skill/command cấp user; đẩy lên remote template khi upstream (chỉ sau duyệt).

### Failure boundaries
- CONFLICT (cả hai cùng đổi) → giữ local, lưu bản remote ra `/tmp/sync-template-conflicts/`, exit 3 → **clarify** với user.
- Lỗi tải / OKF / verify → exit 1 → **failed**, sửa `✗` trước khi xong.
- Branch remote không rõ cái nào mới nhất → **clarify**, hỏi user branch nào.
- health-check `OK` → không cần sync, dừng (**succeeded** no-op).
- Old `skills/` layout → đề xuất migrate, **confirm** trước khi xoá.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | judgment | yêu cầu | Chọn đường: downstream thường → FAST PATH `--full`; upstream, migrate cấu trúc cũ, debug → MANUAL (B01) | đường đi | — |
| W02 | effect | manifest, remote | `python3 harness/scripts/sync-template.py --full` MỘT lần (sync + OKF + fingerprint + cài 3 chỗ + verify + log) | report | exit 1 → failed; exit 3 → W03 |
| W03 | judgment | report | Đọc report; CONFLICT muốn lấy remote → chạy lại `--strategy pull`; branch khác → `--branch` | quyết định | không rõ → hỏi user |
| W04 | deterministic | report | Không gọi thêm okf-check, health-check, vòng verify, không tự sửa log | báo cáo cho user | — |
| W05 | effect | kết quả | Output Report draft | draft + index + log | 0 artefact → skip |

Chi tiết từng bước (nguồn chân lý cho W01–W05 và nhánh MANUAL):

#### FAST PATH — downstream 1 lệnh `--full` (< 30s, mặc định)

Downstream sync là **1 script non-interactive tự chứa**. Gọi **1 lần** với `--full` → mọi bước
hậu-sync (Step 6a/6b/8 + ghi log) chạy trong CÙNG process. Agent đọc 1 report rồi báo cáo —
KHÔNG lặp lại lệnh riêng. Bench repo này: full steady-state 0.27s · full pull+install+verify 0.76s
(`harness/metrics/sync-template-bench.json`).

```bash
python3 harness/scripts/sync-template.py --full        # ⭐ MẶC ĐỊNH: sync + OKF backfill + fingerprint + verify ×3 + ghi log, 1 process
python3 harness/scripts/sync-template.py --full --json  # như trên, output máy đọc (đọc okf_migrated / verify_bad)
python3 harness/scripts/sync-template.py --dry-run      # xem trước, không ghi (kèm --full để xem OKF sẽ migrate gì)
python3 harness/scripts/sync-template.py --strategy pull # ghi đè cả CONFLICT bằng remote (backup .local-bak)
```

> Chạy `--full` **1 lần là xong** — đừng gọi tiếp `okf-check`, `health-check --update`, vòng verify,
> hay tự `Edit` log.md (script đã làm hết). Đó là cách giữ skill dưới 30s: nút thắt cũ là **số
> round-trip agent** quanh các bước hậu-sync, không phải CPU. Không cờ `--full` = hành vi cũ y nguyên.

Phân loại bằng hash 3 mốc — **disk ↔ R0 (remote tại lần sync trước, lưu ở `version.json:remote_synced`) ↔ remote hiện tại**:
- `NEW` (thiếu local) + `UPDATE` (remote mới hơn, local chưa đụng) → **tự PULL**.
- `KEPT` (mình đã custom, remote không mới hơn) → **giữ nguyên**, không hỏi.
- `CONFLICT` (cả hai cùng đổi) → mặc định **giữ local** + lưu bản remote ra `/tmp/sync-template-conflicts/` để diff; exit code 3. **Không bao giờ** tự `--strategy pull` để rút ngắn thời gian.

Quy trình tự động trong script (`--full`): fetch remote `version.json`+`manifest` → phân loại → tải song song → **OKF backfill in-process** (migrate bold→YAML, idempotent) → refresh `version.json` (fingerprint SAU OKF + `template_version` + `remote_synced`) → cài skill ra 3 chỗ (`.claude/commands/`, `~/.claude/skills/`, `~/.claude/commands/`) → **self-verify 3 vị trí** → **append `wiki/log.md`**. Exit: 0 sạch · 1 lỗi tải/OKF/verify · 3 CONFLICT cần quyết.

**Khi nào CẦN can thiệp tay (chạy script trước, đọc report):**
- Report có `CONFLICT` và bạn muốn lấy remote → chạy lại `--strategy pull` (1 quyết định, không phải 3).
- Branch remote KHÁC `version.json:branch` → `--branch <tên>` (xem Step 2 để audit branch).
- Cấu trúc `skills/` cũ cần migrate (Step 3), hoặc cần upstream (đẩy lên) → dùng MANUAL STEPS bên dưới.

> ⚠ Bug đã fix: `health-check --update` đặt baseline = disk → sync KHÔNG phân biệt được "remote mới" vs "mình đã custom" → suýt ghi đè file custom. Script này dùng baseline riêng `remote_synced` (hash remote tại lần sync) nên phân biệt đúng. **Đừng** quay lại dùng `patterns` (disk) làm baseline phân loại.

---

#### MANUAL STEPS (fallback — upstream, migrate cấu trúc cũ, hoặc debug)

##### Step 0: Pre-flight — health-check (chẩn đoán trước khi sync)
Chạy `/health-check` (`python3 harness/scripts/health-check.py --root .`) để biết NÊN sync hướng nào:
- `NEEDS-SYNC` (behind/missing) → downstream (kéo về).
- `DRIFT` (đã sửa local) → upstream (đẩy lên) hoặc revert.
- `OK` → không cần sync, dừng.

##### Step 1: Load Manifest
Read `.template-manifest.json` — inclusion list + remote URL.

##### Step 2: Fetch & Branch Audit
- **CRITICAL**: List all remote branches: `gh api repos/<owner>/<repo>/branches`.
- Check commit date per branch — don't assume `master`/`main` is newest.
- Unclear → ask user which branch.
- Fetch via `gh api` + `curl` — no `git clone`.

##### Step 3: Detect Old Structure Migration
Check for **old `skills/` layout** needing migration to `llmwiki/`:

```bash
# Signs of old structure:
[ -d "skills/" ] && [ ! -d "llmwiki/skills/" ]   # old only
[ -d "skills/" ] && [ -d "llmwiki/skills/" ]       # both exist → migration in progress
```

**Old `skills/` + new `llmwiki/skills/` coexist:**
1. List `skills/` (flat .md + subdirs: `dev-loop/`, `wiki-loop/`, etc.)
2. Map old → new:
   - `skills/dev-loop/*.md`   → `llmwiki/skills/dev-loop/*.md`
   - `skills/wiki-loop/*.md`  → `llmwiki/skills/wiki-loop/*.md`
   - `skills/orchestrate/*.md`→ `llmwiki/skills/orchestrate/*.md`
   - `skills/utils/*.md`      → `llmwiki/skills/utils/*.md`
   - `skills/*.md` (flat)     → already covered by subdirs, skip duplicates
3. Content matches → old stale, safe to remove.
4. Show migration table → confirm before delete.

##### Step 4: Compare Manifest Files
`diff` local vs remote for each file in `includes`:

```bash
BASE="https://raw.githubusercontent.com/<owner>/<repo>/<branch>"
for file in <includes>; do
  http_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/$file")
  # SAME / DIFF / MISSING / NEW / ABSENT
done
```

Status:
- `SAME` — skip
- `DIFF` — content differs
- `MISSING` — remote only → downstream candidate
- `NEW` — local only → upstream candidate
- `ABSENT` — neither

##### Step 5: Sync Plan
Show table. **STOP** → ask user: pull all / push all / specific files / direction per DIFF.

##### Step 6: Execute
- **Downstream**: `mkdir -p` → `curl -sfL <url> -o <local_path>` → update `wiki/log.md`
- **Upstream**: commit + push via `gh`/`git`
- File by file — no `cp -R`

> **Step 6a/6b/8 đã GỘP vào `--full`.** Nếu bạn chạy FAST PATH `--full` thì BỎ QUA 6a/6b/8 —
> script đã OKF-backfill + refresh fingerprint + verify + ghi log trong process. Các bước dưới chỉ
> dùng khi chạy MANUAL (debug / upstream / migrate cấu trúc cũ), không phải sau `--full`.

##### Step 6a: OKF backfill *(MANUAL — `--full` đã làm)*
Template/skill mới có thể nâng định dạng wiki (vd chuẩn OKF v0.1). Sau khi pull, convert mọi file content cũ còn dùng pseudo-frontmatter dạng bold `**Type:**` sang YAML frontmatter để khỏi vướng R9:
```bash
python3 harness/scripts/okf-check.py --check      # exit 3 = có file chưa đạt OKF
python3 harness/scripts/okf-check.py --migrate    # convert bold → YAML (chỉ THÊM frontmatter, giữ body/## Origin)
```
- Idempotent — file đã có `---` frontmatter được bỏ qua. Reserved (index/log/README/decisions/_template…) tự miễn.
- Sau migrate: chạy lại `--check` đến khi `DAT CHUAN OKF v0.1`, rồi cập nhật index/log như mọi thay đổi wiki.

##### Step 6b: Refresh version fingerprint *(MANUAL — `--full` đã làm)*
Nội dung pattern vừa đổi → cập nhật lại `harness/version.json` để health-check khỏi báo DRIFT giả:
```bash
python3 harness/scripts/health-check.py --update   # KHÔNG --bump ở project con
```
- `--bump major|minor|patch` CHỈ chạy ở repo template `Rheinmir/setup` khi PHÁT HÀNH version pattern mới.
- Upstream sync ở repo template: sau khi push, chạy `--update --bump <part>` rồi commit `harness/version.json`.

##### Step 7: Install as Native Skills *(runs every downstream sync)*

Collect skill files synced (under `llmwiki/skills/` in manifest). Skip: `README.md`, `index.md`, `log.md`, no-`## Purpose`/`## Steps` files.

**A. Project-level** (`.claude/commands/` — this repo):
```bash
mkdir -p .claude/commands/
# Add description: frontmatter if missing, then copy
printf -- "---\ndescription: %s\n---\n\n" "$desc" | cat - <src> > .claude/commands/<name>.md
```

**B. Global user-level** (`~/.claude/skills/<name>/SKILL.md` — all projects):
```bash
mkdir -p ~/.claude/skills/<name>/
# Requires name: + description: frontmatter
printf -- "---\nname: %s\ndescription: %s\n---\n\n" "$name" "$desc" | cat - <src> > ~/.claude/skills/<name>/SKILL.md
```

**C. Global slash command** (`~/.claude/commands/<name>.md`):
```bash
printf -- "---\ndescription: %s\n---\n\n" "$desc" | cat - <src> > ~/.claude/commands/<name>.md
```

Install cả 3. Report:

```
| Skill          | Project .claude/commands/ | ~/.claude/skills/ | ~/.claude/commands/ |
|----------------|---------------------------|-------------------|---------------------|
| propose        | ✓                         | ✓                 | ✓                   |
| ingest         | ✓                         | ✓                 | ✓                   |
| ...            | ...                       | ...               | ...                 |
```

##### Step 8: Verify & Finalize
```bash
for name in <skill-list>; do
  [ -f ".claude/commands/$name.md" ]          && echo "✓ proj  $name" || echo "✗ proj  $name"
  [ -f "$HOME/.claude/skills/$name/SKILL.md" ] && echo "✓ global $name" || echo "✗ global $name"
done
```
Fix `✗` before done. No restart needed.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | cần upstream, migrate cấu trúc `skills/` cũ, hoặc debug | chạy MANUAL STEPS 0–8, STOP hỏi user ở Step 5 | downstream thường → FAST PATH | W05 |
| B02 | recovery | exit 3 CONFLICT và user chọn lấy remote | chạy lại `--strategy pull` (ghi đè, backup `.local-bak`) | user giữ local → không làm gì | W04 |
| B03 | conditional_required | branch remote khác `version.json:branch` | `--branch <tên>` sau khi audit branch (Step 2) | — | W02 |
| B04 | user_optional | muốn xem trước | `--dry-run` (kèm `--full` để xem OKF sẽ migrate gì) | — | W02 |
| B05 | conditional_required | phát hiện old `skills/` layout (Step 3) | hiện bảng migration, confirm rồi mới xoá | user từ chối → giữ | W05 |

### Validation và stopping
Tất định: exit code script (0/1/3), self-verify 3 vị trí cài, `okf-check.py --check` ra `DAT CHUAN OKF v0.1` (MANUAL), vòng `[ -f … ]` Step 8 không còn `✗`. Dừng sau MỘT lần `--full` khi exit 0; exit 3 dừng chờ user quyết; MANUAL dừng ở Step 5 chờ duyệt.

### Examples
- **Positive:** project con, Master có fix mới → `python3 harness/scripts/sync-template.py --full` → 2 UPDATE tự PULL, 1 KEPT giữ nguyên, OKF migrate 3 file, verify 3 vị trí ✓, exit 0 trong < 1s → báo report, không chạy thêm lệnh nào.
- **Boundary/failure:** file `llmwiki/skills/dev-loop/ship.md` sửa ở cả local và remote → CONFLICT, giữ local, bản remote ở `/tmp/sync-template-conflicts/`, exit 3 → hiện diff, chờ user; không tự `--strategy pull`.

### Reference — Agent Compatibility

| Agent | Run? | Reason |
|-------|------|--------|
| Claude Code | Yes | Full tool access |
| OpenCode | Yes | Full tool access |
| Antigravity | No | Sandbox blocks file/command tools |

### Delivery — Output Report

After all main skill tasks complete, write a propose draft to the wiki.

#### Steps

**1. Build the filename:**
- Format: `DDMMYY-<ten>.md`
- `DDMMYY` = today (e.g., `020626` for 2 June 2026)
- `<ten>` = 2–4 kebab-case words summarising what was done (e.g., `landing-page-coteccons`, `brand-kit-fintech`, `ingest-auth-spec`)

**2. Write** `llmwiki/wiki/sources/draft/DDMMYY-<ten>.md`:

```
---
type: draft
title: "DDMMYY-<ten>"
status: proposed
tags: [<skill-name>, output-report]
timestamp: YYYY-MM-DD
---

# DDMMYY-<ten>
**Type:** draft
**Status:** proposed
**Tags:** <skill-name>, output-report
**Proposed:** YYYY-MM-DD

## What
<One sentence — what this skill invocation produced or decided>

## Output
<Key artefacts, files created/modified, or decisions made>

## Files
| File | Action |
|------|--------|
| `path/to/file` | created / modified |

## Notes
- Invoked via: `/<skill-name>` skill

## Origin
- **Draft:** `wiki/sources/draft/DDMMYY-<ten>.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
```

**3. Update wiki index & log:**
- `llmwiki/wiki/index.md` — append one row: `| [DDMMYY-<ten>](sources/draft/DDMMYY-<ten>.md) | draft | YYYY-MM-DD |`
- `llmwiki/wiki/log.md` — append: `## YYYY-MM-DD — <skill-name> — <ten>`

> Skip only when the skill produces zero artefacts and zero decisions (e.g., a pure display mode like `/caveman-stats`).

