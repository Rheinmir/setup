---
type: concept
title: Outer Harness — distill + council evaluation (overstack vs 5 trụ cột)
status: active
tags: [outer-harness, council, evaluation, governance, cost-attribution, audit, roadmap]
timestamp: 2026-06-30
---

# Outer Harness — distill + đánh giá bằng council

Trang này chưng cất khung tư tưởng **Outer Harness** (bài của Phúc, `llmwiki/raw/outer-harness.md`) và ghi lại kết quả một phiên `/council` (3 ghế độc lập → blind peer-rank → chairman) đánh giá: (1) luận điểm vững tới đâu, (2) framework overstack/llmwiki đã hiện thực được trụ cột nào, (3) nên áp gì trước. Mục đích là một **bản đồ gap + roadmap** cho chính framework này, không phải tóm tắt lại bài báo.

## 1. Khung tư tưởng (distill những điểm "đắt")

Luận điểm gốc: `Agent = Model + Harness` (LangChain) — mọi thứ không-phải-model là Harness. Harness chia hai lớp theo ẩn dụ "wiring harness" ô tô:

- **Inner Harness** — system prompt lõi, sandbox, execution engine. Provider (Anthropic/OpenAI/Cursor) đã đổ hàng chục triệu đô tối ưu; bản leak của Claude Code là ví dụ chuẩn mực. **Đừng rebuild.**
- **Outer Harness** — mang DNA tổ chức: context doanh nghiệp, quy trình duyệt, tiêu chuẩn chất lượng, cách chia tri thức. Provider không làm thay vì họ không biết công ty bạn vận hành ra sao.

Nghịch lý cốt lõi: tổ chức chi hàng trăm ngàn đô cho Inner (token), còn Outer — thứ *thực sự quyết định chất lượng output* — thì nằm rải rác trên laptop từng người; scale lên 50→1000 engineer là vỡ.

Hai mindset xương sống: **process-centric** (human và agent đều là *node* trên cùng một pipeline; quy trình quyết định context nào inject / output nào pass) và **data-driven** (mọi thao tác sinh structured data → visibility → improvement).

Năm trụ cột: **(1) Cost Attribution** — log mọi run kèm metadata, break down theo team/feature, auto-alert + hard-stop budget. **(2) Multi-layer Knowledge Flow** — context hierarchy 5 tầng có ownership; top-down policy inheritance + bottom-up skill promotion. **(3) Task Tracking** — lifecycle + approval gate + audit trail. **(4) Quality Gates** — separation of duties: kẻ viết code không được là kẻ duy nhất judge code mình (agent có thể comment-out test để pass nhanh). **(5) Audit & Analytics** — append-only log + hash chain cho tamper-evidence; điểm hội tụ của analytics.

## 2. Đánh giá của council

**Phương pháp:** 3 ghế với lăng kính phân biệt (skeptic / enterprise-architect / pragmatic), blind peer-rank với anchor-guard (seed 42), chairman tổng hợp. *Caveat: phiên chạy single-provider (cả 3 ghế đều Claude vì model ngoài không reachable ở máy này), nên độ đa dạng model giảm — nhưng giao thức blind-rank và bảng dissent vẫn giữ.* Đồng thuận tuyệt đối: ghế enterprise-architect thắng (mean rank 1.0, cả 3 judge xếp #1).

### Điểm SẮC (cả 3 đồng ý)
Lằn Inner/Outer là một đường **build-vs-buy** sạch; "xây lớp org-DNA mà provider không bao giờ làm thay" là insight thật và non-obvious. Hệ quả mạnh nhất: coi human + agent là *node hoán đổi được* cho phép **tái dùng SDLC controls cũ** (separation-of-duties, audit, change-management) thay vì dựng một bộ governance AI song song — đây là cách qua SOC2/ISO mà không gấp đôi headcount. Quan sát "agent comment-out test để qua gate" là đúng thực nghiệm và là chỗ đáng đầu tư rigor.

### Điểm YẾU / over-claim
- `Agent = Model + Harness` là **tautology** đội lốt insight — đúng với mọi phần mềm (`program = logic + runtime`).
- "Provider sẽ KHÔNG BAO GIỜ xây Outer" **quá lời**: cost dashboard, audit log, approval workflow, policy layer đã ship (Bedrock/Vertex). Moat đang co — đừng tay-xây thứ sắp bị commoditize trong ~18 tháng.
- Lằn Inner/Outer **mờ hơn** bài vẽ: RAG, tool-routing, guardrails nằm vắt qua cả hai; "đừng rebuild Inner" có thể thành bẫy vendor lock-in ở quy mô lớn.
- "Mọi thao tác sinh data" là **data-lake fallacy**: emit ≠ value nếu không có owner + vòng lặp ra quyết định đóng lại.
- **Hash-chain tamper-evidence là theater** trừ khi quyền-ghi nằm NGOÀI privilege của agent và được neo ngoại bộ; dưới ~10 engineer thì chỉ là compliance theater (chi phí thật, không có auditor để phục vụ).
- `coverage ≥ 80%` / SonarQube là CI hygiene tiền-LLM đổi nhãn; 80% là con số phù phiếm và gameable.
- Mô hình knowledge 5 tầng là nơi **90% công sức thật** nằm, nhưng bài coi như một bullet, thiếu RACI + conflict-resolution.

## 3. overstack/llmwiki ánh xạ vào 5 trụ cột

| Trụ cột | Trạng thái | Căn cứ |
|---------|-----------|--------|
| **2 — Knowledge Flow** | ✅ STRONG (center of gravity) | [[fdk]] + llmwiki hierarchy + CLAUDE.md top-down + `fdk/CAPABILITIES.md` + promote bottom-up (`propose`→gate, `failure-flywheel`, `new-skill`) |
| **4 — Quality Gates** | 🟡 PARTIAL→STRONG | `council` (author≠judge) + `trace-grader` (chấm *đường đi*, bắt "corrupt success" — hơn SonarQube) + `wikieval` (golden CI-blocking) + `verify-before-commit`. Thiếu: một cổng CI ngôn-ngữ độc lập (coverage/lint) |
| **3 — Task Tracking** | 🟡 PARTIAL | `propose`→gate→dispatch có approval, nhưng **không có task ID bền / lifecycle store / audit trail bất biến** |
| **1 — Cost Attribution** | 🔴 MISSING (gap lớn nhất) | RTK `gain` đo *tiết kiệm* token, không phải ledger cost-per-run theo feature kèm budget alert/hard-stop |
| **5 — Audit & Analytics** | 🔴 PARTIAL/MISSING | Mindset data-driven có (`failure-flywheel` + traces), nhưng `log.md` **mutable**, chưa có append-only convergence log |

## 4. Roadmap nên áp (đã calibrate theo scale thật — framework cá nhân, không phải org 500 người)

1. **Per-run metadata JSONL** — append `{run id, tokens, skill, verdict, project}` vào một file append-only. Mở khóa Trụ 1 **và** gieo mầm Trụ 5 với chi phí gần 0. Payoff cao nhất. (Hạ tầng [[feature-catalog]] đã có **code-logger** ghi `events.jsonl` bằng hook — mở rộng schema để thêm token/cost là đường ngắn nhất.)
2. **Gắn task ID vào `propose`→gate** (Trụ 3) — biến luồng duyệt đang có thành traceable. Sửa nhỏ, visibility lớn.
3. **Một cổng CI độc lập** (coverage/lint) cắm vào `verify-before-commit` — đóng nốt gap Trụ 4.
4. **Khoan làm:** hash-chain audit + budget hard-stop. Thuần chi phí, vô ích cho tới khi có auditor thật hoặc đồng đội tiêu tiền của bạn. Lấy **mindset** data-driven khắp nơi; lấy **cơ chế** enterprise chỉ khi có stakeholder thật đòi.

## Notes
- Transcript đầy đủ (answers / blind packet / rankings / dissent / chairman) của phiên council nằm ở scratchpad phiên (`scratchpad/council-run/run/`), không commit vào wiki.
- Liên quan: [[feature-catalog]] (vì sao `council`/`trace-grader`/`wikieval`/`failure-flywheel` tồn tại), [[fdk]] (front-door dev framework), [[harness-enforcement-floor]] (vì sao CI mới là sàn thật — trùng kết luận với Trụ 4).

## Origin
- **Source:** `llmwiki/raw/outer-harness.md` — bài "Outer Harness: Tại sao Process và Data quan trọng hơn Agent" (Nguyễn Trọng Phúc, Apr 2026). Distill + đánh giá theo yêu cầu phiên 2026-06-30.
- **Method:** phiên `/council` 3 ghế (skeptic/enterprise-architect/pragmatic) → blind peer-rank seed 42 → chairman; chạy single-provider (caveat ghi ở Phần 2).
- **Date:** 2026-06-30
- **Liên quan:** [[feature-catalog]], [[fdk]], [[harness-enforcement-floor]].
