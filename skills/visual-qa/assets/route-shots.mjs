#!/usr/bin/env node
// route-shots — luồng QA thị giác: login rồi chụp headless từng route có tồn tại.
// Dùng playwright-core + Chrome hệ thống (không tải browser riêng). Ảnh → <out>/<name>.png.
// Người/agent đọc ảnh → viết FINDINGS.md → bật luồng sửa. (frame QA của dây chuyền.)
//
// Usage: node route-shots.mjs --base http://localhost:5230 --out ./qa-shots \
//                             --user demo --pass demo --pw-root <scratchpad/qa>
import { chromium } from "playwright-core";
import { mkdirSync, statSync, writeFileSync } from "node:fs";

const arg = (k, d) => { const i = process.argv.indexOf(k); return i > -1 ? process.argv[i + 1] : d; };
const BASE = arg("--base", "http://localhost:5230");
const OUT = arg("--out", "./qa-shots");
const USER = arg("--user", "demo");
const PASS = arg("--pass", "demo");

// --route /pc : chụp+kiểm ĐÚNG 1 route (cho vòng tự-kiểm của frame UI).
// --assert   : exit 1 nếu route không 200 hoặc trang rỗng/lỗi (dùng làm acceptance gate).
const ONE = arg("--route", null);
const ASSERT = process.argv.includes("--assert");
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

// ── login qua form ──
await page.goto(BASE + "/auth", { waitUntil: "domcontentloaded" });
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

// ── chụp từng route ──
for (const [name, path] of ROUTES) {
  try {
    const resp = await page.goto(BASE + path, { waitUntil: "domcontentloaded", timeout: 15000 });
    await page.waitForTimeout(2200);
    const file = `${OUT}/${name}.png`;
    await page.screenshot({ path: file });
    results.push({ name, path, status: resp?.status() ?? 0, file });
    console.log(`shot ${name} (${path}) → ${resp?.status()}`);
  } catch (e) {
    results.push({ name, path, error: e.message.split("\n")[0] });
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

// ── assert gate: fail nếu route lỗi HOẶC không có ảnh bằng chứng ──
if (ASSERT) {
  const bad = results.filter((r) => r.error || (r.status && r.status >= 400) || r.status === 0 || !r.evidence);
  if (bad.length) {
    console.error("ASSERT FAIL (thiếu bằng chứng/lỗi): " +
      bad.map((b) => `${b.path}=${b.evidence ? (b.status ?? b.error) : "NO-IMAGE"}`).join(", "));
    process.exit(1);
  }
  console.log("ASSERT OK — mọi route có ảnh bằng chứng");
}
