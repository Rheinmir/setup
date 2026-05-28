---
name: new-project-setup
description: Deploy llmwiki từ đầu vào project mới — template pull, skill install, RTK, wiki seed, onboard
---

# Skill: new-project-setup

## When to use
Project chưa có `llmwiki/`. Hoặc reset từ đầu.

## Steps

**1. CHECK llmwiki tồn tại:**
```bash
test -d llmwiki && echo exists || echo missing
```
`exists` → hỏi user reset không. Reset = xóa `concepts/` + `entities/`, **GIỮ** `log.md` + `sources/`.

**2. Pull template + install skills:**
```bash
# INVOKE: sync-template
# sync-template tự pull từ rheinmir/setup@orca và install skills vào:
#   .claude/commands/           → Claude Code
#   ~/.agents/skills/*/SKILL.md → OpenCode / Antigravity
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

**5. Seed wiki:**
```bash
# Đọc README.md, package.json hoặc go.mod → project name + stack
```
- Tạo `llmwiki/wiki/sources/project-requirements.md` — frontmatter + `## Origin`
- Append `llmwiki/wiki/log.md`: `## YYYY-MM-DD — init — <project-name>`
- Tạo `llmwiki/wiki/index.md` — header + empty table

**6. INVOKE: onboard-codebase** → populate `concepts/` + `entities/` + lint.

## Rules
- Skill install: sync-template step 7 xử lý — không duplicate
- onboard-codebase includes lint — không gọi lint thêm
- RTK guard `uname -r | grep -qi microsoft` bắt buộc trước curl
