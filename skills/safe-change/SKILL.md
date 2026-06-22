---
name: safe-change
description: Modify shared code without breaking existing callers
---

# Skill: safe-change

## When to use
Modifying any function, class, or module called from more than one place.

## Steps

1. Run `impact-check` skill — get list of all callers and dependents.
2. Note current observable behaviour (return values, side effects).
3. Make minimal change. Don't touch adjacent code.
4. For each caller from step 1: verify backward-compatible or explicitly update caller.
5. `CHECK: ls <test-dir>/*<module>* 2>/dev/null | head -3` — if tests exist, `RUN: <test-cmd>`. If none, note explicitly in commit message.
6. Confirm: "Changed X. Verified Y still works." Then invoke `verify-before-commit`.

## Rules
- Backward compatibility impossible → surface to user before proceeding.
- Touch only what task requires — no opportunistic refactoring.
- No tests exist → acceptable to note — don't add tests outside task scope.

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
