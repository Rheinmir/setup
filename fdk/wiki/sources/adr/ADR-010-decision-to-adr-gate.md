---
type: decision
title: "ADR-010: gate decision→ADR (R13) — ép quyết định kiến trúc có ADR, nhưng cho edit + xóa khi bị đè"
status: accepted
tags: [adr, gate, decision, lifecycle, r13, supersede]
timestamp: 2026-06-28
id: ADR-010-decision-to-adr-gate
---

# ADR-010: gate decision→ADR (R13) với vòng đời edit + delete-when-superseded

## Status
Accepted (2026-06-28).

## Context
Quyết định kiến trúc dễ bị "quyết miệng" rồi quên ghi ADR → bus-factor=1, người sau phá vỡ vì không biết "vì sao". Nhưng nếu ép ADR theo kiểu **bất biến cứng** (chỉ thêm, không sửa/xóa) thì ADR lỗi thời chất đống, không dọn được. Cần một gate **ép tạo** nhưng **không cứng**: cho EDIT tự do và cho XÓA khi đã có ADR mới ĐÈ.

## Decision
Thêm **R13** = validator `harness/validators/decision_adr.py` + 3 luật:
1. **decision→ADR (ép tạo):** mỗi row `Type=architecture` trong `decisions.md` phải trỏ một `ADR-N` ở cột Outcome, hoặc khai rõ `(no-adr: <lý do>)`. Quyết định kiến trúc → luôn có bản ghi.
2. **EDIT tự do:** sửa nội dung một ADR KHÔNG bao giờ bị chặn (validator chỉ soi linkage + xóa).
3. **DELETE-needs-supersede:** xóa file ADR khỏi git chỉ hợp lệ khi nó đã bị ĐÈ — nội dung cũ có `Superseded by ADR-M`, HOẶC một ADR còn lại ghi `supersedes ADR-N`. Chống mất quyết định còn sống; cho dọn ADR lỗi thời.

**Tạo ADR** vẫn qua `/docs-curate` (promote draft → `sources/adr/`) hoặc viết tay theo `sources/adr/_template.md`. **Supersede→xóa:** set status `Superseded by ADR-M` ở bản cũ (hoặc ghi `supersedes ADR-N` ở bản mới) rồi `git rm`.

**Gate:** `harness/tests/decision-adr-gate-test.sh` (5/5) wire vào CI `repo-health` + pre-commit (`decision-adr-link` trên decisions.md · `adr-delete-guard` always-run · self-test).

## Consequences
- (+) Quyết định kiến trúc luôn có ADR (hoặc khai miễn rõ ràng) — hết "quyết miệng".
- (+) ADR KHÔNG bất biến cứng: edit thoải mái, xóa được khi đã bị đè → kho ADR sạch, không phình.
- (+) Không xóa nhầm quyết định còn sống (delete-guard).
- (−) Retro-fit: vài row architecture cũ phải bổ sung ref ADR/(no-adr) một lần.

## Origin
- **Source:** goal-set phiên 2026-06-28 ("làm gate decision→ADR nhưng phải có cơ chế edit và xóa khi có cái đè"). Validator + test + wiring trong cùng commit.
- **Liên quan:** [[ADR-009-session-orientation-autoindex-forcequery]], [[rule-registry]], [[ADR-001-policy-as-source-of-truth]].
- **Date:** 2026-06-28
