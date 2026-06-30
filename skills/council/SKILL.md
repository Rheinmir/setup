---
name: council
description: >-
  Run a Karpathy-style LLM council (3-stage multi-agent evaluation) on top of
  the existing orca orchestration: N seats independently answer a question, the
  answers are BLIND peer-ranked (identities stripped so a model can't favour its
  own), and a chairman synthesizes the final answer. The orchestration makes the
  model calls; harness/scripts/council.py does the deterministic protocol math
  (anonymization, mean-rank aggregation, dissent, anchor guard, transcript). Use
  when the user says "run a council", "llm-council", "panel of models", "blind
  peer-rank these answers", "ensemble + chairman", or invokes /council.
---

# Skill: council

> 🧭 Chọn backend cho mỗi seat (model rẻ vs Claude), chạy nhiều seat song song (1 worktree/seat — KHÔNG nhiều opencode/1 folder) → xem **orca-dispatch-reference** (nguồn chân lý duy nhất).

A deterministic harness around Andrej Karpathy's `llm-council`
(https://github.com/karpathy/llm-council) three stages — Stage 1 "First
Opinions", Stage 2 "Review" (anonymized peer-rank), Stage 3 "Final Response"
(chairman) — wired onto orca orchestration.

Split of labour:

- **`harness/scripts/council.py`** owns the DETERMINISTIC protocol and never
  calls a model: anonymize (strip author → A/B/C by stable sha256 order),
  mean-rank aggregation, dissent surfacing, the anchor guard (seed-driven,
  per-judge presentation order — no `Math.random`), and the json+md transcript.
- **The orca orchestration** owns the MODEL GENERATIONS: each seat's answer,
  each judge's ranking, the chairman's synthesis. It dispatches them exactly
  like any other multi-agent wave (see `orca-workflow`, `orchestration`).
- **`harness/council.config.yaml`** is the ONE adapter (`verified: false`): which
  model fills each seat, the judge models, the chairman. Every value is an
  `# ASSUMPTION (not verified)`. The engine never branches on these — it only
  stamps them into the transcript. Finalize the council by editing this one file.

## When to use

Hard questions where one model's answer is risky and you want a panel + an
audit trail of who-ranked-what, with the favour-your-own bias removed by
blinding. For a single quick answer, just ask one model.

## Persona lenses — góc nhìn "vĩ nhân" (optional, ADDITIVE)

Mặc định mỗi seat = một MODEL trả lời. Lớp persona thêm **đa-dạng GÓC NHÌN**: mỗi seat đội một
**lens** (Feynman / Munger / Taleb / Rams …) — quan trọng khi đa-dạng-model bị hạn chế (chỉ có ít
provider). Engine `council.py` KHÔNG đổi: persona chỉ là chữ nhét vào prompt Stage-1.

**Bốc 3-5 người theo case (thuần code, log-được):**
```bash
python3 harness/scripts/council.py roster --case risk            # 3 ghế, có ≥1 cặp đối-trọng
python3 harness/scripts/council.py roster --case ml-ai --size 5  # 5 ghế
python3 harness/scripts/council.py roster --profile lean         # 5 người execution-lean
python3 harness/scripts/council.py roster --personas feynman,taleb,rams --json
```
- Case tag: `design · strategy · debug · risk · product · decision · simplify · ml-ai` (bảng trong `harness/council.personas.yaml`).
- **Luật:** roster luôn cài **≥1 cặp đối-trọng** (chống phòng vọng âm); thiếu → cảnh báo ở stderr. Size lẻ (3/5) để mean-rank không hoà.
- Thư viện: 18 persona + 13 cặp đối-trọng (nguồn `github.com/0xNyk/council-of-high-intelligence`).

**Dùng trong protocol:** sau khi bốc roster, gán mỗi persona vào một seat — có 2 cách:
1. **Động (khuyên):** orchestrator lấy output `roster --json`, với mỗi seat chèn lens vào prompt Stage-1: *"Trả lời qua lăng kính \<name>: \<lens>. \<sig>."*
2. **Cố định:** điền field `persona:` mỗi seat trong `harness/council.config.yaml`.

Roster + lý do bốc (case, cặp tension) **ghi vào transcript** để auditable (Trụ 5). Phần "model nào fill seat" vẫn là unknown đã quarantine ở `council.config.yaml` (`verified`) — persona-lens độc lập với nó.

## Preconditions

- `python3 harness/scripts/council.py selftest` exits 0 (engine is healthy).
- `orca status --json` shows a running runtime; orchestration enabled.
- Seats/judges/chairman set in `harness/council.config.yaml`.

## Protocol (maps each stage to an orca dispatch)

### Stage 1 — First Opinions (orchestration generates)
Dispatch one worker per seat in `council.config.yaml`, same question to each:

```bash
orca orchestration task-create --spec "Answer: <question>" --json
orca orchestration dispatch --task <task_id> --to <seat_handle> --inject --json
orca orchestration check --wait --types worker_done --timeout-ms 300000 --json
```

Collect the replies into `answers.json` — `[{"id","author","text"}, ...]`, where
`author` is the seat id (the real identity; it gets stripped next).

### Stage 2a — blind packet (council.py is deterministic)
```bash
python3 harness/scripts/council.py prepare answers.json --config harness/council.config.yaml --out run/
```
Writes `run/council.packet.{json,md}`: the answers relabelled A/B/C with authors
removed, plus each judge's **presentation order** from the anchor guard. Show
each judge its answers in its row's order to cancel position bias.

### Stage 2b — Review (orchestration generates)
Dispatch each judge in `council.config.yaml` the BLIND answers, in that judge's
presentation order. Ask each to return a ranking of the **labels** (best first).
Collect into `judges.json` — `[{"judge","ranking":["B","A","C"]}, ...]`.

> Blindness, not exclusion, is the guard: a judge may be a seat, but it cannot
> recognise its own answer, so it cannot play favourites.

### Stage 2c — aggregate (council.py is deterministic)
```bash
python3 harness/scripts/council.py rank answers.json --judges judges.json --config harness/council.config.yaml --out run/
```
Writes `run/council.transcript.{json,md}`: mean-rank consensus, the winner, the
dissent table (most-contested answer), and a `chairman_brief`.

### Stage 3 — Final Response (orchestration generates)
Dispatch the chairman the `chairman_brief` from the transcript (consensus order +
the dissent points it must resolve). Its synthesis is the final answer; paste it
back under `chairman_synthesis` in the transcript for the record.

## council.py commands

| Command | Does |
|---------|------|
| `rank <answers.json> --judges <judges.json>` | full aggregation → transcript.json + .md |
| `rank <answers.json>` (no judges) | emits the blind packet, then stops |
| `prepare <answers.json>` | blind packet only (Stage 2a) |
| `roster --case <tag>` / `--profile <p>` / `--personas a,b,c` | bốc 3-5 persona-lens (thuần lookup, ≥1 cặp đối-trọng); `--size 3\|5`, `--json` |
| `selftest` | conformance vectors; asserts determinism + correctness |

Flags: `--seed N` (anchor-guard seed; overrides config `anchor_seed`),
`--out DIR`, `--config harness/council.config.yaml`.

## Adapter boundary (build-now-adapt-later)

- **Contract (built + tested now):** the json schemas (`answers.json`,
  `judges.json`, transcript) and all the deterministic ops in `council.py`.
- **Quarantine (`verified: false`):** model identities in
  `harness/council.config.yaml`. The math is independent of them.
- **Adapt later (one file):** edit seats/judges/chairman in the config, run a
  real council, then flip `verified: true`. No engine change.

## Determinism guarantees

Same `answers.json` + `judges.json` + seed → byte-identical transcript every
run. Anonymization depends on `sha256(id)`, not input order or author, so neither
position nor authorship leaks. The anchor guard is seeded per judge from the
arg — never the global RNG. `selftest` proves all of this (12 checks).
