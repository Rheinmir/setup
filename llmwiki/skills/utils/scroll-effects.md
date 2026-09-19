---
name: scroll-effects
description: >-
  Hub hiệu ứng cuộn trang — 64 bản GỐC nguyên văn (freefrontend/CodePen, MIT) ở repo Rheinmir/uiux-asset để copy nguyên file, kèm 7 hiệu ứng vanilla nhẹ: reveal-on-scroll, staggered text,
  scroll highlight, sticky shrink nav, scroll-to-top, scrollspy TOC, parallax nhẹ data-speed.
  Vanilla HTML/CSS/JS, tôn trọng prefers-reduced-motion. Gọi khi user nói "hiệu ứng scroll",
  "scroll reveal", "scroll to top", "scrollspy", "parallax nhẹ", "highlight khi cuộn", hoặc
  /scroll-effects. KHÁC `blur` (WebGL chuyển ảnh nặng GPU) và `timeline` (trục mốc thời gian) —
  đây là các hiệu ứng cuộn trang dùng hàng ngày, nhẹ, không dependency.
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: scroll-effects

Hub hiệu ứng cuộn trang: **64 bản gốc nguyên văn** (freefrontend/CodePen, MIT) ở `Rheinmir/uiux-asset` — duyệt gallery, copy nguyên file. Kèm 7 hiệu ứng vanilla tự viết trong `assets/` cho dự án không được kéo lib ngoài.

## WHAT

### Purpose và context
- **Purpose:** gắn hiệu ứng cuộn trang nhẹ vào trang đích — mặc định copy nguyên file bản GỐC từ `Rheinmir/uiux-asset`; dự án không được kéo lib ngoài thì dùng 7 pattern vanilla trong `assets/`.
- **Trigger (when to use):**
  - Trang cần hiệu ứng hiện-dần khi cuộn, chữ stagger, highlight dẫn mắt, nav co lại, nút về đầu trang, mục lục bám theo section, hoặc parallax nhẹ.
  - User nói "hiệu ứng scroll", "scroll to top", "scrollspy", "parallax", "reveal khi cuộn".
- **Non-goals:** KHÔNG dùng cho: chuyển ảnh điện ảnh nặng GPU (đó là `blur`), trục timeline mốc thời gian (đó là `timeline`), cuộn ngang pin-section kiểu GSAP ScrollTrigger phức tạp (vượt phạm vi skill nhẹ này — nói rõ với user).

### Mental model
`nhu cầu hiệu ứng → gallery 64 bản gốc (mặc định, copy nguyên file) hoặc 7 pattern vanilla (không được kéo lib) → adapt token theo design.md → một IntersectionObserver + một scroll listener rAF → reduced-motion tắt hết → verify playwright`. Hub rẽ sang skill con tương ứng khi mục gallery thuộc skill con.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | hiệu ứng cần | có | một trong 7 pattern hoặc mục gallery |
| In | ràng buộc dự án | không | có được kéo lib/file ngoài không; có `design.md` không |
| Out | file hiệu ứng trong dự án | có | bản gốc copy nguyên (giữ comment ghi công dòng đầu) hoặc asset vanilla đã adapt |
| Out | bằng chứng verify | có | ảnh trước/sau cuộn, `.is-in` xuất hiện, không horizontal overflow |

### Rules và capabilities
- RULE-01 (MUST): `prefers-reduced-motion: reduce` → tắt toàn bộ: CSS ép `.is-in` hiện ngay không transition, JS bỏ smooth scroll và parallax (đã code sẵn trong assets, đừng xoá nhánh này khi adapt).
- RULE-02 (MUST): Một `IntersectionObserver` dùng chung cho reveal + stagger + highlight + TOC (đã gộp trong `scroll-effects.js`) — đừng tạo 4 observer riêng.
- RULE-03 (MUST): Scroll listener duy nhất, rAF-throttle — nav + top + parallax đọc chung một `scrollY` mỗi frame, không gắn 3 listener `scroll` rời.
- RULE-04 (MUST): Verify bằng `playwright-verify`: chụp trước/sau cuộn, assert `.is-in` xuất hiện, đo không có horizontal overflow do parallax.
- RULE-05 (MUST): Khi adapt vào dự án có `design.md`: đổi token màu/spacing, giữ nguyên tên `data-se-*` (JS bám vào chúng).
- Capabilities: đọc gallery/repo asset ngoài (mạng) hoặc asset nội bộ; ghi file front-end dự án; chạy trình duyệt headless qua HTTP local.

### Failure boundaries
- Yêu cầu là WebGL nặng, timeline mốc, hoặc pin-section GSAP phức tạp → **blocked** ngoài phạm vi, nói rõ với user và chỉ skill đúng.
- Không truy cập được gallery/repo ngoài hoặc dự án cấm lib ngoài → dùng 7 pattern vanilla (không phải lỗi).
- Verify playwright không thấy `.is-in` hoặc có horizontal overflow → **failed**, sửa rồi verify lại.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | judgment | yêu cầu | Khớp phạm vi (không phải blur/timeline/GSAP pin) | hiệu ứng trong phạm vi | ngoài phạm vi → blocked |
| W02 | judgment | ràng buộc dự án | Chọn nguồn: bản gốc gallery (mặc định) hay vanilla `assets/` (B01) | nguồn | — |
| W03 | effect | nguồn | Bản gốc: mở link chạy → copy nguyên `.html` (+ `_assets/`) → giữ comment ghi công → chỉ sửa nội dung/ảnh/màu | file trong dự án | — |
| W04 | effect | `design.md` | Adapt token màu/spacing, giữ `data-se-*`, giữ nhánh reduced-motion | file đã adapt | — |
| W05 | deterministic | trang qua HTTP | `playwright-verify`: chụp trước/sau cuộn, assert `.is-in`, đo overflow | PASS | FAIL → sửa, lặp W05 |

Chi tiết từng bước (nguồn chân lý cho W01–W05):

#### Bản gốc — dùng TRƯỚC (copy nguyên file, đừng viết lại)
Code gốc NGUYÊN VĂN của tác giả (CodePen public = MIT) nằm ở repo ngoài **`Rheinmir/uiux-asset`** — gallery chạy thật: https://rheinmir.github.io/uiux-asset/scroll-effects/ .
Quy trình: mở link **chạy** để xem đúng hiệu ứng → copy nguyên file `.html` (+ thư mục `_assets/` nếu file trỏ tới) vào dự án → giữ comment ghi công dòng đầu → chỉ sửa nội dung/ảnh/màu. Chạy local qua HTTP, không `file://`.
`git clone --depth 1 https://github.com/Rheinmir/uiux-asset` nếu cần cả bộ offline.

Hub: duyệt cả 64 mục ở gallery (lọc theo tên/kỹ thuật/tác giả), rồi rẽ sang skill con tương ứng.

`assets/` trong skill này chỉ là bản rút gọn vanilla tự viết — dùng khi dự án KHÔNG được kéo lib ngoài; mặc định dùng bản gốc ở trên.

#### Assets
`assets/demo.html` (trang demo ráp sẵn cả 7) + `assets/scroll-effects.css` + `assets/scroll-effects.js` — đọc rồi ADAPT (đổi class/token theo `design.md` của dự án nếu có).

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | dự án KHÔNG được kéo lib/file ngoài | dùng 7 pattern vanilla trong `assets/` (mục Reference bên dưới) thay bản gốc | được kéo ngoài → bản gốc gallery | W04 |
| B02 | user_optional | cần cả bộ gốc offline | `git clone --depth 1` repo `Rheinmir/uiux-asset` | — | W03 |
| B03 | conditional_required | mục gallery thuộc một skill con | rẽ sang skill con tương ứng | — | kết thúc ở skill con |

### Validation và stopping
Chạy qua HTTP local (không `file://`). PASS khi playwright chụp trước/sau cuộn thấy `.is-in`, không horizontal overflow, và với reduced-motion mọi phần tử hiện ngay. Dừng khi PASS; FAIL thì sửa và verify lại.

### Examples
- **Positive:** "thêm scroll to top + scrollspy cho trang docs, không được kéo lib" → B01 dùng `[data-se-top]` + `[data-se-toc]` từ `assets/`, đổi token theo `design.md`, giữ `data-se-*` → playwright: nút hiện khi `scrollY > innerHeight`, link TOC nhận `.is-active`.
- **Boundary/failure:** "làm section cuộn ngang pin kiểu GSAP" → ngoài phạm vi skill nhẹ này → nói rõ với user, không cố dựng bằng parallax `data-se-parallax`.

### Reference — 7 pattern (markup tối thiểu + cơ chế)

#### 1. Reveal on scroll — `[data-se-reveal]`
Phần tử mờ + trượt nhẹ, hiện khi cuộn vào khung nhìn.
```html
<div data-se-reveal>Lộ dần khi cuộn tới</div>
```
`IntersectionObserver` gắn `.is-in` → CSS transition `opacity/translateY`. Tham khảo gallery scroll-effects #9 (Animated Scroll Highlight Annotations) về *trường hợp dùng*, không dùng code của họ.

#### 2. Staggered text — `[data-se-stagger]`
Các dòng chữ hiện nối tiếp nhau.
```html
<h2 data-se-stagger>
  <span>Dòng một</span><span>Dòng hai</span><span>Dòng ba</span>
</h2>
```
JS gán `--i` cho mỗi `span` → CSS `transition-delay: calc(var(--i) * 90ms)`. Chỉ tách theo phần tử con có sẵn, không tự split text node (giữ DOM đơn giản, tránh lỗi a11y).

#### 3. Scroll highlight — `[data-se-highlight] > mark`
Đánh dấu ý chính, vệt màu quét trái→phải khi đoạn văn vào khung nhìn.
```html
<p data-se-highlight>Đọc tới đây <mark>ý chính hiện ra</mark> rồi đọc tiếp.</p>
```
`mark` dùng `background-size: 0% → 100%` transition khi cha có `.is-in`. Dùng `<mark>` ngữ nghĩa thật, không span giả.

#### 4. Sticky shrink nav — `[data-se-nav]`
Header co gọn khi cuộn xuống, phồng lại khi về đầu.
```html
<header data-se-nav class="site-nav">…</header>
```
Scroll listener (rAF-throttle) toggle `.is-shrunk` khi `scrollY > 24`. Chỉ đổi padding/font-size qua class, không set style inline từng frame.

#### 5. Scroll to top — `[data-se-top]`
Nút về đầu trang, chỉ hiện sau khi cuộn qua một màn hình.
```html
<button data-se-top aria-label="Về đầu trang">↑</button>
```
Click → `window.scrollTo({ top: 0, behavior: "smooth" })` (trừ khi `prefers-reduced-motion` → `"auto"`). Ngưỡng hiện: `scrollY > innerHeight`.

#### 6. Scrollspy TOC — `[data-se-toc] a[href^="#"]` + `section[id]`
Mục lục sticky, link sáng theo section đang đọc.
```html
<nav data-se-toc><a href="#s1">Mục 1</a><a href="#s2">Mục 2</a></nav>
<section id="s1">…</section><section id="s2">…</section>
```
`IntersectionObserver` với `rootMargin: "-40% 0px -55% 0px"` → link khớp nhận `.is-active`. Tham khảo gallery #19 (Auto-Generated Anchor TOC) về *ý tưởng*, code tự viết.

#### 7. Parallax nhẹ — `[data-se-parallax="0.2"]`
Lớp nội dung trôi chậm hơn/nhanh hơn tốc độ cuộn.
```html
<div data-se-parallax="0.15">Trôi chậm tạo chiều sâu</div>
```
rAF loop: `translateY = (elCenter - viewportCenter) * speed`. Giá trị `speed` khuyến nghị `|v| ≤ 0.3`; vượt quá gây say chuyển động. KHÔNG dùng cho chữ nhỏ cần đọc chính xác.

## Origin
- User chốt "làm đi hỏi nhiều quá" → thay vì bulk-copy 81 tác phẩm, viết BỘ GỐC 7 pattern generic (kỹ thuật chuẩn ngành: IntersectionObserver/scroll listener/rAF — không phải biểu đạt sáng tạo riêng của ai) để downstream tham khảo code mẫu ngay, đúng cách `blur`/`timeline` đã làm.
