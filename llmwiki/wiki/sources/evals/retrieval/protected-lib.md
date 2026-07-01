---
type: eval
id: protected-lib
question: "Cơ chế bảo vệ pattern library khỏi sửa nhầm là gì?"
expected_pages: [ADR-014-protected-pattern-library, R10]
---

# Retrieval golden: protected-lib

Golden truy-hồi (mảnh 2). Frontmatter là hợp đồng máy-đọc: `question` đưa vào query pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4 — không phải 1 trang). Scorer chấm hit@k + token, không gọi model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval). Cap 30 golden (case xấu #1).
