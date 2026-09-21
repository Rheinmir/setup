---
type: source
title: "Baseline slop 20/09/2026 — số đếm theo luật trên các trang HTML do framework sinh, ĐO TRƯỚC KHI SỬA bằng hai cổng (tĩnh + chạy thật)"
status: recorded
tags: [slop, baseline, html, frontend-antipattern, html-visual-gate]
timestamp: 2026-09-20
id: 200926-slop-baseline
---

# Baseline slop — đo trước khi sửa (20/09/2026)

Trang này ghi lại trạng thái ĐỎ của các trang HTML do generator của framework sinh ra, ngay sau khi hai cổng được viết và TRƯỚC khi bất kỳ trang nào được sửa. Lý do ghi lại: một cổng xanh ngay từ lần chạy đầu là cổng không bắt được gì; con số ở đây là bằng chứng hai cổng cắn thật, và là mốc để so khi sửa xong. Bối cảnh: user báo cùng ngày rằng framework có cơ chế bắt slop bắt buộc nhưng không tự áp lên sản phẩm của chính nó — `medic` trước đó chỉ cho cổng tĩnh soi đúng một trang nên luôn xanh.

## Cổng tĩnh — `fdk/tools/frontend-antipattern.py --all --count`

Tổng: **28 FAIL · 29 WARN trên 19 file**.

| Số finding | Mức | Luật | Số trang |
|---:|---|---|---:|
| 20 | WARN | `svg-c-title-nh-ng-kh-ng-ph-i` | 8 |
| 18 | FAIL | `c-pre-code-nh-ng-thi-u-font` | 18 |
| 6 | FAIL | `no-dark-mode` | 6 |
| 5 | WARN | `uppercase-misuse` | 5 |
| 3 | FAIL | `side-stripe` | 3 |
| 3 | WARN | `svg-s-thi-u-role-img` | 3 |
| 1 | FAIL | `gradient-text-background-cli` | 1 |
| 1 | WARN | `prose-ti-ng-vi-t-l-t-code-bl` | 1 |

## Cổng chạy thật — `fdk/tools/html-visual-gate.mjs` (Playwright, sáng và tối, offline)

**17/20 trang có lỗi.** Cột là số chỗ vi phạm; toggle ghi trạng thái nút đổi giao diện.

| Trang | Chữ chìm (sáng) | Chữ chìm (tối) | Khối dính / padding hẹp | Icon đè chữ | Sọc một cạnh | Toggle |
|---|---:|---:|---:|---:|---:|---|
| `html/overstack.html` | 33 | 19 | 0 | 2 | 0 | ok |
| `html/index.html` | 14 | 14 | 0 | 0 | 33 | MISSING |
| `html/280626-health-dashboard.html` | 8 | 8 | 0 | 0 | 6 | MISSING |
| `html/280626-skills-cheatsheet.html` | 6 | 6 | 0 | 1 | 0 | MISSING |
| `html/control-room.html` | 3 | 1 | 0 | 0 | 0 | ok |
| `html/control-room-detail.html` | 1 | 0 | 0 | 0 | 0 | ok |
| `html/control-room-kanban.html` | 0 | 0 | 0 | 0 | 60 | ok |
| `html/fdk-problem-tree.html` | 4 | 6 | 0 | 4 | 60 | MISSING |
| `html/memory-map.html` | 3 | 3 | 0 | 0 | 0 | MISSING |
| `html/skill-whiteboard.html` | 3 | 3 | 0 | 0 | 0 | MISSING |
| `html/wiki-graph-static.html` | 74 | 74 | 0 | 0 | 0 | MISSING |
| `graph/160926-theme-toggle-circle-reveal-motion.graph.html` | 0 | 0 | 0 | 0 | 0 | ok |
| `graph/180926-ship-scroll-originals.graph.html` | 1 | 0 | 0 | 0 | 0 | ok |
| `graph/190926-swh-reuse-layer.graph.html` | 0 | 0 | 0 | 0 | 0 | ok |
| `graph/190926-swh-skill-standardize.graph.html` | 1 | 0 | 0 | 0 | 0 | ok |
| `graph/200926-orca-graph-v3.graph.html` | 1 | 0 | 0 | 0 | 0 | ok |
| `graph/200926-repo-role-ship-flows.graph.html` | 1 | 0 | 1 | 0 | 0 | ok |
| `graph/200926-self-slop-gate.graph.html` | 1 | 0 | 0 | 0 | 0 | ok |
| `graph/atlas.html` | 0 | 0 | 0 | 0 | 0 | ok |
| `html/170926-orca-graph-gates-architecture.html` | 5 | 4 | 1 | 4 | 0 | ok |

Số sọc bị chặn trần 60 mỗi trang trong cổng, nên `60` nghĩa là "ít nhất 60". Trang `170926-orca-graph-gates-architecture.html` là sơ đồ do renderer archify sinh, đưa vào để có mốc cho việc sửa ở fork.

## Ảnh trước

Bộ ảnh chụp cùng lúc với phép đo nằm ở `scratchpad/slop-before/` (mỗi trang hai ảnh sáng và tối, khung 1360×900). Thư mục này không track; trang so sánh trước/sau của Task 12 nhúng lại các ảnh cần thiết.

## Origin

- Node t3 của graph `200926-self-slop-gate` (PLAN `llmwiki/wiki/sources/draft/200926-self-slop-gate-PLAN.md`).
- Dữ liệu thô: `scratchpad/slop-before/static.txt` và `scratchpad/slop-before/visual.json`, sinh ngày 20/09/2026 bằng đúng hai lệnh ghi ở tiêu đề mục.
