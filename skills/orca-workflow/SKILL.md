---
name: orca-workflow
description: Daily propose → gate → dispatch workflow with Orca
---

# Skill: orca-workflow

## Triggers

- User nói "propose <tính năng>", "feature request", "implement <tên>"
- User nói "chạy lint", "verify wiki"
- User nói "sync template", "upstream"

## Workflow: propose

1. **query**: Gather context từ wiki/ về tính năng được yêu cầu
2. **propose**: Tạo draft tại `llmwiki/wiki/sources/draft/DDMMYY-tên.md`
3. **gate**: `orca orchestration gate-create --question "Duyệt proposal này?"` → chờ user
4. **Sau duyệt**: Phân rã tasks từ proposal → `orca orchestration task-create` mỗi task
5. **dispatch**: thử `orca orchestration dispatch --task <id> --to <agent> --inject`; nếu fail → `orca terminal send`
6. **Chờ**: `orca terminal wait --for tui-idle` → `orca terminal read`
7. **Verify**: invoke `verify-before-commit` trước mỗi commit

## Dispatch nhanh

```bash
# Check terminals
orca terminal list

# Tạo Antigravity terminal (nếu chưa có)
orca terminal create --worktree active --title "Antigravity" --command "agy"

# Tạo OpenCode terminal
orca terminal create --worktree active --title "OpenCode" --command "opencode"

# Gửi task
orca terminal send --title "Antigravity" --text "<task description>"

# Đọc kết quả
orca terminal wait --for tui-idle && orca terminal read --title "Antigravity"
```

## Agent binaries

| Agent | Binary | CHECK |
|-------|--------|-------|
| Antigravity | `agy` | `agy --version` |
| OpenCode | `opencode` | `opencode --version` |
| Orca | GUI only — dùng qua `orca terminal *` commands | `orca terminal list` |

> Để biết dispatch, skill install, AgentMemory — xem `llmwiki/skills/setup/orca-dispatch-reference.md`
