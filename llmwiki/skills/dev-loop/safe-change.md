---
name: safe-change
description: Modify shared code without breaking existing callers
---

# Skill: safe-change

## When to use
Modifying any function, class, or module called from more than one place.

## Steps

1. Run `impact-check` skill — get list of all callers and dependents.
2. Note current observable behaviour (return values, side effects).
3. Make minimal change. Don't touch adjacent code.
4. For each caller from step 1: verify backward-compatible or explicitly update caller.
5. `CHECK: ls <test-dir>/*<module>* 2>/dev/null | head -3` — if tests exist, `RUN: <test-cmd>`. If none, note explicitly in commit message.
6. Confirm: "Changed X. Verified Y still works." Then invoke `verify-before-commit`.

## Rules
- Backward compatibility impossible → surface to user before proceeding.
- Touch only what task requires — no opportunistic refactoring.
- No tests exist → acceptable to note — don't add tests outside task scope.