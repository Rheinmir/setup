---
type: draft
title: "Audit + fix docs-site-macos design system"
status: proposed
tags: [redesign-existing-projects, output-report]
proposed: 2026-06-30
id: 300626-audit-fix-docs-site-macos
---

# 300626-audit-fix-docs-site-macos
**Type:** draft
**Status:** proposed
**Tags:** redesign-existing-projects, output-report
**Proposed:** 2026-06-30

## What
Audited the `docs-site-macos` skill's design system against the `/redesign-existing-projects` checklist and applied 8 defect fixes + a11y/head hardening to BOTH mirrored copies (content parity preserved).

## Output
Findings ranked by impact, then fixed in place. The skill was already strong (tiered glass, refraction plane, tinted nav shadow, varied radius, noise texture) — fixes target what it did NOT cover:

1. **Focus ring** — added global `:focus-visible` ring (custom nav/buttons/checkboxes had none — keyboard a11y).
2. **`<head>` meta + favicon** — required `viewport` (Responsive section was dead on mobile without it), `title`/`description`/`theme-color`, inline data-URI favicon.
3. **Collapse no longer clips** — replaced magic `max-height:800px` cap with JS `scrollHeight` measurement + resize re-measure.
4. **Interactive-prototype self-contained** — removed Tailwind CDN + Inter contradiction; aligned to system fonts + inline CSS + blue/white glass palette.
5. **Removed duplicated Output Report block** (dead content, 48 lines).
6. **Blue-tinted shadows** on `.card`/`.diagram-box` (were pure black on a blue field).
7. **Smooth scroll + `scroll-margin-top`** for anchor nav (was instant jump, sections hid under top edge).
8. **`prefers-reduced-motion`** broadened from body-orbs-only to a global guard (ripple/float/pulse/flowArrow/mind-map).

Plus folded-in: skip-link + `<main>` landmark, `role="img"`/`<title>` guidance for informative SVG, `tabular-nums` on tables/diagram figures, `text-wrap: balance/pretty` for headline orphans.

Accepted (intentional, not defects): 6-accent section cycle (well-contained to tag/h4/bullet), system-font stack (self-contained constraint forbids webfonts), dark code panels in a light page (syntax convention).

## Files
| File | Action |
|------|--------|
| `skills/docs-site-macos/SKILL.md` | modified |
| `llmwiki/skills/utils/docs-site-macos.md` | modified (kept byte-identical to canonical) |
| `skills/cursor-animated-sites/SKILL.md` (+ mirror) | modified — pointer to inherit docs-site-macos a11y/head section |
| `skills/md-to-html/SKILL.md` (+ mirror) | modified — added "Output requirements (a11y)" block |
| `skills/uat-nonit-testcase/SKILL.md` (+ mirror) | modified — viewport meta + tabular-nums + focus ring |
| `llmwiki/.claude/hooks/stop.py` | modified — auto-run `sync-skills.py` at end of any turn touching a skill (close transient mirror-staleness gap) |
| `llmwiki/wiki/draft/uiux/300626-audit-fix-docs-site-macos.md` | created |

## Parity strategy (decision)
The question "generate mirror at install vs commit it from repo" was resolved in favour of the **existing committed-mirror + gate** design:
- `skills/<name>/SKILL.md` is the single source of truth; `harness/scripts/sync-skills.py` generates the byte-identical `llmwiki/skills/<loop>/<name>.md` mirror.
- Parity is enforced at three layers: `fdk-gate.py` ("skill mirror parity"), CI `.github/workflows/skills-sync.yml --check`, and now the `stop.py` hook auto-syncs on edit.
- **Generate-at-install was rejected**: generating the mirror during each project's install (from a possibly-stale global installer) is exactly what causes cross-project drift. Committing the generated mirror freezes parity at one point and ships it identically everywhere. The "old global vs new" concern is a versioning problem, not a parity one — handled by `health-check` / `sync-template`, not by changing the mirror strategy.

## Audit scope (what was deliberately NOT patched)
- `tour-guide` / `tour-guide-supademo` — in-app React/Next overlay, not a standalone page; host page owns meta/viewport. Its a11y lens is modal-specific (focus trap, Esc, `aria-modal`), separate from this checklist.
- `web-clone` — faithfully reproduces a source page's UI; imposing our design opinions would defeat its purpose.
- taste/imagegen/brandkit/stitch/high-end/minimalist/industrial/gpt-taste/image-to-code — prompt-guidance skills (design principles for the model), not concrete CSS emitters with these specific defects.

## Notes
- Invoked via: `/redesign-existing-projects` skill (audit mode) targeting `/docs-site-macos`, then extended across sibling HTML-emitting skills.
- All 65 canonical↔mirror skill pairs verified identical (`sync-skills.py --check` ✓). The two trees must always match in CONTENT (filename/path may differ).

## Origin
- **Draft:** `wiki/draft/uiux/300626-audit-fix-docs-site-macos.md`
- **Commit:** `9ecff0d` — fix(skills): a11y/head hardening cho skill sinh-HTML + auto-sync mirror
- **Date promoted:** 2026-06-30 (output-report draft — giữ ở draft/uiux theo /redesign-existing-projects, không promote sang concepts/)
