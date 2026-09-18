---
name: mask-reveal-transition
description: Chuyển/lộ ảnh qua mask hữu cơ dạng vòng loang mực (ink-splatter/blob, `mask-image` radial-gradient động theo scroll progress) hoặc pin split-screen sticky (ảnh cố định bên trái, text cuộn bên phải, đổi ảnh qua mask khi panel active đổi). Bản gốc nguyên văn (Ink Transition, Pinned Split-Screen…) ở repo Rheinmir/uiux-asset; assets/ là bản vanilla CSS mask nhẹ, không WebGL. Gọi khi user nói "mask reveal", "ink transition", "chuyển ảnh qua mask", "split-screen sticky pin", "blob reveal effect", "vết mực loang", "pin ảnh cố định cuộn chữ", hoặc /mask-reveal-transition. KHÁC `skills/scroll-effects` (reveal đơn giản opacity/translate, KHÔNG có mask hình dạng) và `skills/blur` (shader WebGL nặng GPU cho chuyển ảnh toàn màn hình — đây là CSS `mask-image` nhẹ, không cần Three.js/canvas).
---

# Skill: mask-reveal-transition

Component vanilla HTML/CSS/JS — ảnh lộ ra qua một mask hình dạng hữu cơ (vòng loang mực, tâm cố định, bán kính tăng dần) thay vì crossfade/opacity thường. Hai biến thể dùng chung một cơ chế nền: đo tiến trình cuộn TRONG section bằng `getBoundingClientRect()`, map về 0..1, rồi ghi bán kính loang lên CSS custom property.

## Bản gốc — dùng TRƯỚC (copy nguyên file, đừng viết lại)
Code gốc NGUYÊN VĂN của tác giả (CodePen public = MIT) nằm ở repo ngoài **`Rheinmir/uiux-asset`** — gallery chạy thật: https://rheinmir.github.io/uiux-asset/scroll-effects/ .
Quy trình: mở link **chạy** để xem đúng hiệu ứng → copy nguyên file `.html` (+ thư mục `_assets/` nếu file trỏ tới) vào dự án → giữ comment ghi công dòng đầu → chỉ sửa nội dung/ảnh/màu. Chạy local qua HTTP, không `file://`.
`git clone --depth 1 https://github.com/Rheinmir/uiux-asset` nếu cần cả bộ offline.

| Pen gốc — tác giả | Link |
|---|---|
| Ink Transition Scroll Effect — iamryanyu | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/ink-transition-scroll-effect.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/ink-transition-scroll-effect.html) |
| Pinned Split-Screen Mask Reveal — gridmorphic | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/pinned-split-screen-mask-reveal.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/pinned-split-screen-mask-reveal.html) |
| Parallax Jungle Leaves Reveal — Mamboleoo | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/parallax-jungle-leaves-reveal.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/parallax-jungle-leaves-reveal.html) |

`assets/` trong skill này chỉ là bản rút gọn vanilla tự viết — dùng khi dự án KHÔNG được kéo lib ngoài; mặc định dùng bản gốc ở trên.

## When to use
- Chuyển ảnh nghệ thuật/portfolio kiểu "vết mực loang" đồng bộ theo cuộn (không phải crossfade phẳng).
- Layout case-study/portfolio 2 cột: ảnh cố định bên trái, đoạn văn cuộn bên phải, ảnh đổi theo đoạn đang đọc.
- KHÔNG dùng cho reveal đơn giản (mờ + trượt nhẹ khi vào viewport) — đó là `skills/scroll-effects` pattern #1, không có mask hình dạng.
- KHÔNG dùng cho chuyển ảnh toàn màn hình kiểu zoom-blur nặng GPU — đó là `skills/blur` (Three.js/shader). Skill này chỉ CSS `mask-image`, không canvas/WebGL.

## Assets
`assets/demo.html` + `assets/mask-reveal-transition.css` + `assets/mask-reveal-transition.js` — đọc rồi ADAPT (đổi ảnh, `--mrt-edge` độ mềm viền, nội dung panel).

## Cơ chế nền chung
Với mỗi section (`[data-mrt-blob]` hoặc `[data-mrt-split]`): 2 ảnh xếp lớp tuyệt đối trong cùng khung — ảnh **dưới** (z-index thấp, luôn hiện sẵn) và ảnh **trên** (z-index cao, mang mask). Ảnh trên có
```css
mask-image: radial-gradient(circle at 50% 50%, transparent 0, transparent var(--mrt-r), black calc(var(--mrt-r) + var(--mrt-edge)), black 100%);
```
— vùng trong bán kính `--mrt-r` **trong suốt** (ảnh trên biến mất tại đó → lộ ảnh dưới), vùng ngoài `--mrt-r + --mrt-edge` vẫn **đặc** (ảnh trên che kín). `--mrt-r` tăng dần = vòng trong suốt loang rộng ra = ảnh dưới "loang" ra từ tâm, đúng cảm giác vết mực — không phải chiều ngược lại (chấm đặc lớn dần), vì như vậy sẽ che dần thay vì lộ dần.

### Biến thể 1 — Blob/ink mask reveal (`[data-mrt-blob]`)
```html
<section data-mrt-blob>
  <div class="mrt-blob-frame">
    <img class="mrt-blob-under" src="B.jpg" alt="…">
    <img class="mrt-blob-over" src="A.jpg" alt="…">
  </div>
</section>
```
`--mrt-r` ghi **trực tiếp mỗi frame** (không CSS transition) theo scroll progress: scroll listener rAF-throttle đo `stage.getBoundingClientRect()`, `progress = (vh - rect.top) / (vh + rect.height)` kẹp 0..1, nhân với bán kính tối đa (đường chéo khung / 2 + margin) → `over.style.setProperty('--mrt-r', ...)`. KHÔNG dùng transition ở biến thể này — transition sẽ làm vòng loang trễ nhịp so với vị trí cuộn thật (cùng lý do `svg-stroke-reveal` mode "scroll" không dùng transition).

### Biến thể 2 — Pinned split-screen mask reveal (`[data-mrt-split]`)
```html
<div class="mrt-split-section" data-mrt-split>
  <div class="mrt-split-sticky">
    <img class="mrt-split-under" alt="…">
    <img class="mrt-split-over" alt="">
  </div>
  <div class="mrt-split-scroll">
    <article data-mrt-panel data-mrt-src="1.jpg">…</article>
    <article data-mrt-panel data-mrt-src="2.jpg">…</article>
  </div>
</div>
```
Cột ảnh dùng thuần CSS `position: sticky` (KHÔNG GSAP/ScrollTrigger — pin theo cách rẻ nhất trình duyệt hỗ trợ sẵn). JS chỉ có nhiệm vụ **đổi ảnh/mask theo panel đang active**: một `IntersectionObserver` (threshold 0.5) gắn trên từng `[data-mrt-panel]`, khi panel vào tâm khung nhìn → gọi `revealTo(src)`: đẩy ảnh hiện tại lên lớp "trên" (che kín, `--mrt-r = 0` tức thì, ép reflow), đặt ảnh mới xuống lớp "dưới", rồi `requestAnimationFrame` set `--mrt-r` về bán kính tối đa để CSS transition (đăng ký qua `@property --mrt-r { syntax: "<length>"; ... }`) tự chạy mượt. Ở đây `--mrt-r` đổi RỜI RẠC theo sự kiện panel, không theo từng px cuộn — nên (khác biến thể 1) CSS transition trên `--mrt-r` là đúng chỗ.

## Rules
- **Hỗ trợ trình duyệt `mask-image`**: Safari (kể cả Safari hiện đại) chỉ nhận `-webkit-mask-image`/`-webkit-mask-repeat` — PHẢI viết cả `mask-image` chuẩn LẪN `-webkit-mask-image` (đã có sẵn trong CSS asset, đừng xoá prefix khi adapt/minify). Thiếu prefix = ảnh trên không bao giờ có lỗ hổng trên Safari, coi như hiệu ứng không chạy.
- **`position: sticky` không hoạt động nếu BẤT KỲ phần tử cha nào (kể cả xa, lên tới `<body>`) có `overflow: hidden`/`auto`/`scroll` hoặc `clip`** — đây là lỗi hay gặp nhất khi nhúng `.mrt-split-sticky` vào layout có sẵn (nhiều trang đặt `overflow: hidden` trên wrapper để chặn scroll ngang, vô tình giết sticky của mọi phần tử con). Kiểm tra toàn bộ chuỗi cha trước khi báo "sticky không chạy" là bug.
- Biến thể 2 dùng `@property --mrt-r` để trình duyệt animate được custom property nằm trong `calc()`/gradient — thiếu khai báo này, đổi `--mrt-r` bằng JS sẽ nhảy tức thì thay vì mượt qua transition.
- `prefers-reduced-motion: reduce` → cả 2 biến thể set `--mrt-r` = bán kính tối đa ngay lập tức (lộ ảnh hoàn toàn), tắt animate/transition — đã code sẵn trong JS/CSS, đừng xoá nhánh này khi adapt.
- Một scroll listener rAF-throttle DUY NHẤT cho mọi `[data-mrt-blob]` trên trang; một `IntersectionObserver` DUY NHẤT mỗi `[data-mrt-split]` cho các panel của nó — không gắn nhiều listener `scroll` rời hoặc nhiều observer trùng vai trò.
- Verify bằng `playwright-verify`: chụp trước/giữa/sau khi cuộn qua biến thể 1 để thấy vòng loang lớn dần, và assert biến thể 2 đổi đúng ảnh khi mỗi panel vào giữa khung nhìn + cột ảnh thực sự pin (không cuộn theo trang) trong lúc đọc.

## Origin
Batch 180926 — bản gốc NGUYÊN VĂN nằm ở `Rheinmir/uiux-asset/scroll-effects/` (xem mục "Bản gốc" ở trên); `assets/` là bản rút gọn vanilla tự viết.
