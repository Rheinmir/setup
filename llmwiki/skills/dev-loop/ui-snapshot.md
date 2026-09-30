---
name: ui-snapshot
description: "Nén TOÀN BỘ UI/UX của một frontend (React/Next.js/Vue + Tailwind) vào MỘT file HTML tự chứa, chạy offline, dữ liệu placeholder viết cứng, dưới ngưỡng dung lượng (mặc định 5MB): port từng màn hình sang vanilla JS với class Tailwind chép nguyên văn từ JSX, biên dịch Tailwind bằng CHÍNH config của dự án, nhúng font + subset icon + logo, có panel chọn màn/trạng thái và khung điện thoại cho chế độ mobile, verify bằng Playwright. Dùng khi user nói 'snapshot UI', 'gói toàn bộ giao diện vào 1 file html', 'bản demo giao diện offline', 'mockup tĩnh có dữ liệu mẫu', 'nén UIUX dự án', 'gửi giao diện cho người không chạy được app', hoặc invoke /ui-snapshot. KHÁC hallmark/redesign (thiết kế MỚI) và playwright-verify (chỉ chụp/đo app đang chạy) — ui-snapshot TÁI HIỆN giao diện hiện có, không cần backend/đăng nhập."
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: ui-snapshot

Đúc kết từ phiên bonbon-ai 2026-09-19: 12 màn × desktop/mobile + 10 overlay của `fe/` (Next.js 14,
Tailwind 3) gói trong 426 KB, Playwright 22 ảnh, 0 lỗi console.

## WHAT

### Purpose và context
- **Purpose:** một file `.html` duy nhất mở bằng double-click (không server, không mạng, không login) tái hiện đúng giao diện app thật — layout, token màu, font, icon, trạng thái (loading/empty/error/overdue…), overlay (modal, sheet, toast, tour) — với dữ liệu placeholder cứng.
- **Trigger (when to use):**
  - Cần đưa giao diện cho người không chạy được app (sếp, designer, khách, reviewer, tài liệu wiki).
  - Cần bản mockup có dữ liệu mẫu để bàn UX/QC mà không đụng dữ liệu thật hay backend.
  - User nói 'snapshot UI', 'gói giao diện vào 1 file html', 'nén UIUX dự án', hoặc `/ui-snapshot`.
- **Non-goals:** không thiết kế lại (→ hallmark/redesign), không chụp ảnh tĩnh app đang chạy (→ playwright-verify), không nhét dữ liệu thật, không giữ logic nghiệp vụ/API (nút hành động chỉ đổi state trong trang).

### Mental model
Vì sao PORT thay vì build/SSR app thật: app thật cần auth + backend + dữ liệu thật; snapshot bằng DOM thật sẽ kéo theo dữ liệu nhạy cảm và bundle lớn. Port sang vanilla JS với **class chép nguyên văn** + **compile Tailwind bằng config thật** cho ra đúng pixel mà không mang theo gì khác.

`đọc HẾT JSX các trang → liệt kê màn + trạng thái + overlay → viết app.js (router hash, state, data cứng, 1 hàm/màn, nhánh desktop/mobile) → build.py (Tailwind config thật + font + icon subset + asset data URI) → shot.mjs verify → sửa → publish`.

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | thư mục frontend (`--fe`) có `node_modules` | có | để dùng `tailwindcss` CLI + config của dự án |
| In | danh sách trang/route | có (tự dò `app/**/page.tsx`, `pages/`, `src/routes`) | phạm vi "toàn bộ UI" |
| In | ngưỡng dung lượng | không (5 MB) | `--max-mb` |
| In | font chính / logo / banner | không | `--font`, `--asset NAME=path` |
| Out | `<repo>/…/DDMMYY-<project>-uiux-snapshot.html` | có | file duy nhất, offline |
| Out | báo cáo: số màn, KB, ảnh verify, lệch so app thật | có | trung thực, liệt kê chỗ giả lập |

### Rules và capabilities
- RULE-01 (MUST): **Đọc HẾT file JSX của từng trang trước khi port** (kể cả nhánh mobile, empty/loading/error, modal, sheet). Port từ trí nhớ = lệch UI.
- RULE-02 (MUST): **Class Tailwind chép NGUYÊN VĂN** từ JSX, viết dạng chuỗi literal trong `app.js` (JIT chỉ thấy literal; ghép động `bg-${x}` sẽ mất class).
- RULE-03 (MUST): **Dữ liệu placeholder cứng, không bao giờ dữ liệu thật** (không gọi API, không copy từ network capture/DB). Ngày dùng offset tương đối (`D(-9)`) để trạng thái quá hạn ổn định theo thời gian.
- RULE-04 (MUST): Tên icon viết dạng chuỗi có nháy (`"search"`) để `build.py` subset font; icon động thì đặt tên đầy đủ trong map.
- RULE-05 (MUST): Cùng breakpoint với app (vd 768px) và render nhánh desktop/mobile bằng JS (không dựa `md:` khi có chế độ ép mobile trong khung điện thoại).
- RULE-06 (MUST): Asset ngoài (ảnh CDN, font Google) phải nhúng hoặc thay bằng nền/gradient — file phải chạy offline. Ghi rõ mọi chỗ thay thế trong báo cáo.
- RULE-07 (MUST): Verify bằng `shot.mjs` cả desktop + mobile, đọc ảnh, `NO ERRORS` mới báo xong; vượt `--max-mb` = FAIL.
- RULE-08 (SHOULD): Có panel demo (nút "UI") để nhảy tới mọi màn + bật trạng thái (loading/stale, lỗi, toast, tour, các state AI…), và chế độ Auto/Desktop/Mobile.
- Capabilities: đọc codebase; Python 3 + Node + Tailwind CLI của dự án; mạng lúc build (Google Fonts, codepoints); Playwright để verify.

### Failure boundaries
- Dự án không dùng Tailwind → `build.py` để CSS trống: chép CSS module/styled vào template tay, hoặc **clarify** với user.
- Không có mạng lúc build → font/icon không nhúng được → **blocked** (hoặc chấp nhận fallback system font, ghi rõ).
- File vượt ngưỡng → giảm: bỏ weight font thừa, ảnh `sips -Z` nhỏ hơn, bớt dữ liệu mẫu; không cắt màn hình.
- Framework khác (Vue/Svelte/Angular template) → vẫn áp dụng, chỉ đổi nguồn đọc class.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | `--fe` | Dò route + layout + component dùng chung; đọc `tailwind.config`, `globals.css`, `design.md` nếu có | danh sách màn + token | không Tailwind → FB1 |
| W02 | judgment | JSX từng trang | Đọc HẾT từng trang (RULE-01), ghi lại mọi trạng thái/overlay/nhánh mobile | inventory màn × trạng thái | — |
| W03 | effect | inventory | Tạo `<scratch>/app.js` từ `assets/app-skeleton.js`, `template.html` từ `assets/template.html` (thay `__TITLE__`, `__FONT__`); port từng màn, class nguyên văn, data cứng | app.js | — |
| W04 | deterministic | app.js + template | `python3 scripts/build.py --fe <fe> --src <scratch> --out <file> --font "<Font>" --asset LOGO=public/logo.png` | file HTML + KB | lỗi Tailwind → xem stderr; >max → FB3 |
| W05 | deterministic | file | `node scripts/shot.mjs <file> <scratch>/shots d-home=home m-home=home …` (cài `playwright` vào scratch nếu thiếu) rồi ĐỌC ảnh | ảnh + `NO ERRORS` | lỗi → sửa app.js, lặp W04 |
| W06 | effect | file | Đặt vào repo (vd `llmwiki/html/DDMMYY-<project>-uiux-snapshot.html`), ghi log wiki nếu dự án có; báo cáo số màn, KB, chỗ giả lập | báo cáo | — |

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | conditional | trang có dead-code UI (state không có đường vào) | vẫn port nhưng chỉ mở qua panel demo, ghi chú "legacy" | — | W03 |
| B02 | conditional | app có devtool page tối/khác design system | port bằng inline style như bản gốc | — | W03 |
| B03 | recovery | chế độ mobile trên màn rộng lệch layout | khung `#frame` có `transform` để `fixed` bám khung; `#app` là vùng cuộn; override `.h-screen/.min-h-screen` = 100% (đã có trong template) | — | W05 |

### Validation và stopping
Tất định: `build.py` exit 0 và dưới ngưỡng; `shot.mjs` in `NO ERRORS` cho mọi màn desktop + mobile. Cần mắt: so ảnh với app thật/Figma (màu, khoảng cách, chữ tiếng Việt có dấu). Dừng khi mọi màn trong inventory có ảnh sạch và báo cáo đã liệt kê chỗ giả lập.

### Examples
- **Positive:** bonbon-ai `fe/` → login, dashboard overview/pending/overdue, filter theo phòng ban/loại HĐ, chi tiết phiếu 3 tab, VS Code overlay, AI tracker, sheet/modal/toast/tour → 426 KB, 79 icon, 22 ảnh verify, 0 lỗi.
- **Boundary:** dự án ảnh nền hero 3 MB từ CDN → thay gradient + ghi "khác app thật: ảnh nền login" thay vì nhúng làm file vượt ngưỡng.

### Test tất định
`python3 scripts/build.py --fe <fe> --src assets-copy --out /tmp/t.html` với `assets/app-skeleton.js` (đổi tên app.js) + `assets/template.html` phải ra file < 1 MB, rồi `node scripts/shot.mjs /tmp/t.html /tmp/shots d-home=home m-home=home` in `NO ERRORS`.
