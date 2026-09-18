/* mask-reveal-transition.js — gốc viết tay, vanilla. Cơ chế nền dùng chung cho cả 2 biến thể:
   đo tiến trình trong section bằng getBoundingClientRect(), map về 0..1, rồi ghi --mrt-r
   (bán kính vòng loang) lên ảnh "trên" — vùng trong --mrt-r trong suốt nên lộ ảnh "dưới". */
(function () {
  "use strict";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function maxRadiusFor(el) {
    var r = el.getBoundingClientRect();
    return Math.hypot(r.width, r.height) / 2 + 40; // đủ để vòng loang phủ hết góc xa nhất
  }

  // ============================================================
  // Biến thể 1 — blob/ink reveal: --mrt-r đồng bộ LIÊN TỤC theo scroll progress
  // ============================================================
  var blobItems = Array.prototype.slice
    .call(document.querySelectorAll("[data-mrt-blob]"))
    .map(function (stage) { return { stage: stage, over: stage.querySelector(".mrt-blob-over") }; })
    .filter(function (item) { return item.over; });

  if (blobItems.length) {
    if (reduceMotion) {
      blobItems.forEach(function (item) {
        item.over.style.setProperty("--mrt-r", maxRadiusFor(item.over) + "px"); // lộ hết ngay
      });
    } else {
      var tickingBlob = false;
      var applyBlobProgress = function () {
        var vh = window.innerHeight;
        blobItems.forEach(function (item) {
          var rect = item.stage.getBoundingClientRect();
          // progress 0 khi mép trên section chạm đáy viewport, 1 khi mép dưới rời khỏi đỉnh viewport
          var progress = (vh - rect.top) / (vh + rect.height);
          progress = Math.max(0, Math.min(1, progress));
          var r = progress * maxRadiusFor(item.over);
          item.over.style.setProperty("--mrt-r", r.toFixed(1) + "px");
        });
        tickingBlob = false;
      };
      window.addEventListener(
        "scroll",
        function () {
          if (!tickingBlob) {
            tickingBlob = true;
            window.requestAnimationFrame(applyBlobProgress);
          }
        },
        { passive: true }
      );
      applyBlobProgress();
    }
  }

  // ============================================================
  // Biến thể 2 — pinned split-screen: --mrt-r đổi RỜI RẠC khi panel active đổi
  // (CSS transition lo phần mượt, JS chỉ quyết định lộ ảnh nào — không tự animate)
  // ============================================================
  Array.prototype.forEach.call(document.querySelectorAll("[data-mrt-split]"), function (section) {
    var under = section.querySelector(".mrt-split-under");
    var over = section.querySelector(".mrt-split-over");
    var panels = Array.prototype.slice.call(section.querySelectorAll("[data-mrt-panel]"));
    if (!under || !over || !panels.length) return;

    var currentSrc = panels[0].getAttribute("data-mrt-src");
    under.src = currentSrc;
    over.src = currentSrc;

    function revealTo(nextSrc) {
      if (!nextSrc || nextSrc === currentSrc) return;
      over.src = currentSrc; // ảnh đang hiện lên "trên", che kín (--mrt-r về 0)
      under.src = nextSrc; // ảnh sắp lộ nằm "dưới", chờ vòng loang mở ra
      currentSrc = nextSrc;

      if (reduceMotion) {
        over.style.setProperty("--mrt-r", maxRadiusFor(over) + "px"); // lộ ngay, không animate
        return;
      }
      over.style.transition = "none";
      over.style.setProperty("--mrt-r", "0px"); // che kín tức thì
      void over.offsetWidth; // ép reflow để trình duyệt chốt r=0 trước khi cho animate
      over.style.transition = "";
      window.requestAnimationFrame(function () {
        over.style.setProperty("--mrt-r", maxRadiusFor(over) + "px"); // loang ra, lộ ảnh mới
      });
    }

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (en) {
          en.target.classList.toggle("is-active", en.isIntersecting);
          if (en.isIntersecting) revealTo(en.target.getAttribute("data-mrt-src"));
        });
      },
      { root: null, threshold: 0.5 }
    );
    panels.forEach(function (p) { io.observe(p); });
  });
})();
