---
name: build-now-adapt-later
description: When a task is blocked by missing or unverified information (an undocumented protocol, an unknown API shape, a value only real hardware/prod can confirm), build everything that does NOT depend on the unknown right now, and quarantine the unknown behind a single adapter boundary — best-guess defaults + a verified flag + a conformance/adapt kit — so adapting later means editing one file, not rewriting the project. Trigger when the user says "làm những gì có thể trước", "build what we can now", "wrap the unknowns", "isolate/quarantine the unknown parts", "don't block on missing info", "adapter so we can swap later", "ready to adapt", or invokes /build-now-adapt-later. Also applies whenever a spec has ⚠️ "to be verified" items but most of the work doesn't actually depend on them.
---

# Skill: build-now-adapt-later

Ship the certain part now; isolate the uncertain part so it costs one file to finalize later.

## When to use
A task contains some facts you cannot pin down yet (undocumented byte layout, unconfirmed
port/endian, an external API you can't call yet, a value only real hardware or production
reveals) — BUT most of the work doesn't truly depend on those facts. Don't stall the whole
project waiting, and don't scatter guessed values across the codebase. Draw one boundary.

Do NOT use when the unknown is the whole task (e.g. "we don't know what to build"), or when
the unknown is cheap to resolve right now (then just resolve it).

## Core principle
> Everything that depends on a stable **domain contract** is built and tested now.
> Everything that depends on an **unknown** lives behind one adapter, defaulted to a
> documented best-guess, flagged `verified:false`, and swappable in a single edit.

## Steps

1. **Enumerate the unknowns.** List every fact you don't have or can't verify. Tag each ⚠️ and
   note its source-of-truth (real hardware, prod data, a doc you lack, a stakeholder decision).
   If a "fact" can be looked up cheaply now — look it up; it's not an unknown.

2. **Define the stable boundary (the contract).** Write the domain-level interface that
   everything else speaks — types / function signatures / message schema that describe *intent*,
   not the unknown encoding. Rule: the contract must NOT contain any ⚠️ value. (e.g. a
   `SemanticCommand`/`Telemetry` model, not byte offsets; a `PaymentRequest`, not the gateway's
   wire format.)

3. **Quarantine the unknowns.** Put EVERY unknown-dependent constant in ONE config file and
   EVERY unknown-dependent logic in ONE adapter module behind the contract. Seed each with a
   best-guess default from whatever doc you have, mark each `// ASSUMPTION (source / not verified)`,
   and add an explicit `verified: false` flag. The adapter is the only thing that knows the unknown.

4. **Build everything above the boundary — fully.** UI, business logic, transport, safety/error
   handling, validation: all written against the contract, complete and tested. They never import
   a quarantined value.

5. **Build a mock/stub that speaks the same contract.** It lets the whole system run end-to-end
   *today* without the real unknown. Make the mock honor the same adapter/config so it doubles as
   the conformance harness later.

6. **Ship the Adapt-kit.** Produce (a) a short `ADAPT-CHECKLIST` — the exact steps to finalize once
   the unknown is known (edit config → edit adapter → run conformance → flip `verified:true`), and
   (b) conformance tests / vectors that must pass before the guessed values are trusted in
   production / against real hardware.

7. **Guard the boundary.** Add a lint rule or review note: quarantined values must not leak past
   the adapter. If a guessed constant appears in two places, the isolation is already broken — fix
   it before moving on.

## Rules
- The adapter + its config are the ONLY places an unknown lives. Same guess in two files = a leak.
- Every guess is flagged AND sourced. NEVER present a guess as verified, in code or in prose.
- Default behavior under `verified:false` must be **fail-safe**, not optimistic — assume the guess
  is wrong until conformance proves otherwise (especially for anything physical, financial, or destructive).
- Quarantine only what is genuinely unknown. Don't abstract certain things "just in case" — that's
  over-engineering, not isolation.
- The contract is the deliverable downstream work depends on. Keep it stable; widen it deliberately,
  not per-guess.
- State plainly in your handoff: what was built and verified, what is guessed and pending, and the
  one-file path to finalize each ⚠️.

## Quick template (adapt to the stack)
```
contract/         # stable domain types — NO unknown values        (built now, tested now)
  └ model.*       #   intent-level: commands, telemetry, requests
core/             # UI / logic / transport / safety on the contract (built now, tested now)
adapter/
  ├ config.*      # ⚠️ ALL unknown constants + verified:false       (quarantine)
  └ codec.*       # ⚠️ encode/decode against the unknown            (quarantine, swap 1 file)
mock/             # speaks the same adapter → E2E offline + conformance harness
ADAPT-CHECKLIST.* # 5-step finalize procedure when the unknown is known
conformance.*     # vectors that gate verified:true
```

## Worked example (where this was distilled from)
lite3-controller-ui: the MotionSDK protocol (command codes, byte offsets, endian, ports) was
unverified vs real hardware. The contract = `SemanticCommand`/`Telemetry`; the quarantine =
`protocol.config` + `motionsdk-codec`; UI/WS/bridge/safety built fully on the contract; a UDP
mock host gave full E2E offline; an Adapt-kit (checklist + conformance vectors) made finalizing
the protocol a one-file edit. See `llmwiki/wiki/draft/orca/150626-lite3-adapter-isolation.md`.

---

## Output Report (only if the project has an `llmwiki/`)

After the work completes, write a draft report so the decision is traceable.

**1. Filename:** `llmwiki/wiki/draft/orca/DDMMYY-<ten>.md` — `DDMMYY` = today, `<ten>` = 2–4 kebab words.

**2. Write:**
```
# DDMMYY-<ten>
**Type:** draft
**Status:** proposed
**Tags:** build-now-adapt-later, output-report
**Proposed:** YYYY-MM-DD

## What
<One sentence — what was built now vs what was quarantined>

## Boundary
- Contract: <the stable domain types/interface>
- Quarantine: <config + adapter files holding the ⚠️ unknowns>

## Unknowns (⚠️) pending verification
| Unknown | Best-guess source | Finalize by |
|---------|-------------------|-------------|

## Files
| File | Action |
|------|--------|

## Notes
- Invoked via: `/build-now-adapt-later` skill

## Origin
- **Draft:** `wiki/draft/orca/DDMMYY-<ten>.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
```

**3.** Append a row to `llmwiki/wiki/index.md` and a line to `llmwiki/wiki/log.md`.
