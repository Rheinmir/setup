/* scroll-effects.js — gốc viết tay, vanilla. Một observer + một scroll listener rAF-throttle. */
(function () {
  "use strict";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // --- 1 observer chung: reveal + stagger + highlight + scrollspy ---
  var spyLinks = {};
  document.querySelectorAll("[data-se-toc] a[href^='#']").forEach(function (a) {
    spyLinks[a.getAttribute("href").slice(1)] = a;
  });

  var io = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (en) {
        var t = en.target;
        if (t.hasAttribute("data-se-reveal") || t.hasAttribute("data-se-stagger") || t.hasAttribute("data-se-highlight")) {
          if (en.isIntersecting) {
            t.classList.add("is-in");
            io.unobserve(t); // hiện một lần rồi thôi, khỏi tốn observer
          }
        } else if (t.tagName === "SECTION" && t.id && spyLinks[t.id]) {
          if (en.isIntersecting) {
            Object.keys(spyLinks).forEach(function (k) { spyLinks[k].classList.remove("is-active"); });
            spyLinks[t.id].classList.add("is-active");
          }
        }
      });
    },
    { root: null, rootMargin: "-40% 0px -55% 0px", threshold: 0 }
  );

  document.querySelectorAll("[data-se-reveal],[data-se-stagger],[data-se-highlight]").forEach(function (el, idx) {
    // 2. stagger: gán thứ tự cho từng dòng con
    if (el.hasAttribute("data-se-stagger")) {
      Array.prototype.forEach.call(el.children, function (child, i) {
        child.style.setProperty("--i", i);
      });
    }
    if (reduceMotion) {
      el.classList.add("is-in"); // hiện ngay, không chờ cuộn
    } else {
      io.observe(el);
    }
    void idx;
  });

  document.querySelectorAll("section[id]").forEach(function (s) {
    if (spyLinks[s.id]) io.observe(s);
  });

  // --- 1 scroll listener chung (rAF-throttle): nav + top + parallax ---
  var nav = document.querySelector("[data-se-nav]");
  var topBtn = document.querySelector("[data-se-top]");
  var parlxEls = collectParallax();
  var ticking = false;

  function collectParallax() {
    if (reduceMotion) return [];
    return Array.prototype.slice.call(document.querySelectorAll("[data-se-parallax]")).map(function (el) {
      var v = parseFloat(el.getAttribute("data-se-parallax")) || 0;
      v = Math.max(-0.3, Math.min(0.3, v)); // kẹp |v| ≤ 0.3 chống say chuyển động
      return { el: el, speed: v };
    });
  }

  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (nav) nav.classList.toggle("is-shrunk", y > 24);
    if (topBtn) topBtn.classList.toggle("is-in", y > window.innerHeight);
    if (parlxEls.length) {
      var mid = y + window.innerHeight / 2;
      parlxEls.forEach(function (p) {
        var r = p.el.getBoundingClientRect();
        var center = r.top + y + r.height / 2;
        p.el.style.transform = "translateY(" + ((center - mid) * p.speed).toFixed(1) + "px)";
      });
    }
    ticking = false;
  }

  window.addEventListener("scroll", function () {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(onScroll);
    }
  }, { passive: true });
  onScroll();

  // --- 5. scroll-to-top click ---
  if (topBtn) {
    topBtn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
    });
  }
})();
