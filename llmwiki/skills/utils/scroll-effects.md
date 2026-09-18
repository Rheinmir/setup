---
name: scroll-effects
description: >-
  Hub hiệu ứng cuộn trang — 64 bản GỐC nguyên văn (freefrontend/CodePen, MIT) ở repo Rheinmir/uiux-asset để copy nguyên file, kèm 7 hiệu ứng vanilla nhẹ: reveal-on-scroll, staggered text,
  scroll highlight, sticky shrink nav, scroll-to-top, scrollspy TOC, parallax nhẹ data-speed.
  Vanilla HTML/CSS/JS, tôn trọng prefers-reduced-motion. Gọi khi user nói "hiệu ứng scroll",
  "scroll reveal", "scroll to top", "scrollspy", "parallax nhẹ", "highlight khi cuộn", hoặc
  /scroll-effects. KHÁC `blur` (WebGL chuyển ảnh nặng GPU) và `timeline` (trục mốc thời gian) —
  đây là các hiệu ứng cuộn trang dùng hàng ngày, nhẹ, không dependency.
---

# Skill: scroll-effects

Hub hiệu ứng cuộn trang: **64 bản gốc nguyên văn** (freefrontend/CodePen, MIT) ở `Rheinmir/uiux-asset` — duyệt gallery, copy nguyên file. Kèm 7 hiệu ứng vanilla tự viết trong `assets/` cho dự án không được kéo lib ngoài.

## Bản gốc — dùng TRƯỚC (copy nguyên file, đừng viết lại)
Code gốc NGUYÊN VĂN của tác giả (CodePen public = MIT) nằm ở repo ngoài **`Rheinmir/uiux-asset`** — gallery chạy thật: https://rheinmir.github.io/uiux-asset/scroll-effects/ .
Quy trình: mở link **chạy** để xem đúng hiệu ứng → copy nguyên file `.html` (+ thư mục `_assets/` nếu file trỏ tới) vào dự án → giữ comment ghi công dòng đầu → chỉ sửa nội dung/ảnh/màu. Chạy local qua HTTP, không `file://`.
`git clone --depth 1 https://github.com/Rheinmir/uiux-asset` nếu cần cả bộ offline.

Hub: duyệt cả 64 mục ở gallery (lọc theo tên/kỹ thuật/tác giả), rồi rẽ sang skill con tương ứng.

`assets/` trong skill này chỉ là bản rút gọn vanilla tự viết — dùng khi dự án KHÔNG được kéo lib ngoài; mặc định dùng bản gốc ở trên.

## When to use
- Trang cần hiệu ứng hiện-dần khi cuộn, chữ stagger, highlight dẫn mắt, nav co lại, nút về đầu trang, mục lục bám theo section, hoặc parallax nhẹ.
- User nói "hiệu ứng scroll", "scroll to top", "scrollspy", "parallax", "reveal khi cuộn".
- KHÔNG dùng cho: chuyển ảnh điện ảnh nặng GPU (đó là `blur`), trục timeline mốc thời gian (đó là `timeline`), cuộn ngang pin-section kiểu GSAP ScrollTrigger phức tạp (vượt phạm vi skill nhẹ này — nói rõ với user).

## Assets
`assets/demo.html` (trang demo ráp sẵn cả 7) + `assets/scroll-effects.css` + `assets/scroll-effects.js` — đọc rồi ADAPT (đổi class/token theo `design.md` của dự án nếu có).

## 7 pattern (markup tối thiểu + cơ chế)

### 1. Reveal on scroll — `[data-se-reveal]`
Phần tử mờ + trượt nhẹ, hiện khi cuộn vào khung nhìn.
```html
<div data-se-reveal>Lộ dần khi cuộn tới</div>
```
`IntersectionObserver` gắn `.is-in` → CSS transition `opacity/translateY`. Tham khảo gallery scroll-effects #9 (Animated Scroll Highlight Annotations) về *trường hợp dùng*, không dùng code của họ.

### 2. Staggered text — `[data-se-stagger]`
Các dòng chữ hiện nối tiếp nhau.
```html
<h2 data-se-stagger>
  <span>Dòng một</span><span>Dòng hai</span><span>Dòng ba</span>
</h2>
```
JS gán `--i` cho mỗi `span` → CSS `transition-delay: calc(var(--i) * 90ms)`. Chỉ tách theo phần tử con có sẵn, không tự split text node (giữ DOM đơn giản, tránh lỗi a11y).

### 3. Scroll highlight — `[data-se-highlight] > mark`
Đánh dấu ý chính, vệt màu quét trái→phải khi đoạn văn vào khung nhìn.
```html
<p data-se-highlight>Đọc tới đây <mark>ý chính hiện ra</mark> rồi đọc tiếp.</p>
```
`mark` dùng `background-size: 0% → 100%` transition khi cha có `.is-in`. Dùng `<mark>` ngữ nghĩa thật, không span giả.

### 4. Sticky shrink nav — `[data-se-nav]`
Header co gọn khi cuộn xuống, phồng lại khi về đầu.
```html
<header data-se-nav class="site-nav">…</header>
```
Scroll listener (rAF-throttle) toggle `.is-shrunk` khi `scrollY > 24`. Chỉ đổi padding/font-size qua class, không set style inline từng frame.

### 5. Scroll to top — `[data-se-top]`
Nút về đầu trang, chỉ hiện sau khi cuộn qua một màn hình.
```html
<button data-se-top aria-label="Về đầu trang">↑</button>
```
Click → `window.scrollTo({ top: 0, behavior: "smooth" })` (trừ khi `prefers-reduced-motion` → `"auto"`). Ngưỡng hiện: `scrollY > innerHeight`.

### 6. Scrollspy TOC — `[data-se-toc] a[href^="#"]` + `section[id]`
Mục lục sticky, link sáng theo section đang đọc.
```html
<nav data-se-toc><a href="#s1">Mục 1</a><a href="#s2">Mục 2</a></nav>
<section id="s1">…</section><section id="s2">…</section>
```
`IntersectionObserver` với `rootMargin: "-40% 0px -55% 0px"` → link khớp nhận `.is-active`. Tham khảo gallery #19 (Auto-Generated Anchor TOC) về *ý tưởng*, code tự viết.

### 7. Parallax nhẹ — `[data-se-parallax="0.2"]`
Lớp nội dung trôi chậm hơn/nhanh hơn tốc độ cuộn.
```html
<div data-se-parallax="0.15">Trôi chậm tạo chiều sâu</div>
```
rAF loop: `translateY = (elCenter - viewportCenter) * speed`. Giá trị `speed` khuyến nghị `|v| ≤ 0.3`; vượt quá gây say chuyển động. KHÔNG dùng cho chữ nhỏ cần đọc chính xác.

## Rules
- `prefers-reduced-motion: reduce` → tắt toàn bộ: CSS ép `.is-in` hiện ngay không transition, JS bỏ smooth scroll và parallax (đã code sẵn trong assets, đừng xoá nhánh này khi adapt).
- Một `IntersectionObserver` dùng chung cho reveal + stagger + highlight + TOC (đã gộp trong `scroll-effects.js`) — đừng tạo 4 observer riêng.
- Scroll listener duy nhất, rAF-throttle — nav + top + parallax đọc chung một `scrollY` mỗi frame, không gắn 3 listener `scroll` rời.
- Verify bằng `playwright-verify`: chụp trước/sau cuộn, assert `.is-in` xuất hiện, đo không có horizontal overflow do parallax.
- Khi adapt vào dự án có `design.md`: đổi token màu/spacing, giữ nguyên tên `data-se-*` (JS bám vào chúng).

## Origin
- User chốt "làm đi hỏi nhiều quá" → thay vì bulk-copy 81 tác phẩm, viết BỘ GỐC 7 pattern generic (kỹ thuật chuẩn ngành: IntersectionObserver/scroll listener/rAF — không phải biểu đạt sáng tạo riêng của ai) để downstream tham khảo code mẫu ngay, đúng cách `blur`/`timeline` đã làm.
