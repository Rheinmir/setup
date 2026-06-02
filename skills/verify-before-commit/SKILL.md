---
name: verify-before-commit
description: Gate every commit — typecheck, lint, smoke, then promote draft to wiki
---

# Skill: verify-before-commit

## When to use
After completing any implementation task, before `git commit`.

## Steps

**Pre-commit:**
1. `RUN: <type-check-cmd>` — detect from repo: `npx tsc --noEmit` (package.json) / `go build ./...` (go.mod). Fix all errors.
2. `RUN: <lint-cmd>` — detect: `npx eslint src/` / `go vet ./...`. Fix errors; note warnings.
3. `RUN: <test-cmd>` — detect: `npm test` / `go test ./...`. Fix failures.
4. Smoke check: manually verify the golden path works end-to-end.
5. Commit with message describing *why*, not *what*.

**Post-commit — mandatory, never skip:**
6. Find the draft in `llmwiki/wiki/sources/draft/` matching this feature.
   - Promote it to `llmwiki/wiki/concepts/` or `llmwiki/wiki/sources/` (permanent).
   - Add `## Origin` section: `Draft: <path>` / `Commit: <hash> — <msg>` / `Date: YYYY-MM-DD`
   - `CHECK: grep -l "## Origin" <promoted-file>` — must return the file.
7. `RUN: echo "promoted" >> llmwiki/wiki/log.md` — then edit log properly; update `llmwiki/wiki/index.md`.

> No corresponding draft (hotfix/refactor)? Note "no draft — <reason>" in log.md and skip step 6.

All steps mandatory. No exceptions.


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