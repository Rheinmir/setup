---
name: onboard-codebase
description: Deep codebase analysis — populate wiki with architecture, concepts, entities
---

# Skill: onboard-codebase

## Purpose
Analyze unmapped codebase, extract technical/business context, populate Wiki per project standards.

## When to use
- Installing agentic setup into legacy/existing project.
- Wiki outdated or has context gap from recent code changes.

## Steps
1. **Infrastructure Audit**:
   - Map directory structure.
   - Identify tech stack, entry points, build/deploy scripts.
   - Store in `llmwiki/wiki/entities/project-structure.md`.
2. **Deep Code Analysis**:
   - Scan for core domain logic (Services, Models, Controllers).
   - Identify patterns (Repository, Event-driven, etc.).
   - Extract Concepts for `llmwiki/wiki/concepts/`.
3. **Frontend & Style Audit** *(skip if no frontend)*:
   - Identify UI framework (Next.js, React, Vue, etc.) and CSS approach (Tailwind, CSS Modules, styled-components, SCSS).
   - Extract design tokens: color palette, typography scale, spacing, breakpoints — from `tailwind.config.*`, CSS variables, or theme files.
   - Identify component library (shadcn/ui, MUI, Ant Design, Radix, Headless UI, etc.) and local wrappers.
   - Trace global styles: `globals.css`, base layout files, font loading strategy.
   - Document component naming conventions (PascalCase, feature-folder, colocated stories, etc.).
   - Note UI state management (Zustand, Jotai, Context, Redux, etc.) and data-fetching pattern (React Query, SWR, server actions, etc.).
   - Capture routing conventions (file-based, nested layouts, auth guards).
   - Store in `llmwiki/wiki/concepts/fe-style.md`.
4. **Business Logic Extraction**:
   - Reverse-engineer user stories and business rules from code.
   - Generate/Update `AGENT-business.md`.
5. **Entity Cataloging**:
   - List internal services, external APIs, database tables.
   - Create entries in `llmwiki/wiki/entities/`.
6. **Knowledge Injection**:
   - Synthesize into Wiki structure.
   - Update `llmwiki/wiki/index.md` and `llmwiki/wiki/log.md`.
7. **Final Verification**:
   - Run `lint` on generated wiki — check for contradictions.

## Rules
- ALWAYS read implementation to verify business claims.
- Cross-reference `README.md`/comments but prioritize truth in code.
- Focus on "Why" and "How" at code level, not just "What".
- NEVER overwrite existing manual wiki entries without checking `## Origin` section.
- **OKF v0.1 (R9):** mọi trang wiki bắt đầu bằng YAML frontmatter (`---`) có `type` không rỗng (`concept`/`entity`/`source`) — copy `_template.md` tương ứng. Giữ `## Origin` (R2).
- For `fe-style.md`: record actual values (hex codes, px/rem sizes, class names), not descriptions — goal is reproducible visual style without guessing.

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
