---
name: blur
description: Hiệu ứng WebGL "zoom blur" chuyển ảnh nền toàn màn hình (Three.js + shader GLSL riêng, parallax theo chuột, điều hướng scroll/click/phím) cho hero section/slideshow ảnh. Gọi khi user nói "hiệu ứng blur ảnh", "chuyển ảnh mờ dần kiểu zoom", "webgl blur transition", "gallery ảnh full-screen kiểu blur", hoặc /blur. KHÁC `dark-mode-maker` (circle-reveal đổi theme) — đây là hiệu ứng CHUYỂN ẢNH, không phải chuyển theme.
---

# Skill: blur

Component WebGL thuần — canvas full-screen, chuyển giữa các ảnh bằng "zoom blur" (radial blur hội tụ về tâm), scroll/click/phím mũi tên để điều hướng, tâm blur bám theo chuột.

## When to use
- Hero section hoặc slideshow ảnh cần hiệu ứng chuyển CAO CẤP hơn crossfade thường (zoom-blur transition).
- User nói "hiệu ứng blur ảnh", "webgl blur", "gallery kiểu zoom blur".
- KHÔNG dùng cho blur/frosted-glass TĨNH của UI card/panel (đó là `backdrop-filter: blur()` CSS thường, hoặc `docs-site-macos` liquid-glass) — đây là hiệu ứng CHUYỂN ĐỘNG giữa các ảnh, tốn GPU hơn hẳn.

## Assets
`assets/blur.html` + `assets/blur.css` + `assets/blur.js` — đọc rồi ADAPT (đổi mảng `images`, chỉnh tốc độ `duration`/easing).

## ⚠️ Nợ kỹ thuật đã biết — đọc TRƯỚC khi dùng production
`assets/blur.js` dòng 12 import helper `useThree` từ **một CodePen pen của người khác** (`codepen.io/soju22/pen/...js`) — đây là **phụ thuộc CDN vào tài nguyên không do ta sở hữu, có thể đổi/gỡ bất cứ lúc nào không báo trước**. Snippet gốc là demo tham khảo, chưa hardened cho production.
- **ponytail: global external dependency chưa vendor hoá, nâng cấp khi cần production thật** — trước khi dùng cho khách hàng/sản phẩm thật: (1) đọc nội dung pen đó, vendor hoá thành file `.js` riêng trong `assets/`, xoá import CDN; (2) tự viết lại `useThree` (Three.js scene/camera/renderer boilerplate) nếu không rõ license của pen gốc.
- `import ... from 'https://unpkg.com/three@0.120.0/...'` (dòng 1-10) cũng là CDN runtime — chấp nhận được cho prototype, nhưng dự án có bundler nên cài `three` qua npm rồi import local, tránh phụ thuộc mạng lúc chạy.
- `gsap` dùng trong `initScene()` nhưng KHÔNG được import trong file — giả định biến global đã có sẵn (script `<script src="gsap...">` ở trang chứa nó). Thiếu `<script>` đó thì `gsap.fromTo(...)` ném lỗi ngay khi ảnh load xong.

## Cơ chế
- Mỗi ảnh là một `PlaneBufferGeometry` phủ shader tuỳ biến (`ZoomBlurImage`) — fragment shader lấy mẫu ảnh dọc theo vector hướng-về-tâm, trọng số Bezier, tạo hiệu ứng mờ hội tụ khi `uStrength` khác 0.
- Chuyển ảnh: `progress`/`targetProgress` lerp dần (`updateProgress`), `uStrength` của 2 layer ảnh đan chéo (ảnh ra mờ dần, ảnh vào rõ dần).
- Input: cuộn chuột (`wheel`) đổi `targetProgress` theo bước 1/20; click nửa trên/dưới màn hình = lùi/tiến; phím mũi tên tương tự.
- Tâm blur (`uCenter`) lerp theo vị trí chuột mỗi frame → hiệu ứng "mắt dõi theo con trỏ".

## Rules
- Đây là hiệu ứng NẶNG GPU (shader chạy mỗi frame trên toàn viewport) — không dùng cho nhiều instance cùng lúc trên 1 trang, và test trên máy yếu/mobile trước khi chốt (WebGL context có giới hạn số lượng đồng thời của trình duyệt).
- Verify bằng `playwright-verify` — chụp trước/sau khi cuộn, đọc console (context WebGL lỗi thường im lặng ở canvas, không throw JS error thấy ngay).

## Origin
- Nén từ `llmwiki/patterns/blur/` (snippet tham khảo chưa gắn skill nào, chưa từng track git) thành skill thật theo yêu cầu user 2026-09-17 — cùng đợt với `timeline`.
