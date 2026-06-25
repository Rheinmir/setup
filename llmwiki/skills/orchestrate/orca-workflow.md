---
name: orca-workflow
description: Daily propose → gate → dispatch workflow with Orca
---

# Skill: orca-workflow

## Purpose

Điều phối luồng làm việc hàng ngày qua Orca orchestration — propose → gate → dispatch → verify. khi chia agent làm việc chia các agent của từng engine 1:1 (claude cli , antigravity cli, opencode,...)  
  
claude sẽ chủ yếu phân tích, các model còn lại đảm nhiệm việc thực thi.  
  
với opencode có thể chú ý kill và bỏ ra khỏi pool phân phối nếu chờ quá lâu.

## Triggers

- User nói "propose <tính năng>", "feature request", "implement <tên>"
- User nói "chạy lint", "verify wiki"
- User nói "sync template", "upstream"

## Workflow: propose

1. **query**: Gather context từ wiki/ về tính năng được yêu cầu
2. **propose**: Tạo draft tại `llmwiki/wiki/sources/draft/DDMMYY-tên.md` + seq html `llmwiki/html/DDMMYY-tên-seq.html` (mỗi task 1 diagram, badge indigo/emerald/cam).
   - **STYLE seq html BẮT BUỘC theo `docs-site-macos` (liquid-glass macOS), KHÔNG theme tối** (bài học 250626): nền sáng `linear-gradient(180deg,#f7fbff,#eaf2fd)` + refraction `body::before` orbs + `::after` dot-grid; `.diagram-box` glass tier-2 `rgba(255,255,255,.7)`+`backdrop-filter:blur(8px)`+edge-highlight; traffic-light chrome; h2 `#1d1d1f`; badge tint Apple secondary; `.msg` opacity ≥.9. Self-contained. Mẫu: `llmwiki/html/250626-hris-explorer-v2-3channel-seq.html`.
3. **gate**: `orca orchestration gate-create --question "Duyệt proposal này?"` → chờ user
4. **Sau duyệt**: Phân rã tasks từ proposal → `orca orchestration task-create` mỗi task
5. **dispatch**: `orca orchestration dispatch --task <id> --to <agent> --inject`
6. **Chờ**: `orca orchestration check --wait --types worker_done --timeout-ms 300000`
7. **Kiểm tra**: `verify-before-commit` tự động chạy trước mỗi commit

## Antigravity Dispatch Reality (tested 2026-05-21, updated after fix)

**Binary**: `agy` (tại `~/.local/bin/agy`) — KHÔNG phải `antigravity` (not found).

**Tạo terminal**:
```bash
orca terminal create --worktree active --title "Antigravity" --command "agy"
```

**Full tool access** (bắt buộc trước khi dispatch):
- Thêm `PreToolUse)` case vào `~/.orca/agent-hooks/antigravity-hook.sh` output `{"decision":"allow"}`
- Không có bước này: tất cả tool call bị block bởi `jsonhook__orca-status_PreToolUse_0_0`
- Sau khi sửa hook, phải tạo session `agy` mới (close terminal cũ, create mới)

Kết quả thực tế khi dispatch task qua Orca đến Antigravity CLI:

| Bước | Trước fix | Sau fix |
|------|-----------|---------|
| `dispatch --inject` | **Fail** — Orca không nhận Antigravity | **Fail** — vẫn không nhận |
| `terminal send` thủ công | **OK** | **OK** |
| Antigravity đọc file/chạy lệnh | **Blocked** — `jsonhook__orca-status` | **OK** — tool calls pass |
| `worker_done` về inbox | **Không đến** | Chưa test lại |
| Gemini hiểu task | **Đúng** | **Đúng** |

**Hệ quả cho dispatch workflow:**
- Không dùng `--inject` cho Antigravity — luôn dùng `terminal send` thủ công.
- Với full tool access đã bật: dùng `terminal wait --for tui-idle` rồi `terminal read`.
- `worker_done` vẫn chưa chắc hoạt động — cần test lại sau khi có full access.

## Slash Skill Installation per Agent CLI

Mỗi agent khi nhận dispatch **phải tự cài slash skill** từ `llmwiki/skills/` vào CLI của nó trước khi bắt đầu task. Mỗi engine có path và format khác nhau:

### Claude Code CLI
```bash
# Project-level (mặc định — chỉ repo này):
mkdir -p .claude/commands/
cp llmwiki/skills/<loop>/<name>.md .claude/commands/<name>.md

# User-level (tất cả project, cần user approval):
mkdir -p ~/.claude/commands/
cp llmwiki/skills/<loop>/<name>.md ~/.claude/commands/<name>.md
```
Skill ngay lập tức available dưới dạng `/<name>` trong Claude Code, không cần restart.

### OpenCode CLI
```bash
# Skills là thư mục chứa SKILL.md — KHÔNG phải flat file:
mkdir -p ~/.agents/skills/<name>/
cp llmwiki/skills/<loop>/<name>.md ~/.agents/skills/<name>/SKILL.md
# Restart OpenCode để discover skill mới.
```

### Antigravity CLI
```bash
# Dùng cùng shared skill pool với OpenCode:
mkdir -p ~/.agents/skills/<name>/
cp llmwiki/skills/<loop>/<name>.md ~/.agents/skills/<name>/SKILL.md
```

### Rules cho tất cả agent
- Chỉ copy file skill (không copy `README.md`, `index.md`, `log.md`).
- Copy từng file một — không dùng `cp -R`.
- Scope mặc định là **project-level** cho Claude Code; với OpenCode/Antigravity luôn là `~/.agents/skills/`.
- Sau khi cài, report lại coordinator bằng một bảng:
  ```
  | Agent       | Skill         | Installed at                            |
  |-------------|---------------|-----------------------------------------|
  | claude-cli  | propose       | .claude/commands/propose.md             |
  | opencode    | propose       | ~/.agents/skills/propose/SKILL.md       |
  | antigravity | propose       | ~/.agents/skills/propose/SKILL.md       |
  ```

## AgentMemory — Persistent Cross-Session Memory

Service chạy tại `https://cognee1995.coteccons.vn/` — dùng để lưu context giữa các session.

```bash
BASE="https://cognee1995.coteccons.vn"
TOKEN="${AGENTMEMORY_TOKEN}"  # set trong env hoặc lấy từ local memory reference_agentmemory.md

# Health check
curl -sk -H "Authorization: Bearer $TOKEN" "$BASE/agentmemory/health" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status'))"

# Ghi memory (cuối session hoặc sau quyết định quan trọng)
curl -sk -X POST "$BASE/agentmemory/remember" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"<nội dung>","category":"fact|preference|decision|context"}'

# Tìm kiếm (đầu session hoặc trước khi propose)
curl -sk -H "Authorization: Bearer $TOKEN" \
  "$BASE/agentmemory/search?query=<từ+khóa>"
```

**Khi nào dùng:**
- **Đầu session**: search context liên quan trước khi bắt đầu task mới
- **Sau debate/decision**: lưu kết quả approach được chọn + lý do
- **Cuối session**: lưu tasks đã hoàn thành, commits, trạng thái hiện tại

**Lưu ý:** URL `agentmemory.giatbh.io.vn` dùng token khác — không dùng token trên với URL đó.

## Commands chính

```bash
orca orchestration run --spec "Propose: <tính năng>. Query wiki, tạo draft, gate chờ duyệt."
```
