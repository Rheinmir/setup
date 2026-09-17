#!/usr/bin/env node
// Nghiệm thu circle-reveal khi chuyển dark/light — xem skills/dark-mode-maker/SKILL.md § "Circle-reveal
// + crest-glow". Standalone .mjs, không qua `npx playwright test` (đúng convention `playwright-verify`).
//
// Cài trước khi chạy (chưa có sẵn @playwright/test trong project thì cài tạm, KHÔNG cần lưu vào package.json):
//   npm install --no-save @playwright/test
//
// Dùng: node verify-theme-motion.mjs <file.html | http(s)://...>
//
// Assert:
//   - overlay .theme-reveal xuất hiện đúng toạ độ CON TRỎ lúc bấm (không phải tâm nút), màu nền = MODE ĐÍCH
//   - bấm ở điểm ngoài biên nút → toạ độ tỏa bị KẸP trong biên nút (clamp), không vọt ra ngoài
//   - .theme-reveal có filter drop-shadow (crest-glow) — không spawn phần tử .theme-ripple phụ nào
//   - data-theme/localStorage đổi giá trị SAU khi overlay phủ hết viewport (không lộ mode cũ)
//   - overlay bị gỡ khỏi DOM sau khi fade xong
//   - nhánh prefers-reduced-motion: reduce KHÔNG có hiệu ứng full-screen, chỉ crossfade ngắn

import { chromium } from "@playwright/test";

const target = process.argv[2];
if (!target) {
  console.error("Dùng: node verify-theme-motion.mjs <file.html | http(s)://...>");
  process.exit(2);
}
const url = /^https?:\/\//.test(target) ? target : "file://" + (target.startsWith("/") ? target : process.cwd() + "/" + target);

const errors = [];
const note = (msg) => console.log("[note]", msg);
const fail = (msg) => errors.push(msg);

async function withPage(browser, opts, fn) {
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 }, ...opts });
  page.on("pageerror", (e) => fail("pageerror: " + e.message));
  page.on("console", (m) => { if (m.type() === "error") fail("console.error: " + m.text()); });
  await page.goto(url, { waitUntil: "load" });
  await page.waitForTimeout(300);
  try {
    return await fn(page);
  } finally {
    await page.close();
  }
}

async function findSwitch(page) {
  const has = await page.evaluate(() => !!document.querySelector(".theme-switch"));
  if (!has) { fail("Không tìm thấy .theme-switch trên trang — thiếu theme toggle"); return null; }
  return page.$(".theme-switch");
}

function parseClipCircle(clipPath) {
  // "circle(123.45px at 45.6px 78.9px)" -> { r, x, y }
  const m = /circle\(([\d.]+)px at ([\d.]+)px ([\d.]+)px\)/.exec(clipPath || "");
  if (!m) return null;
  return { r: parseFloat(m[1]), x: parseFloat(m[2]), y: parseFloat(m[3]) };
}

async function runOriginFromCursor(browser) {
  await withPage(browser, {}, async (page) => {
    const sw = await findSwitch(page);
    if (!sw) return;
    const box = await sw.boundingBox();
    if (!box) { fail("Không đo được vị trí .theme-switch"); return; }

    // điểm bấm KHÔNG phải tâm nút — gần góc trái-dưới của track
    const px = box.x + box.width * 0.15;
    const py = box.y + box.height * 0.85;
    await sw.click({ position: { x: box.width * 0.15, y: box.height * 0.85 } });
    await page.waitForTimeout(40);
    const clip = await page.evaluate(() => {
      const el = document.querySelector(".theme-reveal");
      return el ? getComputedStyle(el).clipPath : null;
    });
    const c = parseClipCircle(clip);
    if (!c) { fail("Không đọc được clip-path của .theme-reveal ngay sau khi bấm"); }
    else {
      const dx = Math.abs(c.x - px), dy = Math.abs(c.y - py);
      if (dx > 3 || dy > 3) fail(`Điểm tỏa không khớp toạ độ con trỏ: click tại (${px.toFixed(1)},${py.toFixed(1)}), overlay tỏa từ (${c.x},${c.y})`);
      else note(`origin đúng con trỏ: click (${px.toFixed(1)},${py.toFixed(1)}) → overlay (${c.x},${c.y})`);
    }
    // dọn: chờ hết animation trước khi rời trang (tránh log lỗi thừa)
    await page.waitForTimeout(900);
  });
}

async function runOriginClamped(browser) {
  await withPage(browser, {}, async (page) => {
    const sw = await findSwitch(page);
    if (!sw) return;
    const box = await sw.boundingBox();
    if (!box) return;

    // bắn synthetic click với clientX/Y NẰM XA NGOÀI biên nút — JS phải tự kẹp lại trong biên
    const wildX = box.x + box.width + 400;
    const wildY = box.y - 300;
    await page.evaluate(({ wildX, wildY }) => {
      const el = document.querySelector(".theme-switch");
      const ev = new MouseEvent("click", { bubbles: true, clientX: wildX, clientY: wildY });
      el.dispatchEvent(ev);
    }, { wildX, wildY });
    await page.waitForTimeout(40);
    const clip = await page.evaluate(() => {
      const el = document.querySelector(".theme-reveal");
      return el ? getComputedStyle(el).clipPath : null;
    });
    const c = parseClipCircle(clip);
    if (!c) { fail("Không đọc được clip-path của .theme-reveal ở lượt test kẹp biên"); }
    else {
      const withinX = c.x >= box.x - 1 && c.x <= box.x + box.width + 1;
      const withinY = c.y >= box.y - 1 && c.y <= box.y + box.height + 1;
      if (!withinX || !withinY) fail(`Điểm tỏa KHÔNG bị kẹp trong biên nút: click ảo tại (${wildX},${wildY}), overlay tỏa từ (${c.x},${c.y}), biên nút x∈[${box.x.toFixed(1)},${(box.x+box.width).toFixed(1)}] y∈[${box.y.toFixed(1)},${(box.y+box.height).toFixed(1)}]`);
      else note(`clamp đúng: click ảo xa ngoài biên (${wildX},${wildY}) → overlay bị kẹp về (${c.x},${c.y}), trong biên nút`);
    }
    await page.waitForTimeout(900);
  });
}

async function runFullMotion(browser) {
  await withPage(browser, {}, async (page) => {
    const sw = await findSwitch(page);
    if (!sw) return;

    const before = await page.evaluate(() => ({
      theme: document.documentElement.getAttribute("data-theme"),
      isDark: document.documentElement.getAttribute("data-theme")
        ? document.documentElement.getAttribute("data-theme") === "dark"
        : matchMedia("(prefers-color-scheme: dark)").matches,
    }));

    await sw.click();

    // Đợi theo API animation THẬT (event 'finish' + MutationObserver), KHÔNG đoán mốc ms —
    // TOTAL_MS trong HTML có thể chỉnh xuống bất kỳ đâu (đã thấy tận 20ms), đoán mốc cố định sẽ luôn vỡ.
    // LƯU Ý (bug đã bắt được lúc viết test này): `await anim.finished` (promise) có thể resolve TRƯỚC
    // event 'finish' — mà `onfinish` (nơi code thật gọi commit()) lắng nghe qua event, không qua promise.
    // Phải đợi đúng bằng event 'finish' thì mới đồng bộ đúng thời điểm với code thật.
    const r = await page.evaluate(async (beforeTheme) => {
      const el = document.querySelector(".theme-reveal");
      if (!el) return { ok: false, reason: "no-overlay" };
      const cs = getComputedStyle(el);
      const justAfter = {
        bg: cs.backgroundColor,
        position: cs.position,
        filter: cs.filter,
        rippleCount: document.querySelectorAll(".theme-ripple").length,
      };
      const growAnim = el.getAnimations()[0];
      const midTheme = document.documentElement.getAttribute("data-theme"); // đọc NGAY, trước khi await — chắc chắn còn giữa chừng
      if (growAnim) {
        await new Promise((resolve) => {
          if (growAnim.playState === "finished") return resolve();
          growAnim.addEventListener("finish", resolve, { once: true });
        }); // chờ ĐÚNG lúc clip-path phủ hết (event, đồng bộ với onfinish thật), bất kể duration bao nhiêu
      }
      const afterGrowTheme = document.documentElement.getAttribute("data-theme");
      const overlayGone = await new Promise((resolve) => {
        if (!document.querySelector(".theme-reveal")) return resolve(true);
        const mo = new MutationObserver(() => {
          if (!document.querySelector(".theme-reveal")) { mo.disconnect(); resolve(true); }
        });
        mo.observe(document.body, { childList: true });
        setTimeout(() => { mo.disconnect(); resolve(!document.querySelector(".theme-reveal")); }, 3000);
      });
      return { ok: true, justAfter, midTheme, afterGrowTheme, overlayGone };
    }, before.theme);

    if (!r.ok) {
      fail("Không thấy overlay .theme-reveal xuất hiện ngay sau khi bấm toggle");
    } else {
      const wantDark = !before.isDark; // bấm 1 lần = đảo mode
      const wantBg = wantDark ? "rgb(9, 9, 11)" : "rgb(247, 251, 255)"; // #09090b / #f7fbff
      if (r.justAfter.bg !== wantBg) fail(`Màu overlay sai: có ${r.justAfter.bg}, muốn ${wantBg} (mode đích: ${wantDark ? "dark" : "light"})`);
      if (r.justAfter.position !== "fixed") fail(`Overlay không phải position:fixed (đang là ${r.justAfter.position}) — không phủ được toàn viewport`);
      if (!r.justAfter.filter || r.justAfter.filter === "none") fail("Overlay thiếu filter drop-shadow (crest-glow) — hiệu ứng gợn nước không còn");
      if (r.justAfter.rippleCount > 0) fail(`Vẫn còn ${r.justAfter.rippleCount} .theme-ripple phụ — thiết kế cũ (đuổi theo, gây lag) chưa bị gỡ hết`);
    }
    if (r.ok && r.midTheme !== before.theme) fail("data-theme đổi QUÁ SỚM (ngay lúc overlay vừa xuất hiện) — lộ mode mới trước khi phủ hết màn hình");
    if (r.ok && r.afterGrowTheme === before.theme) fail("data-theme KHÔNG đổi sau khi overlay đã phủ hết viewport (grow animation đã finished)");
    if (r.ok && !r.overlayGone) fail("Overlay .theme-reveal vẫn còn trong DOM 3s sau khi animation phải đã xong — có thể chặn tương tác phía dưới");
    const afterGrow = r.ok ? r.afterGrowTheme : null;
    const overlayGone = r.ok ? r.overlayGone : false;

    // localStorage: tìm bất kỳ key nào kết thúc bằng '-theme' đã lưu đúng giá trị mới
    const stored = await page.evaluate((wantDark) => {
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && k.endsWith("-theme")) return localStorage.getItem(k) === (wantDark ? "dark" : "light");
      }
      return false;
    }, !before.isDark);
    if (!stored) fail("localStorage không lưu đúng lựa chọn theme mới (khoá kết thúc bằng '-theme')");

    note(`full-motion: ${before.theme || "(system)"} → ${afterGrow}, overlay gỡ đúng lúc: ${overlayGone}`);
  });
}

async function runReducedMotion(browser) {
  await withPage(browser, { reducedMotion: "reduce" }, async (page) => {
    const sw = await findSwitch(page);
    if (!sw) return;
    const before = await page.evaluate(() => document.documentElement.getAttribute("data-theme"));

    await sw.click();

    // ngay sau click với reduced-motion: nếu có overlay thì phải rất ngắn, không phủ kiểu clip-path lan dần
    await page.waitForTimeout(40);
    const justAfter = await page.evaluate(() => {
      const el = document.querySelector(".theme-reveal");
      return el ? getComputedStyle(el).clipPath : "none";
    });
    if (justAfter !== "none" && justAfter !== "" && !justAfter.includes("none")) {
      fail(`Nhánh reduced-motion vẫn dùng clip-path lan (${justAfter}) — phải là crossfade phẳng, không phải spatial motion`);
    }

    // toàn bộ fallback phải xong trong < 300ms — chờ dư rồi kiểm overlay đã gỡ + theme đã đổi
    await page.waitForTimeout(280);
    const after = await page.evaluate(() => document.documentElement.getAttribute("data-theme"));
    const overlayGone = await page.evaluate(() => !document.querySelector(".theme-reveal"));
    if (after === before) fail("Nhánh reduced-motion: data-theme không đổi");
    if (!overlayGone) fail("Nhánh reduced-motion: overlay vẫn còn trong DOM sau >250ms — không phải ≤150ms crossfade");

    note(`reduced-motion: ${before || "(system)"} → ${after}, xong nhanh, không spatial motion`);
  });
}

const browser = await chromium.launch();
try {
  await runOriginFromCursor(browser);
  await runOriginClamped(browser);
  await runFullMotion(browser);
  await runReducedMotion(browser);
} finally {
  await browser.close();
}

if (errors.length) {
  console.log("VERIFY FAIL:");
  errors.forEach((e) => console.log(" -", e));
  process.exit(1);
}
console.log("VERIFY PASS —", url);
