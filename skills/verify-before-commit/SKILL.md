---
name: verify-before-commit
description: >-
  Gate every commit: run tests, promote wiki draft, verify no regressions
---

# Skill: verify-before-commit

## Purpose
Gate every commit with a checklist that catches regressions, broken types, and missing documentation before code reaches version control.

## When to use
- Before every `git commit` or `git push`
- After completing any implementation task
- When asked to "wrap up" or "finish" a feature

## Steps
1. **Type check** — run the project's type checker (e.g. `tsc --noEmit`, `mypy`). Fix all errors before continuing.
2. **Lint** — run the project's linter (e.g. `eslint`, `ruff`). Fix errors; warnings are acceptable but must be noted.
3. **Tests** — run the full test suite. If any test fails, fix the failure before committing.
4. **Smoke check** — manually verify the golden path of the feature just built works end-to-end.
5. Only after all steps above pass: commit with a message describing *why*, not *what*.
6. **Promote draft** — after commit succeeds, find the corresponding draft file in `wiki/sources/draft/`. Move it to the correct permanent folder (`wiki/concepts/`, `wiki/entities/`, or `wiki/sources/`) and:
   - Fill in any entries left as TBD during proposal.
   - Add a `## Origin` section to the promoted file:
     ```
     ## Origin
     - **Draft:** `wiki/sources/draft/DDMMYY-feature-name-module.md`
     - **Commit:** `<commit hash> — <commit message>`
     - **Date promoted:** YYYY-MM-DD
     ```
7. **Index + log** — update `wiki/index.md` with the promoted file's final location, and append to `wiki/log.md` with the draft filename, commit hash, and destination page.

## Rules
- Never skip steps 1–3 even if "nothing changed in types/tests."
- If no type checker or linter is configured, note this and proceed — but flag it to the user.
- A passing test suite is not the same as a working feature — step 4 is mandatory.
