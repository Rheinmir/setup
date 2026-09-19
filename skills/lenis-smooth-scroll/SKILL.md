---
name: lenis-smooth-scroll
description: Thiết lập Lenis (physics-based smooth scroll) cho TOÀN TRANG + đồng bộ đúng cách với GSAP ScrollTrigger (raf loop dùng chung driver, không lệch pha, không giật khi quay lại tab). Gọi khi user nói "lenis", "smooth scroll", "cuộn mượt kiểu apple", "physics-based scroll", hoặc /lenis-smooth-scroll. KHÁC `skills/gsap-scrolltrigger-pin` (đó là pin + cuộn ngang cho MỘT section cụ thể — dùng CHUNG được với skill này, pin không thay được nền smooth-scroll) và KHÁC `skills/scroll-effects` (vanilla, không dependency; skill này CÓ dependency Lenis + GSAP, là nền smooth-scroll cho cả trang chứ không phải hiệu ứng lẻ).
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: lenis-smooth-scroll

Thiết lập [Lenis](https://lenis.darkroom.engineering/) làm nền cuộn vật lý (physics-based) cho toàn trang, và đồng bộ đúng cách với GSAP ScrollTrigger — đây là bước hay bị làm sai nhất khi ráp 2 thư viện này chung.

## WHAT

### Purpose và context
- **Purpose:** dựng Lenis làm nền cuộn vật lý cho TOÀN TRANG và đồng bộ đúng với GSAP ScrollTrigger (một driver raf, không lệch pha, không giật khi quay lại tab), mặc định bằng bản gốc nguyên văn ở `Rheinmir/uiux-asset`.
- **Trigger (when to use):**
- Trang cần cảm giác cuộn "nặng tay/mượt" kiểu Apple/awwwards thay vì cuộn giật cứng mặc định của trình duyệt.
- Trang đã hoặc sẽ dùng GSAP ScrollTrigger (parallax, reveal, pin) và cần Lenis + ScrollTrigger KHÔNG đá nhau (giật, lệch vị trí trigger).
- KHÔNG dùng nếu chỉ cần vài hiệu ứng cuộn nhẹ không cần smooth-scroll nền (dùng `scroll-effects` — vanilla, 0 dependency).
- KHÔNG dùng để pin/cuộn-ngang một section riêng (đó là `gsap-scrolltrigger-pin`) — nhưng nếu trang có cả hai nhu cầu, khởi tạo Lenis theo skill này TRƯỚC, rồi `gsap-scrolltrigger-pin` hoạt động bình thường bên trên vì cả hai đều lấy ScrollTrigger làm trục.
  - User nói "lenis", "smooth scroll", "cuộn mượt kiểu apple", "physics-based scroll", hoặc `/lenis-smooth-scroll`.
- **Non-goals:** không pin/cuộn ngang một section (→ `gsap-scrolltrigger-pin`), không hiệu ứng cuộn lẻ 0-dependency (→ `scroll-effects`), không viết lại code gốc của tác giả.

### Mental model
`bản gốc (Rheinmir/uiux-asset) → copy nguyên file → chỉ sửa nội dung` | nếu không được kéo lib ngoài: `assets/ (vanilla rút gọn) → ADAPT`. Lõi kỹ thuật: `reduced-motion? → không Lenis` / `new Lenis → driver: 2A raf tự quản (không GSAP) XOR 2B gsap.ticker (có GSAP) → lenis.on('scroll', ScrollTrigger.update) → reveal/data-speed ăn theo cùng driver`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | trang/dự án đích | có | có build step (npm) hay trang tĩnh (CDN) |
| In | có dùng GSAP ScrollTrigger? | có | quyết định driver 2A hay 2B |
| In | được kéo lib ngoài? | có | quyết định bản gốc hay `assets/` |
| Out | trang cuộn Lenis | có | một driver duy nhất; `* 1000` nếu qua `gsap.ticker`; `lagSmoothing(0)`; nhánh reduced-motion còn nguyên |
| Out | bằng chứng verify | có | `playwright-verify`: cuộn nhanh không nhảy vị trí + nhánh reduced-motion qua `page.emulateMedia` |

### Rules và capabilities
- RULE-01 (MUST): **Cài đặt**: `npm i lenis gsap` (khuyến nghị cho dự án có build step) — hoặc CDN như trong `assets/demo.html` (`unpkg.com/lenis`, `cdnjs.cloudflare.com/.../gsap`) cho trang tĩnh/demo nhanh. Không dùng bản Lenis cũ tên gói `@studio-freight/lenis` (đã đổi tên thành `lenis`) trừ khi dự án đang pin phiên bản cũ có lý do.
- RULE-02 (MUST): **Lỗi thường gặp #1**: quên `gsap.ticker.lagSmoothing(0)` → cuộn mượt bình thường nhưng giật một cú khi người dùng đổi tab rồi quay lại — vì GSAP tự bù-lag chồng lên cơ chế làm mượt riêng của Lenis (xem giải thích ở mục Cơ chế).
- RULE-03 (MUST): **Lỗi thường gặp #2**: chạy CẢ 2A (`requestAnimationFrame(raf)` tự quản) LẪN 2B (`gsap.ticker.add`) cùng lúc → hai vòng raf lệch pha, giật nhẹ liên tục. Chỉ chọn MỘT driver: có GSAP thì dùng 2B, không có thì dùng 2A.
- RULE-04 (MUST): **Lỗi thường gặp #3**: gọi `lenis.raf(time)` từ `gsap.ticker` mà quên nhân `* 1000` (giây → mili-giây) → easing tính sai.
- RULE-05 (MUST): `prefers-reduced-motion: reduce` → không khởi tạo Lenis, không giả-mượt bằng CSS `scroll-behavior: smooth` thay thế — để cuộn gốc trình duyệt hoàn toàn (đã code trong `assets/lenis-demo.js`, đừng xoá nhánh này khi adapt).
- RULE-06 (MUST): Verify bằng `playwright-verify`: cuộn nhanh liên tục, kiểm tra không có nhảy vị trí giữa `data-ls-reveal` và section chứa nó; test cả nhánh reduced-motion (giả lập qua `page.emulateMedia`).
- Capabilities: đọc/copy file mẫu từ repo ngoài hoặc `assets/`; ghi vào dự án đích; cài dependency frontend (lenis, gsap); chạy trình duyệt headless để verify.

### Failure boundaries
- Không mở/clone được `Rheinmir/uiux-asset` → dùng `assets/` vanilla rút gọn (**partial**), báo user.
- User bật `prefers-reduced-motion: reduce` → không khởi tạo Lenis (đúng hành vi, không phải lỗi).
- Verify thấy nhảy vị trí/giật → **failed**, rà lại 3 lỗi thường gặp (#1–#3) trước khi báo xong.
- Dự án pin `@studio-freight/lenis` có lý do → giữ nguyên, **clarify** với user trước khi đổi gói.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | judgment | yêu cầu | Chọn pen gốc phù hợp trong bảng "Bản gốc", mở link **chạy** xem đúng hiệu ứng | pen được chọn | không được kéo lib ngoài → B01 |
| W02 | effect | pen | Copy nguyên file `.html` (+ `_assets/`) vào dự án, giữ comment ghi công, chỉ sửa nội dung/ảnh/màu; chạy qua HTTP | trang chạy | — |
| W03 | deterministic | trang | Cài (`npm i lenis gsap` hoặc CDN), khởi tạo Lenis sau guard reduced-motion; chọn MỘT driver (2A hoặc 2B) | Lenis chạy | có GSAP → B02 |
| W04 | deterministic | trang | Verify bằng `playwright-verify` (cuộn nhanh + reduced-motion qua `page.emulateMedia`) | pass | giật/nhảy → rà lỗi #1–#3, lặp W03 |

Chi tiết từng bước (nguồn chân lý cho W01–W04):

#### Bản gốc — dùng TRƯỚC (copy nguyên file, đừng viết lại)
Code gốc NGUYÊN VĂN của tác giả (CodePen public = MIT) nằm ở repo ngoài **`Rheinmir/uiux-asset`** — gallery chạy thật: https://rheinmir.github.io/uiux-asset/scroll-effects/ .
Quy trình: mở link **chạy** để xem đúng hiệu ứng → copy nguyên file `.html` (+ thư mục `_assets/` nếu file trỏ tới) vào dự án → giữ comment ghi công dòng đầu → chỉ sửa nội dung/ảnh/màu. Chạy local qua HTTP, không `file://`.
`git clone --depth 1 https://github.com/Rheinmir/uiux-asset` nếu cần cả bộ offline.

| Pen gốc — tác giả | Link |
|---|---|
| Lenis Smooth Scroll & GSAP Page — filipz | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/lenis-smooth-scroll-gsap-page.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/lenis-smooth-scroll-gsap-page.html) |
| Lenis Smooth Scroll Cinematic Experience — filipz | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/lenis-smooth-scroll-cinematic-experience.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/lenis-smooth-scroll-cinematic-experience.html) |
| Layout Explorations with GSAP, Flip, Lenis and ScrollTrigger N°2 — filipz | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/layout-explorations-with-gsap-flip-lenis-and-scrolltrigger-n-2.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/layout-explorations-with-gsap-flip-lenis-and-scrolltrigger-n-2.html) |
| Staggered Text Scroll Reveal — gusevdigital | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/staggered-text-scroll-reveal.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/staggered-text-scroll-reveal.html) |

`assets/` trong skill này chỉ là bản rút gọn vanilla tự viết — dùng khi dự án KHÔNG được kéo lib ngoài; mặc định dùng bản gốc ở trên.

#### Assets
`assets/demo.html` + `assets/lenis-demo.css` + `assets/lenis-demo.js` — trang demo chạy được (CDN Lenis + GSAP), đọc rồi ADAPT (đổi token/section theo dự án, đổi CDN sang bundle npm nếu dự án đã có build step).

#### Cơ chế

##### 1. Khởi tạo Lenis
```js
const lenis = new Lenis({
  lerp: 0.1,        // nội suy mỗi frame (0–1): thấp = mượt/trễ hơn, cao = bám sát input hơn
  duration: 1.2,     // easing khi có target (vd anchor scroll), không áp dụng cho wheel liên tục
  smoothWheel: true, // bật vật lý mượt cho wheel/trackpad — lý do chính để dùng Lenis
});
```

##### 2A. Đứng một mình (không GSAP) — vòng lặp raf tự quản
```js
function raf(time) {
  lenis.raf(time);
  requestAnimationFrame(raf);
}
requestAnimationFrame(raf);
```

##### 2B. Có GSAP ScrollTrigger — GỘP về một driver duy nhất (không dùng cả 2A lẫn 2B cùng lúc)
```js
gsap.registerPlugin(ScrollTrigger);

lenis.on('scroll', ScrollTrigger.update);         // Lenis cuộn -> báo ScrollTrigger cập nhật ngay
gsap.ticker.add((time) => lenis.raf(time * 1000)); // gsap.ticker LÀM vòng raf cho Lenis luôn
gsap.ticker.lagSmoothing(0);                        // tắt bù-lag mặc định của GSAP (xem lý do bên dưới)
```

**Tại sao phải làm đúng thứ tự 3 dòng này (điểm hay sai nhất):**
- `gsap.ticker` đã tự chạy một vòng `requestAnimationFrame` nội bộ để lái mọi tween/ScrollTrigger. Nếu Lenis lại tự chạy thêm một `requestAnimationFrame(raf)` riêng (cách 2A) TRONG KHI đã có GSAP, hai vòng lặp không cùng nhịp — mỗi frame chúng cập nhật lệch nhau vài mili-giây, ScrollTrigger đọc vị trí cuộn "cũ hơn" hoặc "mới hơn" Lenis một khung hình. Cảm giác là giật nhẹ liên tục khi cuộn nhanh, đặc biệt ở section có `pin` hoặc `scrub`. Sửa bằng cách để **gsap.ticker làm driver DUY NHẤT**: bỏ hẳn `requestAnimationFrame(raf)` riêng, thay bằng `gsap.ticker.add(...)`.
- `gsap.ticker` phát `time` tính bằng **giây**, còn `lenis.raf()` cần **mili-giây** → phải nhân `* 1000`. Quên nhân là lỗi im lặng: Lenis chạy nhưng easing/velocity tính sai theo một hệ thời gian nhỏ hơn 1000 lần, scroll trông "đơ" hoặc "bay" tuỳ lerp.
- `lenis.on('scroll', ScrollTrigger.update)` bắt buộc vì Lenis cập nhật vị trí cuộn qua transform nội bộ (`lerp` mỗi frame, không phải `scrollTop` tức thời) — nếu không báo, ScrollTrigger vẫn dùng sự kiện `scroll` gốc của trình duyệt để tính pin/progress, vốn KHÔNG khớp với vị trí "mượt" mà Lenis đang vẽ ra → pin bị lệch vài px hoặc trigger bắn sai thời điểm.
- `gsap.ticker.lagSmoothing(0)` xử lý một lỗi khác, dễ bị bỏ sót: mặc định GSAP tự phát hiện khung hình bị trễ bất thường (ví dụ tab mất focus vài giây rồi quay lại) và "nén" thời gian lại để bù, cho animation không nhảy cóc. Nhưng Lenis đã tự có cơ chế làm mượt delta-time của riêng nó — hai hệ bù-thời-gian chồng lên nhau khiến cú quay-lại-tab bị giật một nhịp rõ rệt thay vì mượt. Tắt hẳn bù của GSAP (`lagSmoothing(0)`) để một mình Lenis lo phần đó.

##### 3. Tôn trọng `prefers-reduced-motion: reduce`
Không được "giả-mượt" cho người đã bật giảm chuyển động — không khởi tạo `Lenis` luôn, để trình duyệt cuộn gốc (jump-scroll bình thường). Kiểm tra TRƯỚC khi gọi `new Lenis(...)`:
```js
if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  // new Lenis(...) + sync ở trên
} else {
  // cuộn gốc trình duyệt; nếu có reveal-on-scroll đi kèm, hiện thẳng bằng CSS/class, không chờ cuộn mượt
}
```
Xem cách áp dụng đầy đủ (kèm demo reveal fallback) trong `assets/lenis-demo.js`.

##### 4. Demo: reveal + `data-speed` khi cuộn qua Lenis
`assets/demo.html` có vài section gắn `data-ls-reveal` (stagger hiện dần, dùng `ScrollTrigger.create({ once: true })` ăn theo scroll đã sync ở bước 2B) và `data-speed="0.12"` (layer trôi lệch nhẹ qua `gsap.to(..., { scrollTrigger: { scrub: true } })`, giá trị kẹp `|v| ≤ 0.3` để tránh say chuyển động) — cả hai dùng CHUNG driver Lenis/GSAP đã thiết lập, không tạo listener `scroll` rời.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | dự án KHÔNG được kéo lib ngoài / cần bản tự viết | dùng `assets/demo.html` + `assets/lenis-demo.css` + `assets/lenis-demo.js`, ADAPT token/section | — | W03 |
| B02 | conditional_required | trang có GSAP ScrollTrigger | driver 2B: `lenis.on('scroll', ScrollTrigger.update)` + `gsap.ticker.add((time) => lenis.raf(time * 1000))` + `gsap.ticker.lagSmoothing(0)`; bỏ hẳn 2A | không GSAP → 2A | W04 |
| B03 | conditional_required | `prefers-reduced-motion: reduce` | không `new Lenis`, cuộn gốc; reveal hiện thẳng bằng CSS/class | — | W04 |
| B04 | user_optional | trang cần thêm pin/cuộn ngang section | khởi tạo Lenis theo skill này TRƯỚC rồi dùng `gsap-scrolltrigger-pin` bên trên | — | W04 |

### Validation và stopping
Xong khi `playwright-verify` cuộn nhanh liên tục không nhảy vị trí giữa `data-ls-reveal` và section chứa nó, và nhánh reduced-motion (qua `page.emulateMedia`) cuộn gốc không Lenis. Code chỉ có MỘT driver raf.

### Examples
- **Positive:** "làm trang landing cuộn mượt kiểu apple có parallax" → chọn pen "Lenis Smooth Scroll & GSAP Page — filipz", copy nguyên `lenis-smooth-scroll-gsap-page.html`, đổi nội dung/ảnh → verify cuộn nhanh không lệch pin, reduced-motion cuộn gốc.
- **Boundary/failure:** code adapt có cả `requestAnimationFrame(raf)` lẫn `gsap.ticker.add(...)` → giật nhẹ liên tục (lỗi #2) → xoá vòng 2A, chỉ giữ 2B, verify lại; quên `* 1000` thì scroll "đơ/bay" (lỗi #3).

## Origin
Batch 180926 — bản gốc NGUYÊN VĂN nằm ở `Rheinmir/uiux-asset/scroll-effects/` (xem mục "Bản gốc" ở trên); `assets/` là bản rút gọn vanilla tự viết.
