---
type: source
title: "Luật slop UI nào kiểm được thuần bằng code — phân loại 58 gate slop-test + luật hai cổng hiện có thành tĩnh · chạy thật · cần mắt, kèm phân tích luật bo tròn không thêm cạnh màu"
status: recorded
tags: [slop, slop-test, frontend-antipattern, html-visual-gate, rounded-edge, research]
timestamp: 2026-09-21
id: 210926-slop-code-checkable
---

# Luật slop nào kiểm được thuần bằng code (21/09/2026)

Câu hỏi của user ngày 21/09/2026: trong bộ kiểm slop hiện có, phần nào kiểm được thuần bằng code (không cần LLM, không cần mắt người), đặc biệt là luật "bo tròn thì không thêm cạnh màu". Trang này trả lời bằng cách đọc từng gate trong `skills/hallmark/references/slop-test.md` và từng luật đang chạy trong hai cổng, rồi xếp mỗi dòng vào đúng một cột.

Viết tắt dùng trong bảng:

- **FA** = `fdk/tools/frontend-antipattern.py` (cổng tĩnh: regex và tách CSS theo `}` qua hàm `css_rules`, dòng 291-299).
- **VG** = `fdk/tools/html-visual-gate.mjs` (cổng chạy thật: Playwright, đo ở cả sáng và tối, khung 1360×900, offline).
- Ba cột: **tĩnh** = đọc chuỗi HTML/CSS là đủ · **chạy thật** = cần `getComputedStyle`, hình học `getBoundingClientRect`, CSSOM hoặc điểm ảnh trong trình duyệt · **cần mắt** = kết luận phụ thuộc brief, ngữ nghĩa nội dung, hoặc so với output trước, code chỉ thu được tín hiệu phụ.
- Quy ước xếp cột: mỗi gate xếp vào cổng cho kết quả ĐÚNG nhất. Ngoại lệ theo genre không tự động đẩy gate sang "cần mắt", vì genre là tham số đầu vào (đọc được từ stamp), không phải phán đoán.

R22 `html-slop` (`harness/policy.yaml` dòng 181-188) hiện chỉ cưỡng chế ba dấu hiệu qua FA: sọc viền màu một cạnh, gradient-text, thiếu chế độ tối. Các luật còn lại của FA và toàn bộ VG chạy qua medic và test, không chặn lúc ghi.

## 1. Bảng phân loại

### 1a. Từng gate của slop-test.md

| Gate | Nhóm | Cột | Cách đo cụ thể (thuộc tính · ngưỡng) | Đã có luật chưa | Rủi ro báo giả |
|---|---|---|---|---|---|
| Tự chấm 6 trục A–F | Pre-emit | cần mắt | Điểm 1–5 do model tự chấm; code chỉ kiểm được stamp `/* Hallmark · pre-emit critique: … */` có mặt | Chưa | Không áp dụng |
| 1 Display font Inter/Roboto/Open Sans/Poppins/Lato/system | Visual | chạy thật | `getComputedStyle(h1 hoặc phần tử cỡ chữ lớn nhất).fontFamily`, token đầu nằm trong danh sách cấm | Chưa. FA cố ý loại (FA:17-18, FA:74-76) vì báo giả trên seq.html | Trung bình: trang kỹ thuật dùng system font hợp lệ theo chính quyết định ở FA:74 |
| 2a Gradient text (`background-clip:text`) | Visual | tĩnh | Regex `(-webkit-)?background-clip:\s*text` trong `<style>` và `style=""` | Có: FA:79-80, FA:432-436 (FAIL); VG bỏ qua phần tử này khi đo contrast (VG:58) | Thấp: chỉ quét CSS, không quét văn xuôi (FA:428-429) |
| 2b Gradient tím→xanh / cyan→magenta ở nền | Visual | tĩnh | Tách stop của `linear/radial-gradient`, đổi sang hue; FAIL khi hai stop nằm ở dải hue 190–330° cách nhau ≥ 40° | Chưa | Trung bình: brand tím-xanh hợp lệ; genre atmospheric cho radial ở nền |
| 3 Lưới 3 cột bằng nhau, icon trên tiêu đề | Visual | chạy thật | Cha có đúng 3 con cùng rộng (lệch < 2px), mỗi con có `svg/img` nằm trên `h2–h4` đầu tiên | Chưa (FA:74 xếp vào genre-scoped) | Cao: lưới 3 thẻ có icon rất hay hợp lệ |
| 4 Card lồng card | Visual | chạy thật | Phần tử "boxy" (viền đủ 4 cạnh hoặc nền + bóng, dùng lại hàm `boxy` VG:70) chứa hậu duệ boxy | Chưa | Cao: panel chứa thẻ, khung code trong thẻ là bố cục hợp lệ |
| 5 Sọc viền màu dày một cạnh | Visual | chạy thật | Xem mục 2; cascade đã giải xong mới đo đúng | Có một phần: FA `side-stripe` FA:331-352; VG stripe VG:94-98 | Thấp trên phần đang bắt; bỏ sót nhiều (mục 2) |
| 6 Hero căn giữa toàn bộ | Visual | chạy thật | Section đầu có `min-height ≥ 100vh` và tâm ngang của eyebrow/tiêu đề/lede/CTA lệch tâm container < 2px | Chưa | Trung bình: genre atmospheric/playful được phép; nhận diện hero là heuristic |
| 7 Nền `#000`/`#fff` thuần | Visual | tĩnh | Regex `#000(000)?`, `#fff(fff)?`, `black`, `white` trong khai báo màu ở `:root`/`html`/`body` | Chưa (FA:17-18 loại có chủ ý) | Cao: genre modern-minimal cho phép `#fff` |
| 8 Tái dùng cấu trúc (template AI hoặc cùng macrostructure lần trước) | Structural | cần mắt | Code chỉ so được chuỗi stamp với `.hallmark/log.json` khi cả hai tồn tại; "Hero → 3 features → CTA" là phán đoán ngữ nghĩa | Chưa | Không áp dụng |
| 9 Mọi section cách nhau bằng khoảng trắng đều, không đổi nhịp | Structural | chạy thật | Khoảng cách dọc giữa các `section` bằng nhau (lệch < 2px) VÀ không section nào đổi nền/viền | Chưa | Cao: đo được nhưng "đều" chưa chắc là lỗi |
| 10 `transition: all` | Micro | tĩnh | Regex `transition(-property)?\s*:\s*all\b` và class `transition-all` | Chưa | Thấp |
| 11 Hover-scale đồng loạt | Micro | tĩnh | Đếm selector `:hover` có `transform: scale(`, hoặc class `hover:scale-`; FAIL khi ≥ 3 selector không liên quan | Chưa | Trung bình: "không liên quan" khó định nghĩa bằng selector |
| 12 Easing nảy trên trạng thái UI | Micro | tĩnh | `cubic-bezier(x1,y1,x2,y2)` có `y1` hoặc `y2` ngoài [0,1] | Chưa | Trung bình: tương tác vật lý được phép, code không phân biệt được |
| 13 Nhiều hiệu ứng hover cùng lúc | Micro | tĩnh | Một luật `:hover` đổi ≥ 3 nhóm trong {transform, box-shadow, color/background, filter} | Chưa | Trung bình: tách theo luật, không gộp cascade nên có thể sót hoặc thừa |
| 14 Animate width/height/top/left/margin/padding | Micro | tĩnh | `@keyframes` chứa các thuộc tính đó, hoặc `transition(-property)` liệt kê chúng | Chưa | Trung bình: accordion animate `height` là cách làm phổ biến |
| 15 Focus ring hiện dần | Micro | tĩnh | Luật `:focus`/`:focus-visible` đổi `outline`/`box-shadow` trong khi `transition` của cùng selector gồm `outline`/`box-shadow`/`all` | Chưa | Trung bình: `transition: box-shadow` đặt cho hover cũng vô tình làm focus hiện dần |
| 16 Toast ăn mừng hành động đã thấy được | Micro | cần mắt | Cần biết hiệu ứng của hành động có nhìn thấy hay không | Chưa | Không áp dụng |
| 17 Tooltip: độ trễ hover bằng độ trễ focus | Micro | chạy thật | Hover rồi focus cùng một trigger, đo thời điểm tooltip hiện; hover cần 800–1000 ms, focus 0 ms | Chưa | Cao: nhận diện phần tử tooltip là heuristic |
| 18 Nội dung tự xoay không dừng khi hover/focus | Micro | chạy thật | MutationObserver 5 s không tương tác thấy DOM đổi theo chu kỳ; hover rồi đo tiếp, vẫn đổi thì FAIL | Chưa | Trung bình: đồng hồ, bộ đếm sống cũng đổi DOM |
| 19 Tên mẫu "Jane Doe", cliché Acme/Nexus/Seamless/Unleash | Micro | tĩnh | Regex trên văn bản đã bỏ thẻ | Chưa | Trung bình: tài liệu nói VỀ ví dụ vẫn nhắc các tên này |
| 20 Thiếu stamp macrostructure | Variety | tĩnh | Regex `/\* Hallmark · macrostructure:` trong CSS | Chưa | Cao trên trang framework (không do hallmark sinh); chỉ nên chạy trên output hallmark |
| 21 Rơi về Specimen khi brief không đòi | Variety | cần mắt | Phụ thuộc brief | Chưa | Không áp dụng |
| 22 Neutral có chroma 0 | Impl | tĩnh | Regex `oklch\(\s*[\d.]+%?\s+0(\.0+)?\s` trong token nền/bề mặt | Chưa | Trung bình: genre modern-minimal cho phép |
| 23 Accent phủ > 5% viewport | Impl | chạy thật | Chụp viewport, đếm điểm ảnh gần màu `--color-accent` (ΔE nhỏ) chia diện tích | Chưa | Trung bình: phải biết token accent; atmospheric cho tới ~20% |
| 24 Spacing lệch thang (không bội 4px, không `--space-*`) | Impl | tĩnh | `padding/margin/gap` có giá trị px không chia hết cho 4 và không là `var(--space-…)` | Chưa | Trung bình: 1–2px bù viền là hợp lệ |
| 25 Độ rộng đoạn văn ngoài 45–75ch | Impl | chạy thật | `p` ≥ 200 ký tự: bề rộng hộp chia bề rộng glyph `0` của font đó | Chưa | Trung bình: đoạn trong thẻ hẹp, bảng |
| 26 Phần tử tương tác thiếu `:focus-visible`/`:active`/`:disabled` | Impl | tĩnh | Trang có `button/a/input` mà CSS không có selector nào chứa từng trạng thái | Chưa | Thấp ở mức trang; mức từng phần tử cần CSSOM |
| 27 Motion không có `prefers-reduced-motion` | Impl | tĩnh | Có `@keyframes`, `animation:` khác none, hoặc transition có `transform`, mà không có `@media (prefers-reduced-motion` | Chưa | Thấp (xem mục 3) |
| 28 Video: autoplay có tiếng, thiếu poster, LCP lazy | Hero | tĩnh | `<video autoplay>` thiếu `muted` hoặc `poster`; ảnh/video đầu trang có `loading="lazy"` | Chưa | Thấp; hiếm gặp ở trang framework |
| 29 Nền trừu tượng nhiều màu/lớn/mesh động | Hero | cần mắt | Code bắt được `animation` trên `background-position` của `body`, nhưng "nền trừu tượng" là phán đoán | Chưa | Không áp dụng |
| 30a Trộn ≥ 2 thư viện icon | Hero | tĩnh | Đếm họ dấu vết: class `material-icons`, `fa-`, `lucide`, `ph-`, thuộc tính SVG Heroicons, CDN tương ứng | Chưa | Trung bình: SVG inline tự vẽ không có dấu vết |
| 30b Emoji làm icon thẻ/bước/gói giá | Hero | tĩnh | Ký tự `\p{Extended_Pictographic}` là nội dung đầu tiên của heading hoặc con đầu của thẻ | Chưa | Trung bình: emoji trong bảng trạng thái (✅) hợp lệ ở tài liệu |
| 31 Mặc định Lottie | Hero | cần mắt | Có mặt Lottie thì tĩnh bắt được; "SVG tay đã đủ" là phán đoán | Chưa | Không áp dụng |
| 32 Cùng archetype mà không đổi knob | Diversification | cần mắt | Cần `.hallmark/log.json` và brief | Chưa | Không áp dụng |
| 33 SVG/canvas/hình trang trí thiếu `aria-label`/`aria-hidden` | Diversification | tĩnh | `<svg>`, `<canvas>` thiếu `aria-hidden="true"` và thiếu `aria-label`/`role+title` | Có một phần: FA:266-284 (WARN) nhưng miễn SVG thân < 400B (FA:107, FA:266), không soi `<canvas>`/div vẽ CSS | Thấp |
| 34 Cuộn ngang ở 320–1920px | Layout | chạy thật | Ở 320/375/414/768/1360: `documentElement.scrollWidth > clientWidth + 1` | Chưa | Thấp |
| 35 Vị trí dải highlighter/gạch chân | Layout | cần mắt | Gate tự ghi "check là visual"; code chỉ bắt được `text-underline-offset ≥ 5px` | Chưa | Không áp dụng |
| 36 Hàng tương tác không căn giữa dọc | Layout | chạy thật | Flex row trong `nav/header/footer`: tâm dọc các con lệch nhau > 2px | Chưa | Trung bình: hàng cố ý căn baseline |
| 37 > 3 họ font | Typography | chạy thật | Tập token đầu của `fontFamily` trên mọi phần tử có chữ, bỏ `pre/code/kbd/samp`; > 3 thì FAIL | Chưa (html-font-lint chỉ kiểm có font nhúng, không đếm họ) | Thấp |
| 38 Font outlier dùng > 2 chỗ | Typography | chạy thật | Đếm phần tử dùng họ font thứ ba | Chưa | Trung bình: "chỗ" (slot) không định nghĩa được bằng DOM |
| 38a Heading/display in nghiêng | Typography | chạy thật | `fontStyle` italic/oblique trên `h1–h6` hoặc phần tử có chữ cỡ ≥ 24px | Có một phần: FA:82-83, FA:437-441 chỉ bắt `h1–h6` và `<em>/<i>` ngay sau text đầu | Thấp |
| 39a Input đổi border-width giữa trạng thái | Input | chạy thật | Focus bằng bàn phím, so `borderTopWidth` và `offsetHeight` trước/sau | Chưa | Thấp |
| 39b Focus ring làm bằng border thay outline | Input | tĩnh | Luật `input:focus(-visible)` đổi `border` mà không có `outline` | Chưa | Trung bình: `box-shadow` ring cũng là cách hợp lệ |
| 39c Input cao khác nút cạnh nó | Input | chạy thật | Trong cùng `form`/hàng flex: `|h(input) − h(button)| > 2px` | Chưa | Thấp–trung bình |
| 39d Ô helper co lại khi rỗng | Input | cần mắt | Chưa rõ cách nhận diện ô helper bằng DOM | Chưa | Không áp dụng |
| 39e Disabled chỉ bằng opacity | Input | chạy thật | Phần tử `:disabled`/`aria-disabled`: `cursor` khác `not-allowed` | Chưa | Thấp |
| 40 Contrast theo ngưỡng WCAG | Contrast | chạy thật | Ratio 4.5:1, chữ ≥ 24px hoặc ≥ 18.66px đậm 3:1 | Có: VG:47-63, xác minh điểm ảnh VG:118-128 | Thấp: miễn disabled và `data-ovs-deemphasized` (VG:49-55); ngưỡng icon/focus ring 3:1 CHƯA đo |
| 41a Chữ nút ≈ nền nút | Contrast | chạy thật | Trường hợp riêng của 40 (ratio ~1:1) | Có gián tiếp qua VG contrast | Thấp |
| 41b Thiếu hoặc không dùng `--color-accent-ink` | Contrast | tĩnh | Có `--color-accent` làm nền cho phần tử có chữ mà không khai `--color-accent-ink` | Chưa | Cao: quy ước token riêng của hallmark |
| 41c Section tối mà chữ vẫn tối | Contrast | chạy thật | Trường hợp riêng của 40 | Có gián tiếp qua VG contrast | Thấp |
| 42 Nav mặc định AI | Chrome | chạy thật | Logo trái + 4–5 link + nút phải, full-width, viền dưới 1px, nền trắng; miễn khi chỉ có 2 đích (đếm được) | Chưa | Trung bình |
| 43 Footer mặc định AI | Chrome | chạy thật | 4 cột link + hàng icon mạng xã hội + copyright + viền trên 1px | Chưa | Cao: miễn "docs root thật" là phán đoán |
| 44a Hero: padding dưới ≥ 1.3× padding trên | Chrome | chạy thật | `paddingBottom / paddingTop` của section đầu | Chưa | Trung bình: nhận diện hero |
| 44b Hero vừa màn 1280×800 | Chrome | chạy thật | Ở 1280×800: đáy CTA đầu tiên trong hero ≤ 800px | Chưa | Trung bình: nhận diện CTA; trang art-directed được miễn |
| 45 Trang trí không có mục đích | Chrome | cần mắt | Cần ngữ nghĩa nội dung | Chưa | Không áp dụng |
| 46 Số liệu bịa | Honest copy | cần mắt | Chỉ user biết số có nguồn không; code bắt được mẫu quảng cáo | Có heuristic: FA:88-92, FA:447-452 (WARN) | Trung bình (đúng lý do để WARN) |
| 47 Chrome vẽ lại (browser/phone/IDE/terminal) | Re-drawn chrome | tĩnh | ≥ 3 màu traffic-light cố định trong CSS | Có một phần: FA:85-86, FA:442-446 (WARN); khung điện thoại/IDE không bắt được | Thấp trên phần bắt; bỏ sót nhiều |
| 48 Màu/font ngoài token | Token | tĩnh | Literal `#hex/rgb/hsl/oklch` hoặc `font-family` nằm ngoài khối `:root`/`[data-theme]` | Chưa | Cao trên trang framework hiện tại (literal có khắp nơi) |
| 49 Chữ bấm được xuống 2 dòng | Responsive | chạy thật | Xem mục 3 `clickable-wrap` | Chưa | Thấp |
| 50 Track `1fr` chứa ảnh | Mobile | chạy thật | CSSOM: luật có `grid-template-columns` chứa `1fr` không bọc `minmax(0,…)`, `el.matches(selectorText)` và `el.querySelector('img,picture')` | Chưa | Thấp |
| 51 Display heading thiếu `overflow-wrap:anywhere` | Mobile | chạy thật | Phần tử cỡ chữ ≥ 32px: `overflowWrap !== 'anywhere'` | Chưa | Trung bình: heading ngắn không bao giờ tràn, gate vẫn đòi |
| 52 Section-head nhiều cột không co ở mobile | Mobile | chạy thật | Ở 375px: wrapper chứa heading có `gridTemplateColumns` > 1 track | Chưa | Thấp |
| 53 Tab radio CSS làm nhảy cuộn | Mobile | chạy thật | `input[type=radio]` có `position:absolute; top:0`; bấm label rồi so `scrollY` | Chưa | Thấp |
| 54 Eyebrow nằm cạnh heading cùng hàng | Mobile | chạy thật | Wrapper chứa heading và nhãn nhỏ (uppercase hoặc cỡ < ½ heading): hai hộp giao nhau theo trục dọc, lệch trái | Chưa | Trung bình: nhận diện eyebrow |
| 55 Display viết HOA với line-height < 1.0 | Mobile | chạy thật | Xem mục 3 `uppercase-tight-leading` | Chưa | Thấp |
| 56 Hai phần tử sticky cùng `top:0` | Mobile | chạy thật | Đếm phần tử `position: sticky` có `top: 0px`; ≥ 2 và một cái là `header/nav` | Chưa | Thấp |
| 57 Bỏ DNA đã study, quay về theme catalog | Mobile | cần mắt | Phụ thuộc hội thoại trước | Chưa | Không áp dụng |
| 58 Ô bảng/list xuống nhiều dòng | Mobile | chạy thật | Hàng `tr` cao > 1.8× trung vị chiều cao hàng do chữ xuống dòng | Chưa | Trung bình: gate đòi "dữ liệu thật", fixture giả có thể ngắn |

Đếm: **tĩnh 23 · chạy thật 34 · cần mắt 12** (tính cả dòng tách 2a/2b, 30a/30b, 39a–e, 41a–c, 44a/b và dòng tự chấm). Trong 69 dòng, chỉ 2a và 40 có luật đủ; 5, 33, 38a, 41a, 41c, 46, 47 có luật một phần.

### 1b. Luật đang chạy trong hai cổng

| Luật | Cổng | Cột | Cách đo (theo code) | Vị trí | Map gate | Rủi ro báo giả đã biết |
|---|---|---|---|---|---|---|
| ligature chưa tắt | FA | tĩnh | Có `<pre`/`<code` mà thiếu chuỗi `font-variant-ligatures:none` | FA:421-426 | ngoài slop-test | Thấp; so chuỗi chính xác nên `font-variant-ligatures: none` (có dấu cách) bị coi là thiếu |
| gradient-text | FA | tĩnh | `GRAD_TEXT` | FA:79-80, FA:432-436 | 2a | Thấp |
| italic header | FA | tĩnh | `<h_>` có `<em>/<i>` sau text không chứa thẻ; `h1–6{…font-style:italic}` | FA:82-83, FA:437-441 | 38a | Thấp; sót class tiêu đề |
| fake browser chrome | FA | tĩnh | ≥ 3 hex traffic-light khác nhau | FA:85-86, FA:442-446 | 47 | Thấp (WARN) |
| số liệu marketing | FA | tĩnh | `FAKE_METRIC` trên văn bản bỏ thẻ | FA:88-92, FA:447-452 | 46 | Trung bình (WARN) |
| side-stripe | FA | tĩnh | Xem mục 2 | FA:328-352 | 5 | `_is_neutral_color` coi tên màu, `hsl()`, `oklch()` là màu nhấn (FA:321-322) nên `oklch(0.6 0 0)` xám vẫn bị tính |
| no-dark-mode | FA | tĩnh | CSS > 400 ký tự mà không có `[data-theme=dark]`/`prefers-color-scheme: dark`/`.dark`/`[data-mode` | FA:354-363 | ngoài slop-test (luật repo) | Thấp |
| no-theme-toggle | FA | tĩnh | Có dark CSS nhưng không có id/class/aria chứa theme kèm `localStorage`/`data-theme`/`classList` | FA:356-366 | ngoài slop-test | Trung bình: heuristic tên thuộc tính |
| uppercase-misuse | FA | tĩnh | Uppercase trên h1–h4/button/.btn/.title…, hoặc uppercase thiếu `letter-spacing` | FA:306-307, FA:367-378 | gần 55 (không cùng luật) | Trung bình (WARN) |
| SVG remote ref | FA | tĩnh | `href/url(` trỏ `http(s)` trong `<svg>` | FA:100-101, FA:254-258 | ngoài slop-test | Thấp |
| SVG title/desc rỗng | FA | tĩnh | `<title>`/`<desc>` chỉ có khoảng trắng | FA:259-265 | 33 | Thấp |
| SVG thiếu role · thiếu title · title không là con đầu | FA | tĩnh | Chỉ SVG thân ≥ 400B, không `aria-hidden` | FA:266-284 | 33 | Thấp (WARN vì nợ cũ, FA:241-247) |
| neo `data-src` | FA | tĩnh | Đường dẫn/số dòng phải tồn tại | FA:119-145 | ngoài slop-test | Thấp (fail-closed có chủ ý) |
| SVG hai ô đè nhau · ô ngoài viewBox · chữ tràn ô | FA | tĩnh | Toạ độ `rect`/`text`, bề rộng chữ ước lượng 0.55 × cỡ chữ, dung sai 2px | FA:178-237 | ngoài slop-test | Trung bình ở luật chữ tràn (ước lượng, không đo glyph) |
| prose lọt `<pre>` | FA | tĩnh | Chữ Việt có dấu ở dòng không phải comment | FA:457-469 | ngoài slop-test | Trung bình (WARN) |
| contrast | VG | chạy thật | Luminance WCAG, nền cộng dồn lớp bán trong suốt, xác minh bằng điểm ảnh | VG:47-69, VG:118-128 | 40, 41a, 41c | Thấp sau bước điểm ảnh |
| tight (khối dính · padding hẹp) | VG | chạy thật | Hai khối boxy cùng cột cách < 8px; khối có chữ padding < 6px và cao > 36px | VG:70-78 | ngoài slop-test | Trung bình; chip/nút nội dòng đã miễn (VG:76) |
| overlap | VG | chạy thật | Hộp icon ≤ 72px giao hộp chữ > 2px mỗi chiều; bản SVG trong cùng `<g>` | VG:80-91 | ngoài slop-test | Thấp |
| stripe | VG | chạy thật | `::before/::after` rộng ≤ 6px cao ≥ 60% host, bão hoà > 0.35; `border-left/right` ≥ 3px và ≥ 2× các cạnh khác, bão hoà > 0.35 | VG:93-98, báo ở VG:146 | 5 | Thấp; chỉ báo từ lượt sáng (VG:146) |
| toggle | VG | chạy thật | Bấm nút khớp `TOGGLE_SEL`, luminance nền đổi ≥ 0.25, reload giữ `data-theme` | VG:104, VG:130-139, VG:147-148 | ngoài slop-test | Trung bình: selector heuristic |
| glass | VG | chạy thật | Số phần tử có `backdrop-filter` ở sáng khác 0 mà tối bằng 0 (hoặc ngược lại) | VG:99, VG:149-150 | ngoài slop-test | Thấp |
| js error | VG | chạy thật | `pageerror` khi tải | VG:109, VG:151 | ngoài slop-test | Thấp |

## 2. Luật bo tròn không thêm cạnh màu

Luật PLAN chốt (Global constraints của `210926-reading-font-slop-code-PLAN.md`): phần tử có `border-radius` > 0 mà MỘT cạnh, hoặc hai cạnh kề, có viền màu khác các cạnh còn lại thì FAIL, kể cả `blockquote`. Viền đều bốn cạnh, hoặc cạnh màu trên phần tử vuông góc, không thuộc luật này và vẫn chịu `side-stripe` cũ.

### Vì sao `side-stripe` hiện tại bỏ sót

Đọc FA:328-352 và VG:94-98:

1. **Không gộp cascade theo selector.** `css_rules` (FA:291-299) trả từng khối `{…}` riêng, `scan_slop` xét từng khối một (FA:331). Hai khối `.card{border:1px solid #ddd}` và `.card{border-left-color:#e11d48}`, hoặc `.card{…}` cộng `.card--warn{…}`, không bao giờ được nhìn chung. Ngay trong một khối, regex `_STRIPE_BORDER` (FA:303) chỉ khớp shorthand đúng thứ tự `border-left: <số>px solid <màu>`; longhand (`border-left-width` + `border-left-color`), thứ tự khác (`solid 4px red`), đơn vị `rem/em` đều lọt.
2. **Miễn `blockquote`.** FA:333 bỏ qua mọi selector chứa `blockquote`, `hr`, `table`, `td/th`. Luật mới đòi bắt cả `blockquote` khi nó bo tròn.
3. **Không xét `border-radius`.** Không có dòng nào của `scan_slop` đọc radius, nên không phân biệt được sọc trên hộp vuông (quy ước chữ in, có thể chấp nhận) với cạnh màu trên hộp bo tròn (thứ user chỉ ra).
4. **Không bắt `border:1px solid x; border-left-color: accent`.** Ngưỡng `>= 3` px (FA:336) và regex bắt buộc có độ dày, nên viền đều 1px rồi đổi màu một cạnh sang màu nhấn không bao giờ khớp. VG cũng sót: điều kiện `w >= 3 && w >= 2 * max(các cạnh khác)` (VG:98) chỉ so ĐỘ DÀY, không so MÀU; viền 1px đều nhau mà lệch màu thì qua.
5. **Inline style chỉ bắt `border-left`.** Vòng `style=""` (FA:346-349) chỉ chạy `_STRIPE_BORDER`, nên inline `box-shadow: inset 4px 0 0 …`, longhand, và `border-right`/`border-inline-start` viết dạng longhand đều lọt. (Chuỗi inline được nối vào `styles` ở FA:431 nhưng không có ngoặc `{}` nên `css_rules` không tách ra được.)
6. Phụ: cả FA lẫn VG chỉ xét cạnh trái/phải (FA:303 có thêm `inline-start`); cạnh trên/dưới màu trên thẻ bo tròn (ví dụ `border-top: 3px solid accent`) không cổng nào bắt. VG chỉ báo stripe của lượt sáng (VG:146).

### Cách đo chạy thật (đề xuất cho Task 6)

Trong `MEASURE` của VG, với mỗi phần tử nhìn thấy (`vis`, VG:39), rộng ≥ 24px và cao ≥ 16px:

1. `R = max(borderTopLeftRadius, borderTopRightRadius, borderBottomRightRadius, borderBottomLeftRadius)` (parseFloat). Chỉ xét khi `R > 0` (PLAN ghi > 0; nếu sau khi đo thấy nhiễu dưới 1px thì nâng lên ≥ 1px).
2. Với mỗi cạnh `s ∈ {Top, Right, Bottom, Left}`: `w_s = parseFloat(border{s}Width)` (bằng 0 nếu `border{s}Style` là `none/hidden`), `c_s = norm(border{s}Color)` (dùng lại `norm`, VG:37, để đổi mọi định dạng màu sang RGBA).
3. Gom 4 cạnh thành nhóm theo khoá `(round(w_s), c_s)`. Tìm tập cạnh "lạ" `O` sao cho: `|O| = 1`, hoặc `|O| = 2` và hai cạnh kề nhau (Top+Left, Top+Right, Bottom+Left, Bottom+Right); các cạnh còn lại (2–3 cạnh) cùng một khoá. Hai cạnh đối diện (Left+Right khác Top+Bottom) ngoài phạm vi luật như PLAN viết (chưa rõ có muốn gộp không).
4. Cạnh lạ được tính là "cạnh màu" khi đủ cả ba:
   - `w_O ≥ 1px` và alpha màu > 0.4;
   - màu nhấn: `sat(c_O) > 0.35` (dùng lại hàm `sat`, VG:93, cùng ngưỡng với stripe hiện có);
   - lệch so với phần còn lại: hoặc khoảng cách RGB `‖c_O − c_rest‖ > 40` (trên thang 0–255), hoặc `w_O ≥ 1.5 × max(w_rest, 0.5)` (bao cả trường hợp các cạnh còn lại bằng 0).
5. Không miễn `blockquote`. Vẫn miễn như contrast: trong `svg`, `[aria-hidden="true"]`, `:disabled`.
6. Đo ở cả sáng và tối, báo ở cả hai (khác stripe hiện chỉ báo sáng).
7. Mở rộng cho pseudo: host có `R > 0` mà `::before/::after` rộng ≤ 6px cao ≥ 60% host, bão hoà > 0.35 (điều kiện VG:96) cũng tính là cạnh màu trên hộp bo tròn.

Rủi ro báo giả đã thấy trước: tab/nút đang active dùng `border-bottom: 2px solid accent` trên hộp bo tròn sẽ bị bắt; theo đúng chữ của luật thì đó là vi phạm, nhưng cần user xác nhận có muốn miễn (chưa rõ). Ô input kiểu chỉ có viền dưới dùng màu trung tính thì không bị bắt nhờ ngưỡng bão hoà.

Bản tĩnh tương ứng (PLAN Task 6 gọi là `rounded-edge`): gộp khai báo theo selector giống hệt (khối sau đè khối trước, bỏ qua specificity và `@media`), bung shorthand `border`, `border-{side}`, `border-{side}-{width,style,color}`, `border-color`/`border-width` 1–4 giá trị, `border-radius` và bốn longhand góc, rồi áp cùng điều kiện bước 3–4 với `_is_neutral_color` thay cho `sat`. Giới hạn đã biết của bản tĩnh: không gộp được khi hai class khác tên cùng gắn vào một phần tử, và không giải được `var()`; phần đó để bản chạy thật bắt.

## 3. Luật code-được CHƯA cài

Chỉ chọn thứ đo tất định, báo giả thấp. Không có luật bo tròn ở đây (Task 6 riêng). Chưa đo số đếm trên các trang hiện có; Task 7 phải đo trước khi cài (ràng buộc "cổng trước, sửa sau" của PLAN).

| # | Luật đề xuất | Cổng | Gate | Cách đo | Fixture XẤU | Fixture TỐT |
|---|---|---|---|---|---|---|
| 1 | `transition-all` | tĩnh | 10 | Regex `transition(?:-property)?\s*:\s*all\b` trong CSS và `style=""`, cộng class `transition-all` trong `class=""` | `<style>.btn{transition:all .2s}</style>` | `<style>.btn{transition:background-color .2s,color .2s}</style>` |
| 2 | `reduced-motion-missing` | tĩnh | 27 | Có `@keyframes`, hoặc `animation(-name)?:` khác `none`, hoặc `transition` chứa `transform`, mà CSS không có `@media (prefers-reduced-motion` | `<style>@keyframes f{to{transform:rotate(1turn)}}.s{animation:f 1s infinite}</style>` | cùng CSS thêm `@media (prefers-reduced-motion:reduce){.s{animation:none}}` |
| 3 | `horizontal-scroll` | chạy thật | 34 | Ở các bề rộng 320, 375, 768, 1360: `document.documentElement.scrollWidth > document.documentElement.clientWidth + 1` | `<div style="width:1200px;height:10px"></div>` | `<div style="max-width:100%;width:1200px;height:10px"></div>` |
| 4 | `clickable-wrap` | chạy thật | 49 | Ở 320 và 1360: với `button`, `[role=button]`, `[role=tab]`, `nav a`, `footer a`, `a.btn`, đếm số giá trị `top` khác nhau của `Range.getClientRects()` trên nội dung; ≥ 2 dòng thì FAIL. Không xét `a` nằm trong đoạn văn `p` | `<nav style="width:80px"><a href="#">Bắt đầu dùng miễn phí ngay</a></nav>` | `<nav style="width:80px"><a href="#" style="white-space:nowrap">Dùng thử</a></nav>` |
| 5 | `italic-display` | chạy thật | 38a | Phần tử có text trực tiếp, là `h1–h6` hoặc `fontSize ≥ 24px`, có `fontStyle` là `italic`/`oblique`; phủ phần FA:82-83 sót (class tiêu đề, `<em>` nằm sau thẻ khác) | `<p class="hero__title" style="font-size:40px;font-style:italic">Tiêu đề</p>` | `<p class="hero__title" style="font-size:40px;font-weight:700">Tiêu đề</p>` |
| 6 | `uppercase-tight-leading` | chạy thật | 55 | `textTransform === 'uppercase'`, `fontSize ≥ 24px`, và `lineHeight` (px, bỏ qua `normal`) chia `fontSize` < 1.0 | `<h2 style="font-size:48px;line-height:.94;text-transform:uppercase">HAI DÒNG, KHÁC NHAU</h2>` | `<h2 style="font-size:48px;line-height:1.05;text-transform:uppercase">HAI DÒNG, KHÁC NHAU</h2>` |

Dự bị nếu Task 7 còn ngân sách, cùng mức tất định: `sticky-double-top` (gate 56, chạy thật: ≥ 2 phần tử `position:sticky; top:0px`, một là `header/nav`) và `font-family-count` (gate 37, chạy thật: > 3 họ font, bỏ `pre/code`).

## Origin

- Node t5 của PLAN `llmwiki/wiki/sources/draft/210926-reading-font-slop-code-PLAN.md` (Task 5), ngày 21/09/2026.
- Nguồn đã đọc: `skills/hallmark/references/slop-test.md` · `fdk/tools/frontend-antipattern.py` · `fdk/tools/html-visual-gate.mjs` · `harness/policy.yaml` (R22 `html-slop`, dòng 181-188) · `fdk/wiki/sources/200926-slop-baseline.md` · phần đầu `fdk/tools/html-font-lint.py` (để xác nhận nó không đếm họ font).
- Số dòng trỏ vào trạng thái file tại commit `8fb5ef2` cộng working tree ngày 21/09/2026. Không chạy cổng nào khi viết trang này; mọi đánh giá rủi ro báo giả suy từ code và từ ghi chú trong code, chưa đo trên trang thật.
