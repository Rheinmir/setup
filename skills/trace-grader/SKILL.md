---
name: trace-grader
description: >-
  Score the PATH an agent took (tool choice, ordering, retries, repeatability, grounding) — not
  just its final answer — to catch "corrupt success" (right answer via a bad/unsafe path) and
  flakiness. Deterministic trace schema + pass^k repeatability + config-driven rule checks
  (forbidden tool, out-of-order, retry-storm, excessive steps, edited-without-read grounding).
  Parses canonical traces.json, hooklib.audit / code-logger events.jsonl, OR a full Claude Code
  session transcript (--transcript, richest source: recovers retrieval args + observation + per-
  step ok). Trigger when the user says "grade the trajectory", "score the path not the answer",
  "did it cheat / take a bad path", "did it look before it acted / grounding", "corrupt success",
  "is this flaky / does it repeat", "pass^k", "grade a session transcript", "trace grader", or
  invokes /trace-grader.
---

# Skill: trace-grader

Grade an agent's **trajectory**, not just its output. A run can return the right
answer via a bad path (force-pushed, retry-stormed, edited a file it never read) —
"corrupt success" — and it can be flaky (passes once, fails on rerun). An
answer-only checker is blind to both; TraceGrader inspects the path.

## When to use
- You have one or more agent runs (traces) and want to know *how* the answer was
  reached, not only *whether* it was reached.
- You need a repeatability gate: "does this task pass on ALL k reruns?" (`pass^k`).
- You want a deterministic, CI-gateable signal on tool choice / ordering / retries
  / step budget — before reaching for an LLM judge.

## What it is (build-now vs adapter)
Built now — deterministic, no unknowns:
- **Trace schema (the contract):** a run = list of steps `{step, tool, args, observation, ok}`.
- **Parsers:** canonical `traces.json`; the audit jsonl shape written by
  `llmwiki/.claude/hooks/hooklib.audit()` (and code-logger `events.jsonl`); OR a full
  Claude Code **session transcript** (`--transcript`) — the richest source: it recovers
  retrieval args (Grep `pattern`, Read `file_path`), `observation`, and per-step `ok`,
  so grounding + outcome are observable. Sidechain (sub-agent) lines are skipped; a
  transcript carries no task-verdict so its `run.ok` is forced True — trust the FLAGS.
- **`pass^k`:** k runs of one task → require ALL k to deliver; report `pass^k`.
- **Rule checks (config-driven):** `forbidden_tool` (high), `out_of_order` (medium,
  via `must_precede`), `retry_storm` (medium, >N consecutive same-tool failures),
  `excessive_steps` (low, > budget), `edited_without_read` (medium — grounding proxy:
  an Edit/MultiEdit to a file never Read/Grep'd/Write-authored first; gated by
  `grounding.enabled`).
- **Verdict per run:** `clean-pass` / `pass-with-warnings` / `corrupt-success`
  (delivered **and** a high-severity flag) / `fail` (not delivered).

Quarantined behind ONE adapter — `harness/trace-grader.config.yaml`, `verified:false`:
- the rule PARAMETERS (forbidden list, retry threshold, step budget, order
  constraints) — project-specific best-guesses, each `# ASSUMPTION`;
- the inferential **agent-as-judge** axis (task-completion / tool-rationale /
  planning rubric) — `judge_trajectory()` is a STUB, **not called** until a judge
  model is configured and the file is flipped `verified:true`.

Adapting later = edit that one file, never the engine.

## How to run
```bash
# bundled 3-case self-test (clean / corrupt / flaky)
python3 harness/scripts/trace-grader.py --self-test

# grade canonical traces, an audit log, or a full session transcript; --json for machine output
python3 harness/scripts/trace-grader.py --traces traces.json
python3 harness/scripts/trace-grader.py --audit .claude/audit/<date>.jsonl --task my-task
python3 harness/scripts/trace-grader.py --transcript ~/.claude/projects/<proj>/<session>.jsonl --task my-task
```
Exit code is `3` if any run is `corrupt-success` or any task is flaky (so CI can gate).

## Steps
1. **Collect traces.** Either emit `traces.json` in the schema above, or point
   `--audit` at a `hooklib.audit()` jsonl (one run per `session_id`).
2. **Set the boundary.** Edit `harness/trace-grader.config.yaml` ONLY — forbidden
   tools, `retry_threshold`, `step_budget`, `order_constraints`. Keep it the single
   place these values live.
3. **Grade.** Run the grader; read per-run verdicts + flags + the `pass^k` block.
4. **Act on signal.** `corrupt-success` = right answer, bad/unsafe path → investigate
   the flagged step. `pass^k = FAIL` = flaky → not safe to rely on.
5. **(Later) verify the adapter.** Validate thresholds against real traces, then flip
   `verified:true`. Only then consider enabling the agent-as-judge axis.

## Rules
- The config file is the ONLY place rule parameters live. Same guess in two places = a leak.
- Never present a guessed threshold as verified — the file stays `verified:false` until validated.
- The agent-as-judge axis is OFF and uncalled until configured + verified; never fake an inferential score.
- The audit parser cannot see per-step `ok`/observations, so `retry_storm` won't fire from a pure
  audit log — use full `traces.json` when you need failure-aware checks.

## Files
| File | Role |
|------|------|
| `harness/scripts/trace-grader.py` | deterministic engine: schema, parsers, pass^k, rule checks, report, judge STUB |
| `harness/trace-grader.config.yaml` | the ONE adapter (`verified:false`) — every value a `# ASSUMPTION` |
| `harness/tests/trace-grader.fixtures.json` | self-test fixtures: clean / corrupt-success / flaky |
