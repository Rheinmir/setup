---
type: source
title: Bài học Đế quốc Mông Cổ cho chiến lược AI (raw fdk-stragegy)
resource: llmwiki/raw/fdk-stragegy.md
tags: [strategy, source, mongol]
timestamp: 2026-07-02
id: mongol-ai-strategy
relations:
  - {rel: derives-from, path: llmwiki/raw/fdk-stragegy.md}
---

# Bài học Đế quốc Mông Cổ cho chiến lược AI

Nguồn raw nêu 8 bài học tổ chức của Đế quốc Mông Cổ và ánh xạ sang doanh nghiệp/đội dùng AI:

1. **Tốc độ hơn quy mô** — thắng nhờ decision latency thấp, không nhờ đông người; team 10 người + AI agent cạnh tranh được team 50 nếu release nhanh gấp 3.
2. **Meritocracy** — bổ nhiệm theo năng lực; AI khuếch đại khoảng cách giữa người biết leverage và người làm thủ công.
3. **Tiêu chuẩn hóa** — luật chung, trạm ngựa, chuẩn truyền tin → prompt template, coding standard, agent workflow, knowledge graph, ADR, documentation.
4. **Modular Army** — đơn vị 10/100/1000 độc lập → chuỗi agent chuyên trách (planner → research → coding → review → test → deploy), không xây một AI khổng lồ.
5. **Intelligence trước Combat** — do thám/bản đồ trước khi đánh → Data > Model; data sạch + knowledge tốt thắng model mạnh nhưng dữ liệu hỗn loạn.
6. **Chiếm người giỏi thay vì phá hủy** — thu nạp kỹ sư/học giả vùng chinh phục → tận dụng OSS/MCP/SDK/API và ghép lại; người thắng là người tích hợp nhanh nhất.
7. **Logistics quyết định thắng bại** — thắng nhờ hậu cần, không nhờ ngựa → LLM chỉ là "con ngựa"; vector DB, cache, memory, queue, workflow, observability, evaluation, governance mới là hậu cần.
8. **Psychological Warfare** — khiến đối thủ đầu hàng trước khi đánh → release mỗi ngày, demo liên tục, tự động hóa gần hết quy trình tạo áp lực trước khi đối thủ kịp phản ứng.

Bản pattern hóa cho phát triển fdk: [[fdk-dev-strategy]].

## Origin
- **Source:** `llmwiki/raw/fdk-stragegy.md`
- **Date:** 2026-07-02
