---
type: eval
id: r2-origin
title: "R2 — every wiki file needs an Origin section"
input: "Theo rule R2, mọi file nội dung wiki bắt buộc phải có section nào để luôn truy được nguồn gốc?"
expected: "Section '## Origin'."
asserts:
  - 'contains:Origin'
  - 'regex:(?i)\borigin\b'
rubric: "ĐẠT nếu câu trả lời nêu đúng rằng mọi wiki file phải có section '## Origin' (để truy nguồn gốc theo R2). KHÔNG đạt nếu nêu một section khác hoặc bỏ sót."
---

# Golden: R2 origin-required

A WikiEval golden. The frontmatter above is the machine-read contract: `input` is the
question, `expected` is the reference answer, and `asserts` are the tier-1 deterministic
checks the engine runs against the candidate output. This golden is decided entirely at
tier 1 (cheap, no model) — the `rubric` is only consumed if the cascade ever escalates to
the tier-3 judge adapter, which the deterministic engine does not call.

The asserts encode the R2 rule from `harness/policy.yaml`: any answer about traceability
of a wiki page must name the `## Origin` section. `contains:Origin` is the literal check;
`regex:(?i)\borigin\b` is a case-insensitive word-boundary backstop.

## Origin

- **Source:** R2 `origin-required` rule in `harness/policy.yaml` and `harness/validators/origin_required.py`.
- **Created by:** WikiEval build-now slice (`harness/scripts/wikieval.py`) as a seed golden.
