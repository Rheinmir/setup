---
type: draft
title: 250626-onboard-setup
status: proposed
tags: [orca-onboard, output-report]
timestamp: 2026-06-25
---

# 250626-onboard-setup

**Status:** proposed

## Agent CLI Availability
| Agent | Binary | Status |
|-------|--------|--------|
| Antigravity | `agy` | ✅ 1.0.9 |
| OpenCode | `opencode` | ✅ 1.15.13 |
| docs-site-macos | skill | ✅ present |
| Global harness | hooks | ✅ active |

## Cost-aware routing (per user note: "trước khi xem cái gì đắt có thể distill")
This repo is **71 source files**: 39 markdown (skills + prompt templates + wiki), 12 python (harness),
6 shell, 6 json, 3 yaml. **No application code** — it is a docs + skills + harness template repo.

→ The single expensive step in the default pipeline (Phase 1.3 opencode batch analyze, ~1.5M DeepSeek
tokens, ~$0.50) buys **nothing** here: markdown links and python `import`/shell `source` are
mechanical edges that static regex parse extracts deterministically and completely. **Recommendation:
skip opencode batch — Phase 1 = 100% static parse (0 token).**

## Agent Task Assignment
| Task | Agent | Model | Status |
|------|-------|-------|--------|
| Phase 1 — Graph generation (71 files) | **static parse only** (bash+python), Claude for layers/tour | none + Sonnet | done |
| Phase 2 — Domain enrichment | Claude main thread | Sonnet | done |
| Phase 3 — Wiki generation | opencode | DeepSeek Flash v4 | done |
| Phase 4 — HTML docs | deterministic token-fill (python) of docs-site skeleton | none | done |

## What
Onboard `/Users/giatran/orca/design.md/setup` (Rheinmir/setup — the Orca template/skill/harness
ecosystem): build knowledge graph, domain map (skill loops + harness pipeline), wiki, HTML — distilling
into setup's own `llmwiki/`.

## Output
- `.understand-anything/knowledge-graph.json` (static-parse nodes + edges + layers + tour)
- `.understand-anything/ONBOARDING.md` (~distilled)
- `.orca-onboard/intermediate/domain-graph.json`
- `llmwiki/wiki/` (concepts, entities, onboarding-tour)
- `llmwiki/html/onboarding-setup.html`

## Files
| File | Action |
|------|--------|
| `.understand-anything/knowledge-graph.json` | created by Phase 1 static pipeline |
| `.understand-anything/ONBOARDING.md` | created by Phase 1 |
| `.orca-onboard/intermediate/domain-graph.json` | created by Claude |
| `llmwiki/wiki/concepts/*.md`, `entities/*.md` | created |
| `llmwiki/html/onboarding-setup.html` | created |

## Notes
- Invoked via: `/orca-onboard` skill
- Project root: `/Users/giatran/orca/design.md/setup`
- Source files tracked: 71 (excludes existing llmwiki/ content)
- **Phase 1 opencode batch DROPPED** — static parse covers 100% of md/py/sh edges at 0 token

## Cost Estimate (revised down for this repo)
| Phase | Agent | Default est. | Revised est. |
|-------|-------|--------------|--------------|
| Phase 1 (graph) | static parse + Claude layers/tour | ~$0.50 | **~$0.02** (Sonnet only) |
| Phase 2 (domain) | Claude Sonnet | ~$0.50 | ~$0.10 |
| Phase 3 (wiki) | DeepSeek Flash | ~$0.02 | ~$0.02 |
| Phase 4 (HTML) | DeepSeek Flash | ~$0.01 | ~$0.01 |
| **Total** | | **~$1.03** | **~$0.15** |

## Origin
- **Draft:** `wiki/draft/orca/250626-onboard-setup.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
