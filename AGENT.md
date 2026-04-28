# AGENT.md

## Rules
- EVERY wiki file must have an `## Origin` section — source is always traceable
- NEVER write to `raw/`
- ALWAYS update `wiki/index.md` when adding or removing a wiki file
- ALWAYS append to `wiki/log.md` after every operation
- Use `[[wikilinks]]` to cross-reference entries in `wiki/`
- Wiki files live in `concepts/`, `entities/`, or `sources/` — never in `wiki/` root
- Wiki entries are only created AFTER code is committed — never during proposal or planning

## Skills

| Skill | Invoke when | File |
|-------|------------|------|
| `ingest` | A new file appears in `raw/` | `skills/ingest.md` |
| `query` | User asks a question requiring wiki synthesis | `skills/query.md` |
| `lint` | After every 10 ingests, or wiki feels stale | `skills/lint.md` |
| `propose` | Any new feature or change is requested | `skills/propose.md` |
| `impact-check` | Before modifying any shared symbol | `skills/impact-check.md` |
| `safe-change` | Editing code called from more than one place | `skills/safe-change.md` |
| `verify-before-commit` | Before every commit | `skills/verify-before-commit.md` |

## Invocation rules
- New file in `raw/` → invoke `ingest` immediately
- New feature request → invoke `propose` first, stop, wait for approval
- Edit to shared code → invoke `impact-check` then `safe-change`
- Before every commit → invoke `verify-before-commit`
