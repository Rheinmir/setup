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
2. **propose**: Tạo draft tại `llmwiki/wiki/sources/draft/DDMMYY-tên.md`
3. **gate**: `orca orchestration gate-create --question "Duyệt proposal này?"` → chờ user
4. **Sau duyệt**: Phân rã tasks từ proposal → `orca orchestration task-create` mỗi task
5. **dispatch**: `orca orchestration dispatch --task <id> --to <agent> --inject`
6. **Chờ**: `orca orchestration check --wait --types worker_done --timeout-ms 300000`
7. **Kiểm tra**: `verify-before-commit` tự động chạy trước mỗi commit

## Antigravity Dispatch Reality (tested 2026-05-21, updated 2026-05-23)

**Binary**: `agy` — trong PATH tại `%LOCALAPPDATA%\agy\bin\agy.exe` (Windows). KHÔNG phải `antigravity` (not found). KHÔNG phải `~/.local/bin/agy` (Linux path — sai trên Windows).

**Tạo terminal**:
```bash
orca terminal create --worktree active --title "Antigravity" --command "agy"
```

**Hook**: Orca v1.4.21 đã fix "Antigravity Windows hook quoting" — KHÔNG cần sửa tay `antigravity-hook.cmd`. Hook hoạt động đúng out-of-the-box từ v1.4.21.

**OpenCode**: lệnh là `opencode` (npm global tại `%APPDATA%\npm\opencode.cmd`).

Kết quả thực tế khi dispatch task qua Orca đến Antigravity CLI:

| Bước | Trạng thái (sau v1.4.21) |
|------|--------------------------|
| `dispatch --inject` | **Cần retest** — trước v1.4.21 fail |
| `terminal send` thủ công | **OK** |
| Antigravity đọc file/chạy lệnh | **OK** — tool calls pass |
| `worker_done` về inbox | **Cần retest** |
| Gemini hiểu task | **OK** |

**Hệ quả cho dispatch workflow:**
- Thử `--inject` sau v1.4.21 — nếu vẫn fail, fallback dùng `terminal send` thủ công.
- Sau send: dùng `terminal wait --for tui-idle` rồi `terminal read` để lấy kết quả.

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
