---
name: gsap-scrolltrigger-pin
description: Pin một section lại khi cuộn tới, rồi chuyển cuộn dọc thành cuộn ngang qua GSAP ScrollTrigger (pin + scrub + tween xPercent của track). Gọi khi user nói "gsap scrolltrigger", "pin section", "cuộn ngang", "horizontal scroll section", "scroll-driven horizontal", "pinned horizontal scroll", hoặc /gsap-scrolltrigger-pin. KHÁC `scroll-effects` (7 hiệu ứng nhẹ vanilla, không dependency, không pin) và `lenis-smooth-scroll` (làm mượt cuộn TOÀN TRANG, không pin/không đổi hướng cuộn) — skill này CẦN GSAP và chỉ áp dụng cho MỘT section pin cụ thể.
---

# Skill: gsap-scrolltrigger-pin

Section pin lại tại chỗ khi cuộn tới, cuộn dọc của người dùng được ScrollTrigger đọc và tween thành trượt ngang của một track chứa nhiều slide — kỹ thuật "pinned horizontal-scroll section" chuẩn ngành.

## Bản gốc — dùng TRƯỚC (copy nguyên file, đừng viết lại)
Code gốc NGUYÊN VĂN của tác giả (CodePen public = MIT) nằm ở repo ngoài **`Rheinmir/uiux-asset`** — gallery chạy thật: https://rheinmir.github.io/uiux-asset/scroll-effects/ .
Quy trình: mở link **chạy** để xem đúng hiệu ứng → copy nguyên file `.html` (+ thư mục `_assets/` nếu file trỏ tới) vào dự án → giữ comment ghi công dòng đầu → chỉ sửa nội dung/ảnh/màu. Chạy local qua HTTP, không `file://`.
`git clone --depth 1 https://github.com/Rheinmir/uiux-asset` nếu cần cả bộ offline.

| Pen gốc — tác giả | Link |
|---|---|
| Horizontal Scroll Section with GSAP and Locomotive Scroll — cameronknight | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/horizontal-scroll-section-with-gsap-and-locomotive-scroll.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/horizontal-scroll-section-with-gsap-and-locomotive-scroll.html) |
| Smooth Scroll Stacking Accordion — supah | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/smooth-scroll-stacking-accordion.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/smooth-scroll-stacking-accordion.html) |
| Infinite Horizontal Scroll with Progress Tracking — haptichash | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/infinite-horizontal-scroll-with-progress-tracking.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/infinite-horizontal-scroll-with-progress-tracking.html) |
| Pinned Split-Screen Mask Reveal — gridmorphic | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/pinned-split-screen-mask-reveal.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/pinned-split-screen-mask-reveal.html) |
| Scroll-Driven SVG Map Editorial Gallery — knyttneve | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/scroll-driven-svg-map-editorial-gallery.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/scroll-driven-svg-map-editorial-gallery.html) |

`assets/` trong skill này chỉ là bản rút gọn vanilla tự viết — dùng khi dự án KHÔNG được kéo lib ngoài; mặc định dùng bản gốc ở trên.

## When to use
- Trang cần một section kiểu "gallery ngang" (case study, portfolio, sản phẩm) mà người dùng vẫn chỉ lăn chuột dọc như bình thường.
- User nói "pin section", "cuộn ngang", "horizontal scroll section", "scroll-driven horizontal", "gsap scrolltrigger".
- KHÔNG dùng cho hiệu ứng cuộn nhẹ không cần pin (dùng `scroll-effects`) hay làm mượt cảm giác cuộn toàn trang (dùng `lenis-smooth-scroll`) — hai skill đó KHÔNG kéo theo dependency GSAP.

## Assets
`assets/demo.html` + `assets/gsap-scrolltrigger-pin.css` + `assets/gsap-scrolltrigger-pin.js` — đọc rồi ADAPT (đổi nội dung slide, token màu theo `design.md` của dự án nếu có). Mở `demo.html` trực tiếp bằng trình duyệt để xem cơ chế chạy thật (asset load GSAP qua CDN).

## Cơ chế
- Markup: `[data-hp-section] > .hp-pin > [data-hp-track] > [data-hp-slide] × N` — track là flex-row, mỗi slide `flex: 0 0 100vw`, tổng width = N × 100vw (tự nhiên theo layout, không tính tay).
- `ScrollTrigger` pin `.hp-pin` (`pin: true`, `start: "top top"`), `scrub: 1` khoá tiến trình animation vào đúng vị trí cuộn — không phải animation chạy theo thời gian.
- Animation là `gsap.to(track, { xPercent: -100 * (slideCount - 1) })` — `slideCount` đọc từ `track.querySelectorAll('[data-hp-slide]').length`, không hardcode số slide trong code.
- `end` là một HÀM: `() => "+=" + (track.scrollWidth - window.innerWidth)` — tính lại mỗi lần `ScrollTrigger.refresh()` chạy (đo lại theo `track.scrollWidth` thật của DOM tại thời điểm đó), không phải một số cố định.
- `ScrollTrigger.matchMedia()` bọc toàn bộ init: khi viewport đổi breakpoint hoặc `prefers-reduced-motion` đổi, GSAP tự revert nhánh cũ và chạy lại nhánh khớp — đây là cách chuẩn để "sống sót" qua resize, thay vì tự viết resize listener tay.
- `window.addEventListener('load', () => ScrollTrigger.refresh())` bắt trường hợp ảnh/font load xong mới đổi `scrollWidth` thật của track.

## Rules
- **Phụ thuộc GSAP là bắt buộc** — skill này KHÔNG chạy nếu thiếu GSAP + plugin ScrollTrigger. Cài một trong hai cách:
  - CDN (như demo.html): `<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>` + `.../ScrollTrigger.min.js`, load TRƯỚC script của skill.
  - npm: `npm install gsap`, rồi `import gsap from "gsap"; import { ScrollTrigger } from "gsap/ScrollTrigger"; gsap.registerPlugin(ScrollTrigger);`.
- `prefers-reduced-motion: reduce` → nhánh GSAP KHÔNG init gì cả (không ScrollTrigger, không pin, không scrub) — CSS tự chuyển `.hp-pin` thành `overflow-x: auto` cuộn ngang thường (`scroll-snap-type: x mandatory`). Đừng thêm animation JS nào trong nhánh này.
- Track dùng `xPercent`, không dùng `x` (px) — `xPercent` tự bám theo width thật của track dù nội dung slide đổi kích thước, không cần tính lại offset px tay.
- Verify bằng `playwright-verify`: cuộn dọc qua hết section, assert section pin đúng lúc (viewport không cuộn dọc thêm khi track chưa hết slide), assert không có horizontal overflow ở phần còn lại của trang, test resize viewport rồi cuộn lại để chắc `ScrollTrigger.refresh()` đã bắt layout mới.

## Origin
Batch 180926 — bản gốc NGUYÊN VĂN nằm ở `Rheinmir/uiux-asset/scroll-effects/` (xem mục "Bản gốc" ở trên); `assets/` là bản rút gọn vanilla tự viết.
