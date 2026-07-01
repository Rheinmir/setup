---
type: eval
id: harness-local
question: "Làm sao dự án tự build harness riêng mà KHÔNG chạm module gốc?"
expected_pages: [harness-local, ADR-011-project-local-harness]
---

# Retrieval golden: harness-local

Golden truy-hồi (mảnh 2). Frontmatter là hợp đồng máy-đọc: `question` đưa vào query pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4 — không phải 1 trang). Scorer chấm hit@k + token, không gọi model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval). Cap 30 golden (case xấu #1).
