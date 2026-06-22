---
name: query
description: Synthesize answer from wiki; persist new insights as wiki entries
---

# Skill: query

## Purpose
Answer question by synthesizing wiki knowledge. Valuable findings not in wiki become new pages, compounding knowledge over time.

## When to invoke
When user asks question requiring synthesis across multiple wiki pages or raw sources.

## Steps
1. Identify relevant wiki pages. List them.
2. Read each relevant page in full.
3. If answer needs info not in wiki, check `raw/` for unprocessed sources.
4. Synthesize and answer directly.
5. Evaluate: does answer contain non-obvious insight, connection, or conclusion not already in wiki?
   - If yes: create new wiki page (concept or source), update `wiki/index.md`, log in `wiki/log.md`.
   - If no: skip.
6. Append to `wiki/log.md`: `## YYYY-MM-DD — query — <question summary>` with note on whether new page created.

## Rules
- **OKF v0.1 (R9):** any new wiki page starts with a YAML frontmatter block (`---`) with a non-empty `type`; copy the matching `_template.md` and keep the `## Origin` section.
- Never invent facts. Synthesize from wiki and `raw/` only.
- Query revealing gap (missing entity, missing concept) should trigger `ingest` of relevant `raw/` source if one exists.

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
