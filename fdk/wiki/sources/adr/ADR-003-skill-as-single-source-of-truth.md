---
type: decision
title: "ADR-003: skill con là nguồn chân lý — orchestrator delegate, Claude nghĩ / CLI rẻ render"
status: accepted
tags: [adr, skill, dry, propose, orca-workflow, dispatch]
timestamp: 2026-06-27
id: ADR-003-skill-as-single-source-of-truth
---

# ADR-003: skill con là nguồn chân lý — orchestrator chỉ delegate

## Status
Accepted (2026-06-27)

## Context
Skill `propose` từng được mô tả ở hai nơi: bản thân skill `/propose` (canonical `llmwiki/skills/dev-loop/propose.md` + mirror + global), và một lần nữa bằng văn xuôi bên trong bước 2 của `orca-workflow`. Hai bản tả cùng một việc nhưng đã lệch nhau — phần trong `orca-workflow` giàu hơn (nó bắt buộc style `docs-site-macos` glass và đã rút bài học 250626 "sao xấu thế"), còn `/propose` chỉ nói "2 màu". Hệ quả là ai chạy `/propose` lẻ sẽ tạo ra trang HTML phẳng/tối, đúng cái người dùng từng chê. Đây là drift cổ điển do nhân đôi định nghĩa.

Song song, người dùng đặt câu hỏi chi phí: trang seq HTML đầy đủ (Full `docs-site-macos`) nặng 42–60 KB, mà nội dung thật chỉ chiếm 3–8 KB — phần còn lại là markup, CSS và JS. Nếu Claude tự gõ cả trang thì token phình theo độ giàu HTML, trong khi phần phình đó là cơ học, không cần phán đoán.

## Decision
1. **Skill con là nguồn chân lý duy nhất.** Toàn bộ hành vi propose (cặp `.md`+`.html`, các mục R7, style glass `docs-site-macos`, yêu cầu prose chi tiết) sống trong `llmwiki/skills/dev-loop/propose.md`. Sửa hành vi propose chỉ sửa file này; mirror và bản remote được đồng bộ qua `sync-template`, không chép tay.
2. **Orchestrator delegate, không mô tả lại.** `orca-workflow` bước 2 **gọi** `/propose` (Skill tool) thay vì tả lại bằng văn xuôi — đúng pattern bước 1 đã gọi `query`. Bên trong `orca-workflow` chỉ còn phần *điều phối* (R12 sweep, gate, dispatch, verify), không còn phần *định nghĩa* propose.
3. **Tách "Claude nghĩ" khỏi "CLI rẻ render".** Ranh giới đặt đúng ở `.md` / `.html`: Claude sản xuất SUBSTANCE — file `.md` render-complete gồm Plan, prose và một `## Render brief` liệt kê từng bước diagram dạng dữ liệu kèm đoạn prose cho mỗi task. File `.html` là bản RENDER cơ học của brief đó; trong luồng có Orca, việc render được dispatch sang một CLI rẻ (OpenCode `big-pickle`, hoặc `agy`/`kiro`, chi phí $0). Vì render miễn phí nên ưu tiên Full `docs-site-macos` richness — token của Claude chỉ tốn cho substance và không phình theo độ giàu của HTML.

## Consequences
- (+) Sửa propose một chỗ; `/propose` lẻ và `orca-workflow` luôn nhất quán, hết drift glass-style.
- (+) Chi phí render rời khỏi Claude sang engine miễn phí; chọn Full mà không xót token.
- (+) Tách bạch đúng thế mạnh: Claude lo phán đoán/nội dung, CLI rẻ lo khuôn mẫu lặp lại.
- (−) Độ tin cậy dispatch headless chỉ ~1/5 (bài học 250626) → bắt buộc watchdog 60–90s, R7 gate và fallback Claude; "free" là theo xác suất, khi trượt Claude vẫn trả một phần token.
- (−) Handoff đáng tin đòi `.md` phải có `## Render brief` đầy đủ — thêm một mục cho mỗi proposal trong luồng orchestrated; bù lại render mới mechanical được.
- (−) "Sửa một chỗ" chỉ đúng nếu mirror được đồng bộ kỷ luật qua `sync-template`, không chép tay ba bản.

## Origin
- **Decision rút từ:** phiên 2026-06-27 — phát hiện drift `/propose` ↔ `orca-workflow`, rồi bàn chi phí render và mô hình Claude-nghĩ/CLI-rẻ-render.
- **Nguồn:** [[270626-propose-single-source]], `llmwiki/skills/dev-loop/propose.md`, `llmwiki/skills/orchestrate/orca-workflow.md`, cùng họ [[ADR-001-policy-as-source-of-truth]] / [[ADR-002-pull-before-change-gates]].
