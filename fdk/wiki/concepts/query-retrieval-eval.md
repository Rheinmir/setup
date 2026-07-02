---
type: concept
title: query-retrieval-eval — đo TRUY HỒI của skill query (L0→L1)
status: implemented
tags: [query, retrieval, eval, telemetry, progressive-disclosure, measure-first]
timestamp: 2026-07-01
id: query-retrieval-eval
relations:
  - {rel: depends-on, to: outer-harness-evaluation}
---

# query-retrieval-eval — đo truy hồi trước, cải tiến sau

Skill `query` trước đây ở **L0**: thuần prose *"đọc mỗi trang liên quan đầy đủ"* — không có
retrieval code lọc-rồi-trả, không telemetry, và không cách nào đo query có tìm ra đúng trang
không hay tốn bao nhiêu token. Không đo được thì mọi "cải tiến" chỉ là đức tin. Gói này lắp
**cảm biến trước, rồi mới nâng tool** (thứ tự do council chốt — Karpathy mean-rank 1.33, dissent
Linus "ship tool trước"), đưa query lên **L1**: tool có-lọc, model-driven, đo được — nhưng KHÔNG
nuốt SQLite (giữ transparent + git + markdown; L2 hook-inject bị loại vì đoán mù + thuế token mọi lượt).

## Ba mảnh
- **Telemetry** — `harness/scripts/query-log.py`: mỗi query ghi 1 dòng JSONL `{question, pages_hit, tokens_est, tier_reached}`. Fail-open tuyệt đối. Giới hạn đã biết: chỉ đo khi skill `query` được gọi, không đo lượt model tự `Read` thẳng (đo *tool-usage*, không phải mọi retrieval).
- **Eval truy-hồi** — `harness/scripts/retrieval-eval.py`: chấm **hit@k** (top-k có giao `expected_pages` không — TẬP trang chấp nhận được, chống brittle) + **token**, so `harness/metrics/retrieval-baseline.json`. `--check` exit 2 khi hit@k tụt hoặc token phình. `--self-test` tất định (không gọi model). Goldens ở `llmwiki/wiki/sources/evals/retrieval/`.
- **Query 3 tầng** — `query.md` (canonical `skills/query/SKILL.md` + mirror `llmwiki/skills/wiki-loop/query.md`, byte-identical): tầng-1 quét rẻ bằng `ripgrep`/code-graph xếp hạng theo độ-phủ-term (KHÔNG mở full) → tầng-2 chỉ `Read` full top-N → tầng-3 lần theo `[[wikilinks]]`.
- **Pipeline tất định** — `harness/scripts/query-proxy.py` mô phỏng chiến lược L0/L1 để baseline tái-lập-được mà không gọi model (query production vẫn agentic).

## Kết quả đo
L1 giữ **hit@5 7/10 = bằng baseline L0**, token **272k → 95k (−65%)**. Eval đã chặn **3 lần thử
L1 tồi** (ranking chỉ-heading, ranking đếm-dòng, sai hàm xếp hạng) trước khi bản đúng qua — bằng
chứng "measure-first" hoạt động: không cho claim cải tiến khi recall thật sự tụt.

## Kỷ luật chống hai bẫy (chốt bằng CODE, không nhờ ý chí)
- **Mạ vàng eval → tê liệt:** `retrieval-eval` **từ chối chạy khi >30 golden** (hard-cap, exit ≠0).
- **Đo hơi nước:** baseline đo 1 lần lấy sàn; phần tất định tách khỏi model (`query-proxy`); eval + L1 **land cùng đợt** (commit `632e29c`), không đo một hệ chưa tất định rồi tô số.

## Notes
- [[outer-harness-evaluation]] — cùng họ "đo trước khi tin"; kia đo outer harness, đây đo retrieval.
- [[ADR-009-session-orientation-autoindex-forcequery]] — force-query là nơi query được gọi; telemetry đo chính đường đó.
- Nguồn cơ chế 3-tầng: engram (MCP `mem_search` FTS5, search→get→timeline) — steal *kỷ luật disclosure*, không steal DB.

## Origin
- **Source:** `wiki/draft/orca/010726-query-retrieval-eval.md` (proposal + council 5 ghế + 4 case xấu kèm chốt chặn)
- **Commit:** `632e29c` — feat(query): nâng L0→L1 có đo — retrieval-eval + telemetry + query 3-tầng
- **Task:** T-260701-01
- **Date:** 2026-07-01
