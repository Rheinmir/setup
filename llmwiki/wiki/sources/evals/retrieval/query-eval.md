---
type: eval
id: query-eval
question: "Cách đo truy hồi (recall + token) của skill query?"
expected_pages: [query-retrieval-eval]
---

# Retrieval golden: query-eval

Golden truy-hồi (mảnh 2). `question` vào pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4). Chấm hit@k + token, không model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval, nới 10→30). Cap 30 (case #1).
