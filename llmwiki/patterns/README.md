# Pattern Library — kho pattern tham chiếu (BẢO VỆ)

Kho **pattern + anti-pattern** tham chiếu cho các vai trò khi làm việc trên/với overstack:
frontend, backend, adapter (build-now-adapt-later), system-design, BA, tester, PM — cùng
`loops.md` (thư viện vòng lặp agent). Đọc để tham khảo; **không phải** chỗ agent tự ý sửa.

## Mức bảo vệ — "raw nhưng thấp hơn một bậc"
- `raw/` = **không bao giờ** ghi (R1). Folder này **thấp hơn một bậc**: chỉ được sửa **khi user cho phép**.
- Một agent **KHÔNG được tự ý** (vô tình) sửa nội dung file trong `llmwiki/patterns/`. Mọi `Write`/`Edit`
  vào đây bị **R14 patterns-protected** (PreToolUse hook) **chặn**, trừ khi có tín hiệu mở khoá của user.
- **Mở khoá để sửa (user cho phép):** đặt biến môi trường `LLMWIKI_PATTERNS_UNLOCK=1` cho phiên/đại lý
  rồi mới sửa. Không có nó → mọi sửa đổi bị từ chối (fail-safe: thà chặn nhầm còn hơn sửa nhầm kho tham chiếu).

## Cấu trúc
| File | Vai trò |
|------|---------|
| `frontend.md` | UI/FE — Atomic Design, signals, server components, container queries |
| `backend.md` | BE — BFF, idempotency, outbox/event-driven, cache-aside |
| `adapter.md` | build-now-adapt-later — one-config boundary, verified flag, ADAPT-CHECKLIST |
| `system-design.md` | scaling, cache, queue, shard/replica, idempotency, backpressure |
| `ba.md` | Business Analyst — spec-driven, Given/When/Then, traceability |
| `tester.md` | QA — test pyramid, golden/baseline, trajectory grading, eval gate |
| `pm.md` | Product — thin slice, outcome>output, kill-criteria, BNAL sequencing |
| `loops.md` | thư viện vòng lặp agent (crawl từ signals.forwardfuture.com/loop-library) |

Mỗi file: `## Patterns` (When · Do · Why) + `## Anti-patterns` (Smell · Why bad · Instead) + `## Origin`.

## Trạng thái (build-now-adapt-later)
Nội dung hiện **seeded best-guess** (sinh từ `/last30days` research + repo Rheinmir star + crawl),
**chờ user curate** — xem `harness/pattern-library.config.yaml` (`verified: false`). Khi user duyệt xong
một vai trò, cập nhật trạng thái ở config đó. Adapter = chính việc curate nội dung (phán đoán của user).

## Origin
- Tạo theo goal-set 2026-06-29 ("kho pattern tham chiếu ... bảo vệ chỉ sửa khi tôi cho phép, có pattern + anti-pattern").
- Seed: `/last30days` research; Rheinmir starred (gstack roles, system-design-notes, SkillSpector); crawl loop-library.
