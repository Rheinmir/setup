
|           | prompt                                | context(atlan meaning)                           | harness                                                         |
| --------- | ------------------------------------- | ------------------------------------------------ | --------------------------------------------------------------- |
| Phạm vi   | Một câu lệnh hoặc một phiên tương tác | Dữ liệu, tài liệu, lịch sử, tri thức đưa vào AI  | Toàn bộ môi trường vận hành của AI Agent                        |
| Ví dụ     | “Hãy viết bài chuẩn SEO”              | Cung cấp từ khóa, tài liệu, chân dung khách hàng | Quy trình tự nghiên cứu, viết, kiểm SEO, trích nguồn, xuất HTML |
| Điểm mạnh | Dễ bắt đầu, nhanh có kết quả          | Giảm trả lời chung chung, tăng độ chính xác      | Tăng độ tin cậy, kiểm soát, khả năng triển khai thực tế         |
| Giới hạn  | Dễ phụ thuộc vào cách diễn đạt        | Nếu thiếu quy trình, AI vẫn có thể làm sai       | Cần thiết kế hệ thống, tiêu chí, công cụ và giám sát            |

## Kiến trúc harness của llmwiki (implement 2026-06-10)

Chi tiết và cách port sang vendor khác: **[recipe.md](recipe.md)**. Tóm tắt 5 lớp:

```
L0 POLICY   policy.yaml — bất biến R1..R6, khai báo, vendor-free
L1 SESSION  adapter per vendor (Claude Code: hooks + permissions.deny) → validators/
L2 REPO     .pre-commit-config.yaml — backstop vendor-neutral, gate mọi commit
L3 AUDIT    JSONL audit tự động + ccusage — log bằng máy, không nhờ model nhớ
L4 EVALS    wiki-health.py (0 token) + promptfoo golden questions (weekly, ~$1-5)
```

### Checklist 12 primitive (theo [awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering))

| Primitive | llmwiki có gì | Trạng thái |
|---|---|---|
| Agent loop | wiki-loop / dev-loop / orchestrate | ✅ trước đó |
| Planning & decomposition | propose → gate → dispatch | ✅ trước đó |
| Context delivery | wiki/ + active-context.md + caveman | ✅ trước đó |
| Tool design | skills (markdown) | ✅ trước đó |
| Skills & MCP | bộ skills 4 nhóm | ✅ trước đó |
| Permissions & authorization | permissions.deny + PreToolUse block | ✅ mới (L1) |
| Memory & state | wiki/ + active-context.md | ✅ trước đó |
| Orchestration | Orca flows | ✅ trước đó |
| Verification & CI | pre-commit validators | ✅ mới (L2) |
| Observability & tracing | JSONL audit + ccusage | ✅ mới (L3) |
| Debugging & DX | fail-open hooks, stderr viết cho agent đọc | ✅ mới |
| Human-in-the-loop | propose gate, draft approval | ✅ trước đó |


