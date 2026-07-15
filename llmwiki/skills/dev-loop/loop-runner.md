---
name: loop-runner
disable-model-invocation: true
description: Deterministic guardrailed agent-loop driver — wrap any step with propose → deterministic-verify → (critique → revise) and enforce hard termination guards (max_iter, wall-clock budget, no-progress via state-hash, escalate-to-human). The control loop + guards + progress detection are deterministic; the LLM critique/revise step is the one quarantined adapter. Trigger when an agent fix-loop must not spin forever and must not be able to argue its way around a failing test.
---

# Skill: loop-runner

## Purpose
Drive an autonomous fix loop that CANNOT run away. VERIFY is a shell command whose exit-code 0
means pass (pytest / tsc / a lint) — preferred over LLM self-judgment, because the agent cannot
argue its way around a red exit code. The termination guards are MANDATORY and all deterministic.

## When to use
- An agent loops edit-then-check repeatedly (fix failing tests, satisfy a typechecker/lint).
- You need a hard guarantee it stops: bounded iterations, bounded wall-clock, stop-on-stall, escalate.
- You want a replayable run-log + a reflexion lesson trail, without trusting the model to "decide it's done".

## Build-now / adapt-later boundary
- DETERMINISTIC (built + tested now): control loop, all guards, state-hash progress detection,
  run-log artifact, reflexion. → `harness/scripts/loop-runner.py`
- QUARANTINED adapter (`verified: false`): the LLM critique/revise step + the tunable guard values.
  → `harness/loop-runner.config.yaml` (the ONE file you edit to adapt). The default revise step is a
  no-op / shell stub, so the whole loop runs and self-tests WITHOUT an LLM.

## How to run
```
# self-test — 5 deterministic guard scenarios, no LLM, no deps
python3 harness/scripts/loop-runner.py selftest

# real loop around a verify command (config supplies the guard defaults)
python3 harness/scripts/loop-runner.py run \
  --config harness/loop-runner.config.yaml \
  --verify "pytest -q" \
  --revise "<shell cmd, or the real LLM-revise adapter>" \
  --state "src/**" --log harness/out/loop-runner-run.json
```
CLI flags override config. Process exit: 0 SUCCESS · 2 MAX_ITER · 3 TIMEOUT · 4 NO_PROGRESS · 5 ESCALATE.

## The loop (one iteration)
1. PROPOSE — the current workspace state (initial proposal, or the last iteration's revise).
2. VERIFY — run the shell cmd; exit 0 → stop SUCCESS.
3. GUARDS (checked every iteration, all enforced):
   - `max_iter` — hard backstop (always on; cannot be disabled).
   - `budget_seconds` — wall-clock budget (0 = off).
   - `no_progress_k` — state-hash unchanged for K consecutive iterations → NO_PROGRESS (off if no `state_paths`).
   - `escalate_after_iter` — hand off to a human → ESCALATE (0 = off).
4. REFLEXION — append one "lesson" line to the episodic-memory wiki page on failure.
5. CRITIQUE → REVISE — the quarantined adapter (the LLM, or a stub / shell cmd). Then repeat.

## Rules
- VERIFY is deterministic (exit code). NEVER let the LLM self-judge "done".
- The guards are mandatory — never remove one to "let it finish".
- Quarantined values (guard params + the revise hook) live ONLY in the config. The same value in two places is a leak.
- Under `verified: false`, behave fail-safe: assume the revise guess is wrong until conformance proves otherwise.
- The self-test must stay green and must NOT write into the real wiki (its episodic page is redirected to a temp dir).

## Output
- Run-log JSON (iterations, verdicts, termination reason) at `run_log.path`.
- Episodic-memory lessons appended to `reflexion.episodic_memory_page` (lazily created with valid frontmatter + `## Origin`).
