---
name: sync-template
description: Sync structural improvements between project and master template repo
---

# Skill: sync-template

## Purpose
Synchronize structural and template improvements between the current project and the master template repository `https://github.com/Rheinmir/setup.git`.

## When to use
- **Upstream**: After improving a template file locally and wanting to save it to Master.
- **Downstream**: When the Master repo has newer features or fixes that you want to bring into the current project.

## Steps

### Step 1: Load Manifest
Read `.template-manifest.json` for the inclusion list and remote URL.

### Step 2: Fetch Master Repo & Branch Audit
- **CRITICAL**: Always list all remote branches via `gh api repos/<owner>/<repo>/branches`.
- Check latest commit date on each branch — do not assume `master`/`main` is most up-to-date.
- Ask user which branch to use if unclear.
- Use `gh api` + `curl` to fetch files directly — no need to `git clone`.

### Step 3: Detect Old Structure Migration
Before comparing, check if the project has an **old `skills/` layout** that needs migrating to the new `llmwiki/` structure:

```bash
# Signs of old structure:
[ -d "skills/" ] && [ ! -d "llmwiki/skills/" ]   # old only
[ -d "skills/" ] && [ -d "llmwiki/skills/" ]       # both exist → migration in progress
```

**If old `skills/` exists alongside new `llmwiki/skills/`:**
1. List files in `skills/` (flat .md + subdirs like `dev-loop/`, `wiki-loop/`, etc.)
2. Map old → new paths:
   - `skills/dev-loop/*.md`   → `llmwiki/skills/dev-loop/*.md`
   - `skills/wiki-loop/*.md`  → `llmwiki/skills/wiki-loop/*.md`
   - `skills/orchestrate/*.md`→ `llmwiki/skills/orchestrate/*.md`
   - `skills/utils/*.md`      → `llmwiki/skills/utils/*.md`
   - `skills/*.md` (flat)     → already covered by subdirs, skip duplicates
3. For each file: if content matches `llmwiki/` counterpart → old is stale, safe to remove.
4. Present migration table and ask user to confirm before deleting old `skills/`.

### Step 4: Compare Manifest Files
Run `diff` between local and remote for each file in `includes`:

```bash
BASE="https://raw.githubusercontent.com/<owner>/<repo>/<branch>"
for file in <includes>; do
  http_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/$file")
  # SAME / DIFF / MISSING / NEW / ABSENT
done
```

Status legend:
- `SAME` — identical, skip
- `DIFF` — both exist, content differs
- `MISSING` — exists on remote, not local → candidate for downstream
- `NEW` — exists locally, not on remote → candidate for upstream
- `ABSENT` — neither side has it

### Step 5: Sync Plan Presentation
Present table. **STOP and ask** user for direction before executing:
- Pull all / Push all / Specific files
- Which direction for each DIFF file

### Step 6: Execution
- **Downstream**: `mkdir -p` target dir → `curl -sfL <url> -o <local_path>`
- **Upstream**: Commit + push via `gh` or `git`
- Copy file by file — never `cp -R`
- After downstream: update `wiki/log.md`

### Step 7: Install as Native Skills *(runs every downstream sync)*

Collect all skill files synced (files under `llmwiki/skills/` in manifest).
Skip: `README.md`, `index.md`, `log.md`, files without `## Purpose` or `## Steps`.

**A. Project-level** (`.claude/commands/` inside project — for this repo only):
```bash
mkdir -p .claude/commands/
# Add description: frontmatter if missing, then copy
printf -- "---\ndescription: %s\n---\n\n" "$desc" | cat - <src> > .claude/commands/<name>.md
```

**B. Global user-level** (`~/.claude/skills/<name>/SKILL.md` — toàn máy, mọi project):
```bash
mkdir -p ~/.claude/skills/<name>/
# Requires name: + description: frontmatter
printf -- "---\nname: %s\ndescription: %s\n---\n\n" "$name" "$desc" | cat - <src> > ~/.claude/skills/<name>/SKILL.md
```

**C. Global slash command** (`~/.claude/commands/<name>.md` — autocomplete `/name`):
```bash
printf -- "---\ndescription: %s\n---\n\n" "$desc" | cat - <src> > ~/.claude/commands/<name>.md
```

Luôn install cả 3 cho Claude Code. Report bảng sau khi xong:

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
Fix any `✗` before declaring done. Claude Code picks up skills immediately — no restart needed.

## Agent Compatibility

| Agent | Có thể chạy? | Lý do |
|-------|-------------|-------|
| Claude Code CLI | Có | Full tool access |
| OpenCode | Có | Full tool access |
| Antigravity CLI | Không | Sandbox chặn file/command tools |

## Rules
- NEVER sync `.env`, credentials, business-specific docs.
- ALWAYS audit remote branches before syncing — newer content may be on a non-default branch.
- ALWAYS show diff for `[CONFLICT]` files and wait for user instruction.
- NEVER bulk copy (`cp -R`) — copy file by file per manifest.
- **Migration check (Step 3) runs on every sync** — detect old `skills/` layout and offer to migrate.
- **Step 7 runs on every downstream sync** — install to all 3 Claude Code locations.
- Use `impact-check` if template change affects shared logic in `skills/`.
- `[NEW]` files: add to `.template-manifest.json` includes BEFORE upstream commit.
- `[MISSING]` files: add to `.template-manifest.json` includes AFTER downstream copy.
- Native skill frontmatter needs `name:` + `description:`. Slash command needs only `description:`.
- Copy file by file — never `cp -R`.
- Skip `README.md`, `index.md`, `log.md`, files without `## Purpose` or `## Steps`.
