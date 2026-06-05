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

### Node-Draggable Diagrams (REQUIRED for every `.diagram-box`)

Every `.diagram-box` MUST be an interactive node graph, NOT a static or merely-pannable picture:

- **Drag each box (node) individually** — moving one table/step does NOT move the others. Connector lines re-route to follow the node automatically.
- **Drag empty background** = pan the whole canvas.
- **Wheel** = zoom toward the cursor. **Double-click / ⟲ reset** = restore node positions + canvas.
- **`.diagram-box` is vertically resizable** (CSS `resize`) so the container expands smoothly.

This is auto-detected from the authored SVG — **no SVG markup changes needed**. The JS treats every `<rect>` ≥ 70×30 as a node, adopts the `<text>`/small-`<rect>` children whose coords fall inside that rect, wraps them in a `<g class="dnode">`, and binds each `<line>` endpoint to the nearest node so connectors track movement. Coordinate conversion uses `getScreenCTM().inverse()` so dragging stays accurate under zoom/pan.

CSS — replace the old static `.diagram-box` rule with:

```css
.diagram-box{background:rgba(255,255,255,.7);backdrop-filter:blur(8px);
  border:1px solid rgba(255,255,255,.6);border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,.06);
  padding:24px;margin:24px 0;
  position:relative;overflow:hidden;display:flex;flex-direction:column;
  resize:vertical;min-height:160px;transition:box-shadow .2s ease}
.diagram-box:hover{box-shadow:0 6px 28px rgba(0,0,0,.1)}
.diagram-viewport{position:relative;flex:1 1 auto;width:100%;overflow:hidden;cursor:grab;touch-action:none}
.diagram-viewport.grabbing{cursor:grabbing}
.diagram-viewport svg{width:100%;height:auto;display:block;overflow:visible;transform-origin:0 0;
  will-change:transform;user-select:none;-webkit-user-select:none}
.dnode{cursor:move}
.dnode>rect{transition:filter .15s ease}
.dnode:hover>rect:first-of-type{filter:drop-shadow(0 3px 8px rgba(0,0,0,.18))}
.diagram-hint{position:absolute;top:8px;right:12px;z-index:5;font-size:10px;color:#4a4a55;
  background:rgba(255,255,255,.75);border:1px solid rgba(0,0,0,.05);border-radius:20px;
  padding:3px 10px;white-space:nowrap;opacity:0;transition:opacity .2s;pointer-events:none}
.diagram-box:hover .diagram-hint{opacity:.9}
.diagram-reset{position:absolute;bottom:8px;right:10px;z-index:5;font-size:11px;
  background:rgba(255,255,255,.85);border:1px solid rgba(0,0,0,.08);border-radius:8px;
  padding:3px 9px;cursor:pointer;color:#4a4a55;opacity:0;transition:opacity .2s}
.diagram-box:hover .diagram-reset{opacity:1}
.diagram-reset:hover{background:#fff;color:#0f0f12}
.diagram-box::after{content:'';position:absolute;right:3px;bottom:3px;width:10px;height:10px;
  border-right:2px solid rgba(0,0,0,.18);border-bottom:2px solid rgba(0,0,0,.18);
  border-bottom-right-radius:3px;pointer-events:none}
```

JS — add once, call after DOM is parsed (script at end of `<body>`):

```js
function initDraggableDiagrams() {
  const NS = 'http://www.w3.org/2000/svg';
  const nearest = (nodes, x, y) => {
    let best = null, bd = 1e9;
    nodes.forEach(n => {
      const cx = Math.max(n.x, Math.min(x, n.x + n.w)), cy = Math.max(n.y, Math.min(y, n.y + n.h));
      const d = Math.hypot(x - cx, y - cy);
      if (d < bd) { bd = d; best = n; }
    });
    return bd <= 42 ? best : null;
  };
  document.querySelectorAll('.diagram-box').forEach(box => {
    const svg = box.querySelector('svg');
    if (!svg || box.dataset.draggable) return;
    box.dataset.draggable = '1';
    const vp = document.createElement('div'); vp.className = 'diagram-viewport';
    box.insertBefore(vp, svg); vp.appendChild(svg);
    const hint = document.createElement('div'); hint.className = 'diagram-hint';
    hint.textContent = '✥ kéo từng ô · kéo nền để pan · cuộn để zoom · kéo mép dưới để mở rộng';
    box.appendChild(hint);
    const reset = document.createElement('button'); reset.className = 'diagram-reset'; reset.textContent = '⟲ reset';
    box.appendChild(reset);

    // detect node rects + adopt children
    const allRects = [...svg.querySelectorAll('rect')];
    const nodes = allRects.filter(r => (+r.getAttribute('width')) >= 70 && (+r.getAttribute('height')) >= 30)
      .map(r => ({ rect: r, x: +r.getAttribute('x'), y: +r.getAttribute('y'),
        w: +r.getAttribute('width'), h: +r.getAttribute('height'), els: [r], tx: 0, ty: 0 }));
    const inNode = (px, py) => nodes.find(n => px >= n.x-1 && px <= n.x+n.w+1 && py >= n.y-1 && py <= n.y+n.h+1);
    [...svg.querySelectorAll('text')].forEach(t => {
      const x = parseFloat(t.getAttribute('x')), y = parseFloat(t.getAttribute('y'));
      if (isNaN(x) || isNaN(y)) return; const n = inNode(x, y); if (n) n.els.push(t);
    });
    allRects.forEach(r => { if (nodes.some(n => n.rect === r)) return;
      const x = +r.getAttribute('x'), y = +r.getAttribute('y'), w = +r.getAttribute('width')||0, h = +r.getAttribute('height')||0;
      const n = inNode(x+w/2, y+h/2); if (n) n.els.push(r); });
    nodes.forEach(n => { const g = document.createElementNS(NS, 'g'); g.setAttribute('class', 'dnode');
      n.rect.parentNode.insertBefore(g, n.rect); n.els.forEach(el => g.appendChild(el)); n.g = g; });

    // bind connector lines
    const links = [...svg.querySelectorAll('line')].filter(l => l.hasAttribute('x1') && l.hasAttribute('x2'));
    links.forEach(l => { l._x1=+l.getAttribute('x1'); l._y1=+l.getAttribute('y1'); l._x2=+l.getAttribute('x2'); l._y2=+l.getAttribute('y2');
      l._n1 = nearest(nodes, l._x1, l._y1); l._n2 = nearest(nodes, l._x2, l._y2); });
    const reroute = () => links.forEach(l => {
      if (l._n1) { l.setAttribute('x1', l._x1+l._n1.tx); l.setAttribute('y1', l._y1+l._n1.ty); }
      if (l._n2) { l.setAttribute('x2', l._x2+l._n2.tx); l.setAttribute('y2', l._y2+l._n2.ty); } });

    // auto-fit: viewBox (→ svg height → box) grows to contain dragged nodes ("sizing cùng")
    const vbBase = (svg.getAttribute('viewBox') || '0 0 900 200').split(/\s+/).map(Number);
    const fitViewBox = () => {
      const pad = 16;
      let minX = vbBase[0], minY = vbBase[1], maxX = vbBase[0]+vbBase[2], maxY = vbBase[1]+vbBase[3];
      nodes.forEach(n => { minX = Math.min(minX, n.x+n.tx-pad); minY = Math.min(minY, n.y+n.ty-pad);
        maxX = Math.max(maxX, n.x+n.w+n.tx+pad); maxY = Math.max(maxY, n.y+n.h+n.ty+pad); });
      svg.setAttribute('viewBox', `${minX} ${minY} ${maxX-minX} ${maxY-minY}`);
    };

    // pan + zoom + per-node drag
    let ptx=0, pty=0, scale=1;
    const applyCanvas = () => { svg.style.transform = `translate(${ptx}px,${pty}px) scale(${scale})`; };
    const toSvg = (cx, cy) => { const p = svg.createSVGPoint(); p.x=cx; p.y=cy; return p.matrixTransform(svg.getScreenCTM().inverse()); };
    let mode=null, node=null, start=null, t0=null, p0=null;
    vp.addEventListener('pointerdown', e => { vp.setPointerCapture(e.pointerId);
      const g = e.target.closest && e.target.closest('g.dnode');
      if (g) { mode='node'; node = nodes.find(n => n.g === g); start = toSvg(e.clientX, e.clientY); t0 = { x: node.tx, y: node.ty }; }
      else { mode='pan'; p0 = { x: e.clientX-ptx, y: e.clientY-pty }; vp.classList.add('grabbing'); } });
    vp.addEventListener('pointermove', e => {
      if (mode==='node') { const c = toSvg(e.clientX, e.clientY); node.tx = t0.x+(c.x-start.x); node.ty = t0.y+(c.y-start.y);
        node.g.setAttribute('transform', `translate(${node.tx},${node.ty})`); reroute(); }
      else if (mode==='pan') { ptx = e.clientX-p0.x; pty = e.clientY-p0.y; applyCanvas(); } });
    const end = () => { if (mode==='node') fitViewBox(); mode=null; node=null; vp.classList.remove('grabbing'); };
    vp.addEventListener('pointerup', end); vp.addEventListener('pointercancel', end);
    vp.addEventListener('wheel', e => { e.preventDefault();
      const r = vp.getBoundingClientRect(), mx = e.clientX-r.left, my = e.clientY-r.top;
      const ns = Math.min(4, Math.max(0.5, scale*(e.deltaY<0?1.1:0.9)));
      ptx = mx-(mx-ptx)*(ns/scale); pty = my-(my-pty)*(ns/scale); scale = ns; applyCanvas(); }, { passive:false });
    const doReset = () => { ptx=0; pty=0; scale=1; svg.style.transition='transform .3s cubic-bezier(.4,0,.2,1)'; applyCanvas();
      setTimeout(() => { svg.style.transition=''; }, 320);
      nodes.forEach(n => { n.tx=0; n.ty=0; n.g.setAttribute('transform', 'translate(0,0)'); }); reroute(); fitViewBox(); };
    reset.addEventListener('click', doReset); vp.addEventListener('dblclick', doReset);
  });
}
initDraggableDiagrams();
```

Notes:
- Author SVGs exactly as before (fixed `viewBox`, flat `<rect>`/`<text>`/`<line>`). Node grouping + line binding are inferred at runtime — keep node labels' `x`/`y` INSIDE their rect bounds so they get adopted correctly.
- Connectors must be `<line>` (with `x1/y1/x2/y2`) to auto-track. `<path>` connectors stay static — use `<line>` for anything that should follow a node.
- **Auto-fit**: on drag release the SVG `viewBox` grows to contain dragged nodes, so the svg height (and the box) sizes WITH the content — nodes never get clipped after release. `svg{overflow:visible}` keeps a node visible mid-drag too. `fitViewBox()` runs on pointerup + reset.
- Idempotent (`dataset.draggable` guard); `resize:vertical` lets the user grow the container; flex viewport fills new height.

### Copy Button on Code Panels (REQUIRED for every `pre.code-block`)

Every code panel MUST have a hover-revealed Copy button. Capture `textContent` BEFORE injecting the button (so the button label isn't copied), wrap the `<pre>` in a relative `.code-wrap`, and copy via the Clipboard API with an `execCommand` fallback.

```css
.code-wrap{position:relative}
.code-copy{position:absolute;top:8px;right:8px;z-index:2;font-size:11px;font-family:inherit;font-weight:500;
  background:rgba(255,255,255,.1);color:#cbd5e1;border:1px solid rgba(255,255,255,.15);
  border-radius:6px;padding:3px 10px;cursor:pointer;opacity:0;transition:opacity .15s,background .15s,color .15s}
.code-wrap:hover .code-copy{opacity:1}
.code-copy:hover{background:rgba(255,255,255,.2);color:#fff}
.code-copy.copied{background:rgba(16,185,129,.25);color:#6ee7b7;border-color:rgba(16,185,129,.45);opacity:1}
```

```js
function initCodeCopy() {
  document.querySelectorAll('pre.code-block').forEach(pre => {
    if (pre.dataset.copy) return; pre.dataset.copy = '1';
    const code = pre.textContent;
    const wrap = document.createElement('div'); wrap.className = 'code-wrap';
    pre.parentNode.insertBefore(wrap, pre); wrap.appendChild(pre);
    const btn = document.createElement('button'); btn.className = 'code-copy'; btn.textContent = 'Copy';
    wrap.appendChild(btn);
    btn.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(code); }
      catch { const ta = document.createElement('textarea'); ta.value = code;
        document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove(); }
      btn.textContent = '✓ Copied'; btn.classList.add('copied');
      setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 1500);
    });
  });
}
initCodeCopy();
```

## ERD Component (draggable whiteboard)

For DB/schema docs, render an ERD as a **whiteboard**: styled entity cards absolutely positioned on a bounded, scrollable canvas — draggable, with SVG connector lines that follow, plus resize + fullscreen. NOT ASCII, NOT a static flex grid.

**Rules:**
- Verify every FK against the real DB (`pg_constraint`) — never invent. HARD FK = solid blue line (`──FK──▶`); LOGIC relation (join/derive) = dashed gray.
- FK-target headers get `data-ent="<table>"`. Relationship columns get `data-rel="<target>" data-rel-kind="fk|logic"`.
- Entities are `position:absolute` inside `.erd-canvas` (large, e.g. 1480×1100) with initial `data-x/data-y` + inline `left/top`. The canvas sits in `.erd-board` (viewport: `overflow:auto; resize:vertical; height:560px`), so the user scrolls to pan and drags the corner to grow. A `⤢` button toggles `.erd-board.full` (fixed inset overlay).
- Drag updates `left/top` (clamped to canvas), `drawERDLines()` on every move + on board scroll + window resize.

```css
.erd-board{position:relative;border:1px solid var(--border);border-radius:14px;background:var(--glass);background-image:radial-gradient(rgba(99,102,150,.13) 1px,transparent 1px);background-size:22px 22px;overflow:auto;height:560px;resize:vertical}
.erd-board.full{position:fixed;inset:18px;height:auto!important;width:auto;z-index:9999;box-shadow:0 24px 90px rgba(0,0,0,.45);resize:none}
.erd-canvas{position:relative;width:1480px;height:1100px}
.erd-board .erd-ent{position:absolute;width:300px;z-index:1}
.erd-board .erd-ent.star{width:344px;box-shadow:0 0 0 2px #f59e0b66,0 4px 16px rgba(245,158,11,.18)}
.erd-clabel{position:absolute;z-index:0;pointer-events:none;font-size:10.5px;font-weight:800;letter-spacing:.6px;text-transform:uppercase;color:var(--text-2);opacity:.7}
.erd-ent{background:var(--glass);border:1px solid var(--border);border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.05)}
.erd-th{padding:7px 11px;font-family:ui-monospace,monospace;font-size:12px;font-weight:700;color:#fff;display:flex;justify-content:space-between;cursor:grab;user-select:none}
.erd-th .erd-tag{font-size:9px;font-weight:700;background:rgba(255,255,255,.25);padding:1px 5px;border-radius:4px}
.erd-col{padding:4px 11px;border-top:1px solid var(--border);font-family:ui-monospace,monospace;font-size:11.5px;display:flex;flex-wrap:wrap;gap:5px;align-items:baseline}
.erd-b{font-size:8.5px;font-weight:800;padding:1px 4px;border-radius:3px}
.erd-pk{background:#fbbf24;color:#713f12}.erd-fk{background:#3b82f6;color:#fff}.erd-uq{background:#a78bfa;color:#fff}
.erd-ref{color:#2563eb;font-size:10.5px}.erd-ref.logic{color:#94a3b8;font-style:italic}
.erd-note{padding:5px 11px;border-top:1px dashed var(--border);font-size:10px;color:var(--text-2);font-style:italic}
svg.erd-lines{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:3;overflow:visible}
svg.erd-lines path{fill:none}
```

Markup (toolbar + board > canvas; each entity carries `data-x/data-y` + `left/top`; headers/cols carry `data-ent`/`data-rel`):
```html
<div class="erd-toolbar"><span>✋ Kéo header · cuộn để pan · kéo mép dưới khung</span>
  <span style="margin-left:auto"><button id="erd-reset">↺ Reset</button> <button id="erd-full">⤢ Toàn màn hình</button></span></div>
<div class="erd-board" id="erd-board"><div class="erd-canvas" id="erd-canvas">
  <div class="erd-clabel" style="left:16px;top:16px">◆ DIMENSION</div>
  <div class="erd-ent" data-x="16" data-y="44" style="left:16px;top:44px">
    <div class="erd-th" data-ent="employees" style="background:#4f46e5">employees</div>
    <div class="erd-col"><span class="erd-b erd-pk">PK</span> id</div></div>
  <div class="erd-ent" data-x="1060" data-y="52" style="left:1060px;top:52px">
    <div class="erd-th" style="background:#059669">payroll_records</div>
    <div class="erd-col" data-rel="employees" data-rel-kind="fk"><span class="erd-b erd-fk">FK</span> employee_id <span class="erd-ref">→ employees.id</span></div></div>
</div></div>
```

JS — connector lines (canvas-relative) + drag (left/top, clamped) + reset + fullscreen:
```javascript
function drawERDLines() {
  const canvas = document.getElementById('erd-canvas'); if (!canvas) return;
  const NS = 'http://www.w3.org/2000/svg';
  let svg = canvas.querySelector('svg.erd-lines');
  if (!svg) { svg = document.createElementNS(NS,'svg'); svg.setAttribute('class','erd-lines');
    const d = document.createElementNS(NS,'defs');
    d.innerHTML = '<marker id="erd-arrow" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#3b82f6"/></marker><marker id="erd-arrow-g" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/></marker>';
    svg.appendChild(d); canvas.prepend(svg); }
  [...svg.querySelectorAll('path,circle')].forEach(n => n.remove());
  const W = canvas.getBoundingClientRect(), ents = {};
  canvas.querySelectorAll('[data-ent]').forEach(e => ents[e.getAttribute('data-ent')] = e.closest('.erd-ent'));
  canvas.querySelectorAll('[data-rel]').forEach(src => {
    const tgt = ents[src.getAttribute('data-rel')]; if (!tgt) return;
    const fk = (src.getAttribute('data-rel-kind')||'fk') === 'fk';
    const s = src.getBoundingClientRect(), t = tgt.getBoundingClientRect();
    const L = (t.left+t.width/2) < (s.left+s.width/2);
    const sx=(L?s.left:s.right)-W.left, sy=s.top+s.height/2-W.top, tx=(L?t.right:t.left)-W.left, ty=t.top+t.height/2-W.top;
    const dx=Math.max(30,Math.abs(tx-sx)*0.45), c1=sx+(L?-dx:dx), c2=tx+(L?dx:-dx), col=fk?'#3b82f6':'#94a3b8';
    const p=document.createElementNS(NS,'path'); p.setAttribute('d',`M ${sx} ${sy} C ${c1} ${sy} ${c2} ${ty} ${tx} ${ty}`);
    p.setAttribute('stroke',col); p.setAttribute('stroke-width','1.6'); p.setAttribute('stroke-opacity','0.6');
    if(!fk) p.setAttribute('stroke-dasharray','5 4'); p.setAttribute('marker-end',fk?'url(#erd-arrow)':'url(#erd-arrow-g)'); svg.appendChild(p);
    const c=document.createElementNS(NS,'circle'); c.setAttribute('cx',sx); c.setAttribute('cy',sy); c.setAttribute('r','2.5'); c.setAttribute('fill',col); svg.appendChild(c);
  });
}
function initERDBoard() {
  const canvas = document.getElementById('erd-canvas'); if (!canvas) return;
  canvas.querySelectorAll('.erd-ent').forEach(ent => {
    const h = ent.querySelector('.erd-th'); if (!h || h.dataset.drag) return; h.dataset.drag='1';
    let sx,sy,ox,oy,drag=false;
    h.addEventListener('pointerdown', e => { drag=true; ox=parseFloat(ent.style.left)||0; oy=parseFloat(ent.style.top)||0; sx=e.clientX; sy=e.clientY; ent.style.zIndex='30'; h.setPointerCapture(e.pointerId); e.preventDefault(); });
    h.addEventListener('pointermove', e => { if(!drag) return;
      ent.style.left = Math.max(0,Math.min(canvas.clientWidth-ent.offsetWidth, ox+e.clientX-sx))+'px';
      ent.style.top  = Math.max(0,Math.min(canvas.clientHeight-ent.offsetHeight, oy+e.clientY-sy))+'px'; drawERDLines(); });
    const end = () => { if(!drag) return; drag=false; ent.style.zIndex='1'; drawERDLines(); };
    h.addEventListener('pointerup', end); h.addEventListener('pointercancel', end);
  });
  document.getElementById('erd-reset')?.addEventListener('click', () => { canvas.querySelectorAll('.erd-ent').forEach(e => { e.style.left=e.dataset.x+'px'; e.style.top=e.dataset.y+'px'; }); drawERDLines(); });
  document.getElementById('erd-full')?.addEventListener('click', e => { const on=document.getElementById('erd-board').classList.toggle('full'); e.target.textContent=on?'✕ Thoát toàn màn hình':'⤢ Toàn màn hình'; setTimeout(drawERDLines,60); });
}
window.addEventListener('load', () => { initERDBoard(); drawERDLines(); });
let __erdT; window.addEventListener('resize', () => { clearTimeout(__erdT); __erdT=setTimeout(drawERDLines,150); });
document.getElementById('erd-board')?.addEventListener('scroll', () => { clearTimeout(__erdT); __erdT=setTimeout(drawERDLines,40); });
setTimeout(() => { initERDBoard(); drawERDLines(); }, 320);
```

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

**Filename MUST be prefixed with today's date `DDMMYY-`** (same `DDMMYY` as the output-report draft, so HTML and wiki draft stay paired). E.g. on 4 Jun 2026 → `040626-cell-formula-override.html`.

- Single file: `llmwiki/html/DDMMYY-<slug>.html`
- Multi-file: `llmwiki/html/DDMMYY-index.html` + `llmwiki/html/DDMMYY-<slug>.html`
- `<slug>` = 2–4 kebab-case words; `DDMMYY` = today (e.g. `040626`).
- NEVER write to the project root or any other directory.
- If `llmwiki/html/` does not exist, create it first.

## Auto-Host

After creating the HTML file(s), ALWAYS start a local HTTP server for preview:

```bash
cd <project-root>
kill -9 $(lsof -ti :8765) 2>/dev/null
nohup npx serve -p 8765 > /tmp/serve.log 2>&1 &
```

Notify user: open `http://localhost:8765/llmwiki/html/DDMMYY-<file>.html`

If port 8765 is already in use, skip (server already running).

## Multi-File Mode

When generating separate pages per wiki file (all files share the same `DDMMYY-` date prefix):
- Create an `DDMMYY-index.html` overview page (card grid linking to all N pages)
- Create `DDMMYY-{slug}.html` for each wiki file (slug derived from filename)
- Each page shares the same CSS design system but uses its section accent color
- Each page has a nav bar linking to all other pages (highlight current page)
- Each page has its own animated SVG diagram based on the topic content

## Interactive Prototype / Editable Data-Grid (optional)

When the user asks to "see how the UI will look", "tạo bảng tương tác thử", or wants a clickable demo of an editable grid/spreadsheet feature, build a **standalone interactive prototype** (same `DDMMYY-<slug>.html`, Tailwind CDN + vanilla JS, no build). These reusable patterns make override/cascade UIs consistent and self-explanatory:

- **Locale-aware number input** — `parseUserNumber(raw, locale)`: strip the locale's thousand sep, swap decimal to `.`, `Number()`. Display via `Intl.NumberFormat(locale)`. Offer a VN ↔ US/Đài toggle.
- **Override vs Affected, persistent coloring** — compute each row TWICE: with overrides (`v`) and without (`base`). A cell is: **override** (in the override map) → amber `bg-amber-50 ring-amber-300` + `✦`; **affected/cascade** (`base[code] !== v[code]`) → emerald `bg-emerald-50 ring-emerald-200` + `↻`. Both persist (not just a flash) until the override is removed. Add a transient `flash` (~1.4s) on the cells that changed this commit.
- **Attribution (which override caused which cell)** — perturbation: for each override in the row, recompute with that one removed; cells whose value differs are caused by it. Build `causes: affected→[ov]` and `affects: ov→[affected]`. Surface via: (a) hover a cell → add a highlight class to linked cells IN THE SAME ROW (`data-affects` / `data-srcs`), (b) `title` tooltip listing names, (c) a toast after save listing recomputed cells.
- **Frictionless editing** — double-click ANY editable column → inline input immediately. Do NOT gate edits behind a blocking `confirm()`. Surface "sensitive" columns passively (kind-tag in header, tooltip, a flag), never a modal that blocks every edit.
- **Proper modal, not `confirm()`** — reserve a styled modal ONLY for destructive actions (e.g. "clear all overrides"); parametrize title/okText/danger.
- **Focus after async UI** — when an edit starts right after closing a modal/dialog, focus the input on a tick (`setTimeout(...,0)`), or it won't take focus.

Keep the chrome (traffic-light header), Inter font, and slate/amber palette consistent with the doc sites.

## Best Practices

- ALWAYS inline SVG directly in the HTML (not external files)
- ALWAYS use `clamp()` for hero heading size: `font-size: clamp(32px,5vw,56px)`
- NEVER use `☐` Unicode for checklists — ALWAYS use real `<input type="checkbox">` with `<label for="...">` so items are clickable. Add this CSS for every checklist:

```css
.checklist { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.checklist li { display: flex; align-items: flex-start; gap: 10px; font-size: 13px; color: var(--text-2); cursor: pointer; }
.checklist li::before { display: none; }
.checklist input[type="checkbox"] {
  width: 16px; height: 16px; border-radius: 4px; border: 1.5px solid #cbd5e1;
  appearance: none; -webkit-appearance: none; cursor: pointer; flex-shrink: 0;
  background: rgba(255,255,255,.8); margin-top: 2px; transition: all .15s;
}
.checklist input[type="checkbox"]:checked {
  background: #6366f1; border-color: #6366f1;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M13 4L6.5 11 3 7.5' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' fill='none'/%3E%3C/svg%3E");
  background-size: contain;
}
.checklist label { cursor: pointer; line-height: 1.5; }
.checklist input[type="checkbox"]:checked + label { text-decoration: line-through; color: #94a3b8; }
```

```html
<!-- Correct checklist markup -->
<ul class="checklist">
  <li><input type="checkbox" id="c1"><label for="c1">Item text</label></li>
  <li><input type="checkbox" id="c2"><label for="c2">Item text</label></li>
</ul>
```
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