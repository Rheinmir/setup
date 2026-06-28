# Agent Loops — Patterns & Anti-patterns

> Protected reference (overstack pattern library). Seeded best-guess — pending curation.
> Crawled from [signals.forwardfuture.com/loop-library](https://signals.forwardfuture.com/loop-library/) (70 loops) via the overstack `/web-crawl` test, 2026-06-29.

A **loop** = a repeatable AI-agent workflow with an explicit success criterion and a stopping
condition. Many here mirror overstack's own DNA: *self-improving champion* ≈ `success-flywheel`,
*Groundtruth* ≈ `claim-receipts`, *devil's-advocate / multi-LLM convergence* ≈ `council`,
*test stabilizer* ≈ flaky-test handling, *fresh-clone* ≈ the harness fresh-clone test,
*cross-run playbook* ≈ the `success-flywheel` playbook.

## The loop meta-pattern (what every good loop has)
1. **Repeatable trigger** — a recurring task worth automating (the *Loop Hiring Manager* rejects one-offs).
2. **Explicit success criterion** — a measurable bar ("100/100", "<50 ms", "streak of N green").
3. **Stopping condition** — when to halt (target met, no progress, or a real blocker), not "run forever".
4. **Independent verification** — a separate reviewer/holdout proves the win (*builder-reviewer*, *champion on fresh cases*).
5. **Promote on proof** — only durable, repeatedly-won lessons become playbooks/rules (*cross-run playbook*).

## Patterns

### Builder–Reviewer autonomy loop
- **When:** Code work that must converge to "tests pass" without a human in every cycle.
- **Do:** Pass the artifact between a builder agent and an independent reviewer agent until the reviewer's checks succeed.
- **Why:** Independent review catches what the builder rationalizes; the loop ends on objective green, not self-assessment.

### Self-improving champion (promote on holdout)
- **When:** Iterating prompts/strategies where you risk overfitting to the cases you already saw.
- **Do:** Promote a change only when it wins on FRESH holdout cases, not the ones it was tuned on.
- **Why:** Guards against degeneration-of-thought and cherry-picking; mirrors overstack `success-flywheel` (promote winning patterns).

### Fresh-clone onboarding loop
- **When:** Verifying setup/docs have no hidden assumptions baked into your local machine.
- **Do:** Repeat clean onboarding from a fresh clone until a first-time user (or agent) hits zero obstacles.
- **Why:** Surfaces "works on my machine" gaps; overstack runs this as `harness-update`/fresh-clone tests.

### Evidence-first / Groundtruth audit
- **When:** You need a project's real status, not its claimed status.
- **Do:** Audit from direct evidence (logs, runs, files) with severity, and verify every claim against behavior.
- **Why:** Separates proof from assertion — the same principle as overstack `claim-receipts`.

### Stopping-condition before automation
- **When:** Standing up ANY new loop.
- **Do:** Write the success criterion and stopping condition FIRST; a loop without them is a runaway, not a workflow.
- **Why:** Bounds cost and prevents infinite spend; the *loop-auditor* later assigns keep / pivot / retire / kill.

## Anti-patterns

### Unproven automation
- **Smell:** A loop is built for work that has only happened once, or whose success can't be measured.
- **Why bad:** You pay automation cost for a task that may never recur, with no way to know it worked.
- **Instead:** Gate new loops behind a *Loop Hiring Manager* — recurring + measurable + verifiable, or don't loop it.

### No stopping condition (runaway loop)
- **Smell:** The loop "keeps improving" with no target, no no-progress bail-out, and no budget.
- **Why bad:** It burns tokens/compute indefinitely and can thrash, undoing its own work.
- **Instead:** Define target, max iterations, and a no-progress-for-K bail (overstack `loop-runner` does this).

### Self-graded success
- **Smell:** The same agent that did the work also declares it done, with no independent check.
- **Why bad:** Confirmation bias rationalizes a wrong result into a "pass"; corrupt success ships.
- **Instead:** Require independent verification — a reviewer agent, a holdout set, or a blind multi-model panel.

### Loop hoarding (no auditor)
- **Smell:** Loops accumulate; none are ever retired even when they stop earning their keep.
- **Why bad:** Stale loops run on autopilot, waste budget, and mask which workflows actually deliver.
- **Instead:** Run a periodic *loop-auditor* that assigns evidence-backed keep / pivot / retire / kill.

## Full index (70 loops, by category)
- **Engineering:** docs sweep · architecture satisfaction · sub-50 ms page-load · production error sweep · 100% test coverage · logging coverage · quality streak · test-suite speed · repository cleanup · stale-safe batch release · ticket-to-PR-ready · Boeing 747 benchmark · War Loops frontend reconstruction · autonomy builder-reviewer · Codex completion-contract · five-minute repo maintainer · propagation compliance · cold-load trimmer · pixel-safe CSS trim · accessibility repair · housekeeper · test stabilizer · error-message rewrite · stable-frame-rate · dependency-CVE burndown · dependency triage · React Doctor repair · React Doctor 100/100 · evidence-first feature · architecture-preserving refactor · restartable handoff · Recovery Proof · Clodex adversarial-review · Loop Harness verification.
- **Operations:** production data cleanup · post-release baseline · customer AI deployment · recent-feedback sweep · promise-to-proof · Goal Forge · prepare-a-new-project · refund follow-up · next-action confidence check · Living Story.
- **Evaluation:** full product evaluation · self-improving champion · devil's-advocate · fresh-clone · multi-LLM convergence · UI/UX score · Axelrod subagent arena · artifact-to-skill · Strip Miner · cross-run playbook · Loop Hiring Manager · loop-auditor · epistemic frontier · research-to-artifact · literature-search verification · Groundtruth.
- **Content:** nightly changelog · product update podcast · Infinite Clickbait thumbnail · talk-to-five-buyers · one-post-a-week · LaTeX document creation · pre-publish source-check.
- **Design:** SEO/GEO visibility · easy onboarding · Revolve versioned-experiment.

## Origin
- Crawled from `https://signals.forwardfuture.com/loop-library/` (Forward Future, 70 loops) via the overstack `/web-crawl` skill test, 2026-06-29. Distilled into the meta-pattern + curated patterns/anti-patterns above; full names indexed verbatim.
