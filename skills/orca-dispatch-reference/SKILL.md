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
cp llmwiki/skills/dev-loop/propose.md .claude/commands/propose.md
```

### OpenCode / Antigravity
```bash
# CHECK:
ls ~/.agents/skills/

# Install (skill phải là thư mục chứa SKILL.md):
mkdir -p ~/.agents/skills/propose/
cp llmwiki/skills/dev-loop/propose.md ~/.agents/skills/propose/SKILL.md
# Restart OpenCode sau khi install.
```

### Kiro CLI
```bash
# CHECK:
ls ~/.kiro/skills/

# Install (skill phải là thư mục chứa SKILL.md):
mkdir -p ~/.kiro/skills/propose/
cp llmwiki/skills/dev-loop/propose.md ~/.kiro/skills/propose/SKILL.md
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

## Caveman — Prose Compression

Caveman tự động nén ngôn ngữ hội thoại của agent để tiết kiệm ~75% hội thoại (output tokens) mà vẫn giữ nguyên độ chính xác kỹ thuật.

```bash
# Cài đặt cho mọi agent (chạy 1 lần):
# Windows:
irm https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.ps1 | iex
# macOS/Linux/WSL:
curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash

# Kích hoạt thủ công trong phiên chat (nếu không tự bật):
/caveman
# Hoặc nói: "talk like caveman" / "caveman mode"

# Xem thống kê tiết kiệm:
/caveman-stats
```

> Hầu hết tình huống giao tiếp thông thường cần dùng caveman để tiết kiệm token. Chỉ bỏ nén khi viết proposal, tài liệu chính thức, hoặc xuất HTML.



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