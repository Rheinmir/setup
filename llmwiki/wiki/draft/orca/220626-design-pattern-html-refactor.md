---
type: draft
title: 220626-design-pattern-html-refactor
status: done
tags: [orca-workflow, design-pattern, html, refactor]
timestamp: 2026-06-22
---

# 220626-design-pattern-html-refactor

**Status:** approved
**Sequence diagram (hoạt họa):** [html/220626-design-pattern-html-refactor-seq.html](../../../html/220626-design-pattern-html-refactor-seq.html)

## Vấn đề

Ba file `design-pattern-v{1,2,3}.html` hiện chỉ có 4 section mỗi file và prose mỏng — bỏ sót nhiều nội dung quan trọng từ MD source:

| File | Sections thiếu trong HTML |
|------|--------------------------|
| v1 (Phần 000 — Phan Văn Ngọc Thắng) | Bộ khung 5 bước tiếp cận, chi tiết từng building block, Rate Limiting |
| v2 (Phần 001 — Trần Hồng Gấm) | Rate Limiting (Token Bucket/Leaky/Sliding), Consensus Algorithms (Raft/Paxos/PBFT), Monitoring & Observability (Three Pillars, SLI/SLO/SLA) |
| v3 (Phần 002 — Bạch Hồng Vinh) | Communication Patterns (Saga, Event Sourcing), Service Discovery, Retry Exponential Backoff, Stateless Services, Event-Driven Architecture, CQRS |

## Phân công vai trò

**Claude (main):** đọc MD source + HTML hiện tại → xuất content package (text đầy đủ, bảng, code block, prose WHY/WHEN) dưới dạng plain structured text → paste vào terminal agy.

**agy (Antigravity):** nhận content package → dựng HTML hoàn chỉnh theo docs-site-macos theme. agy KHÔNG cần đọc file, chỉ cần nhận content từ Claude.

## Plan

- [ ] Task 1 (Claude): Xuất content package cho v1 — gồm 7 sections đầy đủ (bổ sung Bộ khung 5 bước, LB/DB/Cache/Queue/CDN chi tiết, Rate Limiting) + prose WHY/WHEN mỗi concept
- [ ] Task 2 (agy): Nhận content package v1 → build `design-pattern-v1.html` hoàn chỉnh (docs-site-macos, sidebar, prose)
- [ ] Task 3 (Claude): Xuất content package cho v2 — 7 sections (bổ sung Rate Limiting, Consensus Algorithms, Monitoring & Observability)
- [ ] Task 4 (agy): Nhận content package v2 → build `design-pattern-v2.html`
- [ ] Task 5 (Claude): Xuất content package cho v3 — 10 sections (bổ sung 6 patterns: Saga, Service Discovery, Retry, Stateless, EDA, CQRS)
- [ ] Task 6 (agy): Nhận content package v3 → build `design-pattern-v3.html`

## Agent Task Assignment (BẮT BUỘC với MỌI proposal)

| Task | Agent | Model | Status |
|------|-------|-------|--------|
| Task 1: Xuất content package v1 | Claude main | claude-sonnet-4-6 | done |
| Task 2: Build design-pattern-v1.html | Claude main (agy trust-blocked) | claude-sonnet-4-6 | done |
| Task 3: Xuất content package v2 | Claude main | claude-sonnet-4-6 | done |
| Task 4: Build design-pattern-v2.html | Claude main (agy trust-blocked) | claude-sonnet-4-6 | done |
| Task 5: Xuất content package v3 | Claude main | claude-sonnet-4-6 | done |
| Task 6: Build design-pattern-v3.html | Claude main (agy trust-blocked) | claude-sonnet-4-6 | done |

## Files sẽ tạo/sửa

| File | Action | Lý do |
|------|--------|-------|
| `llmwiki/html/design-pattern-v1.html` | modified | agy build lại từ content package Claude xuất |
| `llmwiki/html/design-pattern-v2.html` | modified | agy build lại từ content package Claude xuất |
| `llmwiki/html/design-pattern-v3.html` | modified | agy build lại từ content package Claude xuất |

## Yêu cầu kỹ thuật cho agy (mỗi task build)

```
Dưới đây là content package cho [v1/v2/v3]. Build một file HTML hoàn chỉnh:
- docs-site-macos theme: light glass, sidebar fixed 200px, orb background, dot-grid
- Sidebar nav list đủ tất cả sections (scroll-spy IntersectionObserver)
- Mỗi section: heading + prose 2–3 câu + table/code block render đẹp
- Glass cards cho mỗi khái niệm quan trọng
- Không thay đổi gì ngoài content đã cho

[CONTENT PACKAGE PASTE VÀO ĐÂY]
```

## Risks

- Claude phải viết prose đủ chất lượng trước khi gửi — nếu thiếu, agy build ra HTML cũng thiếu
- v3 nhiều nhất (6 patterns bổ sung) → content package lớn, cần paste đủ vào terminal agy
- agy không đọc file nguồn, chỉ nhận text → phải đảm bảo content package bao gồm toàn bộ nội dung cũ + mới

## Origin

- **Draft:** `wiki/draft/orca/220626-design-pattern-html-refactor.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
