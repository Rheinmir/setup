# skills/

Multi-step reusable workflows the agent invokes autonomously based on context. Each file defines one skill: when to use it, the steps, and the rules.

| Skill | Purpose |
|-------|---------|
| `ingest` | Process a new `raw/` file into wiki pages |
| `query` | Synthesize an answer from the wiki; persist new insights |
| `lint` | Health-check the wiki for orphans, contradictions, stale content |
| `propose` | Plan a feature before coding; create a draft in `wiki/sources/draft/` |
| `impact-check` | Map all dependents of a symbol before modifying it |
| `safe-change` | Modify shared code without breaking existing behaviour |
| `verify-before-commit` | Gate every commit; promote draft to wiki after success |
