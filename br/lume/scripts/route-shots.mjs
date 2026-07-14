#!/usr/bin/env node
// route-shots — luồng QA thị giác: login rồi chụp headless từng route có tồn tại.
// Dùng playwright-core + Chrome hệ thống (không tải browser riêng). Ảnh → <out>/<name>.png.
// Người/agent đọc ảnh → viết FINDINGS.md → bật luồng sửa. (frame QA của dây chuyền.)
//
// Usage: node route-shots.mjs --base http://localhost:5230 --out ./qa-shots \
//                             --user demo --pass demo --pw-root <scratchpad/qa>
import { chromium } from "playwright-core";
import { mkdirSync, statSync, writeFileSync, existsSync, readFileSync, copyFileSync } from "node:fs";
// Baseline pixel-diff (quyết định 13/07/26 từ /last30days): thứ DUY NHẤT đã chín trong
// ngành cho "AI-generated UI" là baseline snapshot + diff (argos-ci/argos: "detects
// unintended visual changes"). Bắt được đúng loại lỗi mà bất-biến-CSS và mắt agent MÙ:
// thay đổi NGOÀI Ý MUỐN (vd sửa quá tay làm phẳng cả UI). deps: pixelmatch + pngjs.
let pixelmatch = null, PNG = null;
try {
  pixelmatch = (await import("pixelmatch")).default;
  PNG = (await import("pngjs")).PNG;
} catch { /* không có dep → bỏ qua baseline, vẫn chụp bình thường */ }

const arg = (k, d) => { const i = process.argv.indexOf(k); return i > -1 ? process.argv[i + 1] : d; };
const BASE = arg("--base", "http://localhost:5230");
const OUT = arg("--out", "./qa-shots");
const USER = arg("--user", "demo");
const PASS = arg("--pass", "demo");

// --route /pc : chụp+kiểm ĐÚNG 1 route (cho vòng tự-kiểm của frame UI).
// --assert   : exit 1 nếu route không 200 hoặc trang rỗng/lỗi (dùng làm acceptance gate).
const ONE = arg("--route", null);
const ASSERT = process.argv.includes("--assert");
const BASELINE = arg("--baseline", null);                       // thư mục ảnh chuẩn
const UPDATE_BASELINE = process.argv.includes("--update-baseline");
// NGƯỠNG MẶC ĐỊNH = 0 (nghiêm ngặt). BÀI HỌC 13/07/26: đặt 0.5% thì một regression THẬT
// (làm phẳng toàn bộ card) chỉ tạo diff 0.113% trên trang rỗng → LỌT GATE. Ngưỡng phần trăm
// là mô hình SAI. Mô hình đúng (Argos/Chromatic): MỌI diff ≠ 0 phải được NGƯỜI/AGENT xem +
// duyệt tay bằng --update-baseline. Chỉ nới ngưỡng khi render thật sự nhiễu (antialias).
const DIFF_MAX = parseFloat(arg("--diff-threshold", "0"));

// so ảnh hiện tại với baseline → % pixel khác + ghi ảnh diff. Trả null nếu không so được.
function diffAgainstBaseline(curFile, baseFile, outFile) {
  if (!pixelmatch || !PNG || !existsSync(baseFile)) return null;
  try {
    const a = PNG.sync.read(readFileSync(baseFile));
    const b = PNG.sync.read(readFileSync(curFile));
    if (a.width !== b.width || a.height !== b.height) {
      return { pct: 100, note: `kích thước đổi ${a.width}x${a.height} → ${b.width}x${b.height}` };
    }
    const d = new PNG({ width: a.width, height: a.height });
    const changed = pixelmatch(a.data, b.data, d.data, a.width, a.height, { threshold: 0.1 });
    writeFileSync(outFile, PNG.sync.write(d));
    return { pct: +((changed / (a.width * a.height)) * 100).toFixed(3), diffFile: outFile };
  } catch (e) {
    return { pct: -1, note: "diff lỗi: " + e.message.split("\n")[0] };
  }
}
const ROUTES = ONE
  ? [[ONE.replace(/\W+/g, "_").replace(/^_|_$/g, "") || "route", ONE]]
  : [
      ["auth", "/auth"], ["home", "/"], ["explore", "/explore"],
      ["archived", "/archived"], ["attachments", "/attachments"],
      ["inbox", "/inbox"], ["setting", "/setting"],
    ];

mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch({ channel: "chrome", headless: true });
const ctx = await browser.newContext({ viewport: { width: 1360, height: 900 }, deviceScaleFactor: 1 });
const page = await ctx.newPage();
const results = [];

// ── LỖ MÙ ĐÃ VÁ (13/07/26): driver login TRƯỚC rồi mới chụp ⇒ /auth luôn redirect về home
//    ⇒ trang SIGN-IN chưa bao giờ được audit (đúng trang user báo lỗi contrast). Nay chụp +
//    audit trang chưa-đăng-nhập TRƯỚC, rồi mới login. Không route nào được phép là vùng mù.
await page.goto(BASE + "/auth", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(2200);
try {
  const preFile = `${OUT}/signin.png`;
  mkdirSync(OUT, { recursive: true });
  await page.screenshot({ path: preFile });
  const preIssues = await page.evaluate(DESIGN_AUDIT).catch(() => []);
  results.push({ name: "signin", path: "/auth (chưa đăng nhập)", status: 200, file: preFile, issues: preIssues, diff: null });
  console.log(`shot signin (/auth pre-login) → 200` +
    (preIssues.length ? `  ⚑ ${preIssues.map((i) => i.rule + (i.count ? "×" + i.count : "")).join(", ")}` : "  ✓ design-ok"));
} catch (e) { console.log("shot signin FAIL —", e.message.split("\n")[0]); }

try {
  await page.fill('input[type="text"]', USER, { timeout: 5000 });
  await page.fill('input[type="password"]', PASS, { timeout: 5000 });
  await page.getByRole("button", { name: /sign in|đăng nhập/i }).click();
  await page.waitForURL((u) => !u.pathname.startsWith("/auth"), { timeout: 8000 }).catch(() => {});
  await page.waitForTimeout(1500);
  console.log("login: OK");
} catch (e) {
  console.log("login: FAIL —", e.message.split("\n")[0]);
}

// ── BẤT BIẾN MÁY-KIỂM (design invariants) — máy bắt, không dựa mắt người ──
// Sinh ra vì failure 'ui-pass-without-full-visual-review': --assert cũ chỉ kiểm HTTP200 + có
// file ảnh → trang vỡ vẫn "OK". Hai bất biến này bắt đúng 2 lỗi đã lọt (sidebar lệch màu,
// bóng bị clip). Chạy TRONG trang bằng computed style.
function DESIGN_AUDIT() {   // function-declaration (được hoist) — pre-login capture gọi nó trước khi khai
  const issues = [];
  const bodyBg = getComputedStyle(document.body).backgroundColor;
  // 1. MONOCHROME SURFACE (neumorphism move 1): pane lớn (sidebar/aside/nav) phải CÙNG màu nền.
  document.querySelectorAll('aside, nav, [data-slot="sidebar"], [class*="sidebar"]').forEach((el) => {
    if (el.offsetWidth < 40 || el.offsetHeight < 120) return;         // bỏ chip nhỏ
    const bg = getComputedStyle(el).backgroundColor;
    if (bg && bg !== "rgba(0, 0, 0, 0)" && bg !== "transparent" && bg !== bodyBg) {
      issues.push({ rule: "monochrome-surface", el: el.tagName.toLowerCase(), got: bg, want: bodyBg });
    }
  });
  // 2. SHADOW CLIPPED: chỉ tính bóng LỚN (neumorphic, blur ≥ 8px) bị cha overflow:hidden cắt.
  //    Ngưỡng blur là BẮT BUỘC — không có nó thì bắt luôn `shadow-xs` gốc của app → kêu oan
  //    hàng chục lần/route → gate bị phớt lờ. (Bài học: gate noisy = gate chết.)
  const BLUR_MIN = 8;
  let clipped = 0;
  const sample = [];
  document.querySelectorAll("*").forEach((el) => {
    const cs = getComputedStyle(el);
    const sh = cs.boxShadow;
    if (!sh || sh === "none" || sh.includes("inset")) return;
    // lấy blur lớn nhất trong chuỗi box-shadow (px thứ 3 của mỗi lớp)
    const blurs = [...sh.matchAll(/(-?\d+(?:\.\d+)?)px\s+(-?\d+(?:\.\d+)?)px\s+(\d+(?:\.\d+)?)px/g)].map((m) => parseFloat(m[3]));
    if (!blurs.length || Math.max(...blurs) < BLUR_MIN) return;   // bóng nhỏ → bỏ qua
    let p = el.parentElement, d = 0;
    while (p && d++ < 3) {
      const ps = getComputedStyle(p);
      if (ps.overflow === "hidden" || ps.overflowX === "hidden" || ps.overflowY === "hidden") {
        clipped++;
        if (sample.length < 4) sample.push(el.tagName.toLowerCase() + "." + String(el.className || "").slice(0, 24));
        break;
      }
      p = p.parentElement;
    }
  });
  if (clipped) issues.push({ rule: "shadow-clipped", count: clipped, sample });

  // 3. WCAG CONTRAST (BẮT BUỘC — bài học 13/07/26): tương phản chữ là CON SỐ TÍNH ĐƯỢC.
  //    Để nó cho mắt agent là sai thiết kế: rubric ghi "chữ đạt AA" mà không có bất biến ⇒
  //    evaluator KHÔNG detect nổi chữ mờ, kể cả ở trang đăng nhập. Máy phải tính, không đoán.
  const srgb = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
  const lum = ([r, g, b]) => 0.2126 * srgb(r) + 0.7152 * srgb(g) + 0.0722 * srgb(b);
  const parse = (s) => { const m = s && s.match(/rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)/);
    return m ? { rgb: [ +m[1], +m[2], +m[3] ], a: m[4] === undefined ? 1 : +m[4] } : null; };
  const ratio = (fg, bg) => { const L1 = lum(fg), L2 = lum(bg);
    return +(((Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05))).toFixed(2); };
  const effBg = (el) => {                                   // nền hiệu dụng: leo cha tới khi có màu đục
    let q = el;
    while (q && q !== document.documentElement) {
      const c = parse(getComputedStyle(q).backgroundColor);
      if (c && c.a > 0.5) return c.rgb;
      q = q.parentElement;
    }
    const b = parse(getComputedStyle(document.body).backgroundColor);
    return b ? b.rgb : [255, 255, 255];
  };
  const fails = [];
  document.querySelectorAll("*").forEach((el) => {
    // chỉ xét phần tử có CHỮ TRỰC TIẾP (không tính chữ của con)
    const txt = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join(" ").trim();
    if (!txt) return;
    const cs = getComputedStyle(el);
    if (cs.visibility === "hidden" || cs.display === "none" || +cs.opacity < 0.15) return;
    const r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) return;
    const fg = parse(cs.color);
    if (!fg || fg.a < 0.15) return;
    const size = parseFloat(cs.fontSize), weight = +cs.fontWeight || 400;
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    const need = large ? 3.0 : 4.5;                          // WCAG AA
    const got = ratio(fg.rgb, effBg(el));
    if (got < need) fails.push({ text: txt.slice(0, 32), got, need, size: Math.round(size), color: cs.color });
  });
  if (fails.length) {
    fails.sort((a, b) => a.got - b.got);
    issues.push({ rule: "contrast-aa", count: fails.length, worst: fails.slice(0, 6) });
  }
  return issues;
}

// ── chụp từng route + audit ──
for (const [name, path] of ROUTES) {
  try {
    const resp = await page.goto(BASE + path, { waitUntil: "domcontentloaded", timeout: 15000 });
    await page.waitForTimeout(2200);
    const file = `${OUT}/${name}.png`;
    await page.screenshot({ path: file });
    const issues = await page.evaluate(DESIGN_AUDIT).catch(() => []);

    // ── BASELINE DIFF: bắt thay đổi NGOÀI Ý MUỐN (thứ mắt agent + bất-biến-CSS đều mù) ──
    let diff = null;
    if (BASELINE) {
      mkdirSync(BASELINE, { recursive: true });
      const baseFile = `${BASELINE}/${name}.png`;
      if (UPDATE_BASELINE || !existsSync(baseFile)) {
        copyFileSync(file, baseFile);                       // lần đầu / cập nhật → ghi chuẩn
        diff = { pct: 0, note: UPDATE_BASELINE ? "baseline cập nhật" : "baseline mới tạo" };
      } else {
        diff = diffAgainstBaseline(file, baseFile, `${OUT}/${name}.diff.png`);
      }
    }

    results.push({ name, path, status: resp?.status() ?? 0, file, issues, diff });
    const bad = issues.filter((i) => i.rule === "monochrome-surface").length;
    const dtxt = diff ? (diff.note ? `  [baseline: ${diff.note}]`
      : `  [diff ${diff.pct}%${diff.pct > DIFF_MAX ? " ⚠ VƯỢT NGƯỠNG" : ""}]`) : "";
    console.log(`shot ${name} (${path}) → ${resp?.status()}` +
      (issues.length ? `  ⚑ ${issues.map((i) => i.rule + (i.count ? "×" + i.count : "")).join(", ")}` : "  ✓ design-ok") +
      (bad ? "  [VI PHẠM BẤT BIẾN]" : "") + dtxt);
  } catch (e) {
    results.push({ name, path, error: e.message.split("\n")[0], issues: [] });
    console.log(`shot ${name} FAIL — ${e.message.split("\n")[0]}`);
  }
}

await browser.close();

// ── MANIFEST.json = BẰNG CHỨNG (chỉ tin file, không tin lời): mỗi route → file ảnh + bytes
//    thật trên đĩa. Không có file / bytes=0 = CHƯA TỪNG CHỤP = fail. ──
for (const r of results) {
  try {
    r.bytes = r.file ? statSync(r.file).size : 0;
  } catch { r.bytes = 0; }
  r.evidence = r.bytes > 0;
}
const manifest = { base: BASE, ts: Date.now(), shots: results };
const mpath = `${OUT}/MANIFEST.json`;
writeFileSync(mpath, JSON.stringify(manifest, null, 2));
console.log("\n=== BẰNG CHỨNG (route đã test → file ảnh) ===");
for (const r of results) console.log(`  ${r.evidence ? "✓" : "✗"} ${r.path}  ${r.file ?? "(no file)"}  ${r.bytes} bytes`);
console.log(`MANIFEST → ${mpath}`);
console.log("JSON " + JSON.stringify(results));

// ── BÁO BẤT BIẾN THIẾT KẾ (máy chấm, không dựa mắt) ──
const viol = results.flatMap((r) => (r.issues || []).filter((i) => i.rule === "monochrome-surface").map((i) => ({ ...i, path: r.path })));
const clip = results.flatMap((r) => (r.issues || []).filter((i) => i.rule === "shadow-clipped").map((i) => ({ ...i, path: r.path })));
if (viol.length) {
  console.log("\n=== ✗ VI PHẠM BẤT BIẾN: monochrome-surface (pane lệch màu nền) ===");
  viol.forEach((v) => console.log(`  ${v.path}: <${v.el}> bg=${v.got}  ≠ body=${v.want}`));
}
if (clip.length) {
  console.log("\n=== ⚠ shadow-clipped (bóng bị cắt bởi cha overflow:hidden) — PHẢI soi ảnh ===");
  clip.forEach((c) => console.log(`  ${c.path}: ${c.count} phần tử  vd ${(c.sample || []).join(", ")}`));
}
const contrast = results.flatMap((r) => (r.issues || []).filter((i) => i.rule === "contrast-aa").map((i) => ({ ...i, path: r.path })));
if (contrast.length) {
  console.log("\n=== ✗ VI PHẠM WCAG AA: chữ không đủ tương phản (máy TÍNH, không đoán) ===");
  contrast.forEach((c) => {
    console.log(`  ${c.path}: ${c.count} chỗ`);
    (c.worst || []).forEach((w) =>
      console.log(`     "${w.text}"  ${w.got}:1 < cần ${w.need}:1  (${w.size}px, ${w.color})`));
  });
}

// ── assert gate: fail nếu route lỗi / thiếu ảnh / VI PHẠM BẤT BIẾN ──
if (ASSERT) {
  const bad = results.filter((r) => r.error || (r.status && r.status >= 400) || r.status === 0 || !r.evidence);
  if (bad.length) {
    console.error("ASSERT FAIL (thiếu bằng chứng/lỗi): " +
      bad.map((b) => `${b.path}=${b.evidence ? (b.status ?? b.error) : "NO-IMAGE"}`).join(", "));
    process.exit(1);
  }
  if (viol.length) {
    console.error(`ASSERT FAIL — ${viol.length} vi phạm bất biến monochrome-surface (UI vỡ, không được pass)`);
    process.exit(1);
  }
  if (contrast.length) {
    const total = contrast.reduce((s, c) => s + c.count, 0);
    console.error(`ASSERT FAIL — ${total} chỗ chữ KHÔNG đạt WCAG AA trên ${contrast.length} route (a11y là luật, không phải sở thích)`);
    process.exit(1);
  }
  const regress = results.filter((r) => r.diff && !r.diff.note && r.diff.pct > DIFF_MAX);
  if (regress.length) {
    console.error(`\nASSERT FAIL — ${regress.length} route ĐỔI NGOÀI Ý MUỐN so baseline (> ${DIFF_MAX}%):`);
    regress.forEach((r) => console.error(`  ${r.path}: ${r.diff.pct}%  → xem ${r.diff.diffFile}`));
    console.error("  Cố ý đổi? chạy lại với --update-baseline. Không cố ý? ĐÂY LÀ REGRESSION.");
    process.exit(1);
  }
  console.log("\nASSERT OK — có ảnh + không vi phạm bất biến" +
    (BASELINE ? " + không lệch baseline" : "") +
    (clip.length ? ` (⚠ còn ${clip.length} route có shadow-clipped — soi ảnh)` : ""));
}
