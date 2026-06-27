---
type: draft
title: Session review 2026-06-27 — harness hardening (R11/R12/R12v3 + reconcile)
status: review
tags: [review, harness, R11, R12, policy, reconcile, output-report]
timestamp: 2026-06-27
---

# Session review — 2026-06-27

Tổng hợp để review đầy đủ. **Mọi thay đổi đã push lên `rheinmir/setup#orca`** (13 commit, `4d61cf4`→`36aa018`). **Full test sweep: 10/10 PASS** (lệnh tái chạy ở cuối).

## 1. Đã làm gì (theo dòng thời gian)

| # | Commit | Nội dung |
|---|--------|----------|
| 1 | `4d61cf4` | **R11** seq-html-glass-style + **R12** pull-before-change (bản đầu, có per-edit) |
| 2 | `188afae` | Rút gọn R12 → (B) orchestrator sweep + (C) pre-push; **bỏ (A) per-edit** |
| 3 | `e699b2d` | Propose **R12 v3** workspace-aware (gate `gate_16a0e503882d` → duyệt) |
| 4 | `076f970` | Impl R12 v3 T1–T5 (sweep nhiều subrepo, --all-subrepos), test 4/4 |
| 5 | `8ef5b2c` | Backfill **rule-registry** + **ADR-001/002** + lấp **decisions.md** |
| 6 | `f329078` | **T1 reconcile** — thêm R3/R4/R8/R10 vào poc policy; R3/R8 KHÔNG drift |
| 7 | `049abd8` | **T5 drift-test** gen-converters↔policy |
| 8 | `47613b5` | **T4 CONTRIBUTING-harness.md** — đóng gap-backfill |
| 9 | `95770ee` | **policy-drives-wiring** — sinh hook claude từ hook_event rules |
| 10 | `99a4b7e` | **R11 [repo]** — migrate 8 seq html flat → glass, bật repo-tier |
| 11 | `d64a747` | **R6**=verify-before-commit + reconcile **2 policy.yaml** |
| 12 | `a1384e4` | Fix 4 broken wikilink (concept stub) |
| 13 | `36aa018` | Fix poc R7 exclude `_template.md` (khớp production) |

## 2. Rule đã thêm/sửa

- **R11 seq-html-glass-style** (`conditional_require`, `[session, repo]`): seq HTML phải glass docs-site-macos. 8 file cũ đã migrate; pre-commit `seq-html-glass`.
- **R12 pull-before-change** (`process_gate`): **(B)** sweep ở orca-workflow Step 0 (vendor-neutral vì orchestrator chạy) · **(C)** git pre-push (vendor-neutral vì git-level). **Bỏ (A)** per-edit. **v3**: `pull-gate-sweep.sh` quét mọi subrepo (manifest `.harness-workspace.yaml` | auto-discover), `install --all-subrepos`.
- **R3/R4/R8/R10** (`hook_event`): đưa vào policy (trước chỉ wire hardcode). **policy-drives-wiring**: gen-converters SINH hook từ field `event/event_action/blocking/matcher/timeout`.
- **R6 verify-before-commit** (`repo_gate`): điều tra ra KHÔNG reserved — là cổng commit, vốn chỉ ở production policy.
- **Reconcile 2 policy**: `harness/policy.yaml` (L0 declaration) ↔ `poc-vendor-neutral/policy.yaml` (executable) giờ cùng **R1–R12**; drift-test gác parity.

## 3. Test chứng minh (10/10)

| Test | Chứng minh |
|------|-----------|
| `policy-converters-drift-test.sh` (38 check) | mọi rule vào adapter; hook_event khớp wiring; **2 policy khớp rule-set**; negative bắt drift |
| `r12-v3-workspace-test.sh` (4/4) | sweep chặn target-behind, bỏ qua watch-behind; --all-subrepos cài pre-push mỗi target |
| `poc test-broad.sh` | bộ test gốc poc vendor-neutral |
| wiki-health `--fail-on broken` | **0 broken wikilink** |
| R11 files-mode mọi `*-seq.html` | 10/10 glass |
| validate mọi wiki `.md` | R2/R5/R7/R9 sạch (gồm _template miễn đúng) |
| py compile + bash -n | mọi script cú pháp hợp lệ |
| pull-gate-sweep | dogfood R12 trên repo thật |

**Negative test đã chạy** (chứng minh test thật sự bắt lỗi): rule chưa-wire→drift FAIL; bỏ R12 khỏi production→parity FAIL; seq flat→R11 block; local-sau-remote→gate2 block. Tất cả restore sạch.

## 4. Tài liệu nên đọc khi review

- [[rule-registry]] — bảng R1..R12 + 2 policy + caveat (đọc đầu tiên).
- [[ADR-001-policy-as-source-of-truth]] · [[ADR-002-pull-before-change-gates]] — *tại sao*.
- `harness/CONTRIBUTING-harness.md` — runbook thêm rule.
- `decisions.md` — nhật ký quyết định phiên.
- [[270626-framework-gap-backfill]] (T1–T5 done) · [[270626-r12-v3-workspace-aware]].

## 5. Caveat / còn mở (trung thực)

- **gate2 chỉ ở repo đã cài hook** (`.git/hooks` không version-controlled) → team cần `install-harness.sh --all-subrepos` / `pre-commit install --hook-type pre-push`.
- **gate1 (B)** chỉ best-effort (orchestrator chạy); không chặn cứng từng edit — cố ý (ADR-002).
- **2 policy khác schema** (list vs dict) — cố ý (declaration vs executable); chỉ rule-id set bị ràng khớp, KHÔNG hợp nhất schema.
- Migrate 8 seq html dùng **override CSS** (non-destructive) — glass-hóa thật nhưng không viết lại từ đầu; bản infographic cũ trông glass-trên-nền-cũ, chấp nhận (historical).
- `~/.claude/` skill đã sync Step 0 cũ; chạy lại sync nếu muốn bản sweep mới nhất.

## 6. Tái chạy để tự verify

```bash
cd <repo>/setup
# full sweep
for t in policy-converters-drift-test r12-v3-workspace-test; do bash harness/tests/$t.sh; done
bash harness/poc-vendor-neutral/test-broad.sh
python3 harness/scripts/wiki-health.py --wiki-dir llmwiki/wiki --fail-on broken
python3 harness/poc-vendor-neutral/bin/llmwiki-validate.py files llmwiki/html/*-seq.html
```

## Origin
- **Session:** 2026-06-27, autonomous run theo yêu cầu user ("chạy tới khi hết việc fix, commit + document, pass phải qua test").
- **Baseline → HEAD:** `0ed66be` → `36aa018` trên `rheinmir/setup#orca`.
- **Liên quan:** [[rule-registry]], [[270626-framework-gap-backfill]], [[270626-r12-v3-workspace-aware]], ADR-001/002.
