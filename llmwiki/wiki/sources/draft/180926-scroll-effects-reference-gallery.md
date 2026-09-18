---
type: draft
title: "Scroll-effect reference gallery — freefrontend.com/javascript-scroll-effects (81 mục, 4 trang, chỉ link tham khảo)"
status: open
tags: [reference, frontend, scroll, animation, external-link]
timestamp: 2026-09-18
---

# Scroll-effect reference gallery

**Mục đích:** danh sách TRA CỨU cho downstream/phiên sau khi cần cảm hứng kỹ thuật hiệu ứng cuộn trang — KHÔNG phải code đã vendor vào repo. Không đủ căn cứ xác minh license gốc của từng tác giả CodePen (freefrontend chỉ tự gắn nhãn "MIT", CodePen chặn fetch trực tiếp để verify — xem `## Origin`), nên chủ động KHÔNG chép code vào đây. Muốn dùng thật: mở link, tự đọc + xin phép/verify license với tác giả, hoặc viết lại bản GỐC theo đúng kỹ thuật mô tả (như `skills/blur/` đã làm).

## Trang 1 (20 mục)

| # | Tên | Kỹ thuật | Trường hợp dùng | Tác giả (CodePen) |
|---|-----|----------|------------------|---------------------|
| 1 | Interactive Cicada Genomics Landing Page | GSAP ScrollTrigger morph SVG stroke-drawing (tree → butterfly wings) | Landing page khoa học/dữ liệu cần kể chuyện qua hình minh hoạ biến đổi | alyona-mysiura |
| 2 | Interactive Variable Font GSAP Slideshow | Slider full-page nhiều lớp, split-wipe reveal, variable-font width kéo dãn | Slideshow portfolio/case-study nhấn typography động | Cassie Evans |
| 3 | Native CSS Scroll Snap Time Picker | CSS Scroll Snap Events API, bánh xe chọn ngày/giờ kiểu mobile | Form chọn ngày/giờ mobile-first không cần JS picker nặng | Adam Argyle |
| 4 | Observer-Animated Responsive Vertical Timeline | IntersectionObserver fade+slide, layout tách đôi responsive | Timeline sự kiện/lịch sử — **đã có bản GỐC tương đương ở `skills/timeline/`** | Jon Kantner |
| 5 | Interactive 3D Sphere Image Gallery | Canvas render ảnh lên cầu 3D xoay, glitch + phóng to full-screen | Gallery ảnh sáng tạo, portfolio nhiếp ảnh/nghệ thuật | Toshiya Marukubo |
| 6 | Scroll-Driven SVG Map Editorial Gallery | Bản đồ vector động theo scroll + gallery ảnh xen kẽ | Bài viết du lịch/editorial dạng long-form có bản đồ minh hoạ | Mert Cukuren |
| 7 | Scroll-Driven Godzilla Walk-and-Destroy Animation | Nhân vật sprite đi theo path SVG khi cuộn ngang, particle effect | Trang quảng bá/sự kiện cần kể chuyện hoạt hình vui theo cuộn ngang | Tom Miller |
| 8 | Scroll-Driven Particle WebGL Image Matrix | Three.js 50.000 hạt cube hội tụ thành ảnh chân dung theo scroll | Hero section gây ấn tượng mạnh, brand/portfolio cao cấp | ycw |
| 9 | Animated Scroll Highlight Annotations | Đánh dấu đoạn văn nổi bật dần khi cuộn tới | Blog/tài liệu dài cần dẫn mắt người đọc tới ý chính | Jhey |
| 10 | Smooth Parallax Image Scroll Gallery | Parallax trục Y độc lập cho từng ảnh có mask | Gallery ảnh chiều sâu, landing page sản phẩm | Denis Gusev |
| 11 | Staggered Text Scroll Reveal | Tách dòng chữ, hiện lần lượt (stagger) khi vào viewport | Hero heading/tiêu đề cần điểm nhấn chữ chạy vào | Denis Gusev |
| 12 | Twisted Wave GLSL Image Gallery | WebGL sine-wave distortion khi hover + radial blur theo tốc độ cuộn | Gallery thời trang/nghệ thuật cần hiệu ứng "sang" khác biệt | alphardex |
| 13 | GSAP ScrollTrigger List Expansion | Card xếp chồng giãn ra khi cuộn, giống Notification Center iOS | Danh sách thông báo/feature list cần mở rộng mượt khi cuộn tới | Aaron Iker |
| 14 | Cinematic Zoom Blur Image Gallery | GLSL shader + Three.js radial-blur transition giữa các ảnh | Slideshow ảnh điện ảnh — **đã có bản GỐC tương đương ở `skills/blur/`** | Kevin Levron |
| 15 | Scroll-Driven Jigsaw Puzzle Assembler | Mảnh SVG bay từ mép màn hình, ráp thành ảnh hoàn chỉnh khi cuộn | Trang chơi/sự kiện cần hiệu ứng "ráp hình" gây tò mò | Charlotte Dann |
| 16 | Lenis Smooth Scroll & GSAP Page | Lenis (physics-based smooth scroll) + GSAP stagger + clip-path reveal | Trang cần cảm giác cuộn mượt kiểu Apple/agency cao cấp | Filip Zrnzevic |
| 17 | Lenis Smooth Scroll Cinematic Experience | Lenis + chuỗi cảnh cinematic phức tạp cho portfolio | Portfolio cá nhân/agency muốn trải nghiệm cuộn như phim | Filip Zrnzevic |
| 18 | Shattering Image Gallery Transition | WebGL vỡ ảnh thành hạt 3D rồi lộ ảnh bên dưới | Chuyển ảnh gây ấn tượng cho gallery nghệ thuật/thời trang | Kevin Levron |
| 19 | Auto-Generated Anchor Positioned TOC | Tự đọc heading bài viết, dựng mục lục sticky có highlight theo vị trí đọc | Tài liệu/blog dài cần mục lục điều hướng thông minh | Jhey |
| 20 | Glassmorphic Advanced Navigation System | Thanh điều hướng kính mờ nổi, tự đổi bố cục mobile/desktop | Nav bar cho SPA cần thẩm mỹ liquid-glass hiện đại | themrsami |

## Trang 2 (20 mục)

| # | Tên | Kỹ thuật | Trường hợp dùng | Tác giả (CodePen) |
|---|-----|----------|------------------|---------------------|
| 1 | Infinite 3D Poster Scroll Wall | WebGL, lưới poster cuộn vô hạn dày đặc | Trang khoe portfolio/case-study dạng lưới ảnh lớn | James Dow |
| 2 | Smooth Scroll Stacking Accordion | Scroll-driven thay accordion click bằng xếp chồng card pin lại | Danh sách FAQ/feature cần cảm giác tương tác mới lạ hơn accordion thường | Fabio Ottaviani |
| 3 | Smooth 3D Scroll-Driven Reveal | Cuộn có momentum riêng + transform 3D phức tạp cho gallery | Gallery ảnh cao cấp cần cảm giác cuộn "nặng tay" có chủ đích | Sebi |
| 4 | Scroll-Driven Dynamic Marquee Frame | Ticker chạy viền quanh viewport phản ánh tiêu đề section đang xem | Trang portfolio/landing cần khung trang trí động theo scroll | Ryan Mulligan |
| 5 | Pinned Split-Screen Mask Reveal | Ảnh cố định + text chảy đồng bộ, chuyển cảnh kiểu điện ảnh | Case-study/portfolio cần layout 2 cột đồng bộ ảnh-chữ | grid morphic |
| 6 | Parallax Jungle Leaves Reveal | Lá SVG tách ra khi cuộn, lộ logo chữ ở giữa | Trang chủ thương hiệu cần màn mở đầu ấn tượng | Louis Hoebregts |
| 7 | Scroll-Triggered Text Highlights | Highlight chữ chạy trái→phải khi đoạn văn vào khung nhìn | Blog/tài liệu cần nhấn từng câu quan trọng | Ryan Mulligan |
| 8 | Scroll-Driven Image Swapper | Native CSS Scroll-driven Animations API, crossfade kiểu parallax | Gallery/hero cần hiệu ứng chuyển ảnh KHÔNG cần JS nặng | Jhey Tompkins |
| 9 | Sticky Observer Navigation | Header co lại + ẩn tiêu đề khi cuộn, tối ưu hiệu năng | Header site cần tiết kiệm không gian khi cuộn xuống | Claire Larsen |
| 10 | ScrollMagic Pizza Assembly Animation | Nguyên liệu pizza bay từ nhiều hướng ráp lại khi cuộn | Trang quảng bá F&B cần hiệu ứng vui, dễ nhớ thương hiệu | Sandip Dust |
| 11 | Ink Transition Scroll Effect | Ảnh lộ ra qua mask vết mực loang khi cuộn | Chuyển ảnh nghệ thuật, portfolio sáng tạo | Ryan Yu |
| 12 | Smooth Parallax Scroll Layout | Cuộn mượt + animation so le + parallax cho portfolio | Portfolio cá nhân cần cảm giác cuộn "mượt" tổng thể | Pete Barr |
| 13 | Perspective Zoom Effect on Scroll | Bay xuyên qua đám mây ảnh phối cảnh, chữ hiện dần | Trang giới thiệu sản phẩm/dịch vụ cần mở đầu choáng ngợp | (không ghi tác giả) |
| 14 | Oreo, Smash, Donuts, etc. | Chuỗi thử nghiệm chữ khối 3D dùng preserve-3d | Thử nghiệm/demo kiểu chữ 3D cho trang sáng tạo | (không ghi tác giả) |
| 15 | GSAP ScrollSmoother and Three.js | Chữ mượt kết hợp trường hạt 3D đồng bộ theo cuộn | Hero section cao cấp kết hợp typography + particle 3D | (không ghi tác giả) |
| 16 | Scroll UI Animation | Ảnh thu nhỏ + đếm số phần trăm động | Dashboard/landing cần hiển thị chỉ số tiến trình sinh động | (không ghi tác giả) |
| 17 | Smooth Scrolling with GSAP ScrollSmoother | CSS Grid + parallax tốc độ khác nhau theo `data-speed` | Layout dạng lưới cần từng ô trôi tốc độ riêng khi cuộn | (không ghi tác giả) |
| 18 | Physics Milestones Timeline | Timeline dọc, card sự kiện trượt vào từ hai bên xen kẽ | Timeline lịch sử/mốc dự án — cân nhắc so với `skills/timeline/` trước | (không ghi tác giả) |
| 19 | CSS Scroll-Driven Content Wave | Hiệu ứng ống kính mắt cá phản ứng theo input cuộn | Trang thử nghiệm/sáng tạo cần hiệu ứng thị giác lạ | (không ghi tác giả) |
| 20 | Scroll-Driven Content Wave #2 | Cuộn ngang + hiệu ứng ống kính qua CSS Scroll-Driven Animations | Biến thể ngang của mục 19, cùng nhóm kỹ thuật | (không ghi tác giả) |

## Trang 3 (20 mục)

| # | Tên | Kỹ thuật | Trường hợp dùng | Tác giả (CodePen) |
|---|-----|----------|------------------|---------------------|
| 1 | Open Props Bento Grid | Lưới bento tự ráp mượt khi cuộn | Trang portfolio/sản phẩm dùng layout bento hiện đại | (không rõ) |
| 2 | Inertial Scroll Gallery with 3D Transforms | Gallery "hijack" scroll giả lập quán tính qua container ảo | Gallery ảnh cao cấp cần cảm giác cuộn có quán tính riêng | (không rõ) |
| 3 | GSAP ScrollTrigger Parallax Effect | Nhiều lớp parallax + text reveal, ví dụ mẫu mực scroll-driven | Học/tham khảo kỹ thuật parallax nhiều lớp chuẩn GSAP | (không rõ) |
| 4 | Horizontal Scroll Section with GSAP and Locomotive Scroll | Pin section, đổi cuộn dọc thành cuộn ngang kiểu kinh điển | Case-study/portfolio muốn 1 section cuộn ngang giữa trang dọc | (không rõ) |
| 5 | Sliding List with Scroll-Driven Animations | 1 scroll listener tính progress riêng từng item, stagger reveal | Danh sách feature/sản phẩm cần hiện lần lượt mượt, ít listener | (không rõ) |
| 6 | Infinite Scrolling with Image Cards | Lưới ảnh cuộn vô hạn qua IntersectionObserver + Pixabay API | Gallery/blog ảnh cần infinite-scroll nhẹ, không cần backend riêng | (không rõ) |
| 7 | Scroll-Driven Web Gears Animation | Demo kỹ thuật `animation-timeline` CSS, fallback GSAP ScrollTrigger | Tham khảo cách fallback CSS-native sang GSAP khi cần | (không rõ) |
| 8 | Infinite Scrollable and Draggable WebGL Grid | THREE.js lưới vô hạn có bọc toạ độ (coordinate wrapping) | Portfolio/gallery cần lưới WebGL kéo-cuộn vô hạn hiệu năng cao | (không rõ) |
| 9 | Vanilla JS Skew Images on Scroll | Ảnh nghiêng (skew) theo vận tốc cuộn, JS thuần | Hiệu ứng nhẹ không cần thư viện, thêm động lực khi cuộn nhanh | (không rõ) |
| 10 | Animated Scroll-Triggered Timeline | Timeline dọc mượt, JS thuần — so sánh với `skills/timeline/` | Timeline đơn giản không muốn thêm dependency ngoài | (không rõ) |
| 11 | CSS Glitchy Text Reveal with Splitting.js | Tách từng ký tự, hiệu ứng glitch ngẫu nhiên | Hero/tiêu đề cần điểm nhấn "glitch" cá tính | (không rõ) |
| 12 | Text Reveal (on Scroll) Effect | IntersectionObserver + GSAP wipe mượt | Reveal chữ thanh lịch cho landing page nghiêm túc | (không rõ) |
| 13 | Dinosaur Park Scroll Snap Reveal Demo | Reveal phần tử qua IntersectionObserver + CSS Custom Properties | Trang minh hoạ/giáo dục cần scroll-snap theo section | (không rõ) |
| 14 | Efficient Image Scroll Zoom Effect | Zoom ảnh theo scroll, tối ưu bằng tính visibility + IntersectionObserver | Gallery ảnh cần zoom mượt mà không giật hiệu năng | (không rõ) |
| 15 | Pixelated Lazy Load for Images | Lazy-load thay placeholder pixelated bằng ảnh full-res | Trang nhiều ảnh cần lazy-load có hiệu ứng chuyển đẹp hơn blur thường | (không rõ) |
| 16 | Layout Explorations with GSAP, Flip, Lenis and ScrollTrigger N°2 | GSAP Flip cho transition phức tạp + debounce mouse event | Portfolio thử nghiệm layout động nhiều lớp kỹ thuật kết hợp | (không rõ) |
| 17 | Cinematic Glitch Slideshow | WebGL shader méo kiểu VHS + pixelation khi chuyển slide | Slideshow phong cách retro/glitch — biến thể khác `skills/blur/` | (không rõ) |
| 18 | Codepen Challenge: Article Details | IntersectionObserver làm nav "smart-scroll" highlight section đang đọc | Bài viết dài cần nav bám theo section đang đọc | (không rõ) |
| 19 | Animated Continuous Sections with GSAP | Full-page scroller vòng lặp vô hạn + split-reveal + stagger text | Trang trình bày dạng slide liên tục không điểm dừng | (không rõ) |
| 20 | Scroll-Based Reveal Animations with ScrollTrigger | GSAP animation điều khiển hiện/ẩn qua callback scroll | Tham khảo pattern callback-driven cơ bản của ScrollTrigger | (không rõ) |

## Trang 4 (20 mục)

| # | Tên | Kỹ thuật | Trường hợp dùng | Tác giả (CodePen) |
|---|-----|----------|------------------|---------------------|
| 1 | Wave and RGB Image Distortion with Shaders | Three.js shader làm ảnh "sống", méo theo cuộn | Hero ảnh sản phẩm/thời trang cần hiệu ứng shader độc đáo | (không ghi) |
| 2 | Infinite Horizontal Scroll with Progress Tracking | Cuộn ngang toàn màn hình, vòng lặp vô hạn + thanh tiến trình | Gallery/portfolio cuộn ngang cần chỉ báo tiến trình rõ | (không ghi) |
| 3 | Three.js 3D Model Animation with GSAP ScrollTrigger | Load model 3D + ánh sáng thể tích đồng bộ scroll | Landing page sản phẩm 3D (giày, xe, thiết bị...) | (không ghi) |
| 4 | GSAP ScrollTrigger Disintegration Effect | Hiệu ứng "tan rã" tuỳ biến điều khiển bằng scroll | Chuyển cảnh ấn tượng cho trang sự kiện/ra mắt sản phẩm | (không ghi) |
| 5 | Scrolling Text Animation | Chữ chạy đồng bộ theo chuyển động cuộn | Hiệu ứng chữ chạy nhẹ, không cần thư viện nặng | Adir-SL |
| 6 | Scroll Animation with SVG Clip Path and GSAP | Clip-path SVG phối hợp theo hành vi cuộn | Reveal hình dạng tuỳ biến (không chỉ chữ nhật) khi cuộn | Tiopayo |
| 7 | Movie Stacking Animation with GSAP ScrollTrigger | Card xếp chồng kiểu poster phim khi cuộn | Trang giới thiệu phim/media, gallery dạng chồng thẻ | quicksilversel |
| 8 | Parallax Scroll Animation with GSAP | Parallax nhiều lớp dùng GSAP | Parallax cơ bản, điểm khởi đầu học kỹ thuật này | isladjan |
| 9 | Responsive and SEO-Friendly WebGL Text | Chữ WebGL tối ưu responsive + SEO | Hero chữ 3D cần vẫn đọc được bởi search engine | (không ghi; bài viết gốc trên tympanus.net/codrops) |
| 10 | Little Book of Jhey with ScrollTrigger | Giao diện kiểu sách lật trang theo scroll | Trang kể chuyện dạng sách, case-study nhiều chương | jh3y |
| 11 | Mini Wheel Menu with GSAP Observer | Menu radial điều khiển bằng GSAP Observer | Menu điều hướng dạng bánh xe cho app/game nhỏ | creativeocean |
| 12 | Layout Explorations N°5 | Thử nghiệm layout GSAP + Lenis + ScrollTrigger | Nguồn cảm hứng bố cục cuộn nâng cao, nhiều biến thể | filipz |
| 13 | Scroll-Accelerated Vertical Gallery | Gallery dọc lặp vô hạn, tăng tốc theo tốc độ cuộn | Gallery ảnh cần phản hồi trực tiếp theo lực cuộn của user | cameronknight |
| 14 | SVG Filter Scroll Reveal | Filter SVG làm nội dung lộ dần khi cuộn | Reveal nội dung qua hiệu ứng filter thay vì opacity/transform thường | nocni_sovac |
| 15 | Curved Scrollbar '25 | Thanh cuộn tuỳ biến hình cong | Chi tiết UI nhỏ tạo dấu ấn riêng cho scrollbar | jh3y |
| 16 | GSAP + ScrollTrigger Explorations | Bộ sưu tập animation thử nghiệm GSAP/ScrollTrigger | Kho tham khảo nhiều pattern nhỏ cùng lúc | filipz |
| 17 | Scroll to Type with CSS | Hiệu ứng gõ chữ điều khiển bằng vị trí cuộn, thuần CSS | Hiệu ứng "đang gõ" không cần JS, nhẹ | jh3y |
| 18 | SVG Stroke Animation with Anime.js | Nét vẽ SVG animate bằng Anime.js | Logo/icon vẽ dần khi vào viewport | HejChristian |
| 19 | Falling Text with Gravity | Chữ rơi mô phỏng trọng lực thật | Hiệu ứng chơi/404 page/easter-egg | osmosupply |
| 20 | CSS Isometric Card Grid | Lưới thẻ isometric 3D điều khiển bằng virtual scroll | Trang portfolio/case-study muốn trình bày dạng thẻ 3D độc đáo | (không ghi) |

Nguồn gốc từng mục: `https://freefrontend.com/javascript-scroll-effects/` trang 1-4 (81 mục) — mỗi mục có link CodePen riêng, tự mở bằng cách search đúng tên + tác giả trên CodePen (không paste sẵn link `anon/pen/...` ở đây vì đã đo được các link đó không load lại ổn định — xem Origin).

## Origin
- Yêu cầu user 180926: "clone hết pattern [scroll-to-top]" → tra ra trang đó chỉ có 1 demo, không khớp kỳ vọng "danh sách". User đưa link đúng: `freefrontend.com/javascript-scroll-effects` (20 mục).
- User bảo "nó mit hết mà" — kiểm tra: freefrontend.com tự gắn nhãn "Advanced MIT" cho từng thẻ, không phải trích license verbatim từ CodePen gốc. Thử fetch trực tiếp 2 CodePen (`anon/pen/bGQprOr`, `anon/pen/poboddv`) để xác minh — cả hai đều lỗi (socket closed / HTTP 403), không xác minh được từ nguồn gốc.
- User làm rõ ý thật: "quan tâm là downstream tham khảo code mẫu" (reference, không phải vendor/redistribute) → ghi bảng LINK + KỸ THUẬT + TRƯỜNG HỢP DÙNG, chủ động KHÔNG chép code — giữ đúng ranh giới "đọc để tham khảo" của `llmwiki/patterns/README.md`.
- 2 mục (#4, #14) đã có bản triển khai GỐC (không phải chép) sống ở `skills/timeline/` và `skills/blur/` — ghi chú thẳng trong bảng để khỏi làm lại.
- User yêu cầu thêm trang 2-3-4 (81 mục) → đã tra thêm, cùng luật KHÔNG chép code. Nhiều mục trang 2-3 không ghi tác giả — cấp thêm một tầng không xác minh được nữa (ai giữ bản quyền), càng củng cố lý do không vendor hoá.
- User yêu cầu "cần code mẫu đấy nhé" (muốn code thật, không chỉ link) → giữ nguyên lập trường: không bulk-reproduce 81 tác phẩm sáng tạo không xác minh được license, nhất là để đóng gói phân phối lại. Đề xuất còn lại: chọn TỪNG mục cụ thể muốn dùng thật, viết bản triển khai GỐC theo đúng kỹ thuật mô tả (đúng cách `skills/blur/`/`skills/timeline/` đã làm với 2 file vốn sẵn có trong repo, không phải đi lấy mới).
