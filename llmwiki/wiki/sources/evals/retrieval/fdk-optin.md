---
type: eval
id: fdk-optin
question: "Vì sao framework-dev context là opt-in, không auto-bơm đầu phiên?"
expected_pages: [ADR-004-framework-dev-context-opt-in]
---

# Retrieval golden: fdk-optin

Golden truy-hồi (mảnh 2). `question` vào pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4). Chấm hit@k + token, không model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval, nới 10→30). Cap 30 (case #1).
