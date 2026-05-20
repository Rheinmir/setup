---
name: llmwiki
description: LLM Wiki pattern — agentic knowledge base with skills for ingest, query, lint, propose, impact-check, safe-change, verify-before-commit
---

# llmwiki

The LLM Wiki is a persistent, compounding knowledge base maintained by AI agents. Humans drop source documents into `llmwiki/raw/`, the agent distills them into structured wiki pages (`llmwiki/wiki/`), and a set of skills governs the lifecycle: ingest, query, lint, propose, impact-check, safe-change, verify-before-commit.

## When to use

- Setting up a new project with an AI agent
- Onboarding an existing codebase into agentic workflow
- Proposing and implementing features with structured review
- Maintaining project knowledge that persists across sessions

## Setup

The full framework lives in `llmwiki/`:
- `llmwiki/AGENT.md` — behavioral rules and skill table
- `llmwiki/skills/` — individual skill files organized by loop
- `llmwiki/wiki/` — knowledge base (concepts, entities, sources)

For existing projects, run `scripts/migrate-to-llmwiki.sh`.

## Skills

### wiki-loop — Knowledge management
- **ingest**: Process new files from `llmwiki/raw/` into wiki pages
- **query**: Synthesize answers from the wiki; persist new insights
- **lint**: Health-check the wiki for orphans, contradictions, stale content

### dev-loop — Feature development
- **propose**: Plan a feature before coding; create a draft in `llmwiki/wiki/sources/draft/`
- **impact-check**: Map all dependents of a symbol before modifying it
- **safe-change**: Modify shared code without breaking existing behaviour
- **verify-before-commit**: Gate every commit; promote draft to wiki after success
- **onboard-codebase**: Deep analysis of legacy code to populate the wiki

### utils
- **sync-template**: Sync template improvements to master repo
- **md-to-html**: Render markdown → professional HTML
- **docs-site-macos**: Build macOS-style documentation site

## Complete instructions

Read `llmwiki/AGENT.md` for full behavioral rules, skill triggers, and invocation rules. Read each individual skill file in `llmwiki/skills/<loop>/<skill>.md` for detailed steps.
