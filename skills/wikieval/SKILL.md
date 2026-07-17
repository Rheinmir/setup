---
name: wikieval
disable-model-invocation: true
description: Turn wiki golden pages into a CI-blocking eval suite with a cheap→expensive assertion cascade plus a committed regression baseline. Goldens are md files under llmwiki/wiki/sources/evals/ with YAML frontmatter (input, expected, optional rubric, asserts). The engine runs deterministic tier-1 asserts (equals/contains/regex/is-json/is-sql-ish) in pure code, an optional tier-2 similarity, and reports tier-3 (LLM-rubric judge) as the quarantined adapter — never calling a model. Candidate outputs come from --outputs outputs.json so the suite is fully runnable without any model. Trigger when the user says "wikieval", "eval suite for the wiki", "regression gate for goldens", "assertion cascade", "block CI on eval drop", or invokes /wikieval.
---

# Skill: wikieval

Turn wiki goldens into a CI gate: cheap deterministic asserts decide most goldens, a
committed baseline catches regressions, and the one expensive thing (an LLM judge) is
quarantined behind a single adapter file.

## When to use
- You want wiki pages to act as a regression suite an agent (or PR) cannot silently break.
- You have golden input→expected pairs and want them checked in pure code, no model needed.
- You need a CI step that exits non-zero only when a metric drops below a committed baseline.

## The assertion cascade (cheap → expensive, short-circuits)
1. **tier 1 — deterministic asserts** (build-now core): `equals` / `contains` / `icontains` /
   `not-contains` / `regex` / `is-json` / `is-sql-ish` run on the candidate output. If a golden
   declares `asserts`, tier 1 alone decides pass/fail. Unknown ops fail closed.
2. **tier 2 — similarity** (OPTIONAL): only reached when a golden has no asserts. Skipped + noted
   unless `embedding.backend` is set in the config (`difflib` = stdlib lexical, offline; a real
   model id stays skipped until the adapter is wired).
3. **tier 3 — LLM-rubric judge** = THE ADAPTER (`verified: false`). The stub
   `judge(output, rubric) -> {score, reason}` is NEVER called in deterministic mode; escalated
   goldens are reported `needs-judge`.

## Goldens
Markdown under `llmwiki/wiki/sources/evals/` with YAML frontmatter: `input`, `expected`,
optional `rubric`, optional `asserts` (quote each: `'contains:foo'`, `'regex:^...$'`,
`'is-json'`, `'equals:bar'`, `'is-sql-ish'`). Optional `id` (defaults to filename stem).
Each golden also obeys R9 (frontmatter `type`) and R2 (`## Origin`).

## Run it (no model required)
```sh
# run the cascade with a fixed candidate set, print a report
python3 harness/scripts/wikieval.py --outputs harness/evals/wikieval-outputs.example.json

# write / refresh the committed baseline (per-golden pass + score)
python3 harness/scripts/wikieval.py --outputs <outputs.json> --write-baseline

# CI gate: re-run and exit 2 if any metric dropped below baseline (deterministic diff)
python3 harness/scripts/wikieval.py --outputs <outputs.json> --check
```
Baseline: `harness/metrics/eval-baseline.json`. Adapter config: `harness/wikieval.config.yaml`.

## Self-test (build-now slice)
```sh
OUT=harness/evals/wikieval-outputs.example.json
python3 harness/scripts/wikieval.py --outputs $OUT --write-baseline   # both goldens PASS
python3 harness/scripts/wikieval.py --outputs $OUT --check            # exit 0 — no regression
# flip one output to break an assert, then:
python3 harness/scripts/wikieval.py --outputs <broken.json> --check   # exit 2 + regression diff
```

## Adapter boundary (build-now-adapt-later)
- **Built + tested now:** tier-1 asserts, the cascade, baseline write + `--check` regression diff.
- **Quarantined (`verified: false`):** `harness/wikieval.config.yaml` (judge model + rubric prompt,
  embedding backend — each a flagged `# ASSUMPTION`) and the `judge()` stub.
- **Finalize:** wire `judge()` to the configured model, run the self-test, flip `verified: true`.
  One file changes; the rest of WikiEval does not.

## Files
- `harness/scripts/wikieval.py` — the eval engine.
- `harness/wikieval.config.yaml` — the one adapter (`verified: false`).
- `harness/metrics/eval-baseline.json` — committed regression baseline (generated).
- `llmwiki/wiki/sources/evals/*.md` — goldens.
- `harness/evals/wikieval-outputs.example.json` — self-test candidate outputs.
