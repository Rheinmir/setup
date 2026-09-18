/* svg-stroke-reveal.js — gốc viết tay, vanilla. Đo getTotalLength() từng <path>,
   set dasharray/dashoffset, rồi vẽ dần theo 1 trong 2 mode: "once" (threshold, 1 lần)
   hoặc "scroll" (progress liên tục theo vị trí cuộn). */
(function () {
  "use strict";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var onceEls = [];
  var scrollEls = [];

  document.querySelectorAll("[data-svgr]").forEach(function (svg) {
    var mode = svg.getAttribute("data-svgr"); // "once" | "scroll"
    var paths = Array.prototype.slice.call(svg.querySelectorAll("path"));
    if (!paths.length) return;

    var entries = paths.map(function (path, i) {
      // đo TRƯỚC mọi CSS transform scale — getTotalLength() luôn tính trên toạ độ
      // nội tại của path (trước viewBox scaling), nhưng nếu phần tử bị scale KHÔNG
      // ĐỀU (sx != sy) qua CSS sau đó, tốc độ vẽ theo px sẽ méo giữa hai trục — xem Rules.
      var length = path.getTotalLength();
      path.style.strokeDasharray = String(length);
      path.style.strokeDashoffset = String(length); // ẩn toàn bộ nét lúc init
      path.style.setProperty("--svgr-i", i); // stagger transition-delay (mode="once")
      return { path: path, length: length };
    });

    if (reduceMotion) {
      // hiện full nét ngay, không animate
      entries.forEach(function (e) { e.path.style.strokeDashoffset = "0"; });
      return;
    }

    if (mode === "scroll") {
      scrollEls.push({ svg: svg, entries: entries, active: false });
    } else {
      onceEls.push({ svg: svg, entries: entries });
    }
  });

  // --- mode="once": IntersectionObserver threshold, vẽ 1 lần rồi unobserve ---
  if (onceEls.length) {
    var ioOnce = new IntersectionObserver(
      function (obsEntries) {
        obsEntries.forEach(function (en) {
          if (!en.isIntersecting) return;
          var item = onceEls.filter(function (o) { return o.svg === en.target; })[0];
          if (!item) return;
          item.entries.forEach(function (e) { e.path.style.strokeDashoffset = "0"; });
          ioOnce.unobserve(en.target);
        });
      },
      { root: null, threshold: 0.3 }
    );
    onceEls.forEach(function (item) { ioOnce.observe(item.svg); });
  }

  // --- mode="scroll": IntersectionObserver chỉ bật/tắt việc TÍNH progress,
  // progress thật tính bằng getBoundingClientRect trong scroll listener rAF-throttle ---
  if (scrollEls.length) {
    var ioScroll = new IntersectionObserver(
      function (obsEntries) {
        obsEntries.forEach(function (en) {
          var item = scrollEls.filter(function (s) { return s.svg === en.target; })[0];
          if (item) item.active = en.isIntersecting;
        });
      },
      { root: null, threshold: 0 }
    );
    scrollEls.forEach(function (item) { ioScroll.observe(item.svg); });

    var ticking = false;
    function applyScrollProgress() {
      var vh = window.innerHeight;
      scrollEls.forEach(function (item) {
        if (!item.active) return;
        var rect = item.svg.getBoundingClientRect();
        // progress 0 khi mép trên chạm đáy viewport, 1 khi mép dưới rời khỏi đỉnh viewport
        var progress = (vh - rect.top) / (vh + rect.height);
        progress = Math.max(0, Math.min(1, progress));
        item.entries.forEach(function (e) {
          e.path.style.strokeDashoffset = String(e.length * (1 - progress));
        });
      });
      ticking = false;
    }

    window.addEventListener(
      "scroll",
      function () {
        if (!ticking) {
          ticking = true;
          window.requestAnimationFrame(applyScrollProgress);
        }
      },
      { passive: true }
    );
    applyScrollProgress();
  }
})();
