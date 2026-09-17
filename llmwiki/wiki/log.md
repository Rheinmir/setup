
## 2026-09-16 — extract+redesign — skill riêng `dark-mode-maker`, palette trung tính, cursor-origin, bỏ ripple-đuổi

User 3 yêu cầu liên tiếp: (1) "chọn màu dark mode... vẫn dở tệ, chọn lại theo thị trường" (2) "hình tròn không bắt đầu từ tâm nút mà từ vị trí con trỏ, kẹp trong biên nút" (3) "hiệu ứng lag quá... sóng bay nhanh hơn khối trắng đằng sau, không đúng — phải tạo hiệu ứng TRÊN khối trắng" (4) "bê nguyên cái làm hiệu ứng dark/light mode thành 1 skill riêng /dark-mode-maker".

**Palette:** nền/viền/chữ nền tảng đổi từ navy-tinted (`#0c0f16`, border `rgba(120,160,220,.18)` xanh bão hoà) sang trung tính kiểu GitHub Dark/Vercel/Linear (`#09090b`, border `rgba(255,255,255,.10)` trắng trong suốt). Accent giữ nguyên (không phải phần "tệ").

**Cursor-origin:** `flip(e)` giờ nhận event, đọc `e.clientX/clientY`, kẹp (`Math.min/Math.max`) trong `getBoundingClientRect()` của nút; Enter/Space (không toạ độ chuột) rơi về tâm nút.

**Bỏ ripple-đuổi, thay crest-glow:** thiết kế trước spawn 3 `<div>` viền riêng, tỏa NHANH HƠN dòng chính bằng `backdrop-filter:blur` riêng từng cái — lag thật (nhiều blur lớn/frame) + lệch đồng bộ đúng như user quan sát. Thay bằng `filter:drop-shadow(...)` 3 lớp NGAY TRÊN `.theme-reveal` — drop-shadow bám theo rìa đã `clip-path`, cùng 1 phần tử/1 animation nên tự động đồng bộ 100%, không backdrop-filter nào, không phần tử phụ.

**Tách skill:** `skills/dark-mode-maker/` (canonical + mirror + `scripts/verify-theme-motion.mjs` viết lại — assert cursor-origin, clamp, crest-glow, KHÔNG còn `.theme-ripple`). `docs-site-macos/SKILL.md` § Theme Toggle giờ chỉ còn con trỏ ngắn trỏ sang skill mới (một nguồn, sửa một chỗ). Đăng ký đủ 4 bề mặt (`LOOP_MAP`, `marketplace.json`, `AGENT.md`/`CLAUDE.md`, `LOOP_GROUPS` mind-map) qua đúng flow `new-skill` + `sync-skills.py`. `npx skills add . --global --all` để skill thật sự tới máy (fresh-install-smoke ban đầu ĐỎ vì thiếu bước này, đúng thiết kế của chính repo, không phải bug). `capability-stamp` bump 1.3.95→1.3.96, `CAPABILITIES.md` regen.

Evidence: `verify-theme-motion.mjs` PASS cả 2 trang (cursor-origin đúng toạ độ, clamp đúng khi bấm ảo ngoài biên, crest-glow có filter, 0 `.theme-ripple` sót lại). `medic --ci`: 0 fail. `sync-skills.py --check` + `skill-registry.py --check`: sạch.

## 2026-09-16 — upgrade — circle-reveal thành "giọt nước rơi" + gợn liquid-glass (2 bug thật bắt được lúc làm)

User: "nâng cấp hoạt ảnh, nhiều gợn và liquid glass". Thêm 3 vòng `.theme-ripple` (tái dùng công thức Ripple ink đã có) tỏa NHANH HƠN + XA HƠN dòng chính `.theme-reveal` rồi tan. Chụp ảnh thật lộ 2 bug ngay trong lúc build (không phải đoán): (1) `z-index` gợn (299) THẤP hơn dòng chính (300) → flood vẽ đè lên gợn, không hề thấy gì — sửa lên 301. (2) easing `cubic-bezier(.3,0,.1,1)` co gần hết progress trong ~20% thời lượng đầu rồi phẳng lì (không phải "chậm rồi nhanh" như định) — đổi sang `cubic-bezier(.42,0,1,1)` (ease-in chuẩn, chạy đều hết 560ms). (3) Gợn ban đầu là ĐĨA ĐẶC — vòng to vẽ sau che vòng nhỏ vẽ trước, chỉ thấy 1 vệt mờ — đổi sang VÒNG VIỀN (ring, giữa trong suốt, đúng hình dạng vật lý gợn nước thật) để nhiều vòng lồng nhau vẫn thấy hết. Mở rộng `verify-theme-motion.mjs` assert cả `.theme-ripple` (tồn tại/position:fixed/backdrop-filter, tự dọn sau fade, KHÔNG xuất hiện ở nhánh reduced-motion). Sửa `skills/docs-site-macos/SKILL.md` (+ mirror) + `fdk/tools/build-overstack-docs.py` (regen `overstack.html`) + companion HTML — cả 3 nơi đồng bộ. `verify-theme-motion.mjs` + `check-theme-row.mjs` + `check-tag-contrast.mjs` PASS cả 2 trang, `medic --ci` 0 fail.

## 2026-09-16 — correction — .theme-row vẫn "khối kính mờ kép" dù background đã transparent thật

User vẫn thấy khối sau khi `background:transparent` đã đo PASS — đúng: `backdrop-filter:blur(14px)` RIÊNG trên `.theme-row` là thủ phạm. `nav` đã tự blur nền phía sau nó rồi; `.theme-row` (con của `nav`, không phải phần tử độc lập) chồng thêm 1 lớp blur nữa lên đúng vùng đó tạo ra dải "kính mờ kép" nhìn như khối tách rời dù 0 màu — chụp ảnh thật (`sidebar-dark-now.png`, trước/sau) xác nhận rõ. Bỏ hẳn `backdrop-filter` khỏi `.theme-row`, chỉ giữ đường viền mảnh phía trên. Sửa `skills/docs-site-macos/SKILL.md` (+ mirror) + `fdk/tools/build-overstack-docs.py` (regen `overstack.html`) + companion HTML. Cập nhật lại `check-theme-row.mjs` — assertion cũ ("phải có backdrop-filter") chính là giả định sai của vòng sửa trước, giờ đảo ngược thành "PHẢI không có". `verify-theme-motion.mjs` vẫn PASS cả 2 trang, `medic --ci` 0 fail.

## 2026-09-16 — correction — .theme-row background:inherit SAI, đổi transparent + fix --ink2 gốc

User chê `background:inherit` không seamless — đúng: `inherit` vẽ LẠI gradient của `nav` trên hộp nhỏ riêng của `.theme-row` (175×53), không phải lộ đúng pixel `nav` đã render phía sau, vẫn có thể lệch tông. Đổi `background:transparent` (giữ `backdrop-filter:blur` để mờ link cuộn qua bên dưới) — đo Playwright (`check-theme-row.mjs`, đọc `getComputedStyle`) xác nhận `rgba(0,0,0,0)` thật ở cả light/dark, cả 2 trang. Trong lúc đo lộ thêm bug: companion `seq.html` không hề có override `--ink2` cho dark mode (chữ `.lbl`/`nav a`/`.card li`/footer đều tối trên nền tối) — sửa 1 dòng ở gốc biến CSS thay vì vá từng selector, lan đúng ra mọi nơi dùng `var(--ink2)`. Sửa cả `skills/docs-site-macos/SKILL.md` (+ mirror) + `fdk/tools/build-overstack-docs.py` (regen `overstack.html`) + companion HTML. `verify-theme-motion.mjs` + `check-tag-contrast.mjs` + `check-theme-row.mjs` PASS trên cả 2 trang, `medic --ci` 0 fail.

## 2026-09-16 — correction — .tag dark-mode contrast (Playwright bắt được fix đầu SAI)

User đòi bằng chứng máy thay vì ảnh chụp cho fix "160926 .tag dark-mode" — viết `check-tag-contrast.mjs` (Playwright, tính WCAG contrast ratio thật) thì lộ ra: fix vòng 1 (chỉ nâng alpha nền, giữ `color:accent`) đo được **1.0-1.4:1** — mù chữ thật, ảnh chụp trông "có vẻ ổn" vì mắt bắt viền pill chứ không bắt chữ mờ. Vòng 2 (nâng alpha nền `.26` + chữ trắng) PASS accent tối nhưng **FAIL 2.0-2.3:1** với accent sáng (teal/green/orange — nền tint đậm ăn mất chỗ tương phản). Vòng 3 đúng: nền mỏng `.12` + viền đậm `.55` + chữ trắng `#f2f4f8` → đo lại PASS **11-16:1** cả 6 accent, cả `overstack.html` lẫn companion. Sửa tại `fdk/tools/build-overstack-docs.py` (`accent_css()`) + `skills/docs-site-macos/SKILL.md` (+ mirror) + companion HTML. Bài học ghi thẳng vào SKILL.md để không lặp lại 2 lần sai đã đo được. `medic --ci` 0 fail, `verify-theme-motion.mjs` vẫn PASS trên cả 2 trang sau mọi vòng sửa.

## 2026-09-16 — follow-up — theme-toggle-circle-reveal-motion (design feedback sau khi graph done)

User soi trực tiếp trang companion, bắt 2 bug thật sau khi graph đã `done`: (1) `.tag` section-accent trên dark mode gần vô hình (bug hệ thống — tồn tại cả ở `overstack.html` thật, không riêng companion) → sửa tại nguồn: `accent_css()` trong `fdk/tools/build-overstack-docs.py` + tài liệu hoá vào `skills/docs-site-macos/SKILL.md` § CSS Generator Pattern (+ mirror), regen `overstack.html`. (2) 6 diagram archify dùng title/label ASCII-hoá (lỗi của agent, không phải giới hạn archify) → viết lại đầy đủ dấu tiếng Việt, render+visual-check lại cả 6. Archify iframe chrome (toolbar trắng, cross-origin) xác nhận lại là NGOÀI PHẠM VI — không hack, đề nghị `/raise-issue` riêng cho fork `Rheinmir/archify`. `medic --ci` + `verify-theme-motion.mjs` vẫn PASS sau mọi sửa.

## 2026-09-16 — plan+execute — theme-toggle-circle-reveal-motion-PLAN

PLAN 6 task cho `T-260916-01`, user duyệt và ra lệnh làm luôn ("duyệt làm đi chứ") — đã CHẠY THẬT, không chỉ viết kế hoạch: T1 snippet circle-reveal vào `skills/docs-site-macos/SKILL.md` (+ fix `.theme-row{background:inherit}` từ feedback design giữa chừng), T2 sync mirror, T3 phát hiện+sửa drift thật ở `fdk/tools/build-overstack-docs.py` (JS `flip()` trùng lặp), T4 viết `skills/docs-site-macos/scripts/verify-theme-motion.mjs`, T5 cập nhật `fdk.md`+`skills/fdk/SKILL.md`+memory cá nhân, T6 patch companion HTML + verify PASS. `medic --ci`: 0 fail. Verify script PASS thật trên `overstack.html` và companion HTML (2 lần, đều real Playwright/Chromium, không phải mô tả).

## 2026-09-16 — propose — theme-toggle-circle-reveal-motion

Draft `160926-theme-toggle-circle-reveal-motion.md` (task `T-260916-01`): đổi luật chuyển dark/light của `docs-site-macos` (+ mọi trang tuân `html-theme-toggle-required`) từ flip tức thời sang circle-reveal (vòng tròn màu mode đích, tỏa từ nút, lan chậm rồi nhanh-dứt-khoát phủ viewport, fade), cộng script Playwright `verify-theme-motion.mjs` nghiệm thu được. 6 task, companion HTML `160926-theme-toggle-circle-reveal-motion-seq.html` (6 sequence diagram archify). STOP chờ duyệt.

## 2026-09-16 — lint (partial: drift trên `concepts/`, chưa rà `sources/draft/`)

**Trigger:** `harness/trace-grader.config.yaml` sửa (bỏ tool giả `force_push`/`rm_rf`/`prod_write`) + `harness/scripts/trace-grader.py` (`self_test()` hết phụ thuộc config sống) → wiki-sync báo drift 193 file kể từ neo `7ff763bbd7` (2026-09-09), cờ 119 trang.

**Đã rà + sửa thật (10 trang `concepts/` — canonical home, drift ở đây mới ăn tiền):**
- `concepts/decision-anchoring.md` — 2 anchor STALE thật (`stop-debounce`, `code-graph-probe-boundary`), đối chiếu code hiện tại xác nhận WHY vẫn đúng (chỉ dịch số dòng do thêm `_debounce_path()` cho dot-layout) → re-confirm `confirmed:` trong `harness/mechanisms.yaml` lên 2026-09-16, `decision-liveness.py check` xác nhận cả hai LIVE trở lại.
- 9 trang còn lại (`adapt-modes`, `ci-issue-loop`, `commit-dag-hub`, `design-foundation`, `evidence-terminal-chain`, `graph-model`, `log-model`, `provenance-log`, `skill-craft`, `wiki-core-relations`) — đối chiếu diff thật của file gây cờ: đều là log/index tự sinh lớn thêm (không phải claim sai) hoặc thay đổi không chạm mảng mà trang mô tả (vd `diff-jail` mới thêm vào `loop-runner.py` không đụng tính năng `hub` mà `commit-dag-hub.md` nói tới). No-op hợp lệ, không sửa.

**CHƯA rà (nợ mở, việc riêng):** 57 trang `sources/draft/*` (đa số PLAN/proposal đã đóng dấu ngày, gần giống provenance — ít rủi ro nhưng chưa xác nhận) + 52 trang `sources/*session-provenance*.md` (snapshot tĩnh theo thiết kế, không cần rà). Chưa `--mark-synced` vì phần này chưa xong — chạy lại `/lint` full để đóng nốt.

<!-- log:auto:start -->

### 🤖 Log tự-động (code-logger, không do agent ghi)

| Thời điểm | Event | Chi tiết |
|---|---|---|
| 2026-09-16 17:21:31 | `file.write` | skills/dark-mode-maker/scripts/verify-theme-motion.mjs · tool=Edit · session=3125fa29 · actor=agent · prev=bd861b8da6f9a |
| 2026-09-16 17:21:31 | `file.write` | skills/dark-mode-maker/scripts/verify-theme-motion.mjs · tool=Edit · session=3125fa29 · actor=agent · prev=e6dea3ca25ae9 |
| 2026-09-16 17:24:43 | `file.write` | skills/dark-mode-maker/scripts/verify-theme-motion.mjs · tool=Edit · session=3125fa29 · actor=agent · prev=89909904777b1 |
| 2026-09-16 17:24:43 | `file.write` | skills/dark-mode-maker/scripts/verify-theme-motion.mjs · tool=Edit · session=3125fa29 · actor=agent · prev=8b6369c688dc6 |
| 2026-09-16 17:26:45 | `file.write` | skills/dark-mode-maker/scripts/verify-theme-motion.mjs · tool=Edit · session=3125fa29 · actor=agent · prev=60877fc8132a7 |
| 2026-09-16 17:26:45 | `file.write` | skills/dark-mode-maker/scripts/verify-theme-motion.mjs · tool=Edit · session=3125fa29 · actor=agent · prev=62e959777e275 |
| 2026-09-16 17:27:31 | `file.write` | skills/dark-mode-maker/SKILL.md · tool=Edit · session=3125fa29 · actor=agent · prev=7e819ca493feafe4b23da1136cf34943a2e7 |
| 2026-09-16 17:27:31 | `file.write` | skills/dark-mode-maker/SKILL.md · tool=Edit · session=3125fa29 · actor=agent · prev=fc368f53979ff36130a0effe4e6c21a997ad |
| 2026-09-16 17:27:48 | `file.write` | skills/dark-mode-maker/SKILL.md · tool=Edit · session=3125fa29 · actor=agent · prev=701bfc4d1fa9cfcb67d0b80c01fa01f84608 |
| 2026-09-16 17:27:48 | `file.write` | skills/dark-mode-maker/SKILL.md · tool=Edit · session=3125fa29 · actor=agent · prev=71187d79c6058a146f0e566b5c86a5030590 |
| 2026-09-16 17:38:13 | `file.write` | llmwiki/html/overstack.html · tool=Edit · session=3125fa29 · actor=agent · prev=aa146ad1e7d0665ae54826ebe59f5a1ec656d504 |
| 2026-09-16 17:38:13 | `file.write` | llmwiki/html/overstack.html · tool=Edit · session=3125fa29 · actor=agent · prev=c3a17d0f3731ca639cc72f03ee63fefa2ab10e1e |
| 2026-09-16 17:38:28 | `file.write` | llmwiki/html/overstack.html · tool=Edit · session=3125fa29 · actor=agent · prev=8fc7324e5da33a05d1945599a7ffd69e47519b8f |
| 2026-09-16 17:38:28 | `file.write` | llmwiki/html/overstack.html · tool=Edit · session=3125fa29 · actor=agent · prev=7e0e4c0a16560d5e60cba4a9ad70c4515b1ac98b |
| 2026-09-16 17:38:43 | `file.write` | llmwiki/html/overstack.html · tool=Edit · session=3125fa29 · actor=agent · prev=f9613a5e3302522428203646329cb675a3229655 |
| 2026-09-16 17:38:43 | `file.write` | llmwiki/html/overstack.html · tool=Edit · session=3125fa29 · actor=agent · prev=377bdebf000c9cf30a501e99a0340fbc55839057 |
| 2026-09-16 17:39:06 | `file.write` | skills/dark-mode-maker/SKILL.md · tool=Edit · session=3125fa29 · actor=agent · prev=750076a46acd08b172a67be9b4f943025128 |
| 2026-09-16 17:39:06 | `file.write` | skills/dark-mode-maker/SKILL.md · tool=Edit · session=3125fa29 · actor=agent · prev=bd20325731858ab4f0212548162103117569 |
| 2026-09-17 09:30:33 | `file.write` | fdk/tools/build-control-room.py · tool=Edit · session=3125fa29 · actor=agent · prev=b600485c5d0b7e0960393bef79c688228ca4 |
| 2026-09-17 09:30:33 | `file.write` | fdk/tools/build-control-room.py · tool=Edit · session=3125fa29 · actor=agent · prev=6d9c3c4f6d360ec9a071d2bd50ecb8d1fbaf |
| 2026-09-17 09:30:59 | `file.write` | fdk/tools/build-control-room.py · tool=Edit · session=3125fa29 · actor=agent · prev=d9975eeedaf9cffa9a8a8e5766ebea99f003 |
| 2026-09-17 09:30:59 | `file.write` | fdk/tools/build-control-room.py · tool=Edit · session=3125fa29 · actor=agent · prev=4872321da76f514c70750af4d03af956376f |
| 2026-09-17 09:31:08 | `file.write` | fdk/tools/build-control-room.py · tool=Edit · session=3125fa29 · actor=agent · prev=ce1d5d8247f0169f0f929c917042f8adb7c8 |
| 2026-09-17 09:31:08 | `file.write` | fdk/tools/build-control-room.py · tool=Edit · session=3125fa29 · actor=agent · prev=b30a7f2b3075db95149c72e90c6317c061c6 |
| 2026-09-17 09:31:19 | `file.write` | fdk/tools/build-control-room.py · tool=Edit · session=3125fa29 · actor=agent · prev=7614d6ef8caed5f210a776c8400d151a1f0a |
| 2026-09-17 09:31:19 | `file.write` | fdk/tools/build-control-room.py · tool=Edit · session=3125fa29 · actor=agent · prev=ac38ba5116b4940449a88efde1d2b25cd35b |
| 2026-09-17 09:31:30 | `file.write` | fdk/tools/build-control-room.py · tool=Edit · session=3125fa29 · actor=agent · prev=e8eca3de129599a0f2b94d0807ff291b175b |
| 2026-09-17 09:31:30 | `file.write` | fdk/tools/build-control-room.py · tool=Edit · session=3125fa29 · actor=agent · prev=189852d46ea7500157c5c23b43a993cce08c |
| 2026-09-17 09:41:07 | `file.write` | llmwiki/wiki/sources/draft/170926-orca-graph-no-write-sandbox.md · tool=Write · session=3125fa29 · actor=agent · prev=16 |
| 2026-09-17 09:41:07 | `file.write` | llmwiki/wiki/sources/draft/170926-orca-graph-no-write-sandbox.md · tool=Write · session=3125fa29 · actor=agent · prev=6e |
| 2026-09-17 09:41:34 | `file.write` | llmwiki/wiki/sources/draft/170926-orca-graph-no-separate-qc-role.md · tool=Write · session=3125fa29 · actor=agent · prev |
| 2026-09-17 09:41:34 | `file.write` | llmwiki/wiki/sources/draft/170926-orca-graph-no-separate-qc-role.md · tool=Write · session=3125fa29 · actor=agent · prev |
| 2026-09-17 09:42:04 | `file.write` | llmwiki/wiki/sources/ISSUES.md · tool=Edit · session=3125fa29 · actor=agent · prev=60eafd343e9e84b8438b78745063d820de8a4 |
| 2026-09-17 09:42:04 | `file.write` | llmwiki/wiki/sources/ISSUES.md · tool=Edit · session=3125fa29 · actor=agent · prev=f39004edfc0b329b98f0e3ac6d6a6dbed5b65 |
| 2026-09-17 09:42:20 | `commit.reconcile` |  · actor=system · agent_n=1 · human_n=0 · prev=b83402a96484b686916dd562f7339aef0d3a9673320fcca0f3c1ad09332f338e · h=3ceb |
| 2026-09-17 09:42:20 | `commit.reconcile` |  · actor=system · agent_n=4 · human_n=0 · prev=3cebdb0a7a45b59307aecdb5ea39c030276dfd6768ca0a1bd92d786c3842d2c3 · h=601f |
| 2026-09-17 09:43:21 | `file.write` | llmwiki/wiki/index.md · tool=Edit · session=3125fa29 · actor=agent · prev=601f9a00ef0547fd387671e4f133380e657b2c317229a3 |
| 2026-09-17 09:43:21 | `file.write` | llmwiki/wiki/index.md · tool=Edit · session=3125fa29 · actor=agent · prev=7a8b80778e2a9f38203b8c5d81a9ae83c573aa683a4d2c |
| 2026-09-17 09:43:28 | `commit.reconcile` |  · actor=system · agent_n=0 · human_n=2 · human=['llmwiki/wiki/sources/draft/160926-theme-toggle-circle-reveal-motion.md |
| 2026-09-17 09:43:28 | `commit.reconcile` |  · actor=system · agent_n=1 · human_n=3 · human=['llmwiki/wiki/sources/draft/160926-theme-toggle-circle-reveal-motion-PL |

<!-- log:auto:end -->
