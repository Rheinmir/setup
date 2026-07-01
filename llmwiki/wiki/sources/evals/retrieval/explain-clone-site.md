---
type: eval
id: explain-clone-site
question: "Làm sao explain và clone một website?"
expected_pages: [cursor-explain-site, extract-site]
---

# Retrieval golden: explain-clone-site

Golden truy-hồi (mảnh 2). `question` vào pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4). Chấm hit@k + token, không model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval, nới 10→30). Cap 30 (case #1).
