---
type: eval
id: blocking-layer
question: "Lớp CHẶN nằm ở hook/CI hay ở MCP?"
expected_pages: [ADR-006-blocking-stays-hook-mcp-for-tooling]
---

# Retrieval golden: blocking-layer

Golden truy-hồi (mảnh 2). `question` vào pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4). Chấm hit@k + token, không model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval, nới 10→30). Cap 30 (case #1).
