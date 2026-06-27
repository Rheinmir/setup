---
type: decision
title: "ADR-002: R12 pull-before-change — git-level + orchestrator, không per-edit"
status: accepted
tags: [adr, harness, R12, pull-gate, multi-vendor, workspace, multi-repo]
timestamp: 2026-06-27
---

# ADR-002: pull-before-change (R12) — đặt gate ở đâu dưới đa-vendor & đa-subrepo

## Status
Accepted (2026-06-27). Mở rộng: R12 v3 workspace-aware ([[270626-r12-v3-workspace-aware]]).

## Context
Cần kỷ luật "đừng làm trên base cũ" cho 1 framework mà:
1. **Dispatch đa-vendor** (claude/opencode/agy/kiro/cursor) — mỗi vendor lifecycle session khác nhau; không thể tin SessionStart của bất kỳ vendor nào phủ hết.
2. **Workspace nhiều subrepo** — mỗi repo branch/remote riêng; "pull" vốn dĩ per-repo.

Phân biệt 2 bài toán: **gate2 = đừng *kết thúc* sai** (push đè); **gate1 = đừng *bắt đầu* sai** (base cũ → rebase đau, conflict ngữ nghĩa, đàn agent diverge).

## Decision
Chỉ đặt enforcement ở **2 điểm phủ được MỌI vendor**:

- **(C) gate2 = git pre-push hook** (per-repo, git-level). Mọi `git push` của bất kỳ vendor đều chạy hook → đây là **sàn cứng vendor-neutral**. Nhân ra mọi subrepo: `install-harness.sh --all-subrepos`.
- **(B) pre-work sweep = orchestrator chạy MỘT LẦN ở workflow Step 0**, TRƯỚC fan-out. Quét cả workspace (`pull-gate-sweep.sh`), chặn nếu subrepo **target** sau remote. Vendor-neutral *by construction* vì orchestrator làm hộ, không phụ thuộc session worker.

**Bác bỏ (A) per-edit PreToolUse gate1:** cost cao (fetch mỗi edit), lệch vendor (chỉ claude/opencode chặn được; cursor/kiro chỉ nhắc), và (B) đã phủ. Đã gỡ khỏi `pre_tool_use.py` + `gen-converters.py`.

**Bác bỏ SessionStart làm enforcement:** chỉ Claude-local, không tới worker vendor khác → chỉ giữ làm tiện ích phụ.

## Tiêu chí rút ra (tái dùng cho luật tương lai)
- Enforcement chỉ tin **git-level** (mọi vendor) hoặc **orchestrator** (làm hộ trước fan-out). KHÔNG tin lifecycle session từng vendor.
- Resolve repo theo file = **local, rẻ** (`rev-parse --show-toplevel`); **fetch (mạng) chỉ ở (B) sweep + (C) push**, không bao giờ trên đường edit.
- Lỗi hạ tầng (offline/no-remote) → **fail-open**, không khoá cứng.
- target vs watch: chỉ chặn repo ta thật sự sẽ ghi/đẩy.

## Consequences
- (+) Phủ mọi vendor bằng đúng 2 điểm; bỏ được latency per-edit.
- (+) Multi-subrepo chạy mượt: sweep front-load mạng 1 lần, edit không fetch.
- (−) gate2 chỉ có ở repo đã cài hook (`.git/hooks` không version-controlled) → phải `--all-subrepos`/pre-commit pre-push để team có.
- (−) (B) hơi cũ tối đa = tuổi phiên; chấp nhận vì (C) bắt ca thật lúc push.

## Origin
- **Decision rút từ:** chuỗi hỏi-đáp 2026-06-27 (multi-repo → multi-vendor → "tại sao cần session gate" → rút gọn (B)+(C) → v3 workspace-aware).
- **Nguồn:** [[270626-framework-gap-backfill]], [[270626-r12-v3-workspace-aware]], [[rule-registry]], `bin/pull-gate-sweep.sh`, `bin/pull-gate.sh`.
