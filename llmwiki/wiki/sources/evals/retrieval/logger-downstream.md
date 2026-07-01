---
type: eval
id: logger-downstream
question: "code-logger và bản đồ năng lực đi xuống dự án downstream thế nào?"
expected_pages: [ADR-005-logger-and-capabilities-travel-downstream]
---

# Retrieval golden: logger-downstream

Golden truy-hồi (mảnh 2). `question` vào pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4). Chấm hit@k + token, không model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval, nới 10→30). Cap 30 (case #1).
