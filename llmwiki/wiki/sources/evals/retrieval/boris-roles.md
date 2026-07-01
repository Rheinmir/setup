---
type: eval
id: boris-roles
question: "5 vai vòng đời agent của Boris Cherny là gì?"
expected_pages: [boris-cherny-agent-roles, ADR-015-boris-archetypes-into-template]
---

# Retrieval golden: boris-roles

Golden truy-hồi (mảnh 2). Frontmatter là hợp đồng máy-đọc: `question` đưa vào query pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4 — không phải 1 trang). Scorer chấm hit@k + token, không gọi model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval). Cap 30 golden (case xấu #1).
