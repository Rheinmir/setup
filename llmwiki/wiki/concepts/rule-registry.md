---
type: concept
title: Rule Registry — R1..R12 canonical
status: active
tags: [harness, policy, rules, registry, R11, R12, drift]
timestamp: 2026-06-27
---

# Rule Registry — R1..R12

> Lối vào tổng cho phát triển framework: [[fdk]]. Trang này là phần "danh sách rule" của bộ xương đó.

Một trang đọc-là-đủ. Nguồn chân lý máy-đọc là `harness/poc-vendor-neutral/policy.yaml`; nhưng một số luật được wire ở `gen-converters.py` (hook) → `harness-events.py`, KHÔNG nằm trong policy.yaml. Bảng này hợp nhất và **đánh dấu chỗ lệch**.

| ID | Tên | Cơ chế / file | Điểm enforce | enforce_at | Status |
|----|-----|---------------|--------------|------------|--------|
| **R1** | no-write-raw | `deny_write` · `validators/no_write_raw.py` | PreToolUse + pre-commit | session, repo | active |
| **R2** | origin-required | `require_section` · `validators/origin_required.py` | PreToolUse(claude-hook) + pre-commit | session, repo | active |
| **R3** | index-sync | `hook_event` (policy) · `index_sync.py` | Stop hook + pre-commit | session, repo | active |
| **R4** | audit-log | `hook_event` (policy) · `harness-events.py audit` · PostToolUse | session | session | active |
| **R5** | folder-structure | `forbid_root` · `validators/folder_structure.py` | PreToolUse + pre-commit | session, repo | active |
| **R6** | verify-before-commit | `repo_gate` · pre-commit framework + CI + skill `/verify-before-commit` | cổng commit | repo | active |
| **R7** | proposal-complete | `conditional_require` · `validators/proposal_complete.py` | PreToolUse + pre-commit | session, repo | active |
| **R8** | session-health | `hook_event` (policy) · `harness-events.py session` · `session_start.py` | SessionStart | session | active |
| **R9** | okf-frontmatter | `require_frontmatter` · `validators/okf_frontmatter.py` | PreToolUse + pre-commit | session, repo | active |
| **R10** | docs-gate | `hook_event` (policy) · `harness-events.py docs` · UserPromptSubmit | session (report, không chặn) | session | active |
| **R11** | seq-html-glass-style | `conditional_require` · **policy.yaml** | session (write seq html) | session | active |
| **R12** | pull-before-change | `process_gate` · **policy.yaml** | (B) workflow Step 0 sweep · (C) git `pre-push` | session, repo | active |

## R11 — chi tiết
Seq diagram HTML (`*-seq.html`) phải theo style `docs-site-macos` liquid-glass (marker: `backdrop-filter` + `linear-gradient(180deg,#f7fbff…` + edge-highlight). Chặn theme flat tự chế lúc write. enforce_at `[session]` — KHÔNG `[repo]` để không fail ~8 seq html cũ (bật repo sau khi migrate). Xem [[270626-framework-gap-backfill]].

## R12 — chi tiết (gồm v3 workspace-aware)
- **(B) pre-work sweep** — orchestrator chạy `pull-gate-sweep.sh` ở **workflow Step 0** TRƯỚC fan-out: quét MỌI subrepo (manifest `.harness-workspace.yaml` | auto-discover harnessed), chặn nếu subrepo **target** sau remote (watch chỉ cảnh báo). Single-repo → rút về `pull-gate.sh`.
- **(C) pre-push** — git hook per-repo (`.git/hooks/pre-push` + `.pre-commit` stage), **vendor-neutral** (mọi `git push` đều dính). Nhân ra mọi subrepo bằng `install-harness.sh --all-subrepos`.
- **ĐÃ BỎ (A)** per-edit PreToolUse: cost cao, lệch đa-vendor, (B) đã phủ. Xem [[ADR-002-pull-before-change-gates]].

## Tình trạng reconcile (T1 — 2026-06-27)
- ✅ **policy.yaml giờ liệt kê ĐỦ** R1–R5, R7–R12 (thêm R3/R4/R8/R10 dạng `kind: hook_event`, documentary). "Nguồn chân lý" hết rò ở mức **liệt kê**.
- ✅ **R3/R8 KHÔNG mâu thuẫn** — điều tra `harness-events.py` + `stop.py` + `index_sync.py` cho thấy: **R3 = index-sync** (nhất quán Stop + pre-commit), **R8 = session-health** (riêng). Flag "drift" cũ là **quá thận trọng → đã gỡ**.
- ✅ **Policy-drives-wiring (2026-06-27)**: `gen-converters.py` giờ **SINH** hook claude (Stop/PostToolUse/SessionStart/UserPromptSubmit) TỪ `hook_event` rules (`event`/`event_action`/`blocking`/`matcher`/`timeout`) — không còn hardcode. Output verify **IDENTICAL** bản cũ; drift-test 36/0 + assert `event_action` + lệnh chứa action. Policy là nguồn DUY NHẤT cho cả **semantics lẫn wiring**. (PreToolUse = content-gate gộp nhiều rule, giữ hardcode — không thuộc 1 hook_event.)
- ✅ **R6 = verify-before-commit** (2026-06-27) — KHÔNG reserved. Vốn chỉ khai ở `harness/policy.yaml` (L0 production), nay thêm vào PoC (`kind: repo_gate`). Enforce = chính pre-commit framework + CI + skill.

## Hai file policy.yaml (đừng nhầm)
- **`harness/policy.yaml`** — L0 **production**, schema **list**, validator-per-id ở `harness/validators/`. File khai báo (chỉ install-harness *copy*, không code nào parse). Nay liệt kê **R1–R12**.
- **`harness/poc-vendor-neutral/policy.yaml`** — **PoC vendor-neutral**, schema **dict**, là file `gen-converters.py` + `llmwiki-validate.py` THỰC SỰ đọc. Nay cũng **R1–R12**.
- Hai file phục vụ vai trò khác nhau (declaration vs executable demo) nhưng **rule-id set phải khớp** — `policy-converters-drift-test.sh` assert điều này (check 0). Trước 2026-06-27 chúng lệch (prod có R6 thiếu R11/R12; poc ngược lại) → đã reconcile.

## Origin
- **Source:** đọc trực tiếp `harness/poc-vendor-neutral/policy.yaml`, `harness/validators/*.py`, `harness/poc-vendor-neutral/gen-converters.py`, `.pre-commit-config.yaml`, `concepts/R10.md` (baseline `188afae`→`076f970`).
- **Backfill request:** user — "backfill R11/R12/R12v3 vào rule-registry + ADR". Tiền lệ [[270626-framework-gap-backfill]], [[270626-r12-v3-workspace-aware]].
