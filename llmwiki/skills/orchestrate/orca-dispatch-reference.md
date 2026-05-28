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
opencode run -m opencode/big-pickle --dir "<project-path>" --dangerously-skip-permissions "<task>"

# Example:
opencode run -m opencode/big-pickle --dir "C:\Users\olive\orca\workspaces\home-spotify\m" --dangerously-skip-permissions "List all TODO comments in backend/"
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
cp llmwiki/skills/wiki/propose.md .claude/commands/propose.md
```

### OpenCode / Antigravity
```bash
# CHECK:
ls ~/.agents/skills/

# Install (skill = folder with SKILL.md):
mkdir -p ~/.agents/skills/propose/
cp llmwiki/skills/wiki/propose.md ~/.agents/skills/propose/SKILL.md
# Restart OpenCode after install.
```

## AgentMemory

```bash
BASE="https://cognee1995.coteccons.vn"
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

> `agentmemory.giatbh.io.vn` token DIFFERENT — do not mix.

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
