---
type: decision
title: "ADR-014: kho pattern tham chiếu BẢO VỆ (llmwiki/patterns/) + R14 patterns-protected"
status: accepted
tags: [adr, pattern-library, R14, protected, build-now-adapt-later, roles, anti-pattern]
timestamp: 2026-06-29
id: ADR-014-protected-pattern-library
---

# ADR-014: kho pattern tham chiếu bảo vệ + R14 patterns-protected

## Status
Accepted (2026-06-29).

## Context
User cần một **kho pattern + anti-pattern** tham chiếu cho các vai trò làm việc trên overstack
(frontend, backend, adapter/BNAL, system-design, BA, tester, PM) + thư viện vòng lặp agent —
như một phần của `llmwiki/` để tham khảo. Yêu cầu bảo vệ đặc thù: **"raw/ nhưng thấp hơn một
bậc"** — `raw/` không bao giờ ghi (R1); kho này **chỉ được sửa KHI user cho phép**, agent
**không tự ý** (vô tình) sửa nội dung. Có pattern thì có cả anti-pattern.

## Decision
- **Folder `llmwiki/patterns/`** (đi cùng template): `README.md` + một file mỗi vai trò
  (`frontend/backend/adapter/system-design/ba/tester/pm.md`) + `loops.md`. Mỗi file:
  `## Patterns` (When · Do · Why) + `## Anti-patterns` (Smell · Why bad · Instead) + `## Origin`.
- **R14 patterns-protected** = validator `harness/validators/patterns_guard.py` wired vào
  `PreToolUse` (write + bash). Mọi `Write`/`Edit`/bash-ghi vào `protected_dir` bị **chặn (exit 2)**
  trừ khi user **mở khoá** bằng env `LLMWIKI_PATTERNS_UNLOCK=1`. Đọc thì luôn cho. Fail-safe:
  thà chặn nhầm còn hơn sửa nhầm kho tham chiếu. Khai ở cả 2 policy (prod list + poc dict, parity 14=14).
- **build-now-adapt-later:** folder + guard + cấu trúc là **tất định, built now** (test
  `patterns-guard-test.sh` 7/7, CI). Ẩn số = **nội dung seeded có canonical chưa** — đó là việc
  curate của user, nên `harness/pattern-library.config.yaml` mang `verified: false` +
  `content_status: seeded` + ADAPT-CHECKLIST (user duyệt từng vai trò → flip).
- **Seed nội dung:** `/last30days` research + repo Rheinmir star (gstack roles, system-design-notes,
  SkillSpector anti-pattern) + **crawl** `signals.forwardfuture.com/loop-library` (70 loop → `loops.md`).

## Consequences
- (+) Kho tham chiếu sống cùng template, có cả pattern lẫn anti-pattern, **không bị agent sửa bừa**.
- (+) Mở khoá rõ ràng (env) khi user thật sự muốn sửa — không phải hardcode read-only.
- (+) Nhiều pattern soi gương chính overstack (adapter=BNAL, tester=wikieval/trace-grader/council,
  ba=spec-gate, pm=BNAL/failure-flywheel) → tài liệu tự nhất quán với framework.
- (−) Nội dung đang `verified:false` (seeded) — phải nói rõ "chờ user curate", đừng coi là chân lý.
- (−) Thêm một rule (R14) + folder để bảo trì; sửa kho phải nhớ đặt env unlock.

## Origin
- **Source:** goal-set 2026-06-29 ("kho pattern tham chiếu ... bảo vệ chỉ sửa khi tôi cho phép,
  pattern + anti-pattern; /last30days + repo star Rheinmir + /build-now-adapt-later"). Crawl test
  cùng phiên qua `/web-crawl`.
- **Liên quan:** [[build-now-adapt-later]], [[harness-enforcement-floor]] (R14 là một rail mới),
  [[ADR-012-five-trend-features-bnal]] (adapter pattern), [[rule-registry]].
- **Date:** 2026-06-29
