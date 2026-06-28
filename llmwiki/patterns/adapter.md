# Adapter (build-now-adapt-later) — Patterns & Anti-patterns

> Protected reference (overstack pattern library). Seeded best-guess — pending curation.

## Patterns

### One-Config Boundary
- **When:** A feature's logic is certain but some values depend on an unknown — prod, hardware, an undocumented API.
- **Do:** Build the deterministic core plus tests now, and route every unknown-dependent value through a single `harness/<name>.config.yaml`.
- **Why:** Finalizing later costs one file edit instead of rewriting guess-coupled code scattered across the project.

### Verified Flag
- **When:** Shipping a config whose values are best-guesses, not yet confirmed against the real source.
- **Do:** Set `verified: false` and tag each guess with `# ASSUMPTION (source / not verified)` naming where the truth lives.
- **Why:** Uncertainty becomes explicit and machine-checkable, so nobody mistakes an unconfirmed guess for established fact.

### ADAPT-CHECKLIST
- **When:** A `verified: false` adapter ships and someone must finalize it once the real value surfaces.
- **Do:** Embed an `# ADAPT-CHECKLIST` with the exact steps — edit config, run `--self-test`, then flip `verified: true`.
- **Why:** The finalize path is written down, turning adaptation into a short chore rather than a fresh investigation.

### Fail-Safe Default
- **When:** The adapter runs while still `verified: false` and the guessed value may be wrong.
- **Do:** Keep default behavior advisory — warn or log, never block — assuming the guess is wrong until conformance proves otherwise.
- **Why:** A bad guess cannot break production; it only nudges, until verification earns it the right to enforce.

### Mock-Speaks-The-Contract
- **When:** Building and testing the core before the real dependency exists or can be reached.
- **Do:** Make the mock honor the same adapter contract the real source will, so tests assert behavior, not the guess.
- **Why:** Swapping mock for the verified value touches one file; the core and its tests stay untouched.

## Anti-patterns

### Leaked Guess
- **Smell:** The same quarantined constant appears in two or more files; `adapt-registry --check` fails the leak-gate.
- **Why bad:** Finalizing now means hunting every copy, breaking the one-file promise and risking inconsistent values.
- **Instead:** Keep the value only in `harness/<name>.config.yaml` and read it from that single source everywhere.

### Optimistic Default
- **Smell:** A `verified: false` adapter already blocks, rejects, or hard-fails based on an unconfirmed value.
- **Why bad:** A wrong guess takes down real traffic, punishing users for the team's own unresolved uncertainty.
- **Instead:** Default to fail-safe (warn/advisory) and only let the adapter enforce after `verified: true`.

### No Finalize Path
- **Smell:** A `verified: false` adapter ships with no `# ADAPT-CHECKLIST`; the leak-gate fails it.
- **Why bad:** Nobody knows how to confirm the guess, so the temporary quarantine quietly becomes permanent debt.
- **Instead:** Always embed the checklist — edit config, run `--self-test`, flip the flag — before shipping.

### Quarantine-The-Certain
- **Smell:** Deterministic, already-known values get wrapped in an adapter and a `verified` flag anyway.
- **Why bad:** Over-engineering adds config indirection and ceremony where there is no actual unknown to isolate.
- **Instead:** Quarantine only the genuinely unknown; build certain logic plainly in the deterministic core.

### Guess-Presented-As-Verified
- **Smell:** `verified: true` is set without running `--self-test`, or guesses ship with no `# ASSUMPTION` comment.
- **Why bad:** Downstream trusts unconfirmed values as fact, and the fail-safe protections silently switch off.
- **Instead:** Flip `verified: true` only after conformance passes, and annotate every assumption with its real source.

## Origin
- Seeded from overstack's build-now-adapt-later skill + adapt-registry leak-gate — 2026-06-29.
