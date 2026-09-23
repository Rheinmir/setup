---
type: draft
title: "Đề xuất (chờ duyệt) — minimalism mặc định cho mọi HTML framework sinh ra và ở máy khách: màn đầu chỉ tóm tắt, ấn vào mới hiện; luật 'phải có khoảng nghỉ cho mắt' đã vào cổng và audit"
status: proposed
tags: [proposal, minimalism, progressive-disclosure, eye-rest, html-base, docs-site-macos, qc-uiux, downstream]
timestamp: 2026-09-22
---
# sĐề xuất 220926 — minimalism mặc định, ấn vào mới hiện

User ngày 22/09/2026 qua `/fdk`: "toàn framework và downstream với mặc định thiết kế theo kiểu minimalism đi, ấn vào thì mới hiện ra chứ cứ maximalism mọi lúc thế này trong mắt không có khoảng nghỉ nào", rồi "thêm luật vào frontend mặc định của framework và cả phần audit nữa là phải có khoảng nghỉ cho mắt", "các cấp header phải thêm chuẩn từ to tới nhỏ", "còn không thì là yêu cầu đặc biệt", "quét lại hết luôn".

## Đã làm (theo chỉ thị trực tiếp, không chờ duyệt)

Bốn luật mới trong cổng chạy thật `fdk/tools/html-visual-gate.mjs`, nối vào audit `qc-uiux` (mục Visual hierarchy) và khuôn `docs-site-macos`:

- `eye-rest` (WARN) — khoảng nghỉ cho mắt: màn đầu ≤ 55% là chữ/khối, không dải dày liền &gt; 520px thiếu khoảng trống ≥ 24px. Ngưỡng heuristic hiệu chỉnh bằng đo (theme đọc Vietcetera 30%/212px; control-room 90%/760px).
- `heading-scale` (FAIL) — các cấp tiêu đề to → nhỏ, không nhỏ hơn chữ nội dung; lớp font đặt mặc định h1 32 · h2 24 · h3 20 · h4 17px (độ ưu tiên 0).
- `title-scale` (FAIL) — tên trang ≥ 1,2 × mục nav/tab.
- `sentence-case` (FAIL) — viết hoa chữ đầu tiêu đề, nhãn, nút, tab, mục nav; công cụ vá tự sửa trong HTML, lớp nền thêm `::first-letter` cho tiêu đề JS sinh; `data-case="keep"` giữ tên riêng.
- Yêu cầu đặc biệt: `<meta name="overstack-exempt" content="…" data-reason="…">`.

## Hiện trạng

Đo màn đầu 13 trang: không trang nào có phần gập (\`

<details class="orca-details">
<summary>\`); trung vị 1.744 ký tự, 11 hộp, 7 chip. Quét luật \`eye-rest\` trên 57 trang: 47 trang trượt.</summary>



</details>

## Chuẩn

NN/g, Progressive Disclosure (`https://www.nngroup.com/articles/progressive-disclosure/`): ban đầu chỉ hiện vài thứ quan trọng nhất; phần chuyên sâu hiện khi người dùng yêu cầu; phải đưa trước mọi thứ người dùng cần thường xuyên; lối vào phần ẩn rõ và có nhãn; quá 2 tầng thì người dùng lạc.

## Phần chờ duyệt — thiết kế lại để hết nợ `eye-rest`

1. Màn đầu = tên + một câu + tối đa 3–5 con số/trạng thái + lối vào các phần.
2. Mỗi khối có trạng thái thu gọn (mặc định) và mở, dùng `<details>`/`<dialog>`; tối đa 2 tầng; nhớ lựa chọn theo trang.
3. Thẻ một cỡ, bấm mới xem chi tiết (như thẻ kanban scenario-console).
4. Ít màu, ít khung — khoảng trắng là cách phân nhóm chính.
5. Áp cho: overstack, control-room/kanban/detail, health, problem-tree, memory-map, cheatsheet, engine orca-graph, skeleton `orca-onboard`, template problem-tree; nâng `eye-rest` lên FAIL khi nợ về 0.

**Cần user chọn mức:** (a) nhẹ — chỉ gập phần chi tiết dài; (b) vừa — màn đầu thành tóm tắt, mọi khối thu gọn mặc định (đề xuất); (c) mạnh — mỗi trang chỉ còn một màn tổng quan, mọi thứ khác qua popup/trang con. Cùng lúc chốt họ font (Lexend Deca hay Be Vietnam Pro) vì hai việc chạm cùng mọi generator.

## Origin

- Các tin nhắn user ngày 22/09/2026 (trích ở đầu trang), ảnh sidebar kanban và thanh trên scenario-console.
- Số đo: `scratchpad/probe-density.mjs`, `scratchpad/probe-rest.mjs`, quét `html-visual-gate.mjs` 57 trang cùng ngày.
- Chuẩn: NN/g Progressive Disclosure; `fdk/wiki/sources/220926-spacing-standards.md`.

