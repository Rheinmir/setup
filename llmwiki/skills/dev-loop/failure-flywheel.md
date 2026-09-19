---
name: failure-flywheel
description: Capture each agent failure, bucket and count it deterministically, and when a failure class recurs past a threshold, scaffold a candidate rule/skill stub into the propose->gate flow so the same mistake becomes a guardrail instead of repeating. Hamel's create->label->fix->repeat flywheel, self-evolving. Trigger when the user says "log this failure", "record the mistake", "why does this keep happening", "turn failures into rules", "failure taxonomy", "what keeps breaking", or invokes /failure-flywheel. Also run --report periodically to see the top recurring failure classes.
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: failure-flywheel

Turn recurring failures into rules. Capture by code, count deterministically, draft a stub for a human to approve — never auto-promote.

## WHAT

### Purpose và context
- **Purpose:** biến lỗi lặp lại của agent thành guardrail: ghi lỗi bằng code, đếm tất định theo taxonomy, khi một lớp lỗi vượt ngưỡng thì dựng STUB đề xuất rule/skill vào luồng propose→gate.
- **Trigger (when to use):**
  - A task failed in a way that could recur (invented an API, broke a test, ignored a rule, over-built). Record it so it is counted, not forgotten.
  - Periodically (end of session, or every N failures): `--report` to see which failure class recurs most.
  - When a class crosses the recurrence threshold: `--draft <category>` to seed a candidate rule, then run `/propose` to finish it.
  - User nói "log this failure", "record the mistake", "why does this keep happening", "turn failures into rules", "failure taxonomy", "what keeps breaking", hoặc `/failure-flywheel`.
- **Non-goals:** Do NOT use to auto-write rules. This skill seeds the gate; a human always approves. Không tự chưng cất nội dung rule (10% cần phán đoán thuộc về người + `/propose`).

### Mental model
`failure → record(category) → failures.jsonl → --report (group · COUNT · leaderboard) → lớp ≥ recurrence_threshold → --draft stub → /propose → cổng người duyệt`. Hamel: create → label → fix → repeat. Máy làm 90% cơ học; 10% "rule thực sự là gì" để người.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | `<category>` + `"<summary>"` | có (record) | lớp taxonomy gần nhất; category lạ vẫn ghi, bị gắn cờ ở report |
| In | `--detail "..."` | không | chi tiết thêm |
| In | `--date YYYY-MM-DD` | không (draft) | ISO only, mặc định 2026-06-29; sai định dạng → exit 2 |
| In | `harness/failure-flywheel.config.yaml` | có | ngưỡng + taxonomy (adapter, `verified: false`) |
| Out | dòng trong failures.jsonl | có (record) | lịch sử local, gitignored |
| Out | leaderboard | có (report) | đếm theo lớp, first/last seen, lớp nào `DRAFT` |
| Out | `llmwiki/wiki/sources/draft/DDMMYY-failure-<category>.md` | chỉ khi đủ ngưỡng | STUB (OKF frontmatter + `## Origin`, không `## Plan`) — dừng chờ người |

### Rules và capabilities
- RULE-01 (MUST): Capture is fail-open — recording a failure must never break the session.
- RULE-02 (MUST): Never auto-promote. `--draft` seeds `/propose`; a human approves.
- RULE-03 (MUST): The draft filename date is fixed (`--date`, default 2026-06-29, **ISO `YYYY-MM-DD` only** — not the `DDMMYY` wiki filename convention) for determinism; real use can stamp today. A malformed `--date` now exits 2 with a clear error instead of silently falling back to the default (fixed 2026-07-20 after that exact silent-fallback shipped a wrong-dated draft file).
- RULE-04 (MUST): Do not hard-code the threshold or taxonomy anywhere but the config — that is the adapter.
- Capabilities: ghi append lịch sử lỗi local; đọc config ngưỡng/taxonomy; ghi một file draft stub vào wiki draft. Không mạng, không sửa rule/skill thật.

### Failure boundaries
- Ghi lỗi hỏng → fail-open (session không vỡ), không chặn.
- `--draft` lớp chưa đủ ngưỡng → không viết stub (**blocked** hẹp, báo đếm hiện tại).
- `--date` sai định dạng → **failed** exit 2, thông báo rõ.
- Config còn `verified: false` → stub chỉ có human-TODO, không rule tự viết (**partial** có chủ đích).

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | effect | failure vừa xảy ra | `record <category> "<summary>"` dưới lớp taxonomy gần nhất | dòng jsonl | category lạ → vẫn ghi + cờ ở report |
| W02 | deterministic | failures.jsonl + config | `--report` đọc leaderboard | lớp đánh dấu `DRAFT` nếu ≥ ngưỡng | không lớp nào đủ → dừng |
| W03 | effect | lớp đủ ngưỡng | `--draft <category>` dựng stub | file draft stub | chưa đủ ngưỡng / `--date` sai → dừng |
| W04 | judgment | stub | STOP chờ người; người chạy `/propose` để thành rule/skill có gate | proposal đầy đủ | người từ chối → giữ stub |

Chi tiết từng bước (nguồn chân lý cho W01–W04):

#### The flywheel (Hamel: create -> label -> fix -> repeat)
The slow human step is "notice the same mistake keeps happening and turn it into a rule." This makes the mechanical 90% deterministic (capture + taxonomy + count + scaffold) and refuses to fake the 10% that needs judgement (what the rule actually is).

#### Commands
```bash
# 1. CAPTURE — append one failure (BY CODE; failures.jsonl is gitignored local history)
python3 harness/scripts/failure-flywheel.py record <category> "<summary>" [--detail "..."]

# 2. REPORT — deterministic taxonomy: group by category, COUNT, leaderboard (most-frequent
#    first) + first/last seen + which classes are eligible to draft
python3 harness/scripts/failure-flywheel.py --report

# 3. DRAFT — only if <category> recurs >= recurrence_threshold: scaffold a STUB proposal at
#    llmwiki/wiki/sources/draft/DDMMYY-failure-<category>.md and STOP for human approval
python3 harness/scripts/failure-flywheel.py --draft <category> [--date YYYY-MM-DD]
```

#### Steps
1. On a failure, `record` it under the closest taxonomy category (see the config). Capture never blocks — an unlisted category is still recorded and flagged in `--report`.
2. Run `--report` to read the leaderboard. A class marked `DRAFT` has recurred >= the threshold.
3. For an eligible class, `--draft <category>`. It writes a valid draft STUB (OKF frontmatter + `## Origin`, deliberately no `## Plan` so it passes the R7 gate as a seed) containing a templated "TODO: distill rule from these N failures" + the failure list.
4. The stub STOPS for you. Run `/propose` to turn it into a complete, gated rule/skill. FailureFlywheel never auto-promotes — the gate stays human.

#### The adapter boundary (build-now-adapt-later)
Everything above is deterministic and built now. The ONE quarantined unknown is `harness/failure-flywheel.config.yaml` (`verified: false`): the recurrence threshold and taxonomy are best-guesses, and the "distill failures -> rule" model is absent. While it is unset, `--draft` inserts a human-TODO stub instead of an auto-written rule. Finalize later by editing only that one file — calibrate the threshold, name a distill model, flip `verified: true`.


### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | lớp lỗi ≥ `recurrence_threshold` | W03 `--draft` rồi W04 | dưới ngưỡng → skip, chỉ report | W04 |
| B02 | capability_optional | config `verified: true` + có distill model | stub có rule tự chưng cất thay vì human-TODO | chưa verified → human-TODO stub (mặc định hiện tại) | W04 |

### Validation và stopping
Đếm và ngưỡng do `failure-flywheel.py` quyết (tất định). Stub hợp lệ = OKF frontmatter + `## Origin`, cố ý không `## Plan` để qua cổng R7 như hạt giống. Luôn dừng ở W04 — không bao giờ tự promote.

### Examples
- **Positive:** agent bịa API lần thứ N (vượt ngưỡng) → `python3 harness/scripts/failure-flywheel.py record invented-api "called nonexistent fetchAll()"` → `--report` hiện `invented-api` đánh dấu `DRAFT` → `--draft invented-api` viết `llmwiki/wiki/sources/draft/DDMMYY-failure-invented-api.md` và dừng chờ `/propose`.
- **Boundary/failure:** `--draft invented-api --date 19/09/2026` → exit 2 kèm lỗi rõ ràng, không viết file ngày sai.

### Related
- `harness/scripts/code-logger.py` — same by-code, gitignored-JSONL, fail-open capture pattern.
- `llmwiki/skills/dev-loop/propose.md` — the gate this feeds.
- `llmwiki/skills/dev-loop/build-now-adapt-later.md` — the quarantine pattern the config follows.
