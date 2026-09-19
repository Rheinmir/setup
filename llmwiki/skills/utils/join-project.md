---
name: join-project
description: Orient nhanh vào dự án đang chạy đã có llmwiki — read-only, không ghi wiki
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: join-project

## WHAT

### Purpose và context
- **Purpose:** orient nhanh vào dự án đang chạy đã có `llmwiki/` — hiểu context (project là gì, điểm kỹ thuật chính, thay đổi gần đây, trạng thái tools) mà không re-phân tích toàn bộ code.
- **Trigger (when to use):** Agent hoặc dev mới vào giữa dự án đã có `llmwiki/` — cần hiểu context nhanh mà không re-phân tích toàn bộ code.
- **Non-goals:** không sửa wiki (read-only với wiki pages), không cài harness / RTK / tools (việc của `new-project-setup` hoặc `/harness-update`, user quyết), không onboard codebase chưa có wiki (→ `new-project-setup`, phần gap → `onboard-codebase`).

### Mental model
`llmwiki/ có sẵn → index + log + Architecture → 3 concept được [[link]] nhiều nhất → trạng thái skills/harness → bản tổng hợp orient cho người/agent mới`. Wiki là nguồn; skill chỉ đọc và tóm, không bù chỗ trống bằng suy đoán.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | repo có `llmwiki/wiki/index.md` | có | thiếu → dừng, gợi ý `new-project-setup` |
| In | `llmwiki/wiki/concepts/Architecture.md` | không | nếu có thì đọc để lấy stack |
| Out | báo cáo orient | có | project + stack · 3 điểm kỹ thuật · recent changes & open items · skills state (installed/missing) · gợi ý `onboard-codebase` cho gap lớn |
| Out | trạng thái harness | có | `harness: ON` hoặc `MISSING` (chỉ báo) |
| Out | draft output report | có (trừ khi 0 artifact/decision) | `llmwiki/wiki/sources/draft/DDMMYY-<ten>.md` (mục Delivery) |

### Rules và capabilities
- RULE-01 (MUST): Read-only — không tạo hoặc sửa bất kỳ wiki file nào
- RULE-02 (MUST): Không setup RTK hay tools khác — đó là việc của `new-project-setup`
- RULE-03 (MUST): Nếu wiki trống hoặc stale: nói rõ, đừng fabricate context
- Capabilities: đọc wiki + liệt kê thư mục skills cục bộ; ghi duy nhất draft output report ở mục Delivery. Không mạng, không cài đặt.

### Failure boundaries
- `llmwiki/wiki/index.md` không có → **blocked**: dừng, gợi ý chạy `new-project-setup`.
- Harness MISSING → **partial**: chỉ BÁO, đề xuất `/harness-update`, không tự cài.
- Wiki trống/stale → **partial**: nói rõ trong báo cáo, không bịa context.
- Skills thiếu → báo + gợi ý `INVOKE: sync-template`.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | repo | CHECK llmwiki hợp lệ + harness đã cài | ok / missing | llmwiki missing → blocked; harness missing → B01 |
| W02 | effect | wiki | Đọc index, 20 log entries mới nhất, Architecture.md nếu có | tổng quan | — |
| W03 | deterministic | wiki | Tìm 3 concepts được `[[reference]]` nhiều nhất, READ từng file | 3 concept | kết quả rỗng → B02 |
| W04 | deterministic | máy | CHECK tools (`.claude/commands/`, `~/.agents/skills/`) | installed/missing | thiếu → B03 |
| W05 | judgment | W02–W04 | Synthesize & report | báo cáo orient | gap lớn → gợi ý `onboard-codebase` |
| W06 | effect | kết quả | Output report draft (mục Delivery) | draft + index + log | 0 artifact/decision → skip |

Chi tiết từng bước (nguồn chân lý cho W01–W05):

**1. CHECK — llmwiki hợp lệ không? Harness đã cài chưa?**
```bash
test -f llmwiki/wiki/index.md && echo ok || echo "llmwiki missing — run new-project-setup instead"
# Harness enforcement (hooks chặn raw/, Origin, index-sync) có chưa:
test -f llmwiki/.claude/hooks/pre_tool_use.py && echo "harness: ON" \
  || echo "harness: MISSING — đề xuất user gọi /harness-update (skill tự cài + backfill nợ)"
```
Nếu llmwiki missing: dừng, gợi ý chạy `new-project-setup`.
Nếu harness MISSING: chỉ BÁO (skill này read-only) — việc cài là quyết định của user.

**2. Đọc tổng quan:**
```bash
# Đọc theo thứ tự:
READ: llmwiki/wiki/index.md           # danh sách toàn bộ wiki pages
READ: llmwiki/wiki/log.md (20 entries mới nhất)   # recent changes
READ: llmwiki/wiki/concepts/Architecture.md       # nếu tồn tại
```

**3. Tìm 3 concepts được reference nhiều nhất:**
```bash
grep -roh '\[\[.*?\]\]' llmwiki/wiki/ | sort | uniq -c | sort -rn | head -5
```
→ Pick 3 concept files từ danh sách, READ từng file.
Fallback nếu kết quả rỗng:
```bash
ls -t llmwiki/wiki/concepts/ | head -3
```
READ 3 files đầu theo mtime.

**4. CHECK tools:**
```bash
ls .claude/commands/ 2>/dev/null || echo "Claude skills: not installed"
ls ~/.agents/skills/ 2>/dev/null  || echo "Agent skills: not installed"
```
Nếu thiếu: `INVOKE: sync-template` (step 7 auto-installs tất cả).

**5. Synthesize & report:**
In ra:
- Project là gì, stack chính (từ Architecture.md hoặc index)
- 3 điểm kỹ thuật quan trọng nhất (từ concepts vừa đọc)
- Recent changes & open items (từ log.md)
- Skills state (installed / missing)
- Nếu có gaps lớn trong wiki: đề nghị `INVOKE: onboard-codebase` cho phần đó

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | `llmwiki/.claude/hooks/pre_tool_use.py` không có | báo "harness: MISSING", đề xuất user gọi `/harness-update` | không tự cài | W02 |
| B02 | recovery | grep `[[...]]` rỗng | fallback `ls -t llmwiki/wiki/concepts/` lấy 3 file mới nhất, READ 3 file đầu theo mtime | concepts/ rỗng → báo wiki trống | W04 |
| B03 | conditional_required | thiếu skills (Claude hoặc Agent) | gợi ý `INVOKE: sync-template` | — | W05 |

### Validation và stopping
Báo cáo W05 phải có đủ 5 mục; mọi khẳng định truy về file wiki đã đọc. Dừng ngay ở W01 nếu llmwiki thiếu.

### Examples
- **Positive:** repo có `llmwiki/` + harness → W01 "ok" + "harness: ON" → đọc index/log/Architecture → 3 concept top-link → báo cáo "Project X, stack Next.js + Postgres; 3 điểm kỹ thuật…; recent: 5 entry log; skills: installed".
- **Boundary/failure:** repo không có `llmwiki/wiki/index.md` → in "llmwiki missing — run new-project-setup instead" và dừng, không đọc tiếp, không bịa tổng quan.

### Delivery — Output Report

After all main skill tasks complete, write a propose draft to the wiki.

#### Steps

**1. Build the filename:**
- Format: `DDMMYY-<ten>.md`
- `DDMMYY` = today (e.g., `020626` for 2 June 2026)
- `<ten>` = 2–4 kebab-case words summarising what was done (e.g., `landing-page-coteccons`, `brand-kit-fintech`, `ingest-auth-spec`)

**2. Write** `llmwiki/wiki/sources/draft/DDMMYY-<ten>.md`:

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
- **Draft:** `wiki/sources/draft/DDMMYY-<ten>.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
```

**3. Update wiki index & log:**
- `llmwiki/wiki/index.md` — append one row: `| [DDMMYY-<ten>](sources/draft/DDMMYY-<ten>.md) | draft | YYYY-MM-DD |`
- `llmwiki/wiki/log.md` — append: `## YYYY-MM-DD — <skill-name> — <ten>`

> Skip only when the skill produces zero artefacts and zero decisions (e.g., a pure display mode like `/caveman-stats`).