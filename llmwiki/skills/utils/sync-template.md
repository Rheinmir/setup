---
name: sync-template
description: Sync structural improvements between project and master template repo
---

# Skill: sync-template

## Purpose
Sync structural/template improvements between project and `https://github.com/Rheinmir/setup.git`.

## When to use
- **Upstream**: Improved template locally → save to Master.
- **Downstream**: Master has newer fixes → bring into project.

## FAST PATH — downstream 1 lệnh (< 1 giây, mặc định)

Downstream sync giờ là **1 script non-interactive**, KHÔNG hỏi từng bước, fetch song song:

```bash
python3 harness/scripts/sync-template.py            # pull NEW+UPDATE, giữ local-custom, cài skill ×3
python3 harness/scripts/sync-template.py --dry-run   # xem trước, không ghi
python3 harness/scripts/sync-template.py --strategy pull   # ghi đè cả CONFLICT bằng remote (backup .local-bak)
python3 harness/scripts/sync-template.py --json      # output máy đọc
```

Phân loại bằng hash 3 mốc — **disk ↔ R0 (remote tại lần sync trước, lưu ở `version.json:remote_synced`) ↔ remote hiện tại**:
- `NEW` (thiếu local) + `UPDATE` (remote mới hơn, local chưa đụng) → **tự PULL**.
- `KEPT` (mình đã custom, remote không mới hơn) → **giữ nguyên**, không hỏi.
- `CONFLICT` (cả hai cùng đổi) → mặc định **giữ local** + lưu bản remote ra `/tmp/sync-template-conflicts/` để diff; exit code 3.

Quy trình tự động trong script: fetch remote `version.json`+`manifest` → phân loại → tải song song → refresh `version.json` (fingerprint + `template_version` + `remote_synced`) → cài skill ra 3 chỗ (`.claude/commands/`, `~/.claude/skills/`, `~/.claude/commands/`).

**Khi nào CẦN can thiệp tay (chạy script trước, đọc report):**
- Report có `CONFLICT` và bạn muốn lấy remote → chạy lại `--strategy pull` (1 quyết định, không phải 3).
- Branch remote KHÁC `version.json:branch` → `--branch <tên>` (xem Step 2 để audit branch).
- Cấu trúc `skills/` cũ cần migrate (Step 3), hoặc cần upstream (đẩy lên) → dùng MANUAL STEPS bên dưới.

> ⚠ Bug đã fix: `health-check --update` đặt baseline = disk → sync KHÔNG phân biệt được "remote mới" vs "mình đã custom" → suýt ghi đè file custom. Script này dùng baseline riêng `remote_synced` (hash remote tại lần sync) nên phân biệt đúng. **Đừng** quay lại dùng `patterns` (disk) làm baseline phân loại.

---

## MANUAL STEPS (fallback — upstream, migrate cấu trúc cũ, hoặc debug)

### Step 0: Pre-flight — health-check (chẩn đoán trước khi sync)
Chạy `/health-check` (`python3 harness/scripts/health-check.py --root .`) để biết NÊN sync hướng nào:
- `NEEDS-SYNC` (behind/missing) → downstream (kéo về).
- `DRIFT` (đã sửa local) → upstream (đẩy lên) hoặc revert.
- `OK` → không cần sync, dừng.

### Step 1: Load Manifest
Read `.template-manifest.json` — inclusion list + remote URL.

### Step 2: Fetch & Branch Audit
- **CRITICAL**: List all remote branches: `gh api repos/<owner>/<repo>/branches`.
- Check commit date per branch — don't assume `master`/`main` is newest.
- Unclear → ask user which branch.
- Fetch via `gh api` + `curl` — no `git clone`.

### Step 3: Detect Old Structure Migration
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

### Step 4: Compare Manifest Files
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

### Step 5: Sync Plan
Show table. **STOP** → ask user: pull all / push all / specific files / direction per DIFF.

### Step 6: Execute
- **Downstream**: `mkdir -p` → `curl -sfL <url> -o <local_path>` → update `wiki/log.md`
- **Upstream**: commit + push via `gh`/`git`
- File by file — no `cp -R`

### Step 6a: OKF backfill *(sau MỌI downstream sync kéo template/skill mới)*
Template/skill mới có thể nâng định dạng wiki (vd chuẩn OKF v0.1). Sau khi pull, convert mọi file content cũ còn dùng pseudo-frontmatter dạng bold `**Type:**` sang YAML frontmatter để khỏi vướng R9:
```bash
python3 harness/scripts/okf-check.py --check      # exit 3 = có file chưa đạt OKF
python3 harness/scripts/okf-check.py --migrate    # convert bold → YAML (chỉ THÊM frontmatter, giữ body/## Origin)
```
- Idempotent — file đã có `---` frontmatter được bỏ qua. Reserved (index/log/README/decisions/_template…) tự miễn.
- Sau migrate: chạy lại `--check` đến khi `DAT CHUAN OKF v0.1`, rồi cập nhật index/log như mọi thay đổi wiki.

### Step 6b: Refresh version fingerprint *(sau MỌI downstream sync)*
Nội dung pattern vừa đổi → cập nhật lại `harness/version.json` để health-check khỏi báo DRIFT giả:
```bash
python3 harness/scripts/health-check.py --update   # KHÔNG --bump ở project con
```
- `--bump major|minor|patch` CHỈ chạy ở repo template `Rheinmir/setup` khi PHÁT HÀNH version pattern mới.
- Upstream sync ở repo template: sau khi push, chạy `--update --bump <part>` rồi commit `harness/version.json`.

### Step 7: Install as Native Skills *(runs every downstream sync)*

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

### Step 8: Verify & Finalize
```bash
for name in <skill-list>; do
  [ -f ".claude/commands/$name.md" ]          && echo "✓ proj  $name" || echo "✗ proj  $name"
  [ -f "$HOME/.claude/skills/$name/SKILL.md" ] && echo "✓ global $name" || echo "✗ global $name"
done
```
Fix `✗` before done. No restart needed.

## Agent Compatibility

| Agent | Run? | Reason |
|-------|------|--------|
| Claude Code | Yes | Full tool access |
| OpenCode | Yes | Full tool access |
| Antigravity | No | Sandbox blocks file/command tools |

## Rules
- NEVER sync `.env`, credentials, business docs.
- ALWAYS audit remote branches — non-default may be newest.
- ALWAYS show diff for `[CONFLICT]` → wait for instruction.
- NEVER `cp -R` — file by file.
- **Step 3 every sync** — detect old `skills/`, offer migrate.
- **Step 7 every downstream sync** — install all 3 Claude Code locations.
- `[NEW]`: add to manifest BEFORE upstream commit.
- `[MISSING]`: add to manifest AFTER downstream copy.
- Frontmatter: `name:` + `description:` for skills; `description:` only for slash commands.
- Skip `README.md`, `index.md`, `log.md`, no-Purpose/Steps files.
