---
name: md-to-html
description: Render Markdown thành standalone HTML — Mermaid, Chart.js, styled tables, TOC
---

# Skill: md-to-html

## Purpose
Markdown → self-contained HTML: Mermaid diagrams, Chart.js, styled tables, code highlight, floating TOC.

## When to use
- Render/share `.md` as HTML
- Doc has steps, comparisons, numbers to visualize
- Need browser-ready professional output

## Trigger phrases
`/md-to-html`, `md2html`, `biến md thành html`, `render md`, `xuất html từ md`, `visualize doc`

## Output
HTML → `html/` dir (e.g. `html/tên-file.html`). NOT same dir as source `.md`.

## Full instructions
`~/.gemini/antigravity/skills/md-to-html/SKILL.md`

## Output requirements (don't ship a broken page)
The generated HTML must include, regardless of the external template:
- `<meta charset="utf-8">` + `<meta name="viewport" content="width=device-width, initial-scale=1">` and a real `<title>` — without viewport the TOC/tables overflow on mobile.
- `:focus-visible{outline:2px solid <accent>;outline-offset:2px}` so the floating-TOC links and any buttons show a keyboard focus ring.
- `font-variant-numeric:tabular-nums` on `table` (number columns must not jiggle).
- `@media(prefers-reduced-motion:reduce)` to skip Mermaid/Chart entry animation and set `scroll-behavior:auto`; add `html{scroll-behavior:smooth}` + `scroll-margin-top` so TOC anchor jumps glide and headings don't hide under any sticky header.
- A favicon (inline data-URI is fine) and `alt`/`<title>` on informative diagrams.

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
