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
- Verify every FK against the real DB (`pg_constraint`) — never invent.
- **Phân biệt NGUỒN GỐC bảng** bằng badge ở góc phải header (`.erd-org` + `margin-left:auto`): 🆕 MỚI từ feature (`erd-org-new`), cột mới trong bảng cũ (`erd-org-col`), ♻ tái dùng/mở rộng (`erd-org-reuse`), legacy có sẵn (`erd-org-legacy`). Kèm 1 legend màu. HARD FK = solid blue line (`──FK──▶`); LOGIC relation (join/derive) = dashed gray.
- FK-target headers get `data-ent="<table>"`. Relationship columns get `data-rel="<target>" data-rel-kind="fk|logic"`.
- Entities are `position:absolute` inside `.erd-canvas` (large, e.g. 1480×1100) with initial `data-x/data-y` + inline `left/top`. The canvas sits in `.erd-board` (viewport: `overflow:auto; resize:vertical; height:560px`), so the user scrolls to pan and drags the corner to grow. A `⤢` button toggles `.erd-board.full` (fixed inset overlay).
- Drag updates `left/top` (clamped to canvas), `drawERDLines()` on every move + on board scroll + window resize.

```css
.erd-board{position:relative;border:1px solid var(--border);border-radius:14px;background:var(--glass);background-image:radial-gradient(rgba(99,102,150,.13) 1px,transparent 1px);background-size:22px 22px;overflow:auto;height:560px;resize:vertical}
.erd-board.full{position:fixed;inset:18px;height:auto!important;width:auto;z-index:9999;box-shadow:0 24px 90px rgba(0,0,0,.45);resize:none;background-color:rgba(248,247,252,.9);backdrop-filter:blur(32px) saturate(1.4);-webkit-backdrop-filter:blur(32px) saturate(1.4)}  /* fullscreen = frosted MẠNH, nền đặc (đừng để trong suốt) */
body.erd-full-on::before{content:'';position:fixed;inset:0;z-index:9998;background:rgba(20,18,30,.38);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px)}  /* dim + blur trang phía sau */
.erd-canvas{position:relative;width:1480px;height:1100px}
.erd-board .erd-ent{position:absolute;width:300px;z-index:1}
.erd-board .erd-ent.star{width:344px;box-shadow:0 0 0 2px #f59e0b66,0 4px 16px rgba(245,158,11,.18)}
.erd-clabel{position:absolute;z-index:0;pointer-events:none;font-size:10.5px;font-weight:800;letter-spacing:.6px;text-transform:uppercase;color:var(--text-2);opacity:.7}
.erd-ent{background:var(--glass);border:1px solid var(--border);border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.05)}
.erd-th{padding:7px 11px;font-family:ui-monospace,monospace;font-size:12px;font-weight:700;color:#fff;display:flex;align-items:center;gap:6px;cursor:grab;user-select:none}
.erd-th .erd-tag{font-size:9px;font-weight:700;background:rgba(255,255,255,.25);padding:1px 5px;border-radius:4px}
.erd-th .erd-org{margin-left:auto;font-size:8px;font-weight:800;padding:1px 6px;border-radius:4px;white-space:nowrap}
.erd-org-new{background:#16a34a;color:#fff}.erd-org-col{background:#0ea5e9;color:#fff}.erd-org-reuse{background:#fff;color:#b45309}.erd-org-legacy{background:rgba(255,255,255,.28);color:#fff}
.erd-col{padding:4px 11px;border-top:1px solid var(--border);font-family:ui-monospace,monospace;font-size:11.5px;display:flex;flex-wrap:wrap;gap:5px;align-items:baseline}
.erd-b{font-size:8.5px;font-weight:800;padding:1px 4px;border-radius:3px}
.erd-pk{background:#fbbf24;color:#713f12}.erd-fk{background:#3b82f6;color:#fff}.erd-uq{background:#a78bfa;color:#fff}
.erd-ref{color:#2563eb;font-size:10.5px}.erd-ref.logic{color:#94a3b8;font-style:italic}
.erd-note{padding:5px 11px;border-top:1px dashed var(--border);font-size:10px;color:var(--text-2);font-style:italic}
svg.erd-lines{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:3;overflow:visible}
svg.erd-lines path{fill:none}
/* comment / note nodes — panel to, Find/Replace = textarea code */
.erd-cmt{position:absolute;width:340px;background:#fff8c5;border:1px solid #ecd34a;border-radius:11px;box-shadow:0 4px 18px rgba(0,0,0,.15);z-index:5;font-size:12px}
.erd-cmt.big{width:600px}
.erd-cmt-h{background:#f6e05e;padding:5px 10px;border-radius:10px 10px 0 0;cursor:grab;display:flex;justify-content:space-between;align-items:center;font-size:11px;font-weight:800;color:#713f12;user-select:none}
.erd-cmt-h .erd-cmt-tools span{cursor:pointer;opacity:.6;font-weight:700;padding:0 3px}
.erd-cmt-h .erd-cmt-tools span:hover{opacity:1}
.erd-cmt-body{padding:7px 10px;outline:none;min-height:30px;color:#5b4708;line-height:1.45;font-weight:600}
.erd-cmt-body:empty::before{content:'tiêu đề / ghi chú…';opacity:.4;font-weight:400}
.erd-cmt-fr{padding:2px 10px 8px;display:flex;flex-direction:column;gap:7px}
.erd-cmt-grp label{display:flex;justify-content:space-between;align-items:center;font-size:10px;font-weight:700;color:#8a6d1a;margin-bottom:2px}
.erd-cmt-grp label button{font:inherit;font-size:10px;font-weight:700;border:1px solid #d9b94a;background:#fff;border-radius:5px;cursor:pointer;padding:2px 8px}
.erd-cmt-grp label button:hover{background:#fffbe6}
.erd-cmt-grp textarea{width:100%;box-sizing:border-box;font-family:ui-monospace,'SF Mono',monospace;font-size:11px;line-height:1.45;border:1px solid #e3cf6a;border-radius:6px;padding:5px 7px;background:#fffdf0;resize:vertical;min-height:46px;white-space:pre;overflow:auto}
.erd-cmt.big .erd-cmt-grp textarea{min-height:150px}
.erd-cmt-link{padding:0 10px 8px;display:flex;gap:6px;align-items:center;font-size:10px;color:#8a6d1a}
.erd-canvas.linking{cursor:crosshair}
.erd-canvas.linking .erd-ent,.erd-canvas.linking .erd-cmt{outline:2px dashed rgba(245,158,11,.5)}
svg.erd-lines path.rel-hit{pointer-events:stroke;cursor:pointer}
/* global sync panel (ghi layout vào file qua Ctrl+H) */
.erd-syncbox{border:1px solid var(--border);background:var(--glass);border-radius:12px;padding:10px 12px;margin:0 0 8px;font-size:11.5px}
.erd-syncrow{display:flex;align-items:center;gap:8px;margin:6px 0 3px}
.erd-syncrow label{font-weight:700;color:var(--text-2)}
.erd-syncrow .erd-copy{margin-left:auto;font:inherit;font-size:11px;font-weight:700;border:1px solid var(--border);background:#fff;border-radius:6px;cursor:pointer;padding:2px 9px}
.erd-syncrow .erd-copy:hover{background:#f0f0f6}
.erd-syncbox textarea{width:100%;box-sizing:border-box;font-family:ui-monospace,'SF Mono',monospace;font-size:10.5px;line-height:1.4;border:1px solid var(--border);border-radius:6px;padding:6px 8px;background:#fbfbfe;resize:vertical;min-height:54px;white-space:pre;overflow:auto}
```

**Interactions (persist + notes + arrows + sync-to-file):** board state (entity positions, notes, arrows) auto-saves to `localStorage` (live working copy), restored on load from `localStorage` → else from a `<script id="erd-layout-data" type="application/json">{}</script>` marker baked in the file. Double-click empty canvas → a sticky **note** (editable body only — NO per-note code fields). Click a note's **↗** → linking mode → click an entity or a relationship line (`path.rel-hit`) → orange arrow that follows on drag.

**Sync layout back to file (key pattern):** Find/Replace is NOT typed per-note — it's a single **global** toolbar panel (`💾 Đồng bộ → file`) that AUTO-GENERATES for editor Ctrl+H: **Copy Find** = the marker exactly as it sits in the file now (`<script id="erd-layout-data" ...>{...}</script>`), **Copy Replace** = same marker regenerated with current dragged positions + notes. Paste into editor find-replace → Replace-All → layout is written into the source HTML (persists + shareable, not just browser). `Reset` clears localStorage + notes. Markup needs toolbar button `#erd-sync`, panel `#erd-syncbox` (readonly textareas `#erd-find`/`#erd-replace` + copy buttons), and the `<script id="erd-layout-data">{}</script>` marker. The JS below is the full reference (one IIFE):

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
/* ─── ERD whiteboard: lines + drag + comments(find/replace) + arrows + persist + fullscreen ─── */
(function(){
  const NS='http://www.w3.org/2000/svg';
  const LS='erd-board-030626';
  const canvas=document.getElementById('erd-canvas');
  const board=document.getElementById('erd-board');
  if(!canvas) return;

  // baseline = state ĐANG GHI trong file (script#erd-layout-data); localStorage = bản làm việc trực tiếp
  const dataEl=document.getElementById('erd-layout-data');
  const fileRaw=(dataEl&&dataEl.textContent.trim())||'{}';
  let fileState={}; try{ fileState=JSON.parse(fileRaw)||{}; }catch(e){ fileState={}; }
  let BOARD; try{ BOARD=JSON.parse(localStorage.getItem(LS))||null; }catch(e){ BOARD=null; }
  if(!BOARD) BOARD=JSON.parse(JSON.stringify(fileState));   // chưa có bản làm việc → dùng file
  BOARD.ents=BOARD.ents||{}; BOARD.comments=BOARD.comments||[]; BOARD.seq=BOARD.seq||1;
  const save=()=>{ try{ localStorage.setItem(LS,JSON.stringify(BOARD)); }catch(e){} };
  // Find = đoạn script hiện có trong file (1 dòng); Replace = đoạn mới theo BOARD
  const wrapData=j=>'<script id="erd-layout-data" type="application/json">'+j+'<\/script>';
  const findText=()=>wrapData(fileRaw);
  const replaceText=()=>wrapData(JSON.stringify({ents:BOARD.ents,comments:BOARD.comments,seq:BOARD.seq}));
  function nameOf(ent){ const h=ent.querySelector('.erd-th'); return ((h.childNodes[0]&&h.childNodes[0].textContent)||'').trim(); }
  function copyText(t,btn){ const done=()=>{ const o=btn.textContent; btn.textContent='✓'; setTimeout(()=>btn.textContent=o,900); };
    if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(t||'').then(done).catch(fb); } else fb();
    function fb(){ const ta=document.createElement('textarea'); ta.value=t||''; document.body.appendChild(ta); ta.select(); try{document.execCommand('copy');}catch(e){} ta.remove(); done(); } }

  let linking=null;

  function ensureSVG(){
    let svg=canvas.querySelector('svg.erd-lines');
    if(!svg){ svg=document.createElementNS(NS,'svg'); svg.setAttribute('class','erd-lines');
      const d=document.createElementNS(NS,'defs');
      d.innerHTML='<marker id="erd-arrow" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#3b82f6"/></marker>'
        +'<marker id="erd-arrow-g" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/></marker>'
        +'<marker id="erd-arrow-c" markerWidth="8" markerHeight="8" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#ea580c"/></marker>';
      svg.appendChild(d); canvas.prepend(svg); }
    return svg;
  }
  function bez(sx,sy,tx,ty){ const L=tx<sx; const dx=Math.max(30,Math.abs(tx-sx)*0.45); const c1=sx+(L?-dx:dx),c2=tx+(L?dx:-dx); return 'M '+sx+' '+sy+' C '+c1+' '+sy+' '+c2+' '+ty+' '+tx+' '+ty; }

  function draw(){
    const svg=ensureSVG();
    [...svg.querySelectorAll('path,circle')].forEach(n=>n.remove());
    const W=canvas.getBoundingClientRect();
    const ents={}; canvas.querySelectorAll('[data-ent]').forEach(e=>ents[e.getAttribute('data-ent')]=e.closest('.erd-ent'));
    canvas.querySelectorAll('[data-rel]').forEach(src=>{
      const tgt=ents[src.getAttribute('data-rel')]; if(!tgt) return;
      const fk=(src.getAttribute('data-rel-kind')||'fk')==='fk';
      const s=src.getBoundingClientRect(),t=tgt.getBoundingClientRect();
      const L=(t.left+t.width/2)<(s.left+s.width/2);
      const sx=(L?s.left:s.right)-W.left, sy=s.top+s.height/2-W.top, tx=(L?t.right:t.left)-W.left, ty=t.top+t.height/2-W.top;
      const col=fk?'#3b82f6':'#94a3b8';
      const p=document.createElementNS(NS,'path'); p.setAttribute('d',bez(sx,sy,tx,ty)); p.setAttribute('stroke',col); p.setAttribute('stroke-width','1.6'); p.setAttribute('stroke-opacity','0.6');
      if(!fk) p.setAttribute('stroke-dasharray','5 4');
      p.setAttribute('marker-end',fk?'url(#erd-arrow)':'url(#erd-arrow-g)');
      const se=src.closest('.erd-ent'); p.dataset.relkey=(se?nameOf(se):'')+'|'+src.getAttribute('data-rel');
      if(linking){ p.classList.add('rel-hit'); p.addEventListener('click',ev=>{ ev.stopPropagation(); setLink(linking,{type:'rel',key:p.dataset.relkey}); }); }
      svg.appendChild(p);
      const c=document.createElementNS(NS,'circle'); c.setAttribute('cx',sx); c.setAttribute('cy',sy); c.setAttribute('r','2.5'); c.setAttribute('fill',col); svg.appendChild(c);
    });
    BOARD.comments.forEach(cm=>{
      if(!cm.link) return; const el=document.getElementById('cmt-'+cm.id); if(!el) return;
      const r=el.getBoundingClientRect(); const sx=r.left+r.width/2-W.left, sy=r.top+r.height/2-W.top; let tx,ty;
      if(cm.link.type==='ent'){ const te=ents[cm.link.name]||[...canvas.querySelectorAll('.erd-ent')].find(e=>nameOf(e)===cm.link.name); if(!te) return; const t=te.getBoundingClientRect(); const L=(t.left+t.width/2)<r.left+r.width/2; tx=(L?t.right:t.left)-W.left; ty=t.top+t.height/2-W.top; }
      else { const pp=svg.querySelector('path[data-relkey="'+cm.link.key+'"]'); if(!pp) return; const m=pp.getPointAtLength(pp.getTotalLength()/2); tx=m.x; ty=m.y; }
      const p=document.createElementNS(NS,'path'); p.setAttribute('d',bez(sx,sy,tx,ty)); p.setAttribute('stroke','#ea580c'); p.setAttribute('stroke-width','1.8'); p.setAttribute('stroke-dasharray','2 3'); p.setAttribute('marker-end','url(#erd-arrow-c)'); svg.appendChild(p);
    });
  }

  function makeDraggable(el,handle,onEnd){
    handle.style.cursor='grab'; handle.style.userSelect='none';
    let sx,sy,ox,oy,dr=false;
    handle.addEventListener('pointerdown',e=>{ if(e.target.closest('button,input,.erd-cmt-x,.erd-cmt-link-btn')) return; dr=true; ox=parseFloat(el.style.left)||0; oy=parseFloat(el.style.top)||0; sx=e.clientX; sy=e.clientY; el.style.zIndex='40'; handle.style.cursor='grabbing'; handle.setPointerCapture(e.pointerId); e.preventDefault(); });
    handle.addEventListener('pointermove',e=>{ if(!dr) return; const nx=Math.max(0,Math.min(canvas.clientWidth-el.offsetWidth,ox+e.clientX-sx)); const ny=Math.max(0,Math.min(canvas.clientHeight-el.offsetHeight,oy+e.clientY-sy)); el.style.left=nx+'px'; el.style.top=ny+'px'; draw(); });
    const end=()=>{ if(!dr) return; dr=false; el.style.zIndex=el.classList.contains('erd-cmt')?'5':'1'; handle.style.cursor='grab'; onEnd(parseFloat(el.style.left)||0,parseFloat(el.style.top)||0); draw(); };
    handle.addEventListener('pointerup',end); handle.addEventListener('pointercancel',end);
  }

  function startLinking(id){ linking=id; canvas.classList.add('linking'); ensureSVG().classList.add('linking'); draw(); }
  function stopLinking(){ if(!linking) return; linking=null; canvas.classList.remove('linking'); const s=canvas.querySelector('svg.erd-lines'); if(s) s.classList.remove('linking'); draw(); }
  function setLink(id,link){ const cm=BOARD.comments.find(c=>c.id===id); if(cm){ cm.link=link; save(); const el=document.getElementById('cmt-'+id); const lt=el&&el.querySelector('.erd-cmt-lt'); if(lt) lt.textContent='→ '+(link.type==='ent'?link.name:link.key); } stopLinking(); }

  function addCommentNode(cm){
    if(document.getElementById('cmt-'+cm.id)) return;
    const el=document.createElement('div'); el.className='erd-cmt'; el.id='cmt-'+cm.id; el.style.left=cm.x+'px'; el.style.top=cm.y+'px';
    el.innerHTML='<div class="erd-cmt-h"><span>💬 note</span><span class="erd-cmt-tools">'
      +'<span class="erd-cmt-link-btn" title="nối mũi tên tới bảng / đường quan hệ">↗</span>'
      +'<span class="erd-cmt-x" title="xóa">✕</span></span></div>'
      +'<div class="erd-cmt-body" contenteditable="true"></div>'
      +'<div class="erd-cmt-link"><span class="erd-cmt-lt"></span></div>';
    canvas.appendChild(el);
    const body=el.querySelector('.erd-cmt-body'); body.textContent=cm.text||'';
    const lt=el.querySelector('.erd-cmt-lt'); if(cm.link) lt.textContent='→ '+(cm.link.type==='ent'?cm.link.name:cm.link.key);
    body.addEventListener('input',()=>{ cm.text=body.textContent; save(); });
    el.querySelector('.erd-cmt-x').addEventListener('click',()=>{ BOARD.comments=BOARD.comments.filter(c=>c.id!==cm.id); save(); el.remove(); draw(); });
    el.querySelector('.erd-cmt-link-btn').addEventListener('click',()=>startLinking(cm.id));
    makeDraggable(el,el.querySelector('.erd-cmt-h'),(x,y)=>{ cm.x=Math.round(x); cm.y=Math.round(y); save(); });
  }

  function initEnts(){
    canvas.querySelectorAll('.erd-ent').forEach(ent=>{
      const nm=nameOf(ent); ent.dataset.name=nm;
      if(BOARD.ents[nm]){ ent.style.left=BOARD.ents[nm].x+'px'; ent.style.top=BOARD.ents[nm].y+'px'; }
      const h=ent.querySelector('.erd-th'); if(h.dataset.drag) return; h.dataset.drag='1';
      ent.addEventListener('click',e=>{ if(linking){ e.stopPropagation(); setLink(linking,{type:'ent',name:nm}); } });
      makeDraggable(ent,h,(x,y)=>{ BOARD.ents[nm]={x:Math.round(x),y:Math.round(y)}; save(); });
    });
  }

  canvas.addEventListener('dblclick',e=>{ if(e.target.closest('.erd-ent')||e.target.closest('.erd-cmt')) return;
    const W=canvas.getBoundingClientRect(); const cm={id:BOARD.seq++,x:Math.round(e.clientX-W.left),y:Math.round(e.clientY-W.top),text:'',find:'',replace:'',link:null};
    BOARD.comments.push(cm); save(); addCommentNode(cm); const b=document.getElementById('cmt-'+cm.id).querySelector('.erd-cmt-body'); b&&b.focus(); draw(); });
  canvas.addEventListener('click',e=>{ if(linking && !e.target.closest('.erd-ent') && !e.target.closest('path.rel-hit') && !e.target.closest('.erd-cmt')) stopLinking(); });

  document.getElementById('erd-reset')?.addEventListener('click',()=>{ if(!confirm('Reset vị trí + xóa hết note/mũi tên?')) return;
    BOARD={ents:{},comments:[],seq:1}; save(); canvas.querySelectorAll('.erd-cmt').forEach(n=>n.remove());
    canvas.querySelectorAll('.erd-ent').forEach(e=>{ e.style.left=e.dataset.x+'px'; e.style.top=e.dataset.y+'px'; }); draw(); });
  document.getElementById('erd-full')?.addEventListener('click',e=>{ const on=board.classList.toggle('full'); document.body.classList.toggle('erd-full-on',on); e.target.textContent=on?'✕ Thoát toàn màn hình':'⤢ Toàn màn hình'; setTimeout(draw,60); });

  // global sync → file (tự sinh Find/Replace cho Ctrl+H)
  const syncBox=document.getElementById('erd-syncbox');
  function fillSync(){ const f=document.getElementById('erd-find'),r=document.getElementById('erd-replace'); if(f) f.value=findText(); if(r) r.value=replaceText(); }
  document.getElementById('erd-sync')?.addEventListener('click',()=>{ const on=syncBox.hidden; syncBox.hidden=!on; if(on) fillSync(); });
  syncBox?.querySelectorAll('.erd-copy').forEach(b=>b.addEventListener('click',e=>{ fillSync(); copyText(e.target.dataset.t==='find'?findText():replaceText(),e.target); }));

  function boot(){ initEnts(); BOARD.comments.forEach(addCommentNode); draw(); }
  window.addEventListener('load',boot);
  let T; window.addEventListener('resize',()=>{ clearTimeout(T); T=setTimeout(draw,150); });
  board.addEventListener('scroll',()=>{ clearTimeout(T); T=setTimeout(draw,40); });
  setTimeout(boot,320);
  window.drawERDLines=draw;
})();
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