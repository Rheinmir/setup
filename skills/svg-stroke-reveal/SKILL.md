---
name: svg-stroke-reveal
description: Vẽ dần nét SVG (stroke-draw) theo cuộn trang hoặc khi vào viewport — đo `path.getTotalLength()`, set `stroke-dasharray`/`stroke-dashoffset`, animate dashoffset từ length về 0. Gọi khi user nói "vẽ svg khi cuộn", "svg stroke draw", "logo vẽ dần", "path animation reveal", "stroke-dashoffset", hoặc /svg-stroke-reveal. KHÁC `skills/scroll-effects` (7 hiệu ứng cuộn chung — reveal/stagger/highlight/nav/top/toc/parallax, KHÔNG có stroke-draw) — skill này chuyên biệt cho SVG `<path>` có NÉT VẼ (logo, chữ ký, biểu đồ đường, hành trình).
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: svg-stroke-reveal

Component vanilla HTML/CSS/JS — nét `<path>` trong SVG "vẽ" dần ra như có tay đang kẻ, theo % cuộn qua viewport hoặc một lần khi vào khung nhìn. Không dùng thư viện ngoài (không Anime.js, không GSAP).

## WHAT

### Purpose và context
- **Purpose:** nét `<path>` trong SVG "vẽ" dần ra theo % cuộn hoặc một lần khi vào viewport (stroke-dasharray/dashoffset), vanilla không lib ngoài; mặc định dùng bản gốc nguyên văn ở `Rheinmir/uiux-asset`.
- **Trigger (when to use):**
  - Logo/chữ ký/icon cần hiệu ứng "vẽ dần" khi vào viewport (chạy 1 lần).
  - Biểu đồ đường, sơ đồ hành trình, đường route cần "vẽ ra" liên tục theo tiến trình cuộn (gắn với vị trí cuộn thật, không phải chạy 1 lần).
  - User nói "vẽ svg khi cuộn", "svg stroke draw", "logo vẽ dần", "path animation reveal", "stroke-dashoffset", hoặc /svg-stroke-reveal.
- **Non-goals:** KHÔNG dùng cho 7 hiệu ứng cuộn chung (opacity/translate reveal, stagger text, highlight, nav co, scroll-to-top, scrollspy, parallax) — đó là `skills/scroll-effects`. Không dùng cho `<text>` chưa convert outline (xem Rules).

### Mental model
`[data-svgr] > <path>×N → getTotalLength() → dasharray = dashoffset = length (ẩn) → mode "once" (IO một lần + CSS transition) hoặc mode "scroll" (IO bật cờ + 1 listener rAF ghi dashoffset theo progress) → reduce-motion: dashoffset = 0 ngay`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | SVG thật của dự án (các `<path>` có nét) | có | `<text>` phải convert outline trước |
| In | mode `once` hoặc `scroll` | có | logo/chữ ký → once; biểu đồ/hành trình → scroll |
| In | `design.md` của dự án | không | có thì đổi token màu theo nó |
| Out | SVG gắn `[data-svgr]` + CSS/JS trong dự án | có | copy nguyên file gốc hoặc adapt `assets/` |
| Out | bằng chứng verify `playwright-verify` | có | ảnh trước/giữa/sau (scroll) + once chỉ trigger 1 lần |

### Rules và capabilities
- RULE-01 (MUST): **`getTotalLength()` đo trên toạ độ nội tại của path, KHÔNG bị ảnh hưởng bởi CSS transform** — nhưng nếu bạn scale phần tử chứa path bằng `transform: scale(sx, sy)` với `sx != sy` (scale KHÔNG ĐỀU hai trục) SAU khi đã set dasharray, tốc độ vẽ theo px sẽ méo lệch giữa hai trục vì animation vẫn chạy theo length gốc trong khi hiển thị đã bị bóp méo tỷ lệ. Luôn set kích thước qua `viewBox` + `width`/`height` đồng nhất tỉ lệ, tránh CSS scale lệch trục trên chính phần tử mang path.
- RULE-02 (MUST): **`<text>` không stroke-draw được** — phải convert chữ/font sang outline `<path>` thật trước (Illustrator "Create Outlines", Figma "Flatten", hoặc tool convert font-to-path) rồi mới áp `[data-svgr]`. Áp thẳng lên `<text>` sẽ không có gì xảy ra vì `<text>` không có `getTotalLength()`.
- RULE-03 (MUST): Mode "once" dùng CSS transition (mượt, rẻ CPU); mode "scroll" set dashoffset trực tiếp mỗi frame qua JS (bắt buộc để đồng bộ khít với vị trí cuộn) — đừng đổi ngược hai cách này.
- RULE-04 (MUST): Một `IntersectionObserver` riêng cho mỗi mode (không gộp chung logic once/scroll vào 1 observer vì hành vi khác nhau: unobserve-1-lần vs toggle cờ liên tục) và một scroll listener rAF-throttle DUY NHẤT cho tất cả SVG mode "scroll" trên trang — không gắn nhiều listener `scroll` rời cho mỗi SVG.
- RULE-05 (MUST): Verify bằng `playwright-verify`: chụp trước/giữa/sau khi cuộn qua SVG mode "scroll" để thấy dashoffset giảm dần, và assert SVG mode "once" chỉ trigger 1 lần dù cuộn ra vào nhiều lần.
- Capabilities: đọc bản gốc (web/git) + asset skill + `design.md`; ghi HTML/CSS/JS vào dự án đích; chạy trình duyệt headless để verify.

### Failure boundaries
- Áp lên `<text>` chưa convert outline → không có gì xảy ra: **blocked**, yêu cầu convert sang `<path>` trước (RULE-02).
- Phần tử mang path bị CSS scale lệch trục → tốc độ vẽ méo: **failed**, chuyển kích thước qua `viewBox` + `width`/`height` (RULE-01).
- Assert verify đỏ (dashoffset không giảm dần, once trigger lại) → **failed**, sửa rồi verify lại.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | judgment | SVG + yêu cầu | Chọn mode `once` hay `scroll`; kiểm SVG đã là `<path>` (không `<text>`) | mode | `<text>` → blocked tới khi convert |
| W02 | effect | bảng Pen gốc | Mở link **chạy**, copy nguyên file `.html` (+ `_assets/`) vào dự án, giữ comment ghi công | file gốc trong dự án | không được kéo lib ngoài → B01 |
| W03 | effect | file + SVG thật + `design.md` | Chỉ sửa nội dung/ảnh/màu (thay path `d=`) | SVG đã adapt | — |
| W04 | deterministic | trang chạy qua HTTP | Verify bằng `playwright-verify` (RULE-05) | ảnh + assert | đỏ → sửa, lặp W04 |

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | dự án KHÔNG được kéo lib ngoài (bản gốc) | dùng bản rút gọn vanilla `assets/` (mục Reference — Assets), đọc rồi ADAPT | — | W04 |
| B02 | conditional_required | `prefers-reduced-motion: reduce` | `strokeDashoffset = 0` ngay lúc init, bỏ observer/listener | — | W04 |

### Validation và stopping
Assert tất định ở W04 (mode scroll: dashoffset giảm dần qua ảnh trước/giữa/sau; mode once: chỉ trigger 1 lần dù cuộn ra vào). Cần mắt: độ mượt, thứ tự nét. Dừng khi assert xanh.

### Examples
- **Positive:** "logo vẽ dần khi vào màn hình" → `data-svgr="once"` trên logo 4 path → vào viewport 30% thì vẽ lần lượt (stagger 160ms theo thứ tự DOM), cuộn ra vào lại không vẽ lại.
- **Boundary/failure:** chữ ký là `<text>` font script → không có `getTotalLength()`, không vẽ gì → dừng, yêu cầu convert outline (Figma "Flatten") thành `<path>` rồi mới áp `[data-svgr]`.

### Reference — Bản gốc — dùng TRƯỚC (copy nguyên file, đừng viết lại)
Code gốc NGUYÊN VĂN của tác giả (CodePen public = MIT) nằm ở repo ngoài **`Rheinmir/uiux-asset`** — gallery chạy thật: https://rheinmir.github.io/uiux-asset/scroll-effects/ .
Quy trình: mở link **chạy** để xem đúng hiệu ứng → copy nguyên file `.html` (+ thư mục `_assets/` nếu file trỏ tới) vào dự án → giữ comment ghi công dòng đầu → chỉ sửa nội dung/ảnh/màu. Chạy local qua HTTP, không `file://`.
`git clone --depth 1 https://github.com/Rheinmir/uiux-asset` nếu cần cả bộ offline.

| Pen gốc — tác giả | Link |
|---|---|
| Interactive Cicada Genomics Landing Page — alyona-mysiura | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/interactive-cicada-genomics-landing-page.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/interactive-cicada-genomics-landing-page.html) |
| Scroll-Driven SVG Map Editorial Gallery — knyttneve | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/scroll-driven-svg-map-editorial-gallery.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/scroll-driven-svg-map-editorial-gallery.html) |
| Scroll-Driven Godzilla Walk-and-Destroy Animation — creativeocean | [chạy](https://rheinmir.github.io/uiux-asset/scroll-effects/scroll-driven-godzilla-walk-and-destroy-animation.html) · [code](https://github.com/Rheinmir/uiux-asset/blob/main/scroll-effects/scroll-driven-godzilla-walk-and-destroy-animation.html) |

`assets/` trong skill này chỉ là bản rút gọn vanilla tự viết — dùng khi dự án KHÔNG được kéo lib ngoài; mặc định dùng bản gốc ở trên.

### Reference — Assets
`assets/demo.html` + `assets/svg-stroke-reveal.css` + `assets/svg-stroke-reveal.js` — đọc rồi ADAPT vào SVG thật của dự án (thay path `d=`, đổi token màu theo `design.md` nếu có), không copy máy móc.

### Reference — Cơ chế
- Với MỖI `<path>` trong `[data-svgr]`: JS gọi `path.getTotalLength()`, set inline `style.strokeDasharray = length` và `style.strokeDashoffset = length` lúc init → nét ẩn hoàn toàn (dash đúng bằng chiều dài path, offset đẩy hết dash ra ngoài).
- **Mode `data-svgr="once"`** (threshold 1 lần — logo/chữ ký): `IntersectionObserver` threshold 0.3, khi vào viewport → set `strokeDashoffset = 0` cho tất cả path con → CSS `transition: stroke-dashoffset` chạy 1 lần → `unobserve` ngay sau khi trigger, không lặp lại kể cả cuộn ra rồi cuộn lại.
- **Mode `data-svgr="scroll"`** (progress liên tục — biểu đồ/hành trình): `IntersectionObserver` chỉ bật/tắt cờ "đang trong viewport"; khi đang bật, một scroll listener rAF-throttle (dùng chung 1 listener, không tạo nhiều) tính `progress = (innerHeight - rect.top) / (innerHeight + rect.height)` kẹp 0..1, rồi ghi trực tiếp `strokeDashoffset = length * (1 - progress)` mỗi frame — KHÔNG dùng CSS transition ở mode này (transition sẽ làm nét trễ nhịp so với vị trí cuộn thật).
- Path phức tạp nhiều `<path>` con (logo nhiều nét, chữ ký) — mode "once" stagger bằng `transition-delay: calc(var(--svgr-i) * 160ms)`, JS gán `--svgr-i` theo THỨ TỰ path trong DOM (path đầu vẽ trước).
- `prefers-reduced-motion: reduce` → JS set `strokeDashoffset = 0` ngay cho toàn bộ path lúc init, bỏ qua cả hai observer/listener — hiện full nét tức thì, không animate.

## Origin
