---
type: draft
title: OKF v0.1 research + macOS liquid-glass docs site
status: proposed
tags: [docs-site-macos, last30days, output-report]
timestamp: 2026-06-15
---

# 150626-okf-docs-site

## What
Researched Google's newly announced Open Knowledge Format (OKF) v0.1 via `/last30days`, then built a single-file macOS liquid-glass docs site summarizing it.

## Output
- last30days research run (Reddit 18 / HN 28 / GitHub / Polymarket); raw saved to `~/Documents/Last30Days/open-knowledge-format-okf-google-raw-v3.md`
- Single-file HTML docs site with 6 sections (Overview, The Spec, How It Works, Reference Implementations, Ecosystem Fit, Community Reception), 3 animated draggable SVG diagrams (pipeline, concept graph, llms.txt→OKF→MCP stack), macOS chrome repo-card, copy-able code panel, liquid-glass surfaces.

Key facts captured:
- OKF v0.1 published June 12, 2026 by Sam McVeety & Amir Hormati (Google Cloud)
- Spec: one required frontmatter field (`type`); optional title/description/resource/tags/timestamp; consumers tolerate unknown keys
- Repo: GoogleCloudPlatform/knowledge-catalog (~1.3K stars), 3 sample bundles (GA4/Stack Overflow/Bitcoin), 2 reference impls (BigQuery ADK+Gemini agent, static HTML visualizer)
- Ecosystem: stacks with llms.txt (signpost) + MCP (live tools), not a competitor
- Reception: HN 69pts lukewarm-curious; dev wait-and-see

## Files
| File | Action |
|------|--------|
| `llmwiki/html/150626-open-knowledge-format.html` | created |
| `~/Documents/Last30Days/open-knowledge-format-okf-google-raw-v3.md` | created (research raw) |

## Notes
- Invoked via: `/last30days` + `/docs-site-macos` skills
- Preview: http://localhost:8765/llmwiki/html/150626-open-knowledge-format.html

## Origin
- **Draft:** `wiki/sources/draft/150626-okf-docs-site.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
