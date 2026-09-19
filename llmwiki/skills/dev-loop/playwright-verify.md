---
name: playwright-verify
description: "Cài + dùng Playwright bằng standalone .mjs script (không qua npx playwright test / *.spec.ts) để verify code nhanh, một lần: chụp ảnh localhost/file://, đọc console/pageerror, đo getBoundingClientRect khi phần tử không thấy/không bấm được, auth bypass qua addCookies+addInitScript; việc NHIỀU BƯỚC thì mode phiên bền connectOverCDP (tab/cookie giữ nguyên giữa các lượt, không viết mù cả kịch bản). Dùng khi user nói 'verify bằng playwright', 'chụp ảnh trang', 'test nhanh UI bằng script', 'verify nhiều bước', 'giữ session giữa các lần chạy', 'claude-in-chrome bị chặn localhost', 'không click được / không thấy phần tử', hoặc invoke /playwright-verify. KHÁC uat-nonit-testcase (bộ test case UAT cho non-IT) và claude-in-chrome (extension, bị chặn localhost/file://) — đây là hướng dẫn CHUNG áp dụng mọi task."
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: playwright-verify

Đúc kết từ GH#96 — công cụ verify RẺ (< 5s/lần, không LLM) và là cách DUY NHẤT tương tác
được với `localhost`/`file://` khi `claude-in-chrome` bị chặn 2 scheme này trên máy.

## WHAT

### Purpose và context
- **Purpose:** verify code nhanh, một lần, bằng Playwright chạy qua standalone `.mjs` + `node` (không test runner): chụp ảnh `localhost`/`file://`, moi lỗi console/pageerror/http/requestfailed, đo phần tử thật, auth bypass; việc nhiều bước thì phiên bền `connectOverCDP`.
- **Trigger (when to use):**
- `claude-in-chrome` báo `Frame with ID 0 is showing error page` hoặc `Can't interact with
  browser-internal or unparseable URLs` trên `localhost:*` / `file://`.
- Cần chẩn đoán phần tử UI "không thấy" / "không bấm được" — ảnh chụp không đủ, cần số đo
  thật (`getBoundingClientRect`, `getComputedStyle`).
- Cần verify 1 giả thuyết code rồi vứt (không xứng tạo `*.spec.ts` + test runner).
- Cần test qua dev-login/session giả thay vì đăng nhập SSO thật mỗi lần.
  - User nói 'verify bằng playwright', 'chụp ảnh trang', 'test nhanh UI bằng script', 'verify nhiều bước', 'giữ session giữa các lần chạy', 'không click được / không thấy phần tử', hoặc `/playwright-verify`.
- **Non-goals:** không tạo `*.spec.ts` + test runner (`npx playwright test`), không phải bộ test case UAT (→ uat-nonit-testcase), không thay claude-in-chrome cho trang web ngoài bình thường, không commit script vào repo đích.

### Mental model
`giả thuyết cần verify → (đã cài?) → script .mjs một-phát: launch → gắn 4 kênh lỗi → goto (load + wait) → screenshot/đo → close → đọc log + ảnh → vứt`. Nhánh nhiều bước: `một Chrome CDP riêng (profile tạm) ← mỗi lượt step-N.mjs bám vào, state sống giữa các lượt → pkill khi xong`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | URL (`localhost:*` / `file://` / khác) | có | trang cần verify |
| In | project có `@playwright/test` trong `node_modules` | có | script phải chạy TỪ thư mục đó (hoặc `NODE_PATH`) |
| In | cookie/localStorage dev-login | không | cho auth bypass |
| Out | ảnh chụp (vd `/tmp/check.png`) + log `[console]`/`[pageerror]`/`[http]`/`[reqfail]` | có | bằng chứng; ảnh sạch một mình KHÔNG đủ |
| Out | số đo `getBoundingClientRect`/`getComputedStyle` | khi chẩn đoán phần tử | số thật thay vì đoán từ ảnh |
| Out | "xong" | — | giả thuyết xác nhận/bác bỏ bằng log + ảnh; script đã dọn; Chrome CDP (nếu có) đã `pkill` |

### Rules và capabilities
- RULE-01 (MUST): **`import { chromium } from "@playwright/test"` phải chạy TỪ TRONG thư mục project** có
  `@playwright/test` trong `node_modules` — ESM resolve theo `cwd`, không theo vị trí file
  script. Script ở thư mục khác (vd `/tmp`) → `cp` vào project trước khi chạy, hoặc trỏ
  `NODE_PATH`.
- RULE-02 (MUST): **`waitUntil: "networkidle"` TREO VÔ THỜI HẠN trên Next.js dev server** — HMR/webpack dev
  giữ 1 kết nối long-poll/websocket sống liên tục nên network không bao giờ "idle". Dùng
  `waitUntil: "load"` + `page.waitForTimeout(N)` cố định.
- RULE-03 (MUST): **Auth bypass cho dev-login**: `context.addCookies([{url, name, value}])` (ưu tiên `url`
  thay vì `domain`+`path` riêng lẻ — tránh cookie không match) + `context.addInitScript(...)`
  set `localStorage` — set state TRƯỚC khi gọi `newPage()`, không phải sau.
- RULE-04 (MUST): **1 `context` cho mỗi route độc lập** nếu app có logic "gặp 401 ở API phụ → tự xoá session
  toàn cục" — dùng lại 1 context cho nhiều navigation khiến lỗi route N hỏng lây route N+1.
- RULE-05 (MUST): **Chẩn đoán "không thấy/không bấm được"**: đừng chỉ nhìn ảnh chụp — gọi
  `page.evaluate(() => el.getBoundingClientRect())` + `getComputedStyle(el)` lấy số đo thật;
  `locator.click()` tự báo lỗi rõ ("element is not visible") kèm log các bước thử lại, đọc
  log đó trước khi đoán nguyên nhân.
- RULE-06 (MUST): **Ảnh chụp sạch không chứng minh gì — luôn moi 4 kênh lỗi**, không chỉ 2:
  `console` (type `error`) · `pageerror` · `response` có `status() >= 400` · `requestfailed`.
  Analytics crash, API 5xx, promise rejection không hiện lên pixel nào. Gắn vào `page` TRƯỚC
  `goto`:
  ```js
  page.on("response", r => { if (r.status() >= 400) console.log("[http]", r.status(), r.url()); });
  page.on("requestfailed", r => console.log("[reqfail]", r.failure()?.errorText, r.url()));
  ```
- RULE-07 (MUST): **Mode phiên bền: một Chrome riêng, một profile riêng** (`--user-data-dir` tạm). Không bao giờ
  `--remote-debugging-port` lên Chrome cá nhân của user — macOS bật hộp thoại xin phép và
  script sẽ giẫm lên tab user đang làm.
- RULE-08 (MUST): File script standalone không vào git — chạy từ scratchpad, không commit vào repo đích.
- RULE-09 (MUST): Touch only what the task requires — no opportunistic changes.
- Capabilities: chạy trình duyệt headless cục bộ + đọc/ghi file tạm; mạng ngoài chỉ khi cài binary (CDN), có timeout.

### Failure boundaries
- `npx playwright install` bị chặn mạng/treo → **blocked**, báo lỗi rõ (có timeout), không để lệnh treo vô hạn.
- ESM không resolve `@playwright/test` (chạy sai cwd) → cp script vào project hoặc `NODE_PATH`, rồi chạy lại.
- `networkidle` treo trên Next.js dev → đổi sang `load` + `waitForTimeout` (không phải lỗi app).
- Phần tử không thấy/không bấm → đo số thật + đọc log `locator.click()` trước khi kết luận; không đoán từ ảnh.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | máy | Kiểm đã cài (`ls ~/Library/Caches/ms-playwright`); chưa có thì cài | binary sẵn | CDN bị chặn → blocked |
| W02 | judgment | giả thuyết + URL | Viết 1 file `.mjs` chạy thẳng bằng `node`, gắn 4 kênh lỗi trước `goto` | script | — |
| W03 | effect | script | Chạy từ đúng thư mục (`node check.mjs`), đọc log + ảnh; dọn script | log + ảnh | resolve lỗi → cp/NODE_PATH, lặp W03 |
| W04 | effect | việc nhiều bước | Mode phiên bền `connectOverCDP` (B01) | state giữ giữa lượt | xong → `pkill` |

Chi tiết từng bước (nguồn chân lý cho W01–W04):

1. **Kiểm tra đã cài chưa** trước khi cài lại: `ls ~/Library/Caches/ms-playwright` (macOS) —
   binary cache dùng chung mọi project, không cần cài lại per-repo.
   - Chưa có: `pnpm add -D @playwright/test` (bỏ qua nếu project đã có sẵn trong
     `devDependencies`) rồi `npx playwright install chromium`.
   - `npx playwright install` tải binary từ CDN ngoài (`cdn.playwright.dev`) — sandbox/CI có
     allowlist mạng sẽ treo hoặc fail. Set timeout khi gọi tự động; nếu bị chặn, báo lỗi rõ
     thay vì để lệnh treo vô thời hạn.
2. **Viết 1 file `.mjs` chạy thẳng bằng `node`** (không qua `npx playwright test`) — nặng hơn
   cho việc verify-rồi-vứt:
   ```js
   import { chromium } from "@playwright/test"; // export chromium dùng được như package "playwright"

   const browser = await chromium.launch();
   const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
   page.on("console", m => console.log("[console]", m.type(), m.text()));
   page.on("pageerror", e => console.log("[pageerror]", e.message));

   await page.goto("http://localhost:3000/some-page", { waitUntil: "load" }); // KHÔNG "networkidle" — xem Rules #2
   await page.waitForTimeout(1500);
   await page.screenshot({ path: "/tmp/check.png", fullPage: true });

   await browser.close();
   ```
3. **Chạy từ đúng thư mục** (xem Rules #1), `node check.mjs`, đọc console/pageerror log +
   ảnh chụp. Dọn file `.mjs` sau khi xong nếu chạy trong 1 project cụ thể (không cần xoá gì
   khỏi git — script không nằm trong repo nếu chạy từ scratch dir).
4. **Việc NHIỀU BƯỚC có điều kiện → mode phiên bền** (học từ browser-use/browser-harness,
   09/2026). Script một-phát bắt agent viết mù cả kịch bản; sai một bước là chạy lại từ
   đăng nhập. Thay vào đó: dựng MỘT Chrome có cổng CDP, mỗi lượt là một script nhỏ bám vào —
   tab, cookie, `localStorage`, scroll giữ nguyên giữa các lượt, agent nhìn rồi mới quyết bước kế.
   ```bash
   # một lần — Chrome riêng, profile riêng; KHÔNG bám vào Chrome cá nhân của user
   CH="$HOME/Library/Caches/ms-playwright/chromium-1243/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
   "$CH" --remote-debugging-port=9333 --user-data-dir=/tmp/pw-prof --headless=new --no-first-run about:blank &
   ```
   ```js
   // mỗi lượt — step-N.mjs
   import { chromium } from "@playwright/test";
   const browser = await chromium.connectOverCDP("http://localhost:9333");
   const ctx = browser.contexts()[0];
   const page = ctx.pages()[0] ?? await ctx.newPage();   // bám tab cũ, KHÔNG launch mới
   // ... một hành động + quan sát; state sống sang lượt sau ...
   await browser.close();   // chỉ ngắt kết nối, Chrome vẫn chạy
   ```
   Xong việc: `pkill -f "remote-debugging-port=9333"`.
   Đo 09/09/2026 (python-playwright, cùng trang `file://`): launch mới 1.1–1.9s/lượt, mất
   state; `connectOverCDP` 0.65–0.80s/lượt, `window.__marker` sống qua tiến trình mới (3/3).
   Bản `.mjs` trên chưa chạy bằng node trong phiên đo — API đồng nhất với bản python đã chạy.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | việc NHIỀU BƯỚC có điều kiện (cần nhìn rồi mới quyết bước kế) | một Chrome riêng `--remote-debugging-port=9333` + profile tạm; mỗi lượt `step-N.mjs` `connectOverCDP` | việc một-phát → skip; không bao giờ bám Chrome cá nhân | kết thúc bằng `pkill -f "remote-debugging-port=9333"` |
| B02 | user_optional | trang cần dev-login/session giả | `context.addCookies` + `context.addInitScript` TRƯỚC `newPage()`; 1 context/route nếu app tự xoá session khi 401 | — | W03 |
| B03 | recovery | phần tử "không thấy/không bấm được" | `page.evaluate(() => el.getBoundingClientRect())` + `getComputedStyle(el)`, đọc log retry của `locator.click()` | — | W03 |

### Validation và stopping
Kết luận dựa trên 4 kênh lỗi + ảnh + số đo, không chỉ ảnh. Mỗi lượt chạy < 5s, không LLM. Dừng khi giả thuyết đã có bằng chứng; dọn script + `pkill` Chrome CDP.

### Examples
- **Positive:** claude-in-chrome báo `Frame with ID 0 is showing error page` trên `http://localhost:3000/some-page` → cp `check.mjs` vào project → `node check.mjs` → `/tmp/check.png` + log sạch cả `[console]`/`[pageerror]`/`[http]`/`[reqfail]` → xác nhận trang render, xoá script.
- **Boundary/failure:** script dùng `waitUntil: "networkidle"` trên Next.js dev → treo vô hạn; sửa thành `waitUntil: "load"` + `page.waitForTimeout(1500)` → chạy xong. Ảnh sạch nhưng log có `[http] 500 /api/x` → KHÔNG báo pass.
