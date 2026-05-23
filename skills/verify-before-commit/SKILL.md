---
name: verify-before-commit
description: Gate every commit — typecheck, lint, smoke, then promote draft to wiki
---

# Skill: verify-before-commit

## When to use
After completing any implementation task, before `git commit`.

## Steps

**Pre-commit:**
1. `RUN: <type-check-cmd>` — detect from repo: `npx tsc --noEmit` (package.json) / `go build ./...` (go.mod). Fix all errors.
2. `RUN: <lint-cmd>` — detect: `npx eslint src/` / `go vet ./...`. Fix errors; note warnings.
3. `RUN: <test-cmd>` — detect: `npm test` / `go test ./...`. Fix failures.
4. Smoke check: manually verify the golden path works end-to-end.
5. Commit with message describing *why*, not *what*.

**Post-commit — mandatory, never skip:**
6. Find the draft in `llmwiki/wiki/sources/draft/` matching this feature.
   - Promote it to `llmwiki/wiki/concepts/` or `llmwiki/wiki/sources/` (permanent).
   - Add `## Origin` section: `Draft: <path>` / `Commit: <hash> — <msg>` / `Date: YYYY-MM-DD`
   - `CHECK: grep -l "## Origin" <promoted-file>` — must return the file.
7. `RUN: echo "promoted" >> llmwiki/wiki/log.md` — then edit log properly; update `llmwiki/wiki/index.md`.

> No corresponding draft (hotfix/refactor)? Note "no draft — <reason>" in log.md and skip step 6.

All steps mandatory. No exceptions.
