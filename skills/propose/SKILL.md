---
name: propose
description: >-
  Plan a feature before coding — create a draft in wiki/sources/draft/ and stop for approval
---

# Skill: propose

## Purpose
Plan a new feature or change before writing any code. Surfaces impact on existing functionality and gets alignment before implementation.

## When to use
- Any new feature, endpoint, component, or behaviour is requested
- A change touches shared/core code
- The scope is unclear or could be interpreted multiple ways

## Steps
1. Restate the request in one sentence to confirm understanding.
2. List every existing file, function, or module that will be affected or must change.
3. List every existing feature or behaviour that could break as a side effect.
4. Propose the minimal implementation plan as numbered steps.
5. State what success looks like (verifiable criteria).
6. Create a draft file at `llmwiki/wiki/sources/draft/DDMMYY-feature-name-module.md` (e.g. `260425-new-approval-button-fe.md`) containing the proposal output from steps 1–5. Add a row to `llmwiki/wiki/index.md` and append to `llmwiki/wiki/log.md`.
7. STOP. Do not write any code. Wait for the user to approve or redirect.

## Rules
- Never begin implementation during this skill.
- If the impact list is empty, state explicitly "No existing code affected."
- If multiple approaches exist, present them with tradeoffs — do not pick silently.


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