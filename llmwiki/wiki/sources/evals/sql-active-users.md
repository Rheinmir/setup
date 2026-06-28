---
type: eval
id: sql-active-users
title: "SQL — select active users"
input: "Viết một câu SQL lấy tất cả user đang active."
expected: "SELECT * FROM users WHERE active = true;"
asserts:
  - 'is-sql-ish'
  - 'icontains:select'
  - 'contains:FROM'
  - 'regex:(?i)\bwhere\b'
rubric: "ĐẠT nếu là một câu SELECT hợp lệ lấy user đang active (có FROM users và điều kiện active). KHÔNG đạt nếu không phải SQL hoặc thiếu điều kiện lọc active."
---

# Golden: SQL active users

A WikiEval golden that exercises the structural tier-1 operators on a code-shaped answer.
`is-sql-ish` is the heuristic smell-test (the output must start with a SQL verb and carry a
clause keyword or a `;`), `icontains:select` is case-insensitive, `contains:FROM` is the
case-sensitive literal, and `regex:(?i)\bwhere\b` confirms a filter clause. All four must
pass for the golden to pass — this is what makes the regression flip in the self-test easy
to trigger (changing one token in the candidate output breaks `contains:FROM`).

## Origin

- **Source:** synthetic seed example for the WikiEval deterministic assertion cascade.
- **Created by:** WikiEval build-now slice (`harness/scripts/wikieval.py`).
