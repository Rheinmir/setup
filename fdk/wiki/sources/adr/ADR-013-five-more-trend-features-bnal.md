---
type: decision
title: "ADR-013: 5 trend 2026 nữa → 5 chức năng qua build-now-adapt-later (memory · cost · injection · hallucination · prospective-reflection)"
status: accepted
tags: [adr, build-now-adapt-later, bnal, trends, memory, finops, prompt-injection, hallucination, reflection]
timestamp: 2026-06-29
id: ADR-013-five-more-trend-features-bnal
---

# ADR-013: 5 trend 2026 nữa → 5 chức năng (build-now-adapt-later, đợt 2)

## Status
Accepted (2026-06-29).

## Context
Tiếp nối ADR-012 (5 feature đợt 1), một lượt quét trend 30 ngày nữa (qua skill `last30days`, đường WebSearch-fallback) chỉ ra **5 hướng khác** framework chưa có, đều có dữ liệu rất gần đây và đều dính một ẩn số → hợp `/build-now-adapt-later`:

- **Agent memory** (Mem0/Zep/Letta; ADD/UPDATE/DELETE/NOOP, retrieval xếp hạng <7k token) — "lớp quyết định agent là đồ chơi hay hạ tầng production".
- **Token/$ FinOps** — "3× vượt ngân sách token 2026 vào tháng 4"; *không* agent framework nào ship dollar-cap native → phải tự xây per-action/per-session.
- **Indirect injection qua OUTPUT tool** — Anthropic bỏ metric direct-injection (2026-02); output tool vào context như "tin cậy" là mối đe doạ enterprise.
- **Hallucination / Tool Receipts** — agent bịa kết quả tool + trích file/API không tồn tại; phân loại claim theo nguồn tri thức + verify reference.
- **Prospective reflection** — critic nhẹ soi PLAN *trước khi chạy* so với taxonomy lỗi đã chưng cất, ép revise.

## Decision
Dựng cả 5 theo cùng khuôn BNAL của ADR-012 (lõi tất định + test ngay; ẩn số sau **một** `harness/<name>.config.yaml` `verified:false` + ADAPT-CHECKLIST; fail-safe mặc định không phá phiên):

| Feature (`harness/scripts/`) | Core tất định (built now) | Adapter quarantined (verified:false) | Nối với cái đã có |
|---|---|---|---|
| `mem-rank.py` | store + ADD/UPDATE/DELETE/NOOP + retrieve top-k Jaccard (NOOP nếu không liên quan) | `relevance.scorer`/`embedding_model:null`, `eviction.policy`/`max_entries` | bổ sung wiki + `.claude/memory` |
| `token-budget.py` | đếm token by-code, tổng/session, $ từ rates, cờ over-cap | `rates` (drift), `budgets`, `mode:warn` | governor mới (chưa có) |
| `inject-scan.py` | quét OUTPUT tool/retrieved theo signature, exit 0/2 | `patterns`, `classifier:null`, `action:flag` | bổ trợ `egress-guard` (lo mô tả/egress) |
| `claim-receipts.py` | trích reference file → verify resolve, cờ unresolved | `resolver:filesystem` (code-graph absent), `strictness:advisory`, `claim_taxonomy` | gate sống cho class "hallucination" của `failure-flywheel` |
| `prospect-critic.py` | match plan vs trigger/class, ép revise nếu ≥ threshold | `triggers`, `revision_threshold`, `match.mode:keyword` | TIÊU THỤ taxonomy của `failure-flywheel` (gương trước-khi-chạy của `trace-grader`) |

**Giữ trung thực:** wire 5 self-test mới vào `fdk-gate` → **15 self-test BNAL** (5 verified:true + 10 verified:false); leak-gate `adapt-registry --check` xanh với 14 adapter `verified:false`. Khoá schema chung (`mode`…) đã nằm trong `GENERIC_KEYS` nên adapter song song không bị tính leak.

## Consequences
- (+) 5 chức năng nữa chạy được ngay (lõi đã test), hoàn tất mỗi cái = sửa một config + `verified:true`.
- (+) Khép vòng với đồ cũ: `prospect-critic` (trước) ↔ `failure-flywheel`/`trace-grader` (sau); `claim-receipts` biến class hallucination thành gate sống; `inject-scan` + `egress-guard` phủ cả hai phía của bề mặt MCP/tool.
- (+) Lấp 2 khoảng trắng hạ tầng rõ: **memory layer** + **token/$ governor** (cái sau "không framework nào có").
- (−) Tới khi `verified:true`, security/cost/hallucination **chỉ advisory/warn** — chưa chặn; phải nói rõ.
- (−) +5 script + 5 config + thêm metric file (gitignored) để bảo trì; tổng 10 feature BNAL `verified:false` chờ hiệu chỉnh.

## Origin
- **Source:** goal-set phiên 2026-06-29 ("thêm 5 cái nữa, vừa /last30days research vừa /build-now-adapt-later"). Nối ADR-012.
- **Liên quan:** [[ADR-012-five-trend-features-bnal]] (đợt 1), [[build-now-adapt-later]], [[failure-flywheel]] (prospect-critic + claim-receipts bám vào), [[harness-enforcement-floor]].
- **Date:** 2026-06-29
