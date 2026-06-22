---
name: propose
description: Plan a feature before coding — draft in wiki/sources/draft/, stop for approval
---

# Skill: propose

## Purpose
Plan feature/change before writing code. Surfaces impact on existing functionality, gets alignment before implementation.

## When to use
- New feature, endpoint, component, or behaviour requested
- Change touches shared/core code
- Scope unclear or multi-interpretable

## Steps
1. Restate request in one sentence to confirm understanding.
2. List every existing file, function, or module affected or must change.
3. List every existing feature or behaviour that could break as side effect.
4. Propose minimal implementation plan as numbered steps.
5. State what success looks like (verifiable criteria).
6. Create draft file at `llmwiki/wiki/sources/draft/DDMMYY-feature-name-module.md` (e.g. `260425-new-approval-button-fe.md`) containing proposal output from steps 1–5. Draft MUST include (enforced by validator R7 — blocked at write-time and commit if missing):
   - `## Plan` — tasks as `- [ ]` checklist items
   - `## Agent Task Assignment` — table `| Task | Agent (CLI) | Lý do chọn | Status |`, one row per task, **no empty Agent cell**, Status=pending. Pick agents by cost table; if all on one agent, say why.
   - `**Sequence diagram:**` link to companion `.html` (must exist on disk)
   Add row to `llmwiki/wiki/index.md` and append to `llmwiki/wiki/log.md`.
7. Create the **companion HTML sequence diagram** at `llmwiki/html/DDMMYY-feature-name-seq.html` — **one animated diagram PER task in Plan** (R7 checks: `diagram-box` count ≥ task count). Requirements:
   - Each diagram titled by its task + badge naming the assigned agent
   - Lifelines = participants; messages appear **step-by-step (animated)**, auto-loop, click to pause
   - 2-color: indigo = existing, emerald = added/changed; amber = blocked/fail branches
   - Link both ways: `.md` ↔ `.html`
8. STOP. No code. Show the draft content + the HTML preview URL. Wait for user to approve or redirect.

## Rules
- **OKF v0.1 (R9):** the draft starts with a YAML frontmatter block (`---`) with `type: draft` (+ optional `title`/`status`/`tags`/`timestamp`); copy `sources/draft/_template.md`. Keep `**Status:** proposed` in the body so R7 can gate it.
- Never begin implementation during this skill.
- The proposal is a PAIR: `.md` + `.html` (one diagram per task). Validator R7 blocks incomplete proposals at write and commit — fix before asking for approval.
- If impact list empty, state explicitly "No existing code affected."
- If multiple approaches exist, present with tradeoffs — do not pick silently.

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
