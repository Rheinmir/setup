---
name: css-scroll-driven-native
description: Hiệu ứng cuộn trang thuần CSS qua Native CSS Scroll-Driven Animations API (animation-timeline scroll()/view(), animation-range) — ZERO JavaScript. Gọi khi user nói "css scroll driven animation", "animation-timeline", "scroll animation không js", "css thuần cuộn trang", "scroll-driven CSS", hoặc /css-scroll-driven-native. KHÁC `skills/scroll-effects` (đó dùng IntersectionObserver JS, chạy MỌI trình duyệt hiện đại) — skill này 0 JS nhưng trình duyệt CHƯA hỗ trợ đủ (Firefox/Safari còn behind flag/rollout), dùng làm progressive enhancement phía trên scroll-effects, không thay thế khi cần chạy chắc trên mọi trình duyệt.
---

# Skill: css-scroll-driven-native

Hiệu ứng cuộn trang bằng **CSS spec công khai** — `animation-timeline: scroll()` / `view()` + `animation-range` — không một dòng JavaScript.

## Khi nào chọn cái này vs `scroll-effects`

| | `css-scroll-driven-native` (skill này) | `scroll-effects` |
|---|---|---|
| JS | 0 dòng | IntersectionObserver + rAF |
| Hỗ trợ trình duyệt | Chrome/Edge tốt; Firefox/Safari đang rollout, có thể chưa bật mặc định | Mọi trình duyệt hiện đại |
| Khi dùng | Progressive enhancement — thêm "độ mượt" cho trình duyệt đã hỗ trợ, KHÔNG phải cơ chế chính nếu cần chạy chắc production đa trình duyệt ngay | Cơ chế chính khi cần chạy chắc ngay, không đợi rollout |

Khuyến nghị: dùng skill này bên trong `@supports (animation-timeline: scroll())`, fallback tĩnh (không animation, không ẩn nội dung) — hoặc kết hợp cả hai: `scroll-effects` làm nền, skill này override khi trình duyệt hỗ trợ.

⚠️ **Kiểm tra hỗ trợ thật trước khi dùng production** tại [caniuse.com/css-scroll-driven-animations](https://caniuse.com/css-scroll-driven-animations) — đừng tin số liệu cứng ghi trong tài liệu này, API đang rollout nhanh và bảng hỗ trợ có thể đã đổi.

## Assets

`assets/demo.html` + `assets/demo.css` — 3 cơ chế demo, đọc rồi ADAPT (đổi token màu/spacing theo `design.md` của dự án nếu có). Mở trực tiếp bằng trình duyệt hỗ trợ (Chrome/Edge mới) để xem chạy thật; trình duyệt chưa hỗ trợ sẽ tự rơi về trạng thái tĩnh.

## 3 cơ chế (markup tối thiểu + cơ chế)

### 1. Progress bar theo cuộn trang
Thanh cố định trên cùng, dài theo % đã cuộn hết trang.
```html
<div class="csdn-progress"></div>
```
```css
.csdn-progress {
  animation-name: progress-scale;
  animation-duration: 1ms; /* giá trị bất kỳ để kích hoạt engine — thời lượng thật do timeline điều khiển */
  animation-timeline: scroll(root);
  animation-fill-mode: both;
}
@keyframes progress-scale {
  from { transform: scaleX(0); }
  to   { transform: scaleX(1); }
}
```
`scroll(root)` bám vào tiến độ cuộn của toàn trang — không cần `scroll` listener, không cần tính `scrollY / scrollHeight` bằng tay.

### 2. Reveal-on-view khi phần tử vào khung nhìn
```html
<article class="csdn-card">…</article>
```
```css
.csdn-card {
  animation-name: reveal-in;
  animation-timeline: view();
  animation-range: entry 0% cover 40%;
  animation-fill-mode: both;
}
```
`view()` là timeline riêng của TỪNG phần tử theo vị trí trong viewport của chính nó — thay hẳn IntersectionObserver. `animation-range: entry 0% cover 40%` nghĩa là animation chạy từ lúc phần tử bắt đầu vào viewport (`entry 0%`) tới khi đã "cover" 40% quãng đường qua viewport.

### 3. Parallax nhẹ dùng `view()`
Nền và nội dung dùng **`animation-range` khác nhau** trên cùng một timeline `view()` → tạo cảm giác lớp trôi khác tốc độ, không cần tính toán `scrollY` thủ công.
```css
.parallax-bg      { animation-timeline: view(); animation-range: cover 0% cover 100%; }   /* trôi chậm, suốt cả quãng */
.parallax-content { animation-timeline: view(); animation-range: entry 0% cover 35%; }    /* chạy nhanh, chỉ đoạn đầu */
```
Xem `assets/demo.css` mục 3 để có keyframes đầy đủ.

## Rules (BẮT BUỘC)

- **Luôn có fallback `@supports`**: mọi animation nằm trong `@supports (animation-timeline: scroll())` hoặc `@supports (animation-timeline: view())`. Bên NGOÀI khối `@supports` là trạng thái TĨNH mặc định — phần tử **hiện đủ nội dung**, không animation, **KHÔNG BAO GIỜ ẩn/opacity:0 làm mặc định**. Nếu viết `opacity:0` cho hiệu ứng reveal, giá trị đó CHỈ được đặt bên trong `@supports`, không phải ở rule gốc.
- **`prefers-reduced-motion`**: bọc animation trong `@media not (prefers-reduced-motion: reduce)` (lồng bên trong `@supports`, xem `demo.css`). Người dùng bật reduce-motion → mọi phần tử về trạng thái tĩnh giống hệt trình duyệt không hỗ trợ.
- **Bảng hỗ trợ trình duyệt hiện tại** (ghi tại thời điểm viết skill, 2026-09 — có thể đã đổi, luôn tự kiểm tra):
  | Trình duyệt | `animation-timeline: scroll()` | `animation-timeline: view()` |
  |---|---|---|
  | Chrome / Edge | Có | Có |
  | Firefox | Behind flag / đang rollout | Behind flag / đang rollout |
  | Safari | Đang rollout, chưa ổn định | Đang rollout, chưa ổn định |

  KHÔNG cứng số phiên bản vào code hay comment — kiểm tra [caniuse.com/css-scroll-driven-animations](https://caniuse.com/css-scroll-driven-animations) mỗi lần dùng thật.
- `animation-duration` vẫn phải khai (`1ms` hoặc giá trị bất kỳ >0) dù thời lượng thật do timeline điều khiển — một số engine yêu cầu giá trị này để kích hoạt animation.
- Verify bằng `playwright-verify` trên trình duyệt Chromium (CDP mặc định hỗ trợ scroll-driven animations): chụp ảnh tại 0%/50%/100% scroll, assert progress bar/scaleX và card opacity đổi theo vị trí cuộn; đồng thời chụp thêm với `prefers-reduced-motion: reduce` giả lập (Playwright `emulateMedia`) để assert KHÔNG animation nhưng nội dung vẫn hiện đủ.

## Origin

- Bổ sung cho `skills/scroll-effects` (JS-based, chạy mọi trình duyệt) một lựa chọn 0-JS cho trình duyệt đã hỗ trợ — hai skill KHÔNG thay thế nhau, dùng theo bảng "Khi nào chọn cái này" ở trên.
