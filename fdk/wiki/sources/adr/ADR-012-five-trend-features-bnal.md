---
type: decision
title: "ADR-012: 5 trend 2026 → 5 chức năng qua build-now-adapt-later (core now, adapter verified:false)"
status: accepted
tags: [adr, build-now-adapt-later, bnal, trends, observability, security, spec-driven, self-improving, quarantine]
timestamp: 2026-06-29
id: ADR-012-five-trend-features-bnal
---

# ADR-012: 5 trend 2026 → 5 chức năng, dựng bằng build-now-adapt-later

## Status
Accepted (2026-06-29).

## Context
Một lượt quét xu hướng 30 ngày (qua skill `last30days`, đường WebSearch-fallback vì engine chưa cài) chỉ ra **5 hướng** mà framework chưa có nhưng hợp kiến trúc: self-improving "context playbook", agent observability (OpenTelemetry GenAI), tool/egress security, spec-driven development, và component-scoped hooks.

Mỗi hướng đều dính một **ẩn số** không thể chốt ngay:
- ngưỡng "trace nào là THẮNG" + model distill (chỉ biết khi có dữ liệu chấm thật),
- allow-list egress thật của từng dự án (mỗi dự án mỗi khác),
- tên thuộc tính OTel GenAI (conventions còn *experimental* 2026),
- schema spec đồng thuận (stakeholder quyết),
- tín hiệu "skill nào đang active" (host chưa phơi ra).

Dựng "đầy đủ" thì kẹt vào 5 ẩn số này; bỏ qua thì mất 5 hướng giá trị.

## Decision
Dựng cả 5 bằng **`/build-now-adapt-later`**: phần **tất định** (parse, đếm, dựng span, so khớp, dispatch) viết + test **ngay** (mỗi feature có `--self-test`); mỗi **ẩn số** bị nhốt sau **MỘT** config `harness/<name>.config.yaml` mang `verified: false` + comment `ASSUMPTION` + một `# ADAPT-CHECKLIST` (đường hoàn tất một-file). 5 feature:

| Feature (`harness/scripts/`) | Core tất định (built now) | Adapter quarantined (verified:false) |
|---|---|---|
| `success-flywheel.py` | gom win by-code, xếp hạng, draft playbook stub (gương DƯƠNG của failure-flywheel) | `success_threshold`, `recurrence_threshold`, `distill.model:null` |
| `egress-guard.py` | parse Bash/MCP, match allow-list + injection-pattern, exit 0/2 fail-open | `egress.allow_domains` (rỗng), `mode:warn`, patterns |
| `trace-otel.py` | audit phẳng → span OTel-GenAI, truy nhân-quả vs golden | `attribute_map` (experimental), `regression.threshold` |
| `spec-gate.py` | check spec đủ section, conformance "change cite spec?" | `required_sections`, `conformance.mode:advisory` |
| `scoped-hooks.py` | parse frontmatter `guard:`, dispatch khi skill active | `activation.detector`, `frontmatter_key` |

**Fail-safe dưới `verified:false`:** mặc định không phá phiên — egress-guard ở `mode:warn` (phát hiện + cảnh báo, exit 0), spec-gate ở `advisory`, scoped-hooks không-quyết-được → dispatch rỗng. Enforce (block) chỉ bật SAU khi adapter được hiệu chỉnh + `verified:true`.

**Giữ trung thực:** 10 self-test BNAL (5 cũ verified:true + 5 mới verified:false) + leak-gate `adapt-registry --check` (mỗi `verified:false` phải có ADAPT-CHECKLIST, ẩn số không rò ra ≥2 file) đều wire vào `fdk-gate`. `GENERIC_KEYS` của adapt-registry mở rộng thêm `recurrence_threshold`/`prompt` vì success-flywheel ↔ failure-flywheel là adapter song song dùng chung schema-key (không phải leak).

## Consequences
- (+) 5 chức năng **chạy được ngay** (core đã test), không kẹt chờ 5 ẩn số.
- (+) Hoàn tất mỗi cái = sửa **một** file config + `verified:true` (ADAPT-CHECKLIST sẵn); leak-gate + self-test giữ cờ `verified` không nói dối.
- (+) Hai trend bám thẳng `harness-local` (ADR-011): egress-guard hợp làm `P-rule` của dự án; scoped-hooks nối thêm tầng component (global→project→component).
- (−) Tới khi `verified:true`, security/spec **chỉ advisory** — chưa chặn; phải nói rõ, đừng trình "guess" như đã verified.
- (−) Thêm 5 script + 5 config + 5 metric file (gitignored) để bảo trì.

## Origin
- **Source:** goal-set phiên 2026-06-29 ("/build-now-adapt-later 5 hướng này thành 5 chức năng") sau lượt quét trend (goal trước: "dùng /last30days tìm 5 trend chưa có"). Code + self-test + wiring cùng commit.
- **Liên quan:** [[build-now-adapt-later]] (skill nền), [[ADR-011-project-local-harness]] (egress/scoped-hooks bám vào), [[harness-enforcement-floor]], [[failure-flywheel]] (gương âm của success-flywheel).
- **Date:** 2026-06-29
