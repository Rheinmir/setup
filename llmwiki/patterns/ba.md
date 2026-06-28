# Business Analyst — Patterns & Anti-patterns

> Protected reference (overstack pattern library). Seeded best-guess — pending curation.

## Patterns

### Spec as Source of Truth (Spec-Driven Development)
- **When:** Any feature whose intent must survive handoff to AI agents or engineers without distortion.
- **Do:** Ground the spec in a `## Context` of evidence first (overstack R7), then make it the tracked source of truth from which plan and tasks derive.
- **Why:** overstack's spec-gate keeps that chain conformant, preventing drift between what was requested, built, and shipped (cf GitHub Spec Kit).

### Given/When/Then Acceptance Criteria
- **When:** Specifying any requirement that someone must later confirm as objectively done or not done.
- **Do:** Express each criterion as Given (context), When (action), Then (observable outcome), so it reads like an executable test.
- **Why:** Concrete, testable conditions close interpretation gaps and let humans and agents agree on what "done" means.

### Thin Vertical Slices
- **When:** A requirement is large, multi-screen, or spans several layers of the stack at once.
- **Do:** Cut work into thin user stories that each deliver end-to-end user value, not horizontal technical layers.
- **Why:** Small shippable slices surface feedback early, shrink risk, and keep each spec independently verifiable.

### Explicit Success Criteria
- **When:** A feature carries a business goal beyond merely "the code runs without error."
- **Do:** State measurable success criteria — the outcome, metric, and threshold that prove the requirement achieved its business goal.
- **Why:** Defined targets convert opinion ("looks fine") into an objective, checkable pass or fail.

### Requirement-to-Test Traceability
- **When:** Always — every requirement should map forward to a verifying test or conformance check.
- **Do:** Give each requirement a stable ID and link it through plan to tasks to its conformance test.
- **Why:** End-to-end traceability proves coverage, exposes orphan requirements, and survives spec-gate's conformance check.

## Anti-patterns

### Vague / Ambiguous Requirements
- **Smell:** Words like "fast," "intuitive," "handle errors gracefully," or "etc." appear with no measurable definition.
- **Why bad:** Each reader fills the gap differently, so the built result rarely matches the intended one.
- **Instead:** Replace adjectives with Given/When/Then criteria and concrete thresholds an agent can actually verify.

### Scope Creep
- **Smell:** New "while we're here" requirements appear after the spec was agreed, without any re-gating.
- **Why bad:** Unbudgeted additions blow estimates, delay the slice, and quietly erode the spec's authority as single source of truth.
- **Instead:** Park new asks as separate specs; change the current one only through an explicit, re-gated revision.

### Gold-plating
- **Smell:** The spec demands edge-case polish, options, or flexibility no user or stakeholder ever requested.
- **Why bad:** Effort flows into unused capability, inflating cost and surface area while real needs still wait.
- **Instead:** Specify only what a stated success criterion requires; defer extras until real evidence demands them.

### Solutioning in the Requirement
- **Smell:** The requirement prescribes tables, endpoints, or libraries instead of the user's need and desired outcome.
- **Why bad:** Premature design constrains engineers, hides the real intent, and persists in the spec even when wrong.
- **Instead:** State the problem, actor, and observable outcome; leave the "how" to plan and tasks.

### Requirement with No Acceptance Test
- **Smell:** A requirement ships with no Given/When/Then, metric, or check that could ever fail it.
- **Why bad:** Untestable requirements cannot be conformance-checked, so "done" turns negotiable and drift goes undetected.
- **Instead:** Pair every requirement with at least one acceptance test before it passes spec-gate.

## Origin
- Seeded from /last30days research (Spec-Driven Development 2026) + overstack spec-gate — 2026-06-29.
