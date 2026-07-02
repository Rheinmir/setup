---
name: web-clone
description: Clone a website — two modes. SNAPSHOT = a faithful, self-contained offline copy of a page (HTML+CSS+JS+images in one file, exact bytes, SingleFile-style). RECONSTRUCT = AI reverse-engineer the page into a clean editable Next.js/Tailwind codebase (design tokens → component specs → parallel builders → visual-diff QA, the ai-website-cloner-template method). Use when the user wants to "clone this site", copy a page's design/UI + interactions, mirror a layout, save offline, or rebuild a site as editable code. Built-now-adapt-later: snapshot builtin works now; faithful live capture + the reconstruct pipeline are one-config engine adapters.
---

# Skill: web-clone

Two honestly-different jobs. Pick the mode first.

| Mode | Output | Use when | Engine |
|------|--------|----------|--------|
| **snapshot** | ONE self-contained `.html` (exact bytes, offline) | archive / faithful copy / "lưu y hệt offline" | builtin inliner · SingleFile CLI · monolith |
| **reconstruct** | clean **Next.js + Tailwind** codebase (editable) | "rebuild as code I can edit" / "clone giao diện thành code" | the ai-website-cloner-template pipeline |

Mode + engine live in `harness/web-clone.config.yaml` (`verified:false` — the live-capture engine
and reconstruct fidelity are the quarantined unknowns).

## Mode A — snapshot (faithful 1-file copy)
1. **Local page already downloaded:** offline, no key —
   `python3 harness/scripts/web-clone.py inline <page.html> --out clone.html`
   (inlines local `<link>` CSS, `<script src>` JS, images as data-URI → one file).
2. **Live URL, faithful:** set `engine: singlefile-cli` (`npm i -g single-file-cli`, keeps scripts)
   or `monolith` (Rust), then `web-clone.py url "<URL>" --out clone.html`.
3. **JS interactions = best-effort** across all snapshot engines (the quarantined unknown).

## Mode B — reconstruct (→ editable Next.js, the ai-website-cloner-template method)
This is NOT a byte-copy — it reverse-engineers the page into a fresh, clean codebase. Method
(distilled from JCodesMore's `ai-website-cloner-template`, ~6k★; see Related):
1. **Reconnaissance** — browser-MCP/Computer-Use: full-page screenshots @desktop 1440 + mobile 390;
   extract global design tokens (fonts, colors, favicons); sweep scroll/click/hover to find every
   interactive behavior; map page topology.
2. **Foundation** — `layout.tsx` fonts, `globals.css` color tokens + animations, TS interfaces,
   inline SVGs → React icon components, Node asset-download script → `public/`.
3. **Component spec & dispatch** — per section: read EXACT `getComputedStyle()` values (never
   estimate) → write `docs/research/components/<name>.spec.md` (the builder contract: DOM, computed
   styles, state transitions, verbatim content, asset paths, breakpoints) → dispatch **parallel
   builder subagents** (one per sub-component for complex sections; ≤~150 lines spec each).
4. **Assembly** — import components into `app/page.tsx`; wire scroll-snap / Lenis / IntersectionObserver.
5. **Visual-QA diff** — compare clone vs original @desktop+mobile, test every interactive state, fix
   discrepancies by re-extracting. Builders verify `npx tsc --noEmit`; main `npm run build` per merge.

Stack: Next.js + TypeScript + Tailwind v4 + shadcn/ui. Dispatch builders via overstack `/orchestration`
or the Agent tool.

## Rules
- State the mode + be honest: snapshot builtin = LOCAL resources only; faithful live capture needs an
  engine; reconstruct fidelity depends on extraction quality — never claim pixel+behavior perfection.
- Respect copyright / Terms — clone for reference/offline/learning, not to republish someone's site.
- Self-test (snapshot core): `python3 harness/scripts/web-clone.py --self-test`.

## Related
- `harness/scripts/web-clone.py` + `harness/web-clone.config.yaml` (engine/mode adapter).
- **Reconstruct method:** `github.com/JCodesMore/ai-website-cloner-template` (the 5-phase pipeline above).
- **Snapshot engines:** SingleFile (`github.com/gildas-lormeau/SingleFile`), monolith.
- `/web-crawl` (page → markdown text), `/computer-use` + `/orchestration` (recon + parallel builders).
