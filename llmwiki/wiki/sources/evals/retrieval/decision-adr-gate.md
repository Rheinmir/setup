---
type: eval
id: decision-adr-gate
question: "Gate ép quyết định kiến trúc thành ADR (R13) hoạt động ra sao?"
expected_pages: [ADR-010-decision-to-adr-gate]
---

# Retrieval golden: decision-adr-gate

Golden truy-hồi (mảnh 2). `question` vào pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4). Chấm hit@k + token, không model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval, nới 10→30). Cap 30 (case #1).
