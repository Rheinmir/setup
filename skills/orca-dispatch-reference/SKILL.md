---
name: orca-dispatch-reference
description: Reference for Antigravity/OpenCode dispatch, skill installation, AgentMemory, RTK token proxy — NOT a loop skill
---

# Orca Dispatch Reference

> Đây là tài liệu tham khảo, không phải skill. Không invoke trong loop.

## Antigravity (agy)

**Binary**: `agy` — `%LOCALAPPDATA%\agy\bin\agy.exe`. KHÔNG phải `antigravity`, KHÔNG phải `~/.local/bin/agy`.

```bash
# CHECK trước khi dùng:
agy --version
```

**Hook**: Orca v1.4.21 fix Windows hook quoting — không cần sửa tay `antigravity-hook.cmd`.

**Dispatch status** (tested post v1.4.21):

| Method | Status |
|--------|--------|
| `dispatch --inject` | Cần retest |
| `terminal send` thủ công | OK |
| Tool calls trong agy | OK |
| `worker_done` callback | Cần retest |

**Fallback workflow nếu `--inject` fail:**
```bash
orca terminal send --title "Antigravity" --text "<task>"
orca terminal wait --for tui-idle
orca terminal read --title "Antigravity"
```

## Kiro CLI (kiro-cli)

**Binary**: `kiro-cli` — `%LOCALAPPDATA%\Kiro-Cli\kiro-cli.exe` (Windows).

```bash
# CHECK trước khi dùng:
kiro-cli --version
```

## Skill Installation per Agent CLI

Skills nằm tại `llmwiki/skills/<category>/<name>.md`.

### Claude Code
```bash
# CHECK skills đã cài:
ls .claude/commands/

# Install:
cp llmwiki/skills/wiki/propose.md .claude/commands/propose.md
```

### OpenCode / Antigravity
```bash
# CHECK:
ls ~/.agents/skills/

# Install (skill phải là thư mục chứa SKILL.md):
mkdir -p ~/.agents/skills/propose/
cp llmwiki/skills/wiki/propose.md ~/.agents/skills/propose/SKILL.md
# Restart OpenCode sau khi install.
```

### Kiro CLI
```bash
# CHECK:
ls ~/.kiro/skills/

# Install (skill phải là thư mục chứa SKILL.md):
mkdir -p ~/.kiro/skills/propose/
cp llmwiki/skills/wiki/propose.md ~/.kiro/skills/propose/SKILL.md
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

> Token tại `agentmemory.giatbh.io.vn` KHÁC — đừng dùng lẫn.

## RTK — Token Proxy

RTK (Rust Token Killer) tự động filter CLI output trước khi vào context — 60-90% token reduction.

```bash
# CHECK đã cài chưa:
rtk --version

# Cài hook cho agent (chạy 1 lần):
rtk hooks install --agent claude
rtk hooks install --agent opencode
# Sau khi cài: mọi command agent chạy tự qua RTK, không cần thay đổi gì.

# Xem savings:
rtk stats --today
```

> Xem [[concepts/RTK]] để biết chi tiết.
