---
type: eval
id: enforcement-floor
question: "Vì sao CI mới là sàn enforcement thật, ba lớp chặn ra sao?"
expected_pages: [harness-enforcement-floor, ADR-006-blocking-stays-hook-mcp-for-tooling]
---

# Retrieval golden: enforcement-floor

Golden truy-hồi (mảnh 2). `question` vào pipeline, `expected_pages` là TẬP trang chấp nhận được (case xấu #4). Chấm hit@k + token, không model.

## Origin
- Seed dogfood từ fdk/wiki (gói 010726-query-retrieval-eval, nới 10→30). Cap 30 (case #1).
