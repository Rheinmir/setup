---
type: decision
title: "ADR-001: policy.yaml là nguồn chân lý + thin-adapter/thick-policy"
status: accepted
tags: [adr, harness, policy, thin-adapter, R11]
timestamp: 2026-06-27
id: ADR-001-policy-as-source-of-truth
---

# ADR-001: policy.yaml là nguồn chân lý — thin adapter, thick policy

## Status
Accepted (2026-06-27)

## Context
Harness phải gác cùng bộ luật cho NHIỀU vendor (claude, opencode, antigravity, cursor, codex, kiro) + pre-commit/CI. Nếu mỗi vendor mã hóa luật riêng → drift, sửa luật phải sửa N nơi. Mục tiêu framework: scale người (bus-factor=1 → 0), người mới đọc MỘT chỗ là hiểu luật.

Thực tế còn rò: một số luật (R3/R4/R8/R10) đang wire trong `gen-converters.py` (hook) thay vì `policy.yaml` → "nguồn chân lý duy nhất" chưa trọn (xem [[rule-registry]]).

## Decision
- `harness/poc-vendor-neutral/policy.yaml` là **nguồn chân lý máy-đọc**. Lõi `llmwiki-validate.py` + `gen-converters.py` đọc nó; adapter mỗi vendor chỉ là **dây nối MỎNG** sinh ra từ policy — KHÔNG mã hóa luật riêng.
- **Thêm luật = sửa policy.yaml**, KHÔNG sửa code adapter, khi luật biểu diễn được bằng `kind` đã có (`deny_write`, `require_section`, `forbid_root`, `conditional_require`, `require_frontmatter`, `process_gate`).
- Chỉ khi cần `kind` mới mới đụng lõi `llmwiki-validate.py`.

## Case study — R11 (seq-html-glass-style)
Luật "seq HTML phải glass docs-site-macos" thêm vào **chỉ bằng 1 entry policy.yaml** dùng `conditional_require` có sẵn → 0 dòng code adapter. `gen-converters` tự propagate statement sang cursor/codex/kiro. Đây là bằng chứng sống cho "thick policy, thin adapter".

## Consequences
- (+) Sửa luật 1 chỗ; mọi vendor đồng bộ qua regen.
- (+) Người mới đọc policy.yaml + [[rule-registry]] là nắm luật.
- (−) Còn nợ: R3/R4/R8/R10 phải kéo về policy để hết rò (T1 của [[270626-framework-gap-backfill]]).
- (−) `kind` mới vẫn phải đụng lõi — chấp nhận, hiếm.

## Origin
- **Decision rút từ:** chat Gemini (design philosophy) + thực thi R11 trong phiên 2026-06-27.
- **Nguồn:** `policy.yaml`, `gen-converters.py`, [[rule-registry]], [[270626-framework-gap-backfill]].
