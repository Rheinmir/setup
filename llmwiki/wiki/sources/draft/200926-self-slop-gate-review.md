---
type: source
title: "Review độc lập trước khi ship 200926-self-slop-gate — hai cổng có PASS giả không, lớp nền có phá trang nào không"
status: draft
tags: [review, slop, html, frontend-antipattern, html-visual-gate, html-base, ship]
timestamp: 2026-09-21
id: 200926-self-slop-gate-review
---

# Review độc lập — 200926-self-slop-gate

Task 13 yêu cầu soi lại hai thứ trước khi đẩy: **hai cổng có ca PASS giả không**, và **lớp nền có phá trang nào không**. Dưới đây là những gì kiểm chứng được bằng lệnh, kèm những gì còn nợ. Nguyên tắc khi viết trang này: chỉ ghi số đo được, không ghi "đã sửa hết" khi chưa.

## 1. Cổng có PASS giả không — có, và đã vá gốc

**Phát hiện nặng nhất của đợt review: `--all` của cổng tĩnh vẫn là DANH SÁCH TÊN GHI CỨNG.** Sau Task 1 nó đã mở từ 1 trang lên 11 trang, nhưng 11 tên đó là hằng số trong `framework_pages()`. Mọi trang sinh SAU đó — `wiki-graph.html`, `overstack-architecture.html`, và chính `200926-slop-before-after.html` của Task 12 — đều nằm ngoài tầm cổng. Cổng xanh vì nó không nhìn, y hệt lỗi gốc mà PLAN này được lập ra để sửa, chỉ lùi lại một bước.

Đã đổi `framework_pages()` sang **quét thư mục**: mọi `*.html` nằm trực tiếp trong `llmwiki/html` và `llmwiki/graph`, trừ artifact archify (nhận biết bằng nội dung, cùng cách miễn của R16/R20/R22). Trang mới từ nay tự vào phạm vi, không ai phải nhớ thêm tên.

Hệ quả ngay khi mở phạm vi: **26 file → 38 file, 0 FAIL → 23 FAIL**. Đã dọn hết về 0 (xem mục 3).

Hai chỗ PASS giả khác, nhỏ hơn, cũng đã vá:

- **Nút đang tắt bị tính là lỗi.** Cổng chạy-thật đòi 4,5:1 cả với `button:disabled` (làm mờ `opacity:.45` đúng quy ước "bấm không được"). WCAG 1.4.3 miễn trừ điều khiển đang tắt → đây là ĐỎ GIẢ. Cổng nay bỏ qua `:disabled` / `[aria-disabled="true"]` / `fieldset[disabled]`.
- **Làm mờ có chủ ý bị tính là lỗi.** Ba nơi độc lập cùng dính: nút tắt ở bảng delta archify, bóng `moved-from` của bảng so sánh, và 5.295/5.548 node ngoài tiêu điểm của `wiki-graph.html`. Cách chữa KHÔNG phải là đoán theo `opacity` (đoán thì mọi chữ nhạt đều thoát, kể cả chữ nhạt do lỗi) mà là bắt trang **tự khai**: cổng bỏ qua phần tử có `data-ovs-deemphasized`, và `build-wiki-graph.py` gắn/gỡ thuộc tính đó ngay lúc bật/tắt lớp `dim`.

Chiều ngược lại — cổng có bắt thật không — được giữ bằng `harness/tests/html-visual-gate-test.sh`: mỗi luật một fixture XẤU, **12 PASS · 0 FAIL**. Luật mới R22 có fire-drill BAD/GOOD trong `harness-doctor.py`: `argv:bad→2 · argv:good→0 · stdin:bad→2 · stdin:good→0`.

## 2. Lớp nền có phá trang nào không — có một lớp trang, đã vá

`html_base.apply()` bỏ qua trang không có `</head>` tường minh. HTML5 cho phép bỏ thẻ `<head>`, và trang agent viết tay hay chỉ có `<!doctype>` + `<title>` + `<style>` — `120926-downstream-layout.html` là một ca thật: lớp nền không gắn được, `html-slop-fix.py` cũng bỏ qua luôn, trang giữ nguyên gradient-text + sọc viền mà không ai biết.

Đã sửa ba chỗ, cùng một gốc:

1. `html_base.apply()` nhận head NGẦM ĐỊNH — chèn `</head>` ngay trước phần tử nội dung đầu tiên.
2. Script boot theme chèn sau `<html>`/`<!doctype>` khi không có thẻ `<head>` mở (phải chạy TRƯỚC style, nếu không trang nháy sai chế độ).
3. `html-slop-fix.fix_markup()` vá `<style>` ở CẢ ngoài head (trang head ngầm, hoặc style đặt cuối body). An toàn với `<iframe srcdoc>` vì nội dung srcdoc là HTML đã escape nên regex không chạm tới.

Ngoài ca đó, lớp nền **không phá trang nào**: `test_html_base.py` + `test_html_slop_fix.py` 11 PASS, và 38/38 trang qua cổng tĩnh sau khi vá.

## 3. Số đo sau đợt sửa

| Cổng | Phạm vi | Trước PLAN | Sau |
|---|---|---:|---:|
| Tĩnh `frontend-antipattern --all` | 38 file (quét thư mục) | 52 FAIL · 32 WARN | **0 FAIL · 11 WARN** |
| Chạy-thật, trang framework SINH | 21 trang | 17/20 trang có lỗi | **21/21 đạt** |
| Chạy-thật, toàn phạm vi | 38 trang | — | 28/38 đạt |
| `medic --ci` | toàn hệ | 1 fail | **0 fail · 2 warn** |
| `harness-doctor` fire-drill | 22 luật | — | rc 0, R22 xanh |

## 4. Nợ mở — ghi rõ, không bịt

**Mười trang viết tay chưa qua cổng chạy-thật.** Toàn bộ là trang một lần của phiên cũ (`*-seq.html`, `design-pattern-v3.html`, `100926-harness-fixes.html`…). Lỗi tập trung ở một nhúm màu chữ phụ dùng chung: `footer` 2,57:1 · `span.arrow` 3,67:1 · `code` 2,60:1 · `b` 2,57:1 — hụt ngưỡng chứ không phải chìm hẳn. Cổng tĩnh đã sạch trên chúng; cổng chạy-thật thì chưa. **CI vì vậy chỉ gác trang framework SINH RA**, không gác trang lịch sử — gác chúng là khoá CI bằng nợ cũ. Muốn dọn nốt thì một đợt riêng, đổi cùng một nhúm token màu.

**`wiki-graph.html` quá chậm để đo.** 5.548 node, `page.goto` vượt 30s nên cổng chạy-thật timeout. Đây là vấn đề hiệu năng trang, không phải slop; để ngoài danh sách CI kèm ghi chú thay vì hạ ngưỡng timeout cho khuất mắt.

**`examples/checkout-platform-delta.html` của fork archify.** 15 chữ sáng / 6 chữ tối dưới 4,5:1, tất cả nằm trong bóng `data-delta-state="moved-from"` (`opacity:.42`) đánh dấu vị trí CŨ của node đã dời; nhãn thật vẫn rõ ở vị trí mới. Qua được cổng thì bóng phải lên `opacity ≥ 0,85`, tức mất ngôn ngữ thị giác của bảng so sánh — **quyết định thiết kế chờ user chốt**, không tự sửa. (Trang này có thể dùng `data-ovs-deemphasized` như `wiki-graph` đã làm; chưa làm vì cần user đồng ý rằng bóng mờ là "không cần đọc".)

**`docs/gallery.html` của fork** (trang giới thiệu, không phải trang sơ đồ): `toggle: NO-EFFECT`, `/ proof lab` 2,6:1, ba chỗ khối dính 1px. Là template site của upstream, ngoài phạm vi PLAN này.

**11 WARN còn lại của cổng tĩnh**: `svg thiếu role="img"` (9), `uppercase-misuse` (2), prose tiếng Việt lọt code block (2). Mức WARN, không chặn.

## 5. Smoke máy khách — ba lỗi chỉ lộ ở downstream

Cả hai cổng xanh ở repo framework KHÔNG chứng minh được gì cho máy khách: cây thư mục khác (dot layout) và tool chạy từ `~/.claude/harness`. Dựng fixture downstream thật rồi chạy hai cổng lên trang nó sinh ra, bắt được ba lỗi:

1. **Cổng chạy-thật chưa bao giờ xuống máy khách.** `install-harness.sh` chỉ `cp fdk/tools/*.py`; `html-visual-gate.mjs` là `.mjs` nên bị bỏ lại. Máy khách chỉ có cổng tĩnh, và không ai biết vì không có gì báo. Đã thêm `cp fdk/tools/*.mjs`.
2. **Cổng tĩnh giải neo bằng chứng SAI ở máy khách.** `scan_svg_evidence` dùng `ROOT = Path(__file__).parents[2]` — ở máy khách ra `~/.claude`, nên mọi `data-src` resolve trượt và cổng báo "sơ đồ đang nói dối về code" hàng loạt. Đã thêm `project_root(page)`: leo từ TRANG đang soi lên, mốc là `.llmwiki/` · `llmwiki/` · `.git/`.
3. **`overstack.html` mang neo của cây framework.** Trang được dựng ở repo framework rồi copy nguyên xuống, nên `data-src` trỏ `llmwiki/…` · `harness/…` · `.github/…`. Installer nay dịch neo sang layout đích và GỠ neo nào đích không có (giữ node, bỏ lời khai sai). Đo trên fixture: **3 FAIL → 0**.

Smoke này nay là test thường trực `harness/tests/downstream-slop-gate-test.sh`, đã nối vào CI. Cổng chạy-thật ở đó SKIP CÓ TÊN khi máy không có Playwright — không tính là PASS. Cổng gate cũng thử thêm `NODE_PATH` khi tìm Playwright, để máy nào cài global thì downstream chạy được thật.

## 5. Gốc lỗi phát hiện ngoài PLAN — engine orca-graph

Trong lúc dọn, trang `control-room-kanban.html` cứ mọc lại sọc viền sau khi đã sửa generator. Truy ra: `regen_room()` của engine tra `build-control-room.py` theo `__file__.parents[2]`, mà engine cài ở `~/.orca-graph` nên chỗ đó không có `fdk/tools/` → luôn rơi xuống bản cài global `~/.claude/harness` (cũ hơn repo). Daemon `watch` chạy nền, mỗi lượt vẽ đè cockpit bằng CSS cũ, im lặng.

Đã sửa ở repo engine, ba bản: `3.1.2` (thêm cwd), `3.1.3` (đi từ THƯ MỤC GRAPH lên — vì daemon có cwd bất kỳ, chỉ thêm cwd là chưa đủ), `3.1.4` (chip `<code>` xếp dọc cách nhau 3,4px → 13px). Mỗi bản kèm test hồi quy; `tests/test_orca_graph.py` 62 PASS. Provenance trong `fdk/skills.provenance.json` đã re-pin về `7b6eae7` / `3.1.4`.

Bài học đáng ghi: **một bản cài global cũ hơn repo là nguồn hồi quy câm** — nó không báo lỗi, chỉ lặng lẽ ghi đè. Thứ tự tra phải là dự án trước, global sau cùng.

## Origin

- Task 13 của `llmwiki/wiki/sources/draft/200926-self-slop-gate-PLAN.md` — "review độc lập + ship ba repo", user duyệt 20/09/2026 ("dựng qua graph và xử lý hết đi") và giục chạy hết ngày 21/09/2026.
- Số đo trước: `fdk/wiki/sources/200926-slop-baseline.md` (baseline ĐỎ của Task 3).
- Lệnh chạy để lấy từng con số trong trang này: `fdk/tools/frontend-antipattern.py --all`, `fdk/tools/html-visual-gate.mjs`, `fdk/tools/medic.py --ci`, `harness/scripts/harness-doctor.py`, `harness/tests/html-visual-gate-test.sh`, `harness/tests/downstream-slop-gate-test.sh`, `python3 -m pytest harness/tests/`.
- Commit engine đi kèm: `78dd38b`, `e964f00`, `7b6eae7` (Rheinmir/orca-graph). Commit fork archify: `f528f9d`, `0aecf24`.
