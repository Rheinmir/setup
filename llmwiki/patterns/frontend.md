# Frontend — Patterns & Anti-patterns

> Protected reference (overstack pattern library). Seeded best-guess — pending curation.

## Patterns

### Atomic Design Component Hierarchy
- **When:** Building a shared UI library that many app surfaces reuse and must keep visually consistent.
- **Do:** Compose UI bottom-up — atoms into molecules into organisms into templates into pages — each layer building only on the one below.
- **Why:** Reuse and consistency by construction; isolated, testable components; a shared vocabulary across the whole team and design system.

### Fine-Grained Reactivity with Signals
- **When:** Frequently-changing shared state (counters, live agent status, form fields) where re-rendering whole subtrees is wasteful.
- **Do:** Model state as signals; components subscribe to the exact values they read, so only those DOM nodes update.
- **Why:** Surgical updates without virtual-DOM diffing, and predictable performance that scales with what changed, not with tree size.

### Server Components with Hybrid Rendering
- **When:** Content- or data-heavy pages needing fast first paint plus selective interactivity (dashboards, streamed agent output).
- **Do:** Render data-fetching and static UI on the server (RSC), ship zero JS for it, hydrate only interactive islands — at the edge when latency matters.
- **Why:** Far less client JavaScript, faster time-to-interactive, secrets stay server-side, and SEO works by default.

### Container Queries over Media Queries
- **When:** Reusable components that appear in varying slots — sidebar, modal, full-width — within one viewport.
- **Do:** Style components by their own container's size with `@container`, not the global viewport with media queries.
- **Why:** Truly portable components that adapt to the space they are given, decoupled from page layout and screen width.

### Scoped Context Providers
- **When:** Cross-cutting state — theme, locale, auth, agent session — read by many components but rarely changing.
- **Do:** Provide it via Context at the narrowest boundary that needs it; keep hot, frequently-updated state in signals or stores instead.
- **Why:** Eliminates prop drilling without re-rendering the world, and scopes each concern to where it actually applies.

## Anti-patterns

### Prop Drilling
- **Smell:** A prop threaded through several components that never use it, just to reach a deep child.
- **Why bad:** Couples unrelated layers, makes refactors painful, and the noise hides which props each component truly needs.
- **Instead:** Lift the value into a Scoped Context Provider, or colocate the state nearer where it is consumed.

### God Component
- **Smell:** One file of hundreds of lines, dozens of props, many responsibilities, and merge conflicts on every change.
- **Why bad:** Untestable and unreusable; every team touches it, so it becomes both a bottleneck and a bug magnet.
- **Instead:** Decompose along the Atomic Design hierarchy into focused atoms, molecules, and organisms with single responsibilities.

### Viewport-Coupled Components
- **Smell:** A reusable component whose breakpoints reference screen width, so it breaks when placed in a narrow slot.
- **Why bad:** It looks right full-width but overflows or collapses inside sidebars, modals, and grid cells.
- **Instead:** Drive responsiveness with Container Queries so the component adapts to its actual container, not the viewport.

### Framework Soup
- **Smell:** One page loads multiple frameworks or several React versions because each micro-frontend bundles its own runtime.
- **Why bad:** Duplicated runtimes bloat the bundle, slow interactivity, and cause subtle version-mismatch bugs at the seams.
- **Instead:** Enforce a single shared runtime version, share vendor bundles, and lean on Server Components to cut client JS.

### Distributed Monolith (UI)
- **Smell:** Micro-frontends that must be built and deployed together; a change in one breaks or blocks the others.
- **Why bad:** You pay the coordination and complexity tax of micro-frontends while losing the independent-deploy benefit that justifies them.
- **Instead:** Define explicit versioned contracts and independent pipelines; do not split a UI until teams genuinely need autonomy.

## Origin
- Seeded from /last30days research (frontend design patterns 2026, Atomic Design, MFE anti-patterns) — 2026-06-29.
