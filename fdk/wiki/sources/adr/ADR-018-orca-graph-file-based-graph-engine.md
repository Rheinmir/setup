---
type: decision
title: "ADR-018: orca-graph là graph engine file-based một máy — vay luật state của Reprise, không vay hạ tầng"
status: accepted
tags: [adr, orca-graph, graph-engine, state, reprise, file-based]
timestamp: 2026-09-12
id: ADR-018-orca-graph-file-based-graph-engine
---

# ADR-018: orca-graph là graph engine file-based một máy

## Status
Accepted (2026-09-12).

## Context
Dispatch trong `/orca-workflow` không có đồ thị phụ thuộc và không có state bền theo node. Hai PRD Reprise (Work Continuity và Graph Engine) mô tả một engine đầy đủ với PostgreSQL, sandbox, secret gateway, integration queue và compensation. Câu hỏi là vay tới đâu.

## Decision
1. **Vay luật, không vay hạ tầng.** Mọi luật bền state của PRD được đưa vào tool: op_key idempotent, CAS revision, generation, lease và reaper về `unknown`, plan version và superseded, control phân biệt yêu cầu và đã dừng, join của graph mẹ chỉ khi mọi con xong, cycle in đường cụ thể, hạn mức depth và số node. Hạ tầng (DB, sandbox, gateway, tiền, LangGraph, integration queue, compensation) nằm ngoài phạm vi và được ghi rõ trong SKILL.md.
2. **Store là file.** JSONL append-only là sự thật, `graph.json` là cache fold lại, lockfile `O_EXCL`. Một writer là orchestrator. Marker nâng cấp: khi nhiều orchestrator ghi đồng thời thật sự thì chuyển sang SQLite WAL, không làm sớm.
3. **Không LLM trong kiểm quyền, DAG, lifecycle** (bất biến 12 của PRD). Model chỉ được bổ sung ý nghĩa qua `answer` có nhãn và nguồn; `audit` tất định chấm, bịa nguồn bằng 0.
4. **Deps là dữ liệu trong PLAN.** Khuôn `/plan` thêm dòng `**Depends:**` và `**Verify:**`; thiếu thì tool suy luận và gắn nhãn `gợi-ý`, không được dispatch lớp đó khi chưa xác nhận.

## Consequences
- Được: song song và tuần tự có bằng chứng; state sống qua crash; cùng một PLAN chạy lại ra cùng graph; chính PLAN triển khai v2 đã chạy qua tool và lint bắt được một lỗi parser thật.
- Mất: khoá không chặn side-effect của agent đã chạy; không rollback tự động; sổ Orca chỉ sync một chiều; atlas lớn cần graphviz.
- Nợ có kỳ hạn: SQLite khi có nhiều writer; graphviz khi atlas quá vài trăm node.

## Origin
Phiên /fdk 12/09/2026. Liên quan: [[orca-graph]], [[120926-reprise-prd-work-continuity]], [[120926-reprise-graph-engine-prd]], [[ADR-015-boris-archetypes-into-template]] (persona dispatch dùng chung).
