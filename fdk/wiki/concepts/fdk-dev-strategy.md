---
type: concept
title: fdk-dev-strategy — 8 nguyên tắc "Mongol pattern" cho phát triển framework
tags: [strategy, dev-loop, fdk, pattern]
timestamp: 2026-07-02
id: fdk-dev-strategy
relations:
  - {rel: derives-from, path: llmwiki/raw/fdk-stragegy.md}
---

# fdk-dev-strategy — chiến thuật phát triển fdk theo "Mongol pattern"

Chiến lược phát triển fdk được pattern hóa từ 8 bài học tổ chức của Đế quốc Mông Cổ: lợi thế không nằm ở quy mô (số dòng code, số người) mà ở **tốc độ ra quyết định, tiêu chuẩn hóa, modular hóa, và hậu cần (harness)**. Mỗi bài học ánh xạ thành một nguyên tắc dev cụ thể với cơ chế đã có (hoặc cần bổ sung) trong framework.

## 8 nguyên tắc

### 1. Tốc độ hơn quy mô — Optimize decision latency
Không đo tiến độ bằng khối lượng code; đo bằng **độ trễ từ ý tưởng → quyết định → ship**. Cơ chế: vòng `propose → gate → dispatch` ([[orca-workflow]]) phải ngắn; quyết định kiến trúc chốt ngay thành ADR ([[rule-registry]] R13) thay vì treo. Một phiên nên kết thúc bằng một quyết định đã ghi, không phải một thảo luận mở.

### 2. Meritocracy — leverage hơn thâm niên
Ưu tiên năng lực đòn bẩy: một skill/rule tốt nhân giá trị lên mọi phiên, hơn là code tay lặp lại. Khi gặp việc lặp ≥2 lần → cân nhắc chưng thành skill (`/new-skill`) hoặc rule (failure-flywheel). Đánh giá đóng góp theo **số phiên được hưởng lợi**, không theo số dòng.

### 3. Tiêu chuẩn hóa — luật chung, trạm ngựa chung
AI chỉ mạnh khi dữ liệu chuẩn. Chuẩn của fdk: OKF v0.1 cho wiki page, `## Origin` bắt buộc (R2), skill là single source of truth (ADR-003), policy.yaml là nguồn chân lý enforcement (ADR-001), template đồng bộ qua `/sync-template` + `/health-check`. Mọi cải tiến phải chảy về chuẩn chung, không fork cục bộ (drift = nợ).

### 4. Modular Army — đơn vị 10/100/1000
Không xây một agent khổng lồ; chia thành các đơn vị độc lập tự vận hành: skill (đơn vị 10) → loop (dev-loop / wiki-loop / orchestrate, đơn vị 100) → harness + council (đơn vị 1000). Mỗi skill làm MỘT việc, compose qua orchestrator ([[orchestration]], [[fdk]]). Thêm năng lực = thêm đơn vị mới, không phình đơn vị cũ.

### 5. Intelligence trước Combat — Data > Model
Biết địa hình trước khi đánh: query wiki/code-graph/CAPABILITIES **trước** khi grep mù hay code mò (ADR-009 orientation + force-query). Đầu tư vào knowledge sạch (ingest đều, lint wiki, eval truy hồi [[query-retrieval-eval]]) thắng đầu tư vào model mạnh hơn. Wiki hỗn loạn = mù bản đồ.

### 6. Chiếm người giỏi thay vì phá hủy — tích hợp OSS trước, tự viết sau
Người thắng là người **tích hợp nhanh nhất**, không phải code nhiều nhất. Trước khi viết mới: tìm OSS/MCP/SDK/skill có sẵn (`find-skills`, CAPABILITIES.md — "đừng làm lại thứ đã tồn tại", ADR-005). Distill tri thức bên ngoài vào kit (như skill council từ Karpathy, agent-roles từ Boris Cherny) thay vì phát minh lại.

### 7. Logistics quyết định thắng bại — LLM chỉ là con ngựa
Sức mạnh thật nằm ở hậu cần: harness (hook + validator + CI floor, [[harness-enforcement-floor]]), memory/wiki, eval ([[outer-harness-evaluation]], wikieval), observability (code-logger), governance (ADR + rule). Ưu tiên đầu tư dev-effort vào các lớp này hơn là prompt-tinkering — không có hậu cần, framework chỉ là chatbot có style.

### 8. Psychological Warfare — demo liên tục, release mỗi ngày
Áp lực cạnh tranh đến từ **nhịp ship nhìn thấy được**: mỗi phiên kết thúc bằng artefact chạy được (report HTML, tour, skill mới đã đăng ký), commit đều, docs/demo luôn sẵn ([[onboarding-tour]], harness-tour). Nhịp release chính là chỉ số sức khỏe của framework.

## Cách dùng pattern này
- Khi **ưu tiên backlog**: chấm mỗi hạng mục theo nguyên tắc nó phục vụ; hạng mục chạm #3/#4/#7 (chuẩn hóa, modular, hậu cần) thường ăn lãi kép — ưu tiên trước feature bề mặt.
- Khi **review một proposal**: hỏi "cái này giảm decision latency (#1)? tái dùng được (#2)? theo chuẩn (#3)? là đơn vị độc lập (#4)? đã tra đồ nghề có sẵn chưa (#6)?"
- Khi **phiên trôi dạt**: quay về #5 — dừng combat, quay lại intelligence (query wiki trước).

## Notes
- [[fdk]] — front-door phát triển framework
- [[feature-catalog]] — bản đồ năng lực (nguyên tắc #6)
- [[harness-enforcement-floor]] — hậu cần enforcement (nguyên tắc #7)
- [[rule-registry]] — luật chung (nguyên tắc #3)

## Origin
- **Source:** `llmwiki/raw/fdk-stragegy.md` (bài học Đế quốc Mông Cổ → AI), distill 2026-07-02
- **Date:** 2026-07-02
