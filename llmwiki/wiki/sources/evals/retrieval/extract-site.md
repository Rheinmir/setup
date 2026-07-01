---
type: eval
id: extract-site
question: "Skill extract-site dùng để làm gì?"
expected_pages: [extract-site]
---

# Retrieval golden: extract-site

Golden truy-hồi (mảnh 2). `question` vào pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4). Chấm hit@k + token, không model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval, nới 10→30). Cap 30 (case #1).
