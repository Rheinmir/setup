---
type: issue
kind: feature-gap
title: "Chưa có skill rút UI kit HTML (kiểu Figma UI kit) từ token + component thật của một codebase"
status: open
assignee: "@Rheinmir"
dispatch: Claude
entry: /fdk
priority: P2
labels: ready-for-agent
tags: [issue, skill, ui-kit, design-system, tokens, dev-loop]
timestamp: 2026-09-28
id: 280926-ui-kit-from-code
source_session: "m3e-canvas — dựng docs/ui-kit.html từ lib/tokens.ts, rồi yêu cầu rút cách làm thành skill"
---

# Issue: Chưa có skill rút UI kit HTML từ token + component thật của một codebase

## Vấn đề (một câu)
Khi một dự án đã có hệ thiết kế nằm trong code (token màu, thang kích thước, bộ component), overstack chưa có đường nào dựng lại nó thành MỘT trang HTML tham chiếu kiểu "Figma UI kit": đổi được theme, copy được token và markup, đối chiếu được với tên component trong code.

## Bối cảnh & bằng chứng
- Phiên m3e-canvas (28/09/2026) làm tay `docs/ui-kit.html` (khoảng 72 KB) cho editor Material 3 Expressive. Cách làm lặp lại được:
  1. Chạy chính hàm token của app qua test runner để lấy giá trị THẬT: `paletteOf()` cho 7 palette × sáng/tối, không gõ tay hex.
  2. Dựng foundations: 25 vai trò màu, thang chữ, thang shape (`--k` = `scaleR`), bảng kích thước.
  3. Vẽ khoảng 30 component bằng class `.m3-*`, chỉ dựa vào token `--m3-*` và `--k`.
  4. Ghép màn mẫu điện thoại 412×892 và desktop 1280×800 (rail + list-detail).
  5. Kiểm bằng Playwright: 0 lỗi JS, mobile không tràn ngang, chụp sáng/tối.
- Skill gần nhất là `[[hallmark]]`, nhưng `references/design-showcase.html` của nó là bộ mẫu design MẶC ĐỊNH của overstack (build/redesign), không phải kit rút từ code của dự án đích. Còn `extract-site`/`web-clone` rút từ URL đang chạy, không từ nguồn token.
- Skill anh em vừa có: `[[live-mcp-bridge]]` (PR #180). Kit là tài liệu tham chiếu cho định dạng mà agent ghi qua MCP (mỗi thẻ ghi tên `kind`).

## Phạm vi
- Skill mới `skills/ui-kit-from-code/` (loop `dev-loop`, nhóm build) + mirror llmwiki + đăng ký đủ các bề mặt curated.
- `references/ui-kit-reference.html` = chính file m3e-canvas làm mẫu output chuẩn, kèm checklist cấu trúc BẮT BUỘC cho từng phần.
- Universal: áp cho mọi codebase có token (TS/JS, CSS vars, Tailwind config, Style Dictionary, Android/Compose theme…).

## Không thuộc phạm vi
- Sinh design system MỚI khi dự án chưa có (đó là `hallmark`).
- Export sang Figma thật (.fig / plugin), Storybook, hay package npm component.
- Đồng bộ ngược kit → code.

## Hướng gợi ý (không bắt buộc)
Khung 7 phần cố định: thanh điều khiển theme · intro + facts · foundations (màu, chữ, shape, layout/kích thước) · component theo nhóm của app · màn mẫu (mobile + desktop) · nút copy (token, HTML từng thẻ, hex từng ô) · kiểm chứng Playwright.

## Tiêu chí HOÀN THÀNH
- (bổ sung 28/09) Chạy lại trên drafted.ai: `discover.mjs` dừng vì bão hoà và `--coverage` của kit drafted rc 0.
  - **Kết quả 28/09:** 32 trang, 171 pattern, `stoppedBy: saturated` (4 trang liền 0 mới). Cổng phủ 62/171 (36%) → 171/171 (100%): 149 có thẻ, 22 `ui-kit-skip` có lý do. Kit 59 thẻ, Playwright 0 lỗi, 390px không tràn. Lần chạy 16 trang trước đó dừng vì hết ngân sách trang khi trang 13–14 vẫn còn ra pattern mới, đúng failure boundary mới thêm.
- `swh-lint --skills ui-kit-from-code --ci`, `sync-skills.py --check`, `skill-registry.py --check`, `skill-provenance.py check --ci` đều rc 0.
- Skill nêu rõ cấu trúc bắt buộc của từng phần và trỏ tới file mẫu tham chiếu.
- File mẫu mở được độc lập (file://), 0 lỗi JS, không tràn ngang ở 390px.

## Cập nhật 2026-09-28 — lỗ hổng lộ ra khi test thật trên drafted.ai
- **Triệu chứng:** chạy `/ui-kit-from-code https://www.drafted.ai/`, agent chỉ quét đúng 3 trang đã biết (landing, `/auth`, `/learn`) rồi dựng kit. Kit ra đủ 7 phần nhưng chỉ là "phần xương". Người dùng mở `/learn/ai-for-homebuyers` và thấy nhiều pattern kit không có: breadcrumb, hàng tab hình thang, khung section viền đứt, lưới thẻ tính năng, hàng thẻ-link có mũi tên, sơ đồ luồng "PDF → Drafted → Editable plan", dải CTA giữa hai đường kẻ, lưới link "Popular ways to browse".
- **Gốc rễ:** skill chỉ bảo "tìm danh mục component" (W01, judgment). Không có bước bắt agent đi theo link, bấm mở phần ẩn, hay biết khi nào là đủ. Cũng không có cổng nào đo kit đã phủ hết pattern tìm được chưa.
- **Sửa (cùng PR):**
  - `references/discover.mjs`:
    - BFS link cùng origin, cuộn cả container cuộn bên trong, bấm mở accordion/tab/details.
    - Chữ ký pattern = loại + style + hình dạng con, bỏ trùng theo chữ ký.
    - Dừng khi `--saturate` trang liền không có pattern mới. Ra `inventory.json` + crop từng pattern.
    - Chế độ `--coverage` làm cổng phủ.
  - `SKILL.md`: thêm W01b (khám phá), W01c (xem crop), W05b (cổng phủ), RULE-08 (không dừng ở phần xương), RULE-09 (không nhúng tài sản bên thứ ba), B04 (nguồn là URL), 2 failure boundary (container cuộn riêng, chạm trần trang).
- **Lỗi của chính discover.mjs bắt được khi chạy thử:**
  1. `fullPage` chỉ chụp 900px vì site cuộn trong container.
  2. Luật "chỉ lấy khối ngoài cùng" nuốt mọi thẻ nằm trong khung viền đứt (lần đầu chỉ ra 3 card).
  3. Treo vô hạn trên trang cuộn vô hạn (vòng cuộn không có trần). Đã thêm trần 40 bước mỗi container, trần 120 s mỗi trang, và ghi inventory sau mỗi trang.
  4. Khung bố cục cả trang bị tính là card. Đã loại khối rộng ≥ 90% viewport mà cao hơn một màn.
  Tất cả đã sửa trong script.

## Cập nhật 2 (2026-09-28): kit thiếu trạng thái hover / focus / active / selected
- **Triệu chứng:** người dùng chỉ ra kit drafted chỉ bày trạng thái nghỉ. Không có hover, không có "đang chọn", nên không tái dùng được như Figma UI kit (Figma kit luôn có variant state).
- **Gốc rễ:**
  1. `discover.mjs` chỉ chụp style lúc trang vừa tải, không tương tác.
  2. Tab mang `aria-pressed` là `<a>` trong suốt cao đúng 40px, lọt qua mọi luật phân loại nên không được thu thập, và biến thể selected bị tính thành pattern rời.
  3. Hover của Tailwind v4 dùng thuộc tính CSS `scale` riêng, không nằm trong `transform`.
  4. Cổng phủ không đếm trạng thái.
- **Sửa (cùng PR #182):**
  - `discover.mjs` đo HOVER (rê chuột), ACTIVE (`mouse.down` → kéo ra → `mouse.up`, không kích hoạt link) và FOCUS-VISIBLE (Shift rồi focus) trên mọi pattern bấm được. So 16 thuộc tính nhìn thấy được, gồm `scale/translate/rotate` và màu của phần tử con. Focus chỉ là `outline:auto` thì gắn `ua: true`.
  - Phần tử có `aria-pressed/selected/current` luôn thuộc loại `tabs`. Biến thể selected được ghép với biến thể thường qua độ trùng class (≥ 0,6): `selectedOf`.
  - `--coverage` đòi mỗi trạng thái có `data-sig-state="<sig>:<state>"` trong kit, hoặc `ui-kit-skip` có lý do.
  - SKILL.md: RULE-10 (component không chỉ có trạng thái nghỉ), W01b / W05b / failure boundary cho trạng thái dựa vào JS.
- **Nghiệm thu trên drafted.ai:**
  - 32 trang, 175 pattern (bão hoà), 104 trạng thái: 44 hover, 56 focus, 1 active, 3 cặp selected.
  - Cổng: `trạng thái 0/104` → `104/104`, pattern `175/175`.
  - Kit 61 thẻ, 23 dải trạng thái. Playwright 0 lỗi, 390px không tràn.
- **Phát hiện phụ nhờ đo thật:**
  - 6 rule hover trong kit trước đó là đoán và sai. Ví dụ: thẻ lựa chọn và lưới onboarding hover lên viền stone-500 (không phải stone-900); nút viền mảnh hover đổi nền stone-50; hàng link nền giấy hover chuyển nền trắng.
  - 44/56 focus của site chỉ là viền mặc định của trình duyệt. Đây là điểm yếu về accessibility, kit ghi lại chứ không che đi.
- **Còn hở:** trạng thái chỉ có khi JS chạy (menu mở bằng click, tooltip trễ) chưa đo tự động. Disabled mới bắt được dạng tĩnh (thuộc tính `disabled`), chưa đi tìm chủ động.

## Cập nhật 3 (2026-09-28): chạy `/ui-kit-from-code facebook.com`
- **robots.txt:** facebook.com ghi "Collection of data on Facebook through automated means is prohibited unless you have express written permission", `User-agent: *` → `Disallow: /`. `discover.mjs` lúc đó KHÔNG kiểm robots.txt, nên nếu agent không tự đọc thì nó đã crawl. Sửa: script đọc robots.txt trước khi quét, cấm thì dừng rc 3 (cờ `--i-have-permission` chỉ khi user có giấy phép); thêm RULE-11.
- **Nhánh B05, user tự lưu trang:** user lưu News Feed ("Webpage, Complete"). Agent phục vụ qua 127.0.0.1, chặn mọi request ra ngoài (`--offline`), tắt JS (`--no-js`). Không crawler nào chạm tới facebook.com.
- **4 lỗi của discover.mjs bắt được khi chạy trên trang lưu:**
  1. Khi tắt JS, `setTimeout` trong trang không chạy, nên mọi `await wait()` trong `page.evaluate` treo vĩnh viễn (vòng cuộn và reveal). Sửa: mọi lệnh chờ chuyển sang phía Node.
  2. `locator.focus()` treo, và kéo treo luôn lệnh evaluate kế tiếp.
  3. Đo active bằng "nhấn giữ rồi kéo chuột ra" mở native drag trên link/ảnh, `mouse.up` treo.
  4. Trần 120 s/trang quá thấp cho trang 3000+ phần tử (thêm `--page-timeout`).

  Lỗi 2 và 3 được sửa tận gốc bằng cách bỏ hẳn chuột/bàn phím thật, đổi sang CDP `CSS.forcePseudoState`. Kiểm hồi quy trên 2 trang drafted.ai: cách mới bắt nhiều hơn (hover 18 so với 16, focus 23 so với 19, active 2 so với 0, cặp selected 1 so với 0).
- **Nghiệm thu:**
  - Lấy được 579 biến FDS cho cả sáng lẫn tối từ CSS đã lưu.
  - 78 pattern, 5 trạng thái đo được.
  - Kit `~/orca/ui-kits/facebook.html`: 27 thẻ, 66 vai trò màu. Cổng 78/78 + 5/5. Playwright 0 lỗi, 390px không tràn, 0 request ra ngoài.
  - grep 0 tên/nội dung thật của người dùng.
- **Còn hở:**
  - Hover/pressed của nút FDS do JS React gắn nên không đo được trên trang tắt JS. Kit dựng từ token `--hover-overlay` / `--press-overlay` và ghi rõ nguồn.
  - Trang lưu chỉ là bản desktop, nên màn mobile suy từ token.
  - Vòng focus FDS (`--focus-ring-shadow-default`) không hiện trên trang tắt JS.

## Assign & lý do
@Rheinmir, dispatch Claude qua `/fdk`: đã có bản mẫu chạy thật nên việc chủ yếu là chưng cất quy trình, agent làm được (`ready-for-agent`).

## Origin
Raise từ phiên Claude Code ở `~/orca/m3e-canvas` ngày 2026-09-28, sau khi dựng `docs/ui-kit.html` và thêm màn desktop theo yêu cầu người dùng. Bằng chứng: file mẫu đính kèm trong PR của skill, ảnh chụp Playwright trong phiên.
