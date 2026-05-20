# Skill: safe-change

## Purpose
Make a code change while guaranteeing no existing functionality regresses.

## When to use
- Modifying any function, class, or module that is called from more than one place
- Adding behaviour to an existing flow (not a greenfield file)
- Any change where "it worked before" is a hard requirement

## Steps
1. Run `impact-check` skill first — identify all callers and dependents of the target code.
2. Before touching anything, note the current observable behaviour (return values, side effects, output).
3. Make the minimal change required. Do not clean up adjacent code.
4. For each caller identified in step 1, verify the change is backward-compatible or explicitly update the caller.
5. Re-run tests (or describe the manual check if no tests exist) covering the affected paths.
6. Confirm: "Changed X. Verified Y still works. No unintended side effects found." Then run `verify-before-commit` skill.

## Rules
- If tests do not exist for the affected code, write them before making the change.
- If backward compatibility is impossible, surface this to the user before proceeding.
- Touch only what the task requires — no opportunistic refactoring.
