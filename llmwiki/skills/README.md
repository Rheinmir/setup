# skills/

Multi-step reusable workflows the agent invokes autonomously based on context. Each file defines one skill: when to use it, the steps, and the rules.

## wiki-loop — Quản lý tri thức (ingest → query → lint)
| Skill | File | Purpose |
|-------|------|---------|
| `ingest` | `wiki-loop/ingest.md` | Process a new `raw/` file into wiki pages |
| `query` | `wiki-loop/query.md` | Synthesize an answer from the wiki; persist new insights |
| `lint` | `wiki-loop/lint.md` | Health-check the wiki for orphans, contradictions, stale content |

## dev-loop — Feature lifecycle (propose → impact-check → safe-change → verify)
| Skill | File | Purpose |
|-------|------|---------|
| `propose` | `dev-loop/propose.md` | Plan a feature before coding; create a draft in `wiki/sources/draft/` |
| `impact-check` | `dev-loop/impact-check.md` | Map all dependents of a symbol before modifying it |
| `safe-change` | `dev-loop/safe-change.md` | Modify shared code without breaking existing behaviour |
| `verify-before-commit` | `dev-loop/verify-before-commit.md` | Gate every commit; promote draft to wiki after success |
| `onboard-codebase` | `dev-loop/onboard-codebase.md` | Deep analysis of legacy code to populate Wiki |

## utils — Công cụ phụ trợ
| Skill | File | Purpose |
|-------|------|---------|
| `sync-template` | `utils/sync-template.md` | Sync template improvements to master repo |
| `md-to-html` | `utils/md-to-html.md` | Render markdown → professional HTML |
| `docs-site-macos` | `utils/docs-site-macos-skill.md` | Build macOS-style documentation site |
