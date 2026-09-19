---
name: orca-dispatch-reference
description: Reference for Antigravity/OpenCode dispatch, skill installation, AgentMemory, RTK token proxy — NOT a loop skill
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Orca Dispatch Reference

> Reference doc, not a skill. Do not invoke in loop.

> **Nguồn chân lý DUY NHẤT cho dispatch.** Mọi skill orca-* / orchestration (orca-workflow, orca-onboard, orca-cli, orchestration, council…) chỉ TRỎ về đây — đừng nhân bản roster/syntax ở nơi khác (chống drift).

## WHAT

### Purpose và context
- **Purpose:** nguồn chân lý DUY NHẤT để tra cú pháp + roster dispatch (agent backend, chọn model theo cost, OpenCode, concurrency, orchestration, Antigravity), cài skill theo agent CLI, AgentMemory và RTK.
- **Trigger (when to use):** skill orca-* / orchestration (orca-workflow, orca-onboard, orca-cli, orchestration, council…) cần biết giao task cho agent nào, gõ lệnh dispatch nào, cài skill vào CLI nào, hoặc kiểm AgentMemory/RTK.
- **Non-goals:** Reference doc, not a skill — không chạy trong loop; không chứa giá model làm cứng (nguồn là `/claude-api`); không phải nơi nhân bản roster sang skill khác.

### Mental model
`nhu cầu (backend · model tier · lệnh dispatch · cài skill · memory · token proxy) → mục tham chiếu tương ứng → CHECK công cụ có mặt → chạy lệnh đã verify → fallback ghi sẵn nếu hỏng`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | loại task cần giao (rẻ/cơ học/answer-only hay reasoning đắt) | có | quyết định backend + tier |
| In | agent CLI đích có mặt trên máy | có | CHECK trước (`agy --version`, `rtk --version`…) |
| Out | backend + model + lệnh dispatch đúng cú pháp | có | tên `--agent` hợp lệ theo picker UI |
| Out | draft output report + index + log | khi có artifact/quyết định | có bảng Agent Task Assignment |

### Rules và capabilities
- RULE-01 (MUST): **Nguồn chân lý DUY NHẤT cho dispatch.** Mọi skill orca-* / orchestration chỉ TRỎ về đây — đừng nhân bản roster/syntax ở nơi khác (chống drift).
- RULE-02 (MUST): **Cost-tier (luật):** rẻ / cơ học / **answer-only → opencode free**; reasoning đắt / tổng hợp / chairman → **Claude** (đắt nhất, để dành).
- RULE-03 (MUST): **advisor luôn phải ≥ executor** (luật pairing cứng của advisor tool, request sai cặp trả 400).
- RULE-04 (MUST): KHÔNG `--dangerously-skip-permissions` khi dispatch TỪ Claude Code (classifier DENY — bài học 120626).
- RULE-05 (MUST): KHÔNG mở nhiều opencode trong CÙNG 1 folder — mỗi worker = 1 worktree riêng.
- RULE-06 (SHOULD): **Giá đổi theo thời gian** — ĐỪNG chép số làm cứng; bảng chỉ để XẾP HẠNG tương đối, gọi `/claude-api` khi cần số thật.
- Capabilities: chạy agent CLI cục bộ trong terminal/worktree; tạo/xoá worktree; gọi HTTP tới AgentMemory với token từ biến môi trường.

### Failure boundaries
- `--agent <id>` bịa → `"Unknown TUI agent"`: validate TRƯỚC khi tạo worktree.
- opencode im lặng quá watchdog 60–90s → kill + **fallback Claude**.
- Antigravity `--inject` hỏng → fallback `terminal send` / `wait` / `read`.
- Task có file-edit/dependency → không giao opencode.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | judgment | loại task | Chọn backend + tier theo bảng roster và chain Claude (RULE-02, RULE-03) | backend + model | — |
| W02 | deterministic | agent CLI | CHECK công cụ có mặt theo mục tương ứng | có mặt | thiếu → báo user |
| W03 | effect | backend + task | Chạy lệnh dispatch/cài đặt ở mục tham chiếu | task đang chạy / skill đã cài | lỗi → B01/B02 |
| W04 | effect | kết quả | Output report + cập nhật status agent (mục Delivery) | draft + index + log | 0 artifact → skip |

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | recovery | opencode stall quá watchdog 60–90s | kill + fallback Claude | — | W04 |
| B02 | recovery | Antigravity `dispatch --inject` fails | `orca terminal send` rồi `wait --for tui-idle` rồi `read` | — | W04 |
| B03 | conditional_required | nhiều worker opencode song song | 1 worktree riêng mỗi worker, hoặc `opencode serve` + `--attach` | — | W03 |
| B04 | conditional_required | dùng `--inject` | spawn agent vào terminal đích trước (`orca worktree create --agent` hoặc `orca terminal create`) | — | W03 |

### Validation và stopping
Đúng tên agent: picker UI là ground truth. Hoàn tất dispatch: `orca orchestration check --types worker_done`. Dừng khi task xong hoặc fallback đã nhận việc.

### Examples
- **Positive:** cần 3 worker render rẻ song song → `opencode/big-pickle`, mỗi worker một `orca worktree create --name <w>` + `opencode run --dir "<worktree-path>" … &`, xong `orca worktree rm`.
- **Boundary/failure:** giao opencode `big-pickle` đọc 40 file + sinh báo cáo dài → im lặng quá 90s → kill, chuyển Claude (Sonnet 5 mặc định), KHÔNG thêm `--dangerously-skip-permissions` (classifier DENY).

### Reference — Agent backends — roster & chọn theo cost (verified 2026-07-01)

Orca drive model bằng cách chạy một **agent CLI** trong terminal/worktree. Picker UI: **OpenCode · Claude · GitHub Copilot · Antigravity · Kiro**. Ba hệ tên hay lệch (picker ≠ `@`-handle ≠ `--agent` id) → bảng này hoà giải:

| Picker (UI) | `--agent <id>` | provider/model | Cost | Dùng cho |
|---|---|---|---|---|
| OpenCode | `opencode` | `opencode/big-pickle` (+free khác) | **$0** | task rẻ, render, **seat answer-only** |
| Claude | `claude` | (phiên hiện tại) | **đắt nhất** | reasoning khó, chairman — **để dành** |
| Antigravity | `agy` | — | rẻ | render dự phòng |
| GitHub Copilot | `copilot` | — | rẻ | dự phòng |
| Kiro | `kiro` | — | rẻ | dự phòng |

- `--agent <id>` bịa → `"Unknown TUI agent"` (validate TRƯỚC khi tạo worktree). Tập recognized cho `--inject` (live error): `claude · codex · gemini · droid`. Không có lệnh liệt kê — **picker UI là ground truth**.
- **Cost-tier (luật):** rẻ / cơ học / **answer-only → opencode free**; reasoning đắt / tổng hợp / chairman → **Claude** (đắt nhất, để dành). Khớp split "Claude-nghĩ / CLI-rẻ-render" của `orca-workflow`.

#### Chain TRONG chính Claude — 4 model, 4 mức giá (đừng coi "Claude" là một khối)

Picker "Claude" ở bảng trên gộp bốn model có giá lệch nhau tới 10 lần. Trước khi mặc định
coi nhánh Claude là "đắt nhất, để dành", chọn đúng TIER bên trong nó — cùng luật rẻ/cơ học
→ answer-only, đắt/tổng hợp → chairman, chỉ áp lại một tầng sâu hơn:

| Model | Model ID | Input/Output $/1M (mốc `/claude-api`) | Dùng cho trong dispatch |
|---|---|---|---|
| Haiku 4.5 | `claude-haiku-4-5` | $1 / $5 | search/grep/list, sub-agent đọc-hàng-loạt, worker rẻ trong multiagent |
| Sonnet 5 | `claude-sonnet-5` | $2 / $10 | build/CRUD/refactor tiêu chuẩn — mặc định khi KHÔNG ai chỉ định model |
| Opus 5 | `claude-opus-5` | $5 / $25 | reasoning khó, review sâu, **advisor** cho executor Sonnet |
| Fable 5.1 | `claude-fable-5-1` | $10 / $50 | chairman/tổng hợp cuối, quyết định kiến trúc, phiên agentic dài — đắt nhất trong 4, để dành |

- **Giá đổi theo thời gian** — nguồn chân lý là bảng "Current Models" trong skill `/claude-api`, ĐỪNG chép số ở đây làm cứng. Bảng trên chỉ để XẾP HẠNG tương đối (Haiku < Sonnet < Opus < Fable), gọi `/claude-api` khi cần số thật.
- Đổi model trong CÙNG một phiên (không mở phiên mới): `/model sonnet|opus|haiku|fable`.
- **Multiagent nhiều Claude cùng lúc:** worker rẻ đọc-hàng-loạt = Haiku; executor mặc định = Sonnet; **advisor luôn phải ≥ executor** (Sonnet → Opus/Opus 4.8, không được thấp hơn — luật pairing cứng của advisor tool, request sai cặp trả 400).

### Reference — OpenCode — cheap dispatch (verified)

**Free models ($0, opencode zen):** `opencode/big-pickle` · `deepseek-v4-flash-free` · `mimo-v2.5-free` · `nemotron-3-ultra-free` · `north-mini-code-free`.

```bash
opencode run -m opencode/big-pickle --dir "<worktree-path>" "<task>"   # headless, $0
opencode run -m opencode/big-pickle --format json "<task>"            # JSON events (parse máy)
opencode run -m <model> -s <session_id> "<task>"                      # nối session (--continue / --fork)
# ⚠ KHÔNG --dangerously-skip-permissions khi dispatch TỪ Claude Code (classifier DENY — bài học 120626).
#   Task answer-only (không đụng file) thì KHÔNG cần quyền → chạy thẳng được.
```

**⚠ Reliability (verified 2026-07-01):** `big-pickle` ngon với câu **ngắn/answer-only** (toán → vài giây); **STALL/timeout trên task NẶNG** (đọc nhiều file / sinh dài — đo >560s vẫn chưa xong). Đặt **watchdog 60–90s** → im lặng thì kill + **fallback Claude**. Task có file-edit/dependency → đừng giao opencode.

### Reference — Concurrency — KHÔNG mở nhiều opencode trong CÙNG 1 folder (researched + verified)

Nhiều opencode cùng 1 folder **dùng chung SQLite/session** (resolve `project_id` theo working dir) → **đè nhau, hỏng git snapshot** (opencode issues #31307 / #4251 / #28249). Test "3 song song 1 folder OK" là MISLEADING — chỉ đúng với câu tí hon answer-only.

**Pattern ĐÚNG (đã validate):** mỗi worker = **1 worktree riêng**, 1 opencode/worktree:
```bash
orca worktree create --name <w> --setup skip --no-parent --json       # tách dir+branch
opencode run --dir "<worktree-path>" -m opencode/big-pickle "<task>" &  # N cái song song được
orca worktree rm --worktree name:<w> --force --json                   # dọn
```
Hoặc multiplexer: `opencode serve --port <P>` + `opencode run --attach http://localhost:<P> -s <id>`.

### Reference — Orchestration dispatch (qua orca runtime — plumbing đã verify live)

```bash
orca orchestration task-create --spec "<task>" --task-title "<t>" --json     # → task_id
orca orchestration dispatch --task <id> --to <handle> --inject --json        # --inject CẦN agent CLI đang chạy trong terminal đích
orca orchestration check --terminal <handle> --types worker_done --wait --timeout-ms 300000 --json
```
- Spawn agent vào terminal trước khi `--inject`: `orca worktree create --agent <id> --prompt "<task>"` hoặc `orca terminal create --command "<cli>"`.
- Group address: `@all @idle @claude @codex @opencode @gemini @droid @worktree:<id>`.

### Reference — Antigravity (agy)

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

### Reference — Skill Installation per Agent CLI

Skills: `llmwiki/skills/<category>/<name>.md`.

#### Claude Code
```bash
# CHECK:
ls .claude/commands/

# Install:
cp llmwiki/skills/dev-loop/propose.md .claude/commands/propose.md
```

#### OpenCode / Antigravity
```bash
# CHECK:
ls ~/.agents/skills/

# Install (skill = folder with SKILL.md):
mkdir -p ~/.agents/skills/propose/
cp llmwiki/skills/dev-loop/propose.md ~/.agents/skills/propose/SKILL.md
# Restart OpenCode after install.
```

### Reference — AgentMemory

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

### Reference — RTK — Token Proxy

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

### Delivery — Output Report

After all main skill tasks complete, write a propose draft to the wiki.

#### Steps

**1. Build the filename:**
- Format: `DDMMYY-<ten>.md`
- `DDMMYY` = today (e.g., `020626` for 2 June 2026)
- `<ten>` = 2–4 kebab-case words summarising what was done (e.g., `landing-page-coteccons`, `brand-kit-fintech`, `ingest-auth-spec`)

**2. Write** `llmwiki/wiki/draft/orca/DDMMYY-<ten>.md`:

```
---
type: draft
title: "DDMMYY-<ten>"
status: proposed
tags: [<skill-name>, output-report]
timestamp: YYYY-MM-DD
---

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
