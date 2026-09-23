---
type: draft
title: "PLAN — hệ khoảng cách chống slop: một thang (Carbon + Tailwind), line-height và độ dài dòng theo WCAG/USWDS, proximity tiêu đề, phân tầng nhãn sidebar — lớp nền tự bẻ về thang, hai cổng gác phần còn lại"
status: approved
tags: [plan, orca-graph, spacing, typography, line-height, wcag, slop, html-base]
timestamp: 2026-09-22
---

# PLAN 220926 — hệ khoảng cách chống slop

User ngày 22/09/2026: "luật padding cách dòng vẫn slop và không có hệ thống gì cả, lên mạng research chuẩn đi và áp vào như 1 luật chóng slop", rồi chỉ vào `div.brand` và `div.grp` trong sidebar `control-room-kanban.html`: "cái này cần nổi bật hơn bằng màu tương phản hẳn hoặc cách nào đó".

Chuẩn và số đo trước: `fdk/wiki/sources/220926-spacing-standards.md` — 92 giá trị khoảng cách khác nhau trên 54 trang, 61% ngoài lưới 4px, line-height 14 giá trị (hay gặp 1,35).

Ngoài phạm vi (nói thẳng): UI sản phẩm dự án khách (việc của `hallmark` theo `design.md` riêng); giá trị `em` trong khoảng cách (không quy được ra px nếu không biết cỡ chữ phần tử — cổng chạy thật đo px đã tính thay cho cổng tĩnh); bố cục lưới/cột.

## Global constraints
- Thang duy nhất: 2 · 4 · 8 · 12 · 16 · 20 · 24 · 32 · 40 · 48 · 64 · 80 · 96 px. Ngoại lệ: 0, 1px, `%`, `vw/vh`, `auto`, `calc()`, `clamp()`, `var()`.
- Line-height chữ nội dung ≥ 1,5 · tiêu đề 1,1–1,3 · đoạn chữ ≤ 80 ký tự · khoảng trên tiêu đề ≥ 1,5 lần khoảng dưới · vùng bấm ≥ 24×24 px — nguồn ở trang chuẩn.
- Cổng trước, sửa sau: mỗi luật có số đỏ trên trạng thái hiện tại trước khi sửa trang.
- Một nguồn cho việc bẻ về thang: `fdk/tools/html-slop-fix.py` (lớp nền đã gọi nó cho mọi trang) — không sửa tay từng generator.
- Không phá bố cục: bẻ về bậc GẦN NHẤT; ảnh trước/sau cho user duyệt bằng mắt.
- Không AI-attribution trong commit (R15).

### Task 1: bộ đo khoảng cách và số đỏ theo từng luật
**Kind:** research
**Thoả:** user 22/09 "không có hệ thống gì cả"
**Depends:** —
**Files:** fdk/tools/spacing-survey.py
**Interfaces:**
- Consumes: —
- Produces: `spacing-survey.py [--all] [--json]` — theo trang: số giá trị khoảng cách khác nhau, số ngoài thang, line-height; rc 2 khi còn ngoài thang
```python
SCALE = (0, 1, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96)
def off_scale(css: str) -> list[float]: ...
```
**Verify:** `python3 fdk/tools/spacing-survey.py --all >/dev/null; [ $? -ne 1 ]`

### Task 2: token khoảng cách + nhịp chữ trong lớp nền
**Kind:** build
**Thoả:** chuẩn Carbon/Tailwind/USWDS trong 220926-spacing-standards
**Depends:** Task 1 (contract)
**Files:** fdk/tools/html_base.py, harness/tests/test_html_base.py
**Interfaces:**
- Consumes: thang của Task 1
- Produces: token `--sp-1…--sp-12` theo thang, `--lh-body:1.6`, `--lh-heading:1.2`, `--measure:70ch`; mặc định `p,li,dd{line-height:var(--lh-body)}` và `h1,h2,h3{line-height:var(--lh-heading)}` ở độ ưu tiên thấp (`:where`) để trang tự đặt vẫn thắng
```python
SCALE_PX = (2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96)
```
**Verify:** `python3 -m pytest -q harness/tests/test_html_base.py`

### Task 3: tự bẻ khoảng cách về thang trong html-slop-fix
**Kind:** build
**Thoả:** user 22/09 "áp vào như 1 luật chống slop" — trang mới và trang cũ đều về thang mà không ai phải nhớ
**Depends:** Task 1 (contract)
**Files:** fdk/tools/html-slop-fix.py, harness/tests/test_html_slop_fix_spacing.py
**Interfaces:**
- Consumes: thang của Task 1
- Produces: phép vá mới: padding/margin/gap/inset/top/…/row-gap/column-gap có `px`/`rem` ngoài thang → bậc gần nhất; line-height < 1,5 trên luật chọn chữ nội dung (`p`, `li`, `body`, `.desc`…) → `var(--lh-body)`; không đụng data-URI, JS, srcdoc
```python
def snap(px: float) -> float: ...   # bậc gần nhất của SCALE_PX, giữ 0/1
```
**Verify:** `python3 -m pytest -q harness/tests/test_html_slop_fix_spacing.py`

### Task 4: luật chống slop khoảng cách ở hai cổng
**Kind:** build
**Thoả:** user 22/09 "áp vào như 1 luật chóng slop"
**Depends:** Task 1 (contract), Task 3 (effect_order)
**Files:** fdk/tools/frontend-antipattern.py, fdk/tools/html-visual-gate.mjs, harness/tests/test_frontend_antipattern_slop.py, harness/tests/html-visual-gate-test.sh
**Interfaces:**
- Consumes: thang Task 1
- Produces: tĩnh `spacing-off-scale`; chạy thật `line-height-body` (đoạn ≥ 2 dòng, lh/fs < 1,5 → FAIL), `measure-too-wide` (> 80ch), `heading-proximity` (khoảng trên < 1,5 × khoảng dưới), `hierarchy-flat` (nhãn nhóm/tên trang trong nav khác mục cùng cấp < 2 trong 4: cỡ · đậm · màu · hoa-thường), `tap-target` (< 24px); mỗi luật fixture XẤU cắn, TỐT sạch
```js
// MEASURE: const lh = parseFloat(cs.lineHeight) / parseFloat(cs.fontSize)
```
**Verify:** `python3 -m pytest -q harness/tests/test_frontend_antipattern_slop.py && bash harness/tests/html-visual-gate-test.sh`

### Task 5: phân tầng nhãn sidebar (brand · nhóm · mục)
**Kind:** design
**Thoả:** user 22/09 trên `div.brand` + `div.grp` của control-room-kanban: "cần nổi bật hơn bằng màu tương phản hẳn"
**Depends:** Task 4 (acceptance)
**Files:** fdk/tools/build-control-room.py, fdk/tools/html_shell.py
**Interfaces:**
- Consumes: luật `hierarchy-flat` của Task 4
- Produces: brand = cỡ lớn hơn + đậm + màu nhấn; nhãn nhóm = chữ hoa nhỏ giãn chữ, màu chữ chính đậm, khoảng trên ≥ 1,5 lần khoảng dưới; mục = chữ thường màu phụ; cùng quy ước cho sidebar docs-shell
```css
nav .grp{margin:var(--sp-5) 0 var(--sp-2)}
```
**Verify:** `python3 -m pytest -q harness/tests/test_control_room.py`

### Task 6: khuôn skill theo thang + token
**Kind:** docs
**Thoả:** khuôn docs-site-macos không còn dạy số ngoài thang
**Depends:** Task 2 (contract), Task 3 (contract)
**Files:** skills/docs-site-macos/SKILL.md, llmwiki/skills/utils/docs-site-macos.md, fdk/tools/html_shell_vendor.py
**Interfaces:**
- Consumes: token Task 2
- Produces: mục "Hệ khoảng cách" trong SKILL (thang, line-height, measure, proximity, nguồn); CSS mẫu dùng token; `html_shell.py --sync` lại
```bash
python3 fdk/tools/html_shell.py --sync
```
**Verify:** `python3 -m pytest -q harness/tests/test_html_shell.py`

### Task 7: sinh lại mọi trang, cổng xanh, ảnh trước/sau
**Kind:** test
**Thoả:** user 22/09 — xong = nhìn thấy khác biệt
**Depends:** Task 5 (acceptance), Task 6 (acceptance)
**Files:** llmwiki/html/220926-spacing-before-after.html
**Interfaces:**
- Consumes: mọi task trên
- Produces: trang generator sinh lại + trang tay qua `--apply`; `spacing-survey --all` về 0 ngoài thang trên trang generator; trang ảnh trước/sau
```bash
python3 fdk/tools/spacing-survey.py --all
```
**Verify:** `python3 fdk/tools/frontend-antipattern.py --all >/dev/null; [ $? -ne 1 ] && test -s llmwiki/html/220926-spacing-before-after.html`

### Task 8: review độc lập + medic --ci
**Kind:** review
**Thoả:** luật repo: đọc gate trước khi đẩy
**Depends:** Task 7 (acceptance)
**Files:** llmwiki/wiki/sources/draft/220926-spacing-system-review.md
**Interfaces:**
- Consumes: toàn bộ diff
- Produces: finding theo mức chặn / nên sửa / ghi nhận
```bash
python3 fdk/tools/medic.py --ci
```
**Verify:** `test -s llmwiki/wiki/sources/draft/220926-spacing-system-review.md && python3 fdk/tools/medic.py --ci`

## Origin

- Hai tin nhắn user ngày 22/09/2026 (luật padding/cách dòng; ảnh chọn `div.brand`, `div.grp` trong `llmwiki/html/control-room-kanban.html`).
- Chuẩn: `fdk/wiki/sources/220926-spacing-standards.md` (WCAG 1.4.12/1.4.8/2.5.8, IBM Carbon, Tailwind, USWDS, Baymard, Butterick).
- PLAN liền trước: `220926-docs-shell-kit-PLAN` (lớp nền tự gắn), `210926-reading-font-slop-code-PLAN` (hai cổng slop).
