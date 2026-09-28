#!/usr/bin/env node
/* discover.mjs — vòng khám phá component cho ui-kit-from-code.
 * Đi theo link cùng origin (BFS), cuộn hết trang, bấm mở phần ẩn (accordion, tab, details, menu),
 * gom các khối trông như component và gán cho mỗi khối một CHỮ KÝ = loại + style chính + hình dạng
 * con. Chữ ký trùng thì chỉ đếm thêm lần gặp; chữ ký mới thì chụp crop + lưu HTML rút gọn.
 * Dừng khi hết ngân sách trang hoặc SATURATE trang liên tiếp không thêm chữ ký mới.
 *
 *   NODE_PATH=$(npm root -g) node discover.mjs <url> [--out dir] [--pages 15] [--saturate 3]
 *        [--include <regex>] [--exclude <regex>] [--viewport 1440x900]
 *   node discover.mjs --coverage <out>/inventory.json <kit.html>
 *        cổng phủ: mỗi pattern phải có thẻ trong kit mang data-sig="<sig>" (một thẻ có thể ghi
 *        nhiều sig, cách nhau bởi dấu cách) hoặc nằm trong <meta name="ui-kit-skip" content="sig:lý do;…">.
 *        In pattern còn thiếu, rc 1 nếu còn thiếu.
 *
 * Trạng thái: với pattern bấm được (button, card-link, link, tabs, disclosure, input, card có cursor
 * pointer), đo style trước/sau HOVER, FOCUS-VISIBLE (bàn phím) và ACTIVE (nhấn giữ, kéo chuột ra
 * rồi mới nhả nên không click); khác thì lưu `states.<tên> = {diff, crop}`. Pattern mang dấu chọn
 * (aria-pressed/selected/current/checked, data-state=active|on|checked|open, class is-active|active|
 * selected) được ghép với biến thể thường cùng họ: `selectedOf = <sig biến thể thường>`.
 * Ra: <out>/inventory.json (mọi pattern: kind, sig, styles, pages, count, crop, html, states, sel)
 *     <out>/crops/<kind>-<n>.png · <out>/pages/<slug>.png · bảng tóm tắt trên stdout.
 * Chỉ đọc trang công khai; không gửi form, không đăng nhập, không bấm link ra ngoài. */
import { createRequire } from "node:module";
import { mkdirSync, writeFileSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";

if (process.argv[2] === "--coverage") {
  const inv = JSON.parse(readFileSync(process.argv[3], "utf8"));
  const html = readFileSync(process.argv[4], "utf8");
  const covered = new Set([...html.matchAll(/data-sig="([^"]+)"/g)].flatMap((m) => m[1].split(/\s+/)));
  const skip = new Map([...html.matchAll(/<meta name="ui-kit-skip" content="([^"]*)"/g)].flatMap((m) => m[1].split(";").filter(Boolean).map((x) => x.split(":"))));
  const miss = inv.patterns.filter((p) => !covered.has(p.sig) && !skip.has(p.sig));
  const pct = Math.round((100 * (inv.patterns.length - miss.length)) / inv.patterns.length);
  console.log(`phủ ${inv.patterns.length - miss.length}/${inv.patterns.length} pattern (${pct}%) · ${covered.size} sig trong kit · ${skip.size} bỏ có lý do`);
  for (const p of miss) console.log(`  THIẾU ${p.sig}  ${p.kind.padEnd(10)} ×${p.count}  ${p.crop ?? "(không crop)"}  "${p.firstText.slice(0, 50)}"`);
  /* trạng thái: mỗi state đo được phải có data-sig-state="<sig>:<state>" trong kit, hoặc ui-kit-skip
     "<sig>:<state>:lý do". Cặp selected tính là state "selected" của biến thể thường. */
  const shown = new Set([...html.matchAll(/data-sig-state="([^"]+)"/g)].flatMap((m) => m[1].split(/\s+/)));
  const need = inv.patterns.filter((p) => !skip.has(p.sig)).flatMap((p) => [
    ...Object.keys(p.states || {}).map((st) => ({ p, st })),
    ...(p.selectedOf ? [{ p: inv.patterns.find((q) => q.sig === p.selectedOf) || p, st: "selected", via: p.sig }] : []),
  ]);
  const skipState = (k) => [...html.matchAll(/<meta name="ui-kit-skip" content="([^"]*)"/g)].some((m) => m[1].split(";").some((x) => x.startsWith(k + ":")));
  const smiss = need.filter(({ p, st }) => !shown.has(`${p.sig}:${st}`) && !skipState(`${p.sig}:${st}`));
  console.log(`trạng thái ${need.length - smiss.length}/${need.length} (hover/focus/active/selected)`);
  for (const { p, st, via } of smiss) console.log(`  THIẾU ${p.sig}:${st.padEnd(8)} ${p.kind.padEnd(10)} ${(p.states?.[st]?.crop) ?? (via ? "selected=" + via : "")}  ${JSON.stringify(p.states?.[st]?.diff ?? {}).slice(0, 110)}`);
  process.exit(miss.length || smiss.length ? 1 : 0);
}

const require = createRequire(process.env.NODE_PATH ? process.env.NODE_PATH + "/" : import.meta.url);
const { chromium } = require("playwright");

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf("--" + k); return i >= 0 ? argv[i + 1] : d; };
const start = argv.find((a) => /^https?:\/\//.test(a));
if (!start) { console.error("usage: discover.mjs <url> [--out dir] [--pages 15] [--saturate 3] [--include re] [--exclude re]"); process.exit(2); }
const OUT = opt("out", "./ui-kit-discovery");
const MAX = Number(opt("pages", 15));
const SAT = Number(opt("saturate", 3));
const INC = opt("include") ? new RegExp(opt("include")) : null;
/* mặc định bỏ đường dẫn cần đăng nhập, tải file, và trang pháp lý */
const EXC = new RegExp(opt("exclude", "(logout|signout|/api/|/app/|\\.(pdf|zip|png|jpe?g|svg|mp4)$|/privacy|/terms|/legal)"));
const [VW, VH] = opt("viewport", "1440x900").split("x").map(Number);
mkdirSync(OUT + "/crops", { recursive: true });
mkdirSync(OUT + "/pages", { recursive: true });

const origin = new URL(start).origin;
const norm = (u) => { try { const x = new URL(u, origin); x.hash = ""; if ([...x.searchParams].length > 2) x.search = ""; return x.origin === origin ? x.href.replace(/\/$/, "") : null; } catch { return null; } };

/* chạy trong trang: trả về các khối ứng viên, mỗi khối có kind + style + shape + selector tạm */
function collect() {
  const px = (v) => Math.round(parseFloat(v) || 0);
  const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width >= 8 && r.height >= 8 && s.visibility !== "hidden" && s.display !== "none" && +s.opacity > 0.05; };
  const transparent = (c) => !c || c === "transparent" || /rgba?\([^)]*,\s*0\)$/.test(c) || /\/\s*0\)$/.test(c);
  const boxy = (s) => !transparent(s.backgroundColor) || px(s.borderTopWidth) > 0 || px(s.borderBottomWidth) > 0 || (s.boxShadow && s.boxShadow !== "none") || s.backgroundImage !== "none";
  const kindOf = (e, s, r) => {
    const t = e.tagName.toLowerCase(), role = e.getAttribute("role") || "", cls = String(e.className?.baseVal ?? e.className ?? "");
    if (/^h[1-6]$/.test(t)) return "heading";
    if (t === "input" || t === "textarea" || t === "select" || role === "combobox" || role === "textbox") return "input";
    /* phần tử mang trạng thái chọn luôn là tab/toggle, kể cả khi trong suốt (tab vẽ bằng SVG) */
    if (e.hasAttribute("aria-pressed") || e.hasAttribute("aria-selected") || (e.hasAttribute("aria-current") && e.getAttribute("aria-current") !== "false")) return "tabs";
    if (role === "tab" || role === "tablist") return "tabs";
    if (t === "summary" || t === "details" || e.hasAttribute("aria-expanded") && t !== "a") return "disclosure";
    if (t === "table") return "table";
    if (t === "blockquote") return "quote";
    if (t === "pre" || (t === "code" && r.height > 30)) return "code";
    if (t === "hr" || role === "separator") return "divider";
    if (t === "ol" || t === "ul") return e.closest("nav") ? null : "list";
    if (t === "img" || t === "picture" || t === "video" || t === "figure") return r.width < 48 && r.height < 48 ? "avatar" : "media";
    if (/breadcrumb/i.test((e.getAttribute("aria-label") || "") + cls) && (t === "nav" || t === "ol")) return "breadcrumb";
    if (t === "nav" || t === "header") return "nav";
    if (t === "footer") return "footer";
    if (t === "a" && boxy(s) && r.width >= 280 && r.height >= 36) return "card-link";
    if (t === "button" || role === "button" || (t === "a" && boxy(s) && r.height <= 64)) return "button";
    if (t === "a" && !boxy(s)) return r.height < 40 ? "link" : null;
    if (boxy(s) && r.width <= 64 && r.height <= 32 && (e.innerText || "").trim().length <= 12) return /full|9999/.test(s.borderRadius) || px(s.borderRadius) >= r.height / 2 ? "badge" : "tag";
    /* khung bố cục (phủ gần hết bề ngang và cao hơn một màn, hoặc nền phẳng không bo) không phải component */
    if (boxy(s) && ((r.width >= innerWidth * 0.9 && r.height > innerHeight) || r.height > innerHeight * 2.5)) return null;
    if (boxy(s) && r.width >= 120 && r.height >= 48) return /aside|callout|note|alert|tip/i.test(cls + role) ? "callout" : "card";
    if (t === "p" && r.height > 20) return "text";
    return null;
  };
  const shape = (e, depth = 2) => depth === 0 || !e.children.length ? e.tagName.toLowerCase()
    : e.tagName.toLowerCase() + "(" + [...new Set([...e.children].slice(0, 6).map((c) => shape(c, depth - 1)))].join(",") + ")";
  const out = [];
  let n = 0;
  for (const e of document.querySelectorAll("body *")) {
    if (!vis(e) || e.closest("[data-discover-skip]")) continue;
    const s = getComputedStyle(e), r = e.getBoundingClientRect();
    const kind = kindOf(e, s, r);
    if (!kind) continue;
    /* thẻ lồng trong khung (vd lưới thẻ trong section viền đứt) vẫn được lấy: chữ ký lo việc bỏ trùng.
       Chỉ bỏ khối con phủ gần kín khối cha cùng loại, vì đó là lớp bọc của cùng một thẻ. */
    if (kind === "card") { const pc = e.parentElement?.closest("[data-discover-card]"); if (pc) { const pr = pc.getBoundingClientRect(); if (r.width * r.height > 0.85 * pr.width * pr.height) continue; } e.setAttribute("data-discover-card", ""); }
    const st = { bg: s.backgroundColor, color: s.color, font: s.fontFamily.split(",")[0].replace(/"/g, ""), fs: px(s.fontSize), fw: s.fontWeight,
      radius: s.borderRadius, border: px(s.borderTopWidth) ? `${px(s.borderTopWidth)} ${s.borderTopStyle} ${s.borderTopColor}` : "",
      shadow: s.boxShadow === "none" ? "" : s.boxShadow.replace(/rgba\(0, 0, 0, 0\) 0px 0px 0px 0px,?\s*/g, "").slice(0, 80),
      pad: s.padding, tt: s.textTransform, ls: s.letterSpacing, display: s.display, w: Math.round(r.width), h: Math.round(r.height) };
    const id = "d" + n++;
    e.setAttribute("data-discover-id", id);
    const ds = e.getAttribute("data-state") || "";
    const sel = ["aria-pressed", "aria-selected", "aria-checked"].some((a) => e.getAttribute(a) === "true") || (e.hasAttribute("aria-current") && e.getAttribute("aria-current") !== "false")
      || /^(active|on|checked|open)$/.test(ds) || /(^|\s)(is-active|active|selected|is-selected)(\s|$)/.test(String(e.className?.baseVal ?? e.className ?? ""));
    const pointer = s.cursor === "pointer";
    out.push({ id, kind, st, sel, pointer, shape: shape(e), text: (e.innerText || e.getAttribute("alt") || "").trim().replace(/\s+/g, " ").slice(0, 80),
      cls: String(e.className?.baseVal ?? e.className ?? "").slice(0, 200),
      html: e.outerHTML.replace(/<svg[\s\S]*?<\/svg>/g, "<svg/>").replace(/\s(srcset|sizes|style|data-[\w-]+)="[^"]*"/g, "").replace(/(src|href)="[^"]{80,}"/g, '$1="…"').slice(0, 1600) });
  }
  return { items: out, links: [...document.querySelectorAll("a[href]")].map((a) => a.getAttribute("href")) };
}

/* chữ ký: loại + style ảnh hưởng nhìn thấy (làm tròn) + hình dạng con. Chữ và kích thước tuyệt đối
   không vào chữ ký, để 10 thẻ cùng kiểu nội dung khác nhau vẫn là một pattern. */
const bucket = (v, step) => Math.round(v / step) * step;
const sigOf = (it) => {
  const s = it.st;
  const key = it.kind === "heading" || it.kind === "text" || it.kind === "link"
    ? [it.kind, s.font, s.fs, s.fw, s.color, s.tt, s.ls]
    : [it.kind, s.bg, s.color, s.font, bucket(s.fs, 2), s.fw, s.radius, s.border, s.shadow ? "sh" : "", s.pad, s.tt,
       it.kind === "card" || it.kind === "callout" || it.kind === "card-link" ? it.shape : "", it.kind === "button" ? bucket(s.h, 4) : ""];
  return createHash("sha1").update(JSON.stringify(key)).digest("hex").slice(0, 10);
};

/* style dùng để so trạng thái: chỉ thuộc tính nhìn thấy được thay đổi khi tương tác */
/* scale/translate/rotate là thuộc tính riêng (Tailwind v4 dùng chúng thay cho transform: hover:scale-105) */
const STATE_PROPS = ["backgroundColor", "color", "borderTopColor", "borderTopWidth", "boxShadow", "outlineStyle", "outlineColor", "outlineWidth", "transform", "scale", "translate", "rotate", "opacity", "textDecorationLine", "filter", "backgroundImage"];
const INTERACTIVE = new Set(["button", "card-link", "link", "tabs", "disclosure", "input"]);
async function snap(loc) {
  return loc.evaluate((e, props) => { const s = getComputedStyle(e); const o = {}; for (const k of props) o[k] = s[k];
    /* hover thường đổi màu con (icon, chữ) chứ không đổi khối ngoài: gộp màu chữ của con trực tiếp */
    o.childColors = [...e.querySelectorAll("*")].slice(0, 6).map((c) => getComputedStyle(c).color).join("|"); return o; }, STATE_PROPS).catch(() => null);
}
const diffOf = (a, b) => { if (!a || !b) return null; const d = {}; for (const k of Object.keys(a)) if (a[k] !== b[k]) d[k] = [a[k], b[k]]; return Object.keys(d).length ? d : null; };
/* đo hover / focus-visible / active cho một phần tử; trả {state: {diff, crop}} */
async function measureStates(page, loc, base) {
  const out = {};
  const box = await loc.boundingBox().catch(() => null);
  if (!box || box.width < 4) return out;
  const before = await snap(loc);
  const shot = async (name) => { const f = `crops/${base}-${name}.png`; return (await loc.screenshot({ path: `${OUT}/${f}`, timeout: 3000 }).then(() => f).catch(() => null)); };
  try {
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2); await page.waitForTimeout(450);
    const d = diffOf(before, await snap(loc)); if (d) out.hover = { diff: d, crop: await shot("hover") };
    await page.mouse.down(); await page.waitForTimeout(150);
    const a = diffOf(before, await snap(loc)); if (a && JSON.stringify(a) !== JSON.stringify(d)) out.active = { diff: a, crop: await shot("active") };
    await page.mouse.move(1, 1); await page.mouse.up(); await page.waitForTimeout(300);
    /* focus-visible cần "chế độ bàn phím": nhấn Shift trước rồi focus bằng code */
    await page.keyboard.press("Shift"); await loc.focus({ timeout: 1000 }).catch(() => {}); await page.waitForTimeout(250);
    const f = diffOf(before, await snap(loc));
    /* focus chỉ bật outline:auto là viền mặc định của trình duyệt, không phải style của site */
    if (f) out.focus = { diff: f, crop: await shot("focus"), ua: Object.keys(f).every((k) => /^outline/.test(k)) && f.outlineStyle?.[1] === "auto" };
    await loc.evaluate((e) => e.blur()).catch(() => {});
  } catch {}
  return out;
}

/* bấm mở phần ẩn: accordion, details, tab chưa chọn, menu. Không bấm link, không gửi form. */
async function reveal(page) {
  return page.evaluate(async () => {
    const wait = (ms) => new Promise((r) => setTimeout(r, ms));
    let n = 0;
    for (const d of [...document.querySelectorAll("details:not([open])")].slice(0, 6)) { d.open = true; n++; }
    const clickable = [...document.querySelectorAll('[aria-expanded="false"]:not(a), [role="tab"][aria-selected="false"]')].filter((e) => !e.closest("form")).slice(0, 8);
    for (const e of clickable) { try { e.click(); n++; await wait(250); } catch {} }
    return n;
  });
}

const queue = [norm(start)], seen = new Set(queue);
const inv = new Map();
const log = [];
let dry = 0, visited = 0, stateCount = 0;
const save = () => writeFileSync(`${OUT}/inventory.json`, JSON.stringify({ start, visited, stoppedBy: dry >= SAT ? "saturated" : queue.length ? (visited >= MAX ? "page-budget" : "running") : "no-more-links", pages: log, patterns: [...inv.values()] }, null, 1));
const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: VW, height: VH } });
while (queue.length && visited < MAX && dry < SAT) {
  const url = queue.shift();
  const page = await ctx.newPage();
  const guard = setTimeout(() => { console.log(`   bỏ trang (quá 120s): ${url}`); page.close().catch(() => {}); }, 120000);
  try {
    await page.goto(url, { waitUntil: "networkidle", timeout: 45000 }).catch(() => {});
    await page.waitForTimeout(1200);
    /* cuộn cả window lẫn container cuộn bên trong để nạp phần lazy */
    await page.evaluate(async () => {
      const wait = (ms) => new Promise((r) => setTimeout(r, ms));
      const scrollers = [document.scrollingElement, ...[...document.querySelectorAll("*")].filter((e) => /(auto|scroll)/.test(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight + 100)];
      /* trần 40 bước mỗi container: trang cuộn vô hạn làm scrollHeight tăng mãi, không có trần là treo */
      for (const s of scrollers.slice(0, 4)) { for (let y = 0, k = 0; y < s.scrollHeight && k < 40; y += 600, k++) { s.scrollTop = y; await wait(120); } s.scrollTop = 0; }
    });
    const opened = await reveal(page);
    await page.waitForTimeout(400);
    const { items, links } = await page.evaluate(collect);
    const slug = new URL(url).pathname.replace(/\W+/g, "-").replace(/^-|-$/g, "") || "home";
    /* trang cuộn trong container riêng thì fullPage chỉ chụp một màn: tạm mở container ra rồi mới chụp */
    await page.evaluate(() => {
      const big = [...document.querySelectorAll("*")].filter((e) => /(auto|scroll)/.test(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight + 100)
        .sort((a, b) => b.scrollHeight - a.scrollHeight)[0];
      if (!big) return;
      for (let e = big; e && e !== document.documentElement; e = e.parentElement) { e.style.setProperty("height", "auto", "important"); e.style.setProperty("max-height", "none", "important"); e.style.setProperty("overflow", "visible", "important"); }
      document.documentElement.style.setProperty("height", "auto", "important"); document.body.style.setProperty("overflow", "visible", "important");
    });
    await page.screenshot({ path: `${OUT}/pages/${slug}.png`, fullPage: true }).catch(() => {});
    let fresh = 0;
    for (const it of items) {
      const sig = sigOf(it);
      const hit = inv.get(sig);
      if (hit) { hit.count++; if (!hit.pages.includes(url)) hit.pages.push(url); continue; }
      fresh++;
      const n = [...inv.values()].filter((x) => x.kind === it.kind).length + 1;
      const crop = `crops/${it.kind}-${n}.png`;
      const el = page.locator(`[data-discover-id="${it.id}"]`);
      await el.scrollIntoViewIfNeeded({ timeout: 2000 }).catch(() => {});
      const ok = await el.screenshot({ path: `${OUT}/${crop}`, timeout: 4000 }).then(() => true).catch(() => false);
      const rec = { sig, kind: it.kind, count: 1, pages: [url], firstText: it.text, shape: it.shape, styles: it.st, cls: it.cls, html: it.html, crop: ok ? crop : null, sel: it.sel };
      if (INTERACTIVE.has(it.kind) || (it.kind === "card" && it.pointer)) {
        rec.states = await measureStates(page, el, `${it.kind}-${n}`);
        stateCount += Object.keys(rec.states).length;
      }
      inv.set(sig, rec);
    }
    for (const h of links) { const u = norm(h); if (u && !seen.has(u) && !EXC.test(u) && (!INC || INC.test(u))) { seen.add(u); queue.push(u); } }
    visited++;
    dry = fresh === 0 ? dry + 1 : 0;
    log.push({ url, items: items.length, fresh, opened });
    console.log(`${String(visited).padStart(2)}  +${String(fresh).padStart(3)} mới / ${String(items.length).padStart(4)} khối  mở ${opened}  trạng thái Σ${stateCount}  ${url}`);
  } catch (e) { console.log(`   lỗi trang ${url}: ${String(e.message).slice(0, 80)}`); }
  finally { clearTimeout(guard); await page.close().catch(() => {}); save(); }
}
await b.close();

/* ghép biến thể "đang chọn" với biến thể thường cùng họ: cùng loại, cùng hình dạng con, chung ≥ 60%
   class (bỏ class màu/z/trạng thái); lấy cặp giống nhất */
const tok = (c) => new Set(c.split(/\s+/).filter((t) => t && !/^(is-active|active|selected|z-|text-stone-|text-neutral-|bg-|border-stone-|hover:|aria-|data-)/.test(t)));
const jac = (a, b) => { const A = tok(a), B = tok(b); if (!A.size && !B.size) return 0; let i = 0; for (const x of A) if (B.has(x)) i++; return i / (A.size + B.size - i); };
let pairs = 0;
for (const p of inv.values()) {
  if (!p.sel) continue;
  let best = null, bs = 0.6;
  for (const q of inv.values()) if (q !== p && !q.sel && q.kind === p.kind && q.shape === p.shape) { const j = jac(p.cls, q.cls); if (j >= bs) { bs = j; best = q; } }
  if (best) { p.selectedOf = best.sig; pairs++; }
}
const list = [...inv.values()].sort((a, b) => a.kind.localeCompare(b.kind) || b.count - a.count);
writeFileSync(`${OUT}/inventory.json`, JSON.stringify({ start, visited, stoppedBy: dry >= SAT ? "saturated" : queue.length ? "page-budget" : "no-more-links", pages: log, patterns: list }, null, 1));
const byKind = list.reduce((m, p) => ((m[p.kind] = (m[p.kind] || 0) + 1), m), {});
console.log(`\n${list.length} pattern từ ${visited} trang · dừng vì ${dry >= SAT ? `${SAT} trang liền không có gì mới` : queue.length ? "hết ngân sách trang" : "hết link"}`);
console.log(Object.entries(byKind).map(([k, v]) => `${k} ${v}`).join(" · "));
const stTotals = list.reduce((m, p) => { for (const k of Object.keys(p.states || {})) m[k] = (m[k] || 0) + 1; return m; }, {});
console.log(`trạng thái: ${Object.entries(stTotals).map(([k, v]) => `${k} ${v}`).join(" · ") || "0"} · cặp selected ${pairs}`);
