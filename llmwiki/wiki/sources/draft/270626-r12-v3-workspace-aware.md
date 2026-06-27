---
type: draft
title: R12 v3 — workspace-aware pull-gate (nhiều subrepo)
status: proposed
tags: [harness, R12, pull-gate, workspace, multi-repo, orchestrator, pre-push, vendor-neutral]
timestamp: 2026-06-27
---

# 270626 — R12 v3 workspace-aware

## Bối cảnh

R12 hiện (sau khi rút gọn) = **(B)** orchestrator pre-work sweep + **(C)** pre-push git-level. Nhưng cả hai đang **single-repo**: `pull-gate.sh` chỉ check repo của `cwd`. Thực tế người dùng làm trong **1 workspace nhiều subrepo** (vd `design.md` + nested `setup/` + `co2-be/inventory`), và **dispatch đa-vendor** (opencode/agy/kiro/copilot/cursor).

Hai điểm phủ-mọi-vendor đã chốt: **(B)** do orchestrator chạy (không dựa lifecycle session vendor), **(C)** git-level (mọi `git push` đều dính). Việc còn lại: nâng cả hai từ 1-repo lên **cả workspace**.

## Vấn đề kiểm chứng

| # | Vấn đề | Bằng chứng |
|---|--------|-----------|
| V1 | (B) chỉ fetch repo của `cwd` | `pull-gate.sh` dùng `git rev-parse --abbrev-ref HEAD` ở cwd; edit file subrepo khác → check sai repo (đã phân tích turn trước) |
| V2 | (C) chỉ cài pre-push 1 repo | `.git/hooks/pre-push` + `install-harness` hiện chạy 1 ROOT; subrepo khác KHÔNG có gate2 → push lọt |
| V3 | Chưa có nguồn "danh sách subrepo" | Không manifest, không sweep; deps/vendored repo lẫn lộn nếu auto-discover thô |

## Thiết kế (nguyên tắc)

- **Resolve repo theo file = local, rẻ** (`git -C <dir> rev-parse --show-toplevel`) — KHÔNG fetch. Fetch chỉ ở (B) sweep + (C) push.
- **(B) sweep = read-only**: fetch song song từng subrepo (timeout, fail-open), in bảng trạng thái; **chỉ chặn fan-out nếu subrepo ĐÍCH (sắp ghi) đang sau remote**. Không auto-pull (người quyết từng repo).
- **Discovery**: manifest `.harness-workspace.yaml` (liệt kê subrepo + exclude globs) ưu tiên; fallback `find -maxdepth N -name .git`. Scope "harnessed-repo only" để bỏ deps lạ.
- **(C) bất biến per-repo**, chỉ nhân ra mọi subrepo qua `--all-subrepos`.

## Plan

> Execution **hoãn** tới sau gate.

- [ ] **T1** — `harness/poc-vendor-neutral/bin/pull-gate-sweep.sh`: discover subrepo (manifest|find) → fetch song song (timeout, fail-open) → in bảng `repo · branch · ahead/behind`; exit 2 nếu **subrepo đích** behind. Tái dùng `pull-gate.sh` per repo.
- [ ] **T2** — Schema + parser `.harness-workspace.yaml` (`subrepos: [...]`, `exclude: [...]`, `targets: [...]`); thiếu manifest → auto-discover depth N + lọc harnessed.
- [ ] **T3** — `install-harness.sh --all-subrepos`: loop subrepo → cài pre-push (gate2) + `.pre-commit` mỗi cái; idempotent; report bảng đã-cài.
- [ ] **T4** — orca-workflow Step 0: gọi `pull-gate-sweep.sh` thay `pull-gate.sh gate1` (sweep cả workspace trước fan-out); cập nhật 2 bản skill.
- [ ] **T5** — Test multi-subrepo fixture: tạo 2-3 repo giả, 1 cái cố tình behind → sweep phát hiện đúng (exit 2 khi là đích); `--all-subrepos` wire đúng N pre-push; reversible.

## Agent Task Assignment

| Task | Agent CLI | Lý do chọn | Status |
|------|-----------|------------|--------|
| T1 pull-gate-sweep.sh | Claude Code | Ngữ nghĩa orchestration + exit-code đích/không-đích dễ vỡ | pending |
| T2 manifest schema + parser | OpenCode `big-pickle` | Parse YAML + glob, cơ học | pending |
| T3 install --all-subrepos | Kiro | Loop cài + config, độc lập verify | pending |
| T4 Step 0 → sweep (2 skill) | Claude Code | Sửa luồng workflow, prose (không caveman) | pending |
| T5 multi-subrepo test fixture | Kiro | Tạo fixture + assert, độc lập | pending |

## Sequence diagram

Mỗi task một sơ đồ (glass docs-site-macos, badge agent): [`270626-r12-v3-workspace-aware-seq.html`](../../../html/270626-r12-v3-workspace-aware-seq.html)

## Origin

- **Request:** user — "dựng propose R12 v3 workspace-aware rồi gate, cập nhật lại test".
- **Tiền lệ:** [[270626-framework-gap-backfill]] (R11 + R12 (B)+(C)); turn phân tích multi-repo + đa-vendor (gate2 git-level là sàn duy nhất phủ mọi vendor).
- **Baseline:** `rheinmir/setup#orca` @ `188afae` (đã push, synced).
- **Commit:** _(verify-before-commit điền khi promote)_
