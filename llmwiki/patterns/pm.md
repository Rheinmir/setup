# Product Manager — Patterns & Anti-patterns

> Protected reference (overstack pattern library). Seeded best-guess — pending curation.

## Patterns

### Thinnest Valuable Slice
- **When:** Starting a new bet whose user demand is still an unproven hypothesis.
- **Do:** Ship the smallest end-to-end increment that delivers real value, not a prototype or a half-wired feature.
- **Why:** You validate the value hypothesis with real usage before committing the full build budget.

### Outcome Over Output
- **When:** Framing any roadmap item, quarterly goal, or definition of success.
- **Do:** State the target change in user behavior or business metric, validated through continuous discovery, then let the team pick the solution.
- **Why:** The team stays accountable for solving the problem, not for shipping a predetermined feature.

### Paired Success + Guardrail Metrics
- **When:** Before launching any experiment, release, or pricing change.
- **Do:** Name the one metric you intend to move and the guardrail metrics — retention, latency, support load — you must not harm.
- **Why:** It blocks a local win that quietly erodes trust, retention, or cost.

### Pre-Mortem with Kill Criteria
- **When:** Committing to any multi-week bet or expensive build.
- **Do:** Before starting, write down the evidence that would make you stop and the date you will check it.
- **Why:** Killing a loser becomes a pre-agreed decision, not a painful argument after sunk cost piles up.

### Build-Now-Adapt-Later Sequencing
- **When:** A spec mixes certain requirements with unknowns like pricing, an unverified integration, or real-world data.
- **Do:** Ship the certain part now and quarantine each unknown behind a flag with a best-guess default, per overstack build-now-adapt-later.
- **Why:** You deliver value this week, and the later swap edits one file instead of the whole project.

## Anti-patterns

### Feature Factory
- **Smell:** The roadmap is a list of features with ship dates but no stated user outcome.
- **Why bad:** Teams celebrate shipping velocity while real user and business outcomes stay flat.
- **Instead:** Tie every item to an outcome metric, and cut anything that cannot name the behavior it changes.

### Vanity Metrics
- **Smell:** Reports show totals that only ever rise — pageviews, signups, cumulative users — with no denominator.
- **Why bad:** The number looks like progress while activation, retention, or revenue may be flat or falling.
- **Instead:** Track rates and cohorts paired with guardrails, and report the metric that is allowed to go down.

### Sunk-Cost Roadmap
- **Smell:** "We have already built half of it" keeps a feature alive, and no kill criteria were ever set.
- **Why bad:** Unrecoverable past spend, not future value, drives the decision toward something evidence says will not pay off.
- **Instead:** Decide on expected future value alone, and let pre-set kill criteria override what you already spent.

### HiPPO Decisions
- **Smell:** Priorities reorder to match the most senior person in the room rather than evidence from users or data.
- **Why bad:** Discovery and metrics get overridden, the team disengages, and the same misjudgments keep recurring.
- **Instead:** Bring evidence to every call, and log recurring overrides so overstack's failure-flywheel turns them into a rule.

### Building for Imagined Scale
- **Smell:** The team builds sharding, multi-tenancy, or config frameworks for users and load that do not yet exist.
- **Why bad:** You burn the budget on hypothetical futures while the real, current value hypothesis stays untested.
- **Instead:** Ship the thin slice for today's load and defer scale behind a flag, per build-now-adapt-later.

## Origin
- Seeded from /last30days research (product management 2026) + overstack build-now-adapt-later / failure-flywheel — 2026-06-29.
