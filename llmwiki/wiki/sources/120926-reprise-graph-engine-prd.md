---
type: source
title: "Reprise Graph Engine PRD v1.0 — full cycle xử lý yêu cầu bằng graph phân cấp: ba cấu trúc tách nhau, leaf contract, scheduler durable, replan, 12 bất biến"
status: ingested
tags: [prd, reprise, graph-engine, containment-tree, dag, scheduler, replan, orca-graph]
timestamp: 2026-09-12
id: 120926-reprise-graph-engine-prd
relations:
  - {rel: informs, to: orca-graph}
  - {rel: derives-from, to: 120926-reprise-prd-work-continuity}
  - {rel: raw, path: llmwiki/raw/Reprise-Graph-Engine-Full-Cycle-PRD.md}
---

# Reprise Graph Engine PRD v1.0 — xử lý yêu cầu bằng graph phân cấp

## Tóm tắt

Tài liệu 1.998 dòng mô tả một engine nhận một yêu cầu lớn ("làm app đặt phòng họp product-grade"), chia thành graph mẹ và các graph con theo cấp, chạy bằng scheduler bền, và giữ được lịch sử khi yêu cầu đổi giữa chừng. Ý tưởng trung tâm ở §3: **ba cấu trúc khác nhau, đừng vẽ chung thành một búi**. Cây chứa việc trả lời "ai sở hữu"; đồ thị phụ thuộc trả lời "cần gì trước"; máy trạng thái thực thi trả lời "đang ở pha nào". Nhiều tool orchestration vẽ cả ba lên một hình rồi không biết cạnh nào nghĩa gì.

## Các ý đã áp vào orca-graph v2 (12/09/2026)

| Mục PRD | Cơ chế | Cách vào orca-graph |
|---|---|---|
| §4 cấp chứa | Graph mẹ, con, cấp là độ sâu chứa việc, không phải số prompt | `build --parent gid/node`, node mẹ có `child_graph`, join khi mọi node con xong |
| §5.2 giới hạn cứng | depth tối đa 6, tối đa 20 con trực tiếp | tool từ chối khi vượt |
| §5.3 cycle xuyên module | Compiler trả đường cycle cụ thể, không chỉ "graph invalid" | `check-cycles` in `a/t2 → b/t3 → a/t2` |
| §4.4 leaf đủ tốt | Leaf cần outcome, input có version, output schema, phạm vi ghi, phép kiểm | `lint`, `build --strict` |
| §7.3, §10.1 replan | Plan version mới, kết quả cũ vào lịch sử, không last-write-wins | `plan_version`, `superseded[]`, `spec_hash` làm node đã xong thành `stale` |
| §8.3 control | Yêu cầu dừng khác với workload đã dừng | `control pause|resume|cancel|status`, `pause_requested` chỉ thành `paused` khi không còn node chạy |
| §12.1 hạn mức | Concurrency reserve trước khi fan-out | `--max-parallel` |
| §16.1 bất biến 2, 4, 11, 12 | Không publish stale; thiếu required child không completed; pause phân biệt nhận và dừng; không cần LLM để kiểm DAG | đều tất định trong tool |

## Những gì nằm ngoài phạm vi và được nói thẳng trong SKILL.md

PostgreSQL ledger với `SKIP LOCKED`, sandbox và isolation runtime, secret gateway, ngân sách tiền, ánh xạ LangGraph, integration queue với candidate hash, compensation cho effect ngoài. Đây là engine khác, không phải bản nâng cấp của một tool file-based.

## Bài học khi dogfood

PLAN triển khai chính bản nâng cấp này được chạy qua orca-graph. Lệnh `lint` bắt được node t7 thiếu Verify. Nguyên nhân là parser coi dòng `## ` bên trong khối code của PLAN là hết task. Cổng tất định bắt lỗi mà mắt người bỏ qua, đúng tinh thần bất biến 12 của PRD.

## Origin

- Nguồn thô: `llmwiki/raw/Reprise-Graph-Engine-Full-Cycle-PRD.md` (user đưa ngày 12/09/2026, yêu cầu "triển khai xong PRD thì dùng").
- Triển khai: PLAN `sources/draft/120926-orca-graph-v2-PLAN.md`, graph `wiki/graph/120926-orca-graph-v2.graph.json`, concept [[orca-graph]], quyết định [[ADR-018-orca-graph-file-based-graph-engine]].
