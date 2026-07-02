---
name: impact-check
description: Map all callers and dependents of a symbol before modifying shared code
---

# Skill: impact-check

## Purpose
Before modifying any symbol (function, class, variable, config key), map all dependents so no callers blindsided.

## When to use
- Before editing shared utility, base class, or widely-imported module
- Before renaming or deleting anything
- As first step of `safe-change` or `propose`

## Steps
1. Identify exact symbol(s) to change.
2. Search entire codebase for all imports, calls, references to each symbol.
3. For each reference: note file path, line number, how it uses symbol.
4. Classify each reference:
   - **Direct** — calls or imports symbol itself
   - **Indirect** — depends on behaviour symbol produces (e.g. reads its output)
5. Report full list. If zero references found outside file, state explicitly.
6. Flag any reference in test file separately — those must update or give false confidence.
7. If symbol not yet documented in `wiki/`, note as gap — do not create entry now. Wiki entries only written after code committed (see `verify-before-commit`).

## Rules
- Do not modify anything during this skill — output only.
- If codebase large, search by symbol name AND file pattern (e.g. all `*.ts` files).
- Do not assume symbol unused because no direct callers — check indirect dependents too.

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
