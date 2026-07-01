---
type: eval
id: trend-bnal-2
question: "5 trend 2026 tiếp (memory, cost, injection, hallucination) áp ntn?"
expected_pages: [ADR-013-five-more-trend-features-bnal]
---

# Retrieval golden: trend-bnal-2

Golden truy-hồi (mảnh 2). `question` vào pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4). Chấm hit@k + token, không model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval, nới 10→30). Cap 30 (case #1).
