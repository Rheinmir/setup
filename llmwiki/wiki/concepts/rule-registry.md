---
type: concept
title: Rule Registry — R1..R12 canonical
status: active
tags: [harness, policy, rules, registry, R11, R12, drift]
timestamp: 2026-06-27
---

# Rule Registry — R1..R12

Một trang đọc-là-đủ. Nguồn chân lý máy-đọc là `harness/poc-vendor-neutral/policy.yaml`; nhưng một số luật được wire ở `gen-converters.py` (hook) → `harness-events.py`, KHÔNG nằm trong policy.yaml. Bảng này hợp nhất và **đánh dấu chỗ lệch**.

| ID | Tên | Cơ chế / file | Điểm enforce | enforce_at | Status |
|----|-----|---------------|--------------|------------|--------|
| **R1** | no-write-raw | `deny_write` · `validators/no_write_raw.py` | PreToolUse + pre-commit | session, repo | active |
| **R2** | origin-required | `require_section` · `validators/origin_required.py` | PreToolUse(claude-hook) + pre-commit | session, repo | active |
| **R3** | ⚠️ DRIFT | pre-commit gán `index_sync.py`="R3"; `gen-converters` gán **Stop hook**="R3" | mâu thuẫn 2 file | — | **needs-reconcile** |
| **R4** | audit | `harness-events.py audit` · PostToolUse | session | session | active |
| **R5** | folder-structure | `forbid_root` · `validators/folder_structure.py` | PreToolUse + pre-commit | session, repo | active |
| **R6** | (trống) | không thấy validator/hook nào | — | — | **unknown/reserved** |
| **R7** | proposal-complete | `conditional_require` · `validators/proposal_complete.py` | PreToolUse + pre-commit | session, repo | active |
| **R8** | ⚠️ DRIFT | `gen-converters` gán **SessionStart**="R8"; nhưng pre-commit gọi `index_sync.py`="R3" | mâu thuẫn | session | **needs-reconcile** |
| **R9** | okf-frontmatter | `require_frontmatter` · `validators/okf_frontmatter.py` | PreToolUse + pre-commit | session, repo | active |
| **R10** | docs-gate | `harness-events.py docs` · UserPromptSubmit | session (report, không chặn) | session | active |
| **R11** | seq-html-glass-style | `conditional_require` · **policy.yaml** | session (write seq html) | session | active |
| **R12** | pull-before-change | `process_gate` · **policy.yaml** | (B) workflow Step 0 sweep · (C) git `pre-push` | session, repo | active |

## R11 — chi tiết
Seq diagram HTML (`*-seq.html`) phải theo style `docs-site-macos` liquid-glass (marker: `backdrop-filter` + `linear-gradient(180deg,#f7fbff…` + edge-highlight). Chặn theme flat tự chế lúc write. enforce_at `[session]` — KHÔNG `[repo]` để không fail ~8 seq html cũ (bật repo sau khi migrate). Xem [[270626-framework-gap-backfill]].

## R12 — chi tiết (gồm v3 workspace-aware)
- **(B) pre-work sweep** — orchestrator chạy `pull-gate-sweep.sh` ở **workflow Step 0** TRƯỚC fan-out: quét MỌI subrepo (manifest `.harness-workspace.yaml` | auto-discover harnessed), chặn nếu subrepo **target** sau remote (watch chỉ cảnh báo). Single-repo → rút về `pull-gate.sh`.
- **(C) pre-push** — git hook per-repo (`.git/hooks/pre-push` + `.pre-commit` stage), **vendor-neutral** (mọi `git push` đều dính). Nhân ra mọi subrepo bằng `install-harness.sh --all-subrepos`.
- **ĐÃ BỎ (A)** per-edit PreToolUse: cost cao, lệch đa-vendor, (B) đã phủ. Xem [[ADR-002-pull-before-change-gates]].

## Lệch cần xử (G2 — không che giấu)
- **policy.yaml chỉ chứa**: R1, R2, R5, R7, R9, R11, R12. R3/R4/R8/R10 wire ở `gen-converters.py` (hook → `harness-events.py`), KHÔNG trong policy → "nguồn chân lý duy nhất" còn rò.
- **R3 vs R8 mâu thuẫn**: pre-commit gọi `index_sync.py` nhãn "R3"; gen-converters nhãn Stop="R3", SessionStart="R8". Cần chốt số. (T1 của [[270626-framework-gap-backfill]]).
- **R6 trống** — chưa rõ retired hay reserved.

## Origin
- **Source:** đọc trực tiếp `harness/poc-vendor-neutral/policy.yaml`, `harness/validators/*.py`, `harness/poc-vendor-neutral/gen-converters.py`, `.pre-commit-config.yaml`, `concepts/R10.md` (baseline `188afae`→`076f970`).
- **Backfill request:** user — "backfill R11/R12/R12v3 vào rule-registry + ADR". Tiền lệ [[270626-framework-gap-backfill]], [[270626-r12-v3-workspace-aware]].
