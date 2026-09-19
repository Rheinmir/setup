---
name: verify-before-commit
description: Gate every commit — typecheck, lint, smoke, then promote draft to wiki
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: verify-before-commit

## WHAT

### Purpose và context
- **Purpose:** gate every commit — typecheck, lint, test, smoke trước commit; sau commit promote draft lên wiki và đóng vòng đời task.
- **Trigger (when to use):** After any impl task, before `git commit`.
- **Non-goals:** không viết tính năng mới, không bỏ qua bước nào vì "thay đổi nhỏ", không tự đổi state-machine task ngoài lệnh `code-logger.py` đã khai.

### Mental model
`diff → typecheck → lint → test → qc-regression → task_lifecycle gate → smoke → commit (why) → promote draft (+ ## Origin) → log + index → task state=done`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | thay đổi code đã impl | có | đối tượng gate |
| In | draft khớp feature trong `llmwiki/wiki/sources/draft/` | không | không có (hotfix/refactor) → ghi "no draft — <reason>" vào log |
| In | `task: T-…` trong frontmatter draft | không | không có → skip step 8 (fail-open) |
| Out | commit | có | message nói *why*, không *what* |
| Out | trang wiki đã promote có `## Origin` | khi có draft | `concepts/` hoặc `sources/` |
| Out | `llmwiki/wiki/log.md` + `index.md` | có | cập nhật |

### Rules và capabilities
- RULE-01 (MUST): All steps mandatory. No exceptions.
- RULE-02 (MUST): Post-commit — mandatory, never skip.
- Capabilities: chạy typecheck/lint/test/smoke của repo (tự dò theo manifest); chạy validator harness nếu có; ghi git commit + wiki + log vòng đời task.

### Failure boundaries
- Typecheck/lint/test đỏ → **blocked**: fix rồi chạy lại, không commit.
- `qc-regression.py --run` đỏ → **blocked** (bug đã fix tái phát hoặc chưa fix); chưa có test `qc-*` → fail-open, không chặn.
- `task_lifecycle.py` chặn (task-ID sai state-machine) → **blocked**; không có file (install cũ) → bỏ qua.
- Không có draft → không promote, ghi lý do vào log (**succeeded** hẹp). Không có `task:` id → skip step 8, không phải lỗi.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | repo | Type-check (dò lệnh theo repo) | rc 0 | lỗi → fix, lặp |
| W02 | deterministic | repo | Lint | rc 0, ghi chú warning | lỗi → fix, lặp |
| W03 | deterministic | repo | Test + test tái hiện qc-code (3b, nếu có harness) | rc 0 | fail → fix, lặp |
| W04 | deterministic | draft/task | Trụ 3 gate `task_lifecycle.py` (nếu có harness) | rc 0 | chặn → blocked |
| W05 | judgment | app | Smoke check golden path end-to-end | golden path chạy | hỏng → fix |
| W06 | effect | diff | Commit, message *why* | commit hash | — |
| W07 | effect | draft | Promote draft + `## Origin` + log + index | trang wiki | không draft → B01 |
| W08 | effect | `task:` id | Đóng vòng đời task qua `code-logger.py` (best-effort) | state=done | không id → B02 |

Chi tiết từng bước (nguồn chân lý cho W01–W08; W01–W03 = bước 1–3b, W04 = 4, W05 = 5, W06 = 6 pre-commit, W07 = 6–7 post-commit, W08 = 8):

**Pre-commit:**
1. `RUN: <type-check-cmd>` — detect from repo: `npx tsc --noEmit` (package.json) / `go build ./...` (go.mod). Fix all errors.
2. `RUN: <lint-cmd>` — detect: `npx eslint src/` / `go vet ./...`. Fix errors; note warnings.
3. `RUN: <test-cmd>` — detect: `npm test` / `go test ./...`. Fix failures.
3b. **Test tái hiện qc-code (nếu có harness):** `RUN: [ -f harness/scripts/qc-regression.py ] && python3 harness/scripts/qc-regression.py --run` — chạy các test `qc-*` do `/qc-code` sinh (tái hiện bug đã tìm). ĐỎ = một bug đã fix nay tái phát, hoặc chưa fix. Tất định, 0-token, KHÔNG gọi LLM. Fail-open nếu chưa có test `qc-*` nào (dự án chưa dùng qc-code) — không chặn.
4. **Trụ 3 gate (nếu có harness):** `RUN: [ -f harness/validators/task_lifecycle.py ] && python3 harness/validators/task_lifecycle.py --root .` — chặn cứng nếu task-ID đi sai state-machine (lùi/nhảy/né gate) hoặc draft trỏ task lạ. Không có file (install cũ) → bỏ qua. Đây là bản CỨNG của step 8 best-effort bên dưới.
5. Smoke check: verify golden path end-to-end.
6. Commit with message: *why*, not *what*.

**Post-commit — mandatory, never skip:**
6. Find draft in `llmwiki/wiki/sources/draft/` matching feature.
   - Promote to `llmwiki/wiki/concepts/` or `llmwiki/wiki/sources/` (permanent).
   - Add `## Origin` section: `Draft: <path>` / `Commit: <hash> — <msg>` / `Date: YYYY-MM-DD`
   - `CHECK: grep -l "## Origin" <promoted-file>` — must return file.
7. `RUN: echo "promoted" >> llmwiki/wiki/log.md` — then edit log properly; update `llmwiki/wiki/index.md`.
8. **Trụ 3 — đóng vòng đời (best-effort, fail-open):** draft có frontmatter `task: T-…` → `python3 harness/scripts/code-logger.py --task set <T-id> state=done note="<commit-hash>"`. Lệnh fail-open (thiếu `--task`/id → bỏ qua, không chặn commit). Xác nhận: `--task show <T-id>` in lifecycle proposed→approved→dispatched→done; `--audit` xác minh các transition nằm trong chuỗi bất biến.

> No draft (hotfix/refactor)? Note "no draft — <reason>" in log.md, skip step 6.
> No `task:` id (install cũ / propose bỏ qua mint)? Skip step 8 — fail-open, không phải lỗi.

All steps mandatory. No exceptions.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | không có draft (hotfix/refactor) | ghi "no draft — <reason>" vào `log.md`, skip step 6 post-commit | — | W08 |
| B02 | conditional_required | draft không có `task:` id (install cũ / propose bỏ qua mint) | skip step 8 — fail-open | — | kết thúc |
| B03 | capability_optional | có `harness/` (qc-regression, task_lifecycle, code-logger) | chạy 3b, 4, 8 | thiếu file → bỏ qua, fail-open | bước kế |

### Validation và stopping
Tất định: rc của typecheck/lint/test/qc-regression/task_lifecycle; `CHECK: grep -l "## Origin" <promoted-file>` phải trả file; `--task show <T-id>` + `--audit` xác nhận lifecycle. Cần review: smoke golden path. Dừng khi mọi bước pre + post xong; đỏ ở pre-commit thì không commit.

### Examples
- **Positive:** repo có `package.json` → `npx tsc --noEmit`, `npx eslint src/`, `npm test` xanh, `qc-regression.py --run` xanh → commit "why" → promote draft `DDMMYY-login-otp.md` vào `wiki/concepts/` có `## Origin` → `code-logger.py --task set T-12 state=done note="<hash>"`.
- **Boundary/failure:** `go test ./...` fail 1 test → dừng ở W03, fix rồi chạy lại, chưa commit. Hotfix không có draft → log "no draft — hotfix typo", skip promote.

### Delivery — Output Report

After all main skill tasks complete, write a propose draft to the wiki.

#### Steps

**1. Build the filename:**
- Format: `DDMMYY-<ten>.md`
- `DDMMYY` = today (e.g., `020626` for 2 June 2026)
- `<ten>` = 2–4 kebab-case words summarising what was done (e.g., `landing-page-coteccons`, `brand-kit-fintech`, `ingest-auth-spec`)

**2. Write** `llmwiki/wiki/sources/draft/DDMMYY-<ten>.md`:

```
---
type: draft
title: "DDMMYY-<ten>"
status: proposed
tags: [<skill-name>, output-report]
timestamp: YYYY-MM-DD
---

# DDMMYY-<ten>
**Type:** draft
**Status:** proposed
**Tags:** <skill-name>, output-report
**Proposed:** YYYY-MM-DD

## What
<One sentence — what this skill invocation produced or decided>

## Output
<Key artefacts, files created/modified, or decisions made>

## Files
| File | Action |
|------|--------|
| `path/to/file` | created / modified |

## Notes
- Invoked via: `/<skill-name>` skill

## Origin
- **Draft:** `wiki/sources/draft/DDMMYY-<ten>.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
```

**3. Update wiki index & log:**
- `llmwiki/wiki/index.md` — append one row: `| [DDMMYY-<ten>](sources/draft/DDMMYY-<ten>.md) | draft | YYYY-MM-DD |`
- `llmwiki/wiki/log.md` — append: `## YYYY-MM-DD — <skill-name> — <ten>`

> Skip only when the skill produces zero artefacts and zero decisions (e.g., a pure display mode like `/caveman-stats`).
