---
name: dark-mode-maker
description: Circle-reveal (giọt nước rơi + crest-glow liquid-glass) khi chuyển dark/light mode — nút gạt switch, overlay tỏa từ VỊ TRÍ CON TRỎ (kẹp trong biên nút), palette dark-mode trung tính kiểu thị trường (GitHub Dark/Vercel/Linear), nghiệm thu bằng Playwright thật. Gọi khi user nói 'làm dark mode', 'theme toggle', 'chuyển sáng tối', 'circle reveal', 'hiệu ứng đổi giao diện', hoặc /dark-mode-maker. KHÁC docs-site-macos (đó là sàn trang tài liệu macOS, dark-mode-maker là module toggle dùng được cho MỌI trang HTML).
---

# Skill: dark-mode-maker

Module độc lập, tách ra từ `docs-site-macos` (feedback 160926: "bê nguyên cái làm hiệu ứng dark/light mode thành 1 skill riêng"). Dùng được cho BẤT KỲ trang HTML nào cần nút chuyển dark/light — không chỉ trang docs-site-macos.

## When to use
- Trang cần nút chuyển dark/light (mọi trang HTML sinh cho người xem, theo luật `html-theme-toggle-required`).
- User nói "làm dark mode", "theme toggle", "chuyển sáng tối", "circle reveal", "hiệu ứng đổi giao diện".
- `docs-site-macos` § Theme Toggle trỏ vào đây thay vì nhúng lại toàn bộ CSS/JS.
- KHÔNG dùng để chọn xem trang có BẮT BUỘC phải có toggle hay không — đó là luật `html-theme-toggle-required` (`/fdk` § Rules), skill này chỉ lo PHẦN "chuyển thế nào" sau khi đã quyết có toggle.

## Contract (markup tối thiểu)

Cần một `<nav>` (hoặc container tương đương) chứa link điều hướng — nút gạt tự chèn vào cuối bằng JS, không cần viết tay markup:

```html
<nav>…link điều hướng…</nav>
```

JS tự tạo `.theme-row > .lbl + .theme-switch`, đặt `data-theme` lên `<html>`, lưu `localStorage`. Không đổi tên các class này — script nghiệm thu (`scripts/verify-theme-motion.mjs`) bám đúng vào chúng.

## 1. Nút gạt (switch)

Hàng footer **dính đáy** container cha (`position:sticky`), nhãn trái + switch phải, vách ngăn mảnh phía trên — KHÔNG chip icon rải góc:

```css
:root{--nav-pad-y:18px} /* nguồn chân lý duy nhất cho padding dọc của container cha */
.theme-row{position:sticky;bottom:calc(-1 * var(--nav-pad-y));margin-top:auto;display:flex;
  align-items:center;justify-content:space-between;padding:11px 16px;
  border-top:1px solid rgba(30,90,170,.14);background:transparent}
.theme-switch .track{display:inline-block;position:relative;width:50px;height:26px;border-radius:999px;…}
.theme-switch .track::before{content:'☀️';left:6px;…} .theme-switch .track::after{content:'🌙';right:6px;…}
.theme-switch .knob{position:absolute;top:2px;left:2px;width:20px;height:20px;border-radius:50%;background:#fff;transition:left .18s}
.theme-switch.on .knob{left:26px} .theme-switch.on .track{background:…dark…}
```

⚠️ **`.theme-row` PHẢI `background:transparent`, KHÔNG `backdrop-filter` riêng (bài học 160926, 2 vòng sai đã đo được).** `.theme-row` là con trực tiếp của container cha (`nav`), không phải content-card độc lập:
- **Sai lần 1 — fill riêng:** cho nó một màu nền phẳng của riêng nó (kể cả gradient "gần giống" nav) luôn lộ thành khối tách rời khỏi lớp kính phía sau — feedback thật: *"div này cho transparency luôn luôn đi chứ"*.
- **Sai lần 2 — `background:inherit`:** tưởng đã sửa, nhưng `inherit` chỉ copy CÔNG THỨC gradient rồi vẽ LẠI trên hộp nhỏ riêng của `.theme-row` — không phải lộ đúng pixel cha đã vẽ, vẫn lệch tông.
- **Sai lần 3 — giữ `backdrop-filter:blur` "cho chắc":** dù nền đã transparent thật (đo `rgba(0,0,0,0)`), một lớp blur RIÊNG chồng lên đúng vùng cha-đã-tự-blur tạo dải "kính mờ kép" nhìn như khối riêng dù 0 màu — bắt được bằng ảnh chụp thật, không phải suy đoán.
- **Đúng:** `background:transparent`, KHÔNG `backdrop-filter` trên `.theme-row`. Để lộ thẳng pixel cha đã render, không tự vẽ/tự blur gì thêm.

## 2. Chống FOUC

```html
<script>(function(){try{var t=localStorage.getItem("<tên-trang>-theme");
if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}catch(e){}})();</script>
```

## 3. Palette dark-mode — trung tính kiểu thị trường, KHÔNG navy-tinted (bài học 160926)

Bản đầu dùng nền `#0c0f16` + border `rgba(120,160,220,.18)` (xanh navy đậm) — feedback thật: *"chọn màu dark mode... vẫn dở tệ, chọn lại bộ màu theo thị trường đi"*. Tham chiếu 3 sản phẩm dark-mode được đánh giá tốt nhất hiện nay (GitHub Dark, Vercel/Geist, Linear): nền TRUNG TÍNH gần đen (không ngả xanh), viền TRẮNG TRONG SUỐT (không viền màu bão hoà), giữ ĐÚNG MỘT accent màu (ở đây là xanh hệ thống Apple `#0a84ff`) làm điểm nhấn — không rải màu bão hoà vào chrome/border:

| Token | Trước (navy-tinted, SAI) | Sau (trung tính, thị trường) |
|---|---|---|
| nền gốc | `#0c0f16` | `#09090b` |
| gradient nền, stop 2 | `#0a0d13` / `#0d1017` | `#08080a` |
| `--glass2` (card) | `rgba(30,34,44,.72)` | `rgba(32,32,36,.72)` |
| `--glass3` (bảng/data) | `rgba(36,40,52,.9)` | `rgba(39,39,44,.9)` |
| `--border` | `rgba(120,160,220,.18)` (xanh bão hoà) | `rgba(255,255,255,.10)` (trắng trong suốt — đúng cách GitHub/Vercel/Linear vẽ viền trên nền tối) |
| `--t1` (chữ chính) | `#e7e9ee` / `#e8eaf0` | `#f4f4f5` |
| `--t2` (chữ phụ) | `#9aa2b1` (xám-xanh) | `#a1a1aa` (xám trung tính) |
| nav/container cha | `rgba(18,21,28,.82)` hay gradient `rgba(24,30,44,…)` | `rgba(20,20,23,.82)` hay gradient `rgba(28,28,31,…)` |
| toggle track (on) | `#2b3040→#191d27` / `rgba(60,70,110,.55)` | `#2c2c30→#19191b` / `rgba(58,58,64,.6)` |
| màu nền overlay chuyển mode | `#0c0f16` | `#09090b` |

Accent (`#0a84ff`, tag 6-màu Apple secondary) **giữ nguyên** — không phải phần "dở tệ", đó là điểm nhấn có chủ đích. Chỉ nền/viền/chữ trung tính là phần cần trung tính hoá.

## 4. Circle-reveal + crest-glow (REQUIRED) — tỏa từ CON TRỎ, kẹp trong biên nút

**Nguồn gốc điểm tỏa: vị trí con trỏ chuột lúc bấm, kẹp (clamp) trong biên nút** (bài học 160926 — trước tỏa từ tâm nút, cố định): dùng toạ độ click thật (`e.clientX/clientY`), giới hạn trong `getBoundingClientRect()` của nút — bấm lệch về mép trái/phải nút thì điểm tỏa theo đúng mép đó, không vọt ra ngoài nút. Phím Enter/Space (không có toạ độ chuột) rơi về tâm nút.

**KHÔNG dùng nhiều vòng gợn độc lập đuổi theo dòng chính (bài học 160926, thiết kế ĐẦU bị bỏ).** Bản đầu spawn 3 `<div>` viền tròn riêng, tỏa NHANH HƠN + XA HƠN dòng chính bằng `backdrop-filter:blur` riêng từng cái — feedback thật: *"hiệu ứng lag quá... sóng bay nhanh hơn cả khối trắng đằng sau? không phải tạo hiệu ứng trên khối trắng đằng sau mới đúng à"*. Hai lỗi chồng nhau:
- **Lag thật:** `backdrop-filter:blur` trên nhiều `<div>` cỡ lớn (đường kính > 2× bán kính phủ màn hình) mỗi frame là cực tốn GPU — không phải cảm giác, là chi phí render thật.
- **Sai concept:** gợn tách rời dòng chính, chạy theo timeline riêng (`setTimeout` + `el.animate()` độc lập) → không đồng bộ hoàn hảo, đúng như user quan sát "sóng bay nhanh hơn khối trắng".

**Đúng: `filter:drop-shadow(...)` nhiều lớp NGAY TRÊN chính phần tử dòng chính** — `drop-shadow` vẽ theo đúng RÌA đã bị `clip-path` cắt (khác `box-shadow`, vốn vẽ theo hộp chữ nhật, không theo hình dạng đã clip). Vì là filter trên CÙNG MỘT phần tử, CÙNG MỘT animation — rìa sáng tự động bám đúng dòng chính mỗi frame, không cần đồng bộ, không cần phần tử phụ, không cần `backdrop-filter`:

```css
.theme-reveal{position:fixed;inset:0;z-index:300;pointer-events:none;will-change:clip-path;
  filter:
    drop-shadow(0 0 1px rgba(255,255,255,.95))
    drop-shadow(0 0 5px rgba(255,255,255,.45))
    drop-shadow(0 0 14px var(--reveal-tint,rgba(10,132,255,.35)))}
/* duration/easing: xem §4 khối JS bên dưới + "bài học easing 160926 (v3)" */
```

Ba lớp `drop-shadow` xếp từ rìa sáng sắc nét (viền nước) → quầng trắng mềm (khúc xạ) → quầng màu rộng theo `--reveal-tint` (MODE ĐÍCH) — đọc như một gợn sóng/kính lỏng thật đang cuốn theo rìa nước dâng, không phải sóng bay tách rời.

```js
(function(){var K='<tên-trang>-theme',d=document.documentElement,nav=document.querySelector('nav');if(!nav)return;
function isDark(){var t=d.getAttribute('data-theme');return t?t==='dark':matchMedia('(prefers-color-scheme: dark)').matches}
var sw=document.createElement('div');sw.className='theme-switch';sw.setAttribute('role','switch');sw.setAttribute('tabindex','0');
sw.innerHTML='<span class="track"><span class="knob"></span></span>';
var row=document.createElement('div');row.className='theme-row';
var lb=document.createElement('span');lb.className='lbl';lb.textContent='Giao diện';row.appendChild(lb);row.appendChild(sw);nav.appendChild(row);
function paint(){var dk=isDark();sw.classList.toggle('on',dk);sw.setAttribute('aria-checked',dk?'true':'false');
  sw.setAttribute('aria-label',dk?'Nút gạt giao diện: đang tối — gạt sang sáng':'Nút gạt giao diện: đang sáng — gạt sang tối')}
var busy=false;
function commit(next){d.setAttribute('data-theme',next);try{localStorage.setItem(K,next)}catch(e){}paint()}
function flip(e){
  if(busy)return; var next=isDark()?'light':'dark';
  var r=sw.getBoundingClientRect();
  // điểm tỏa = con trỏ chuột lúc bấm, KẸP trong biên nút; Enter/Space (không toạ độ) -> tâm nút
  var x=(e&&typeof e.clientX==='number')?Math.min(Math.max(e.clientX,r.left),r.right):r.left+r.width/2;
  var y=(e&&typeof e.clientY==='number')?Math.min(Math.max(e.clientY,r.top),r.bottom):r.top+r.height/2;
  var reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  // <tên-trang>: đổi 2 màu + 2 tint này khớp nền light/dark thật của trang (xem §3 Palette)
  var bg=next==='dark'?'#09090b':'#f7fbff';
  var tint=next==='dark'?'rgba(90,168,255,.28)':'rgba(10,132,255,.20)';
  var canAnimate='animate' in document.createElement('div');
  busy=true;
  var el=document.createElement('div');el.className='theme-reveal';
  el.style.cssText='position:fixed;inset:0;z-index:300;pointer-events:none;will-change:clip-path;background:'+bg;
  el.style.setProperty('--reveal-tint',tint);
  document.body.appendChild(el);
  if(reduced||!canAnimate){
    // fallback bắt buộc (FR-007, chuẩn motion.md của hallmark): KHÔNG bỏ hẳn overlay — collapse
    // về crossfade ngắn ≤150ms thay vì hiệu ứng spatial full-screen, KHÔNG có crest-glow.
    el.style.cssText+=';opacity:0;transition:opacity .075s linear';
    requestAnimationFrame(function(){el.style.opacity='1'});
    setTimeout(function(){commit(next);el.style.opacity='0';setTimeout(function(){el.remove();busy=false},90)},90);
    return;
  }
  var maxR=Math.hypot(Math.max(x,innerWidth-x),Math.max(y,innerHeight-y));
  // cấu trúc TỈ LỆ (bài học 160926 v4): chỉnh MỘT số TOTAL_MS, grow/fadeOut tự chia theo tỉ lệ cố định —
  // không sửa 2 con số rời rạc mỗi lần user đổi ý về tốc độ.
  var TOTAL_MS=20,GROW_RATIO=.8,growMs=Math.round(TOTAL_MS*GROW_RATIO),fadeMs=TOTAL_MS-growMs;
  var grow=el.animate([
    {clipPath:'circle(0px at '+x+'px '+y+'px)'},
    {clipPath:'circle('+maxR+'px at '+x+'px '+y+'px)'}
  ],{duration:growMs,easing:'cubic-bezier(.55,0,1,.45)',fill:'forwards'}); // ease-in tăng tốc (bài học 160926 v3): càng gần lúc phủ hết càng nhanh
  grow.onfinish=function(){
    commit(next); // đổi data-theme ĐÚNG lúc phủ hết, trước fade
    var fadeOut=el.animate([{opacity:1},{opacity:0}],{duration:fadeMs,easing:'ease-out',fill:'forwards'});
    fadeOut.onfinish=function(){el.remove();busy=false};
  };
}
sw.addEventListener('click',flip); // click event tự mang clientX/clientY
sw.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();flip(e)}});
paint()})();
```

⚠️ **Bài học easing 160926 (v1, đã thay ở v2 bên dưới):** `cubic-bezier(.3,0,.1,1)` (thiết kế đầu) co gần hết chuyển động trong ~20% thời lượng đầu rồi phẳng lì suốt phần còn lại — ngược hẳn ý định "chậm đầu, nhanh cuối". Đo bằng ảnh chụp thật ở nhiều mốc thời gian mới lộ ra (ở 130/560ms tức 23% thời lượng, overlay đã phủ gần hết màn hình). Đổi sang `cubic-bezier(.42,0,1,1)` (ease-in chuẩn CSS, 560ms) trải đều suốt duration — nhưng vẫn CHẬM ở khoảnh khắc ngay sau click.

⚠️ **Bài học easing 160926 (v2, đã thay ở v3 bên dưới):** feedback thật sau khi ship v1: *"vẫn làm nó có cảm giác bị delay khựng"*. Root cause KHÔNG phải jank — là ease-in (dù trải đều) vẫn có đạo hàm ~0 ngay tại t=0, nên 100-150ms đầu tiên sau click gần như không thấy overlay nhúc nhích → đọc y hệt "app đứng hình". Đổi sang `cubic-bezier(.16,1,.3,1)` (ease-out expo) + cắt `duration` 560→280ms (grow) và 180→70ms (fadeOut) — tổng cảm nhận 740ms → 350ms.

⚠️ **Bài học easing 160926 (v3):** feedback tiếp: *"xong trong nửa giây thôi vẫn lâu quá"* + *"càng gần hết giờ càng nhanh"*. Hai tín hiệu: (1) 350ms VẪN bị coi là chậm — user không có ngưỡng "đủ nhanh" cố định, cắt tới khi còn đọc được là một hình tròn lan ra (không phải flash) thì dừng; (2) hình dạng đường cong mong muốn là TĂNG TỐC dần tới lúc phủ hết, không phải ease-out (chậm dần cuối, tạo cảm giác "còn dư việc" ở đoạn cuối). Vì duration đã cực ngắn, phần "chậm đầu" của ease-in không còn đủ thời gian để bị cảm nhận như delay nữa — mâu thuẫn v1-vs-v2 chỉ tồn tại khi duration còn dài. Đổi easing sang `cubic-bezier(.55,0,1,.45)` (ease-in-quad, tăng tốc đều, kết thúc ở tốc độ cao nhất). **Quy luật rút ra:** duration càng ngắn thì hình dạng easing càng ít quan trọng — ưu tiên cắt duration trước, chỉnh easing sau.

⚠️ **Bài học 160926 (v4, cấu trúc):** user tiếp tục ép duration xuống dần (350→200→50→20ms) qua nhiều lượt — feedback: *"cấu trúc tỉ lệ thôi nhập tối đa time vào thì tự chia lại duration"*. Thay vì 2 số `duration` rời rạc phải sửa tay mỗi lần, khai MỘT `TOTAL_MS` + `GROW_RATIO` cố định (0.8), grow/fadeOut tự tính theo tỉ lệ — đổi tốc độ chỉ sửa một số. Ở TOTAL_MS=20 (growMs=16, fadeMs=4) vẫn PASS ổn định qua script nghiệm thu (§ bên dưới) — nhưng đây là ranh giới: dưới ~20ms tổng, hiệu ứng "hình tròn lan ra" gần như không còn phân biệt được với việc đổi màu tức thời (flash) bằng mắt thường; hạ thêm chỉ còn ý nghĩa lý thuyết.

⚠️ **Bài học 160926 (v5, chốt):** sau v4 (TOTAL_MS=20) vẫn bị chê *"vẫn lâu quá"* → user chốt *"làm instance [instant] luôn đi"*. Với hiệu ứng phản hồi trực tiếp theo click, có một NGƯỠNG NGƯỜI DÙNG THỰC không cố định trước được bằng số — an toàn nhất là hỏi trước khi đầu tư thiết kế reveal cầu kỳ (overlay/clip-path/crest-glow) cho một nút bấm tần suất cao như theme-toggle, thay vì mặc định luôn có hiệu ứng. Khi user đòi "instant": bỏ HẲN overlay + `el.animate`, `flip()` chỉ còn `commit(next)` — không lùi về TOTAL_MS nhỏ dần nữa, xoá luôn CSS `.theme-reveal` nếu không còn phần tử nào tạo class đó. Xem `llmwiki/html/overstack.html` làm ví dụ tham chiếu. Circle-reveal trong skill này vẫn là pattern MẶC ĐỊNH tốt cho landing/showcase ít click — không áp dụng cứng nhắc cho mọi nơi.

⚠️ **Bẫy khi viết script nghiệm thu cho duration cực ngắn:** `await animation.finished` (Promise) có thể **resolve TRƯỚC** event `'finish'` — mà `onfinish` (nơi code thật gọi `commit()`) lắng nghe qua event, không qua promise. Đo bằng browser thật (`getAnimations()[0].playState`) mới lộ ra: promise resolve xong mà `data-theme` VẪN chưa đổi. Test phải đợi đúng bằng `addEventListener('finish', ...)` (hoặc kiểm `playState==='finished'` trước) mới đồng bộ đúng thời điểm với `onfinish` thật — xem `scripts/verify-theme-motion.mjs`. Bài học chung: KHÔNG hardcode mốc ms để đoán "animation xong chưa" — dùng API/event thật, càng đúng ở mọi duration.

Trang không có sidebar (landing một cột)? Đặt cùng hàng footer của trang, vẫn là NÚT GẠT có nhãn — tuyệt đối không quay lại chip icon trôi nổi ở góc.

## Nghiệm thu tự động

```bash
npm install --no-save @playwright/test   # cài tạm, không cần lưu vào package.json
node skills/dark-mode-maker/scripts/verify-theme-motion.mjs <file.html>
```

Assert: overlay `.theme-reveal` xuất hiện đúng toạ độ con trỏ (kẹp trong biên nút) + màu nền MODE ĐÍCH; `data-theme`/`localStorage` đổi SAU khi phủ hết viewport; overlay tự gỡ khỏi DOM sau fade; nhánh `prefers-reduced-motion: reduce` không có `clip-path` lan (crossfade phẳng, không spatial motion).

## Rules
- KHÔNG spawn phần tử phụ độc lập cho hiệu ứng gợn — dùng `filter:drop-shadow` nhiều lớp trên CHÍNH `.theme-reveal` (xem §4, lý do lag + lệch đồng bộ đã đo được).
- KHÔNG `backdrop-filter` trên `.theme-row` (xem §1) và KHÔNG override `background` riêng cho nó ở khối dark-mode.
- Điểm tỏa LUÔN kẹp trong biên nút (`getBoundingClientRect()` của `.theme-switch`) — không bao giờ vọt ra ngoài dù con trỏ đang ở đâu trên màn hình lúc bấm.
- Palette dark-mode trung tính (§3) — không thêm màu bão hoà vào nền/viền/chữ nền tảng; accent giữ nguyên một màu duy nhất.
- `docs-site-macos` (và mọi skill sinh HTML khác cần toggle) trỏ VÀO skill này thay vì nhúng lại CSS/JS — một nguồn, sửa một chỗ.
