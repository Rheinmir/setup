---
type: draft
title: theme-toggle-circle-reveal-motion
status: proposed
tags: [docs-site-macos, motion, theme-toggle, playwright, design-foundation]
timestamp: 2026-09-16
task: T-260916-01
---

# 160926-theme-toggle-circle-reveal-motion

**Status:** proposed
**Sequence diagram:** [160926-theme-toggle-circle-reveal-motion-seq.html](../../../html/160926-theme-toggle-circle-reveal-motion-seq.html)

## What
Đổi luật chuyển dark/light mode của framework overstack (và mọi trang tuân luật `html-theme-toggle-required`) từ "flip tức thời" sang một hiệu ứng circle-reveal bắt buộc: bấm nút toggle → một hình tròn màu nền = mode đích, tỏa ra từ đúng vị trí nút, lan chậm rồi nhanh-dứt-khoát phủ kín màn hình, rồi fade — hết fade thì trang đã ở mode mới hoàn toàn; đồng thời cung cấp một script Playwright độc lập để nghiệm thu hiệu ứng này trên bất kỳ trang nào `docs-site-macos` sinh ra kể từ bản cập nhật.

## Context
- [[design-foundation]] — hallmark là SÀN cho UI sản phẩm downstream, nhưng `docs-site-macos` là **ngoại lệ có tên**: theme của TA cho artifact nội bộ (report/seq/dashboard/proposal render), không bị hallmark thay, vẫn phải qua cổng universal (không fake chrome, không gradient text). Đề xuất này SỬA đúng cái ngoại lệ có tên đó, không đụng hallmark.
- Memory `html-theme-toggle-required` (feedback user nhắc 2 lần, 2026-07-06): mọi HTML sinh cho người xem (report, docs site, dashboard, cây vấn đề, proposal render…) PHẢI có toggle sáng/tối dạng nút gạt, không ép 1 mode; snippet chuẩn nằm ở `skills/docs-site-macos/SKILL.md` § "Theme Toggle sáng/tối", rule mirror ở `llmwiki/skills/utils/fdk.md:101` § Rules, generator giữ 1 nguồn `_DARK_RULES` trong `fdk/tools/build-overstack-docs.py` để tránh 2 bản CSS lệch nhau.
- `skills/docs-site-macos/SKILL.md:196-226` — kỹ thuật **Ripple effect** đã có sẵn cho nút sidebar/toggle: 1 `<span>` overlay được chèn vào phần tử cha `position` + `overflow:hidden`, bán kính = khoảng cách xa nhất tới 4 góc phần tử, animate bằng `@keyframes` + `cubic-bezier`, tự dọn ở `animationend`. Đây là kỹ thuật gốc cần **mở rộng từ phủ-1-nút thành phủ-cả-viewport** cho circle-reveal, không phải viết mới từ đầu.
- `skills/docs-site-macos/SKILL.md:1014-1024` — `flip()` hiện tại đổi `data-theme` + `localStorage` ngay lập tức, không có bước trung gian nào — đây là điểm cần chèn overlay.
- `skills/hallmark/SKILL.md` (Disciplines that hold across every verb, mục 6 Mobile + motion.md): "Support `prefers-reduced-motion: reduce`. Spatial motion collapses to ≤150ms opacity crossfade." — kỷ luật a11y-motion đã có sẵn trong framework, đề xuất này phải tuân theo cùng chuẩn, không phát minh luật riêng.
- `skills/dev-loop/playwright-verify.md` (mirror `llmwiki/skills/dev-loop/playwright-verify.md`) — pattern chuẩn cho script Playwright standalone `.mjs` (không qua test runner), verify nhanh 1 lần, đọc console/pageerror. Script nghiệm thu circle-reveal đi theo đúng pattern này, không tạo cơ chế mới.

## Global constraints
- **Không ép 1 mode** (memory `html-theme-toggle-required`, nhắc 2 lần) — circle-reveal chỉ đổi CÁCH chuyển, không được biến mất khả năng user tự chọn light/dark.
- **Dạng nút bắt buộc: NÚT GẠT (switch)** có nhãn "Giao diện", hàng footer dính đáy sidebar/nav, KHÔNG chip icon rải góc (memory cùng nguồn, feedback lần 3).
- **Generator một nguồn** — `_DARK_RULES` trong `fdk/tools/build-overstack-docs.py` và snippet trong `skills/docs-site-macos/SKILL.md` phải khớp nhau; chép tay 2 bản là mầm drift (nguyên văn dòng 995 SKILL.md).
- **`prefers-reduced-motion: reduce` phải được tôn trọng** — theo đúng chuẩn `motion.md` của hallmark: spatial motion collapse về ≤150ms opacity crossfade, không ép người dùng nhạy cảm motion chịu hiệu ứng full-screen 500-600ms.
- **System fonts / self-contained** — trang docs-site-macos không tải asset ngoài (SKILL.md §Fonts); overlay circle-reveal phải là CSS/JS thuần, không thêm dependency/thư viện animation ngoài.
- **Prose đầy đủ cho tài liệu người đọc** (`llmwiki/CLAUDE.md`): SPEC này và companion HTML phải viết câu hoàn chỉnh, không caveman.
- **KHÔNG ghi công AI trong commit/PR** (`llmwiki/skills/utils/fdk.md`).

## Non-goals
- KHÔNG bắt buộc `hallmark` (sàn UI sản phẩm cho dự án downstream) phải tự thêm RUNTIME toggle nếu bản thân trang đó vốn không theo luật `html-theme-toggle-required` (hallmark chọn 1 mode/theme cố định theo brief, đó là quyết định thiết kế khác, không phải phạm vi đề xuất này).
- KHÔNG polyfill cho trình duyệt cổ (IE, hoặc browser đã hết hỗ trợ) — chỉ cần fallback graceful (đổi tức thời, không lỗi/không kẹt overlay).
- KHÔNG biến script Playwright thành gate BẮT BUỘC tự động trong pre-commit/CI ở bản này — theo đúng pattern hiện có của `playwright-verify` (chạy tay/theo yêu cầu). Nâng thành gate tự động là việc khác, ghi vào Assumptions bên dưới.
- KHÔNG hồi tố bắt build lại hàng loạt các trang HTML cũ đã tồn tại trong `llmwiki/html/` — luật mới chỉ áp cho trang sinh ra **kể từ bản cập nhật này**.
- KHÔNG đổi cách hallmark chọn theme mặc định hay hệ 20-theme catalog của nó.

## Approaches
**A. View Transitions API** (`document.startViewTransition()` + CSS animate `::view-transition-new(root)` bằng `clip-path: circle()`).
- Ưu: API trình duyệt gốc, GPU-composite, ít code viết tay.
- Nhược: độ phủ trình duyệt không đều (Firefox từng thiếu/chưa đủ, tuỳ thời điểm phát hành); pseudo-element `::view-transition-*` không có DOM handle thật → Playwright khó `page.locator()`/đọc computed style trực tiếp, dễ viết test flaky hoặc phải suy luận qua screenshot-diff (chậm, không xác đáng bằng assert DOM).

**B. DOM overlay thủ công + Web Animations API** (tạo `<div class="theme-reveal">` thật, animate bằng `element.animate({clipPath:[...]}, {...})` hoặc `@keyframes` + class, xong thì đổi `data-theme` rồi remove) — mở rộng trực tiếp từ kỹ thuật Ripple đã có ở SKILL.md:196-226.
- Ưu: chạy được trên mọi trình duyệt hiện đại (WAAPI hỗ trợ rộng hơn View Transitions); phần tử có thật trong DOM nên Playwright assert được trực tiếp (tồn tại/màu/kích thước/thời điểm remove); tái dùng nguyên khung Ripple đã có, ít rủi ro conflict CSS mới.
- Nhược: thêm ~30-40 dòng JS trong snippet (so với vài dòng của View Transitions); phải tự quản lifecycle (dedup nếu bấm liên tục khi overlay đang chạy).

**C. CSS-only** (1 pseudo-element cố định `::before` full-viewport, đổi toạ độ tâm qua CSS custom properties `--x --y`, transition trên `clip-path`).
- Ưu: không cần animate bằng JS, chỉ set custom property rồi transitionend.
- Nhược: vẫn cần JS để đọc toạ độ nút (nút toggle nằm khác vị trí tuỳ trang có/không sidebar) nên không tiết kiệm được nhiều so với B; khó làm easing 2 pha (chậm→nhanh-dứt-khoát) bằng transition đơn thuần như WAAPI/`@keyframes` cho phép.

**Chọn B.** Lý do quyết định: yêu cầu cốt lõi của user là nghiệm thu được bằng Playwright — B là phương án duy nhất cho DOM handle thật để assert trực tiếp (tồn tại/toạ độ/màu/thời điểm gỡ), đồng thời không phụ thuộc độ chín của 1 API còn đang lan rộng hỗ trợ (A) và tránh giới hạn easing của C. B cũng tái dùng đúng kỹ thuật Ripple đã có, giảm bề mặt code mới.

## Plan
- [ ] **T1 — Viết snippet circle-reveal chuẩn**, thay thế/bọc `flip()` trong `skills/docs-site-macos/SKILL.md` § "Theme Toggle sáng/tối" (dòng ~978-1026). Mở rộng kỹ thuật Ripple (dòng ~196-226): overlay `<div class="theme-reveal">` gắn `position:fixed;inset:0` (không phải absolute trong nút — cần phủ toàn viewport), bán kính khởi tạo từ tâm nút, đích = khoảng cách xa nhất tới 4 góc viewport (không phải góc nút); màu nền overlay = token nền của MODE ĐÍCH (đọc từ CSS variable, không hardcode hex); easing 2 pha (`cubic-bezier` chậm đầu → nhanh-dứt-khoát, không linear); `data-theme` + `localStorage` đổi khi overlay đã phủ hết viewport (trước lúc fade, để không lộ nội dung mode cũ qua lớp overlay đang mờ dần); sau đó overlay fade rồi bị gỡ khỏi DOM. Có nhánh `@media (prefers-reduced-motion: reduce)`: bỏ animate full-screen, chỉ giữ ≤150ms opacity crossfade như chuẩn `motion.md` của hallmark. Trình duyệt không hỗ trợ `Element.animate` (cực hiếm, nhưng vẫn cần fallback) → đổi tức thời như hiện tại, không lỗi console.
- [ ] **T2 — Đồng bộ mirror `llmwiki/skills/utils/docs-site-macos.md`** — copy y hệt canonical sau khi T1 chốt (đúng pattern parity đã dùng cho `design-prim`).
- [ ] **T3 — Rà generator `fdk/tools/build-overstack-docs.py`** — kiểm `_DARK_RULES` và mọi chỗ khác trong file có emit JS `flip()`/theme-switch hay không (không chỉ CSS). Có → cập nhật đồng bộ theo snippet T1, giữ đúng nguyên tắc "một nguồn, emit nhiều khối" đã ghi ở SKILL.md dòng 995. Không có (generator chỉ emit CSS, JS luôn được LLM copy tay từ SKILL.md) → ghi rõ trong PLAN kèm bằng chứng grep, coi là no-op.
- [ ] **T4 — Viết script Playwright độc lập `skills/docs-site-macos/scripts/verify-theme-motion.mjs`**, theo đúng convention của `playwright-verify` (`.mjs` standalone, không qua test runner). Nhận đường dẫn 1 file HTML (`file://` hoặc `http://`), mở bằng Chromium, đọc `data-theme` ban đầu, bấm `.theme-switch`, rồi assert theo thứ tự: (a) overlay xuất hiện với toạ độ tâm ≈ vị trí nút; (b) màu nền overlay khớp token của MODE ĐÍCH (không phải mode hiện tại); (c) overlay đạt kích thước phủ hết viewport trước khi bắt đầu fade; (d) `data-theme` + `localStorage` đã đổi đúng giá trị ở cuối; (e) overlay bị gỡ khỏi DOM sau khi animation kết thúc (không kẹt lại). Chạy thêm 1 lượt với `page.emulateMedia({reducedMotion:'reduce'})` — assert KHÔNG có overlay full-screen, chỉ có crossfade ngắn. Thoát rc 0 khi mọi assert đạt; rc khác 0 kèm dòng lý do rõ ràng khi thiếu bất kỳ mảnh nào.
- [ ] **T5 — Cập nhật 2 điểm tham chiếu luật:** `llmwiki/skills/utils/fdk.md` dòng ~101 (đoạn "HTML cho người xem phải có TOGGLE sáng/tối") thêm 1 câu trỏ tới yêu cầu circle-reveal + đường dẫn script T4; và memory cá nhân `html-theme-toggle-required.md` (`/Users/giatran/.claude/projects/-Users-giatran-orca-setup-setup/memory/`) — cập nhật mục "How to apply" ghi rõ luật đã đổi từ 2026-09-16, trỏ `T-260916-01`.
- [ ] **T6 — Chứng minh thật:** render companion HTML của chính proposal này bằng `docs-site-macos` (đã có snippet mới từ T1), rồi chạy `verify-theme-motion.mjs` (T4) trên trang đó → đính kết quả rc + log làm bằng chứng cho SC-004.

## Agent Task Assignment
| Task | Agent (CLI) | Lý do chọn | Status |
|---|---|---|---|
| T1 | Claude (phiên này) | Quyết định kỹ thuật animation (bán kính, easing 2 pha, thời điểm đổi `data-theme`) cần đọc hiểu toàn bộ style-guide + kỹ thuật Ripple sẵn có, không phải việc cơ học giao được cho CLI rẻ | pending |
| T2 | Claude (phiên này) | Copy đồng bộ canonical→mirror ngay sau T1, cùng phiên để không lệch nội dung | pending |
| T3 | Claude (phiên này) | Cần đối chiếu logic sinh code với quyết định T1; giao CLI khác không có ngữ cảnh T1 dễ đồng bộ sai | pending |
| T4 | Claude (phiên này) | Assertion Playwright phải bám đúng tên class/thứ tự sự kiện vừa chốt ở T1 | pending |
| T5 | Claude (phiên này) | Sửa 2 dòng tham chiếu luật, việc nhỏ giữ cùng phiên cho số liệu (đường dẫn script, task ID) khớp thật | pending |
| T6 | Claude (phiên này) | Cần chạy Playwright thật + đọc log trong sandbox hiện có để làm bằng chứng SC-004, không dispatch ra ngoài được | pending |

Toàn bộ giao một agent (không dispatch CLI rẻ) vì đây là `/propose` standalone (không qua `orca-workflow`/`orca-graph` dispatch) — quyết định kỹ thuật của T1 phải truyền nguyên vẹn sang T3/T4/T6 trong cùng phiên, tách ra nhiều CLI ở quy mô 6 task nhỏ-liên-đới-chặt sẽ tốn thêm vòng đồng bộ context hơn là giữ lại.

## Render brief
Mỗi task dưới đây là input cho `docs-site-macos` + `archify sequence` dựng companion HTML — participants là các thực thể chạm tới trong task, message màu theo variant: indigo = đã có sẵn (existing), emerald = thêm/đổi (added), amber = chặn/rủi ro (blocked/fail).

**T1 — Viết snippet circle-reveal.** Participants: `Claude`, `docs-site-macos/SKILL.md`, `Ripple-pattern (dòng 196-226)`, `Theme-toggle cũ (flip(), dòng 1014-1024)`.
1. *(existing)* Claude đọc `flip()` hiện tại — đổi `data-theme` tức thời, không có bước trung gian.
2. *(existing)* Claude đọc kỹ thuật Ripple đã có — overlay `<span>` con của phần tử `position`+`overflow:hidden`, bán kính tới góc xa nhất, `@keyframes`+`cubic-bezier`, tự dọn ở `animationend`.
3. *(added)* Claude viết overlay `.theme-reveal` mới: `position:fixed;inset:0`, bán kính khởi tạo từ tâm nút toggle, đích = khoảng cách xa nhất tới 4 góc **viewport** (không phải góc nút).
4. *(added)* Claude gán màu nền overlay = token nền của MODE ĐÍCH, đọc từ CSS variable.
5. *(added)* Claude viết easing 2 pha (chậm đầu → nhanh-dứt-khoát) bằng `cubic-bezier` phi tuyến, không dùng `linear`.
6. *(added)* Claude bọc `flip()`: đổi `data-theme`+`localStorage` ngay khi overlay đã phủ hết viewport, TRƯỚC lúc bắt đầu fade.
7. *(added)* Claude thêm nhánh `@media (prefers-reduced-motion: reduce)` — bỏ animate full-screen, chỉ giữ ≤150ms opacity crossfade.
8. *(added)* Claude ghi đè snippet mới vào § "Theme Toggle sáng/tối" của `SKILL.md`.

Prose: Đây là task nặng nhất và là gốc của mọi task sau — nó không viết từ số 0 mà **mở rộng** một kỹ thuật đã tồn tại và đã được kiểm chứng trong chính skill này (Ripple), giảm rủi ro so với phát minh một cơ chế animation hoàn toàn mới. Điểm khó nhất là thời điểm đổi `data-theme`: phải xảy ra khi overlay ĐÃ phủ kín màn hình nhưng TRƯỚC khi nó bắt đầu mờ đi, nếu không người xem sẽ thấy nội dung mode cũ lộ ra qua lớp phủ đang fade — đây chính là điều FR-005 khoá lại.

**T2 — Đồng bộ mirror.** Participants: `Claude`, `skills/docs-site-macos/SKILL.md (canonical)`, `llmwiki/skills/utils/docs-site-macos.md (mirror)`.
1. *(existing)* Canonical đã có snippet mới từ T1.
2. *(added)* Claude copy nguyên văn canonical đè lên mirror.
3. *(existing)* `diff` canonical/mirror trả về rỗng — parity giữ đúng pattern đã dùng cho `design-prim`.

Prose: Bước thuần cơ học, không có quyết định kỹ thuật mới — rủi ro duy nhất là quên chạy, nên `diff` ở bước 3 là bằng chứng bắt buộc, không phải tuỳ chọn.

**T3 — Rà generator.** Participants: `Claude`, `fdk/tools/build-overstack-docs.py`, `_DARK_RULES`.
1. *(existing)* Claude grep toàn file tìm mọi chỗ emit JS `flip()`/`theme-switch` (không chỉ CSS `_DARK_RULES`).
2. *(blocked)* Tìm thấy bản JS trùng lặp ngoài nguồn snippet SKILL.md → đánh dấu rủi ro drift, phải cập nhật đồng bộ theo T1 trước khi đóng task.
3. *(added)* Không tìm thấy JS trùng lặp (generator chỉ emit CSS, JS luôn do LLM copy tay từ SKILL.md) → ghi no-op kèm bằng chứng lệnh grep đã chạy.

Prose: Task này tồn tại để tránh đúng cái bẫy dòng 995 của SKILL.md đã tự cảnh báo — "chép tay 2 bản là mầm drift". Nhánh (2) và (3) loại trừ nhau; kết quả thật quyết định nhánh nào chạy, không đoán trước.

**T4 — Script Playwright nghiệm thu.** Participants: `Claude`, `Playwright (Chromium)`, `file HTML mục tiêu`, `.theme-switch`, `.theme-reveal overlay`.
1. *(added)* Script mở file HTML mục tiêu bằng Chromium, đọc `data-theme` ban đầu.
2. *(added)* Script bấm `.theme-switch`.
3. *(added)* Script assert toạ độ tâm overlay ≈ vị trí nút, màu nền overlay khớp token MODE ĐÍCH.
4. *(added)* Script assert overlay đạt kích thước phủ hết viewport trước khi bắt đầu fade.
5. *(added)* Script assert `data-theme`+`localStorage` đã đổi đúng giá trị ở cuối.
6. *(added)* Script assert overlay bị gỡ khỏi DOM sau khi animation kết thúc.
7. *(added)* Script lặp lại với `page.emulateMedia({reducedMotion:'reduce'})`, assert KHÔNG có overlay full-screen, chỉ có crossfade ngắn.

Prose: Đây là bằng chứng máy cho SC-001/SC-002 — script không kiểm tra "trông có động hay không" bằng screenshot-diff (dễ flaky), mà assert trực tiếp trên DOM handle thật của phương án B, đúng lý do B được chọn ở `## Approaches`.

**T5 — Cập nhật tham chiếu luật.** Participants: `Claude`, `llmwiki/skills/utils/fdk.md`, `memory html-theme-toggle-required.md`.
1. *(existing)* `fdk.md` dòng ~101 mô tả luật toggle cũ, chưa nhắc motion.
2. *(added)* Claude thêm 1 câu trỏ yêu cầu circle-reveal + đường dẫn script T4.
3. *(added)* Claude cập nhật mục "How to apply" của memory cá nhân, trỏ `T-260916-01`.

Prose: Việc này đảm bảo luật mới **discoverable** ở đúng nơi framework/downstream đọc được (FR-011) — không chỉ nằm trong memory cá nhân của agent, vốn không đi theo khi kéo repo sang máy khác.

**T6 — Chứng minh thật.** Participants: `Claude`, `docs-site-macos generator`, `verify-theme-motion.mjs`, `companion HTML của chính proposal này`.
1. *(existing)* Companion HTML `160926-theme-toggle-circle-reveal-motion-seq.html` đã tồn tại (chính trang đang render).
2. *(added)* Sau khi T1 xong, Claude patch trang này dùng snippet mới.
3. *(added)* Claude chạy `verify-theme-motion.mjs` trên trang đó.
4. *(added)* Kết quả rc + log được đính vào PLAN làm bằng chứng SC-004.

Prose: Vòng khép kín — chính trang tài liệu hoá đề xuất này trở thành vật chứng đầu tiên cho đề xuất, thay vì chỉ có lời hứa trong SPEC.

## Requirements (FR)
- **FR-001**: Toggle sáng/tối trong `docs-site-macos` PHẢI kích hoạt hiệu ứng circle-reveal thay cho đổi `data-theme` tức thời.
- **FR-002**: Vòng tròn xuất phát từ toạ độ nút toggle thật (không phải giữa màn hình cố định).
- **FR-003**: Màu nền vòng tròn = màu nền của MODE ĐÍCH (mode sắp chuyển tới), không phải mode hiện tại.
- **FR-004**: Animation có 2 pha tốc độ rõ rệt — lan chậm lúc đầu rồi nhanh-dứt-khoát phủ hết viewport (easing phi tuyến, không dùng `linear`).
- **FR-005**: `data-theme` + `localStorage` phải đổi giá trị TRƯỚC hoặc ĐÚNG lúc overlay bắt đầu fade — không được lộ nội dung mode cũ qua lớp overlay đang mờ dần.
- **FR-006**: Sau khi fade xong, overlay phải bị gỡ khỏi DOM hoàn toàn (không để lại phần tử che khuất tương tác).
- **FR-007**: `prefers-reduced-motion: reduce` PHẢI được tôn trọng — fallback về ≤150ms opacity crossfade, không ép hiệu ứng full-screen.
- **FR-008**: Trình duyệt không hỗ trợ Web Animations API (hiếm) → fallback đổi tức thời, không throw lỗi console, không kẹt overlay.
- **FR-009**: `_DARK_RULES`/generator (`fdk/tools/build-overstack-docs.py`) và snippet trong `SKILL.md` không được lệch nhau — một nguồn hoặc đồng bộ tường minh có ghi chú.
- **FR-010**: Phải có script Playwright độc lập verify được toàn bộ chuỗi hành vi FR-001 đến FR-008 trên bất kỳ file HTML nào `docs-site-macos` sinh ra.
- **FR-011**: Luật mới phải nằm ở nơi framework/downstream đọc được thật (skill + wiki của repo), không chỉ nằm trong memory cá nhân của agent.

## Success criteria (SC)
- **SC-001**: Người xem bấm nút chuyển giao diện trên bất kỳ trang do `docs-site-macos` sinh ra (kể từ bản này) thấy một vòng tròn màu (đúng màu nền mode đích) tỏa từ nút, lan nhanh dứt khoát phủ kín màn hình, mờ dần, rồi toàn trang đã ở mode mới — không còn cảm giác "chuyển cái rụp" tức thời như trước.
- **SC-002**: Người dùng đã bật "giảm chuyển động" (`prefers-reduced-motion: reduce`) ở hệ điều hành vẫn chuyển được mode, chỉ với hiệu ứng mờ ngắn, không bị ép chịu hiệu ứng full-screen họ không muốn.
- **SC-003**: Agent/dev tạo trang mới bằng `/docs-site-macos` từ giờ trở đi không cần tự nghĩ lại hiệu ứng — snippet đã có sẵn trong skill, copy đúng là chạy đúng ngay.
- **SC-004** *(bằng chứng máy cho SC-001/SC-002)*: `node skills/docs-site-macos/scripts/verify-theme-motion.mjs <file.html>` chạy Playwright xác nhận đúng chuỗi hành vi FR-001→FR-008, thoát mã 0 khi đạt.

## Assumptions
- **(default)** Thời lượng animation ~450–600ms tổng (lan chậm ~150ms đầu, nhanh-dứt-khoát phần còn lại), fade ~150–200ms sau khi phủ hết viewport — user không cho số cụ thể; đây là khoảng hợp lý theo cảm nhận UX phổ biến cho hiệu ứng "lan rồi dứt khoát", dễ chỉnh 1-2 dòng ở T1 nếu user muốn khác.
- **(default)** Luật mới chỉ áp cho trang sinh ra từ bản cập nhật này trở đi — không hồi tố ép build lại hàng loạt trang HTML cũ trong `llmwiki/html/` (đã ghi ở Non-goals).
- **(default)** Chọn phương án B (DOM overlay + WAAPI) thay vì A (View Transitions API) vì cần Playwright assert được trực tiếp — xem lý do đầy đủ ở `## Approaches`.
- **(default, find-out-later → U-01)** Phạm vi "toàn bộ ứng dụng đang xài framework này" trong yêu cầu gốc của user: SPEC này hiểu là "mọi trang ĐÃ theo luật `html-theme-toggle-required` (docs/report/dashboard framework sinh, và downstream tự thêm toggle theo cùng luật đó)" — KHÔNG mở rộng thành "mọi trang `hallmark` build (kể cả landing/marketing site vốn không có toggle theo thiết kế) giờ bắt buộc phải có toggle". Nếu user muốn mở rộng bắt buộc-có-toggle sang cả phạm vi hallmark, đó là một quyết định lớn hơn (đổi luật of hallmark, không phải chỉ đổi cách animate) — cần một `/propose` riêng. Ghi nợ: `U-01`.
- **(default)** Không biến script T4 thành gate CI/pre-commit bắt buộc ở bản này (đã ghi ở Non-goals) — nếu về sau muốn nâng cấp, đó là việc mở rộng `verify-before-commit`/`medic`, ghi thành đề xuất riêng.

## Self-review
1. **Phủ yêu cầu** — user hỏi 3 việc: (a) đổi luật xuyên suốt framework + downstream → FR-001…FR-011 + T1, T3, T5; (b) motion cụ thể (circle màu nền mode đích, tỏa từ nút, lan chậm-rồi-nhanh, fade, xong mới chuyển hẳn) → FR-002…FR-006, Approaches; (c) nghiệm thu bằng Playwright trên trang docs-site-macos sinh ra "từ lúc này" → FR-010, T4, T6, SC-004. Cả 3 đều có task/FR tương ứng, không rơi rớt.
2. **Quét placeholder** — đã soát toàn draft, mọi chỗ mơ hồ đã được thay bằng giá trị cụ thể ngay tại chỗ; mỗi task nêu rõ file + hành vi thật, không câu nào cần đoán thêm.
3. **Nhất quán tên-kiểu** — dùng thống nhất `theme-reveal` (tên class overlay), `flip()` (tên hàm hiện có bị bọc lại, không đổi tên để giữ tương thích chỗ khác gọi tới nó nếu có), `verify-theme-motion.mjs` (tên script) xuyên suốt Plan/FR/SC, không đổi tên giữa chừng.

## Origin
- **Draft:** `wiki/sources/draft/160926-theme-toggle-circle-reveal-motion.md`
- **Commit:** _(filled by `verify-before-commit`)_
- **Date promoted:** _(filled by `verify-before-commit`)_
