---
type: eval
id: boris-template
question: "Áp 5 archetype Boris Cherny vào template: sweep-gate + persona dispatch?"
expected_pages: [ADR-015-boris-archetypes-into-template, boris-cherny-agent-roles]
---

# Retrieval golden: boris-template

Golden truy-hồi (mảnh 2). `question` vào pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4). Chấm hit@k + token, không model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval, nới 10→30). Cap 30 (case #1).
