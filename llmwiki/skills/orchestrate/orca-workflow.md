---
name: orca-workflow
description: Daily propose → gate → dispatch workflow with Orca
---

# Skill: orca-workflow

## Purpose

Propose → gate → dispatch → verify qua Orca. Agent pool 1:1 per engine (claude, agy, opencode, kiro, copilot).

Claude: analyze. Others: execute. Kill opencode nếu chờ quá lâu.

**Caveman Mode**: Agent comms dùng `caveman` (~75% token save). Tắt khi: viết proposal, tài liệu, HTML.


## Triggers

- "propose <feature>", "feature request", "implement <name>"
- "chạy lint", "verify wiki"
- "sync template", "upstream"

## Workflow: propose

1. **query**: Gather context từ wiki/ về tính năng được yêu cầu
2. **propose**: Tạo CẶP file đủ chuẩn R7 (validator chặn nếu thiếu) — draft `llmwiki/wiki/sources/draft/DDMMYY-tên.md` PHẢI có `## Plan` (checklist `- [ ]`) + `## Agent Task Assignment` (Task | Agent CLI | Lý do chọn | Status=pending — khai ngay lúc propose, chọn theo bảng chi phí) + link seq html; và `llmwiki/html/DDMMYY-tên-seq.html` với **MỖI task một diagram** gắn badge agent (indigo = legacy, emerald = thêm/sửa, cam = nhánh chặn; message từng bước, auto-loop). Link 2 chiều md ↔ html
3. **gate**: `orca orchestration gate-create --question "Duyệt proposal này?"` → chờ user (gửi kèm preview URL của html)
4. **Sau duyệt**: Phân rã tasks từ proposal → `orca orchestration task-create` mỗi task
5. **dispatch**: `orca orchestration dispatch --task <id> --to <agent> --inject`
6. **Chờ**: `orca orchestration check --wait --types worker_done --timeout-ms 300000`
7. **Kiểm tra**: `verify-before-commit` tự động chạy trước mỗi commit

## Gotchas orchestration CLI (bài học 230626)

- **2 id từ `task-create --json`**: response có envelope `id` (uuid) VÀ `result.task.id` (`task_xxxx`). Mọi lệnh sau (`gate-create --task`, `dispatch --task`, `task-update --id`) PHẢI dùng `result.task.id`, KHÔNG dùng envelope id. Dùng nhầm: gate vẫn tạo/resolve được nhưng trỏ task ma → task thật kẹt ở `ready`.
- **Status hợp lệ của `task-update --status`**: `ready` | `in_progress` | `completed` | `failed`. KHÔNG có `done` — truyền `done` trả `ok:false` lặng lẽ (không báo lỗi rõ).
- Lấy id thật chắc ăn: `orca orchestration task-list --json` rồi match theo `spec`.

## An toàn container / DB (BẮT BUỘC trước khi đụng docker)

### Trước khi đụng container (docker compose / docker run)

```bash
# BẮT BUỘC chạy trước bất kỳ --force-recreate, down, recreate nào:
docker inspect <container_name> --format '{{json .Mounts}}' | python3 -m json.tool
```

So sánh `Source` path với volume trong compose file sắp dùng. Nếu khác → DỪNG, hỏi user.

**Production DB của Cozyroom:** `/mnt/c/Users/olive/orca/workspaces/home-spotify/m/data/metadata.db`
Không bao giờ đổi volume mount mà không backup + xác nhận user.

> Bài học 2026-05-29: recreate container với compose sai path → mất toàn bộ DB người dùng.

## Dispatch nhanh

```bash
# OpenCode non-interactive (DEFAULT — dùng big-pickle miễn phí):
# ⚠ KHÔNG dùng --dangerously-skip-permissions khi dispatch từ Claude Code — auto-mode classifier sẽ DENY (bài học 120626)
opencode run -m opencode/big-pickle --dir "<project>" "<task>"

# Antigravity non-interactive:
agy -p "<task>"

# Kiro non-interactive:
kiro run --dir "<project>" "<task>"

# GitHub Copilot Coding Agent (async — via GitHub issue):
gh issue create --title "<task>" --body "<task details>" --assignee "@me"
# Then: gh copilot suggest "<task>" or trigger via VS Code Copilot Chat

# Nếu dùng Orca terminal (interactive):
orca terminal list
orca terminal create --worktree active --title "OpenCode" --command "opencode"
orca terminal send --title "OpenCode" --text "<task>"
orca terminal wait --for tui-idle && orca terminal read --title "OpenCode"
```

## Phân công task theo chi phí

| Task | Agent | Model |
|------|-------|-------|
| Search, grep, list, read | OpenCode | `opencode/big-pickle` ($0) |
| Viết boilerplate, CRUD | OpenCode | `opencode/big-pickle` ($0) |
| Wiki ingest/lint | OpenCode | `opencode/big-pickle` ($0) |
| Review diff, explain | agy | default |
| Architectural decisions | Claude Code | sonnet-4-6 |
| Debug lỗi khó | Claude Code | sonnet-4-6 |
| Frontend UI boilerplate | Kiro | default |
| Cross-file refactor | Kiro | default |
| PR review + suggest fixes | Copilot | gpt-4o (GitHub) |

## Agent binaries

| Agent | Binary | CHECK |
|-------|--------|-------|
| Antigravity | `agy` | `agy --version` |
| OpenCode | `opencode run -m opencode/big-pickle` | `opencode --version` |
| Kiro | `kiro run` | `kiro --version` |
| GitHub Copilot | `gh copilot suggest` | `gh copilot --version` |
| Orca | GUI only — dùng qua `orca terminal *` commands | `orca terminal list` |

## Antigravity Dispatch Reality (tested 2026-05-21, updated 2026-05-23)

**Binary**: `agy` — `%LOCALAPPDATA%\agy\bin\agy.exe`. NOT `antigravity`, NOT `~/.local/bin/agy` (Linux).

**Tạo terminal**:
```bash
orca terminal create --worktree active --title "Antigravity" --command "agy"
```

**Hook**: Orca v1.4.21 fix Windows hook quoting — `antigravity-hook.cmd` no manual edit needed.

**OpenCode**: `opencode` — npm global at `%APPDATA%\npm\opencode.cmd`.

Dispatch status:

| Bước | Trạng thái |
|------|-----------|
| `dispatch --inject` | Thử sau v1.4.21 — nếu fail, dùng `terminal send` |
| `terminal send` thủ công | **OK** |
| Antigravity đọc file/chạy lệnh | **OK** |
| `worker_done` về inbox | Cần retest |

## Slash Skill Installation per Agent CLI

Agent nhận dispatch: **tự cài skill** từ `llmwiki/skills/` trước khi bắt đầu.

### Claude Code CLI
```bash
mkdir -p .claude/commands/
cp llmwiki/skills/<loop>/<name>.md .claude/commands/<name>.md
# User-level:
mkdir -p ~/.claude/commands/
cp llmwiki/skills/<loop>/<name>.md ~/.claude/commands/<name>.md
```

### OpenCode CLI
```bash
mkdir -p ~/.agents/skills/<name>/
cp llmwiki/skills/<loop>/<name>.md ~/.agents/skills/<name>/SKILL.md
# Restart OpenCode để discover skill mới.
```

### Antigravity CLI
```bash
mkdir -p ~/.agents/skills/<name>/
cp llmwiki/skills/<loop>/<name>.md ~/.agents/skills/<name>/SKILL.md
```

### Kiro CLI
```bash
mkdir -p ~/.kiro/skills/<name>/
cp llmwiki/skills/<loop>/<name>.md ~/.kiro/skills/<name>/SKILL.md
```

### GitHub Copilot
```bash
# Workspace-level steering via .github/copilot-instructions.md
# Skills injected as context file:
mkdir -p .github/
cat llmwiki/skills/<loop>/<name>.md >> .github/copilot-instructions.md
# Or per-skill steering file (Copilot Workspace):
mkdir -p .github/skills/
cp llmwiki/skills/<loop>/<name>.md .github/skills/<name>.md
```

### Rules cho tất cả agent
- Copy skill files only — skip `README.md`, `index.md`, `log.md`.
- File by file — no `cp -R`.
- Scope: `.claude/commands/` (Claude Code); `~/.agents/skills/` (OpenCode/agy); `~/.kiro/skills/` (Kiro); `.github/` (Copilot).
- Sau khi cài, report:
  ```
  | Agent       | Skill   | Installed at                            |
  |-------------|---------|------------------------------------------|
  | claude-cli  | propose | .claude/commands/propose.md              |
  | opencode    | propose | ~/.agents/skills/propose/SKILL.md        |
  | antigravity | propose | ~/.agents/skills/propose/SKILL.md        |
  | kiro        | propose | ~/.kiro/skills/propose/SKILL.md          |
  | copilot     | propose | .github/skills/propose.md                |
  ```

## AgentMemory — Persistent Cross-Session Memory

Service tại `https://agentmemory.giatbh.io.vn/` — lưu context giữa các session.

```bash
BASE="https://agentmemory.giatbh.io.vn"
TOKEN="${AGENTMEMORY_TOKEN}"

# Health check
curl -sk -H "Authorization: Bearer $TOKEN" "$BASE/agentmemory/health"

# Ghi memory (cuối session hoặc sau quyết định quan trọng)
curl -sk -X POST "$BASE/agentmemory/remember" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"<nội dung>","category":"fact|preference|decision|context"}'

# Tìm kiếm (đầu session hoặc trước khi propose)
curl -sk -H "Authorization: Bearer $TOKEN" \
  "$BASE/agentmemory/search?query=<từ+khóa>"
```

**Khi dùng:**
- **Đầu session**: search context trước khi bắt đầu
- **Sau decision**: lưu approach + lý do
- **Cuối session**: lưu tasks xong, commits, trạng thái

## Commands chính

```bash
orca orchestration run --spec "Propose: <tính năng>. Query wiki, tạo draft, gate chờ duyệt."
```

> Dispatch chi tiết: `llmwiki/skills/orchestrate/orca-dispatch-reference.md`
