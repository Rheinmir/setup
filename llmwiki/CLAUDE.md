Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

Tradeoff: These guidelines bias toward caution over speed. For trivial tasks, use judgment.

1. Think Before Coding
Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing:

State your assumptions explicitly. If uncertain, ask.
If multiple interpretations exist, present them - don't pick silently.
If a simpler approach exists, say so. Push back when warranted.
If something is unclear, stop. Name what's confusing. Ask.

2. Simplicity First
Minimum code that solves the problem. Nothing speculative.

No features beyond what was asked.
No abstractions for single-use code.
No "flexibility" or "configurability" that wasn't requested.
No error handling for impossible scenarios.
If you write 200 lines and it could be 50, rewrite it.
Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

3. Surgical Changes
Touch only what you must. Clean up only your own mess.

When editing existing code:

Don't "improve" adjacent code, comments, or formatting.
Don't refactor things that aren't broken.
Match existing style, even if you'd do it differently.
If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:

Remove imports/variables/functions that YOUR changes made unused.
Don't remove pre-existing dead code unless asked.
The test: Every changed line should trace directly to the user's request.

4. Goal-Driven Execution
Define success criteria. Loop until verified.

Transform tasks into verifiable goals:

"Add validation" → "Write tests for invalid inputs, then make them pass"
"Fix the bug" → "Write a test that reproduces it, then make it pass"
"Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

These guidelines are working if: fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
## Rules
- FOLLOW the instructions in README.md in wiki folder
- EVERY wiki file must have an `## Origin` section — source is always traceable
- NEVER write to `raw/`
- ALWAYS update `wiki/index.md` when adding or removing a wiki file
- ALWAYS append to `wiki/log.md` after every operation
- Use `[[wikilinks]]` to cross-reference entries in `wiki/`
- Wiki files live in `concepts/`, `entities/`, `sources/`, `draft/`, `architecture/`, or `tours/` — never in `wiki/` root (enforced by R5 validator)
- Wiki entries are only created AFTER code is committed — never during proposal or planning
- Match a file's verbosity to its reader. Markdown that a machine or agent reads and executes (SKILL.md, policy.yaml, AGENT.md, pure reference tables) may be concise. Documentation a human reads or reviews (review reports, ADRs, README, CONTRIBUTING and runbooks, output-reports, HTML pages) must be full, readable prose with complete sentences — never caveman or over-compressed shorthand there; caveman is only for ephemeral agent-to-agent messages. (Feedback 2026-06-27.)

## Skills

| Skill | Invoke when | File | Loop |
|-------|------------|------|------|
| `ingest` | A new file appears in `raw/` | `skills/wiki-loop/ingest.md` | wiki-loop |
| `query` | User asks a question requiring wiki synthesis | `skills/wiki-loop/query.md` | wiki-loop |
| `lint` | After every 10 ingests, or wiki feels stale | `skills/wiki-loop/lint.md` | wiki-loop |
| `propose` | Any new feature or change is requested | `skills/dev-loop/propose.md` | dev-loop |
| `impact-check` | Before modifying any shared symbol | `skills/dev-loop/impact-check.md` | dev-loop |
| `safe-change` | Editing code called from more than one place | `skills/dev-loop/safe-change.md` | dev-loop |
| `verify-before-commit` | Before every commit | `skills/dev-loop/verify-before-commit.md` | dev-loop |
| `orca-workflow` | Daily propose → gate → dispatch with Orca | `skills/orchestrate/orca-workflow.md` | orchestrate |
| `orca-onboard` | Parallel codebase onboarding with Orca | `skills/orchestrate/orca-onboard.md` | orchestrate |

## Invocation rules
- New file in `raw/` → invoke `ingest` immediately
- New feature request → invoke `propose` first, stop, wait for approval
- Edit to shared code → invoke `impact-check` then `safe-change`