---
name: docs-site-macos
description: >
  Build a beautiful macOS-inspired documentation site (single HTML file) with glassmorphism cards,
  animated SVG diagrams, traffic-light window chrome, and per-section color theming.
  Trigger when the user wants to create a docs site, landing page, showcase, portfolio, guide,
  tutorial site, feature overview, or product documentation — especially when they mention
  wanting it to look "clean", "modern", "Apple-like", "macOS style", "glass", "frosted",
  "animated diagrams", or "single HTML file". Also use when the user has multiple markdown
  files and wants them rendered into a cohesive visual HTML page with sections.
  If the user says "6 file" or wants separate pages per topic, generate one HTML file per
  wiki file (index.html as overview + N topic files), NOT a single combined page.
---

# macOS Docs Site Builder

Build a **single-file HTML documentation site** with macOS-inspired design system.
Output is a self-contained `.html` file (no JS libraries, no build step).

## Design System

### Color Palette

Base: `#f2f0f7` (purple-ish light gray)
Text: `#0f0f12` / `#4a4a55`
Glass: `rgba(255,255,255,.7)` with `backdrop-filter: blur(8px)`
Border: `rgba(255,255,255,.6)` or `rgba(0,0,0,.06)`

### Section Color Cycle

Sections cycle through this accent palette in order. Pick the Nth accent for the Nth section,
wrapping around if there are more sections than accents:

```css
/* Cycle (6 accents, repeat as needed) */
#sec-0 .tag { background: rgba(99,102,241,.12); color: #6366f1; }
#sec-0 .card h4 { color: #6366f1; } #sec-0 .section-header h2 { color: #4338ca; }
#sec-0 .card li::before { color: #6366f1; }
#sec-0 .section-bg::before { background: linear-gradient(180deg, rgba(99,102,241,.04) 0%, transparent 60%); }

#sec-1 { accent: #059669 emerald; dark: #047857; }
#sec-2 { accent: #d97706 amber; dark: #b45309; }
#sec-3 { accent: #db2777 pink; dark: #be185d; }
#sec-4 { accent: #0891b2 cyan; dark: #0e7490; }
#sec-5 { accent: #9333ea purple; dark: #7e22ce; }
/* then repeat #sec-6 = #sec-0, #sec-7 = #sec-1, ... */
```

**Full accent table:**

| Index | Accent | Dark (h2) | Gradient overlay |
|-------|--------|-----------|------------------|
| 0     | `#6366f1` indigo | `#4338ca` | `rgba(99,102,241,.04)` |
| 1     | `#059669` emerald | `#047857` | `rgba(16,185,129,.04)` |
| 2     | `#d97706` amber | `#b45309` | `rgba(245,158,11,.04)` |
| 3     | `#db2777` pink | `#be185d` | `rgba(236,72,153,.04)` |
| 4     | `#0891b2` cyan | `#0e7490` | `rgba(6,182,212,.04)` |
| 5     | `#9333ea` purple | `#7e22ce` | `rgba(168,85,247,.04)` |

For each section, use the accent for:
- `.tag` background (at 12% opacity)
- `.card h4` color
- `.card li::before` color (the `›` bullet)
- `.section-header h2` color (dark shade)

### Glassmorphism Cards

```css
.card {
  background: rgba(255,255,255,.7);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,.6);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,.06);
  padding: 20px;
}
```

Apply this same glass style to: `.diagram-box`, `table`, `.repo-card`, and the converter mockup.

### macOS Chrome Elements

The **repo card** and **converter mockup** use a macOS window header:
```html
<div class="chrome">
  <span style="width:12px;height:12px;border-radius:50%;background:#ff5f57"></span>
  <span style="width:12px;height:12px;border-radius:50%;background:#ffbd2e"></span>
  <span style="width:12px;height:12px;border-radius:50%;background:#28c840"></span>
  <div class="url-bar">...</div>
</div>
```

### Navigation

Fixed top nav with:
- `background: rgba(242,240,247,.82)` + `backdrop-filter: blur(24px) saturate(1.4)`
- Height 48px
- Active link: accent color + `rgba(99,102,241,.1)` background
- Scroll spy via IntersectionObserver watching `section[id]`

## Page Architecture

```
<nav>          — fixed top bar with section links
<hero>         — gradient title + subtitle
<repo-card>    — optional: link to source repo with chrome + collapse
<section id="sec-{i}">  — repeat for each topic (i = 0..N-1):
  class="section-bg s-bg{i}"
  .section-header  — .tag badge ("0{i+1} · Title") + h2 + p
  .diagram-box     — animated SVG (see below)
  .content-grid    — 2-column cards (Workflow + Use cases)
  .table-wrap      — optional comparison table
  footer link      — "Chi tiết: file.md"
<footer>
```

## Section-Bg Pattern

Each `<section>` gets two classes: `section-bg s-bgN` (N = section index mod 6).
The gradient overlay is a `::before` pseudo-element:

```css
.section-bg { position: relative; overflow: hidden; }
.section-bg::before { content: ''; position: absolute; inset: 0; pointer-events: none; }
/* Generate one .s-bgN::before per section index, cycling through 6 colors */
```

Section padding: `padding: 64px 24px 72px; max-width: 1100px; margin: 0 auto;`

### CSS Generator Pattern

Generate the per-section CSS dynamically. For N sections, generate N rule sets using `#sec-{i}` IDs:

```
For i in 0..N-1:
  accent = palette[i % 6]
  dark   = dark[i % 6]
  gradient = overlay[i % 6]

  #sec-{i} .tag { background: accent at 12%; color: accent; }
  #sec-{i} .card h4 { color: accent; }
  #sec-{i} .card li::before { color: accent; }
  #sec-{i} .section-header h2 { color: dark; }
  .s-bg{i}::before { background: linear-gradient(180deg, gradient 0%, transparent 60%); }


## Animated SVG Diagrams

Each diagram is an inline SVG (not external file) with `viewBox` for responsiveness.

### Key Animations (reusable CSS in `<defs><style>`)

```css
@keyframes flowArrow { 0% { stroke-dashoffset: 20; } 100% { stroke-dashoffset: 0; } }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: .4; } }
@keyframes float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
@keyframes glow { 0%,100% { filter: drop-shadow(0 0 4px rgba(...)); } 50% { filter: drop-shadow(0 0 12px rgba(...)); } }
@keyframes bounce { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
@keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0; } }
@keyframes orbit { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
@keyframes scanLine { 0% { transform: translateX(-40px); } 100% { transform: translateX(320px); } }
@keyframes stack { 0%,100% { opacity:.15; } 50% { opacity:.7; } }
```

Apply to SVG elements: `.flow` (dashed arrows), `.pulse` (nodes), `.float` (output badges), `.glow` (phone icon), `.drone` (bouncing), `.blink` (drone light), `.orbit-ring` (spinning product), `.cameraFlash` (strobe), `.scan` (scan line), `.stackAnim` (DICOM slices), `.center-pulse` (orbit core).

### SVG Box Styling

- **Nodes**: `rx="6"` or `rx="8"` rounded rects with `fill="rgba(255,255,255,.7)"` and colored stroke
- **Arrows**: `<line>` with `marker-end="url(#arrowN)"` using `<marker>` def, `stroke-width="2"`, and `.flow` class
- **Text**: `text-anchor="middle"`, `font-size="9-11"`, `font-weight="600"` for labels
- Use `font-family` from the page (`Inter, -apple-system, ...`)
- Always include `xmlns="http://www.w3.org/2000/svg"` on `<svg>`

## Collapse / Xem thêm

Animated expand/collapse section:

```html
<button class="collapse-toggle" onclick="toggleX()">
  <span class="arrow" id="arrowX">▶</span> Label
</button>
<div class="collapse-body" id="bodyX">
  <div class="collapse-body-inner">...</div>
</div>
```

CSS:
```css
.collapse-body {
  max-height: 0; overflow: hidden;
  transition: max-height .35s cubic-bezier(.4,0,.2,1), opacity .25s ease;
  opacity: 0;
}
.collapse-body.open { max-height: 800px; opacity: 1; }
.collapse-toggle .arrow { transition: transform .25s cubic-bezier(.4,0,.2,1); }
.collapse-toggle .arrow.open { transform: rotate(90deg); }
```

JS:
```js
function toggleX() {
  document.getElementById('bodyX').classList.toggle('open');
  document.getElementById('arrowX').classList.toggle('open');
}
```

## Responsive

```css
@media (max-width: 700px) {
  .content-grid { grid-template-columns: 1fr; }
}
```

## Scroll Spy

```js
const observer = new IntersectionObserver(entries => {
  let active = '';
  for (const entry of entries) {
    if (entry.isIntersecting) active = entry.target.id;
  }
  if (active) links.forEach(a => a.classList.toggle('active', a.getAttribute('href') === '#' + active));
}, { rootMargin: '-40% 0px -55% 0px' });
sections.forEach(s => observer.observe(s));
```

## Font

Use Inter from Google Fonts:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```
Font stack: `'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif`

## Output Path — CRITICAL

**ALWAYS write HTML files to `llmwiki/html/` inside the current project root.**

- Single file: `llmwiki/html/<slug>.html`
- Multi-file: `llmwiki/html/index.html` + `llmwiki/html/<slug>.html`
- NEVER write to the project root or any other directory.
- If `llmwiki/html/` does not exist, create it first.

## Auto-Host

After creating the HTML file(s), ALWAYS start a local HTTP server for preview:

```bash
cd <project-root>
kill -9 $(lsof -ti :8765) 2>/dev/null
nohup npx serve -p 8765 > /tmp/serve.log 2>&1 &
```

Notify user: open `http://localhost:8765/llmwiki/html/<file>.html`

If port 8765 is already in use, skip (server already running).

## Multi-File Mode

When generating separate pages per wiki file:
- Create an `index.html` overview page (card grid linking to all N pages)
- Create `{slug}.html` for each wiki file (slug derived from filename)
- Each page shares the same CSS design system but uses its section accent color
- Each page has a nav bar linking to all other pages (highlight current page)
- Each page has its own animated SVG diagram based on the topic content

## Best Practices

- ALWAYS inline SVG directly in the HTML (not external files)
- ALWAYS use `clamp()` for hero heading size: `font-size: clamp(32px,5vw,56px)`
- ALWAYS make each `<section>` self-contained with accent colors from the cycle by its index (use `#sec-{i}` CSS rules)
- Keep SVG viewBox widths consistent (900) across diagrams for visual harmony
- Use relative `../file.md` links for "Chi tiết" footers pointing to companion markdown files
- The hero heading gradient should use 3 stops: `linear-gradient(135deg, #6366f1, #a855f7, #ec4899)`
- Nav logo gradient: `linear-gradient(135deg, #6366f1, #a855f7)`
- Number of sections is variable — cycle through the 6-color palette with modulo (`i % 6`)
- ALWAYS start an auto-host server after writing the HTML file (see Auto-Host section above)


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