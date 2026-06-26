---
name: join-project
description: Orient nhanh vào dự án đang chạy đã có llmwiki — read-only, không ghi wiki
---

# Skill: join-project

## When to use
Agent hoặc dev mới vào giữa dự án đã có `llmwiki/` — cần hiểu context nhanh mà không re-phân tích toàn bộ code.

## Steps

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

## Rules
- Read-only — không tạo hoặc sửa bất kỳ wiki file nào
- Không setup RTK hay tools khác — đó là việc của `new-project-setup`
- Nếu wiki trống hoặc stale: nói rõ, đừng fabricate context


---

## Output Report

After all main skill tasks complete, write a propose draft to the wiki.

### Steps

**1. Build the filename:**
- Format: `DDMMYY-<ten>.md`
- `DDMMYY` = today (e.g., `020626` for 2 June 2026)
- `<ten>` = 2–4 kebab-case words summarising what was done (e.g., `landing-page-coteccons`, `brand-kit-fintech`, `ingest-auth-spec`)

**2. Write** `llmwiki/wiki/sources/draft/DDMMYY-<ten>.md`:

```
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