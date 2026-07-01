---
type: eval
id: pull-gate
question: "Pull-before-change gate hoạt động thế nào?"
expected_pages: [ADR-002-pull-before-change-gates]
---

# Retrieval golden: pull-gate

Golden truy-hồi (mảnh 2). Frontmatter là hợp đồng máy-đọc: `question` đưa vào query pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4 — không phải 1 trang). Scorer chấm hit@k + token, không gọi model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval). Cap 30 golden (case xấu #1).
