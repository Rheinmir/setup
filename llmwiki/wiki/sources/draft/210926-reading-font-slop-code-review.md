---
type: draft
title: "Review độc lập PLAN 210926 — font Be Vietnam Pro + luật slop kiểm bằng code (rounded-edge và 6 luật mới)"
status: recorded
tags: [review, font, be-vietnam-pro, slop, frontend-antipattern, html-visual-gate, orca-graph, parity]
timestamp: 2026-09-21
---

# Review độc lập — 210926 reading-font + slop-code

Phạm vi: `210926-reading-font-slop-code-PLAN.md`. Diff đọc: `fdk/tools/html_font.py`, `html_base.py`, `html-font-lint.py`,
`frontend-antipattern.py`, `html-visual-gate.mjs`, 5 file test, `skills/docs-site-macos/SKILL.md`, `fdk/tools/assets/fonts/*`;
repo engine `~/.orca-graph/repo` (`git diff` + file mới). Người review KHÔNG viết code này. Không sửa code, không commit.

## Đã chạy

| Lệnh | Kết quả |
|---|---|
| `pytest -q test_html_font.py test_html_base.py test_frontend_antipattern_slop.py` | 22 passed |
| `bash harness/tests/html-visual-gate-test.sh` (có Playwright) | 26 PASS · 0 FAIL · 0 SKIP |
| `bash harness/tests/downstream-slop-gate-test.sh` | PASS (cổng chạy thật SKIP vì script không thấy Playwright qua NODE_PATH của nó) |
| `bash harness/tests/html-font-lint-test.sh` | 6 PASS |
| `cd ~/.orca-graph/repo && pytest -q tests/` | 62 passed |
| `frontend-antipattern.py --all` | rc 2 (chỉ WARN), 0 hit rounded-edge / transition-all / reduced-motion-missing |
| Mô phỏng máy khách: copy riêng `fdk/tools/*.py` sang thư mục trống (không woff2) → `html_font.py --check`, `--apply`, `html-font-lint.py` | OK / nhúng được / 1/1 đạt |

## Kết luận các câu hỏi (a)–(e)

- (a) Regex làm mới khối `<style id="ovs-font">` / `"ovs-base"` (`html_font.py:85-87`, `html_base.py:102-106`): **ổn**. Nội dung hai khối là CSS do chính
  code sinh (`head_css()`/`base_css()`), không bao giờ chứa `</style`, nên non-greedy dừng đúng ở thẻ đóng của nó. Thay thế qua hàm/lambda nên
  không dính lỗi escape `\1` trong base64. Idempotent đã kiểm (`apply(apply(x)) == apply(x)`, kể cả nhánh `family_dark`). Quét mọi `*.html`
  đang track: không trang nào có marker `id="ovs-font"`/`id="ovs-base"` ngoài đúng một khối `<style>` → không có srcdoc/JS nào bị ăn nhầm ở trạng thái hiện tại.
- (c) Máy khách: `check()` chạy được khi thiếu woff2 (nhánh `exists()`), không ghi cứng đường dẫn repo framework trong các file đã đổi.
  `install.sh` engine đã đổi sang `BeVietnamPro-NOTICE.txt`; NOTICE hai repo khớp byte.
- (d) Còn nhắc Lexend là font hiện hành: chỉ một chỗ (F7). Các chỗ khác là comment/test nói về bản CŨ, đúng ngữ cảnh.

## Findings

### F1 — CHẶN (thứ tự đẩy) · repo engine chưa commit, pin framework vẫn trỏ bản Lexend
- File: `~/.orca-graph/repo` (git status: `M engine/html_font.py`, `engine/html_font_data.py`, `engine/html_base.py`, `install.sh`, `D engine/LexendDeca-NOTICE.txt`, `?? engine/BeVietnamPro-NOTICE.txt`); `fdk/skills.provenance.json:841-851` vẫn `commit 7b6eae7…`, `version 3.1.4`.
- Kịch bản hỏng: đẩy framework trước → máy khách cài engine theo pin cũ (Lexend) trong khi `html-font-lint` của framework lấy `MARK`/`WEIGHT_TEXT` mới
  (`'Be Vietnam Pro'`, `--fw-text:400`) → trang graph/atlas engine sinh ở máy khách rớt lint, `--parity` rc 2. Nếu đẩy engine mà quên `git add engine/BeVietnamPro-NOTICE.txt`
  thì `raw_install` (`install.sh:34`, `curl -fsSL`) gặp 404 → cài dở.
- Cách sửa: commit + tag engine (gồm NOTICE mới, xoá NOTICE cũ), push; rồi re-pin `skills.provenance.json` (commit + version) trước khi push framework.

### F2 — NÊN SỬA (bắt buộc kiểm trước commit) · file font mới chưa track, test "đồng bộ woff2" PASS giả khi thiếu file
- File: `fdk/tools/assets/fonts/BeVietnamPro-{400,600,800}-vi.woff2`, `BeVietnamPro-NOTICE.txt` đang `??` (chưa add), còn Lexend đã `D` staged.
  `fdk/tools/html_font.py:94` chỉ so woff2 khi `woff2(w).exists()`; `harness/tests/test_html_font.py:24-30` không assert file woff2 tồn tại.
- Kịch bản hỏng: commit quên ba file woff2 → trên repo framework `--check` vẫn OK (rơi vào nhánh "máy khách"), test "data module khớp woff2" vẫn xanh,
  `--rebuild`/`--sync` sau này không có nguồn. (Quên NOTICE thì test mới đỏ — woff2 thì không.)
- Cách sửa: `git add fdk/tools/assets/fonts/BeVietnamPro-*`; trong test repo thêm `assert all(hf.woff2(w).is_file() for w in hf.WEIGHTS)`.

### F3 — NÊN SỬA · rounded-edge báo giả trên spinner tải (cả hai cổng)
- File: `fdk/tools/frontend-antipattern.py:352-383` (`_rounded_edge`), `fdk/tools/html-visual-gate.mjs:105-113`.
- Kịch bản (đã chạy): `.sp{border:3px solid #e5e5e5;border-top-color:#0a84ff;border-radius:50%}` — spinner kinh điển, không phải sọc cạnh.
  Cổng tĩnh: `1 FAIL … → .sp (top)`; cổng chạy thật: `rounded-edge: … div.sp`, rc 2. Cổng tĩnh chạy ở máy khách (`downstream-slop-gate`) → chặn trang dự án khách có spinner.
- Cách sửa: miễn phần tử tròn (mọi góc radius ≥ 50% / ≥ min(w,h)/2 ở cổng chạy thật; `border-radius:50%` hoặc ≥ 999px ở cổng tĩnh) — hình tròn không có "cạnh" để làm sọc;
  thêm fixture spinner vào nhóm TỐT của cả hai test.

### F4 — NÊN SỬA · parity không so `base_css()` — thay đổi vừa làm ở lớp nền lọt qua được
- File: `fdk/tools/html-font-lint.py:45-47` chỉ so `LIGHT/DARK/KEY/STYLE_ID` của `html_base`.
- Kịch bản (đã chạy): copy engine sang thư mục tạm, xoá dòng `@media (prefers-reduced-motion: reduce)` khỏi `engine/html_base.py`,
  `ORCA_GRAPH_ENGINE_DIR=… html-font-lint.py --parity` → `✓ parity … khớp`, rc 0. Chính diff này thêm media query vào `base_css()` và đổi logic `apply()` —
  loại lệch không cổng nào bắt. (`head_css()` thì đã được so, `base_css()` chưa.)
- Cách sửa: thêm `if any(mb.base_css(family_dark=f) != tb.base_css(family_dark=f) for f in (True, False)): bad.append("html_base.base_css()")`.

### F5 — NÊN SỬA · rounded-edge tĩnh báo giả với màu viền `color-mix(...)`
- File: `fdk/tools/frontend-antipattern.py:364` (tách token `[\w-]+\([^)]*\)` dừng ở `)` đầu tiên) + `_neutral_edge`.
- Kịch bản (đã chạy `_rounded_edge`): `.row{border-radius:8px;border-bottom:1px solid color-mix(in srgb, var(--ink) 12%, transparent)}` → `'bottom'` (FAIL).
  Đây là đường kẻ xám mảnh kiểu hiện đại; cổng chạy thật (computed rgb) không báo, chỉ cổng tĩnh báo → FAIL ở máy khách.
- Cách sửa: coi `color-mix(` chứa `transparent` hoặc token trung tính (`var(--ink|--line|--border…)`) là trung tính; tối thiểu: mọi `color-mix(` → không kết luận (bỏ qua, để cổng chạy thật xử).

### F6 — GHI NHẬN · comment đo đạc t7 đã lỗi thời sau khi chính diff chèn media query vào lớp nền
- File: `fdk/tools/frontend-antipattern.py:474-479`: "html_base.py KHÔNG chèn sẵn media query … 20 trang WARN … ponytail: nâng nhánh transform lên FAIL khi 20 trang về 0".
- Thực tế `html_base.py:64-67` nay chèn `@media (prefers-reduced-motion: reduce)` vào MỌI trang qua lớp nền → nhánh WARN không bao giờ bắn trên trang framework;
  điều kiện "khi 20 trang về 0" đã đạt, người đọc sau sẽ hiểu sai trạng thái nợ.
- Cách sửa: cập nhật comment (số đo mới + lý do giữ/nâng mức).

### F7 — GHI NHẬN · nhãn CI còn ghi Lexend là font hiện hành
- File: `.github/workflows/harness.yml:233` — `html-font-lint — mọi HTML framework sinh ra = Lexend Deca Light NHÚNG …`.
- Không hỏng logic (chỉ là tên step), nhưng đọc log CI sẽ thấy luật sai. Cách sửa: đổi thành "font mặc định của html_font.py (Be Vietnam Pro)".

### F8 — GHI NHẬN · giới hạn đã biết của rounded-edge tĩnh (cổng chạy thật bù)
- `frontend-antipattern.py:422-428` gộp theo selector CHUẨN HOÁ nguyên văn: radius ở `.card`, cạnh màu ở `.card.warn` hoặc `[data-theme=dark] .card` → cổng tĩnh không thấy
  (fixture `rounded-edge-dark` chỉ chứng minh ở cổng chạy thật). `_RADIUS_DECL` coi mọi `var(` là bo góc > 0 → `border-radius:var(--r0)` với `--r0:0` + sọc trái bị báo rounded-edge thay vì side-stripe (vẫn FAIL, chỉ sai tên luật).
- Không cần sửa ngay; ghi vào `210926-slop-code-checkable.md` như giới hạn tĩnh.

### F9 — GHI NHẬN · điểm kiểm marker quét toàn trang, không chỉ `<head>`
- `html_font.py:85` và `html_base.py:102` kiểm `'id="ovs-font"' in html` trên TOÀN trang. Trang có chuỗi đó trong văn xuôi không escape nháy, hoặc trong srcdoc nháy đơn/JS template,
  sẽ (a) không được chèn font lần đầu, hoặc (b) bị `re.sub(count=1)` làm mới khối nằm trong JS thay vì head. Quét hiện tại: 0 trang dính, nên chỉ ghi nhận.
- Cách sửa nếu muốn chặn trước: tìm marker trong phần trước `</head>` (như `has_own_theme` đang làm).

## Không thấy vấn đề (đã soi, có căn cứ)

- Sáu luật mới: `transition-all` và `reduced-motion-missing` (tĩnh) có fixture XẤU/TỐT gồm cả biến thể dễ báo giả (`allow`, `--transition:all`, `<code>transition-all</code>` trong văn xuôi, `animation:none`, media query có sẵn).
  `italic-display`, `uppercase-tight-leading` (FAIL) và `horizontal-scroll`, `clickable-wrap` (WARN, rc 0) mỗi luật có cặp fixture; test WARN kiểm cả `rc = 0` lẫn dòng `⚠`, fixture TỐT kiểm không có `⚠` → không PASS giả do rc.
- `rounded-edge` chạy thật: fixture chỉ-ở-tối grep đúng `chỉ ở tối`, fixture đường kẻ xám không báo.
- Khớp weight: trang xin 500 → 400, 700 → 800 theo luật khớp font CSS; `.ovs-eyebrow{font-weight:500}` ra 400, không giả đậm.
- `html_font_data.py` hai repo khớp byte; `html_font.py`/`html_base.py` hai repo chỉ khác khối docstring "BẢN SAO".
- Máy khách (layout dot): các file đã đổi không ghi cứng đường dẫn repo; `graph-viz.py` fallback `~/.claude/harness/fdk/tools/html_font.py` giữ nguyên.

## Origin

- Việc giao: Task 9 của `llmwiki/wiki/sources/draft/210926-reading-font-slop-code-PLAN.md`, review độc lập trước khi đẩy, phiên `d3f387e6`, ngày 21/09/2026.
- Căn cứ: `git diff` hai repo (framework nhánh `orca`, engine `~/.orca-graph/repo` nhánh `main`), kết quả chạy test liệt kê ở mục "Đã chạy",
  thí nghiệm spinner/color-mix/parity trong scratchpad phiên (không ghi vào repo).
