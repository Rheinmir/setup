---
name: orca-workflow
description: Daily propose → gate → dispatch workflow with Orca
---

# Skill: orca-workflow

## Triggers

- User nói "propose <tính năng>", "feature request", "implement <tên>"
- User nói "chạy lint", "verify wiki"
- User nói "sync template", "upstream"

## ⚠️ QUY TẮC BẤT BIẾN — KHÔNG ĐƯỢC BỎ QUA

### Trước khi đụng container (docker compose / docker run)

```bash
# BẮT BUỘC chạy trước bất kỳ --force-recreate, down, recreate nào:
docker inspect <container_name> --format '{{json .Mounts}}' | python3 -m json.tool
```

So sánh `Source` path với volume trong compose file sắp dùng. Nếu khác → DỪNG, hỏi user.

**Production DB của Cozyroom:** `/mnt/c/Users/olive/orca/workspaces/home-spotify/m/data/metadata.db`
Không bao giờ đổi volume mount mà không backup + xác nhận user.

> Bài học 2026-05-29: recreate container với compose sai path → mất toàn bộ DB người dùng.

---

## Workflow: propose

1. **query**: Gather context từ wiki/ về tính năng được yêu cầu
2. **propose**: Tạo draft tại `llmwiki/wiki/draft/orca/DDMMYY-tên.md`
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
| Kiro | `kiro-cli` | `kiro-cli --version` |
| Orca | GUI only — dùng qua `orca terminal *` commands | `orca terminal list` |

## Caveman Mode

Dùng `caveman` (plugin `/caveman`) cho hầu hết tình huống để tiết kiệm ~75% token. Không dùng khi viết proposal, tài liệu, hoặc xuất HTML.

> Để biết dispatch, skill install, AgentMemory — xem `llmwiki/skills/setup/orca-dispatch-reference.md`


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