#!/usr/bin/env node
// html-visual-gate — cổng CHẠY THẬT cho HTML framework sinh ra: mở trang bằng trình duyệt ở CẢ sáng và tối rồi ĐO.
// Bắt thứ cổng tĩnh (frontend-antipattern.py) không thấy được vì phải dựng hình mới biết:
//   contrast   chữ chìm vào nền (< 4.5:1; chữ ≥ 24px hoặc ≥ 18.66px đậm: 3:1)
//   tight      hai khối có nền/viền riêng xếp dọc dính nhau (< 8px), hoặc chữ chạm mép khối cha (padding < 6px)
//   overlap    hộp chữ giao với hộp icon/svg anh em trong cùng một node (> 2px mỗi chiều)
//   stripe     sọc màu một cạnh vẽ bằng ::before/::after (cổng tĩnh chỉ thấy border-left / inset)
//   rounded-edge  phần tử ĐÃ bo góc (> 0.5px) mà 1–3 cạnh có viền màu nhấn lệch màu (> 40) hoặc dày ≥ 1.5× cạnh còn lại (đo CẢ sáng lẫn tối)
//   horizontal-scroll  trang cuộn ngang ở bề rộng 320/375/768/1360 (scrollWidth > clientWidth + 1)
//   clickable-wrap     nút / tab / link điều hướng (nav a, footer a, a.btn) bẻ chữ thành ≥ 2 dòng ở 320 hoặc 1360; bỏ qua link trong <p>
//   italic-display     chữ hiển thị (h1–h6 hoặc ≥ 24px) in nghiêng — phủ chỗ cổng tĩnh sót (class tiêu đề, <em> sau thẻ khác)
//   uppercase-tight-leading  chữ HOA ≥ 24px có line-height < 1.0 × cỡ chữ (dòng HOA dính nhau)
//   toggle     có nút đổi sáng/tối; bấm thì nền đổi chiều sáng; tải lại vẫn giữ
//   glass      phần tử khai kính (backdrop-filter) phải còn kính ở CẢ hai chế độ
// Usage: NODE_PATH=$(npm root -g) node html-visual-gate.mjs <trang.html …> [--json] [--shots <dir>] [--only contrast,tight]
// Exit: 0 sạch (có thể kèm dòng ⚠ WARN: horizontal-scroll, clickable-wrap) · 2 có lỗi · 4 không có Playwright (SKIP có tên — caller không được đếm là PASS).
// Sinh ra 20/09/2026 sau khi bộ đo nháp trả 0 ở hai cột mà user thấy lỗi bằng mắt: mỗi luật ở đây có fixture XẤU chứng minh nó cắn
// (harness/tests/html-visual-gate-test.sh).
import { pathToFileURL } from 'url';
import { mkdirSync, existsSync } from 'fs';
import { resolve, basename } from 'path';
import { createRequire } from 'node:module';
// Playwright: ESM KHÔNG đọc NODE_PATH → đi qua createRequire như harness/tests/orca-graph-ui-smoke.mjs: <repo>/scratchpad/node_modules
// (do /playwright-verify cài) → cạnh file này → NODE_PATH (global).
let chromium;
try { const tryReq = base => { try { return createRequire(base)('playwright'); } catch { return null; } };
  // NODE_PATH cũng phải được thử: ở MÁY KHÁCH tool chạy từ ~/.claude/harness/fdk/tools nên không có
  // scratchpad/node_modules nào cạnh nó — không thử NODE_PATH thì cổng luôn SKIP và downstream mất hẳn cổng chạy-thật.
  const np = (process.env.NODE_PATH || '').split(':').filter(Boolean).map(d => tryReq(d + '/_.js'));
  const mod = tryReq(new URL('../../scratchpad/_.js', import.meta.url)) || tryReq(import.meta.url) || tryReq(process.cwd() + '/scratchpad/_.js') || tryReq(process.cwd() + '/_.js') || np.find(Boolean);
  if (!mod) throw new Error('no playwright'); chromium = mod.chromium; } catch (e) { console.error('SKIP html-visual-gate: không có Playwright (npm i -g playwright && npx playwright install chromium)'); process.exit(4); }
const argv = process.argv.slice(2); const flag = n => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : null; };
const asJson = argv.includes('--json'), shots = flag('--shots'), only = (flag('--only') || '').split(',').filter(Boolean);
const pages = argv.filter((a, i) => !a.startsWith('--') && !['--shots', '--only'].includes(argv[i - 1]));
if (!pages.length) { console.error('cần ít nhất một trang .html'); process.exit(1); }
if (shots) mkdirSync(shots, { recursive: true });

const MEASURE = () => {
  // Mọi định dạng màu (rgb, oklab do color-mix sinh ra, color(srgb …), tên màu) → RGBA thật bằng canvas của trình duyệt. Đọc số thô từ
  // chuỗi `oklab(0.82 -0.02 -0.07)` như RGB là SAI (20/09/2026: báo nhầm chữ sáng thành 1.2:1).
  const _cv = document.createElement('canvas'); _cv.width = _cv.height = 1; const _cx = _cv.getContext('2d', { willReadFrequently: true }); const _memo = new Map();
  const norm = c => { if (!c) return c; if (/^rgba?\(/.test(c)) return c; if (_memo.has(c)) return _memo.get(c); _cx.clearRect(0, 0, 1, 1); _cx.fillStyle = '#000'; _cx.fillStyle = c; _cx.fillRect(0, 0, 1, 1); const d = _cx.getImageData(0, 0, 1, 1).data; const am = c.match(/\/\s*([\d.]+%?)\s*\)/); let a = d[3] / 255; const v = `rgba(${d[0]}, ${d[1]}, ${d[2]}, ${a})`; _memo.set(c, v); return v; };
  const lum = c0 => { const c = norm(c0); const m = (c || '').match(/[\d.]+/g); if (!m || m.length < 3) return null; const [r, g, b] = m.slice(0, 3).map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }); return { L: 0.2126 * r + 0.7152 * g + 0.0722 * b, a: m[3] === undefined ? 1 : +m[3] }; };
  const vis = el => { const r = el.getBoundingClientRect(), cs = getComputedStyle(el); return r.width > 2 && r.height > 2 && cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity > 0.05 && el.offsetParent !== null; };
  const name = el => (el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/)[0] : ''));
  // nền THẬT sau chữ: cộng dồn các lớp bán trong suốt từ trong ra ngoài, đáy là nền trang theo chế độ
  const pageDark = (() => { const l = lum(getComputedStyle(document.body).backgroundColor); const h = lum(getComputedStyle(document.documentElement).backgroundColor); const base = (l && l.a > .5) ? l.L : (h && h.a > .5 ? h.L : null); return base === null ? document.documentElement.getAttribute('data-theme') === 'dark' : base < 0.3; })();
  const bgL = el => { const layers = []; for (let n = el; n; n = n.parentElement) { const cs = getComputedStyle(n); const l = lum(cs.backgroundColor); if (l && l.a > 0.02) layers.push(l); if (cs.backgroundImage && cs.backgroundImage !== 'none' && /gradient/.test(cs.backgroundImage)) { const g = cs.backgroundImage.match(/rgba?\([^)]*\)/g); if (g) { const ls = g.map(lum).filter(x => x && x.a > 0.3); if (ls.length) layers.push({ L: ls.reduce((s, x) => s + x.L, 0) / ls.length, a: Math.max(...ls.map(x => x.a)) * 0.9 }); } } }
    let L = pageDark ? 0.012 : 0.96; for (const l of layers.reverse()) L = l.L * l.a + L * (1 - l.a); return L; };
  const out = { contrast: [], tight: [], overlap: [], stripe: [], rounded_edge: [], italic_display: [], upper_tight: [], glass: 0, texts: 0, pageDark };
  const seenText = new Set();
  for (const el of document.querySelectorAll('body *')) {
    if (!vis(el) || el.closest('[aria-hidden="true"],svg,script,style,noscript')) continue;
    // WCAG 1.4.3 miễn trừ ĐIỀU KHIỂN ĐANG TẮT — nút disabled vốn được làm mờ để báo "bấm không được",
    // bắt nó đạt 4,5:1 là đỏ giả (20/09/2026: nút Overview disabled của trang delta archify).
    if (el.closest(':disabled,[aria-disabled="true"],fieldset[disabled]')) continue;
    // Làm mờ CÓ CHỦ Ý (node ngoài tiêu điểm của đồ thị, bóng vị trí cũ trong bảng so sánh…): trang phải TỰ KHAI
    // bằng data-ovs-deemphasized ngay lúc làm mờ. Khai báo tường minh nên vẫn kiểm được; suy đoán theo opacity
    // thì mọi chữ nhạt đều thoát, kể cả chữ nhạt do lỗi.
    if (el.closest('[data-ovs-deemphasized]')) continue;
    const own = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim().length > 1).map(n => n.textContent.trim()).join(' ');
    if (!own) continue; const cs = getComputedStyle(el); out.texts++;
    if (cs.backgroundClip === 'text' || cs.webkitBackgroundClip === 'text') continue;       // gradient-text: cổng tĩnh đã FAIL, ở đây đo sẽ sai
    const f = lum(cs.color); if (!f) continue; const fa = f.a * (+cs.opacity);
    const B = bgL(el), F = f.L * fa + B * (1 - fa), cr = (Math.max(F, B) + 0.05) / (Math.min(F, B) + 0.05);
    const px = parseFloat(cs.fontSize), big = px >= 24 || (px >= 18.66 && +cs.fontWeight >= 600), need = big ? 3 : 4.5;
    if (cr < need) { const k = name(el) + '|' + cr.toFixed(1); if (!seenText.has(k)) { seenText.add(k); const id = out.contrast.length; el.setAttribute('data-ovs-gate-i', id); out.contrast.push({ id, el: name(el), text: own.slice(0, 36), ratio: +cr.toFixed(2), need, fgL: F, fgRaw: f.L, fgA: fa }); } }
  }
  // chữ TRONG SVG (nhãn node, nhãn vùng của sơ đồ): màu chữ là `fill`; nền do bước điểm-ảnh phía Node xác minh (ước lượng ở đây chỉ để lọc sơ bộ)
  for (const el of document.querySelectorAll('svg text')) { if (el.closest('[aria-hidden="true"],[data-ovs-deemphasized]') || !el.textContent.trim() || el.textContent.trim().length < 2) continue; const r = el.getBoundingClientRect(); if (r.width < 6 || r.height < 5) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity < 0.05) continue; const f = lum(cs.fill); if (!f) continue; out.texts++;
    let op = 1; for (let n = el; n && n.tagName.toLowerCase() !== 'html'; n = n.parentElement) op *= +getComputedStyle(n).opacity || 1; const fa = f.a * (+cs.fillOpacity || 1) * op;
    const px = parseFloat(cs.fontSize) || 12, need = px >= 24 ? 3 : 4.5; const id = out.contrast.length; el.setAttribute('data-ovs-gate-i', id);
    out.contrast.push({ id, el: 'svg text' + (el.getAttribute('class') ? '.' + el.getAttribute('class').split(' ')[0] : ''), text: el.textContent.trim().slice(0, 36), ratio: 0, need, fgL: f.L, fgRaw: f.L, fgA: fa, svg: true }); }
  const boxy = el => { if (!vis(el)) return false; const cs = getComputedStyle(el), r = el.getBoundingClientRect(); if (r.height < 28 || r.width < 80) return false; const bg = lum(cs.backgroundColor); return (parseFloat(cs.borderTopWidth) > 0 && parseFloat(cs.borderBottomWidth) > 0) || (bg && bg.a > 0.06) || (cs.backdropFilter && cs.backdropFilter !== 'none') || cs.boxShadow !== 'none'; };
  for (const par of document.querySelectorAll('body, body *')) { const kids = [...par.children].filter(boxy); if (kids.length < 2) continue;
    for (let i = 1; i < kids.length; i++) { const a = kids[i - 1].getBoundingClientRect(), c = kids[i].getBoundingClientRect(); const gap = c.top - a.bottom;
      const sameCol = Math.min(a.right, c.right) - Math.max(a.left, c.left) > Math.min(a.width, c.width) * 0.6;
      if (sameCol && gap > -1 && gap < 8 && out.tight.length < 40) out.tight.push({ a: name(kids[i - 1]), b: name(kids[i]), gap: +gap.toFixed(1), kind: 'khối dính nhau' }); } }
  for (const el of document.querySelectorAll('body *')) { if (!boxy(el) || el.closest('svg')) continue; const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    if (/^inline/.test(cs.display) || /^(code|kbd|samp|span|a|label|button|input|select|textarea|th|td)$/i.test(el.tagName)) continue;   // chip/code/nút nội dòng: padding nhỏ là bình thường
    const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 3); if (!hasText) continue;
    const pads = [cs.paddingTop, cs.paddingBottom, cs.paddingLeft, cs.paddingRight].map(parseFloat); if (Math.min(...pads) < 6 && r.height > 36 && out.tight.length < 40) out.tight.push({ a: name(el), b: '(chữ chạm mép)', gap: Math.min(...pads), kind: 'padding quá hẹp' }); }
  // icon đè chữ: trong cùng một cha, hộp của svg/img/i.icon giao hộp của phần tử chứa chữ
  for (const par of document.querySelectorAll('body *')) { if (!vis(par) || par.children.length < 2 || par.children.length > 8) continue;
    // icon = hình NHỎ (≤ 72px). SVG lớn phủ cả vùng (lớp nối dây của mind-map, biểu đồ) là LỚP NỀN, không phải icon đè chữ.
    const icons = [...par.children].filter(e => { if (!vis(e)) return false; const r = e.getBoundingClientRect(); if (r.width > 72 || r.height > 72) return false; if (/^i$/i.test(e.tagName) && e.textContent.trim().length > 0) return false;   // <i> có chữ = chữ NGHIÊNG, không phải icon
      return /^(svg|img|i)$/i.test(e.tagName) || /icon|glyph|ico\b/i.test(typeof e.className === 'string' ? e.className : ''); });
    const texts = [...par.children].filter(e => vis(e) && !icons.includes(e) && e.textContent.trim().length > 2 && !e.querySelector('svg,img'));
    for (const ic of icons) for (const tx of texts) { const a = ic.getBoundingClientRect(); const rg = document.createRange(); rg.selectNodeContents(tx); const b = rg.getBoundingClientRect();
      const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left), oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (ox > 2 && oy > 2 && out.overlap.length < 30) out.overlap.push({ node: name(par), icon: name(ic), text: tx.textContent.trim().slice(0, 28), ox: +ox.toFixed(0), oy: +oy.toFixed(0) }); } }
  // SVG: <text> giao với <use>/<image>/<path class=icon> trong cùng <g>
  for (const g of document.querySelectorAll('svg g')) { const tx = [...g.children].filter(e => e.tagName.toLowerCase() === 'text' && e.textContent.trim().length > 2); const ic = [...g.children].filter(e => /^(use|image|foreignObject)$/i.test(e.tagName) || /icon|glyph|sigil/i.test(e.getAttribute('class') || '') || e.hasAttribute('data-semantic-sigil') || (e.tagName.toLowerCase() === 'g' && e.getAttribute('aria-hidden') === 'true'));
    for (const i of ic) for (const t of tx) { const a = i.getBoundingClientRect(), b = t.getBoundingClientRect(); if (a.width < 4 || b.width < 4) continue; const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left), oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (ox > 2 && oy > 2 && out.overlap.length < 30) out.overlap.push({ node: 'svg g', icon: i.tagName, text: t.textContent.trim().slice(0, 28), ox: +ox.toFixed(0), oy: +oy.toFixed(0) }); } }
  // sọc một cạnh vẽ bằng pseudo-element
  const sat = c => { const m = (c || '').match(/[\d.]+/g); if (!m) return 0; const [r, g, b] = m.map(Number); const a = m[3] === undefined ? 1 : +m[3]; const mx = Math.max(r, g, b), mn = Math.min(r, g, b); return a > 0.4 && mx > 0 ? (mx - mn) / mx : 0; };
  for (const el of document.querySelectorAll('body *')) { if (!vis(el)) continue; const r = el.getBoundingClientRect(); if (r.height < 28 || r.width < 60) continue;
    for (const ps of ['::before', '::after']) { const cs = getComputedStyle(el, ps); if (!cs || cs.content === 'none' || cs.display === 'none') continue; const w = parseFloat(cs.width), h = parseFloat(cs.height);
      if (w > 0 && w <= 6 && h >= r.height * 0.6 && (sat(cs.backgroundColor) > 0.35 || /gradient/.test(cs.backgroundImage)) && out.stripe.length < 60) out.stripe.push({ el: name(el), via: ps, w }); }
    const cs = getComputedStyle(el); for (const side of ['Left', 'Right']) { const w = parseFloat(cs['border' + side + 'Width']), others = ['Top', 'Bottom', side === 'Left' ? 'Right' : 'Left'].map(s => parseFloat(cs['border' + s + 'Width']));
      if (w >= 3 && w >= 2 * Math.max(...others, 0.5) && sat(cs['border' + side + 'Color']) > 0.35 && out.stripe.length < 60) out.stripe.push({ el: name(el), via: 'border-' + side.toLowerCase(), w }); } }
  // rounded-edge: đọc computed style (đã qua cascade) — bo góc + cạnh màu nhấn lệch (PLAN 210926 t6)
  const SIDES = ['Top', 'Right', 'Bottom', 'Left'];
  for (const el of document.querySelectorAll('body *')) { if (!vis(el) || el.closest('svg')) continue; const cs = getComputedStyle(el);
    if (!['TopLeft', 'TopRight', 'BottomRight', 'BottomLeft'].some(k => parseFloat(cs['border' + k + 'Radius']) > 0.5)) continue;
    { const rr = el.getBoundingClientRect(), half = Math.min(rr.width, rr.height) / 2 - 1; // phần tử TRÒN (spinner, avatar) — không phải thẻ có sọc (review t9 F3)
      if (['TopLeft', 'TopRight', 'BottomRight', 'BottomLeft'].every(k => parseFloat(cs['border' + k + 'Radius']) >= half || /%/.test(cs['border' + k + 'Radius']) && parseFloat(cs['border' + k + 'Radius']) >= 50)) continue; }
    const sig = SIDES.map(s => { const w = parseFloat(cs['border' + s + 'Width']), st = cs['border' + s + 'Style']; return w > 0 && st !== 'none' && st !== 'hidden' ? { c: norm(cs['border' + s + 'Color']), w } : null; });
    // ngưỡng t5: màu nhấn sat > 0.35; lệch = khác màu > 40 (kênh RGB lệch nhiều nhất) hoặc dày ≥ 1.5× — 1–3 cạnh, kề hay đối diện
    const rgb = c => ((c || '').match(/[\d.]+/g) || []).slice(0, 3).map(Number), dRGB = (x, y) => { const a = rgb(x), b = rgb(y); return Math.max(...a.map((v, i) => Math.abs(v - b[i]))); };
    const hit = sig.some(a => { if (!a || sat(a.c) <= 0.35) return false; const odd = sig.map((b, j) => b && b.c === a.c && b.w === a.w ? j : -1).filter(j => j >= 0);
      if (odd.length === 4) return false; const rest = sig.filter((b, j) => b && !odd.includes(j));
      return rest.every(b => dRGB(a.c, b.c) > 40) || a.w >= 1.5 * Math.max(0, ...rest.map(b => b.w)); });
    if (hit && out.rounded_edge.length < 60) out.rounded_edge.push(name(el)); }
  // italic-display + uppercase-tight-leading (PLAN 210926 t7): chữ HIỂN THỊ có text trực tiếp
  for (const el of document.querySelectorAll('body *')) { if (!vis(el) || el.closest('svg,script,style,[aria-hidden="true"]')) continue;
    if (![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1)) continue; const cs = getComputedStyle(el), px = parseFloat(cs.fontSize);
    if ((/^H[1-6]$/.test(el.tagName) || px >= 24) && /italic|oblique/.test(cs.fontStyle) && out.italic_display.length < 40) out.italic_display.push(name(el));
    const lh = parseFloat(cs.lineHeight);   // 'normal' → NaN → bỏ qua
    if (cs.textTransform === 'uppercase' && px >= 24 && lh / px < 1 && out.upper_tight.length < 40) out.upper_tight.push(`${name(el)} (${(lh / px).toFixed(2)})`); }
  out.glass = [...document.querySelectorAll('body *')].filter(e => { const cs = getComputedStyle(e); return vis(e) && ((cs.backdropFilter && cs.backdropFilter !== 'none') || (cs.webkitBackdropFilter && cs.webkitBackdropFilter !== 'none')); }).length;
  out.bodyL = (() => { const l = lum(getComputedStyle(document.body).backgroundColor), h = lum(getComputedStyle(document.documentElement).backgroundColor); return (l && l.a > .5) ? l.L : (h && h.a > .5 ? h.L : null); })();
  return out;
};

// horizontal-scroll + clickable-wrap: đo lại ở từng bề rộng (resize cùng trang, không tải lại)
const LAYOUT = () => { const d = document.documentElement, wrap = [];
  for (const el of document.querySelectorAll('button,[role=button],[role=tab],nav a,footer a,a.btn')) { if (el.closest('p,[aria-hidden="true"]')) continue;
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el); if (r.width < 2 || r.height < 2 || cs.visibility === 'hidden' || el.textContent.trim().length < 2) continue;
    const rg = document.createRange(); rg.selectNodeContents(el); const rs = [...rg.getClientRects()].filter(x => x.width > 1 && x.height > 1).sort((a, b) => a.top - b.top);
    // số dòng = số cụm rect KHÔNG chồng nhau theo chiều dọc (icon căn giữa cùng dòng với chữ không bị đếm thành dòng mới)
    let lines = 0, bot = -Infinity; for (const x of rs) { if (x.top >= bot - 1) { lines++; bot = x.bottom; } else bot = Math.max(bot, x.bottom); }
    if (lines >= 2 && wrap.length < 40) wrap.push((el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/)[0] : '')) + ' "' + el.textContent.trim().slice(0, 24) + '"'); }
  return { over: d.scrollWidth - d.clientWidth, wrap }; };
const WIDTHS = [320, 375, 768, 1360], WRAP_AT = [320, 1360];
const TOGGLE_SEL = '.theme-switch,[data-theme-toggle],.theme-toggle,#theme-toggle,#themeToggle,[aria-label*="giao diện" i],[aria-label*="theme" i],[class*="theme-t"],[id*="theme"]';
const on = k => !only.length || only.includes(k);
const b = await chromium.launch(); const report = []; let bad = 0;
for (const file of pages) { const abs = resolve(file); const row = { page: file, findings: {} };
  if (!existsSync(abs)) { row.error = 'không tồn tại'; bad++; report.push(row); continue; }
  for (const theme of ['light', 'dark']) {
    const ctx = await b.newContext({ viewport: { width: 1360, height: 900 }, colorScheme: theme, offline: true }); const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 140)));
    // chỉ đặt khi CHƯA có: đặt vô điều kiện thì lần reload của phép thử toggle bị ghi đè → báo nhầm NOT-PERSISTED
    await p.addInitScript(t => { try { for (const k of ['theme', 'ovs-theme', 'color-scheme', 'og-theme']) if (localStorage.getItem(k) === null) localStorage.setItem(k, t); } catch (e) {} }, theme);
    await p.goto(pathToFileURL(abs).href, { waitUntil: 'load', timeout: 30000 }).catch(e => errs.push('goto: ' + e.message.slice(0, 80)));
    await p.evaluate(t => { const d = document.documentElement; if (d.getAttribute('data-theme') !== t) d.setAttribute('data-theme', t); return document.fonts.ready; }, theme); await p.waitForTimeout(250);
    const m = await p.evaluate(MEASURE); m.jsErrors = errs;
    // Xác minh bằng ĐIỂM ẢNH: nền ước lượng từ CSS sai khi có lớp giả (::before), backdrop-filter, ảnh nền cố định… Chụp đúng ô chứa chữ,
    // lấy màu CHIẾM NHIỀU NHẤT làm nền thật rồi tính lại; chỉ giữ finding khi điểm ảnh cũng xác nhận. (20/09/2026: bản ước lượng báo nhầm
    // logo đọc rõ mồn một là 2.05:1.)
    const verified = [];
    for (const c of m.contrast.slice(0, 90)) { const h = await p.$(`[data-ovs-gate-i="${c.id}"]`); if (!h) continue; let buf; try { buf = await h.screenshot({ type: 'png', timeout: 4000 }); } catch (e) { verified.push(c); continue; }
      const px = await p.evaluate(async ([b64, fgL]) => { const img = new Image(); img.src = 'data:image/png;base64,' + b64; await img.decode(); const cv = document.createElement('canvas'); cv.width = img.width; cv.height = img.height; const g = cv.getContext('2d'); g.drawImage(img, 0, 0); const d = g.getImageData(0, 0, cv.width, cv.height).data; const hist = new Map();
        for (let i = 0; i < d.length; i += 4) { const k = (d[i] >> 3) << 10 | (d[i + 1] >> 3) << 5 | (d[i + 2] >> 3); hist.set(k, (hist.get(k) || 0) + 1); } // nền = màu chiếm nhiều nhất TRỪ các điểm ảnh của chính nét chữ (ô nhỏ chữ đậm thì nét chữ có thể chiếm đa số → đo ra 1:1 giả).
        const lumOf = k => { const c = [(k >> 10) << 3, ((k >> 5) & 31) << 3, (k & 31) << 3].map(v => { v = (v + 4) / 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; };
        let best = 0, bk = 0, best2 = 0, bk2 = -1; for (const [k, n] of hist) { if (n > best) { best = n; bk = k; } if (Math.abs(lumOf(k) - fgL) > 0.06 && n > best2) { best2 = n; bk2 = k; } }
        if (bk2 >= 0 && best2 > d.length / 4 * 0.12) bk = bk2;
        const ch = [(bk >> 10) << 3, ((bk >> 5) & 31) << 3, (bk & 31) << 3].map(v => { v = (v + 4) / 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }); return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]; }, [buf.toString('base64'), c.fgRaw]);
      const F = c.fgRaw * c.fgA + px * (1 - c.fgA), cr = (Math.max(F, px) + 0.05) / (Math.min(F, px) + 0.05);
      if (cr < c.need) verified.push({ ...c, ratio: +cr.toFixed(2), by: 'pixel' }); }
    m.contrast = verified.concat(m.contrast.slice(90).filter(c => !c.svg)); row.findings[theme] = m;
    if (shots) await p.screenshot({ path: `${shots}/${basename(file, '.html')}-${theme}.png` });
    if (theme === 'light' && (on('horizontal-scroll') || on('clickable-wrap'))) { row.hscroll = []; row.wrap = [];
      for (const w of WIDTHS) { await p.setViewportSize({ width: w, height: 900 }); await p.waitForTimeout(150); const l = await p.evaluate(LAYOUT);
        if (l.over > 1) row.hscroll.push({ w, over: l.over }); if (WRAP_AT.includes(w)) for (const x of l.wrap) row.wrap.push(`${x} @${w}`); }
      await p.setViewportSize({ width: 1360, height: 900 }); await p.waitForTimeout(150); }
    if (theme === 'light') { // toggle: bấm → nền đổi chiều; tải lại → giữ
      // phần tử NHÌN THẤY đầu tiên khớp selector (selector rộng còn khớp cả <script id="…theme…"> / <meta name="theme-color"> trong <head>)
      let tg = null; for (const h of await p.$$(TOGGLE_SEL)) { if (await h.evaluate(e => { const r = e.getBoundingClientRect(); return r.width > 4 && r.height > 4 && !/^(script|style|meta|link|template)$/i.test(e.tagName); })) { tg = h; break; } }
      const follows = await p.$('[data-ovs-theme-follow]');
      if (follows) row.toggle = 'follows-parent'; else if (!tg) row.toggle = 'MISSING';
      else { const lumNow = () => p.evaluate(() => { const f = c => { const m = c.match(/[\d.]+/g); if (!m) return null; const a = m[3] === undefined ? 1 : +m[3]; return a < .5 ? null : (0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2]) / 255; }; return f(getComputedStyle(document.body).backgroundColor) ?? f(getComputedStyle(document.documentElement).backgroundColor) ?? (document.documentElement.getAttribute('data-theme') === 'dark' ? 0 : 1); });
        const before = await lumNow(); await tg.click({ force: true }).catch(() => {}); await p.waitForTimeout(700); const after = await lumNow();
        const attr = await p.evaluate(() => document.documentElement.getAttribute('data-theme')); await p.reload({ waitUntil: 'load' }).catch(() => {}); await p.waitForTimeout(200);
        const kept = await p.evaluate(() => document.documentElement.getAttribute('data-theme'));
        row.toggle = Math.abs(before - after) < 0.25 ? 'NO-EFFECT' : (kept !== attr ? 'NOT-PERSISTED' : 'ok'); } }
    await ctx.close(); }
  const L = row.findings.light, D = row.findings.dark; const probs = [];
  if (on('contrast')) for (const [t, m] of [['sáng', L], ['tối', D]]) if (m.contrast.length) probs.push(`contrast(${t}): ${m.contrast.length} chữ chìm — vd "${m.contrast[0].text}" ${m.contrast[0].ratio}:1 (cần ${m.contrast[0].need}) ở ${m.contrast[0].el}`);
  if (on('tight') && L.tight.length) probs.push(`tight: ${L.tight.length} chỗ — vd ${L.tight[0].a} ↔ ${L.tight[0].b} (${L.tight[0].kind}, ${L.tight[0].gap}px)`);
  if (on('overlap') && (L.overlap.length || D.overlap.length)) { const o = (L.overlap[0] || D.overlap[0]); probs.push(`overlap: ${Math.max(L.overlap.length, D.overlap.length)} icon đè chữ — vd "${o.text}" trong ${o.node} (${o.ox}×${o.oy}px)`); }
  if (on('stripe') && L.stripe.length) probs.push(`stripe: ${L.stripe.length} sọc màu một cạnh — vd ${L.stripe[0].el} (${L.stripe[0].via})`);
  if (on('rounded-edge') && (L.rounded_edge.length || D.rounded_edge.length)) probs.push(`rounded-edge: ${Math.max(L.rounded_edge.length, D.rounded_edge.length)} phần tử bo góc có cạnh màu — vd ${L.rounded_edge[0] || D.rounded_edge[0]}${L.rounded_edge.length ? '' : ' (chỉ ở tối)'}`);
  // WARN (in ⚠, KHÔNG đổi exit code — mọi caller coi rc≠0 là đỏ). Đo t7 21/09/2026 trên 39 trang của --all:
  //   horizontal-scroll 33 trang (viewer orca-graph từ engine repo riêng tràn ở 320/375; bảng/sơ đồ rộng) → nợ lớn → WARN.
  //   clickable-wrap    10 trang, báo giả thấy rõ: thẻ node role=button nhiều dòng CÓ CHỦ Ý (overstack.html), link tên file dài
  //                     trong danh sách (atlas, *.graph.html) → WARN.
  //   italic-display, uppercase-tight-leading: 0 trang → FAIL (tất định, không nợ).  ponytail: nâng WARN lên FAIL khi nợ về 0.
  const warns = [];
  if (on('horizontal-scroll') && row.hscroll.length) warns.push(`horizontal-scroll: cuộn ngang ở ${row.hscroll.map(h => h.w + 'px (+' + h.over + ')').join(', ')}`);
  if (on('clickable-wrap') && row.wrap.length) warns.push(`clickable-wrap: ${row.wrap.length} nút/link bẻ dòng — vd ${row.wrap[0]}`);
  if (on('italic-display') && L.italic_display.length) probs.push(`italic-display: ${L.italic_display.length} chữ hiển thị in nghiêng — vd ${L.italic_display[0]}`);
  if (on('uppercase-tight-leading') && L.upper_tight.length) probs.push(`uppercase-tight-leading: ${L.upper_tight.length} chữ HOA lớn dòng dính — vd ${L.upper_tight[0]}`);
  if (on('toggle') && row.toggle !== 'ok' && row.toggle !== 'follows-parent') probs.push(`toggle: ${row.toggle}`);
  if (on('toggle') && row.toggle === 'ok' && L.bodyL !== null && D.bodyL !== null && Math.abs(L.bodyL - D.bodyL) < 0.25) probs.push('toggle: sáng và tối cho CÙNG một nền');
  if (on('glass') && L.glass > 0 && D.glass === 0) probs.push(`glass: sáng có ${L.glass} lớp kính, tối mất hết`);
  if (on('glass') && D.glass > 0 && L.glass === 0) probs.push(`glass: tối có ${D.glass} lớp kính, sáng mất hết`);
  const je = [...L.jsErrors, ...D.jsErrors]; if (je.length) probs.push(`js: ${je[0]}`);
  row.problems = probs; row.warnings = warns; if (probs.length) bad++; report.push(row); }
await b.close();
if (asJson) console.log(JSON.stringify(report.map(r => ({ page: r.page, toggle: r.toggle, problems: r.problems, warnings: r.warnings, light: r.findings.light && { contrast: r.findings.light.contrast, tight: r.findings.light.tight, overlap: r.findings.light.overlap, stripe: r.findings.light.stripe, rounded_edge: r.findings.light.rounded_edge, italic_display: r.findings.light.italic_display, upper_tight: r.findings.light.upper_tight, glass: r.findings.light.glass }, hscroll: r.hscroll, wrap: r.wrap, dark: r.findings.dark && { contrast: r.findings.dark.contrast, rounded_edge: r.findings.dark.rounded_edge, overlap: r.findings.dark.overlap, glass: r.findings.dark.glass } })), null, 1));
else { for (const r of report) { console.log(`${r.problems && r.problems.length ? '✗' : '✓'} ${r.page}${r.error ? ' — ' + r.error : ''}`); for (const q of r.problems || []) console.log('    ' + q); for (const q of r.warnings || []) console.log('    ⚠ ' + q); }
  console.log(`html-visual-gate: ${report.length - bad}/${report.length} trang đạt`); }
process.exit(bad ? 2 : 0);
