---
type: source
title: "Chuẩn khoảng cách và nhịp chữ cho UI — WCAG 1.4.12 / 1.4.8 / 2.5.8, thang IBM Carbon, Tailwind, USWDS, Baymard, Butterick — đọc từ nguồn gốc để làm luật chống slop"
status: recorded
tags: [spacing, typography, line-height, wcag, design-tokens, slop]
timestamp: 2026-09-22
id: 220926-spacing-standards
---

# Chuẩn khoảng cách và nhịp chữ (22/09/2026)

User ngày 22/09/2026: "luật padding cách dòng vẫn slop và không có hệ thống gì cả, lên mạng research chuẩn đi và áp vào như một luật chống slop". Trang này ghi các con số đọc TRỰC TIẾP từ nguồn gốc (văn bản chuẩn, mã nguồn token), kèm cách mỗi chuẩn biến thành luật đo được.

## Hiện trạng đo được trước khi có luật

`scratchpad/spacing-survey.py` trên 54 trang HTML của framework: 6.423 giá trị padding/margin/gap, **92 giá trị khác nhau**, **61% nằm ngoài lưới 4px** (hay gặp: 6, 10, 14, 18px và các giá trị lẻ do `em` sinh ra như 8,8px, 6,72px, 4,48px). Line-height có 14 giá trị khác nhau, hay gặp nhất 1,35 và 1. Trang tệ nhất dùng 57 giá trị khoảng cách riêng. Nói cách khác: mỗi generator và mỗi khuôn skill tự chọn số, không có thang chung.

## Các chuẩn

**WCAG 2.2 SC 1.4.12 Text Spacing (mức AA)** — văn bản gốc trong repo `w3c/wcag`: trang không được mất nội dung hay chức năng khi người dùng đặt line-height ≥ 1,5 lần cỡ chữ, khoảng sau đoạn ≥ 2 lần cỡ chữ, letter-spacing ≥ 0,12 lần, word-spacing ≥ 0,16 lần. Chuẩn nói rõ: "Content is not required to use these text spacing values" — đây là yêu cầu trang CHỊU ĐƯỢC các giá trị đó (không cắt chữ, không chồng chữ), không phải bắt tác giả dùng chúng. Vì vậy luật "line-height nội dung ≥ 1,5" dưới đây là luật thẩm mỹ-đọc lấy cảm hứng từ con số này và từ USWDS, không phải một yêu cầu tuân thủ WCAG.

**WCAG SC 1.4.8 Visual Presentation (mức AAA)**: dòng không quá 80 ký tự (40 với chữ CJK); giãn dòng trong đoạn tối thiểu một-rưỡi; khoảng giữa đoạn lớn hơn giãn dòng ít nhất 1,5 lần.

**WCAG SC 2.5.8 Target Size (Minimum), mức AA**: vùng bấm tối thiểu 24×24 CSS px, có năm ngoại lệ (đủ khoảng cách, nằm trong dòng chữ, do trình duyệt vẽ…).

**USWDS (hệ thiết kế của chính phủ Mỹ), trang Typography**: "Use at least 1.5 times the amount of whitespace above the heading as below it"; văn bản dài có line-height ≥ 1,5; dòng 45–90 ký tự, mục tiêu 66.

**Baymard Institute**: 50–60 ký tự/dòng là tối ưu (dẫn Emil Ruder), tới 75 chấp nhận được; khuyên `max-width` khoảng `70ch`.

**Butterick, Practical Typography**: tiêu đề thuộc về phần chữ PHÍA SAU, nên khoảng dưới tiêu đề nhỏ hơn khoảng trên; khi đã có khoảng giữa đoạn thì khoảng quanh tiêu đề phải lớn hơn nữa để còn phân biệt.

**IBM Carbon, `packages/layout/src/dtcg/layout.json`**: đơn vị gốc (mini-unit) 8px; thang `spacing-01…13` = 2 · 4 · 8 · 12 · 16 · 24 · 32 · 40 · 48 · 64 · 80 · 96 · 160 px — tức lưới 8px, cho phép nửa và phần tư đơn vị (4px, 2px) ở bậc nhỏ.

**Tailwind CSS v4, `theme.css`**: `--spacing: 0.25rem` (mọi khoảng cách là bội số 4px); line-height `tight 1.25 · snug 1.375 · normal 1.5 · relaxed 1.625 · loose 2`.

## Chuẩn rút ra cho framework

- **Thang khoảng cách:** 2 · 4 · 8 · 12 · 16 · 20 · 24 · 32 · 40 · 48 · 64 · 80 · 96 px (Carbon + bậc 20 của Tailwind). Ngoại lệ hợp lệ: 0, 1px (viền, khe mảnh), giá trị `%`/`vw`/`auto`/`calc`/`clamp`.
- **Line-height:** chữ nội dung (đoạn, mục danh sách, ô bảng có câu) ≥ 1,5; tiêu đề 1,1–1,3; chữ nhỏ trong nhãn/huy hiệu một dòng được miễn.
- **Độ dài dòng:** đoạn chữ không rộng quá 80 ký tự (WCAG 1.4.8), mục tiêu khoảng 66–70 ký tự.
- **Proximity của tiêu đề:** khoảng trên tiêu đề ≥ 1,5 lần khoảng dưới (USWDS).
- **Phân tầng nhãn:** nhãn nhóm và tên trang phải khác các mục cùng cấp ở ít nhất hai trong bốn thuộc tính: cỡ chữ, độ đậm, màu, kiểu chữ (hoa/thường). Chuẩn Gestalt về tương phản/tầng bậc; phản hồi trực tiếp của user trên sidebar kanban ("cái này cần nổi bật hơn bằng màu tương phản hẳn").
- **Vùng bấm:** ≥ 24×24 px (WCAG 2.5.8).
- **Độ nổi của nhãn (luật riêng của framework, CHẶT hơn chuẩn):** nhãn nhóm/tên trang trong nav không được có tương phản thấp hơn mục liên kết (trừ nhãn tô màu nhấn đạt AA 4,5:1), và phải đậm hơn ≥ 100 hoặc to hơn mục. Nguồn: phản hồi trực tiếp của user ngày 22/09/2026 trên sidebar kanban — nhãn nhóm cũ đạt tương phản 8,4:1 (qua AA) và khác mục ở 3/4 thuộc tính nhưng user vẫn thấy chìm ("cần nổi bật hơn bằng màu tương phản hẳn"). Chuẩn Gestalt chỉ đòi "khác biệt"; ở đây đòi khác biệt THEO HƯỚNG NỔI HƠN. Review t8 ghi nhận luật này báo FAIL cả nhãn xám đậm chữ hoa 5,8:1 — đó là chủ đích.

## Bổ sung cùng ngày — tầng bậc chữ và khoảng nghỉ

- **Thang tiêu đề to → nhỏ, tên trang lớn hơn nav/tab, viết hoa chữ đầu:** yêu cầu trực tiếp của user (ảnh sidebar kanban: tên trang viết thường và không lớn hơn mục bên dưới). Ngưỡng 1,2 lần là mức chênh nhỏ nhất mắt còn phân biệt được hai tầng cỡ chữ trong một thang modular (tỉ lệ 1,2 "minor third" là bậc nhỏ nhất thường dùng).
- **Khoảng nghỉ cho mắt (`eye-rest`):** không có chuẩn công khai cho con số; dựa trên NN/g Progressive Disclosure (chỉ hiện vài thứ quan trọng nhất, phần còn lại khi yêu cầu, tối đa 2 tầng — `https://www.nngroup.com/articles/progressive-disclosure/`) và hiệu chỉnh bằng đo: theme đọc Vietcetera 30% mực, dải dày liền 212px; control-room 90%, 760px. Ngưỡng 55% / 520px là HEURISTIC của framework, mức WARN.

## Origin

- W3C WCAG, repo `w3c/wcag`: `guidelines/sc/21/text-spacing.html`, `understanding/21/text-spacing.html`, `understanding/20/visual-presentation.html`, `understanding/22/target-size-minimum.html` — tải ngày 22/09/2026 (trang w3.org trả 403 cho công cụ đọc nên đọc bản trong repo).
- IBM Carbon: `https://github.com/carbon-design-system/carbon/blob/main/packages/layout/src/dtcg/layout.json` và `packages/layout/src/index.ts` (miniUnit = 8), 22/09/2026.
- Tailwind CSS: `https://github.com/tailwindlabs/tailwindcss/blob/main/packages/tailwindcss/theme.css`, 22/09/2026.
- USWDS Typography: `https://designsystem.digital.gov/components/typography/`, 22/09/2026.
- Baymard: `https://baymard.com/blog/line-length-readability`, 22/09/2026.
- Butterick: `https://practicaltypography.com/space-above-and-below.html`, 22/09/2026.
- Material Design 3 (`m3.material.io`) và Carbon docs site render bằng JS, công cụ đọc không lấy được nội dung — không dùng làm nguồn.
