/* lenis-demo.js — gốc viết tay cho skill lenis-smooth-scroll.
   Cơ chế: Lenis raf loop do gsap.ticker lái (không chạy 2 vòng raf song song) +
   lenis.on('scroll', ScrollTrigger.update) để ScrollTrigger biết Lenis vừa cuộn +
   gsap.ticker.lagSmoothing(0) để tránh giật khi tab quay lại từ nền.
   Tôn trọng prefers-reduced-motion: reduce -> không khởi tạo Lenis, dùng cuộn gốc trình duyệt. */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var badge = document.querySelector("[data-ls-badge]");

  if (reduceMotion || typeof Lenis === "undefined" || typeof gsap === "undefined") {
    // Không mượt-giả cho người cần giảm chuyển động: để trình duyệt cuộn gốc.
    // Reveal vẫn phải xảy ra, chỉ là không cần Lenis/ScrollTrigger để làm điều đó.
    document.querySelectorAll("[data-ls-reveal]").forEach(function (el) {
      el.classList.add("is-in");
    });
    if (badge) badge.textContent = reduceMotion ? "reduced-motion: native scroll" : "Lenis/GSAP chưa nạp";
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  var lenis = new Lenis({
    lerp: 0.1, // nội suy vị trí mỗi frame (0–1); thấp = mượt/trễ hơn, cao = bám sát chuột hơn
    duration: 1.2, // thời lượng easing khi có target (anchor scroll), không áp dụng cho wheel liên tục
    smoothWheel: true, // bật vật lý mượt cho scroll-wheel/trackpad (đây là lý do dùng Lenis)
    wheelMultiplier: 1,
  });

  // --- Đồng bộ Lenis với GSAP ScrollTrigger ---
  // 1) mỗi lần Lenis cuộn (kể cả giữa 2 frame do easing), báo ScrollTrigger cập nhật vị trí pin/scrub.
  lenis.on("scroll", ScrollTrigger.update);

  // 2) để gsap.ticker LÀM VÒNG LẶP RAF DUY NHẤT cho Lenis, thay vì tự requestAnimationFrame riêng.
  //    gsap.ticker đã có 1 vòng rAF nội bộ đồng bộ khung hình cho toàn bộ animation GSAP;
  //    nếu Lenis tự chạy thêm 1 requestAnimationFrame(loop) độc lập, hai vòng lặp không cùng
  //    một "nhịp" -> lệch pha 1 frame giữa vị trí cuộn (Lenis) và animation (GSAP), gây giật nhỏ
  //    liên tục khi cuộn nhanh. Gộp về một driver duy nhất (gsap.ticker) loại bỏ lệch pha đó.
  //    gsap.ticker phát time tính bằng GIÂY, còn lenis.raf() cần mili-giây -> nhân 1000.
  gsap.ticker.add(function (time) {
    lenis.raf(time * 1000);
  });

  // 3) tắt lag-smoothing mặc định của GSAP. Mặc định, khi tab mất focus rồi quay lại,
  //    gsap.ticker phát hiện khung hình bị "trễ" (delta lớn bất thường) và tự nén thời gian lại
  //    để bù — nhưng Lenis đã tự quản lý delta/velocity của riêng nó, nên cú nén này làm Lenis
  //    giật một cú khi tab active lại (2 hệ làm mượt thời gian đá nhau). lagSmoothing(0) tắt hẳn
  //    cơ chế bù của GSAP, để một mình Lenis lo phần mượt thời gian.
  gsap.ticker.lagSmoothing(0);

  if (badge) badge.textContent = "Lenis + ScrollTrigger đang chạy";

  // --- Demo: reveal stagger theo data-ls-reveal, dùng ScrollTrigger (đã ăn theo scroll của Lenis) ---
  document.querySelectorAll("[data-ls-reveal]").forEach(function (el) {
    ScrollTrigger.create({
      trigger: el,
      start: "top 85%",
      onEnter: function () { el.classList.add("is-in"); },
      once: true,
    });
  });

  // --- Demo: data-speed tạo lệch nhẹ theo layer khi cuộn qua (dùng chung driver Lenis/GSAP ở trên,
  //     không tạo thêm listener scroll rời). |speed| kẹp để tránh say chuyển động. ---
  document.querySelectorAll("[data-speed]").forEach(function (el) {
    var raw = parseFloat(el.getAttribute("data-speed")) || 0;
    var speed = Math.max(-0.3, Math.min(0.3, raw));
    if (!speed) return;
    gsap.to(el, {
      y: function () { return window.innerHeight * speed; },
      ease: "none",
      scrollTrigger: { trigger: el, start: "top bottom", end: "bottom top", scrub: true },
    });
  });
})();
