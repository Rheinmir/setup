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
6. Create draft file at `llmwiki/wiki/sources/draft/DDMMYY-feature-name-module.md` (e.g. `260425-new-approval-button-fe.md`) containing proposal output from steps 1–5. Add row to `llmwiki/wiki/index.md` and append to `llmwiki/wiki/log.md`.
7. Create the **companion HTML sequence diagram** at `llmwiki/html/DDMMYY-feature-name-seq.html` — animated sequence diagram(s) of how the code/data will flow through the proposed change (one diagram per flow: happy path, fail/block path, async path if any). This is what the user reviews at the gate. Requirements:
   - Lifelines = participants (user, services, hooks, DB…); messages appear **step-by-step (animated)**, auto-loop, click to pause
   - 2-color convention: indigo = existing/legacy components, emerald = components this proposal adds/changes
   - Link both ways: the `.md` draft links to the `.html` and vice versa
8. STOP. No code. Show the draft content + the HTML preview URL. Wait for user to approve or redirect.

## Rules
- Never begin implementation during this skill.
- The proposal is a PAIR: `.md` (detail, diffable) + `.html` (animated sequence diagram for gate review). Missing either = incomplete proposal.
- If impact list empty, state explicitly "No existing code affected."
- If multiple approaches exist, present with tradeoffs — do not pick silently.