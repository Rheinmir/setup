---
name: infinite-webgl-grid
description: Lưới ảnh WebGL (Three.js) cuộn/kéo VÔ HẠN qua coordinate-wrapping — kéo hoặc cuộn dịch một offset ảo, vị trí mesh tính lại bằng modulo nên lưới trông vô hạn dù chỉ có N×N tile thật tồn tại. Gọi khi user nói "lưới ảnh vô hạn", "infinite scroll grid webgl", "draggable image wall", "poster wall cuộn vô hạn", hoặc /infinite-webgl-grid. KHÁC `skills/threejs-particle-morph` (particle rời rạc HỘI TỤ thành 1 ảnh theo tiến độ scroll, có "đích" cố định — đây là LƯỚI tile duyệt liên tục, không có đích) và KHÁC `skills/blur` (chuyển ảnh nọ sang ảnh kia trên 1 plane, không phải duyệt lưới nhiều ảnh).
---

# Skill: infinite-webgl-grid

Component Three.js thuần — lưới N×N tile ảnh cố định, kéo (pointer) hoặc cuộn (wheel) để duyệt như thể lưới trải dài vô hạn theo mọi hướng, dùng kỹ thuật coordinate-wrapping (modulo offset), không phải sinh/huỷ mesh liên tục.

## Bản gốc — dùng TRƯỚC (copy nguyên file, đừng viết lại)
Code gốc NGUYÊN VĂN của tác giả (CodePen public = MIT) nằm ở repo ngoài **`Rheinmir/uiux-asset`** — gallery chạy thật: https://rheinmir.github.io/uiux-asset/scroll-effects/ .
Quy trình: mở link **chạy** để xem đúng hiệu ứng → copy nguyên file `.html` (+ thư mục `_assets/` nếu file trỏ tới) vào dự án → giữ comment ghi công dòng đầu → chỉ sửa nội dung/ảnh/màu. Chạy local qua HTTP, không `file://`.
`git clone --depth 1 https://github.com/Rheinmir/uiux-asset` nếu cần cả bộ offline.

| Pen gốc — tác giả | Link |
|---|---|
| Infinite Scrollable and Draggable WebGL Grid — ReGGae | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/infinite-scrollable-and-draggable-webgl-grid.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/infinite-scrollable-and-draggable-webgl-grid.html) |
| Infinite 3D Poster Scroll Wall — photodow | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/infinite-3d-poster-scroll-wall.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/infinite-3d-poster-scroll-wall.html) |
| Infinite Scrolling with Image Cards — jkantner | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/infinite-scrolling-with-image-cards.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/infinite-scrolling-with-image-cards.html) |

`assets/` trong skill này chỉ là bản rút gọn vanilla tự viết — dùng khi dự án KHÔNG được kéo lib ngoài; mặc định dùng bản gốc ở trên.

## When to use
- Portfolio/gallery/poster-wall cần cảm giác "duyệt vô hạn" theo mọi hướng (không phải cuộn 1 chiều thông thường).
- User nói "lưới ảnh vô hạn", "infinite scroll grid webgl", "draggable image wall", "poster wall cuộn vô hạn".
- KHÔNG dùng khi cần particle hội tụ thành MỘT ảnh cụ thể theo scroll progress (đó là `threejs-particle-morph` — có state "đã tới đích", còn đây không có đích, chỉ duyệt liên tục).
- KHÔNG dùng cho hiệu ứng chuyển giữa 2 ảnh trên cùng 1 khung (đó là `blur`).

## Assets
`assets/demo.html` + `assets/demo.css` + `assets/demo.js` — đọc rồi ADAPT (đổi `gridSize`/`tileSize`/`gap`/`poolSize` khi khởi tạo `InfiniteGrid`, thay `_drawPlaceholder()` bằng ảnh thật qua `THREE.TextureLoader` load URL thay vì data URL canvas). Demo tự vẽ placeholder (canvas số + màu hash) nên chạy được ngay không cần ảnh/network.

## Cơ chế
- **Mesh cố định, không sinh thêm**: `gridSize × gridSize` mesh (`PlaneGeometry` dùng chung 1 instance + material riêng mỗi mesh) dựng một lần lúc init, KHÔNG BAO GIỜ add/remove mesh lúc chạy — khác hẳn cách làm ngây thơ "sinh mesh mới khi kéo tới vùng chưa có".
- **Offset ảo, không di chuyển camera ra xa vô hạn**: kéo/cuộn chỉ cộng dồn vào `offset.x/offset.y` (số float, có thể tăng vô hạn theo lý thuyết, không bao giờ chạm giới hạn thực tế). Camera đứng yên.
- **Wrap bằng modulo**: mỗi mesh có toạ độ cục bộ cố định `localX/localY` (vị trí trong lưới N×N gốc). Vị trí hiển thị thật mỗi frame = `wrap(localX - offset.x)`, với `wrap(raw) = ((raw + half) % full + full) % full - half` (`full = gridSize*pitch`, `half = full/2`) — gấp toạ độ vô hạn về dải hiển thị quanh tâm, đúng công thức mod chuẩn cho kỹ thuật này.
- **Texture reuse khi tile nhảy cóc**: mỗi mesh chỉ đổi `material.map` khi "chỉ số tile ảo" của nó đổi (tính từ `wrapped_position + offset`, làm tròn theo `pitch`) — tức đúng lúc tile rời khung nhìn một bên và xuất hiện lại bên đối diện. Texture lấy từ **pool cố định** (`poolSize` texture load một lần qua `THREE.TextureLoader`), KHÔNG tạo texture mới mỗi lần nhảy cóc.
- **Placeholder không phụ thuộc mạng**: pool texture sinh từ `<canvas>` vẽ số + màu (golden-angle hue spread để phân biệt bằng mắt), `canvas.toDataURL()` rồi vẫn nạp qua `THREE.TextureLoader.load(dataUrl)` — demo chạy offline nhưng vẫn đúng đường API load ảnh thật (khi thay ảnh thật chỉ cần đổi URL, không đổi luồng code).
- **Inertia**: pointer drag ghi `velocity` (delta di chuyển của lần pointermove cuối); khi thả tay, mỗi frame `offset += velocity; velocity *= damping (0.92)` cho tới khi dưới ngưỡng — lerp về 0 dần, không phải mô phỏng vật lý thật.
- **Cleanup**: `destroy()` gỡ pointerdown/pointermove/pointerup/pointercancel/wheel/resize listener, dispose từng material, dispose geometry dùng chung (1 lần), dispose từng texture trong pool (1 lần — KHÔNG dispose theo mesh vì texture được nhiều mesh share), dispose renderer, gỡ canvas khỏi DOM.

## Rules
- **Giới hạn tile/texture đồng thời**: mobile GPU giới hạn số texture unit hoạt động cùng lúc. Giữ lưới hiển thị thực tế (không tính vòng đệm wrap) ở khoảng **≤ 5×5 tile cùng lúc**; demo mặc định `gridSize=7` (5 hiển thị + 1 vòng đệm mỗi bên để tile nhảy cóc mượt, không pop-in). Cần nhiều ảnh khác nhau hơn số tile hiển thị → dùng **texture atlas** (gộp nhiều ảnh vào 1 texture, đổi UV offset thay vì đổi `material.map` riêng từng texture) thay vì tăng `poolSize` vô hạn — mỗi texture riêng vẫn tốn 1 texture unit dù không hiển thị cùng lúc nếu code giữ tham chiếu.
- **Passive: false bắt buộc**: listener `wheel` và `pointermove` phải đăng ký `{ passive: false }` rồi gọi `preventDefault()` đúng chỗ (chỉ khi đang kéo hoặc đang ở trong canvas) — thiếu cờ này, trình duyệt hiện đại mặc định passive nên `preventDefault()` bị bỏ qua ÂM THẦM (không lỗi, không cảnh báo) và trang nền vẫn cuộn/zoom song song với lưới, gây giật/xung đột trên mobile. CSS `touch-action: none` trên container là điều kiện cần đi kèm, không thay thế được `preventDefault`.
- Ortho camera dùng cho demo (lưới phẳng, không méo phối cảnh) — đổi sang `PerspectiveCamera` nếu cần hiệu ứng chiều sâu (tile xa mờ/nhỏ dần), khi đó công thức wrap vẫn giữ nguyên, chỉ đổi cách map world-unit sang pixel.
- Verify bằng `playwright-verify` — chụp trước/giữa/sau khi kéo mạnh (test cả 4 hướng), đọc console (context WebGL lỗi thường im lặng ở canvas, không throw JS error rõ ràng).

## Origin
