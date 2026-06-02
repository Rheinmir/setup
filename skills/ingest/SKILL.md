---
name: ingest
description: >-
  Process a new file in raw/ and distill its knowledge into wiki pages
---

# Skill: ingest

## Purpose
Process a new file in `raw/` and distill its knowledge into the wiki. Each ingest typically touches 10-15 wiki files.

## When to invoke
Automatically when a new file appears in `raw/`.

## Steps
1. Read the source file in `raw/` completely. Do not summarize prematurely.
2. Extract key takeaways: facts, decisions, entities, concepts introduced by the source.
3. For each entity or concept found:
   - If it already has a wiki page: open it and add/revise relevant information.
   - If it does not exist: create the appropriate file in `wiki/concepts/` or `wiki/entities/`.
4. Create or update a summary page in `wiki/sources/` for the source itself (link back to the `raw/` file).
5. Add `[[wikilinks]]` between all newly created or updated pages.
6. Update `wiki/index.md` for every file created or modified.
7. Append to `wiki/log.md`: `## YYYY-MM-DD — ingest — <filename>` with a bullet list of all pages touched.

## Rules
- Never modify the file in `raw/`. Read only.
- Do not create a wiki page unless the source actually introduces that entity or concept.
- Prefer updating an existing page over creating a duplicate.


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