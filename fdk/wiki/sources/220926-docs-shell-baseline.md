---
type: source
title: "Baseline docs-shell 22/09/2026 — trang tài liệu theo khuôn docs-site-macos thiếu quy định MUST nào, đo TRƯỚC khi lớp nền tự chèn"
status: recorded
tags: [docs-site-macos, docs-shell, baseline, html-base, sidebar]
timestamp: 2026-09-22
id: 220926-docs-shell-baseline
---

# Baseline docs-shell — đo trước khi sửa (22/09/2026)

Trang này ghi trạng thái ĐỎ của các trang tài liệu dựng theo khuôn `docs-site-macos`, đo bằng `fdk/tools/docs-shell-survey.py --all` trước khi lớp nền `html_base` được dạy tự chèn bộ khung. Kết quả: **0/6 trang đủ khung**.

## Phạm vi

Một trang được tính là docs-shell khi `<nav>` của nó có `.logo` và từ bốn link neo `#…` trở lên. Khảo sát thô ban đầu đếm mọi trang có `<nav>` (39 trang) và cho số thiếu rất lớn, nhưng phần lớn số đó là trang có sidebar RIÊNG: 19 trang đồ thị do engine orca-graph sinh (sidebar liệt kê node, không phải mục lục tài liệu), ba trang control-room, trang so sánh trước/sau, và các trang sequence dạng một màn hình. Những trang này không theo khuôn docs-site-macos nên bộ đo không hỏi chúng; áp khung tài liệu lên chúng sẽ phá bố cục riêng.

## Số đo

| Trang | Thiếu |
|---|---|
| `llmwiki/html/080926-prd-grade-fe-docs.html` | mind-map, draggable |
| `llmwiki/html/100926-harness-fixes.html` | mind-map, draggable |
| `llmwiki/html/120926-downstream-layout.html` | icon-tile, mind-map |
| `llmwiki/html/design-pattern-v3.html` | icon-tile, skip-link, main-id, favicon, mind-map, draggable |
| `llmwiki/html/index.html` | icon-tile, skip-link, main-id, favicon, scroll-spy, ripple, mind-map |
| `llmwiki/html/overstack.html` | skip-link, main-id, favicon, mind-map, draggable |

Theo quy định: mind-map 6 · draggable 4 · icon-tile 3 · skip-link 3 · main-id 3 · favicon 3 · scroll-spy 1 · ripple 1 · nav-toggle 0.

Trang người dùng chỉ ra (`120926-downstream-layout.html`) thiếu icon tile — đúng lý do sidebar "trông chán": bảy dòng chữ xám giống nhau, tiền tố số lẫn vào nhãn, mục đang chọn chỉ có nền xanh 8%.

## Hiệu chỉnh bộ đo (cùng ngày)

Hai chỗ đếm sai của bản đo đầu, sửa trong `docs-shell-survey.py` trước khi sửa trang: (1) `index.html` bị tính là docs-shell vì nav lọc thẻ của nó có bốn link `href="#"` — nay chỉ tính neo có tên; (2) mind map khuôn skill dùng `class="mm"`, bản đầu chỉ tìm chữ "mindmap" nên báo thiếu nhầm ở mọi trang. Số đúng trước khi sửa: **0/5 trang đủ khung** — icon-tile 2 · skip-link 2 · main-id 2 · favicon 2 · draggable 1 · mind-map 0. Sau khi lớp nền tự gắn: 5/5 (node t7).

## Origin

- Node t1 của graph `220926-docs-shell-kit` (PLAN `llmwiki/wiki/sources/draft/220926-docs-shell-kit-PLAN.md`).
- Lệnh đo: `python3 fdk/tools/docs-shell-survey.py --all`, chạy ngày 22/09/2026 trên working tree sau commit `2c3ea8f`.
