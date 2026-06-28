---
type: decision
title: "ADR-009: session-orientation + auto-index + force-query — phiên mới biết hệ thống có gì, không 'lơ ngơ'"
status: accepted
tags: [adr, session, orientation, code-index, code-graph, auto-index, force-query, propose]
timestamp: 2026-06-28
---

# ADR-009: phiên mới phải BIẾT hệ thống có gì (orientation) + index tự khớp + propose buộc ground wiki

## Status
Accepted (2026-06-28).

## Context
Yêu cầu (goal-set): *"vào session mới thì hệ thống vẫn chạy tốt và BIẾT nó có gì chứ không lơ ngơ"*. Ba lỗ hổng:
1. **Lơ ngơ đầu phiên** — `session_start.py` chỉ inject pattern-health; agent KHÔNG được nhắc rằng project có code-index (code-graph) + wiki + CAPABILITIES để query → grep/đọc mù, chậm.
2. **Index không tự khớp** — đổi wiki thì Stop hook CHECK→BLOCK, bắt sửa `index.md` tay (self-heal `--fix` có nhưng không wire).
3. **Propose "mù"** — `/propose` không buộc query lại wiki để ground.

Đã có sẵn (xác minh): code-graph server `--watch` **auto-reindex** code khi đổi (debounce 2s) + `code_graph_keeper.py` (SessionStart) re-register repo cho watcher bền qua restart → **code-index auto-update là CÓ**, chỉ thiếu phần "nhắc agent query nó".

## Decision
1. **Session-orientation** — `session_start.py` thêm `orient()`: đầu phiên in NGẮN cho agent biết project có **code-index (code-graph, auto-watch) · wiki · CAPABILITIES.md** và NHẮC query trước khi đọc/grep rộng. Chỉ in khi thật sự có (không noise). Project-relevant nên KHÔNG vi phạm ADR-004 (chỉ cấm auto-bơm FDK framework-dev).
2. **Auto-index** — `stop.py` tự chạy `index_sync --fix` khi phiên đụng wiki → file wiki MỚI tự vào `index.md`. Chiều xóa/stale vẫn để check chặn (gỡ row là quyết định người).
3. **Force-query grounding** — R7 `proposal_complete` +check (f): chặn draft propose thiếu `## Context` có nội dung; `/propose` +bước 0 "force-query wiki TRƯỚC khi draft".

**Gate:** `harness/tests/auto-index-and-grounding-test.sh` (auto-index + R7-f) wire vào CI `repo-health` + pre-commit.

## Consequences
- (+) Phiên mới **tự định hướng**: agent biết query code-index/wiki để định vị nhanh, không lơ ngơ.
- (+) `index.md` tự khớp khi thêm file wiki; propose buộc ground vào wiki (chống đề xuất trùng/mâu thuẫn).
- (+) Mọi cơ chế được test + CI/pre-commit gác → không thể âm thầm gỡ.
- (−) Orientation in mỗi phiên (ngắn) — chấp nhận vì đó chính là yêu cầu "luôn nhắc".
- Ghi chú: **ADR vẫn được tạo qua `/docs-curate` (promote draft → `sources/adr/`)** hoặc tay; CHƯA có skill *bắt buộc* ghi ADR khi có quyết định — `decisions.md` log mọi quyết định, ADR là bản chi tiết promote sau (cân nhắc gate "decision→ADR" sau).

## Origin
- **Source:** goal-set phiên 2026-06-28. Commits: `876a8b7` (auto-index + force-query + test), `d8e3ae9` (orientation). Code-index auto-update có sẵn (code-graph `--watch` + `code_graph_keeper.py`).
- **Liên quan:** [[ADR-004-framework-dev-context-opt-in]], [[ADR-008-framework-wiki-lives-in-the-kit]], [[rule-registry]].
- **Date:** 2026-06-28
