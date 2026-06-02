---
name: new-project-setup
description: Deploy llmwiki từ đầu vào project mới — template pull, skill install, RTK, Caveman, wiki seed, onboard
---

# Skill: new-project-setup

## When to use
Project mới hoàn toàn chưa có `llmwiki/`, hoặc cần reset lại từ đầu.

## Steps

**1. CHECK — llmwiki đã tồn tại chưa?**
```bash
test -d llmwiki && echo exists || echo missing
```
Nếu `exists`: hỏi user có muốn reset không.
Reset = xóa `llmwiki/wiki/concepts/` và `llmwiki/wiki/entities/` — **GIỮ** `log.md` và `sources/`.

**2. Pull template + install skills:**
```bash
# INVOKE: sync-template
# sync-template tự pull từ rheinmir/setup@orca và install skills vào:
#   .claude/commands/           ← Claude Code
#   ~/.agents/skills/*/SKILL.md ← OpenCode / Antigravity
#   ~/.kiro/skills/*/SKILL.md   ← Kiro CLI
```

**3. Init wiki folder structure:**
```bash
mkdir -p llmwiki/wiki/{concepts,entities,sources/draft} llmwiki/{skills,raw}
touch llmwiki/wiki/index.md llmwiki/wiki/log.md llmwiki/raw/.gitkeep
```

**4. RTK token proxy (WSL only):**
```bash
# Guard — chỉ chạy trong WSL:
uname -r | grep -qi microsoft || { echo "RTK install: WSL only — skip"; exit 0; }

# CHECK đã cài chưa:
rtk --version 2>/dev/null || {
  curl -fsSL https://github.com/rtk-ai/rtk/releases/latest/download/rtk-x86_64-unknown-linux-musl.tar.gz \
    | tar xz -C /usr/local/bin
}

# Init global config + patch ~/.claude/settings.json:
rtk init -g

# Verify hook:
grep -q "rtk hook claude" ~/.claude/settings.json && echo "RTK hooked" || echo "MANUAL: add rtk hook to settings.json"
```

**4.b Caveman Setup:**
```bash
# Cài đặt caveman cho mọi agent phát hiện trên máy:
# Windows (PowerShell):
irm https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.ps1 | iex
# macOS / Linux / WSL (Bash):
curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash
```

**5. Seed wiki với project info:**
```bash
# Đọc README.md, package.json hoặc go.mod để lấy project name + stack
```
- Tạo `llmwiki/wiki/sources/project-requirements.md` với frontmatter + `## Origin`
- Append vào `llmwiki/wiki/log.md`: `## YYYY-MM-DD — init — <project-name>`
- Tạo `llmwiki/wiki/index.md` với header + empty table

**6. INVOKE: onboard-codebase**
Phân tích sâu codebase → populate `concepts/` + `entities/` + chạy lint.

## Rules
- Không duplicate skill install — sync-template step 7 xử lý toàn bộ
- onboard-codebase đã bao gồm lint — không gọi lint thêm sau step 6
- RTK guard `uname -r | grep -qi microsoft` là bắt buộc trước khi curl


---

## Output Report

After all main skill tasks complete, write a propose draft to the wiki.

### Steps

**1. Build the filename:**
- Format: `DDMMYY-<ten>.md`
- `DDMMYY` = today (e.g., `020626` for 2 June 2026)
- `<ten>` = 2–4 kebab-case words summarising what was done (e.g., `landing-page-coteccons`, `brand-kit-fintech`, `ingest-auth-spec`)

**2. Write** `llmwiki/wiki/sources/draft/DDMMYY-<ten>.md`:

```
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