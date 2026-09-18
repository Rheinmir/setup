---
type: draft
title: "Scroll-effect reference gallery — freefrontend.com/javascript-scroll-effects (80 mục, 4 trang, chỉ link tham khảo)"
status: done
tags: [reference, frontend, scroll, animation, external-link]
timestamp: 2026-09-18
---

# Scroll-effect reference gallery

**Mục đích:** danh sách TRA CỨU cho downstream/phiên sau khi cần cảm hứng kỹ thuật hiệu ứng cuộn trang — KHÔNG phải code đã vendor vào repo. Tác giả đã xác minh tới cấp profile CodePen (fetch HTML 4 trang, ghép từng block theo đúng thứ tự). Cột "MIT" là nhãn freefrontend.com tự gắn từng mục — KHÔNG verify được từ trang pen gốc (CodePen chặn fetch trực tiếp: 403/socket, oEmbed cũng lỗi transport), nên chủ động KHÔNG chép code vào đây. Muốn dùng thật: mở link, tự đọc + xin phép/verify license với tác giả, hoặc viết lại bản GỐC theo đúng kỹ thuật mô tả (như `skills/blur/`, `skills/timeline/`, `skills/scroll-effects/` đã làm).

## Trang 1 (20 mục)

| # | Tên | Kỹ thuật | Trường hợp dùng | Tác giả (CodePen) |
|---|-----|----------|------------------|---------------------|
| 1 | Interactive Cicada Genomics Landing Page | GSAP ScrollTrigger morph SVG stroke-drawing (tree → butterfly wings) | Landing page khoa học/dữ liệu cần kể chuyện qua hình minh hoạ biến đổi | alyona-mysiura |
| 2 | Interactive Variable Font GSAP Slideshow | Slider full-page nhiều lớp, split-wipe reveal, variable-font width kéo dãn | Slideshow portfolio/case-study nhấn typography động | Cassie Evans (cassie-codes) |
| 3 | Native CSS Scroll Snap Time Picker | CSS Scroll Snap Events API, bánh xe chọn ngày/giờ kiểu mobile | Form chọn ngày/giờ mobile-first không cần JS picker nặng | Adam Argyle (argyleink) |
| 4 | Observer-Animated Responsive Vertical Timeline | IntersectionObserver fade+slide, layout tách đôi responsive | Timeline sự kiện/lịch sử — **đã có bản GỐC tương đương ở `skills/timeline/`** | Jon Kantner (jkantner) |
| 5 | Interactive 3D Sphere Image Gallery | Canvas render ảnh lên cầu 3D xoay, glitch + phóng to full-screen | Gallery ảnh sáng tạo, portfolio nhiếp ảnh/nghệ thuật | Toshiya Marukubo (toshiya-marukubo) |
| 6 | Scroll-Driven SVG Map Editorial Gallery | Bản đồ vector động theo scroll + gallery ảnh xen kẽ | Bài viết du lịch/editorial dạng long-form có bản đồ minh hoạ | Mert Cukuren (knyttneve) |
| 7 | Scroll-Driven Godzilla Walk-and-Destroy Animation | Nhân vật sprite đi theo path SVG khi cuộn ngang, particle effect | Trang quảng bá/sự kiện cần kể chuyện hoạt hình vui theo cuộn ngang | Tom Miller (creativeocean) |
| 8 | Scroll-Driven Particle WebGL Image Matrix | Three.js 50.000 hạt cube hội tụ thành ảnh chân dung theo scroll | Hero section gây ấn tượng mạnh, brand/portfolio cao cấp | ycw |
| 9 | Animated Scroll Highlight Annotations | Đánh dấu đoạn văn nổi bật dần khi cuộn tới | Blog/tài liệu dài cần dẫn mắt người đọc tới ý chính | Jhey (jh3y) |
| 10 | Smooth Parallax Image Scroll Gallery | Parallax trục Y độc lập cho từng ảnh có mask | Gallery ảnh chiều sâu, landing page sản phẩm | Denis Gusev (gusevdigital) |
| 11 | Staggered Text Scroll Reveal | Tách dòng chữ, hiện lần lượt (stagger) khi vào viewport | Hero heading/tiêu đề cần điểm nhấn chữ chạy vào | Denis Gusev (gusevdigital) |
| 12 | Twisted Wave GLSL Image Gallery | WebGL sine-wave distortion khi hover + radial blur theo tốc độ cuộn | Gallery thời trang/nghệ thuật cần hiệu ứng "sang" khác biệt | alphardex |
| 13 | GSAP ScrollTrigger List Expansion | Card xếp chồng giãn ra khi cuộn, giống Notification Center iOS | Danh sách thông báo/feature list cần mở rộng mượt khi cuộn tới | Aaron Iker (aaroniker) |
| 14 | Cinematic Zoom Blur Image Gallery | GLSL shader + Three.js radial-blur transition giữa các ảnh | Slideshow ảnh điện ảnh — **đã có bản GỐC tương đương ở `skills/blur/`** | Kevin Levron (soju22) |
| 15 | Scroll-Driven Jigsaw Puzzle Assembler | Mảnh SVG bay từ mép màn hình, ráp thành ảnh hoàn chỉnh khi cuộn | Trang chơi/sự kiện cần hiệu ứng "ráp hình" gây tò mò | Charlotte Dann (pouretrebelle) |
| 16 | Lenis Smooth Scroll & GSAP Page | Lenis (physics-based smooth scroll) + GSAP stagger + clip-path reveal | Trang cần cảm giác cuộn mượt kiểu Apple/agency cao cấp | Filip Zrnzevic (filipz) |
| 17 | Lenis Smooth Scroll Cinematic Experience | Lenis + chuỗi cảnh cinematic phức tạp cho portfolio | Portfolio cá nhân/agency muốn trải nghiệm cuộn như phim | Filip Zrnzevic (filipz) |
| 18 | Shattering Image Gallery Transition | WebGL vỡ ảnh thành hạt 3D rồi lộ ảnh bên dưới | Chuyển ảnh gây ấn tượng cho gallery nghệ thuật/thời trang | Kevin Levron (soju22) |
| 19 | Auto-Generated Anchor Positioned TOC | Tự đọc heading bài viết, dựng mục lục sticky có highlight theo vị trí đọc | Tài liệu/blog dài cần mục lục điều hướng thông minh | Jhey (jh3y) |
| 20 | Glassmorphic Advanced Navigation System | Thanh điều hướng kính mờ nổi, tự đổi bố cục mobile/desktop | Nav bar cho SPA cần thẩm mỹ liquid-glass hiện đại | themrsami |

## Trang 2 (20 mục)

| # | Tên | Kỹ thuật | Trường hợp dùng | Tác giả (CodePen) |
|---|-----|----------|------------------|---------------------|
| 1 | Infinite 3D Poster Scroll Wall | WebGL, lưới poster cuộn vô hạn dày đặc | Trang khoe portfolio/case-study dạng lưới ảnh lớn | James Dow (photodow) |
| 2 | Smooth Scroll Stacking Accordion | Scroll-driven thay accordion click bằng xếp chồng card pin lại | Danh sách FAQ/feature cần cảm giác tương tác mới lạ hơn accordion thường | Fabio Ottaviani (supah) |
| 3 | Smooth 3D Scroll-Driven Reveal | Cuộn có momentum riêng + transform 3D phức tạp cho gallery | Gallery ảnh cao cấp cần cảm giác cuộn "nặng tay" có chủ đích | DivineBlow |
| 4 | Scroll-Driven Dynamic Marquee Frame | Ticker chạy viền quanh viewport phản ánh tiêu đề section đang xem | Trang portfolio/landing cần khung trang trí động theo scroll | Ryan Mulligan |
| 5 | Pinned Split-Screen Mask Reveal | Ảnh cố định + text chảy đồng bộ, chuyển cảnh kiểu điện ảnh | Case-study/portfolio cần layout 2 cột đồng bộ ảnh-chữ | gridmorphic |
| 6 | Parallax Jungle Leaves Reveal | Lá SVG tách ra khi cuộn, lộ logo chữ ở giữa | Trang chủ thương hiệu cần màn mở đầu ấn tượng | Louis Hoebregts (Mamboleoo) |
| 7 | Scroll-Triggered Text Highlights | Highlight chữ chạy trái→phải khi đoạn văn vào khung nhìn | Blog/tài liệu cần nhấn từng câu quan trọng | Ryan Mulligan |
| 8 | Scroll-Driven Image Swapper | Native CSS Scroll-driven Animations API, crossfade kiểu parallax | Gallery/hero cần hiệu ứng chuyển ảnh KHÔNG cần JS nặng | Jhey (jh3y) |
| 9 | Sticky Observer Navigation | Header co lại + ẩn tiêu đề khi cuộn, tối ưu hiệu năng | Header site cần tiết kiệm không gian khi cuộn xuống | Claire Larsen (ClaireLarsen) |
| 10 | ScrollMagic Pizza Assembly Animation | Nguyên liệu pizza bay từ nhiều hướng ráp lại khi cuộn | Trang quảng bá F&B cần hiệu ứng vui, dễ nhớ thương hiệu | Sandip Dust (SandipDust) |
| 11 | Ink Transition Scroll Effect | Ảnh lộ ra qua mask vết mực loang khi cuộn | Chuyển ảnh nghệ thuật, portfolio sáng tạo | Ryan Yu (iamryanyu) |
| 12 | Smooth Parallax Scroll Layout | Cuộn mượt + animation so le + parallax cho portfolio | Portfolio cá nhân cần cảm giác cuộn "mượt" tổng thể | Pete Barr (petebarr) |
| 13 | Perspective Zoom Effect on Scroll | Bay xuyên qua đám mây ảnh phối cảnh, chữ hiện dần | Trang giới thiệu sản phẩm/dịch vụ cần mở đầu choáng ngợp | iamryanyu |
| 14 | Oreo, Smash, Donuts, etc. | Chuỗi thử nghiệm chữ khối 3D dùng preserve-3d | Thử nghiệm/demo kiểu chữ 3D cho trang sáng tạo | ste-vg |
| 15 | GSAP ScrollSmoother and Three.js | Chữ mượt kết hợp trường hạt 3D đồng bộ theo cuộn | Hero section cao cấp kết hợp typography + particle 3D | cmalven |
| 16 | Scroll UI Animation | Ảnh thu nhỏ + đếm số phần trăm động | Dashboard/landing cần hiển thị chỉ số tiến trình sinh động | daniel-hult |
| 17 | Smooth Scrolling with GSAP ScrollSmoother | CSS Grid + parallax tốc độ khác nhau theo `data-speed` | Layout dạng lưới cần từng ô trôi tốc độ riêng khi cuộn | GreenSock (tài khoản chính thức) |
| 18 | Physics Milestones Timeline | Timeline dọc, card sự kiện trượt vào từ hai bên xen kẽ | Timeline lịch sử/mốc dự án — cân nhắc so với `skills/timeline/` trước | januaryofmine |
| 19 | CSS Scroll-Driven Content Wave | Hiệu ứng ống kính mắt cá phản ứng theo input cuộn | Trang thử nghiệm/sáng tạo cần hiệu ứng thị giác lạ | Jhey (jh3y) |
| 20 | Scroll-Driven Content Wave #2 | Cuộn ngang + hiệu ứng ống kính qua CSS Scroll-Driven Animations | Biến thể ngang của mục 19, cùng nhóm kỹ thuật | Jhey (jh3y) |

## Trang 3 (20 mục)

| # | Tên | Kỹ thuật | Trường hợp dùng | Tác giả (CodePen) |
|---|-----|----------|------------------|---------------------|
| 1 | Open Props Bento Grid | Lưới bento tự ráp mượt khi cuộn | Trang portfolio/sản phẩm dùng layout bento hiện đại | mobalti |
| 2 | Inertial Scroll Gallery with 3D Transforms | Gallery "hijack" scroll giả lập quán tính qua container ảo | Gallery ảnh cao cấp cần cảm giác cuộn có quán tính riêng | lmgonzalves |
| 3 | GSAP ScrollTrigger Parallax Effect | Nhiều lớp parallax + text reveal, ví dụ mẫu mực scroll-driven | Học/tham khảo kỹ thuật parallax nhiều lớp chuẩn GSAP | celli |
| 4 | Horizontal Scroll Section with GSAP and Locomotive Scroll | Pin section, đổi cuộn dọc thành cuộn ngang kiểu kinh điển | Case-study/portfolio muốn 1 section cuộn ngang giữa trang dọc | cameronknight |
| 5 | Sliding List with Scroll-Driven Animations | 1 scroll listener tính progress riêng từng item, stagger reveal | Danh sách feature/sản phẩm cần hiện lần lượt mượt, ít listener | stevenlei |
| 6 | Infinite Scrolling with Image Cards | Lưới ảnh cuộn vô hạn qua IntersectionObserver + Pixabay API | Gallery/blog ảnh cần infinite-scroll nhẹ, không cần backend riêng | Jon Kantner (jkantner) |
| 7 | Scroll-Driven Web Gears Animation | Demo kỹ thuật `animation-timeline` CSS, fallback GSAP ScrollTrigger | Tham khảo cách fallback CSS-native sang GSAP khi cần | Jhey (jh3y) |
| 8 | Infinite Scrollable and Draggable WebGL Grid | THREE.js lưới vô hạn có bọc toạ độ (coordinate wrapping) | Portfolio/gallery cần lưới WebGL kéo-cuộn vô hạn hiệu năng cao | ReGGae |
| 9 | Vanilla JS Skew Images on Scroll | Ảnh nghiêng (skew) theo vận tốc cuộn, JS thuần | Hiệu ứng nhẹ không cần thư viện, thêm động lực khi cuộn nhanh | vstefanova |
| 10 | Animated Scroll-Triggered Timeline | Timeline dọc mượt, JS thuần — so sánh với `skills/timeline/` | Timeline đơn giản không muốn thêm dependency ngoài | gaganagarwal092 |
| 11 | CSS Glitchy Text Reveal with Splitting.js | Tách từng ký tự, hiệu ứng glitch ngẫu nhiên | Hero/tiêu đề cần điểm nhấn "glitch" cá tính | Jhey (jh3y) |
| 12 | Text Reveal (on Scroll) Effect | IntersectionObserver + GSAP wipe mượt | Reveal chữ thanh lịch cho landing page nghiêm túc | Le_Petit_Garage |
| 13 | Dinosaur Park Scroll Snap Reveal Demo | Reveal phần tử qua IntersectionObserver + CSS Custom Properties | Trang minh hoạ/giáo dục cần scroll-snap theo section | michellebarker |
| 14 | Efficient Image Scroll Zoom Effect | Zoom ảnh theo scroll, tối ưu bằng tính visibility + IntersectionObserver | Gallery ảnh cần zoom mượt mà không giật hiệu năng | CAWeissen |
| 15 | Pixelated Lazy Load for Images | Lazy-load thay placeholder pixelated bằng ảnh full-res | Trang nhiều ảnh cần lazy-load có hiệu ứng chuyển đẹp hơn blur thường | markmead |
| 16 | Layout Explorations with GSAP, Flip, Lenis and ScrollTrigger N°2 | GSAP Flip cho transition phức tạp + debounce mouse event | Portfolio thử nghiệm layout động nhiều lớp kỹ thuật kết hợp | filipz |
| 17 | Cinematic Glitch Slideshow | WebGL shader méo kiểu VHS + pixelation khi chuyển slide | Slideshow phong cách retro/glitch — biến thể khác `skills/blur/` | filipz |
| 18 | Codepen Challenge: Article Details | IntersectionObserver làm nav "smart-scroll" highlight section đang đọc | Bài viết dài cần nav bám theo section đang đọc | Sicontis |
| 19 | Animated Continuous Sections with GSAP | Full-page scroller vòng lặp vô hạn + split-reveal + stagger text | Trang trình bày dạng slide liên tục không điểm dừng | GreenSock (tài khoản chính thức) |
| 20 | Scroll-Based Reveal Animations with ScrollTrigger | GSAP animation điều khiển hiện/ẩn qua callback scroll | Tham khảo pattern callback-driven cơ bản của ScrollTrigger | GreenSock (tài khoản chính thức) |

## Trang 4 (20 mục)

| # | Tên | Kỹ thuật | Trường hợp dùng | Tác giả (CodePen) |
|---|-----|----------|------------------|---------------------|
| 1 | Wave and RGB Image Distortion with Shaders | Three.js shader làm ảnh "sống", méo theo cuộn | Hero ảnh sản phẩm/thời trang cần hiệu ứng shader độc đáo | Ryan Yu (iamryanyu) |
| 2 | Infinite Horizontal Scroll with Progress Tracking | Cuộn ngang toàn màn hình, vòng lặp vô hạn + thanh tiến trình | Gallery/portfolio cuộn ngang cần chỉ báo tiến trình rõ | haptichash |
| 3 | Three.js 3D Model Animation with GSAP ScrollTrigger | Load model 3D + ánh sáng thể tích đồng bộ scroll | Landing page sản phẩm 3D (giày, xe, thiết bị...) | yudizsolutions |
| 4 | GSAP ScrollTrigger Disintegration Effect | Hiệu ứng "tan rã" tuỳ biến điều khiển bằng scroll | Chuyển cảnh ấn tượng cho trang sự kiện/ra mắt sản phẩm | dev_loop |
| 5 | Scrolling Text Animation | Chữ chạy đồng bộ theo chuyển động cuộn | Hiệu ứng chữ chạy nhẹ, không cần thư viện nặng | Adir-SL |
| 6 | Scroll Animation with SVG Clip Path and GSAP | Clip-path SVG phối hợp theo hành vi cuộn | Reveal hình dạng tuỳ biến (không chỉ chữ nhật) khi cuộn | Tiopayo |
| 7 | Movie Stacking Animation with GSAP ScrollTrigger | Card xếp chồng kiểu poster phim khi cuộn | Trang giới thiệu phim/media, gallery dạng chồng thẻ | quicksilversel |
| 8 | Parallax Scroll Animation with GSAP | Parallax nhiều lớp dùng GSAP | Parallax cơ bản, điểm khởi đầu học kỹ thuật này | isladjan |
| 9 | Responsive and SEO-Friendly WebGL Text | Chữ WebGL tối ưu responsive + SEO | Hero chữ 3D cần vẫn đọc được bởi search engine | (vô danh trên freefrontend; bài gốc trên tympanus.net/codrops) |
| 10 | Little Book of Jhey with ScrollTrigger | Giao diện kiểu sách lật trang theo scroll | Trang kể chuyện dạng sách, case-study nhiều chương | Jhey (jh3y) |
| 11 | Mini Wheel Menu with GSAP Observer | Menu radial điều khiển bằng GSAP Observer | Menu điều hướng dạng bánh xe cho app/game nhỏ | Tom Miller (creativeocean) |
| 12 | Layout Explorations N°5 | Thử nghiệm layout GSAP + Lenis + ScrollTrigger | Nguồn cảm hứng bố cục cuộn nâng cao, nhiều biến thể | filipz |
| 13 | Scroll-Accelerated Vertical Gallery | Gallery dọc lặp vô hạn, tăng tốc theo tốc độ cuộn | Gallery ảnh cần phản hồi trực tiếp theo lực cuộn của user | cameronknight |
| 14 | SVG Filter Scroll Reveal | Filter SVG làm nội dung lộ dần khi cuộn | Reveal nội dung qua hiệu ứng filter thay vì opacity/transform thường | nocni_sovac |
| 15 | Curved Scrollbar '25 | Thanh cuộn tuỳ biến hình cong | Chi tiết UI nhỏ tạo dấu ấn riêng cho scrollbar | Jhey (jh3y) |
| 16 | GSAP + ScrollTrigger Explorations | Bộ sưu tập animation thử nghiệm GSAP/ScrollTrigger | Kho tham khảo nhiều pattern nhỏ cùng lúc | filipz |
| 17 | Scroll to Type with CSS | Hiệu ứng gõ chữ điều khiển bằng vị trí cuộn, thuần CSS | Hiệu ứng "đang gõ" không cần JS, nhẹ | Jhey (jh3y) |
| 18 | SVG Stroke Animation with Anime.js | Nét vẽ SVG animate bằng Anime.js | Logo/icon vẽ dần khi vào viewport | HejChristian |
| 19 | Falling Text with Gravity | Chữ rơi mô phỏng trọng lực thật | Hiệu ứng chơi/404 page/easter-egg | osmosupply |
| 20 | CSS Isometric Card Grid | Lưới thẻ isometric 3D điều khiển bằng virtual scroll | Trang portfolio/case-study muốn trình bày dạng thẻ 3D độc đáo | Jon Kantner (jkantner) |

(Tổng: 20 + 20 + 20 + 20 = 80 mục.)

Nguồn gốc từng mục: `https://freefrontend.com/javascript-scroll-effects/` trang 1-4 — mỗi mục có link CodePen riêng (dạng `codepen.io/anon/pen/...` đã ẩn danh hoá), tác giả xác định qua profile link `codepen.io/<tên>` kề mỗi mục. Tự mở pen bằng cách search đúng tên + tác giả trên CodePen.

## Origin
- Yêu cầu user 180926: "clone hết pattern [scroll-to-top]" → tra ra trang đó chỉ có 1 demo, không khớp kỳ vọng "danh sách". User đưa link đúng: `freefrontend.com/javascript-scroll-effects`.
- Bản đầu ghi "nhiều mục không ghi tác giả" — **SAI, đã đính chính 180926**: lỗi do text-extract làm rớt dòng tác giả. Fetch lại HTML 4 trang + ghép block theo thứ tự → **80/80 mục có tác giả** (chỉ 1 mục vô danh: #9 trang 4, nguồn gốc là bài Codrops). Không còn mục "không rõ" nào.
- User bảo "nó mit hết mà" + gửi `freefrontend.dev/terms/` — **hai điểm cần tách bạch**: (1) freefrontend.**dev** là site KHÁC (Bootstrap/Tailwind snippets, Arizona), terms của nó (free dùng personal/commercial, cấm resell as-is) KHÔNG áp cho freefrontend.**com**; (2) freefrontend.**com** (Vladimir, one-person) ghi "Copy-Paste Friendly — Grab it, paste it, tweak it", mỗi snippet gắn nhãn "MIT" — nhưng đó vẫn là nhãn của site trung gian, không phải license verbatim từ trang pen gốc (CodePen chặn fetch trực tiếp: HTTP 403 / socket closed, oEmbed cũng lỗi transport). Vì vậy giữ luật KHÔNG chép code hàng loạt vào repo.
- User làm rõ ý thật: "downstream tham khảo code mẫu" (reference, không phải vendor/redistribute) → bảng LINK + KỸ THUẬT + TRƯỜNG HỢP DÙNG + TÁC GIẢ, không chép code.
- 2 mục đã có bản triển khai GỐC sống ở `skills/timeline/` (#4 trang 1) và `skills/blur/` (#14 trang 1). Sau khi user chốt "làm đi hỏi nhiều quá", đã viết thêm `skills/scroll-effects/` — 7 pattern generic gốc viết tay (reveal, stagger, highlight, shrink-nav, scroll-to-top, scrollspy TOC, parallax nhẹ), vì các kỹ thuật này là chuẩn ngành không phải biểu đạt riêng của ai. Hàng xịn WebGL/GSAP còn lại muốn đạt chất lượng tương đương thì làm từng mục (viết lại gốc hoặc verify license + attribution), không có đường bulk.
