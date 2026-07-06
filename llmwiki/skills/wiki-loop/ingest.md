---
name: ingest
description: Process new file in llmwiki/raw/ and distill into wiki pages
---

# Skill: ingest

## Purpose
Process new file in `raw/`, distill knowledge into wiki. Each ingest touches 10-15 wiki files.

## When to invoke
Automatically when new file appears in `raw/`.

## Steps
1. Read source file in `raw/` completely. No premature summarizing.
2. Extract key takeaways: facts, decisions, entities, concepts from source.
   Rồi lập **docs-impact-plan** trước khi ghi (distill openwiki 060726): `điểm mới trong nguồn → trang bị ảnh hưởng → sửa/tạo gì → vì sao`. Trang không truy được về một điểm cụ thể trong nguồn thì KHÔNG đụng.
3. For each entity or concept:
   - Has wiki page: open it, add/revise relevant info.
   - No page: create in `wiki/concepts/` or `wiki/entities/`.
4. Create or update summary page in `wiki/sources/` for source (link back to `raw/` file).
5. Add `[[wikilinks]]` between all new/updated pages.
6. Update `wiki/index.md` for every file created or modified.
7. Append to `wiki/log.md`: `## YYYY-MM-DD — ingest — <filename>` with bullet list of all pages touched.

## Rules
- **OKF v0.1 (R9):** every wiki page starts with a YAML frontmatter block (`---`) carrying a non-empty `type` (e.g. `concept`, `entity`, `source`) plus optional `title`/`tags`/`timestamp`/`resource`. Copy the matching `_template.md`. Keep the `## Origin` body section (R2).
- Never modify file in `raw/`. Read only.
- No wiki page unless source actually introduces that entity or concept.
- Prefer updating existing page over creating duplicate.
- **Canonical home**: mỗi concept một trang chính chủ — chi tiết nằm ở đó, trang khác chỉ nhắc ngắn + `[[wikilink]]`; đừng nhân bản cùng giải thích ra nhiều trang.
- **Surgical trên trang có sẵn**: cập nhật = thay đúng câu lỗi thời, không viết lại phần còn đúng; cấm edit formatting-only (reformat bảng/dòng trống/wording khi nội dung không sai).

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
