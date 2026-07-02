---
name: lint
description: Periodic wiki health check — orphans, missing links, contradictions, stale, index gaps
---

# Skill: lint

## When to invoke
After every 10 ingests, or when wiki stale/inconsistent.

## Steps

1. **Orphans** — `RUN: grep -rL "wiki/" --include="*.md" llmwiki/wiki/concepts/ llmwiki/wiki/entities/` → files not referenced anywhere. Flag each.

2. **Missing links** — scan pages for entity/concept names that exist as wiki files but not written as `[[wikilinks]]`. Fix in place.

3. **Contradictions** — compare claims about same entity across ≤2 pages at a time. Flag pairs (file:line vs file:line). Do NOT pick winner — flag for human review.

4. **Stale claims** — `RUN: grep -rl "raw/" --include="*.md" llmwiki/wiki/` → pages referencing raw/. Flag each.

5. **Index gaps** — `RUN: comm -23 <(find llmwiki/wiki -name "*.md" | sort) <(grep -o "llmwiki/wiki/[^)]*" llmwiki/wiki/index.md | sort)` → files missing from index. Add rows.

6. **Empty pages** — `RUN: for f in llmwiki/wiki/**/*.md; do [ $(wc -l < "$f") -lt 5 ] && echo "$f"; done` → flag for deletion or content.

7. **Missing Origin** — `RUN: grep -rL "## Origin" llmwiki/wiki/concepts/ llmwiki/wiki/entities/` → flag each as incomplete.

8. Append to `llmwiki/wiki/log.md`: `## YYYY-MM-DD — lint` with issues found/fixed vs flagged.

## Rules
- Fix automatically: missing links (step 2), index gaps (step 5).
- Flag, not resolve: contradictions, orphans, empty pages — need human decision.

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
