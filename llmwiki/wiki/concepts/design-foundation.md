---
type: concept
title: "Design foundation — nền chung cho mọi UI (hallmark là sàn, taste là flavour)"
status: active
tags: [design, slop-test, hallmark, frontend, foundation]
timestamp: 2026-07-15
---

# Design foundation — một sàn chung, nhiều gu bên trên

Overstack có nhiều skill design (`design-taste-frontend`, `high-end-visual-design`, `docs-site-macos`, `gpt-taste`, `minimalist-ui`, `industrial-brutalist-ui`, `brandkit`, `redesign-existing-projects`…). Mỗi cái mang một **gu** thật mà người dùng chọn có chủ ý — brutalist, editorial, glass, high-end agency. Chúng không sai. Cái từng thiếu (vấn đề `p-23`) là **một sàn chung**: không có nền, mỗi skill tự bịa luật, và HTML do chính framework tự sinh không bị soi cùng chuẩn với UI giao user.

`hallmark` (Together AI, hấp thụ 2026-07-15) là sàn đó. Mọi skill design đứng **trên** nó, không cạnh tranh với nó.

## Sàn: 6 discipline + slop-test

Sàn không phụ thuộc verb hay gu — nó áp cho mọi output UI. Nguồn đầy đủ: `skills/hallmark/references/slop-test.md` (57 cổng + pre-emit critique 6 trục) và `references/anti-patterns.md`.

1. **Pre-emit self-critique** — trước khi trả về bất kỳ output nào, chấm 1–5 trên sáu trục (Philosophy · Hierarchy · Execution · Specificity · Restraint · **Variety**). Bất kỳ trục nào < 3 → một lượt revise trước khi quét cổng. Stamp sáu điểm ở đầu artifact.
2. **Honest copy** — không bịa số liệu. `+47% conversion`, `trusted by 50,000+` là slop ngay khi được bịa ra. Dùng số thật, hoặc placeholder có nhãn, hoặc đổi macrostructure. (Khớp anti-fabrication ta đã có.)
3. **Locked tokens** — mọi màu và mọi `font-family` qua một biến có tên (`var(--color-accent)`). Không hex/OKLCH/`rgb()` inline giữa render.
4. **No re-drawn chrome** — cấm vẽ tay fake browser bar (URL pill + traffic-light dots), fake phone frame, fake code-window. Môi trường của user đã có chrome thật.
5. **Mobile bốn width** — verify ở 320/375/414/768px. Không horizontal scroll; không clickable-text hai dòng; grid ảnh dùng `minmax(0,1fr)`.
6. **No italic header** — heading luôn roman. Italic emphasis trong heading (`Built to <em>think</em>`) là một trong những dấu hiệu AI đáng tin nhất. Nhấn bằng weight/màu/underline; italic chỉ sống trong body-copy.

## Cưỡng chế: cổng tất định + bộ nhớ Variety

- **`fdk/tools/frontend-antipattern.py`** — cổng tất định (wired vào `medic` probe `p_frontend`) mang nhóm slop-test **grep được**: gradient text, font AI-default làm display, pure `#000`/`#fff`, italic header, fake chrome, card-in-card, số liệu bịa. Cổng **universal** áp mọi HTML ta sinh; cổng **genre/structural** (cần một brief thật) không áp cho artifact kỹ thuật (seq.html/report — có glass riêng, R11).
- **Bộ nhớ Variety travel-được** — mỗi HTML sinh ra stamp macrostructure/theme của nó (theo repo, xuyên phiên). Cổng Variety đọc nó → trang mới phải khác **cấu trúc** trang trước, không phải colour-swap. Đây là thứ đưa slop-test từ một-lần thành liên-tục.

## Sàn vs flavour — ranh giới

- **Sàn (hallmark):** 6 discipline + slop-test. Không thương lượng. Mọi UI phải vượt.
- **Flavour (skill taste):** gu cụ thể lên trên sàn — palette, type-pairing, motion, không khí. Skill taste **thêm** lên sàn, **không thay** sàn.
- **Ngoại lệ có tên:** `docs-site-macos` là theme của TA cho **artifact nội bộ** (seq/report/dashboard/proposal render), không phải UI sản phẩm giao user. Nó không bị hallmark thay — nó phục vụ máy-đọc/tham-chiếu, tuân R11 glass. Cổng universal vẫn áp cho nó (không fake chrome, không gradient text), cổng genre thì không.

## Đối chiếu frontend-design (Anthropic) — 2026-07-17

Skill `frontend-design` chính thống của `anthropics/skills` được đối chiếu từng luật với sàn (T-260717-02, adapt_mode: dissolve). Kết quả: **4 cụm sàn thiếu** được absorb làm checkpoint — ba cụm default-AI-look có tên (kem+serif+đất-nung / gần-đen+acid / broadsheet), hero-là-thesis, signature-element (tiêu boldness đúng một chỗ), UX-writing theo hành động — và **6 cụm trùng** sàn không absorb lại. Delta đầy đủ: `skills/hallmark/references/frontend-design-delta.md`.

## Đối chiếu effective-html (Plannotator) — 2026-09-15

Repo `plannotator/effective-html` (MIT, sáu skill: `html` router + `design-artifact` + `html-wireframe`/`html-prototype`/`html-plan`/`html-diagram`) được đối chiếu với sàn (adapt_mode: dissolve — user yêu cầu trực tiếp "hoà tan hết, làm luật tham chiếu"). Trục của nó khác `frontend-design`: **chọn ĐÚNG DẠNG artifact HTML và chứng minh nó đủ trạng thái** trước khi tính tới thẩm mỹ — palette/typography là chuyện của mục trên, mục này là chuyện cấu trúc/hành vi.

**Cụm trùng, không absorb lại:** phần thẩm mỹ chống-AI-slop của `design-artifact` (kem+serif+đất-nung, gần-đen+acid, gradient tím-xanh hero, font "an toàn" Inter/Space Grotesk, emoji làm section marker, `rounded-lg` rải khắp, thẻ có accent-bar, ép căn giữa toàn trang) đã nằm trong slop-test 57 cổng + 3 cụm default-AI-look đã absorb từ `frontend-design` ở trên — cùng một danh sách, khác cách diễn đạt.

**Bốn cụm sàn thiếu, absorb làm luật mới:**

1. **Router theo DẠNG, không theo trang.** Trước khi vào bước thị giác, xác định artifact đang là gì — report/tool (văn xuôi, giữ nguyên), wireframe (thử cấu trúc), prototype/mockup (thử hành vi hoặc thị giác), plan (giữ commitment nguồn), hay diagram (xem mục Đối chiếu ngữ pháp sơ đồ trong `skills/diagram/SKILL.md`). Sai dạng thì mọi luật thẩm mỹ phía sau đều lạc đề.
2. **Kỷ luật độ nét (fidelity) hai đầu.** *Wireframe* phải CỐ Ý CHƯA XONG — grayscale, viền trơn, không gradient/shadow/minh hoạ — và khi cấu trúc còn mở, dựng 2–3 hướng khác nhau thật sự (đổi mô hình điều hướng/nhóm/mật độ, không phải đổi màu) trong CÙNG một file có bộ chọn gõ-bàn-phím được. *Prototype/mockup* ở đầu kia phải liệt kê trước rồi dựng đủ các trạng thái mà kịch bản thật sự chạm tới: loading, empty, error, success, disabled, mobile, cộng trạng thái riêng của miền — thiếu một trạng thái mà kịch bản chạm tới là artifact chưa xong, không phải "để sau".
3. **Plan giữ nguyên commitment nguồn.** Một plan/roadmap render ra HTML không được tự bơm thêm progress-bar, badge trạng thái, hay tóm tắt kiểu dashboard khi nguồn không có số đó — đúng tinh thần chống-bịa-số đã có ở mục Honest copy, áp riêng cho thể loại plan. Phải tách rõ ba loại: quyết định đã chốt, giả định, câu hỏi còn mở; giữ đúng thứ tự và ngôn ngữ nguồn trừ khi user yêu cầu tổng hợp rộng hơn.
4. **Verify trung thực, không lấy đọc-tĩnh thay test-trên-trình-duyệt.** Kiểm ở hai bề rộng màn hình, đi hết `Tab`/`Shift+Tab`/`Enter`/`Escape`, xác nhận dialog bẫy focus và trả focus về đúng nút đã mở nó, và soi màu chữ TÍNH RA (computed) trên từng nền — chữ kế thừa màu body giữa một vùng tối màu là lỗi hay lọt nhất. Không có công cụ trình duyệt thì phải NÓI RÕ phần chưa kiểm chứng được, không được ngầm coi đọc code là đã verify — cùng tinh thần "báo cáo của user thắng cổng xanh máy" đã có trong framework.

Không absorb: cơ chế phát hành `tot`/`tot.page` của Plannotator (ngoài phạm vi, ta không dùng), và các file `agents/openai.yaml` (adapter riêng cho Codex, không áp dụng ở đây).

## Origin
- Chưng cất từ `Nutlope/hallmark` (Together AI) — `skills/hallmark/references/slop-test.md` + `anti-patterns.md` (clone `scratchpad/hallmark/`, 2026-07-15).
- Absorb qua `/propose` → `150726-hallmark-design-foundation` (T2), task `T-260715-02`. Đóng `p-23`.
- Absorb `plannotator/effective-html` (MIT) 2026-09-15 qua `/orca-graph` (yêu cầu trực tiếp, adapt_mode dissolve) — clone tạm `scratchpad/effective-html-src/`, xoá sau khi chưng cất; luật mới ghi ở mục "Đối chiếu effective-html" trên và trong `skills/diagram/SKILL.md`.
- **Commit:** _(verify-before-commit điền)_
