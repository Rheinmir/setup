/**
 * gsap-scrolltrigger-pin — bản gốc, viết theo cơ chế chuẩn ngành:
 * pin section + tween xPercent của track theo tiến trình cuộn dọc (scrub).
 * Không copy code từ CodePen/demo tham khảo nào — chỉ áp dụng cơ chế chung
 * của GSAP ScrollTrigger (pin: true + scrub + tween xPercent).
 *
 * Yêu cầu: GSAP + ScrollTrigger đã load trước script này (xem demo.html).
 */
(function () {
  if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") {
    console.warn("[gsap-scrolltrigger-pin] GSAP/ScrollTrigger chưa load — bỏ qua init.");
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  function initHorizontalPin(section, track) {
    const slides = track.querySelectorAll("[data-hp-slide]");
    const slideCount = slides.length; // đọc từ DOM — không hardcode số slide

    if (slideCount < 2) return null;

    const tween = gsap.to(track, {
      xPercent: -100 * (slideCount - 1),
      ease: "none",
      scrollTrigger: {
        trigger: section,
        start: "top top",
        // end tính động theo track.scrollWidth mỗi lần refresh, không hardcode
        // theo số slide hay theo px cố định
        end: () => "+=" + (track.scrollWidth - window.innerWidth),
        pin: true,
        scrub: 1,
        invalidateOnRefresh: true,
      },
    });

    return tween;
  }

  // matchMedia: tự re-init khi resize đổi breakpoint, và tự chọn nhánh
  // reduced-motion — GSAP revert sạch nhánh cũ trước khi chạy nhánh mới.
  ScrollTrigger.matchMedia({
    "(prefers-reduced-motion: no-preference)": function () {
      document.querySelectorAll("[data-hp-section]").forEach((section) => {
        const track = section.querySelector("[data-hp-track]");
        if (!track) return;
        initHorizontalPin(section, track);
      });

      // ảnh/font load xong có thể đổi track.scrollWidth -> refresh lại 1 lần
      window.addEventListener("load", () => ScrollTrigger.refresh());

      // cleanup khi rời media query (bắt buộc theo API matchMedia của GSAP)
      return () => ScrollTrigger.getAll().forEach((st) => st.kill());
    },
    "(prefers-reduced-motion: reduce)": function () {
      // Không tạo ScrollTrigger nào — CSS (.hp-pin { overflow-x: auto }) đã
      // tự chuyển section thành khung cuộn ngang thường, không pin/scrub.
    },
  });
})();
