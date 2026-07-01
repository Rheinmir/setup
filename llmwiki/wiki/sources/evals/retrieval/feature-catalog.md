---
type: eval
id: feature-catalog
question: "Bản đồ mọi năng lực framework và vì sao cần nằm ở đâu?"
expected_pages: [feature-catalog]
---

# Retrieval golden: feature-catalog

Golden truy-hồi (mảnh 2). `question` vào pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4). Chấm hit@k + token, không model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval, nới 10→30). Cap 30 (case #1).
