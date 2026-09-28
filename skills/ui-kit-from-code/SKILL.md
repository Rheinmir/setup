---
name: ui-kit-from-code
description: "Rút hệ thiết kế ĐANG CÓ của một dự án — từ code (token màu, thang kích thước, component) hoặc từ URL site đang chạy thành MỘT trang HTML tham chiếu kiểu Figma UI kit: foundations + component theo nhóm + màn mẫu mobile/desktop, đổi palette/sáng-tối/shape, copy token/HTML/hex. Giá trị lấy bằng cách CHẠY hàm token thật (hoặc đọc style thật bằng Playwright) chứ không gõ tay; có vòng KHÁM PHÁ tự đi theo link + bấm mở phần ẩn, bỏ trùng theo chữ ký, dừng khi bão hoà, và cổng PHỦ bắt mọi pattern tìm được phải có mặt trong kit (không dừng ở phần xương). Mẫu output chuẩn: references/ui-kit-reference.html. KHÁC hallmark (dựng/đổi thiết kế mới): skill này chỉ CHÉP LẠI hệ đang có, không sáng tác. Gọi khi user nói 'ui kit', 'figma ui kit bằng html', 'bóc design system ra', 'trang tham chiếu component', 'design token page', 'component gallery', 'style guide từ code', 'bóc trang này ra html kit', 'làm giàu kit', hoặc /ui-kit-from-code."
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: ui-kit-from-code

## WHAT

### Purpose và context
- **Purpose:** dựng một file HTML độc lập để người (designer, dev, agent) tra cứu và dùng lại hệ thiết kế THẬT của dự án như một Figma UI kit: xem mọi token và component, đổi theme tại chỗ, copy thẳng token hoặc markup đem đi.
- **Trigger:** "bóc nó ra thành UI kit", "figma ui kit bằng html", "trang tham chiếu design system", "component gallery để tái dùng". Thường gặp sau khi dự án đã có token và component ổn định nhưng chưa có trang nào gom chúng lại.
- **Non-goals:** sáng tác hệ mới hoặc chỉnh thẩm mỹ (→ `hallmark`); clone nguyên trang để chạy lại (→ `extract-site` / `web-clone`); xuất file Figma thật, Storybook hay package npm; sửa code component của dự án.

### Mental model
```
nguồn token (TS/CSS/Tailwind/Compose…) ──chạy thật──▶ JSON token ──▶ CSS vars --<ns>-<role> + --k
component trong code (kích thước, variant, tên kind) ──đọc──▶ class .<ns>-* chỉ dựa vào vars
URL gốc ──discover.mjs (link BFS · mở phần ẩn · chữ ký · bão hoà)──▶ inventory.json + crops ──▶ danh mục phải dựng
kit.html + inventory.json ──--coverage──▶ phủ 100% (data-sig / ui-kit-skip)
                                   └──▶ ui-kit.html (7 phần bắt buộc) ──Playwright──▶ bằng chứng
```
Kit là **bản sao có kiểm chứng** của hệ trong code: mọi màu và số đo đều truy ngược được về một hằng số hoặc hàm trong repo. Chỗ nào phải vẽ theo spec vì code không nói rõ thì phải khai ra (RULE-04).

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | nguồn token | có | file/hàm sinh màu, chữ, shape, kích thước (vd `lib/tokens.ts` → `paletteOf`) |
| In | danh mục component | có | tên loại (`kind`/component name) + nhóm như app đang chia (palette, sidebar, docs) |
| In | nền tảng đích | có | mobile / desktop / cả hai, kèm kích thước khung thật |
| Out | `docs/ui-kit.html` (hoặc đường user chọn) | có | 1 file, mở bằng file:// được, có đủ 7 phần bên dưới |
| Out | báo cáo nguồn gốc | có | phần nào lấy từ code, phần nào vẽ theo spec |
| Out | bằng chứng Playwright | có | 0 lỗi JS, `scrollWidth - innerWidth = 0` ở 390px, ảnh sáng + tối + màn mẫu |

### Rules và capabilities
- RULE-01 (MUST): màu và số đo lấy bằng cách **chạy** code token của dự án (test runner/script tạm, xoá sau khi dump), không gõ tay hex. Code chỉ đọc được mà không chạy được (CSS vars, JSON) thì parse file.
- RULE-02 (MUST): mọi class component chỉ tham chiếu CSS var (`--<ns>-<role>`, `--k`); không hex/rgb rời trong CSS component. Nhờ vậy khối `:root` + CSS `.<ns>-*` bê sang dự án khác là chạy.
- RULE-03 (MUST): mỗi thẻ component ghi đúng **tên trong code** (kind/component name + field chính) và **số đo** (dp/px) như code dùng.
- RULE-04 (MUST): khai trong báo cáo (và ghi chú thẻ nếu cần) mọi phần vẽ theo spec hoặc đơn giản hoá (vd animation morph chỉ xoay); không trình bày như bản sao 1:1.
- RULE-05 (MUST): đủ 7 phần cấu trúc dưới đây; thiếu phần nào phải ghi lý do trong báo cáo (vd app không có desktop).
- RULE-06 (MUST): file tự chứa: font chỉ từ Google Fonts, JS/CSS inline, không build, không fetch dữ liệu ngoài.
- RULE-08 (MUST): **Không dừng ở phần xương.** Danh mục component phải đến từ vòng khám phá W01b (đi theo link, bấm mở phần ẩn, dừng khi bão hoà), không chỉ từ vài trang/file đã biết. Mỗi pattern trong `inventory.json` phải có thẻ trong kit mang `data-sig="<sig>"`, hoặc được bỏ có lý do qua `<meta name="ui-kit-skip" content="<sig>:<lý do>;…">`. Cổng: `node references/discover.mjs --coverage inventory.json kit.html` rc 0.
- RULE-10 (MUST): **Component không chỉ có trạng thái nghỉ.** Mỗi trạng thái mà W01b đo được (hover, focus-visible, active, selected) phải hiện trong kit: thẻ bày biến thể ở trạng thái đó (class `is-hover` / `is-focus` / `is-active` / `is-on` sao chép đúng rule `:hover`… của site) và mang `data-sig-state="<sig>:<state>"`. Hoặc được bỏ có lý do qua `ui-kit-skip` `"<sig>:<state>:lý do"`. Focus chỉ là `outline:auto` của trình duyệt (`ua: true`) thì kit ghi rõ "focus mặc định trình duyệt, site không style riêng". Cổng `--coverage` đếm cả trạng thái.
- RULE-09 (MUST): nguồn là site của người khác thì không nhúng ảnh, logo, wordmark SVG hay nội dung có bản quyền của họ vào kit; thay bằng khối giữ chỗ ghi rõ "ảnh …". Kit giữ ở máy user; muốn chia sẻ ra ngoài thì hỏi trước (B03).
- RULE-07 (SHOULD): đặt file mẫu `references/ui-kit-reference.html` cạnh khi làm; tái dùng khung, CSS vỏ trang và script điều khiển của nó, chỉ thay token, component, màn mẫu.
- Capabilities: đọc codebase; chạy test runner/script của dự án; ghi 1 file HTML; chạy Playwright (xem `/playwright-verify`).

### Cấu trúc bắt buộc của từng phần
Theo đúng thứ tự trong `references/ui-kit-reference.html`:

| # | Phần | Bắt buộc có | Trong file mẫu |
|---|---|---|---|
| 1 | **Thanh điều khiển** (sticky) | chọn palette (nếu app có nhiều) · sáng/tối · thang shape (nếu app có) · nút "Copy CSS token" cho khối `:root` của lựa chọn hiện tại; nhớ lựa chọn bằng `localStorage` (bọc try/catch); lần đầu theo `prefers-color-scheme` | `.bar` · `#swatches` `#mode` `#shape` `#copy-tokens` |
| 2 | **Mục lục** (sidebar, ẩn < 900px) | nhóm Nền tảng / Thành phần / Mẫu; tự tô mục đang xem (IntersectionObserver) | `.side` |
| 3 | **Intro** | eyebrow chỉ đường nguồn (`<file token> → <file kit>`) · h1 · 1 đoạn nói kit lấy từ đâu và dùng lại thế nào · dải "facts" các hằng số layout quan trọng | `.intro` `.facts` |
| 4 | **Nền tảng** | (a) **Màu:** mọi vai trò, ô có chữ màu `on*` đúng cặp, bấm để copy hex · (b) **Chữ:** thang chữ với tên + size/line-height/weight · (c) **Shape:** thang bo góc nhân `--k` · (d) **Layout & kích thước:** bảng size scale của component chính + bảng hằng số khung/lề/khoảng cách | `#color` `#type` `#shape` `#layout` |
| 5 | **Thành phần** | chia nhóm như app đang chia (vd Hành động · Điều hướng · Chứa nội dung · Nhập liệu · Phản hồi); mỗi thẻ `.spec` = header (tên người đọc + chip **tên trong code** + số đo) → `.stage` bày mọi variant/size/state quan trọng → footer (ghi chú + nút **Copy HTML** tự gắn); thẻ mang `data-sig` của các pattern nó phủ (RULE-08). Nhóm nào inventory có nhiều pattern thì chia thẻ theo từng pattern, không gộp thành một thẻ chung | `#actions` `#navigation` `#containment` `#inputs` `#feedback` |
| 6 | **Màn mẫu** | ≥ 1 màn **mobile** và ≥ 1 màn **desktop** (khi app hỗ trợ) ở đúng kích thước khung của app, thu nhỏ bằng `zoom`; ghép từ chính class component ở phần 5 theo quy tắc bố cục của app (vd bottom nav trên mobile → navigation rail + list-detail trên desktop); chú thích dưới khung liệt kê component đã dùng | `#screens` `.phone` `.desk` |
| 7 | **Script** | bảng token nhúng dạng `ROLES` + `PALETTES[key].light/dark` sinh từ dump · `apply()` ghi CSS var lên `:root` · render ô màu / thang chữ / thang shape từ dữ liệu · gắn nút copy · toast báo copy (clipboard bị chặn thì báo copy tay) | `<script>` cuối file |

Chung cho cả trang: vỏ trang mặc chính token của kit (trang đổi theme cùng component); `prefers-reduced-motion` tắt animation; `:focus-visible` rõ; nút icon có `aria-label`; mobile 390px không tràn ngang (bảng/màn mẫu nằm trong container `overflow-x:auto`).

### Failure boundaries
- Không tìm được nguồn token (màu hardcode rải rác trong component) → **partial**: gom màu thực dùng bằng grep, ghi rõ "không có nguồn token, màu suy từ component", đề xuất tách token (việc riêng).
- Site cuộn trong container riêng (body cao đúng 1 màn) → `fullPage` chỉ chụp 1 màn; `discover.mjs` tự mở container trước khi chụp, script tự viết phải làm tương tự.
- Trạng thái chỉ có khi JS chạy (menu mở bằng click, tooltip trễ, animation vào) → `:hover` thuần CSS đo được, còn trạng thái dựa JS có thể lọt; W01c xem crop `*-hover.png` rồi tự bổ sung. Nhấn giữ (active) đo bằng `mouse.down` → kéo chuột ra ngoài → `mouse.up`, nên không kích hoạt link. Không đo được thì ghi rõ trong báo cáo.
- Khám phá chạm trần trang (`stoppedBy: page-budget`) mà trang cuối vẫn ra pattern mới → báo user, đề xuất tăng `--pages` hoặc thu hẹp `--include`, không coi kit là đủ.
- Token chỉ chạy được trong runtime nặng (cần DB/app server) → dump bằng Playwright từ app đang chạy (`getComputedStyle` trên `:root`), ghi rõ cách lấy.
- Dự án chỉ có một nền tảng → phần 6 chỉ có màn đó, ghi lý do.
- Playwright báo lỗi JS hoặc tràn ngang sau 3 vòng sửa → dừng, báo lỗi còn lại.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | judgment | codebase | tìm nguồn token, danh mục component + nhóm, kích thước khung mobile/desktop, tài liệu schema (nếu có) | danh sách neo `file:line` | không có token → partial (xem Failure) |
| W01b | deterministic | URL gốc (app dev hoặc site) | vòng khám phá: `NODE_PATH=$(npm root -g) node references/discover.mjs <url> --out <scratch>/disc --pages 32 --saturate 4` (cần Playwright global; ~40 s/trang, chạy nền) (BFS link cùng origin, cuộn cả container trong, bấm mở accordion/tab/details, chữ ký = loại + style + hình dạng con, bỏ trùng; với pattern bấm được còn đo HOVER / FOCUS-VISIBLE / ACTIVE bằng chuột và bàn phím thật, và ghép biến thể SELECTED qua aria-pressed/selected/current, data-state, class is-active) | `inventory.json` + `crops/*.png` + ảnh từng trang | `stoppedBy: page-budget` còn ra mới → tăng ngân sách (Failure) |
| W01c | judgment | crops + ảnh trang | XEM mọi crop mới và ảnh toàn trang; gom pattern thành nhóm kit, ghi pattern bộ phân loại bỏ sót (vd tab hình thang, sơ đồ luồng) vào danh sách phải dựng | bảng pattern → nhóm → thẻ kit | — |
| W02 | deterministic | neo token | viết test/script tạm gọi hàm token thật, dump JSON (mọi palette × sáng/tối, size scale) → xoá file tạm | `tokens.json` ở scratchpad | chạy lỗi → parse tĩnh |
| W03 | effect | JSON | rút gọn thành `ROLES` + `PALETTES` và nhúng vào bản sao của file mẫu | khối dữ liệu trong `<script>` | — |
| W04 | judgment | component code | viết lại phần 4–5: mỗi component một class `.<ns>-*` dùng số đo từ code; thẻ `.spec` đủ header/stage/footer | phần 4–5 | thiếu số đo trong code → vẽ theo spec + khai (RULE-04) |
| W05 | judgment | quy tắc bố cục app | ghép phần 6: màn mobile + desktop từ class ở W04 | phần 6 | app 1 nền tảng → ghi lý do |
| W05b | deterministic | kit + inventory | `node references/discover.mjs --coverage <scratch>/disc/inventory.json <kit.html>` | `phủ N/N (100%)` + `trạng thái M/M` rc 0 | THIẾU pattern → dựng thẻ; THIẾU `sig:state` → thêm biến thể trạng thái vào thẻ (RULE-10) hoặc `ui-kit-skip` có lý do; chạy lại |
| W06 | deterministic | file | Playwright: tải trang, đếm `pageerror`, chụp đầu trang + giữa + màn mẫu, bật tối + palette khác chụp lại, viewport 390 đo tràn ngang | ảnh + số liệu | lỗi → sửa, tối đa 3 vòng |
| W07 | judgment | ảnh | nhìn ảnh một lượt, sửa lỗi bố cục thấy được (chữ dồn dòng, mục lệch), chụp lại 1 lần | kit xong | — |
| W08 | judgment | kết quả | báo user: đường file, nội dung 7 phần, phần nào từ code / theo spec, bằng chứng W06 | báo cáo | — |

**Dump token mẫu (vitest, TS):** tạo `lib/zz-kit-dump.test.ts` gọi hàm token rồi `writeFileSync(<scratchpad>/tokens.json, …)`, chạy `npx vitest run lib/zz-kit-dump.test.ts`, rồi `rm` file. Không để file tạm lọt vào diff của dự án.

**Kiểm Playwright mẫu:** như `/playwright-verify`: `chromium.launch()` → `goto(file://…/ui-kit.html)` → `page.on("pageerror")` → `screenshot` → `click('#mode button[data-v="dark"]')` → trang 390×844 đo `document.documentElement.scrollWidth - innerWidth`.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional_required | token là CSS vars / Tailwind config / JSON (không phải hàm) | parse tĩnh thay cho chạy (W02) | — | W03 |
| B02 | conditional_required | app có tài liệu schema cho agent (vd `agent.md`) | chip "tên trong code" ghi đúng tên field của schema, màn mẫu theo quy tắc trong tài liệu đó | không có → dùng tên component | W04 |
| B04 | conditional_required | nguồn là URL site đang chạy (không có code) | W02 thay bằng Playwright: đọc CSS vars ở `:root`/`.dark` + `getComputedStyle` của phần tử thật; màu `lab()`/`oklch()` đổi sang hex; áp RULE-09 | có code → skip | W03 |
| B03 | user_optional | user muốn link chia sẻ | đăng file lên Artifact/hosting user chọn; file vẫn giữ ở repo | mặc định chỉ file local | W08 |

### Validation và stopping
Máy kiểm: W05b cổng phủ rc 0 (mọi pattern có `data-sig` hoặc `ui-kit-skip`); W06 phải cho `pageerror = 0` và tràn ngang = 0 ở 390px. Mắt kiểm: đủ 7 phần theo bảng cấu trúc; so ảnh sáng/tối; thử nút Copy CSS token và 1 nút Copy HTML. Tối đa 3 vòng sửa ở W06, W07 chỉ chụp lại một lần.

### Examples
- **Positive:** m3e-canvas (Next.js, editor Material 3 Expressive). Dump `paletteOf()` qua vitest ra 7 palette × sáng/tối; kit có 25 vai trò màu, 15 kiểu chữ, 3 mức shape, khoảng 30 component chia 5 nhóm như bảng Parts của app, màn mobile 412×892 (list + detail) và desktop 1280×800 (rail + list-detail); Playwright 0 lỗi, 390px không tràn. Kết quả chính là `references/ui-kit-reference.html`.
- **Positive (URL):** drafted.ai. Lần đầu chỉ quét 3 trang đã biết nên kit chỉ là phần xương. Chạy W01b từ `/learn/ai-for-homebuyers` với `--pages 32 --saturate 4`: `discover.mjs` đi 32 trang (learn, use-cases, trang danh sách mẫu nhà, FAQ, news, careers, onboarding), gom 171 pattern, dừng vì 4 trang liền không có gì mới (~40 s/trang). W05b lần đầu báo `phủ 62/171 (36%)`. Sau khi dựng thêm các nhóm Danh sách mẫu nhà, Bài viết & section, bảng chữ thực dùng sinh từ inventory, và ghi 22 `ui-kit-skip` (ảnh, embed bên thứ ba, khung trang), cổng báo `phủ 171/171 (100%)`. W01c còn bắt thêm một pattern mà bộ phân loại bỏ sót: tab hình thang vẽ bằng SVG.
  Vòng 3 thêm đo trạng thái: 175 pattern, 104 trạng thái (44 hover, 56 focus, 1 active, 3 cặp selected). Lần đầu `trạng thái 0/104`. Sau khi thêm 23 dải trạng thái và thẻ "Focus · 2 kiểu", cổng báo `175/175` + `104/104`. Số đo cũng sửa 6 rule hover đoán sai trước đó (vd thẻ lựa chọn hover lên stone-500 chứ không phải stone-900), và cho thấy 44/56 focus chỉ là viền mặc định của trình duyệt.
- **Boundary/failure:** repo React chỉ có màu hex rải trong 40 file `.module.css`, không có token → partial: grep ra 18 màu thực dùng, kit ghi "màu suy từ component", đề xuất tách token trước khi kit hoá đầy đủ.
