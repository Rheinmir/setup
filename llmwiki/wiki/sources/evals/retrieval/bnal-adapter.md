---
type: eval
id: bnal-adapter
question: "build-now-adapt-later: core-now + adapter verified:false nghĩa là gì?"
expected_pages: [ADR-012-five-trend-features-bnal, ADR-013-five-more-trend-features-bnal]
---

# Retrieval golden: bnal-adapter

Golden truy-hồi (mảnh 2). `question` vào pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4). Chấm hit@k + token, không model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval, nới 10→30). Cap 30 (case #1).
