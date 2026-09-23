---
type: draft
title: "PLAN — bộ khung trang tài liệu tự gắn: mọi quy định MUST của docs-site-macos mà máy làm được thì lớp nền tự chèn (sidebar icon + chip số + viên active, skip-link, main#main, favicon, scroll spy, ripple, nút sidebar mobile, mind map), phần còn lại gác bằng luật"
status: approved
tags: [plan, orca-graph, docs-site-macos, html-base, sidebar, a11y, slop]
timestamp: 2026-09-22
---

# PLAN 220926 — bộ khung trang tài liệu tự gắn

User ngày 22/09/2026, kèm ảnh sidebar trang `llmwiki/html/120926-downstream-layout.html`: "mấy nhãn trong sidebar này trông chán thế nhỉ", rồi "còn cái nào tương tự nữa không thì làm với tất cả 1 lượt luôn".

Gốc chung: skill `docs-site-macos` khai 13 luật MUST và nhiều thành phần REQUIRED (icon tile trong sidebar, mind map, ripple, scroll spy, skip-link…), nhưng chúng chỉ là VĂN XUÔI — agent dựng trang bỏ qua thì không gì bắt. Khảo sát ngày 22/09 (`scratchpad/shell-survey.py`) trên 39 trang có `<nav>`: thiếu icon tile 37 · main#main 36 · skip-link 35 · mind map 34 · ripple 32 · scroll spy 32 · sơ đồ kéo-thả 20 · favicon inline 17 · nút sidebar mobile 12. Copy button và `:focus-visible` đã đủ (0 thiếu).

Hướng: phần MÁY LÀM ĐƯỢC thì lớp nền `fdk/tools/html_base.py` tự chèn khi trang có sidebar kiểu docs-shell (một chỗ, mọi generator + `html_font.py --apply` + engine cùng nhận). Phần cần nội dung thì luật gác. Sidebar được làm lại theo khuôn Icon Tiles của skill.

Ngoài phạm vi (nói thẳng): luật quy trình không đo trên trang được (RULE-08 auto-host, RULE-09 audit Playwright — đã có hai cổng); trang có sidebar RIÊNG không theo khuôn docs-shell (control-room, trang graph của engine) — Task 1 chốt danh sách và lý do; font chữ trong chart (đang chờ user chọn).

## Global constraints
- Cổng trước, sửa sau: mỗi luật/phần chèn mới có số đếm ĐỎ trên trạng thái hiện tại (bảng khảo sát ở trên) trước khi sửa.
- Một nguồn: mọi thứ chèn nằm trong `fdk/tools/html_shell.py` (html_base gọi khi file có mặt — engine không mang file này nên trang graph không đổi, parity `html_base` giữ nguyên); idempotent và LÀM MỚI khối cũ như khối font/nền (PLAN 210926). Không chép CSS/JS vào từng generator.
- Không phá trang đang chạy: chỉ chèn khi trang THIẾU thành phần đó; trang đã tự có (vd overstack có scroll spy riêng) thì giữ nguyên.
- Sidebar mới phải qua hai cổng slop: không sọc viền một cạnh, không bo tròn kèm cạnh màu, contrast ≥ 4,5:1 ở cả sáng và tối.
- Xong = khảo sát về 0 trên trang docs-shell + hai cổng xanh + ảnh trước/sau.
- Bản sao ở engine orca-graph giữ parity (`html-font-lint --parity`).
- Không AI-attribution trong commit (R15).

### Task 1: chốt phạm vi docs-shell và biến khảo sát thành bộ đo có số đỏ
**Kind:** research
**Thoả:** user 22/09 "còn cái nào tương tự nữa không thì làm với tất cả 1 lượt luôn"
**Depends:** —
**Files:** fdk/tools/docs-shell-survey.py, fdk/wiki/sources/220926-docs-shell-baseline.md
**Interfaces:**
- Consumes: —
- Produces: `docs-shell-survey.py [--all] [--json]` — nhận diện trang docs-shell (có `<nav>` chứa `.logo` + ≥ 4 link `#sec-`), in bảng thiếu theo quy định; rc 2 khi có thiếu. Bảng baseline + danh sách trang loại trừ kèm lý do.
```python
def is_docs_shell(html: str) -> bool: ...        # <nav> có .logo và ≥ 4 <a href="#…">
CHECKS = {"icon-tile": ..., "skip-link": ..., "main-id": ..., "mind-map": ..., "ripple": ...,
          "scroll-spy": ..., "draggable": ..., "favicon": ..., "nav-toggle": ...}
```
**Verify:** `python3 fdk/tools/docs-shell-survey.py --all >/dev/null; [ $? -ne 1 ] && test -s fdk/wiki/sources/220926-docs-shell-baseline.md`

### Task 2: lớp nền chèn khung a11y + điều hướng cho trang docs-shell
**Kind:** build
**Thoả:** RULE-03 · RULE-06 của docs-site-macos (skip-link, main#main, favicon inline, nút sidebar mobile)
**Depends:** Task 1 (contract)
**Files:** fdk/tools/html_shell.py, fdk/tools/html_base.py, harness/tests/test_html_shell.py
**Interfaces:**
- Consumes: `is_docs_shell()` của Task 1 (chép logic, không import chéo tool)
- Produces: `html_base.apply()` chèn khi THIẾU: `<a class="skip-link" href="#main">`, `id="main"` cho vùng nội dung chính, `<link rel="icon" href="data:image/svg+xml,…">`, cặp `.nav-toggle`/`.nav-close` + JS; khối `<style id="ovs-shell">` + `<script id="ovs-shell-js">` làm mới được
```python
SHELL_STYLE_ID, SHELL_JS_ID = "ovs-shell", "ovs-shell-js"
def shell_css() -> str: ...
def shell_js() -> str: ...      # nav-toggle, scroll spy, ripple, progress
```
**Verify:** `python3 -m pytest -q harness/tests/test_html_shell.py harness/tests/test_html_base.py`

### Task 3: sidebar làm lại — icon tile, chip số, viên active, scroll spy, ripple, vạch tiến độ
**Kind:** design
**Thoả:** user 22/09 "mấy nhãn trong sidebar này trông chán thế nhỉ" · Sidebar Icon Tiles + Scroll Spy + Water-Ripple của docs-site-macos
**Depends:** Task 2 (contract)
**Files:** fdk/tools/html_shell.py, harness/tests/test_html_shell.py
**Interfaces:**
- Consumes: khối `ovs-shell` của Task 2
- Produces: mỗi `nav a` thiếu `.ic` được gắn icon SVG line (tra từ khoá tên mục → bộ icon nhỏ; không khớp thì monogram) trong tile màu theo accent section; tiền tố "01 ·" tách thành chip số mono mờ; mục active = viên nền đậm + chấm màu (KHÔNG sọc cạnh); scroll spy IntersectionObserver; ripple; vạch tiến độ đọc ở đáy nav
```python
ICONS = {"vấn đề|problem": "<path …/>", "kiến trúc|architecture|layout": "…", "nghiệm thu|test|verify": "…", ...}
def nav_icon(label: str) -> str: ...   # SVG 14px stroke trắng
```
**Verify:** `python3 -m pytest -q harness/tests/test_html_shell.py && bash harness/tests/html-visual-gate-test.sh`

### Task 4: sơ đồ kéo-thả và mind map tự sinh cho trang docs-shell
**Kind:** build
**Thoả:** RULE-04 (mind map mặc định) · RULE-07 (node-draggable cho mọi .diagram-box) của docs-site-macos
**Depends:** Task 2 (contract), Task 3 (effect_order)
**Files:** fdk/tools/html_shell.py, harness/tests/test_html_shell.py
**Interfaces:**
- Consumes: khối `ovs-shell` của Task 2
- Produces: trong `html_shell.apply()` — mind map collapsible sinh từ cây h2/h3 của chính trang (chèn sau hero, chỉ khi trang chưa có); JS node-draggable của skill gắn cho `.diagram-box` chưa có `data-draggable`. 
```python
def mind_map(html: str) -> str: ...     # <details class="ovs-mindmap"> từ h2/h3
def draggable_js() -> str: ...          # lấy nguyên từ docs-site-macos Node-Draggable
```
**Verify:** `python3 -m pytest -q harness/tests/test_html_shell.py`

### Task 5: luật gác cho phần máy không tự chèn được
**Kind:** build
**Thoả:** user 22/09 "làm với tất cả" — quy định văn xuôi không được bỏ qua lặng lẽ nữa
**Depends:** Task 1 (data), Task 3 (effect_order), Task 4 (effect_order)
**Files:** harness/validators/html_docs_shell.py, harness/tests/test_html_docs_shell.py
**Interfaces:**
- Consumes: bộ đo Task 1
- Produces: R20 báo WARN khi trang docs-shell (không qua lớp nền) thiếu thành phần MUST, kèm lệnh sửa `html_font.py --apply`; fire-drill BAD (trang tay thiếu) → WARN, GOOD (sau apply) → sạch
```python
def shell_gaps(html: str) -> list[str]: ...   # dùng lại CHECKS của docs-shell-survey
```
**Verify:** `python3 -m pytest -q harness/tests/test_html_docs_shell.py`

### Task 6: bản sao engine, skill và tài liệu
**Kind:** integration
**Thoả:** parity engine orca-graph (PLAN 210926) · skill không còn dạy chép tay thứ lớp nền đã tự chèn
**Depends:** Task 3 (contract), Task 4 (contract)
**Files:** ~/.orca-graph/repo/engine/html_base.py, skills/docs-site-macos/SKILL.md, llmwiki/skills/utils/docs-site-macos.md
**Interfaces:**
- Consumes: `html_base.py` sau Task 3–4
- Produces: engine khớp parity; SKILL ghi rõ phần nào lớp nền tự gắn khi chạy `html_font.py --apply`
```bash
python3 fdk/tools/html-font-lint.py --parity
```
**Verify:** `python3 fdk/tools/html-font-lint.py --parity`

### Task 7: áp cho mọi trang, khảo sát về 0, hai cổng xanh, ảnh trước/sau
**Kind:** test
**Thoả:** user 22/09 "làm với tất cả 1 lượt luôn"
**Depends:** Task 5 (acceptance), Task 6 (acceptance)
**Files:** llmwiki/html/220926-docs-shell-before-after.html
**Interfaces:**
- Consumes: mọi task trên
- Produces: mọi trang docs-shell qua `html_font.py --apply`, `docs-shell-survey --all` rc 0, trang ảnh trước/sau (sidebar downstream-layout sáng/tối + 2 trang khác)
```bash
python3 fdk/tools/html_font.py --apply llmwiki/html/*.html llmwiki/graph/*.html
python3 fdk/tools/docs-shell-survey.py --all
```
**Verify:** `python3 fdk/tools/docs-shell-survey.py --all && python3 fdk/tools/frontend-antipattern.py --all >/dev/null; [ $? -ne 1 ] && test -s llmwiki/html/220926-docs-shell-before-after.html`

### Task 8: review độc lập + medic --ci
**Kind:** review
**Thoả:** luật repo: đọc gate trước khi đẩy
**Depends:** Task 7 (acceptance)
**Files:** llmwiki/wiki/sources/draft/220926-docs-shell-kit-review.md
**Interfaces:**
- Consumes: toàn bộ diff
- Produces: báo cáo finding theo mức chặn / nên sửa / ghi nhận
```bash
python3 fdk/tools/medic.py --ci
```
**Verify:** `test -s llmwiki/wiki/sources/draft/220926-docs-shell-kit-review.md && python3 fdk/tools/medic.py --ci`

## Origin

- Hai tin nhắn user ngày 22/09/2026 (ảnh sidebar `120926-downstream-layout.html`; "làm với tất cả 1 lượt").
- Khảo sát `scratchpad/shell-survey.py` cùng ngày; luật nguồn `skills/docs-site-macos/SKILL.md:54-66`, Icon Tiles `:1035`, Node-Draggable `:563`.
- PLAN liền trước: `210926-reading-font-slop-code-PLAN` (lớp nền làm mới khối cũ, parity engine).
