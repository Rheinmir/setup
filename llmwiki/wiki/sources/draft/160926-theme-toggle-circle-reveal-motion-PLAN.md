---
type: draft
title: theme-toggle-circle-reveal-motion-PLAN
status: proposed
timestamp: 2026-09-16
task: T-260916-01
---

# Circle-reveal theme motion — PLAN thi hành

**Goal:** Đổi luật chuyển dark/light của `docs-site-macos` (+ mọi trang tuân `html-theme-toggle-required`) từ flip tức thời sang circle-reveal, cộng script Playwright nghiệm thu được.
**Architecture:** Mở rộng kỹ thuật Ripple đã có sẵn trong skill (DOM overlay + Web Animations API `clip-path`), không dùng View Transitions API — để có DOM handle thật cho Playwright assert trực tiếp.
**Tech stack:** HTML/CSS/JS thuần (không dependency ngoài), Python 3 (generator `fdk/tools/build-overstack-docs.py`), Node + `@playwright/test` (script nghiệm thu).
**SPEC nguồn:** `wiki/sources/draft/160926-theme-toggle-circle-reveal-motion.md` (đã duyệt 2026-09-16).

## Origin
- **SPEC:** `wiki/sources/draft/160926-theme-toggle-circle-reveal-motion.md`
- **Commit:** _(verify-before-commit điền)_

## Global constraints
- Không ép 1 mode — circle-reveal chỉ đổi CÁCH chuyển, không được bỏ khả năng user tự chọn light/dark.
- Dạng nút bắt buộc: NÚT GẠT (switch), nhãn "Giao diện", hàng footer dính đáy sidebar/nav.
- Generator một nguồn — `_DARK_RULES`/JS trong `fdk/tools/build-overstack-docs.py` và snippet trong `skills/docs-site-macos/SKILL.md` phải khớp nhau.
- `prefers-reduced-motion: reduce` phải tôn trọng — fallback ≤150ms opacity crossfade, không phải 0 motion, không phải spatial motion full-screen.
- System fonts / self-contained — không thêm dependency animation ngoài.
- Prose đầy đủ cho tài liệu người đọc; KHÔNG ghi công AI trong commit/PR.

## File structure
- Sửa `skills/docs-site-macos/SKILL.md` — canonical, § "Theme Toggle sáng/tối", thêm mục 4 circle-reveal + fix `.theme-row{background:inherit}`.
- Sửa `llmwiki/skills/utils/docs-site-macos.md` — mirror, phải parity byte-for-byte với canonical.
- Sửa `fdk/tools/build-overstack-docs.py` — generator, đồng bộ CSS `.theme-row` + JS `flip()`.
- Sửa `llmwiki/html/overstack.html` — output generated, regen từ generator sau khi sửa.
- Tạo `skills/docs-site-macos/scripts/verify-theme-motion.mjs` — script Playwright nghiệm thu độc lập.
- Sửa `llmwiki/skills/utils/fdk.md` + `skills/fdk/SKILL.md` — canonical+mirror, thêm dòng trỏ luật mới.
- Sửa `llmwiki/html/160926-theme-toggle-circle-reveal-motion-seq.html` — companion HTML của SPEC, patch bằng snippet mới làm bằng chứng T6.

### Task 1: Viết snippet circle-reveal (canonical)

**Thoả:** FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008

**Files:**
- Sửa: `skills/docs-site-macos/SKILL.md` § "Theme Toggle sáng/tối" (mục 3 fix `.theme-row`, mục 4 mới circle-reveal)

**Interfaces:**
- Produces: overlay `.theme-reveal` (`position:fixed;inset:0`), hàm `flip()` gọi `commit(next)` giữa lúc grow-animation `onfinish`, biến `busy` chặn double-click. Task 3 (generator) và Task 6 (companion HTML patch) đọc đúng contract này.

**Depends:** —
**Verify:** `grep -c "theme-reveal" skills/docs-site-macos/SKILL.md` (≥ 1)

- [x] **Step 1: đọc `flip()` cũ + kỹ thuật Ripple sẵn có** (dòng 196-226, 1014-1024 bản cũ) làm tham chiếu.
- [x] **Step 2: viết overlay `.theme-reveal` + `flip()` mới**:

```js
function flip(){
  if(busy)return; var next=isDark()?'light':'dark';
  var r=sw.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2;
  var reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var bg=next==='dark'?'#0c0f16':'#f7fbff';
  var canAnimate='animate' in document.createElement('div');
  busy=true;
  var el=document.createElement('div');el.className='theme-reveal';el.style.background=bg;
  document.body.appendChild(el);
  if(reduced||!canAnimate){
    el.style.cssText+=';opacity:0;transition:opacity .075s linear';
    requestAnimationFrame(function(){el.style.opacity='1'});
    setTimeout(function(){commit(next);el.style.opacity='0';setTimeout(function(){el.remove();busy=false},90)},90);
    return;
  }
  var maxR=Math.hypot(Math.max(x,innerWidth-x),Math.max(y,innerHeight-y));
  var grow=el.animate([
    {clipPath:'circle(0px at '+x+'px '+y+'px)'},
    {clipPath:'circle('+maxR+'px at '+x+'px '+y+'px)'}
  ],{duration:520,easing:'cubic-bezier(.3,0,.1,1)',fill:'forwards'});
  grow.onfinish=function(){
    commit(next);   // FR-005: data-theme đổi ĐÚNG lúc phủ hết, trước fade
    var fadeOut=el.animate([{opacity:1},{opacity:0}],{duration:180,easing:'ease-out',fill:'forwards'});
    fadeOut.onfinish=function(){el.remove();busy=false};   // FR-006: gỡ khỏi DOM sau fade
  };
}
```

- [x] **Step 3: fix `.theme-row{background:inherit}`**:

```css
.theme-row{position:sticky;bottom:calc(-1 * var(--nav-pad-y));margin-top:auto;display:flex;align-items:center;justify-content:space-between;
  padding:11px 16px;border-top:1px solid rgba(30,90,170,.14);background:inherit;backdrop-filter:blur(14px)}
```

- [x] **Step 4: verify** — `grep -c "theme-reveal" skills/docs-site-macos/SKILL.md` → 4 (đạt, ≥ 1).

### Task 2: Đồng bộ mirror docs-site-macos

**Thoả:** FR-011

**Files:**
- Sửa: `llmwiki/skills/utils/docs-site-macos.md`

**Interfaces:**
- Consumes: nội dung canonical từ Task 1 (đã chốt).

**Depends:** Task 1
**Verify:** `diff skills/docs-site-macos/SKILL.md llmwiki/skills/utils/docs-site-macos.md` (rc 0, rỗng)

- [x] **Step 1: copy canonical → mirror**:

```bash
cp skills/docs-site-macos/SKILL.md llmwiki/skills/utils/docs-site-macos.md
```

- [x] **Step 2: verify**:

```bash
diff skills/docs-site-macos/SKILL.md llmwiki/skills/utils/docs-site-macos.md
# (không in gì — rc 0) → PASS
```

### Task 3: Rà + sửa generator

**Thoả:** FR-009

**Files:**
- Sửa: `fdk/tools/build-overstack-docs.py` (`.theme-row` CSS dòng ~282/311, JS `flip()` dòng ~324-334)
- Sửa: `llmwiki/html/overstack.html` (output, regen)

**Interfaces:**
- Consumes: contract `.theme-reveal`/`commit()`/`busy` từ Task 1.

**Depends:** Task 1
**Verify:** `python3 fdk/tools/build-overstack-docs.py --check`

- [x] **Step 1: grep**:

```bash
grep -n "flip\|theme-switch\|theme-row\|_DARK_RULES" fdk/tools/build-overstack-docs.py
# → CÓ JS trùng lặp thật (dòng 329 flip(), dòng 282/311 .theme-row) — nhánh blocked của SPEC, không phải no-op
```

- [x] **Step 2: sửa `.theme-row`**:

```python
# base (light default) — trước: background:linear-gradient(180deg,rgba(255,255,255,.55),rgba(240,248,255,.65))
".theme-row{...background:inherit;backdrop-filter:blur(14px) saturate(1.4);...}"
# _DARK_RULES — trước: ("& .theme-row", "border-top-color:var(--border);background:linear-gradient(180deg,rgba(24,28,38,.7),rgba(16,20,28,.85))")
("& .theme-row", "border-top-color:var(--border)"),  # background:inherit đã tự lo
```

- [x] **Step 3: sửa JS `flip()`** — thay bằng cùng logic circle-reveal (grow/commit/fade/reduced-motion) như Task 1:

```python
JS = r"""
...
var busy=false;
function commit(next){d.setAttribute('data-theme',next);try{localStorage.setItem(K,next)}catch(e){}paint()}
function flip(){
  if(busy)return;var next=isDark()?'light':'dark';
  var r=sw.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2;
  var reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var bg=next==='dark'?'#0c0f16':'#f7fbff';
  var canAnimate='animate' in document.createElement('div');
  busy=true;
  var el=document.createElement('div');el.className='theme-reveal';el.style.cssText='position:fixed;inset:0;z-index:300;pointer-events:none;will-change:clip-path,opacity;background:'+bg;
  document.body.appendChild(el);
  if(reduced||!canAnimate){
    el.style.cssText+=';opacity:0;transition:opacity .075s linear';
    requestAnimationFrame(function(){el.style.opacity='1'});
    setTimeout(function(){commit(next);el.style.opacity='0';setTimeout(function(){el.remove();busy=false},90)},90);
    return;
  }
  var maxR=Math.hypot(Math.max(x,innerWidth-x),Math.max(y,innerHeight-y));
  var grow=el.animate([{clipPath:'circle(0px at '+x+'px '+y+'px)'},{clipPath:'circle('+maxR+'px at '+x+'px '+y+'px)'}],{duration:520,easing:'cubic-bezier(.3,0,.1,1)',fill:'forwards'});
  grow.onfinish=function(){
    commit(next);
    var fadeOut=el.animate([{opacity:1},{opacity:0}],{duration:180,easing:'ease-out',fill:'forwards'});
    fadeOut.onfinish=function(){el.remove();busy=false};
  };
}
"""
```

- [x] **Step 4: regen**:

```bash
python3 fdk/tools/build-overstack-docs.py
# ✓ wrote llmwiki/html/overstack.html (599090 bytes, 817 dòng)
```

- [x] **Step 5: verify**:

```bash
python3 fdk/tools/build-overstack-docs.py --check
# overstack.html khớp đĩa ✓ → PASS
```

### Task 4: Script Playwright nghiệm thu

**Thoả:** FR-010

**Files:**
- Tạo: `skills/docs-site-macos/scripts/verify-theme-motion.mjs`

**Interfaces:**
- Consumes: DOM contract từ Task 1 (`.theme-switch`, `.theme-reveal`, `data-theme`, key localStorage kết thúc `-theme`).
- Produces: CLI `node verify-theme-motion.mjs <file.html>` → rc 0 PASS / rc 1 FAIL + danh sách lý do.

**Depends:** Task 1
**Verify:** `node skills/docs-site-macos/scripts/verify-theme-motion.mjs llmwiki/html/overstack.html` (cần `npm install --no-save @playwright/test` trước, chạy từ thư mục có `node_modules` trong chuỗi ancestor của script)

- [x] **Step 1: viết script** — assert overlay đúng toạ độ/màu, `data-theme` đổi SAU khi grow xong (không phải giữa chừng), overlay gỡ khỏi DOM sau fade, `localStorage` đúng; lượt 2 với `page.emulateMedia({reducedMotion:'reduce'})` assert không có spatial motion:

```js
import { chromium } from "@playwright/test";
// ... (toàn bộ script thật tại skills/docs-site-macos/scripts/verify-theme-motion.mjs)
async function runFullMotion(browser) {
  await withPage(browser, {}, async (page) => {
    const sw = await findSwitch(page);
    const before = await page.evaluate(() => ({ theme: document.documentElement.getAttribute("data-theme") }));
    const box = await sw.boundingBox();
    await sw.click();
    await page.waitForTimeout(300);
    const mid = await page.evaluate(() => document.documentElement.getAttribute("data-theme"));
    if (mid !== before.theme) fail("data-theme đổi QUÁ SỚM — lộ mode mới trước khi phủ hết màn hình");
    await page.waitForTimeout(350);
    const afterGrow = await page.evaluate(() => document.documentElement.getAttribute("data-theme"));
    if (afterGrow === before.theme) fail("data-theme KHÔNG đổi sau khi overlay đã phủ hết viewport");
  });
}
```

- [x] **Step 2: cài playwright tạm** (scratchpad, không lưu vào repo):

```bash
cd scratchpad && npm install --no-save @playwright/test
```

- [x] **Step 3: chạy thật trên `overstack.html`**:

```bash
node verify-theme-motion.mjs ../llmwiki/html/overstack.html
# [note] full-motion: (system) → dark, overlay gỡ đúng lúc: true
# [note] reduced-motion: (system) → dark, xong nhanh, không spatial motion
# VERIFY PASS — file:///…/overstack.html
```

### Task 5: Cập nhật tham chiếu luật

**Thoả:** FR-011

**Files:**
- Sửa: `llmwiki/skills/utils/fdk.md` § Rules
- Sửa: `skills/fdk/SKILL.md` (canonical, parity với trên)
- Sửa: `/Users/giatran/.claude/projects/-Users-giatran-orca-setup-setup/memory/html-theme-toggle-required.md` (memory cá nhân, ngoài repo)

**Interfaces:**
- Consumes: đường dẫn script từ Task 4, mô tả hành vi từ Task 1.

**Depends:** Task 1, Task 4
**Verify:** `diff skills/fdk/SKILL.md llmwiki/skills/utils/fdk.md` (rc 0, rỗng)

- [x] **Step 1: thêm dòng luật mới vào `fdk.md`**:

```markdown
- **Chuyển mode PHẢI qua circle-reveal, không phải flip tức thời (feedback 160926, task `T-260916-01`)** —
  nút gạt bấm xong mở một overlay tròn màu nền = MODE ĐÍCH, tỏa từ đúng toạ độ nút, lan chậm rồi
  nhanh-dứt-khoát phủ kín viewport, ĐÓ mới là lúc `data-theme`/`localStorage` đổi giá trị, rồi overlay
  fade. Tôn trọng `prefers-reduced-motion: reduce`. Snippet chuẩn: skill `docs-site-macos` § "Theme
  Toggle sáng/tối" mục 4; nghiệm thu bằng `node skills/docs-site-macos/scripts/verify-theme-motion.mjs
  <file.html>`.
```

- [x] **Step 2: đồng bộ canonical**:

```bash
cp llmwiki/skills/utils/fdk.md skills/fdk/SKILL.md
diff skills/fdk/SKILL.md llmwiki/skills/utils/fdk.md   # rc 0 → PASS
```

- [x] **Step 3: cập nhật memory cá nhân**:

```markdown
**Cập nhật 160926 (task `T-260916-01`):** chuyển mode giờ KHÔNG còn tức thời — phải qua circle-reveal
(...). Nghiệm thu máy: `node skills/docs-site-macos/scripts/verify-theme-motion.mjs <file.html>` — đã
chạy PASS thật trên `llmwiki/html/overstack.html` và trên chính companion HTML của đề xuất.
```

### Task 6: Chứng minh thật trên companion HTML

**Thoả:** FR-001…FR-010 (bằng chứng end-to-end), SC-001, SC-002, SC-004

**Files:**
- Sửa: `llmwiki/html/160926-theme-toggle-circle-reveal-motion-seq.html`

**Interfaces:**
- Consumes: contract circle-reveal từ Task 1, script từ Task 4.

**Depends:** Task 1, Task 4
**Verify:** `node skills/docs-site-macos/scripts/verify-theme-motion.mjs llmwiki/html/160926-theme-toggle-circle-reveal-motion-seq.html`

- [x] **Step 1: patch trang** — thay `flip()` cũ bằng đúng logic circle-reveal của Task 1 (đã có `.theme-reveal` CSS + `.theme-row{background:inherit}` từ vòng sửa feedback design trước đó).
- [x] **Step 2: chạy verify thật** → `VERIFY PASS — file:///…/160926-theme-toggle-circle-reveal-motion-seq.html`. Log:
  ```
  [note] full-motion: (system) → dark, overlay gỡ đúng lúc: true
  [note] reduced-motion: (system) → dark, xong nhanh, không spatial motion
  VERIFY PASS
  ```

## Self-review
1. **Phủ SPEC** — FR-001…FR-011 đều có task nhận (Task 1: 001-005,007,008 · Task 2/5: 011 · Task 3: 009 · Task 4: 010). SC-001/002 chứng bằng Task 6 chạy thật trên 2 trang; SC-003 là hệ quả tự nhiên của Task 1-2 (snippet có sẵn trong skill); SC-004 = chính output PASS của Task 4/6.
2. **Quét placeholder** — không còn chỗ mơ hồ chờ điền; mọi step đã đánh dấu `[x]` kèm bằng chứng lệnh + output thật (không phải dự đoán).
3. **Nhất quán tên/kiểu** — `flip()`, `commit()`, `busy`, `.theme-reveal`, `.theme-switch`, `verify-theme-motion.mjs` dùng thống nhất Task 1/3/4/6, không đổi tên giữa chừng.

## Kết quả thật (không phải kế hoạch — đã chạy)
- `medic --ci`: 0 fail · 1 warn (orchestration, không liên quan) · 18 ok.
- `python3 fdk/tools/build-overstack-docs.py --check`: PASS.
- `node skills/docs-site-macos/scripts/verify-theme-motion.mjs llmwiki/html/overstack.html`: PASS.
- `node skills/docs-site-macos/scripts/verify-theme-motion.mjs llmwiki/html/160926-theme-toggle-circle-reveal-motion-seq.html`: PASS.
- Parity canonical↔mirror: `docs-site-macos` OK, `fdk` OK.
