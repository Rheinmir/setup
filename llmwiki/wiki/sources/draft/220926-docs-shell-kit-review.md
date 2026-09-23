---
type: draft
title: Review độc lập — docs-shell kit (PLAN 220926) + bản vá Windows GH#167/168/169
status: recorded
tags: [review, docs-shell, html_shell, r20, windows, installer]
timestamp: 2026-09-22
---

# Review độc lập — docs-shell kit + Windows (22/09/2026)

Người review không viết code này. Chỉ đọc và chạy, không sửa file nào.

## Đã chạy

| Lệnh | Kết quả |
|---|---|
| `pytest -q test_html_shell.py test_html_docs_shell.py test_html_base.py` | 21 passed |
| `html_docs_shell.py --self-test` | 11/11 ok |
| `docs-shell-survey.py --all` | 4/5. `llmwiki/html/overstack.html` thiếu skip-link, main-id, favicon, draggable (file trong working tree chưa được áp lại) |
| `bash harness/tests/windows-portability-test.sh` | 5 PASS · 0 FAIL |
| `html-font-lint.py --parity` | engine khớp nguồn framework |
| mirror validator / mirror skill | giống hệt nhau |
| Probe tay (Python, không ghi file repo) | 12 kịch bản, kết quả ở dưới |

## Finding

### Chặn

1. **File mới chưa được track, mà R20 đã hứa với máy khách.** `git status`: `fdk/tools/html_shell.py`, `html_shell_vendor.py`, `harness/tests/test_html_shell.py`, `test_html_docs_shell.py`, `windows-portability-test.sh` đều ở trạng thái `??`. Trong khi đó `html_docs_shell.py` (R20, đã track và đã sửa) và `html_base.py` (đã sửa) sẽ đi theo commit. Nếu commit thiếu mấy file này thì `_shell()` (`fdk/tools/html_base.py:101`) lặng lẽ trả nguyên trang. R20 vẫn chặn và bảo "chạy --apply là xong", nhưng `--apply` không làm gì. Kết quả là mọi máy khách kẹt vòng chặn → apply → vẫn chặn. Còn CI thì đỏ ngay ở step windows-portability, vì file script không tồn tại. **Sửa:** `git add` cả 5 file trong cùng commit với R20. Có thể thêm: R20 chỉ hứa `--apply` khi `html_shell.py` có mặt cạnh `html_font.py`.

2. **`apply` không idempotent trên trang đã có scroll spy hoặc ripple riêng. Đã tái hiện trên chính `overstack.html`.** Chỗ gây lỗi là `fdk/tools/html_shell.py:182-183`: `"spy": "IntersectionObserver" not in html or 'id="ovs-shell-js"' in html`, và `ripple` cũng viết y như vậy. Lần áp đầu thấy trang có IO riêng nên bỏ qua spy. Lần sau thì khối `ovs-shell-js` đã có mặt, nên cờ bật và chèn thêm `JS_SPY` + `JS_RIPPLE`. Đo được: `sh.apply(overstack)` rồi áp lại → khối JS từ 5851 lên 7050 ký tự, số `new IntersectionObserver` từ 1 lên 2. Kết quả là hai spy cùng tranh class `.active` và mỗi click ra hai ripple. Chính R20 cũng bảo agent chạy `html_font.py --apply` lên file đã áp, nên đây là đường chạy thường xuyên chứ không hiếm. Test idempotent (`test_html_shell.py:70`) chỉ thử trang không có IO riêng nên không bắt được. **Sửa:** ghi quyết định vào khối của mình, ví dụ `<script id="ovs-shell-js" data-parts="spy,ripple">`, hoặc bỏ khối `ovs-shell-js` ra khỏi html trước khi tính cờ `need` (làm giống cách `drag` đã bỏ `DRAG_JS`). Thêm một test "trang có IO riêng, áp 2 lần thì bằng nhau".

3. **R20 hứa sai về main-id: trang hợp lệ bị chặn mãi.** Validator `harness/validators/html_docs_shell.py` (`shell_problem`) coi `main-id` là thứ lớp nền tự chèn, nhưng `html_shell.py:197-204` cố ý KHÔNG chèn trong hai ca:
   - trang đã có `<main id="content">` (điều kiện `"id=" not in mm.group(1)`),
   - CSS có `body > …` (`_child_of_body_css`), ca mà code tự gọi là "sẽ gãy nếu bọc".
   Probe: áp xong, R20 vẫn trả rc 2 với lời "Lớp nền tự chèn main-id — chạy --apply", tức là vòng lặp vô tận. Ở ca `<main id="content">`, skip-link `href="#main"` còn trỏ vào hư không. **Sửa:** validator chấp nhận `<main>` với bất kỳ id nào, còn html_shell cho skip-link trỏ tới id thật của `<main>`. Ca `body >` thì chuyển `main-id` sang nhóm `MANUAL` và ghi lời nhắn đúng sự thật, hoặc cho phép `<meta name="overstack-shell" content="…">` để miễn.

4. **`install.ps1` không parse được trên Windows PowerShell 5.1, đúng đường chạy trong `.EXAMPLE`.** Cách chạy được hướng dẫn là `iwr … -OutFile install.ps1; .\install.ps1`. Windows PowerShell 5.1 (mặc định trên Win10/11) đọc file .ps1 không BOM theo cp1252. Ký tự `—` là UTF-8 `E2 80 94`, trong đó byte 0x94 thành `”`, và PowerShell coi `”` là dấu đóng chuỗi. Đo bằng `pwsh` Parser trên nội dung decode cp1252: bản mới có 2 lỗi (L110 thiếu `}`, L126 `try` thiếu `finally`), bản HEAD cũng có 2 lỗi (L112 chuỗi không đóng). Lỗi có từ trước, nhưng diff thêm một chỗ nữa: dòng `Write-Host "…CANH BAO: … WSL — phan global…"` (`install.ps1:115`). Như vậy bản vá GH#169 không chạy được tới dòng nào trên 5.1. `install-ps1-test.sh` chạy bằng pwsh 7 (mặc định UTF-8) nên không thấy. **Sửa:** thay mọi `—`/`→` trong file bằng ASCII (file vốn đã cố viết không dấu), hoặc lưu UTF-8 có BOM. Thêm vào test một bước parse file đã decode cp1252.

### Nên sửa

5. **Cảnh báo WSL gần như không bao giờ hiện.** Chỗ lỗi ở `harness/poc-vendor-neutral/bootstrap.sh`, trong điều kiện `ls /mnt/c/Users/*/.local/bin/claude.exe /mnt/c/Users/*/AppData/Roaming/npm/claude.cmd >/dev/null 2>&1`. `ls` trả rc khác 0 khi có BẤT KỲ đối số nào không tồn tại (đo: `ls /etc/hosts /nonexistent` → rc 1). Vậy cảnh báo chỉ hiện khi máy có CẢ bản native lẫn bản npm, trong khi máy thường chỉ có một. Test (5) của `windows-portability-test.sh` chỉ `grep` + `bash -n` nên PASS dù nhánh này chết. **Sửa:** `for f in …; do [ -e "$f" ] && { found=1; break; }; done` hoặc `compgen -G`. Quoting của printf thì đúng: `\\` in ra `\`.

6. **Logo dạng `<a class="logo" href="#top">` bị biến thành mục nav.** `_nav_links` (`html_shell.py:108-123`) chỉ bỏ qua `href="#"`. Probe cho ra `<a class="logo ovs-na" href="#top" title="Brandsub"><span class="ic">…B…</span><span class="ovs-lbl">Brandsub</span></a>`: `<small>` bị nuốt, chữ dính nhau "Brandsub", và logo nhận style mục (13px, flex, icon tile). Logo cũng bị đếm vào ngưỡng ≥4 neo của `is_docs_shell`. **Sửa:** bỏ qua `<a>` có class `logo`, cả trong `_nav_links` lẫn khi đếm neo (ở 3 bản `is_docs_shell`).

7. **Bọc `<main style="display:contents">` gãy trong hai ca bố cục thường gặp** (`html_shell.py:201-204`):
   - (a) `<header><nav>…</nav></header>`: `<main>` mở TRONG header. Probe xác nhận `</header>` nằm giữa `<main>` và `</main>`, nên parser đóng main ở `</header>` và nội dung rơi ra ngoài main. Skip-link khi đó trỏ vào một main rỗng.
   - (b) CSS dùng combinator anh em như `nav ~ section`, `nav + main`: `_child_of_body_css` chỉ soi `body >`, nên vẫn bọc (probe xác nhận), và section không còn là anh em của nav nữa.

   **Sửa:** chỉ bọc khi `</nav>` là con trực tiếp của `<body>`, và bỏ qua khi CSS có `nav\s*[~+]`. Nếu không chắc thì đừng bọc: gắn `id="main"` vào section đầu tiên sau nav là đủ cho skip-link.

8. **R20 không có đường miễn cho trang docs-shell cố ý tối giản.** `nav_problem` có `<meta name="overstack-nav" content="none">`, còn `shell_problem` thì không có. Một trang có `.logo` + 4 neo mà cố ý không muốn mind map hay ripple bị chặn cứng. Lối thoát duy nhất là chạy `--apply`, tức là chấp nhận bị chèn mind map. **Sửa:** thêm meta miễn theo từng mục, ví dụ `<meta name="overstack-shell" content="no-mind-map">`, và bắt kèm lý do như luật nav.

9. **Luật favicon lệch giữa hai bên, nên chặn trang hợp lệ.** Validator đòi `rel="icon"` đứng TRƯỚC `href="data:`. html_shell (`:181`) thì thấy có `rel="icon"` là thôi không chèn. Probe cho hai ca bị chặn mãi với lời hứa "Lớp nền tự chèn favicon":
   - `<link href="data:…" rel="icon">` (thứ tự thuộc tính hợp lệ),
   - `<link rel="icon" href="/favicon.svg">`.

   **Sửa:** validator khớp theo từng thuộc tính, không phụ thuộc thứ tự. Favicon dạng file thì nên chấp nhận, hoặc cho html_shell cùng một điều kiện với validator.

10. **`html_base._shell` không bắt ngoại lệ** (`fdk/tools/html_base.py:101-107`). Chỉ cần một lỗi regex hay lỗi thiếu thuộc tính trong html_shell trên một trang lạ (ví dụ `re.search(...).group(0)` ở `:179` khi nav không khớp) là MỌI generator và `html_font --apply` đều crash, không chỉ riêng trang docs-shell. **Sửa:** `try: return m.apply(html) except Exception as e: print warning; return html`.

### Ghi nhận

11. **Rủi ro srcdoc đã được kiểm, không thành vấn đề.** `overstack.html` có 2 srcdoc (576 KB và 216 KB) chứa `</head>` và `</body>` thô. `_body_end` lấy `</body>` CUỐI nên đúng, `<nav` đầu tiên là nav thật. Attribute trong srcdoc buộc phải escape `"` thành `&quot;`, nên regex `href="#` và `class="logo"` không khớp bên trong. Còn hở hai ca hiếm: chuỗi `'<nav …class="logo"…'` trong `<script>`, và trang bỏ `</body>` nhưng có chuỗi `'</body>'` trong JS (khi đó khối script bị chèn vào giữa chuỗi JS).
12. **Mind map chèn sai chỗ khi section lồng nhau.** `html_shell.py:215` dùng `<section…>.*?</section>` non-greedy, nên nếu hero có section con thì mind map lọt vào GIỮA hero (probe xác nhận).
13. **Có thể sinh id trùng.** Trang có `<div id="main">` mà không có `<main>` sẽ bị bọc thêm `<main id="main">`, thành 2 `id="main"` (probe).
14. **Các check chỉ dò chuỗi, dễ đỗ nhờ chữ.** Chữ `ripple`/`IntersectionObserver`/`skip-link` xuất hiện trong nội dung (hoặc IO dùng cho reveal) là đủ qua. Sau lần áp đầu, CSS `.ovs-ripple` luôn có mặt nên check `ripple` luôn qua, kể cả khi JS ripple bị bỏ.
15. **JS_RIPPLE để lại style inline vĩnh viễn.** Nó gắn `overflow:hidden` (và `position:relative` nếu đang static) vào MỌI `button`/`nav a` được bấm, và không gỡ lại. Nút nào có badge/tooltip/dropdown định vị tuyệt đối sẽ bị cắt sau click đầu tiên. Nên bọc ripple trong một `span` con có `overflow:hidden` thay vì đổi style của phần tử.
16. **Cách đọc rc trong CI chỉ bắt rc 1.** `harness.yml`: `[ "$rc" = 1 ]` nên mọi rc khác 0/1/2 (vd 127 khi thiếu file) đều qua xanh. Nên đổi thành `[ "$rc" = 0 ] || [ "$rc" = 2 ] || exit 1`.
17. **`install-harness.sh` có sẵn một mẫu dễ mất dữ liệu (có từ trước, diff không tạo ra).** Dòng `{ [ -f ] && [ -s ]; } && cp … || echo '{}' > "$SETTINGS"`: nếu `cp` backup thất bại thì settings của user bị ghi đè thành `{}`. Nên đổi sang `if … then cp … || exit 1; else echo '{}' > …; fi`.
18. **Phần Windows kiểm lại đều đúng.**
    - `export PYTHONUTF8=1 PYTHONIOENCODING=utf-8` đứng trước mọi lệnh python: bootstrap dòng 23 (không có python), install.sh dòng 19 (python đầu tiên ở dòng 131), install-harness dòng 24 (python đầu tiên ở dòng 135).
    - `python3 - "$SETTINGS"` + `sys.argv[1]` đúng: argv là `['-', path]`, heredoc có quote nên `$HOME` trong HOOKS_DIR vẫn là chuỗi literal như trước.
    - Logic chọn Git Bash trong ps1 đúng: loại `System32\*`, `-notlike` không phân biệt hoa thường, Split-Path hai lần từ `Git\cmd\git.exe` ra `Git\bin\bash.exe`, thêm NoteProperty `Source` cho FileInfo.
    - Engine: `reconfigure` đặt sau `import sys` ở cả 3 file.

    Còn một rủi ro: lệnh gợi ý `curl.exe … | & "…bash.exe"` và chính `$scriptText | & $bash.Source` khi chạy trong PowerShell 5.1 đi qua `$OutputEncoding`, mặc định là ASCII, nên chữ có dấu trong bootstrap thành `?`. Hiện chỉ làm hỏng phần hiển thị, nhưng sẽ gãy nếu sau này script có đường dẫn hay chuỗi so sánh chứa dấu.
19. **Test không có ca PASS giả.** Các assert đều đo thật: vendor khớp nguyên văn skill, drift validator↔survey, fire-drill chặn → apply → qua. Nhưng độ phủ còn hở đúng ở finding 2, 3, 5, 9.
20. **`overstack.html` trong working tree chưa đủ khung** (survey ✗). Lần Write/Edit kế tiếp vào file này sẽ bị R20 chặn. Nên chạy lại generator (đi qua html_base, áp một lần thì sạch) trước khi push, và đừng chạy `--apply` chồng thêm cho tới khi finding 2 được sửa.

## Origin

Review độc lập theo yêu cầu phiên 22/09/2026 trước khi đẩy PLAN `llmwiki/wiki/sources/draft/220926-docs-shell-kit-PLAN.md` cùng các bản vá GH#167/168/169. Bằng chứng lấy từ các lệnh trong bảng "Đã chạy" và các probe Python chạy trên bản sao trong bộ nhớ hoặc thư mục tạm, không ghi vào file nào của repo. Riêng phần parse PowerShell cp1252 chạy bằng `pwsh` với `System.Management.Automation.Language.Parser`.
