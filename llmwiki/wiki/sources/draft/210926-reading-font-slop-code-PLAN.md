---
type: draft
title: "PLAN — đổi font mặc định mọi HTML framework sinh sang Be Vietnam Pro (theme đọc kiểu Vietcetera), và nghiên cứu luật slop nào kiểm được thuần bằng code, trước hết là luật 'đã bo tròn thì không thêm cạnh màu'"
status: approved
tags: [plan, orca-graph, font, typography, be-vietnam-pro, slop, frontend-antipattern, html-visual-gate]
timestamp: 2026-09-21
---

# PLAN 210926 — font đọc Be Vietnam Pro + luật slop kiểm bằng code

User giao ngày 21/09/2026: "lên task refactor toàn bộ bằng font family `/Users/giatran/Downloads/vietcetera-inspired-reading-theme.html` và study phần check slop trước có phần nào check thuần bằng code được không, đặc biệt là slop bo tròn thì không thêm cạnh màu".

Hiện trạng đo được lúc lập PLAN:
- Font của mọi HTML framework sinh đi qua MỘT nguồn `fdk/tools/html_font.py` (Lexend Deca 300, nhúng base64 từ `html_font_data.py`); 14 generator gọi nó. Repo engine `Rheinmir/orca-graph` mang bản sao `engine/html_font.py` + `engine/html_font_data.py` có kiểm parity.
- Theme mẫu dùng **Be Vietnam Pro** 400/500/600/700/800 cho mọi thứ, body 17px/1.75, heading 700–800 siết `letter-spacing` âm (-.035em tới -.055em). Be Vietnam Pro KHÔNG có bản variable → mỗi weight là một file.
- Cổng tĩnh đã có luật `side-stripe` (`fdk/tools/frontend-antipattern.py:351`) nhưng: đọc từng khai báo riêng lẻ (không gộp cascade), bỏ qua `blockquote`, không xét `border-radius`, không bắt kiểu `border:1px solid x; border-left-color: accent`. Cổng chạy thật (`fdk/tools/html-visual-gate.mjs`) chỉ bắt sọc vẽ bằng `::before/::after`.

Ngoài phạm vi (nói thẳng): bộ màu/giấy của theme mẫu (paper, đỏ, vàng) — user nói "font family", không nói palette; UI sản phẩm dự án khách (việc của `hallmark` theo `design.md` riêng).

## Global constraints
- Font vẫn NHÚNG base64 (user chốt "nhúng hết" 20/09): trang mở file://, offline vẫn đúng font; không gọi fonts.googleapis.com. Giấy phép SIL OFL 1.1, kèm NOTICE.
- Một nguồn duy nhất `fdk/tools/html_font.py`; không generator nào tự khai font-family. Bản sao engine phải khớp byte (parity test).
- Cổng trước, sửa sau: luật mới phải ĐỎ trên fixture XẤU và có số đếm trên trạng thái hiện tại trước khi sửa trang.
- Luật "bo tròn không thêm cạnh màu": phần tử có `border-radius` > 0 mà MỘT cạnh (hoặc hai cạnh kề) có viền màu khác các cạnh còn lại → FAIL, kể cả `blockquote`. Viền đều bốn cạnh, hoặc cạnh màu trên phần tử vuông góc, không thuộc luật này (vẫn chịu `side-stripe` cũ).
- Xong = cổng xanh CỘNG ảnh trước/sau cho user nhìn.
- Không AI-attribution trong commit (R15).

### Task 1: lấy và cắt font Be Vietnam Pro, đo cỡ để chốt số weight nhúng
**Kind:** research
**Thoả:** user 21/09 "refactor toàn bộ bằng font family vietcetera-inspired-reading-theme.html"
**Depends:** —
**Files:** fdk/tools/assets/fonts/BeVietnamPro-NOTICE.txt, fdk/tools/assets/fonts/
**Interfaces:**
- Consumes: —
- Produces: các file `BeVietnamPro-<w>-vi.woff2` (subset latin + tiếng Việt) + bảng cỡ từng weight; bộ weight nhúng (mặc định 400/600/800 nếu 5 weight vượt 150 KB tổng)
```bash
B=https://raw.githubusercontent.com/google/fonts/main/ofl/bevietnampro
for w in Regular SemiBold ExtraBold; do curl -fsSLO $B/BeVietnamPro-$w.ttf; done
python3 fdk/tools/html_font.py --rebuild <thư-mục-ttf>   # 400 30,4 KB · 600 32,2 KB · 800 32,7 KB
```
**Verify:** `ls fdk/tools/assets/fonts/BeVietnamPro-*-vi.woff2 && test -s fdk/tools/assets/fonts/BeVietnamPro-NOTICE.txt`

### Task 2: đổi nguồn font html_font.py sang Be Vietnam Pro
**Kind:** build
**Thoả:** user 21/09 "refactor toàn bộ bằng font family vietcetera-inspired-reading-theme.html"
**Depends:** Task 1 (data)
**Files:** fdk/tools/html_font.py, fdk/tools/html_font_data.py, harness/tests/test_html_font.py
**Interfaces:**
- Consumes: woff2 của Task 1
- Produces: `FAMILY="Be Vietnam Pro"`, một `@font-face` mỗi weight, token `--fw-text:400` · `--fw-strong:600` · `--fw-heading:700` · `--ls-heading` âm theo theme; `--rebuild` nhận nhiều file; `head_css()`/`apply()` giữ nguyên chữ ký
```python
FAMILY = "Be Vietnam Pro"
WEIGHTS = (400, 600, 800)
WEIGHT_TEXT, WEIGHT_STRONG, WEIGHT_HEADING = 400, 600, 800
TRACK_HEADING = "-.03em"          # chỉ h1/h2
def font_face() -> str:           # một @font-face mỗi weight, src base64 từ html_font_data.WOFF2_B64[w]
    ...
```
**Verify:** `python3 fdk/tools/html_font.py --check && python3 -m pytest -q harness/tests/test_html_font.py harness/tests/test_html_base.py`

### Task 3: lint font, tài liệu và skill theo font mới
**Kind:** docs
**Thoả:** user 21/09 "refactor toàn bộ bằng font family vietcetera-inspired-reading-theme.html"
**Depends:** Task 2 (contract)
**Files:** fdk/tools/html-font-lint.py, harness/tests/html-font-lint-test.sh, skills/docs-site-macos/SKILL.md, fdk/CAPABILITIES.md
**Interfaces:**
- Consumes: hằng `FAMILY`, `MARK` của Task 2
- Produces: xem Verify
```python
def _need() -> tuple:              # html-font-lint đọc hằng từ html_font, không ghi cứng tên font
    hf = _load(HERE / "html_font.py")
    return ('id="ovs-font"', hf.MARK, "data:font/woff2;base64,", f"--fw-text:{hf.WEIGHT_TEXT}")
```
**Verify:** `bash harness/tests/html-font-lint-test.sh && ! grep -n "Lexend" fdk/tools/html-font-lint.py skills/docs-site-macos/SKILL.md fdk/CAPABILITIES.md`

### Task 4: bản sao font ở repo engine orca-graph
**Kind:** integration
**Thoả:** user 21/09 "refactor toàn bộ bằng font family vietcetera-inspired-reading-theme.html"
**Depends:** Task 2 (contract)
**Files:** ~/.orca-graph/repo/engine/html_font.py, ~/.orca-graph/repo/engine/html_font_data.py, ~/.orca-graph/repo/engine/BeVietnamPro-NOTICE.txt
**Interfaces:**
- Consumes: `html_font.py` + `html_font_data.py` của Task 2
- Produces: xem Verify
```bash
cp fdk/tools/html_font_data.py fdk/tools/assets/fonts/BeVietnamPro-NOTICE.txt ~/.orca-graph/repo/engine/
# html_font.py / html_base.py: chép đè, giữ khối docstring "BẢN SAO" của engine
python3 fdk/tools/html-font-lint.py --parity
```
**Verify:** `cmp fdk/tools/html_font_data.py ~/.orca-graph/repo/engine/html_font_data.py && cd ~/.orca-graph/repo && python3 -m pytest -q tests/test_orca_graph.py -k font`

### Task 5: nghiên cứu — luật slop nào kiểm được thuần bằng code
**Kind:** research
**Thoả:** user 21/09 "study phần check slop trước có phần nào check thuần bằng code được không, đặc biệt là slop bo tròn thì không thêm cạnh màu"
**Depends:** —
**Files:** fdk/wiki/sources/210926-slop-code-checkable.md
**Interfaces:**
- Consumes: —
- Produces: bảng phân loại từng gate trong `skills/hallmark/references/slop-test.md` + luật hai cổng hiện có thành ba cột: tĩnh (regex/CSS parse) · chạy thật (computed style/hình học) · cần mắt; mỗi dòng nêu cách đo, đã có luật chưa, rủi ro báo giả; danh sách luật code-được CHƯA cài cho Task 7
```bash
python3 fdk/tools/frontend-antipattern.py --all --count
NODE_PATH=$(npm root -g) node fdk/tools/html-visual-gate.mjs <trang…> --json
```
**Verify:** `test -s fdk/wiki/sources/210926-slop-code-checkable.md && grep -q "bo tròn" fdk/wiki/sources/210926-slop-code-checkable.md`

### Task 6: luật 'bo tròn không thêm cạnh màu' ở cả hai cổng
**Kind:** build
**Thoả:** user 21/09 "study phần check slop trước có phần nào check thuần bằng code được không, đặc biệt là slop bo tròn thì không thêm cạnh màu"
**Depends:** —
**Files:** fdk/tools/frontend-antipattern.py, fdk/tools/html-visual-gate.mjs, harness/tests/test_frontend_antipattern_slop.py, harness/tests/html-visual-gate-test.sh
**Interfaces:**
- Consumes: —
- Produces: luật tĩnh `rounded-edge` (gộp khai báo theo selector, bắt cả `border-left-color` đè lên viền đều) + luật chạy thật `rounded-edge` (getComputedStyle: radius > 0 và cạnh lệch màu/độ dày, không miễn blockquote); fixture XẤU cắn, fixture TỐT sạch
```python
def _rounded_edge(decl: str):     # decl đã gộp theo selector; trả cạnh lệch hoặc None
    ...                            # radius > 0, không tròn (50% / ≥999px), 1–3 cạnh màu nhấn khác màu hoặc dày ≥ 1.5×
```
**Verify:** `python3 -m pytest -q harness/tests/test_frontend_antipattern_slop.py && bash harness/tests/html-visual-gate-test.sh`

### Task 7: cài các luật code-được còn thiếu mà Task 5 tìm ra
**Kind:** build
**Thoả:** user 21/09 "study phần check slop trước có phần nào check thuần bằng code được không, đặc biệt là slop bo tròn thì không thêm cạnh màu"
**Depends:** Task 5 (data), Task 6 (effect_order)
**Files:** fdk/tools/frontend-antipattern.py, fdk/tools/html-visual-gate.mjs, harness/tests/test_frontend_antipattern_slop.py, harness/tests/html-visual-gate-test.sh
**Interfaces:**
- Consumes: danh sách luật chưa cài của Task 5
- Produces: mỗi luật mới có fixture XẤU cắn + TỐT sạch
```python
_TRANS_ALL = re.compile(r"(?<![\w-])transition(?:-property)?\s*:\s*all\b", re.I)
# chạy thật: italic-display · uppercase-tight-leading (MEASURE) · horizontal-scroll · clickable-wrap (LAYOUT 320/375/768/1360)
```
**Verify:** `python3 -m pytest -q harness/tests/test_frontend_antipattern_slop.py && bash harness/tests/html-visual-gate-test.sh`

### Task 8: sinh lại mọi trang, hai cổng xanh, trang ảnh trước/sau
**Kind:** test
**Thoả:** user 21/09 "refactor toàn bộ bằng font family vietcetera-inspired-reading-theme.html" · user 21/09 "study phần check slop trước có phần nào check thuần bằng code được không, đặc biệt là slop bo tròn thì không thêm cạnh màu"
**Depends:** Task 2 (data), Task 3 (acceptance), Task 4 (acceptance), Task 7 (acceptance)
**Files:** llmwiki/html/210926-font-slop-before-after.html
**Interfaces:**
- Consumes: —
- Produces: mọi trang generator sinh lại bằng font mới, hai cổng về 0, trang so sánh ảnh sáng/tối trước-sau
```bash
for t in build-overstack-docs build-docs-index build-control-room build-health-dashboard build-cheatsheet memory-map whiteboard-skill-map; do python3 fdk/tools/$t.py; done
for g in llmwiki/graph/*.graph.json; do python3 fdk/tools/graph-viz.py $g; done
python3 fdk/tools/html_font.py --apply llmwiki/html/*.html   # trang dựng tay: làm mới khối font/nền cũ
```
**Verify:** `python3 fdk/tools/frontend-antipattern.py --all >/dev/null; [ $? -ne 1 ] && bash harness/tests/html-font-lint-test.sh && test -s llmwiki/html/210926-font-slop-before-after.html`

### Task 9: review độc lập + medic --ci trước khi đẩy
**Kind:** review
**Thoả:** luật repo: đọc gate trước khi đẩy (memory repo-role-and-html-font)
**Depends:** Task 8 (acceptance)
**Files:** llmwiki/wiki/sources/draft/210926-reading-font-slop-code-review.md
**Interfaces:**
- Consumes: —
- Produces: xem Verify
```bash
python3 -m pytest -q harness/tests/test_html_font.py harness/tests/test_html_base.py harness/tests/test_frontend_antipattern_slop.py
bash harness/tests/downstream-slop-gate-test.sh
python3 fdk/tools/medic.py --ci
```
**Verify:** `test -s llmwiki/wiki/sources/draft/210926-reading-font-slop-code-review.md && python3 fdk/tools/medic.py --ci`

## Origin

- Yêu cầu user ngày 21/09/2026 (prompt cuối phiên `9b60028e`, bàn giao sang phiên `d3f387e6`), file mẫu `/Users/giatran/Downloads/vietcetera-inspired-reading-theme.html`.
- Hiện trạng đọc từ `fdk/tools/html_font.py`, `fdk/tools/frontend-antipattern.py:328-352`, `fdk/tools/html-visual-gate.mjs:1-12`, `~/.orca-graph/repo/engine/html_font.py`.
- PLAN liền trước cùng dòng việc: `200926-self-slop-gate-PLAN` (hai cổng slop), `200926-repo-role-ship-flows-PLAN` (font một nguồn).
