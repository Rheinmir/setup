---
type: eval
id: scanner-gitignore
question: "wiki-tree scanner lọc file gitignored tại đâu?"
expected_pages: [ADR-007-wiki-scanner-skip-gitignored-at-lister]
---

# Retrieval golden: scanner-gitignore

Golden truy-hồi (mảnh 2). `question` vào pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4). Chấm hit@k + token, không model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval, nới 10→30). Cap 30 (case #1).
