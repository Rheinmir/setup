---
type: draft
title: "Review độc lập PLAN 220926-spacing-system — không có lỗi chặn; ba lỗi nên sửa (hierarchy-flat báo giả nhãn xám đậm, fix_markup sửa cả chuỗi trong JS và ví dụ code, _BODY_SEL bắt theo chuỗi con)"
status: recorded
tags: [review, spacing, slop, html-base, html-slop-fix, visual-gate]
timestamp: 2026-09-22
---

# Review độc lập — PLAN 220926 hệ khoảng cách

Người review không viết code này. Chỉ đọc và chạy thử, không sửa file nào. Bản sao để thử nằm ở `/tmp/spacing-review/`.

## Đã chạy (kết quả thật)

- `pytest -q test_html_slop_fix_spacing.py test_frontend_antipattern_slop.py test_html_base.py` → 23 passed.
- `spacing-survey.py --all` → 56 trang · 6.200 giá trị · 0 ngoài thang · rc 0.
- `bash harness/tests/html-visual-gate-test.sh` → 38 PASS · 0 FAIL · 0 SKIP · rc 0.
- Idempotent: gọi `html_base.apply` 3 lần trên `overstack.html` (bản HEAD và bản working tree) → lần 2 và lần 3 ra đúng kết quả lần 1. Gọi `fix_page` 2 lần cũng vậy. Trên bản HEAD, lần đầu bẻ 90 giá trị về thang, và nội dung `<script>` không đổi.
- Sidebar cũ `scratchpad/hier/old.html` bị hierarchy-flat bắt cả `div.brand` và `div.grp` (lý do: CHÌM hơn mục). `new.html`, nơi brand tô màu nhấn `--accent-ink`, qua sạch, tức không bắt nhầm brand màu nhấn.
- Quét `fix_markup` trên toàn bộ trang HTML của repo (llmwiki/html, llmwiki/graph, skills, harness/templates): không trang nào bị đổi nội dung `<script>` hay `srcdoc`. Có một thay đổi trong `<pre>/<code>`, nhưng đó là `style=""` của chính thẻ `<code>` (7px → 8px), tức sửa đúng.
- Trong 47 trang ở HEAD có 105 luật line-height < 1,5, và không luật nào khớp `_BODY_SEL`. Phép nâng line-height hiện chưa đổi gì trên trang có sẵn.
- Engine (`git -C ~/.orca-graph/repo diff`): trong `graph-viz.py` và `graph-atlas.py`, mọi dòng đổi đều nằm trong chuỗi CSS, cộng thêm khối `reconfigure(utf-8)`. Không dòng nào chạm chuỗi không phải CSS. `.chip{min-height:24px}` có tác dụng thật vì `.chips` là flex. Hàm `base_css` của engine giống hệt bản trong setup.
- Installer `install-harness.sh:158` chép `fdk/tools/*.py` và `:161` chép `*.mjs`, nên `spacing-survey.py` cũng tới máy khách.
- Khối css trong `skills/docs-site-macos/SKILL.md`, bản mirror và `docs-site-skeleton.html` đều 0 giá trị ngoài thang. Mục "Hệ khoảng cách" giống nhau giữa bản canonical và bản mirror.

## Finding

1. **Nên sửa** · `fdk/tools/html-visual-gate.mjs:165` (`const dim`) · hierarchy-flat báo FAIL giả với kiểu nhãn nhóm phổ biến nhất: xám, đậm, chữ hoa, nhỏ hơn mục. Kịch bản thử `/tmp/spacing-review/muted.html`: `.grp{11px;700;uppercase;#5f6673}` đặt cạnh `a{13px;400;#111}` khác nhau đủ 4/4 thuộc tính và tương phản 5,8:1 (đạt AA), vậy mà vẫn FAIL "CHÌM hơn mục". Lý do: điều kiện `crOf(lb) < crOf(ln) - 0.3` đúng với MỌI nhãn nhạt hơn mục, trong khi chỉ màu bão hoà mới được tha. Trang chuẩn `220926-spacing-standards.md` chỉ ghi luật "≥ 2/4 thuộc tính", không có điều kiện ĐỘ NỔI, nên cổng khắt khe hơn chuẩn nó dẫn. Một trang khách làm đúng kiểu sidebar macOS/GitHub sẽ bị chặn. Cách sửa: bổ sung luật ĐỘ NỔI kèm lý do (phản hồi của user) vào trang chuẩn, hoặc chỉ tính `dim` khi nhãn còn thua ở một trục khác. Ví dụ: tính khi `weak`, hoặc khi `crOf(lb) < 4.5`. Nhãn đạt AA mà đậm hơn mục thì nên tha. Thêm fixture `hierarchy-flat-muted-ok`.

2. **Nên sửa** · `fdk/tools/html-slop-fix.py:185-192` · `fix_markup` sửa nhầm những thứ không phải CSS của trang. Rủi ro này giờ lớn hơn, vì `html_base.apply` gọi `fix_markup` trên MỌI lần làm mới (`html_base.py:122-125`). Tái hiện bằng chuỗi mẫu:
   - `sty(rest)` chạy TRƯỚC bước tách `<script>`, nên `` const t=`<style>.z{padding:6px}</style>` `` trong JS bị đổi thành `8px`.
   - Regex `style\s*=\s*"` không có ranh giới từ và chạy cả trên văn xuôi: ví dụ code đã escape `<pre><code>&lt;div style="padding:10px"&gt;` bị đổi thành `12px` (tài liệu hướng dẫn sai lệch so với bản gốc). Chữ trong đoạn `style="margin:6px"` và `data-style="…"` cũng bị đổi.
   - `srcdoc='<style>…</style><b style="…">'` dùng nháy đơn cũng bị sửa, trái với docstring dòng 4 ("không đụng JS, không đụng srcdoc").

   Trên trang thật của repo chưa trúng chỗ nào (xem quét ở trên). Cách sửa: tách `<script>`, `<pre>`, `<code>`, `<textarea>` ra TRƯỚC khi chạy `sty` và `inline`; đổi regex inline thành `(?<![\w-])style\s*=\s*"` và chỉ khớp bên trong thẻ mở (`<[a-z][^>]*\sstyle="`).

3. **Nên sửa** · `fdk/tools/html-slop-fix.py:32` (`_BODY_SEL`) · Nhánh class khớp theo CHUỖI CON (`\.[\w-]*(?:desc|lead|body|prose|text|note|summary)[\w-]*`). Thử `fix_spacing(sel+"{line-height:1.1}")`: `.text-muted`, `.lead-in`, `.context-menu` (vì chứa "text"), `.summary`, `.hint-text`, `.footnote` và `.sidebar li` đều bị nâng lên `var(--lh-body,1.6)`. Đó là nhãn một dòng hoặc menu, nên chúng cao thêm khoảng 45% và lệch hàng với chip/nút bên cạnh. `_NOT_BODY` không chặn được vì không chứa "muted", "menu" hay "sidebar". Cách sửa: khớp theo từ (`\.(?:[\w-]+-)?(?:desc|lead|body|prose|summary)(?:-[\w-]+)?\b`, bỏ "text" và "note"), hoặc chỉ nâng khi selector chứa phần tử `p/li/dd/blockquote`. Thêm các ca trên vào `test_html_slop_fix_spacing.py`.

4. **Ghi nhận** · `fdk/tools/spacing-survey.py:37` với `frontend-antipattern.py` (`_spacing_off`) · Hai bộ đo KHÔNG khớp nhau với `var()`. Với `.x{gap:var(--sp,10px)}`, survey báo `[10.0]`, còn cổng tĩnh và phép vá bỏ qua cả hai. Vì phép vá không sửa được giá trị này, survey sẽ báo đỏ mãi. Global constraint của PLAN ghi `var()` là ngoại lệ. `test_spacing_off_scale_matches_spacing_survey_on_samples` PASS vì không có mẫu `var(`. Quy ước < 2px thì khớp ở cả ba nơi. Cách sửa: thêm `var\(` vào dòng 37 và thêm mẫu `var(` vào test so khớp.

5. **Ghi nhận** · `html-slop-fix.py:31` (`_SPACE` có `re.I`), còn `_SP_PROP` và survey `PROP` không có `re.I` · `.a{PADDING:10px}` được vá thành 12px nhưng cổng không báo, còn `10PX` thì không ai bắt. Chỉ bỏ sót, không làm hỏng trang. Nếu muốn nhất quán thì dùng cùng cờ ở cả ba nơi.

6. **Ghi nhận** · `html-slop-fix.py` (`snap`) và `test_html_slop_fix_spacing.py:12` · Giá trị âm được làm tròn ra XA số 0 khi hoà (`-6px → -8px`), và `!important` được giữ đúng (`p{margin:-6px 0 !important}` → `-8px 0 !important`). Margin âm thường dùng để kéo đè 1 viền hay 1 icon cho khít, nên đổi 2px sẽ làm lệch hình học. Nên để giá trị âm do người quyết: bỏ qua trong phép vá, cổng vẫn báo.

7. **Ghi nhận** · `fdk/tools/html-visual-gate.mjs:17`, `:141`, `:245`, `:249` · Chú thích và thông điệp còn sót từ bản đầu. Dòng 17 bị vỡ chữ ("> 85 ( 0.5em"). Dòng 141 nhắc `--measure:70ch`, trong khi token thật là `34em`. Dòng 245 và thông điệp WARN vẫn ghi "ước lượng 0.5em/ký tự", dù code đã đếm ký tự thật (`chars / (lines - 0.5)`). Phần đếm ký tự đã đúng; chỉ cần sửa lời.

8. **Ghi nhận** · `fdk/tools/spacing-survey.py:19` (`ROOT = parents[2]`) · Trên máy khách, file được chép vào `~/.claude/harness/fdk/tools/`, nên `--all` dò `~/.claude/harness/llmwiki/html` và ra 0 trang (in docstring, rc 1). Đưa đường dẫn trang cụ thể thì vẫn chạy. Docstring dòng 8 nói có đo "inset/top/right/bottom/left" nhưng regex `PROP` không có các thuộc tính đó (test lại coi `inset:10px` là hợp lệ). Cách sửa: `--all` lấy gốc từ `Path.cwd()` hoặc `git rev-parse --show-toplevel`, và bỏ câu trong docstring.

9. **Ghi nhận** · `llmwiki/html/overstack.html` qua cổng thật · measure-too-wide báo 15 đoạn, khoảng 128 ký tự mỗi dòng, và heading-proximity báo 3 tiêu đề (cả hai chỉ là WARN). Token `--measure:34em` có trong lớp nền nhưng `build-overstack-docs.py` chưa dùng. Trang chủ của chính framework vẫn vượt ngưỡng WCAG 1.4.8 (80 ký tự) mà PLAN đặt ra.

10. **Ghi nhận (ngoài phạm vi PLAN)** · `html-slop-fix.py:148` · Log "2× nền hex gần-trắng → --ovs-surface2" hiện lại ở mỗi lần chạy, dù chuỗi ra không đổi, vì regex khớp lại `var(--ovs-surface2,#…)` rồi viết lại y hệt. Người đọc log sẽ tưởng lần chạy thứ hai vẫn còn slop để vá. Nên chỉ đếm khi chuỗi thật sự thay đổi.

Không có finding mức chặn. Các kịch bản (a)–(f) mà PLAN yêu cầu soi: idempotent đạt, engine chỉ đổi CSS, installer chép đủ file, các cổng không PASS giả trên fixture (38/38). Ba lỗi nên sửa trên đều là báo giả hoặc sửa nhầm, tái hiện được bằng chuỗi mẫu, nhưng chưa trúng trang nào trong repo.

## Origin

Review độc lập ngày 22/09/2026, theo yêu cầu soát PLAN `llmwiki/wiki/sources/draft/220926-spacing-system-PLAN.md` trước khi push. Chuẩn đối chiếu: `fdk/wiki/sources/220926-spacing-standards.md`. Bằng chứng lấy từ lệnh chạy thật trên repo `/Users/giatran/orca/setup/setup`, engine `~/.orca-graph/repo`, và bản sao trong `/tmp/spacing-review/`.
