#!/usr/bin/env node
// button-harmony — cổng chạy-thật (Playwright) đo độ HÀI HÒA của nút và hàng hành động, bổ sung cho html-visual-gate.
//
// Vì sao có (user 24/09/2026, ảnh cockpit intake): luật action-left dồn nút về góc phải — đúng — nhưng không ai đo xem
// nút có còn ĐI CÙNG thứ nó phục vụ không: "+ Giao việc mới" đứng lẻ một dòng dưới tiêu đề, "Chọn thư mục…" trôi tận
// mép phải cách ô Repo cả màn hình, thanh trên hụt 600px vì một ô rỗng chiếm chỗ. Cổng tĩnh và visual-gate đều xanh.
// "Ưu tiên phải nhưng vẫn phải hài hòa" → đo bằng hình học thật ở màn rộng VÀ màn hẹp.
//
// Luật (mỗi luật một con số, không cảm tính):
//   lone-action      FAIL  hàng chỉ có MỘT nút, KHÔNG phải hàng kết thúc khối (còn nội dung phía sau trong cùng khối),
//                          mà nút trôi xa: khoảng trống bên trái nút > 50% bề rộng hàng. Nút phụ phải đứng CÙNG DÒNG với
//                          tiêu đề/ô nó phục vụ (hàng tiêu đề space-between, hoặc ô + nút một hàng). Hàng kết thúc khối
//                          (nút gửi ở góc phải dưới) được tha — đó là action-left.
//   edge-gap         FAIL  hàng flex ngang canh mép (justify flex-end/space-between hoặc có con margin-left:auto) mà con
//                          cuối KHÔNG chạm mép phải nội dung (hụt > 8px): có thứ vô hình chiếm chỗ hoặc bị kẹp bề rộng.
//   empty-occupant   FAIL  con của hàng flex ngang không có chữ, không có con hiển thị, không nền/viền, mà rộng > 48px —
//                          ô rỗng vô hình đẩy lệch bố cục (vd ô thông báo chưa có nội dung).
//   mixed-edge       WARN  trong một khối (form/section/article/dialog/.card), các hàng kết thúc có nút căn KHÁC mép nhau.
//
// Usage: NODE_PATH=$(npm root -g) node button-harmony.mjs <trang.html|http://…> … [--widths 1440,390] [--json]
// Trang cần đăng nhập/tương tác: chụp DOM đã render ra file rồi chạy trên file (script ứng dụng gỡ ra để không gọi API).
// Exit: 0 sạch · 1 có FAIL · 2 thiếu playwright (BỎ QUA, không phải đạt).
import { createRequire } from 'node:module';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
const json = args.includes('--json');
const wi = args.indexOf('--widths');
const WIDTHS = wi >= 0 ? args[wi + 1].split(',').map(Number) : [1440, 390];
const pages = args.filter((a, i) => !a.startsWith('--') && args[i - 1] !== '--widths');
if (!pages.length) { console.error('usage: button-harmony.mjs <page.html|url> … [--widths 1440,390] [--json]'); process.exit(2); }

// Playwright: ESM không đọc NODE_PATH → createRequire, cùng thứ tự tìm với html-visual-gate (scratchpad → cạnh file → cwd → NODE_PATH).
let chromium;
{ const tryReq = base => { try { return createRequire(base)('playwright'); } catch { return null; } };
  const np = (process.env.NODE_PATH || '').split(':').filter(Boolean).map(d => tryReq(d + '/_.js'));
  const mod = tryReq(new URL('../../scratchpad/_.js', import.meta.url)) || tryReq(import.meta.url) || tryReq(process.cwd() + '/scratchpad/_.js') || tryReq(process.cwd() + '/_.js') || np.find(Boolean);
  if (!mod) { console.error('button-harmony: BỎ QUA — thiếu playwright (npm i -g playwright && npx playwright install chromium)'); process.exit(2); }
  chromium = mod.chromium; }

const MEASURE = () => {
  const out = [];
  const vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const name = e => (e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).join('.') : '')).slice(0, 60);
  const label = e => (e.innerText || e.value || e.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 40);
  const isBtn = e => e.matches('button,[role=button],a.btn,input[type=submit],input[type=button]');
  const row = e => { const s = getComputedStyle(e); return (s.display === 'flex' || s.display === 'inline-flex') && !s.flexDirection.startsWith('column'); };
  const content = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    return [r.left + parseFloat(s.borderLeftWidth) + parseFloat(s.paddingLeft), r.right - parseFloat(s.borderRightWidth) - parseFloat(s.paddingRight)]; };
  const later = e => { for (let n = e.nextElementSibling; n; n = n.nextElementSibling) if (vis(n) && (n.innerText || '').trim()) return true; return false; };
  const skip = e => e.closest('[data-harmony-exempt]');
  const painted = ks => (ks.backgroundColor && !/rgba\(0, 0, 0, 0\)|transparent/.test(ks.backgroundColor)) || parseFloat(ks.borderTopWidth) > 0 || ks.backgroundImage !== 'none';
  const hollow = k => !(k.innerText || '').trim() && ![...k.children].some(vis) && !painted(getComputedStyle(k))
    && !k.matches('input,textarea,select,img,svg,canvas,video,iframe,hr,button');   // takes room, shows nothing
  for (const e of document.querySelectorAll('body *')) {
    if (!vis(e) || !row(e) || skip(e)) continue;
    const kids = [...e.children].filter(vis);
    if (!kids.length) continue;
    const [cl, cr] = content(e), w = cr - cl;
    const btns = kids.filter(isBtn);
    // lone-action: one button alone on its row, not closing its block, floating far from the start of the row
    if (btns.length === 1 && kids.length === 1 && w > 200 && later(e)) {
      const gap = btns[0].getBoundingClientRect().left - cl;
      if (gap > 0.5 * w) out.push({ level: 'FAIL', rule: 'lone-action', where: name(e), msg: `nút "${label(btns[0])}" đứng lẻ một dòng, trôi ${Math.round(gap)}px khỏi đầu hàng (${Math.round(100 * gap / w)}% bề rộng) — đặt cùng dòng với tiêu đề/ô nó phục vụ` });
    }
    // edge-gap: an edge-aligned row whose last child stops short of the content edge
    const s = getComputedStyle(e);
    const edge = /flex-end|end|space-between/.test(s.justifyContent) || kids.some(k => getComputedStyle(k).marginLeft === 'auto' || (k.style && k.style.marginLeft === 'auto'))
      || kids.some(k => { const m = getComputedStyle(k).marginLeft; return parseFloat(m) > 40 && kids.indexOf(k) > 0; });
    const rs = kids.map(k => k.getBoundingClientRect());
    const oneLine = Math.max(...rs.map(r => r.top)) < Math.min(...rs.map(r => r.bottom));   // every child shares one vertical band
    if (edge && oneLine && w > 200) {
      const solid = kids.filter(k => !hollow(k));
      const last = Math.max(...solid.map(k => k.getBoundingClientRect().right + parseFloat(getComputedStyle(k).marginRight)));
      if (cr - last > 8) out.push({ level: 'FAIL', rule: 'edge-gap', where: name(e), msg: `hàng canh mép phải nhưng con cuối dừng cách mép ${Math.round(cr - last)}px` });
    }
    // empty-occupant: an invisible empty child taking room in a horizontal row
    for (const k of e.children) {                 // zero-height boxes still take width in a row: do not filter by vis()
      const ks = getComputedStyle(k), kr = k.getBoundingClientRect();
      if (ks.display === 'none' || ks.visibility === 'hidden' || ks.position === 'absolute' || ks.position === 'fixed') continue;
      if (parseFloat(ks.flexGrow) > 0) continue;   // a flex spacer (flex:1) is a deliberate push, not an accidental occupant
      if (kr.width > 48 && hollow(k))
        out.push({ level: 'FAIL', rule: 'empty-occupant', where: name(k), msg: `ô rỗng vô hình rộng ${Math.round(kr.width)}px chiếm chỗ trong hàng ${name(e)} — ẩn khi rỗng (:empty{display:none}) hoặc bỏ` });
    }
  }
  // mixed-edge: closing action rows inside one block align to different edges
  for (const blk of document.querySelectorAll('form,section,article,dialog,.card')) {
    if (!vis(blk) || skip(blk)) continue;
    const [bl, br] = content(blk), edges = new Set();
    for (const r of blk.querySelectorAll('*')) {
      if (!vis(r) || !row(r) || r.closest('form,section,article,dialog,.card') !== blk) continue;
      const bs = [...r.children].filter(k => vis(k) && isBtn(k));
      if (!bs.length || later(r)) continue;
      const L = Math.min(...bs.map(b => b.getBoundingClientRect().left)), R = Math.max(...bs.map(b => b.getBoundingClientRect().right));
      edges.add(Math.abs(br - R) <= 4 ? 'phải' : Math.abs(L - bl) <= 4 ? 'trái' : 'giữa');
    }
    if (edges.size > 1) out.push({ level: 'WARN', rule: 'mixed-edge', where: name(blk), msg: `các hàng nút kết thúc căn khác mép: ${[...edges].join(', ')}` });
  }
  return out;
};

const browser = await chromium.launch();
let fails = 0; const report = [];
for (const p of pages) {
  const url = /^https?:/.test(p) ? p : pathToFileURL(resolve(p)).href;
  const row = { page: p, findings: [] };
  for (const w of WIDTHS) {
    const pg = await browser.newPage({ viewport: { width: w, height: 900 } });
    await pg.goto(url, { waitUntil: 'load' }).catch(() => {});
    await pg.waitForTimeout(200);
    const seen = new Set();
    for (const f of await pg.evaluate(MEASURE)) {
      const k = f.rule + f.where + f.msg; if (seen.has(k)) continue; seen.add(k);
      row.findings.push({ ...f, width: w });
    }
    await pg.close();
  }
  const bad = row.findings.filter(f => f.level === 'FAIL');
  fails += bad.length; report.push(row);
  if (!json) {
    console.log(`${bad.length ? '✗' : '✓'} ${p}`);
    for (const f of row.findings) console.log(`    ${f.level === 'WARN' ? '⚠ ' : ''}${f.rule} @${f.width}: ${f.where} — ${f.msg}`);
  }
}
await browser.close();
if (json) console.log(JSON.stringify(report, null, 1));
else console.log(`button-harmony: ${report.filter(r => !r.findings.some(f => f.level === 'FAIL')).length}/${report.length} trang hài hòa`);
process.exit(fails ? 1 : 0);
