---
name: wikieval
disable-model-invocation: true
description: Turn wiki golden pages into a CI-blocking eval suite with a cheap→expensive assertion cascade plus a committed regression baseline. Goldens are md files under llmwiki/wiki/sources/evals/ with YAML frontmatter (input, expected, optional rubric, asserts). The engine runs deterministic tier-1 asserts (equals/contains/regex/is-json/is-sql-ish) in pure code, an optional tier-2 similarity, and reports tier-3 (LLM-rubric judge) as the quarantined adapter — never calling a model. Candidate outputs come from --outputs outputs.json so the suite is fully runnable without any model. Trigger when the user says "wikieval", "eval suite for the wiki", "regression gate for goldens", "assertion cascade", "block CI on eval drop", or invokes /wikieval.
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: wikieval

Turn wiki goldens into a CI gate: cheap deterministic asserts decide most goldens, a
committed baseline catches regressions, and the one expensive thing (an LLM judge) is
quarantined behind a single adapter file.

## WHAT

### Purpose và context
- **Purpose:** make wiki golden pages a regression suite checked in pure code (no model), with a committed baseline and a CI exit code that fires only when a metric drops below it.
- **Trigger (when to use):**
  - You want wiki pages to act as a regression suite an agent (or PR) cannot silently break.
  - You have golden input→expected pairs and want them checked in pure code, no model needed.
  - You need a CI step that exits non-zero only when a metric drops below a committed baseline.
  - User says "wikieval", "eval suite for the wiki", "regression gate for goldens", "assertion cascade", "block CI on eval drop", or `/wikieval` (model-invocation disabled — user invokes).
- **Non-goals:** never calls an LLM (tier 3 is reported `needs-judge`, not judged); does not generate candidate outputs (they come from `--outputs`); does not author goldens' content for you.

### Mental model
`golden (input · expected · rubric? · asserts?) + candidate output → cascade: tier 1 asserts → [tier 2 similarity] → [tier 3 needs-judge] → per-golden pass+score → baseline (write) | regression diff (check)`. Cheap tiers short-circuit; the expensive one sits behind one adapter file.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | goldens `llmwiki/wiki/sources/evals/*.md` | có | YAML frontmatter `input`, `expected`, optional `rubric`, optional `asserts`, optional `id`; also R9 `type` + R2 `## Origin` |
| In | `--outputs <outputs.json>` | có | candidate outputs per golden — makes the suite runnable without any model |
| In | mode | không | none = report; `--write-baseline`; `--check` |
| In | `harness/wikieval.config.yaml` | không | adapter config (`verified: false`): judge model, rubric prompt, `embedding.backend` |
| Out | report | có | per-golden pass/fail/score/`needs-judge` |
| Out | `harness/metrics/eval-baseline.json` | với `--write-baseline` | committed per-golden pass + score |
| Out | exit code | với `--check` | 0 = no regression; 2 = a metric dropped below baseline (+ regression diff) |

### Rules và capabilities
- RULE-01 (MUST): If a golden declares `asserts`, tier 1 alone decides pass/fail. Unknown ops fail closed.
- RULE-02 (MUST): tier 2 similarity is only reached when a golden has no asserts; skipped + noted unless `embedding.backend` is set (`difflib` = stdlib lexical, offline; a real model id stays skipped until the adapter is wired).
- RULE-03 (MUST): the `judge(output, rubric) -> {score, reason}` stub is NEVER called in deterministic mode; escalated goldens are reported `needs-judge`.
- RULE-04 (MUST): `--check` is a deterministic diff against the committed baseline; exit 2 only on a drop.
- RULE-05 (MUST): the adapter boundary is one file — finalizing the judge changes `harness/wikieval.config.yaml` + `judge()` only; the rest of WikiEval does not change.
- Capabilities: read goldens + candidate outputs + adapter config; write baseline file; no network, no model.

### Failure boundaries
- An assert fails → golden **failed** (report); with `--check`, drop vs baseline → exit 2 + regression diff.
- Unknown assert op → **failed** closed (not skipped).
- Golden without asserts and no `embedding.backend` → tier 2 skipped + noted; rubric escalation → `needs-judge` (not a pass, not a fail).
- Missing/invalid `--outputs` file → **blocked**: cannot run without candidates.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | goldens, `--outputs` | Load goldens + candidate outputs | pairs per golden | missing outputs → blocked |
| W02 | deterministic | pair, `asserts` | Tier 1 deterministic asserts | pass/fail if asserts declared | unknown op → fail closed |
| W03 | deterministic | pair, config | Tier 2 similarity (only if no asserts) | score or "skipped + noted" | backend unset → skip |
| W04 | deterministic | rubric | Tier 3 → report `needs-judge` (judge never called) | `needs-judge` | — |
| W05 | deterministic | results, mode | Report / `--write-baseline` / `--check` diff vs baseline | report, baseline file, exit 0/2 | drop → exit 2 |

Chi tiết từng bước (nguồn chân lý cho W01–W05):

#### The assertion cascade (cheap → expensive, short-circuits)
1. **tier 1 — deterministic asserts** (build-now core): `equals` / `contains` / `icontains` /
   `not-contains` / `regex` / `is-json` / `is-sql-ish` run on the candidate output. If a golden
   declares `asserts`, tier 1 alone decides pass/fail. Unknown ops fail closed.
2. **tier 2 — similarity** (OPTIONAL): only reached when a golden has no asserts. Skipped + noted
   unless `embedding.backend` is set in the config (`difflib` = stdlib lexical, offline; a real
   model id stays skipped until the adapter is wired).
3. **tier 3 — LLM-rubric judge** = THE ADAPTER (`verified: false`). The stub
   `judge(output, rubric) -> {score, reason}` is NEVER called in deterministic mode; escalated
   goldens are reported `needs-judge`.

#### Goldens
Markdown under `llmwiki/wiki/sources/evals/` with YAML frontmatter: `input`, `expected`,
optional `rubric`, optional `asserts` (quote each: `'contains:foo'`, `'regex:^...$'`,
`'is-json'`, `'equals:bar'`, `'is-sql-ish'`). Optional `id` (defaults to filename stem).
Each golden also obeys R9 (frontmatter `type`) and R2 (`## Origin`).

#### Run it (no model required)
```sh
# run the cascade with a fixed candidate set, print a report
python3 harness/scripts/wikieval.py --outputs harness/evals/wikieval-outputs.example.json

# write / refresh the committed baseline (per-golden pass + score)
python3 harness/scripts/wikieval.py --outputs <outputs.json> --write-baseline

# CI gate: re-run and exit 2 if any metric dropped below baseline (deterministic diff)
python3 harness/scripts/wikieval.py --outputs <outputs.json> --check
```
Baseline: `harness/metrics/eval-baseline.json`. Adapter config: `harness/wikieval.config.yaml`.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | capability_optional | golden has no `asserts` AND `embedding.backend` set | tier 2 similarity (`difflib` offline) | backend unset or real model id not wired → skipped + noted | W04 |
| B02 | user_optional | `--write-baseline` | write/refresh `harness/metrics/eval-baseline.json` | — | end |
| B03 | user_optional | `--check` | deterministic diff vs baseline, exit 2 on drop | no baseline → run `--write-baseline` first | end |

### Validation và stopping
Everything is code-checked: asserts, cascade, baseline diff and exit code are deterministic. Only tier 3 needs review (`needs-judge`) and stays out of the pass/fail decision until the adapter is finalized.

#### Self-test (build-now slice)
```sh
OUT=harness/evals/wikieval-outputs.example.json
python3 harness/scripts/wikieval.py --outputs $OUT --write-baseline   # both goldens PASS
python3 harness/scripts/wikieval.py --outputs $OUT --check            # exit 0 — no regression
# flip one output to break an assert, then:
python3 harness/scripts/wikieval.py --outputs <broken.json> --check   # exit 2 + regression diff
```

### Examples
- **Positive:** `python3 harness/scripts/wikieval.py --outputs harness/evals/wikieval-outputs.example.json --check` after writing baseline → both goldens PASS → exit 0.
- **Boundary/failure:** flip one candidate so `'contains:foo'` no longer matches → `--check` exits 2 with the regression diff naming that golden.
- **Boundary:** golden with only `rubric`, no asserts, no `embedding.backend` → tier 2 skipped + noted, reported `needs-judge`; judge not called.

### Reference — Adapter boundary (build-now-adapt-later)
- **Built + tested now:** tier-1 asserts, the cascade, baseline write + `--check` regression diff.
- **Quarantined (`verified: false`):** `harness/wikieval.config.yaml` (judge model + rubric prompt,
  embedding backend — each a flagged `# ASSUMPTION`) and the `judge()` stub.
- **Finalize:** wire `judge()` to the configured model, run the self-test, flip `verified: true`.
  One file changes; the rest of WikiEval does not.

### Reference — Files
- `harness/scripts/wikieval.py` — the eval engine.
- `harness/wikieval.config.yaml` — the one adapter (`verified: false`).
- `harness/metrics/eval-baseline.json` — committed regression baseline (generated).
- `llmwiki/wiki/sources/evals/*.md` — goldens.
- `harness/evals/wikieval-outputs.example.json` — self-test candidate outputs.
