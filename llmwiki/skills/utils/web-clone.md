---
name: web-clone
description: Clone a website's exact look — save a faithful, self-contained offline copy of a page (HTML + CSS + JS + images in one file), preserving UI and (best-effort) interactions. Use when the user wants to "clone this site", copy a page's design/UI, mirror a layout, or save a page for offline. Built-now-adapt-later: a builtin inliner makes a local page self-contained now; faithful live-URL capture + JS-interaction fidelity are a one-config engine adapter (SingleFile CLI / monolith).
---

# Skill: web-clone

Save a page as ONE self-contained HTML that renders offline — UI intact, scripts kept. The
capture engine is a quarantined adapter (`harness/web-clone.config.yaml`, `verified:false`).

## When to use
- User wants a page's **look/UI**, not just its text ("clone this site", "copy this design", "lấy y giao diện").
- Archiving a page for offline / as a reference snapshot.
- Seeding a UI starting point from an existing design (respecting copyright).

## Steps
1. **Live URL, faithful capture:** prefer an external engine (set `engine` in config):
   - **SingleFile CLI** (`npm i -g single-file-cli`) — keeps scripts, highest fidelity.
   - **monolith** (`cargo install monolith`) — fast Rust single-file.
   Then: `python3 harness/scripts/web-clone.py url "<URL>" --out clone.html`
   (shells out to the configured engine; tells you to install one if absent).
3. **Already downloaded / local page:** make it self-contained offline (no network, no key):
   `python3 harness/scripts/web-clone.py inline <page.html> --out clone.html`
   (inlines local `<link>` CSS, `<script src>` JS, and images as data URIs → one file).
4. **Verify:** open the output offline; check the UI matches. Note that **dynamic JS interactions
   are best-effort** across all engines (the quarantined unknown — see `preserve_interactions`).

## Rules
- Builtin `inline` handles LOCAL resources only; faithful **live-URL** capture needs an engine
  (the BNAL adapter) — never claim faithful capture without a wired engine.
- `preserve_interactions: best-effort` — say so; do not promise pixel + behavior perfection.
- Respect copyright / Terms; clone for reference/offline, not to republish someone's site.
- Self-test: `python3 harness/scripts/web-clone.py --self-test`.

## Related
- `harness/scripts/web-clone.py` + `harness/web-clone.config.yaml` (the engine adapter).
- `/web-crawl` — when you want the page's text/markdown, not its UI.
- `docs-site-macos` — to BUILD a macOS-style site from scratch (not clone an existing one).
