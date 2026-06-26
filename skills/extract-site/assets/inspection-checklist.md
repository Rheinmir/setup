# Website Inspection Checklist

Distilled from the ai-website-cloner-template INSPECTION_GUIDE. Use during
Phase 1 (Reconnaissance). What to capture when reverse-engineering any site
via browser MCP / computer-use / DevTools.

## Phase 1 — Visual Audit

### Screenshots to capture
- [ ] Every distinct page — desktop (1440), tablet (768), mobile (390)
- [ ] Dark / light mode variants (if applicable)
- [ ] Key interaction states (hover, active, open menus, modals)
- [ ] Loading / skeleton, empty, and error states

### Design tokens to extract
- [ ] **Colors** — bg, text (primary/secondary/muted), accent, border, hover, error/success/warning
- [ ] **Typography** — family, sizes (h1–h6, body, caption, label), weights, line-heights, letter-spacing
- [ ] **Spacing** — look for a scale: 4 / 8 / 12 / 16 / 24 / 32px
- [ ] **Border radius** — buttons, cards, avatars, inputs
- [ ] **Shadows / elevation** — card, dropdown, modal overlay
- [ ] **Breakpoints** — where does layout shift?
- [ ] **Icons** — library? custom SVG? sizes?
- [ ] **Buttons** — every variant (primary, secondary, ghost, icon-only, danger)
- [ ] **Inputs** — text, textarea, select, checkbox, toggle

## Phase 2 — Component Inventory
For each distinct UI component document: name · structure · variants · states
(default/hover/active/disabled/loading/error/empty) · responsive behavior ·
interactions (click/hover/focus/keyboard) · animations.

Common components: nav (top/side/bottom), cards, buttons, forms, modals,
dropdowns, tabs, avatars, skeletons, toasts, tooltips.

## Phase 3 — Layout Architecture
- [ ] Grid system (CSS Grid / Flexbox / fixed)
- [ ] Column count per breakpoint · main max-width
- [ ] Sticky elements (header, sidebar, floating buttons)
- [ ] Z-index layers (nav, modals, tooltips, overlays)
- [ ] Scroll behavior (infinite scroll, pagination, virtual scroll)

## Phase 4 — Technical Stack Detection
- [ ] **Framework** — React/Vue/Angular? check `__NEXT_DATA__`, `__NUXT__`, `ng-version`
- [ ] **CSS approach** — Tailwind (utility classes), CSS Modules, styled-components, Emotion, vanilla
- [ ] **State** — Redux / React Query / Zustand / Pinia (check DevTools)
- [ ] **API** — REST vs GraphQL (network tab for `/graphql`)
- [ ] **Fonts** — Google / self-hosted / system
- [ ] **Images** — CDN, lazy, srcset, WebP/AVIF
- [ ] **Animation lib** — Framer Motion / GSAP / CSS-only / Lenis (smooth scroll → check `.lenis`)
