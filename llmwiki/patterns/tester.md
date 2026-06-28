# Tester / QA — Patterns & Anti-patterns

> Protected reference (overstack pattern library). Seeded best-guess — pending curation.

## Patterns

### Shape tests like a pyramid (cheap → expensive)
- **When:** Any suite that mixes fast deterministic checks with slow, costly, or model-based ones.
- **Do:** Run many cheap deterministic asserts first, fewer similarity checks next, fewest LLM-judge calls last — wikieval's tier-1→tier-3 cascade.
- **Why:** Most failures are caught in milliseconds for free, so expensive judges only ever run on the survivors.

### Golden datasets with a committed baseline
- **When:** Output is stable and you must catch regressions across changes to prompts, code, or models.
- **Do:** Freeze known-good input/expected pairs as goldens (wikieval: `llmwiki/wiki/sources/evals/`), commit a baseline score, and fail CI when it drops.
- **Why:** Turns "seems fine" into a measurable floor, so any regression surfaces as a number instead of a surprise.

### Grade the trajectory, not just the answer
- **When:** Testing tool-using agents where the path taken matters as much as the final result.
- **Do:** Score tool choice, ordering, retries, and repeatability with trace-grader; flag forbidden tools, out-of-order steps, and retry storms.
- **Why:** Catches "corrupt success" — a right answer reached via an unsafe, flaky, or non-repeatable path.

### LLM-as-judge as a gated, multi-judge step
- **When:** Output is open-ended — prose, plans, code — with no single exact-match expected value.
- **Do:** Score against an explicit rubric, and for high-stakes calls use council's blind multi-model panel so no judge favors its own answer.
- **Why:** Adds graded judgment where equality fails, while blind peer-ranking and a chairman curb single-model bias.

### Deterministic fixtures plus property and negative tests
- **When:** Behavior depends on inputs, time, randomness, or external state you can pin down.
- **Do:** Pin seeds, clock, and fixtures so reruns match; assert invariants over generated inputs; and include negative, adversarial cases.
- **Why:** Reproducible runs make failures real signals, and property/negative coverage finds edges that hand-picked happy paths miss.

## Anti-patterns

### Flaky tests
- **Smell:** The same commit passes and fails across reruns, and the team's habit is "just run it again".
- **Why bad:** Red stops meaning broken, so real regressions get re-run away and trust in the suite collapses.
- **Instead:** Quarantine the flake, fix the root cause (time, seed, order, network), and use pass^k repeatability to detect it.

### Testing implementation, not behavior
- **Smell:** Tests assert internal calls or private structure and break on refactors that leave behavior unchanged.
- **Why bad:** Brittle tests block safe refactors and give false confidence while the real contract stays unverified.
- **Instead:** Assert observable outputs and contracts; for agents, check the outcome and allowed path, not the exact wording.

### No negative cases
- **Smell:** Every test is happy-path, and nothing covers bad input, error states, refusals, or injection attempts.
- **Why bad:** Failure modes and guardrails ship completely unverified, so the first real bad input becomes the test.
- **Instead:** Add adversarial goldens — malformed input, forbidden-tool attempts, prompt injection, and expected refusals.

### Trusting local over CI
- **Smell:** "Works on my machine", merging on a local green, and skipping or ignoring the CI run.
- **Why bad:** Environment drift hides breakage, results are not reproducible, and main lands broken for everyone else.
- **Instead:** Treat CI as the floor — the same containerized run gates the merge, and local is only a preview.

### Eval with no baseline
- **Smell:** Scores are reported as raw numbers with no committed reference, signed off as "looks good enough".
- **Why bad:** You cannot distinguish improvement from regression, so quality drifts downward silently between changes.
- **Instead:** Commit a baseline and block on the delta against it — wikieval's regression gate does exactly this.

## Origin
- Seeded from /last30days research (AI agent evaluation/testing 2026) + overstack eval tools (wikieval, trace-grader, council) — 2026-06-29.
