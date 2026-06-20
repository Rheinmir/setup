---
type: draft
title: 180626-orca-framework-overview
status: proposed
tags: [docs-site-macos, output-report]
timestamp: 2026-06-18
---

# 180626-orca-framework-overview

**Status:** proposed

## What
Trang HTML single-file giới thiệu toàn bộ repo `rheinmir/setup#orca` (đặt tên là **llmwiki** — framework vận hành AI-agent, phân phối dạng template) với grid 24 skill phân nhóm theo màu + legend giải thích màu.

## Output
- Tên gọi chốt: **llmwiki** — gọi là *framework* (bản chất: luật + loop + runtime) phân phối dưới dạng *template* (copy-in + npx skills add).
- 24 skill chia 6 nhóm màu: Wiki Loop (xanh dương·3), Dev Loop (xanh ngọc·4), Onboard & Setup (chàm·3), Orchestrate·Orca (lục·3), Caveman·Token (cam·7), Utils·Output (hồng·4). `orca-onboard` xếp vào Orchestrate.
- Trang gồm: hero, định nghĩa framework-vs-template, diagram 4-vòng-lặp (draggable), skill-grid + legend italic, 4 bước setup, cây thư mục.
- Đã chạy `npx skills add rheinmir/setup#orca --global --all` (các skill PromptScript không hỗ trợ global install — bỏ qua, phần còn lại cài OK).

## Files
| File | Action |
|------|--------|
| `llmwiki/html/180626-orca-framework-overview.html` | created |

## Notes
- Invoked via: `/docs-site-macos` skill
- Preview: `http://localhost:8765/llmwiki/html/180626-orca-framework-overview.html`
- Self-contained: 0 external request; liquid-glass + draggable SVG diagram + ripple + scroll-spy.

## Origin
- **Draft:** `wiki/sources/draft/180626-orca-framework-overview.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
