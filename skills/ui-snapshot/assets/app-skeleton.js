/* ui-snapshot app skeleton — copy to <src>/app.js, then port each screen.
   Rules: class strings copied VERBATIM from the JSX (Tailwind JIT only sees literal strings);
   every icon name written as a quoted literal ("search") so build.py can subset the icon font;
   data is hard-coded placeholder — never real user data. */
(() => {
"use strict";
// ── placeholder data (relative dates keep "overdue" states stable over time) ──
const D = (n) => { const d = new Date(); d.setHours(9, 0, 0, 0); d.setDate(d.getDate() + n); return d.toISOString(); };
const ITEMS = [ /* { Code: "X-001", title: "…", status: "Waiting", deadline: D(-3), amount: 1200000 }, … */ ];

// ── helpers ──
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const ic = (n, cls = "", st = "") => `<span class="material-symbols-outlined ${cls}"${st ? ` style="${st}"` : ""}>${n}</span>`;

// ── state + hash router (#/login, #/list, #/detail/<id> …) ──
const S = { mode: "auto", demoOpen: false /* + UI state: filters, open sheets, tabs, toasts … */ };
const route = () => { const h = decodeURIComponent(location.hash.replace(/^#\/?/, "")) || "home"; const [p, q] = h.split("?"); return { parts: p.split("/"), q: new URLSearchParams(q || "") }; };
const go = (h) => { location.hash = "#/" + h; };
const isMobile = () => S.mode === "mobile" || (S.mode === "auto" && innerWidth < 768);   // same breakpoint as the app

// ── screens: one function per page, desktop + mobile branch like the real component ──
function home() { return isMobile() ? `<div class="…">mobile</div>` : `<div class="…">desktop</div>`; }
function screen() { const { parts } = route(); return ({ home })[parts[0]]?.() ?? home(); }

// ── demo panel: jump to any screen/state (not part of the real app) ──
const SCREENS = [["Nhóm", [["home", "Trang chủ"]]]];
function demoPanel() {
  return `${S.demoOpen ? `<div class="fixed right-14 top-[6vh] z-[9999] max-h-[88vh] w-[300px] overflow-y-auto rounded-xl border bg-white p-3 text-[12px] shadow-2xl">
    <div class="mb-3 flex rounded-full bg-slate-100 p-0.5">${["auto", "desktop", "mobile"].map((m) => `<button data-act="mode" data-v="${m}" class="flex-1 rounded-full py-1 text-[10px] font-bold uppercase ${S.mode === m ? "bg-white shadow-sm" : ""}">${m}</button>`).join("")}</div>
    ${SCREENS.map(([g, l]) => `<p class="mt-2 text-[9px] font-bold uppercase tracking-widest text-slate-500">${g}</p>${l.map(([h, t]) => `<button data-go="${h}" class="block w-full rounded px-2 py-1 text-left hover:bg-slate-100">${t}</button>`).join("")}`).join("")}
  </div>` : ""}<button data-act="demo" class="fixed right-2 top-[42%] z-[9999] rounded-full bg-slate-900/90 px-3 py-2 text-[11px] font-bold uppercase text-white shadow-xl">${ic("dashboard", "text-[16px]")} UI</button>`;
}

// ── render + event delegation (data-act / data-go / data-bind) ──
function render() {
  const a = document.activeElement, bind = a?.dataset?.bind, pos = bind ? a.selectionStart : null;
  document.body.classList.toggle("phone-mode", isMobile() && innerWidth >= 768);   // phone frame on wide screens
  document.getElementById("app").innerHTML = screen();
  document.getElementById("chrome").innerHTML = demoPanel();
  if (bind) { const el = document.querySelector(`[data-bind="${bind}"]`); el?.focus(); try { el.setSelectionRange(pos, pos); } catch (e) {} }
}
const H = { demo: () => { S.demoOpen = !S.demoOpen; }, mode: (d) => { S.mode = d.v; } };
document.addEventListener("click", (e) => {
  const t = e.target.closest("[data-act],[data-go]"); if (!t) return;
  if (t.dataset.go) { e.preventDefault(); go(t.dataset.go); return; }
  const f = H[t.dataset.act]; if (f) { e.preventDefault(); if (!f(t.dataset)) render(); }
});
document.addEventListener("input", (e) => { const b = e.target.dataset?.bind; if (b) { S[b] = e.target.value; render(); } });
addEventListener("hashchange", render); addEventListener("resize", () => { clearTimeout(render.t); render.t = setTimeout(render, 120); });
render();
})();
