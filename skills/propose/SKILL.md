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
6. Create a draft file at `llmwiki/wiki/sources/draft/DDMMYY-feature-name-module.md` (e.g. `260425-new-approval-button-fe.md`) containing the proposal output from steps 1–5. The draft MUST include (enforced by validator R7 — an incomplete proposal is blocked at write-time and at commit):
   - `## Plan` — tasks as `- [ ]` checklist items
   - `## Agent Task Assignment` — table `| Task | Agent (CLI) | Lý do chọn | Status |`, one row per task, **no empty Agent cell**, Status=pending. Pick agents by the cost table (OpenCode big-pickle $0 for cheap/mechanical work, Claude for architectural/risky work, agy/kiro per their strengths); if everything stays on one agent, say why.
   - `**Sequence diagram:**` link to the companion `.html` (must exist on disk)
   Add a row to `llmwiki/wiki/index.md` and append to `llmwiki/wiki/log.md`.
7. Create the **companion HTML sequence diagram** at `llmwiki/html/DDMMYY-feature-name-seq.html` — **one animated sequence diagram PER task in the Plan** (R7 checks: number of `diagram-box` ≥ number of tasks). This is what the user reviews at the gate. Requirements:
   - Each diagram titled by its task + a badge naming the agent assigned to it
   - Lifelines = participants (user, services, hooks, DB…); messages appear **step-by-step (animated)**, auto-loop, click to pause
   - 2-color convention: indigo = existing/legacy components, emerald = components this proposal adds/changes; amber = blocked/fail branches
   - Link both ways: the `.md` draft links to the `.html` and vice versa
8. STOP. Do not write any code. Show the draft content + the HTML preview URL. Wait for the user to approve or redirect.

## Rules
- Never begin implementation during this skill.
- The proposal is a PAIR: `.md` (detail, diffable) + `.html` (one sequence diagram per task). Missing either = incomplete — validator R7 will block the write and the commit, so fix before asking for approval.
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