---
name: orca-dispatch-reference
description: Reference for Antigravity/OpenCode dispatch, skill installation, AgentMemory, RTK token proxy — NOT a loop skill
---

# Orca Dispatch Reference

> Reference doc, not a skill. Do not invoke in loop.

## OpenCode — Default Model

**Default**: `opencode/big-pickle` — $0.00, non-interactive.

```bash
# Non-interactive task dispatch (default pattern):
# ⚠ KHÔNG dùng --dangerously-skip-permissions khi dispatch từ Claude Code — auto-mode classifier sẽ DENY (bài học 120626)
opencode run -m opencode/big-pickle --dir "<project-path>" "<task>"

# Example:
opencode run -m opencode/big-pickle --dir "C:\Users\olive\orca\workspaces\home-spotify\m" "List all TODO comments in backend/"
```

**Model tiers** (fallback if big-pickle fails):
| Model | Cost | Dùng khi |
|-------|------|---------|
| `opencode/big-pickle` | $0.00 | Default — all tasks |
| `google/gemini-2.5-flash` | ~$0.075/1M | big-pickle insufficient context |
| `opencode/deepseek-v4-flash-free` | $0.00 | Alternative free |

---

## Antigravity (agy)

**Binary**: `agy` — `%LOCALAPPDATA%\agy\bin\agy.exe`. NOT `antigravity`, NOT `~/.local/bin/agy`.

```bash
# CHECK trước khi dùng:
agy --version
```

**Hook**: Orca v1.4.21 fix Windows hook quoting — no manual `antigravity-hook.cmd` edit.

**Dispatch status** (post v1.4.21):

| Method | Status |
|--------|--------|
| `dispatch --inject` | retest |
| `terminal send` | OK |
| Tool calls | OK |
| `worker_done` callback | retest |

**Fallback if `--inject` fails:**
```bash
orca terminal send --title "Antigravity" --text "<task>"
orca terminal wait --for tui-idle
orca terminal read --title "Antigravity"
```

## Skill Installation per Agent CLI

Skills: `llmwiki/skills/<category>/<name>.md`.

### Claude Code
```bash
# CHECK:
ls .claude/commands/

# Install:
cp llmwiki/skills/dev-loop/propose.md .claude/commands/propose.md
```

### OpenCode / Antigravity
```bash
# CHECK:
ls ~/.agents/skills/

# Install (skill = folder with SKILL.md):
mkdir -p ~/.agents/skills/propose/
cp llmwiki/skills/dev-loop/propose.md ~/.agents/skills/propose/SKILL.md
# Restart OpenCode after install.
```

## AgentMemory

```bash
BASE="https://agentmemory.giatbh.io.vn"
TOKEN="${AGENTMEMORY_TOKEN}"

# CHECK health:
curl -sk -H "Authorization: Bearer $TOKEN" "$BASE/agentmemory/health"

# Ghi:
curl -sk -X POST "$BASE/agentmemory/remember" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"content":"<text>","category":"fact|preference|decision|context"}'

# Tìm:
curl -sk -H "Authorization: Bearer $TOKEN" "$BASE/agentmemory/search?query=<keyword>"
```

## RTK — Token Proxy

RTK (Rust Token Killer): auto-filter CLI output before context — 60-90% token reduction.

```bash
# CHECK:
rtk --version

# Install hook (once):
rtk hooks install --agent claude
rtk hooks install --agent opencode
# All agent commands auto-route through RTK.

# Savings:
rtk stats --today
```

> Xem [[concepts/RTK]] để biết chi tiết.

---

## Output Report

After all main skill tasks complete, write a propose draft to the wiki.

### Steps

**1. Build the filename:**
- Format: `DDMMYY-<ten>.md`
- `DDMMYY` = today (e.g., `020626` for 2 June 2026)
- `<ten>` = 2–4 kebab-case words summarising what was done (e.g., `landing-page-coteccons`, `brand-kit-fintech`, `ingest-auth-spec`)

**2. Write** `llmwiki/wiki/draft/orca/DDMMYY-<ten>.md`:

```
# DDMMYY-<ten>
**Type:** draft
**Status:** proposed
**Tags:** <skill-name>, output-report
**Proposed:** YYYY-MM-DD

## Agent Task Assignment
| Task | Agent | Status |
|------|-------|--------|
| <mô tả task 1> | <tên agent> | pending / in-progress / done |
| <mô tả task 2> | <tên agent> | pending / in-progress / done |

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
- **Draft:** `wiki/draft/orca/DDMMYY-<ten>.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
```

**3. Update wiki index & log:**
- `llmwiki/wiki/index.md` — append one row: `| [DDMMYY-<ten>](draft/orca/DDMMYY-<ten>.md) | draft | YYYY-MM-DD |`
- `llmwiki/wiki/log.md` — append: `## YYYY-MM-DD — <skill-name> — <ten>`

**4. Update agent statuses & sync push — BẮT BUỘC, không bỏ qua:**
- Mở lại file `llmwiki/wiki/draft/orca/DDMMYY-<ten>.md`
- Cập nhật cột **Status** trong bảng `## Agent Task Assignment` theo trạng thái thực tế của từng agent (pending → in-progress → done)
- Clone `rheinmir/setup` nhánh `orca`, copy các skill file đã sửa, rồi push ngược lên:
  ```bash
  git clone git@github.com:rheinmir/setup.git /tmp/rheinmir-setup-sync -b orca --depth 1
  cp /path/to/skill.md /tmp/rheinmir-setup-sync/skills/<skill-name>/SKILL.md
  cd /tmp/rheinmir-setup-sync
  git add .
  git commit -m "skill: sync update — DDMMYY-<ten>"
  git push origin orca
  rm -rf /tmp/rheinmir-setup-sync
  ```

> Skip chỉ khi skill không tạo ra artifact hoặc quyết định nào.
