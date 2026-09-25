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
//   toggle     có nút đổi sáng/tối; bấm thì nền đổi chiều sáng; tải lại vẫn giữ; nút KHÔNG nhảy chỗ trong lúc đang bấm (±1px)
//   glass      phần tử khai kính (backdrop-filter) phải còn kính ở CẢ hai chế độ
//   Nhịp chữ & khoảng cách (PLAN 220926 t4, fdk/wiki/sources/220926-spacing-standards.md) — đo một lượt ở chế độ sáng:
//   line-height-body   FAIL  p/li/dd/blockquote/td có chữ trực tiếp, ≥ 2 dòng, line-height/font-size < 1.45 (bỏ nav, button, svg, pre/code)
//   measure-too-wide   WARN  p ≥ 3 dòng, ký tự/dòng THẬT (số ký tự ÷ số dòng) > 85 (WCAG 1.4.8: ≤ 80; token --measure 34em)
//   heading-proximity  WARN  h2/h3 có anh em trước & sau: khoảng trên < 1.5 × khoảng dưới (USWDS)
//   hierarchy-flat     FAIL  nhãn trong <nav> (class grp|group|brand|logo|eyebrow|section-title, h2–h6) khác `nav a` gần nhất < 2/4 thuộc tính
//   sentence-case      FAIL  tiêu đề/nhãn/nút/tab/mục nav viết hoa chữ đầu (tha định danh, tên riêng, code, data-case="keep")
//   heading-scale      FAIL  cấp tiêu đề có mặt to → nhỏ (h1 > h2 > h3 > h4) và không nhỏ hơn chữ nội dung
//   title-scale        FAIL  tên trang (brand/logo/h1) ≥ 1,2 × chữ lớn nhất của mục nav/tab
//   eye-rest           WARN  màn đầu ≤ 55% là chữ/khối, không dải dày liền > 520px thiếu khoảng trống ≥ 24px
//   line-over-text     FAIL  phần tử có định vị (absolute/fixed/sticky), mảnh ≤ 6px, có màu, cắt ngang chữ không thuộc nó (vạch tiến độ đè mục)
//   row-wrap           FAIL  hàng flex ngang ≥ 2 mục nhỏ (≤ 64px cao) rơi xuống ≥ 2 dòng ở 375 hoặc 1360 — dùng .ovs-line (một dòng, mờ mép, hover thấy đủ)
//   action-left        FAIL  hàng nút kết thúc form/dialog/thẻ không chạm mép phải nội dung (±4px); ưu tiên góc: phải-dưới → trái-trên → phải-trên → trái-dưới
//   field-ring         FAIL  ô nhập chữ có viền lúc nghỉ, outline/box-shadow khi focus, hoặc focus không đổi nền (phản hồi phải bằng nền đậm dần)
//   fixed-trapped      FAIL  position:fixed có left:0 + right:0 mà rộng < cửa sổ (tổ tiên transform/filter/backdrop-filter/contain nhốt lại)
//   band-misaligned    FAIL  dải (≥ 70% rộng cha) có nền/viền trên-dưới riêng mà mép trái/phải không khớp mép cha, mép nội dung cha hay mép anh em
//   kanban-uniform     FAIL  bảng kanban (≥ 2 cột lane|kanban|[data-kanban-lane]): mọi thẻ cùng rộng + cao (±2px) và cùng style
//   tap-target         WARN  nav a / button / [role=button] < 24×24 (WCAG 2.5.8); tha link trong p, li ngoài nav, aria-hidden
// Usage: NODE_PATH=$(npm root -g) node html-visual-gate.mjs <trang.html …> [--json] [--shots <dir>] [--only contrast,tight]
// Exit: 0 sạch (có thể kèm dòng ⚠ WARN: horizontal-scroll, clickable-wrap, measure-too-wide, heading-proximity, tap-target) · 2 có lỗi · 4 không có Playwright (SKIP có tên — caller không được đếm là PASS).
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

const MEASURE = (theme) => {
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
  // Nhịp chữ & khoảng cách (PLAN 220926 t4, chuẩn fdk/wiki/sources/220926-spacing-standards.md) — đo MỘT lượt ở chế độ sáng.
  Object.assign(out, { line_body: [], measure: [], heading_prox: [], hier_flat: [], tap: [] });
  if (theme === 'light') {
    const ownText = el => [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1);
    const box = (el, cs) => { const r = el.getBoundingClientRect(), f = k => parseFloat(cs[k]) || 0;
      return { h: r.height - f('paddingTop') - f('paddingBottom') - f('borderTopWidth') - f('borderBottomWidth'), w: r.width - f('paddingLeft') - f('paddingRight') - f('borderLeftWidth') - f('borderRightWidth') }; };
    const lhOf = cs => { const v = parseFloat(cs.lineHeight); return isNaN(v) ? 1.2 * parseFloat(cs.fontSize) : v; };   // 'normal' ≈ 1.2 (Chromium, font sans thường)
    // line-height-body: chữ nội dung ≥ 2 dòng phải giãn ≥ 1.5 (ngưỡng 1.45 trừ sai số làm tròn px)
    for (const el of document.querySelectorAll('p,li,dd,blockquote,td')) { if (!vis(el) || !ownText(el) || el.closest('nav,button,svg,pre,code,[aria-hidden="true"]')) continue;
      const cs = getComputedStyle(el), fs = parseFloat(cs.fontSize), lh = lhOf(cs), b = box(el, cs);
      if (b.h > 1.8 * lh && lh / fs < 1.45 && out.line_body.length < 40) out.line_body.push(`${name(el)} (${(lh / fs).toFixed(2)})`);
      // measure-too-wide: ký tự/dòng THẬT = số ký tự ÷ số dòng hiển thị (WCAG 1.4.8: ≤ 80). Bản đầu ước lượng bề rộng ÷ 0,5em —
      // lệch với token độ dài dòng vì chữ trung bình hẹp hơn 0,5em giả định (token nay là --measure:34em ≈ 68 ký tự thật). Đo đoạn ≥ 3 dòng
      // (dòng cuối ngắn kéo trung bình xuống ít hơn) và bỏ dòng cuối khỏi mẫu số.
      const lines = Math.round(b.h / lh), chars = el.textContent.replace(/\s+/g, ' ').trim().length;
      if (el.tagName === 'P' && lines >= 3 && chars / (lines - 0.5) > 85 && out.measure.length < 40) out.measure.push(`${name(el)} (~${Math.round(chars / (lines - 0.5))} ký tự/dòng)`); }
    // heading-proximity: khoảng trên tiêu đề ≥ 1.5 × khoảng dưới (USWDS) — đo khoảng HÌNH HỌC thật (đã gồm margin collapse)
    const sib = (el, dir) => { for (let n = el[dir]; n; n = n[dir]) if (vis(n)) return n; return null; };
    for (const h of document.querySelectorAll('h2,h3')) { if (!vis(h) || h.closest('svg,nav,[aria-hidden="true"]') || /absolute|fixed/.test(getComputedStyle(h).position)) continue;
      const pr = sib(h, 'previousElementSibling'), nx = sib(h, 'nextElementSibling'); if (!pr || !nx) continue;
      const a = pr.getBoundingClientRect(), r = h.getBoundingClientRect(), c = nx.getBoundingClientRect();
      const above = r.top - a.bottom, below = c.top - r.bottom; if (above < -1 || below <= 0) continue;   // không xếp dọc (lưới/flex ngang) → bỏ
      if (above < 1.5 * below && out.heading_prox.length < 40) out.heading_prox.push(`${name(h)} "${h.textContent.trim().slice(0, 24)}" trên ${Math.round(above)}px < 1.5 × dưới ${Math.round(below)}px`); }
    // hierarchy-flat: nhãn trong <nav> phải khác mục liên kết gần nhất ở ≥ 2/4 thuộc tính (cỡ · độ đậm · màu · hoa/thường)
    const rgb = c => ((norm(c) || '').match(/[\d.]+/g) || []).slice(0, 3).map(Number);
    for (const nav of document.querySelectorAll('nav')) { const links = [...nav.querySelectorAll('a')].filter(vis);
      for (const lb of nav.querySelectorAll('*')) { const cls = typeof lb.className === 'string' ? lb.className : '';
        if (!(/^H[2-6]$/.test(lb.tagName) || /grp|group|brand|logo|eyebrow|section-title/i.test(cls)) || !vis(lb) || !ownText(lb) || lb.querySelector('a')) continue;
        const r = lb.getBoundingClientRect(), cands = links.filter(a => a !== lb && !a.contains(lb) && !lb.contains(a)); if (!cands.length) continue;
        const d = a => { const q = a.getBoundingClientRect(); return Math.hypot(q.left + q.width / 2 - r.left - r.width / 2, q.top + q.height / 2 - r.top - r.height / 2); };
        const ln = cands.reduce((x, y) => d(y) < d(x) ? y : x), A = getComputedStyle(lb), B = getComputedStyle(ln), ca = rgb(A.color), cb = rgb(B.color);
        const diff = [Math.abs(parseFloat(A.fontSize) - parseFloat(B.fontSize)) >= 1, Math.abs(+A.fontWeight - +B.fontWeight) >= 100,
          Math.max(...ca.map((v, i) => Math.abs(v - cb[i]))) > 40, (A.textTransform === 'uppercase') !== (B.textTransform === 'uppercase')].filter(Boolean).length;
        // ĐỘ NỔI (user 22/09 trên sidebar kanban: nhãn nhóm 'cần nổi bật hơn bằng màu tương phản hẳn'): khác mà CHÌM hơn vẫn là phẳng —
        // nhãn không được tương phản thấp hơn mục, và phải đậm hơn (≥ +100) hoặc to hơn mục.
        const crOf = el => { const l = lum(getComputedStyle(el).color), bg = bgL(el); if (!l) return 0; const hi = Math.max(l.L, bg), lo = Math.min(l.L, bg); return (hi + .05) / (lo + .05); };
        const dim = crOf(lb) < crOf(ln) - 0.3 && !(sat(A.color) > 0.35 && crOf(lb) >= 4.5),   // màu NHẤN đạt AA = cách nổi hợp lệ (brand tô accent)
               weak = +A.fontWeight < +B.fontWeight + 100 && parseFloat(A.fontSize) <= parseFloat(B.fontSize);
        if ((diff < 2 || dim || weak) && out.hier_flat.length < 40) out.hier_flat.push(`${name(lb)} "${lb.textContent.trim().slice(0, 20)}" vs ${name(ln)}: cỡ ${A.fontSize}/${B.fontSize} · đậm ${A.fontWeight}/${B.fontWeight} · tương phản ${crOf(lb).toFixed(1)}/${crOf(ln).toFixed(1)} · ${A.textTransform}/${B.textTransform} (${diff}/4 khác${dim ? ' · CHÌM hơn mục' : ''}${weak ? ' · không đậm/to hơn mục' : ''})`); } }
    // tap-target: vùng bấm ≥ 24×24 (WCAG 2.5.8) — tha link trong câu chữ (p, li ngoài nav) và phần tử aria-hidden
    for (const el of document.querySelectorAll('nav a,button,[role=button]')) { if (!vis(el) || el.closest('p,[aria-hidden="true"]') || (el.closest('li') && !el.closest('nav'))) continue;
      const r = el.getBoundingClientRect(); if ((r.height < 24 || r.width < 24) && out.tap.length < 40) out.tap.push(`${name(el)} "${el.textContent.trim().slice(0, 20)}" ${Math.round(r.width)}×${Math.round(r.height)}`); }
    // ── PLAN 220926 (user 22/09): chữ hoa đầu câu · tiêu đề to hơn nav/tab · các cấp tiêu đề to → nhỏ · khoảng nghỉ cho mắt.
    // Miễn khi trang TỰ KHAI yêu cầu đặc biệt: <meta name="overstack-exempt" content="sentence-case,heading-scale,…" data-reason="…">
    const ex = new Set(((document.querySelector('meta[name="overstack-exempt"]') || {}).content || '').split(/[\s,]+/).filter(Boolean));
    Object.assign(out, { sent_case: [], head_scale: [], title_scale: [], eye_rest: [] });
    const fsOf = el => parseFloat(getComputedStyle(el).fontSize);
    // sentence-case: nhãn/tiêu đề/mục nav/tab/nút bắt đầu bằng chữ THƯỜNG. Tha: định danh (có số, -, _, ., /, :, @), text-transform hoa, trong code.
    if (!ex.has('sentence-case')) {
      const IDENT = /[\d\-_.\/:@]/, BRANDS = new Set(['overstack', 'orca', 'llmwiki', 'npm', 'npx', 'git', 'gh', 'curl', 'claude', 'iphone', 'macos', 'ios']);
      for (const el of document.querySelectorAll('h1,h2,h3,h4,h5,h6,nav a,.brand,.logo,[role=tab],.tabs button,button,th,summary,legend,label')) {
        if (!vis(el) || el.closest('code,pre,kbd,svg,[aria-hidden="true"],[data-case="keep"]')) continue; const cs = getComputedStyle(el);
        if (/uppercase|capitalize/.test(cs.textTransform) || getComputedStyle(el, '::first-letter').textTransform === 'uppercase') continue;
        const txt = (el.innerText || '').trim().replace(/^[^\p{L}\p{N}]+/u, ''); if (!txt) continue;
        const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, { acceptNode: n => n.textContent.trim() ? 1 : 3 }); const first = w.nextNode();
        if (first && first.parentElement.closest('code,kbd,samp')) continue;       // mở đầu bằng định danh trong <code> — không phải câu
        const tok = txt.split(/\s+/)[0], ch = txt[0];
        if (ch === ch.toUpperCase() || ch !== ch.toLowerCase() || IDENT.test(tok) || BRANDS.has(tok.toLowerCase().replace(/[^\p{L}]/gu, ''))) continue;
        if (out.sent_case.length < 40) out.sent_case.push(`${name(el)} "${txt.slice(0, 28)}"`); } }
    // heading-scale: cấp tiêu đề có mặt phải to → nhỏ (h1 > h2 > h3 > h4, lấy cỡ LỚN NHẤT mỗi cấp, chênh ≥ 1px) và tiêu đề ≥ cỡ chữ nội dung
    if (!ex.has('heading-scale')) {
      const lv = [1, 2, 3, 4, 5, 6].map(n => [...document.querySelectorAll('h' + n)].filter(e => vis(e) && !e.closest('nav,svg,[aria-hidden="true"]')).map(fsOf)).map(a => a.length ? Math.max(...a) : null);
      const pres = lv.map((v, i) => [i + 1, v]).filter(x => x[1] != null);
      for (let k = 1; k < pres.length; k++) if (pres[k][1] >= pres[k - 1][1] - 0.5 && out.head_scale.length < 10) out.head_scale.push(`h${pres[k][0]} ${pres[k][1]}px ≥ h${pres[k - 1][0]} ${pres[k - 1][1]}px`);
      // cỡ chữ NỘI DUNG = cỡ chiếm nhiều ký tự nhất trong p/li (bỏ câu lead/hero/deck — lead to hơn tiêu đề thẻ là thiết kế bình thường)
      const tally = {}; for (const e of document.querySelectorAll('p,li')) { if (!vis(e) || e.closest('nav,header,.hero,.lead,.deck,.intro,svg') || /lead|deck|intro/.test(e.className)) continue;
        const k = fsOf(e); tally[k] = (tally[k] || 0) + (e.innerText || '').length; }
      const bs = Object.keys(tally).length ? +Object.entries(tally).sort((a, b) => b[1] - a[1])[0][0] : null;
      if (bs && pres.length) { const [n, v] = pres[pres.length - 1]; if (v < bs && out.head_scale.length < 10) out.head_scale.push(`h${n} ${v}px nhỏ hơn chữ nội dung ${bs}px`); } }
    // title-scale: tên trang (.brand/.logo trong nav, hoặc h1) ≥ 1,2 × chữ lớn nhất của mục nav / tab chọn nội dung
    if (!ex.has('title-scale')) {
      const items = [...document.querySelectorAll('nav a,[role=tab],.tabs button,.tabs a')].filter(e => vis(e) && !/brand|logo/.test(e.className)).map(fsOf);
      const mx = items.length ? Math.max(...items) : 0;
      for (const t of [...document.querySelectorAll('nav .brand, nav .logo, h1')].filter(vis).slice(0, 3)) { const f = fsOf(t);
        if (mx && f < 1.2 * mx && out.title_scale.length < 5) out.title_scale.push(`${name(t)} "${(t.innerText || '').trim().slice(0, 24)}" ${f}px < 1,2 × mục nav/tab ${mx}px`); } }
    // eye-rest: màn đầu (vùng nội dung, bỏ sidebar) — "mực" (chữ + khối có nền/viền) ≤ 55% và không dải dày liền > 520px thiếu khoảng trống ≥ 24px.
    // Ngưỡng HEURISTIC của framework (không có chuẩn công khai): hiệu chỉnh 22/09/2026 — theme đọc Vietcetera 30%/212px qua; control-room 90%/760px trượt.
    if (!ex.has('eye-rest')) {
      const H = innerHeight, W = innerWidth, navE = document.querySelector('nav'), nr = navE && navE.getBoundingClientRect();
      const x0 = nr && nr.height > H * .6 && nr.width < W * .4 ? nr.right : 0, gw = Math.ceil((W - x0) / 8), gh = Math.ceil(H / 8);
      const grid = new Uint8Array(gw * gh), rows = new Uint8Array(Math.ceil(H / 4));
      const paint = r => { const a = Math.max(0, Math.floor((r.left - x0) / 8)), c = Math.min(gw - 1, Math.floor((r.right - x0) / 8)), t = Math.max(0, Math.floor(r.top / 8)), d = Math.min(gh - 1, Math.floor(r.bottom / 8));
        for (let y = t; y <= d; y++) for (let x = a; x <= c; x++) grid[y * gw + x] = 1; for (let y = Math.max(0, Math.floor(r.top / 4)); y <= Math.min(rows.length - 1, Math.floor(r.bottom / 4)); y++) rows[y] = 1; };
      for (const el of document.querySelectorAll('body *')) { if ((navE && navE.contains(el)) || el.closest('.ovs-theme')) continue; const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || +cs.opacity < .1 || cs.display === 'none') continue;
        for (const n of el.childNodes) if (n.nodeType === 3 && n.textContent.trim()) { const rg = document.createRange(); rg.selectNodeContents(n); for (const q of rg.getClientRects()) if (q.bottom > 0 && q.top < H && q.right > x0) paint(q); }
        const r = el.getBoundingClientRect(); if (r.bottom <= 0 || r.top >= H || r.right <= x0) continue;
        const bg = cs.backgroundColor; if ((bg && !/rgba?\(0, 0, 0, 0\)|transparent/.test(bg) && r.width < W * .9) || (parseFloat(cs.borderTopWidth) > 0 && cs.borderTopStyle !== 'none' && r.width > 40 && r.height > 20)) paint(r); }
      const ink = grid.reduce((a, v) => a + v, 0) / grid.length; let run = 0, best = 0, gap = 0;
      for (const v of rows) { if (v) { if (gap * 4 >= 24) run = 0; run += 1 + (gap * 4 < 24 ? gap : 0); gap = 0; best = Math.max(best, run); } else gap++; }
      if (ink > 0.55) out.eye_rest.push(`màn đầu ${Math.round(ink * 100)}% là chữ/khối (trần 55%)`);
      if (best * 4 > 520) out.eye_rest.push(`dải dày liền ${best * 4}px không có khoảng trống ≥ 24px (trần 520px)`); }
    // line-over-text (user 22/09, ảnh sidebar showcase: vạch tiến độ absolute trong sidebar cuộn cắt ngang mục "Chấm trạng thái"):
    // phần tử CÓ ĐỊNH VỊ (absolute/fixed/sticky), mảnh (cạnh ngắn ≤ 6px, cạnh dài ≥ 24px), có màu (nền/viền của nó hoặc con),
    // giao với hộp chữ KHÔNG thuộc nó > 2px ngang và > 1px dọc → vạch đè chữ. Khối dính đáy có nền đặc che chữ khi cuộn là bình thường (không mảnh).
    out.line_text = [];
    if (!ex.has('line-over-text')) {
      const painted = e => [e, ...e.querySelectorAll('*')].some(x => { const c = getComputedStyle(x), q = x.getBoundingClientRect();
        return q.width > 0 && q.height > 0 && ((c.backgroundColor && !/rgba?\(0, 0, 0, 0\)|transparent/.test(c.backgroundColor)) || (parseFloat(c.borderTopWidth) > 0 && c.borderTopStyle !== 'none')); });
      const lines = [...document.querySelectorAll('body *')].filter(e => { const c = getComputedStyle(e); if (!/absolute|fixed|sticky/.test(c.position) || c.visibility === 'hidden' || +c.opacity < .1) return false;
        const r = e.getBoundingClientRect(); return Math.min(r.width, r.height) <= 6 && Math.max(r.width, r.height) >= 24 && r.bottom > 0 && r.top < innerHeight && painted(e); });
      if (lines.length) { const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, { acceptNode: n => n.textContent.trim() ? 1 : 3 });
        for (let n; (n = w.nextNode()) && out.line_text.length < 10;) { const pe = n.parentElement; if (!pe || !vis(pe)) continue;
          const rg = document.createRange(); rg.selectNodeContents(n);
          for (const q of rg.getClientRects()) for (const l of lines) { if (l.contains(pe)) continue; const r = l.getBoundingClientRect();
            const ox = Math.min(r.right, q.right) - Math.max(r.left, q.left), oy = Math.min(r.bottom, q.bottom) - Math.max(r.top, q.top);
            if (ox > 2 && oy > 1 && !out.line_text.some(x => x.startsWith(name(l)))) out.line_text.push(`${name(l)} ${Math.round(r.width)}×${Math.round(r.height)} cắt chữ "${n.textContent.trim().slice(0, 24)}"`); } } } }
    // fixed-trapped (user 24/09, thanh tiến độ nằm trong sidebar thay vì đầu trang): position:fixed khai left:0 + right:0 (ý là phủ ngang
    // cả cửa sổ) mà rộng thật < cửa sổ − 2px → bị tổ tiên có transform / filter / backdrop-filter / contain / will-change biến thành khung chứa.
    out.trapped = [];
    if (!ex.has('fixed-trapped')) for (const el of document.querySelectorAll('body *')) { const cs = getComputedStyle(el);
      if (cs.position !== 'fixed' || cs.left !== '0px' || cs.right !== '0px' || cs.display === 'none') continue;
      const w = el.getBoundingClientRect().width; if (w >= document.documentElement.clientWidth - 2) continue;
      let a = el.parentElement, why = ''; for (; a && a !== document.documentElement; a = a.parentElement) { const c = getComputedStyle(a);
        const k = ['transform', 'filter', 'backdropFilter', 'perspective'].find(x => c[x] && c[x] !== 'none') || (/paint|layout|strict|content/.test(c.contain) && 'contain') || (/transform|filter/.test(c.willChange) && 'will-change');
        if (k) { why = `${name(a)} có ${k}`; break; } }
      if (out.trapped.length < 5) out.trapped.push(`${name(el)} rộng ${Math.round(w)}px / cửa sổ ${document.documentElement.clientWidth}px${why ? ' — bị nhốt vì ' + why : ''}`); }
    // field-ring (user 24/09, ô "Mã ghép": viền 1px + vòng focus 2px lệch 2px = hai vòng khoanh): ô nhập chữ KHÔNG viền lúc nghỉ, KHÔNG
    // outline/box-shadow khi focus; phản hồi bằng NỀN — focus phải đổi nền (ΔL ≥ 0.01) so với lúc nghỉ, không thì người dùng không thấy ô đang nhận chữ.
    out.field = [];
    if (!ex.has('field-ring')) { const act = document.activeElement;
      for (const el of document.querySelectorAll('input:not([type]),input[type=text],input[type=search],input[type=email],input[type=url],input[type=tel],input[type=password],input[type=number],textarea')) {
        if (!vis(el) || el.disabled || out.field.length >= 6) continue; const tr0 = el.style.transition; el.style.transition = 'none'; const c0 = getComputedStyle(el), r0 = bgL(el);   // tắt transition khi đo: không thì focus() đọc ra màu ĐANG chuyển (= màu nghỉ)
        const bd = ['Top', 'Right', 'Bottom', 'Left'].filter(k => parseFloat(c0['border' + k + 'Width']) >= 1 && c0['border' + k + 'Style'] !== 'none' && (lum(c0['border' + k + 'Color']) || { a: 0 }).a > .1);
        if (bd.length) out.field.push(`${name(el)} có viền ${bd.length === 4 ? 'bốn cạnh' : bd.join('/')} lúc nghỉ`);
        el.focus({ preventScroll: true }); const c1 = getComputedStyle(el);
        if (c1.outlineStyle !== 'none' && parseFloat(c1.outlineWidth) > 0) out.field.push(`${name(el)} focus vẽ outline ${c1.outlineWidth}`);
        else if (c1.boxShadow && c1.boxShadow !== 'none') out.field.push(`${name(el)} focus vẽ box-shadow (vòng)`);
        if (Math.abs(bgL(el) - r0) < 0.01) out.field.push(`${name(el)} focus không đổi nền — người dùng không thấy ô đang nhận chữ`);
        el.blur(); el.style.transition = tr0; }
      if (act && act.focus) act.focus({ preventScroll: true }); }
    // action-left (user 24/09 "nút phải ưu tiên align bên phải"): hàng nút KẾT THÚC một form / dialog / thẻ (con cuối, chỉ chứa button|a.btn)
    // phải chạm mép PHẢI vùng nội dung của khung (±4px). Thứ tự góc ưu tiên cho cụm nút: phải-dưới → trái-trên → phải-trên → trái-dưới;
    // luật này đo trường hợp phổ biến nhất (nút hành động cuối khung). Tha nút rộng ≥ 90% khung (nút full-width trên mobile).
    out.action_left = [];
    if (!ex.has('action-left')) for (const box of document.querySelectorAll('form,dialog,[role=dialog],.card,[class*=modal]')) { if (!vis(box) || out.action_left.length >= 6) continue;
      const kids = [...box.children].filter(k => vis(k) && !/^(P|SMALL|OUTPUT)$/.test(k.tagName) && !/status|err|hint|note|muted/.test(typeof k.className === 'string' ? k.className : ''));
      const last = kids[kids.length - 1]; if (!last) continue;
      const btns = last.matches('button,a.btn,[role=button]') ? [last] : [...last.children].filter(vis);
      if (!btns.length || !btns.every(b => b.matches('button,a.btn,[role=button],input[type=submit]'))) continue;
      const bc = getComputedStyle(box), br = box.getBoundingClientRect(), cr = br.right - parseFloat(bc.borderRightWidth) - parseFloat(bc.paddingRight), cl = br.left + parseFloat(bc.borderLeftWidth) + parseFloat(bc.paddingLeft);
      const right = Math.max(...btns.map(b => b.getBoundingClientRect().right)), left = Math.min(...btns.map(b => b.getBoundingClientRect().left));
      if (right - left >= 0.9 * (cr - cl)) continue;
      if (Math.abs(right - cr) > 4) out.action_left.push(`${name(box)} › "${btns.map(b => (b.innerText || '').trim().slice(0, 18)).join(' · ')}" kết thúc ở x=${Math.round(right)}, mép phải nội dung x=${Math.round(cr)}`); }
    // band-misaligned (user 24/09, ảnh hàng "Giao diện" sidebar intake-guide: dải nền trắng x=4→227 trong nav 0→232, mục nav 12→220):
    // DẢI (rộng ≥ 70% cha) có nền đặc hoặc viền trên/dưới RIÊNG, mà mép trái HOẶC phải không khớp (±2px) mép cha, mép nội dung cha,
    // hay mép bất kỳ anh em nào → tấm vá lơ lửng: không tràn hẳn, không thẳng cột.
    out.band = [];
    if (!ex.has('band-misaligned')) {
      const pc0 = e => { const d = getComputedStyle(e); return /flex/.test(d.display) ? (/column/.test(d.flexDirection) ? 'block' : 'flex') : d.display; };   // flex dọc = xếp khối như block
      const own = c => (c.backgroundColor && (lum(c.backgroundColor) || { a: 0 }).a > .3) || ['Top', 'Bottom'].some(s => parseFloat(c['border' + s + 'Width']) > 0 && c['border' + s + 'Style'] !== 'none');
      for (const el of document.querySelectorAll('body *')) { const pe = el.parentElement; if (!pe || pe === document.body || !vis(el) || out.band.length >= 10) continue;
        const cs = getComputedStyle(el); if (!own(cs) || parseFloat(cs.borderRadius) > 0.5 || /^table|flex|grid/.test(pc0(pe)) || /^table/.test(cs.display)) continue;   // ô bảng / con flex-grid ngang xếp nối nhau, không phải dải
        const r = el.getBoundingClientRect(), pr = pe.getBoundingClientRect(), pc = getComputedStyle(pe);
        const cl = pr.left + parseFloat(pc.borderLeftWidth) + parseFloat(pc.paddingLeft), crt = pr.right - parseFloat(pc.borderRightWidth) - parseFloat(pc.paddingRight);
        if (r.width < 0.7 * (crt - cl) || r.width < 80) continue;
        const sib = [...pe.children].filter(s => s !== el && vis(s)).map(s => s.getBoundingClientRect());
        const ok = (x, refs) => refs.some(v => Math.abs(x - v) <= 2);
        const L = ok(r.left, [pr.left, cl, pr.left + parseFloat(pc.borderLeftWidth), ...sib.map(s => s.left)]), R = ok(r.right, [pr.right, crt, pr.right - parseFloat(pc.borderRightWidth), ...sib.map(s => s.right)]);
        if (!L || !R) out.band.push(`${name(el)} x=${Math.round(r.left)}→${Math.round(r.right)} trong ${name(pe)} ${Math.round(pr.left)}→${Math.round(pr.right)} (nội dung ${Math.round(cl)}→${Math.round(crt)})`); } }
    // kanban-uniform (user 22/09: "làm kanban thì luôn chung 1 style và thẻ phải luôn size cố định"): bảng = ≥ 2 cột anh em
    // (class chứa lane|kanban|swimlane hoặc [data-kanban-lane]); thẻ = con trực tiếp của cột mang class lặp nhiều nhất (bỏ tiêu đề/gợi ý).
    // MỌI thẻ trên bảng phải cùng rộng + cùng cao (±2px) và cùng style (nền · viền · bo · padding · cỡ/họ chữ).
    out.kanban = [];
    if (!ex.has('kanban-uniform')) {
      const sig = el => { const s = getComputedStyle(el); return [s.backgroundColor, s.borderTopWidth, s.borderTopColor, s.borderRadius, s.paddingTop, s.paddingLeft, s.fontSize, s.fontFamily].join(' | '); };
      const boards = new Set(); for (const l of document.querySelectorAll('[class*=lane],[class*=kanban] > *,[data-kanban-lane]')) if (vis(l) && l.parentElement) boards.add(l.parentElement);
      for (const bd of boards) { const lanes = [...bd.children].filter(c => vis(c) && (c.hasAttribute('data-kanban-lane') || /lane|kanban|col/i.test(c.className || ''))); if (lanes.length < 2) continue;
        const tally = {}; for (const ln of lanes) for (const c of ln.children) if (vis(c) && !/^H[1-6]$/.test(c.tagName) && typeof c.className === 'string' && c.className.trim()) { const k = c.className.trim().split(/\s+/)[0]; tally[k] = (tally[k] || 0) + 1; }
        const top = Object.entries(tally).sort((a, b) => b[1] - a[1])[0]; if (!top || top[1] < 2) continue;
        const cards = lanes.flatMap(ln => [...ln.children].filter(c => vis(c) && typeof c.className === 'string' && c.className.trim().split(/\s+/)[0] === top[0]));
        const rs = cards.map(c => c.getBoundingClientRect()), ws = rs.map(r => r.width), hs = rs.map(r => r.height), tag = `${name(bd)} .${top[0]} ×${cards.length}`;
        if (Math.max(...ws) - Math.min(...ws) > 2) out.kanban.push(`${tag}: rộng lệch ${Math.round(Math.min(...ws))}–${Math.round(Math.max(...ws))}px`);
        if (Math.max(...hs) - Math.min(...hs) > 2) out.kanban.push(`${tag}: cao lệch ${Math.round(Math.min(...hs))}–${Math.round(Math.max(...hs))}px (đặt height cố định + cắt chữ bằng line-clamp)`);
        const sg = new Set(cards.map(sig)); if (sg.size > 1) out.kanban.push(`${tag}: ${sg.size} style khác nhau — vd ${[...sg].slice(0, 2).join(' ≠ ')}`); } }
  }
  out.glass = [...document.querySelectorAll('body *')].filter(e => { const cs = getComputedStyle(e); return vis(e) && ((cs.backdropFilter && cs.backdropFilter !== 'none') || (cs.webkitBackdropFilter && cs.webkitBackdropFilter !== 'none')); }).length;
  out.bodyL = (() => { const l = lum(getComputedStyle(document.body).backgroundColor), h = lum(getComputedStyle(document.documentElement).backgroundColor); return (l && l.a > .5) ? l.L : (h && h.a > .5 ? h.L : null); })();
  return out;
};

// horizontal-scroll + clickable-wrap: đo lại ở từng bề rộng (resize cùng trang, không tải lại)
const LAYOUT = () => { const d = document.documentElement, wrap = [];
  for (const el of document.querySelectorAll('button,[role=button],[role=tab],nav a,footer a,a.btn')) { if (el.closest('p,[aria-hidden="true"]')) continue;
    if (el.querySelector(':scope > div, :scope > p')) continue;   // THẺ bấm được (kanban, node) nhiều dòng là thiết kế — luật này cho NHÃN nút/link
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el); if (r.width < 2 || r.height < 2 || cs.visibility === 'hidden' || el.textContent.trim().length < 2) continue;
    const rg = document.createRange(); rg.selectNodeContents(el); const rs = [...rg.getClientRects()].filter(x => x.width > 1 && x.height > 1).sort((a, b) => a.top - b.top);
    // số dòng = số cụm rect KHÔNG chồng nhau theo chiều dọc (icon căn giữa cùng dòng với chữ không bị đếm thành dòng mới)
    let lines = 0, bot = -Infinity; for (const x of rs) { if (x.top >= bot - 1) { lines++; bot = x.bottom; } else bot = Math.max(bot, x.bottom); }
    if (lines >= 2 && wrap.length < 40) wrap.push((el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/)[0] : '')) + ' "' + el.textContent.trim().slice(0, 24) + '"'); }
  // row-wrap (user 24/09 "tràn thì không xuống dòng, chỉ mờ đi"): hàng flex ngang ≥ 2 mục NHỎ (mỗi mục ≤ 64px cao — không phải lưới thẻ)
  // mà các mục rơi xuống ≥ 2 dòng → FAIL. Sửa: class ovs-line của lớp nền (một dòng, mờ mép khi tràn, hover thấy đủ).
  const rows = [];
  for (const el of document.querySelectorAll('body *')) { const cs = getComputedStyle(el); if (/^H[1-6]$/.test(el.tagName) || !/flex/.test(cs.display) || !/^row/.test(cs.flexDirection) || cs.flexWrap === 'nowrap') continue;
    const kids = [...el.children].filter(k => { const c = getComputedStyle(k), r = k.getBoundingClientRect(); return r.width > 1 && r.height > 1 && c.position !== 'absolute' && c.position !== 'fixed' && c.display !== 'none'; });
    if (kids.length < 2) continue; const rs = kids.map(k => k.getBoundingClientRect()); if (Math.max(...rs.map(r => r.height)) > 64) continue;
    if (kids.some(k => getComputedStyle(k).flexBasis === '100%')) continue;   // mục chủ ý chiếm trọn dòng (vd hộp kết quả bên dưới) — không phải tràn
    const tops = []; for (const r of rs) if (!tops.some(t => Math.abs(t - r.top) < Math.min(...rs.map(x => x.height)) / 2)) tops.push(r.top);
    if (tops.length >= 2 && rows.length < 20) rows.push((el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/)[0] : '')) + ` (${kids.length} mục, ${tops.length} dòng)`); }
  return { over: d.scrollWidth - d.clientWidth, wrap, rows }; };
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
    const m = await p.evaluate(MEASURE, theme); m.jsErrors = errs;
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
    if (theme === 'light' && (on('horizontal-scroll') || on('clickable-wrap') || on('row-wrap'))) { row.hscroll = []; row.wrap = []; row.rowwrap = [];
      for (const w of WIDTHS) { await p.setViewportSize({ width: w, height: 900 }); await p.waitForTimeout(150); const l = await p.evaluate(LAYOUT);
        if (l.over > 1) row.hscroll.push({ w, over: l.over }); if (WRAP_AT.includes(w)) for (const x of l.wrap) row.wrap.push(`${x} @${w}`); if (w === 375 || w === 1360) for (const x of l.rows) row.rowwrap.push(`${x} @${w}`); }
      await p.setViewportSize({ width: 1360, height: 900 }); await p.waitForTimeout(150); }
    if (theme === 'light') { // toggle: bấm → nền đổi chiều; tải lại → giữ
      // phần tử NHÌN THẤY đầu tiên khớp selector (selector rộng còn khớp cả <script id="…theme…"> / <meta name="theme-color"> trong <head>)
      let tg = null; for (const h of await p.$$(TOGGLE_SEL)) { if (await h.evaluate(e => { const r = e.getBoundingClientRect(); return r.width > 4 && r.height > 4 && !/^(script|style|meta|link|template)$/i.test(e.tagName); })) { tg = h; break; } }
      const follows = await p.$('[data-ovs-theme-follow]');
      if (follows) row.toggle = 'follows-parent'; else if (!tg) row.toggle = 'MISSING';
      else { const lumNow = () => p.evaluate(() => { const f = c => { const m = c.match(/[\d.]+/g); if (!m) return null; const a = m[3] === undefined ? 1 : +m[3]; return a < .5 ? null : (0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2]) / 255; }; return f(getComputedStyle(document.body).backgroundColor) ?? f(getComputedStyle(document.documentElement).backgroundColor) ?? (document.documentElement.getAttribute('data-theme') === 'dark' ? 0 : 1); });
        const before = await lumNow();
        // toggle-jump (user 24/09 "ấn vào nó vẫn bị nhảy lên"): đo hộp nút GIỮA lúc bấm — ripple đổi static→relative làm bottom/right sót lại
        // có hiệu lực ~0,5s rồi trả về, nên đo sau click không bao giờ thấy. Nhấn = mouse down/up thật (thay tg.click).
        const b0 = await tg.boundingBox(); if (b0) { await p.mouse.move(b0.x + b0.width / 2, b0.y + b0.height / 2); await p.mouse.down(); await p.waitForTimeout(80);
          const b1 = await tg.boundingBox(); await p.mouse.up(); if (b1 && (Math.abs(b1.x - b0.x) > 1 || Math.abs(b1.y - b0.y) > 1)) row.toggleJump = `${Math.round(b1.x - b0.x)},${Math.round(b1.y - b0.y)}px`; }
        else await tg.click({ force: true }).catch(() => {});
        await p.waitForTimeout(700); const after = await lumNow();
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
  // PLAN 220926 t4: line-height-body + hierarchy-flat FAIL (chuẩn đo được, lỗi thật); measure-too-wide (đếm ký tự thật),
  // heading-proximity (bố cục lưới dễ báo giả), tap-target (chưa tính ngoại lệ khoảng cách của WCAG 2.5.8) → WARN.
  if (on('line-height-body') && L.line_body.length) probs.push(`line-height-body: ${L.line_body.length} khối chữ nhiều dòng giãn < 1.5 — vd ${L.line_body[0]}`);
  if (on('hierarchy-flat') && L.hier_flat.length) probs.push(`hierarchy-flat: ${L.hier_flat.length} nhãn nav không NỔI hơn mục (< 2/4 khác biệt, chìm hơn, hoặc không đậm/to hơn) — vd ${L.hier_flat[0]}`);
  if (on('measure-too-wide') && L.measure.length) warns.push(`measure-too-wide: ${L.measure.length} đoạn quá dài dòng (đếm ký tự thật, chuẩn ≤ 80 ký tự — dùng max-width:var(--measure)) — vd ${L.measure[0]}`);
  if (on('sentence-case') && L.sent_case && L.sent_case.length) probs.push(`sentence-case: ${L.sent_case.length} nhãn/tiêu đề bắt đầu bằng chữ thường — viết hoa chữ đầu (trừ định danh/tên riêng) — vd ${L.sent_case[0]}`);
  if (on('heading-scale') && L.head_scale && L.head_scale.length) probs.push(`heading-scale: cấp tiêu đề không to → nhỏ — ${L.head_scale.join(' · ')}`);
  if (on('title-scale') && L.title_scale && L.title_scale.length) probs.push(`title-scale: tên trang không lớn hơn mục nav/tab — ${L.title_scale[0]}`);
  if (on('line-over-text') && L.line_text && L.line_text.length) probs.push(`line-over-text: vạch mảnh có định vị đè lên chữ — ${L.line_text.slice(0, 3).join(' · ')}`);
  // row-wrap FAIL: lớp nền (html_base LINE_JS) tự gắn ovs-line cho hàng rơi dòng → trang mang lớp nền sạch; còn bắt được = trang KHÔNG mang lớp nền.
  if (on('row-wrap') && row.rowwrap && row.rowwrap.length) probs.push(`row-wrap: hàng chip/chỉ số/nút rơi xuống nhiều dòng — dùng class ovs-line (một dòng, mờ mép khi tràn, hover thấy đủ) — ${row.rowwrap.slice(0, 3).join(' · ')}`);
  if (on('action-left') && L.action_left && L.action_left.length) probs.push(`action-left: hàng nút cuối khung không nằm bên phải (ưu tiên góc phải-dưới) — ${L.action_left.slice(0, 3).join(' · ')}`);
  if (on('field-ring') && L.field && L.field.length) probs.push(`field-ring: ô nhập khoanh viền/vòng — dùng nền trong suốt, hover/focus đậm dần — ${L.field.slice(0, 3).join(' · ')}`);
  if (on('fixed-trapped') && L.trapped && L.trapped.length) probs.push(`fixed-trapped: phần tử fixed phủ ngang bị nhốt trong khung cha — đặt nó làm con trực tiếp của <body> — ${L.trapped.join(' · ')}`);
  if (on('band-misaligned') && L.band && L.band.length) probs.push(`band-misaligned: dải có nền/viền riêng lệch mép — không tràn hẳn cha, không thẳng cột anh em — ${L.band.slice(0, 3).join(' · ')}`);
  if (on('kanban-uniform') && L.kanban && L.kanban.length) probs.push(`kanban-uniform: thẻ kanban không đồng nhất — ${L.kanban.slice(0, 3).join(' · ')}`);
  if (on('eye-rest') && L.eye_rest && L.eye_rest.length) warns.push(`eye-rest: không có khoảng nghỉ cho mắt — ${L.eye_rest.join(' · ')}`);
  if (on('heading-proximity') && L.heading_prox.length) warns.push(`heading-proximity: ${L.heading_prox.length} tiêu đề gần đoạn TRÊN hơn đoạn dưới — vd ${L.heading_prox[0]}`);
  if (on('tap-target') && L.tap.length) warns.push(`tap-target: ${L.tap.length} vùng bấm < 24×24 — vd ${L.tap[0]}`);
  if (on('toggle') && row.toggle !== 'ok' && row.toggle !== 'follows-parent') probs.push(`toggle: ${row.toggle}`);
  if (on('toggle') && row.toggleJump) probs.push(`toggle: nút đổi giao diện NHẢY chỗ khi đang bấm (dx,dy = ${row.toggleJump}) — thường do ripple static→relative gặp top/bottom/right sót lại`);
  if (on('toggle') && row.toggle === 'ok' && L.bodyL !== null && D.bodyL !== null && Math.abs(L.bodyL - D.bodyL) < 0.25) probs.push('toggle: sáng và tối cho CÙNG một nền');
  if (on('glass') && L.glass > 0 && D.glass === 0) probs.push(`glass: sáng có ${L.glass} lớp kính, tối mất hết`);
  if (on('glass') && D.glass > 0 && L.glass === 0) probs.push(`glass: tối có ${D.glass} lớp kính, sáng mất hết`);
  const je = [...L.jsErrors, ...D.jsErrors]; if (je.length) probs.push(`js: ${je[0]}`);
  row.problems = probs; row.warnings = warns; if (probs.length) bad++; report.push(row); }
await b.close();
if (asJson) console.log(JSON.stringify(report.map(r => ({ page: r.page, toggle: r.toggle, problems: r.problems, warnings: r.warnings, light: r.findings.light && { contrast: r.findings.light.contrast, tight: r.findings.light.tight, overlap: r.findings.light.overlap, stripe: r.findings.light.stripe, rounded_edge: r.findings.light.rounded_edge, italic_display: r.findings.light.italic_display, upper_tight: r.findings.light.upper_tight, line_body: r.findings.light.line_body, measure: r.findings.light.measure, heading_prox: r.findings.light.heading_prox, hier_flat: r.findings.light.hier_flat, tap: r.findings.light.tap, sent_case: r.findings.light.sent_case, head_scale: r.findings.light.head_scale, title_scale: r.findings.light.title_scale, eye_rest: r.findings.light.eye_rest, glass: r.findings.light.glass }, hscroll: r.hscroll, wrap: r.wrap, dark: r.findings.dark && { contrast: r.findings.dark.contrast, rounded_edge: r.findings.dark.rounded_edge, overlap: r.findings.dark.overlap, glass: r.findings.dark.glass } })), null, 1));
else { for (const r of report) { console.log(`${r.problems && r.problems.length ? '✗' : '✓'} ${r.page}${r.error ? ' — ' + r.error : ''}`); for (const q of r.problems || []) console.log('    ' + q); for (const q of r.warnings || []) console.log('    ⚠ ' + q); }
  console.log(`html-visual-gate: ${report.length - bad}/${report.length} trang đạt`); }
process.exit(bad ? 2 : 0);
