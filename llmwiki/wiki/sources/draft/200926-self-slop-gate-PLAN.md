---
type: draft
title: "PLAN — framework tự bắt slop của chính nó: cổng có sẵn phải chạy trên MỌI trang sinh ra, thêm luật sọc viền · thiếu toggle · chữ chìm · đè chữ · viết hoa lệch, rồi gom các generator về một lớp nền chung và sửa hết"
status: approved
tags: [plan, orca-graph, slop, html, design-base, frontend-antipattern, dark-mode, archify]
timestamp: 2026-09-20
---

# PLAN 200926 — framework tự bắt slop của chính nó

User báo ngày 20/09/2026, kèm ảnh: trang HTML do script của framework sinh ra "lắm slop" — căn lề và khoảng cách giữa các khối vỡ, chữ trùng màu nền ở dark/light, mất hiệu ứng kính, viết HOA chỗ có chỗ không, thẻ và nút có sọc viền màu. Câu chốt của user: **"framework chúng ta có các cơ chế bắt slop bắt buộc nhưng chưa tự bắt nó"**. Đo lại thì đúng từng chữ: `fdk/tools/frontend-antipattern.py` chạy lên tất cả 41 trang ra 52 FAIL và 32 WARN, nhưng `medic` chỉ cho nó soi đúng một trang (`overstack.html`) nên luôn xanh. Quét thêm bằng Playwright: 13 trang không có nút đổi sáng/tối (trái luật của repo), 198 thẻ có sọc màu bên trái trên 5 trang (mức tối thiểu, bộ đo còn sót), nhãn mờ chìm nền ở trang sơ đồ và ở `overstack.html`, icon đè chữ trong sơ đồ archify. User duyệt cùng ngày: "dựng qua graph và xử lý hết đi".

Gốc chung: mỗi generator tự viết một bộ CSS riêng, không chia sẻ bộ màu dark, khoảng cách, thẻ, toggle hay quy ước viết hoa; và cổng gác có sẵn không được áp lên sản phẩm của chính framework. Font là thứ đầu tiên đã gom về một nguồn (`fdk/tools/html_font.py`); PLAN này gom nốt phần còn lại theo đúng cách đó.

Ngoài phạm vi (nói thẳng): UI sản phẩm của dự án khách (việc của `hallmark`/`prd-grade-fe` theo `design.md` riêng); các trang `.html` cũ do agent dựng tay nằm trong `llmwiki/html/` — thư mục này gitignored trừ `overstack.html`, tức chúng là sản phẩm cục bộ không ship; PLAN sửa KHUÔN sinh ra chúng (template `docs-site-macos`) và chạy bộ vá máy-làm-được lên bản cục bộ, phần không vá tự động được thì liệt kê ra chứ không giả vờ sạch.

## Global constraints
- Cổng trước, sửa sau: mọi luật mới phải ĐỎ trên trạng thái hiện tại (có số đếm ghi lại) rồi mới được sửa trang cho xanh. Cổng xanh ngay từ đầu là cổng không bắt được gì.
- Tiêu chí xong KHÔNG phải "cổng xanh" mà là cổng xanh CỘNG trang ảnh trước/sau để user nhìn bằng mắt. Hai lần trong ngày tôi đã báo đạt dựa trên số đo hẹp.
- Một nguồn cho lớp nền: `fdk/tools/html_base.py` (mở rộng `html_font.py`), generator gọi đúng một hàm `apply()` trước khi ghi; không chép CSS nền vào từng generator. Repo engine mang BẢN SAO như đã làm với font, có kiểm parity.
- Quy ước viết hoa duy nhất: chỉ NHÃN NHỎ (eyebrow, tiêu đề nhóm trong menu, tiêu đề cột bảng) được `text-transform:uppercase` và bắt buộc kèm `letter-spacing`; tiêu đề, nút, mục menu, thẻ: viết thường hoa đầu câu. Không viết HOA bằng tay trong nội dung.
- Cấm sọc viền màu một cạnh trên thẻ/nút/callout (vẽ bằng `border-left`, `::before` hay `box-shadow` inset đều tính). Phân loại bằng chấm màu, nhãn, hoặc nền nhạt toàn thẻ.
- Mọi trang có nút đổi sáng/tối dùng được, nhớ lựa chọn (localStorage), chống nháy khi tải; ở cả hai chế độ mọi chữ đạt tương phản tối thiểu 4,5:1 (chữ lớn 3:1).
- Gate phải được ĐỌC trước khi đẩy; working tree có file lạ thì chạy gate trên checkout sạch của commit. Mỗi repo đi đúng luồng theo `repo_role` (framework · module).
- Không AI-attribution trong commit (R15).

### Task 1: cổng tĩnh — thêm luật và mở phạm vi ra MỌI trang framework sinh
**Kind:** build
**Thoả:** user 20/09 "có cơ chế bắt slop bắt buộc nhưng chưa tự bắt nó" · "thẻ nút có cái viền xanh" · "chỗ nào upper chỗ nào không" · luật repo "HTML phải có toggle dark/light"
**Depends:** —
**Files:**
- Sửa: `fdk/tools/frontend-antipattern.py`
- Tạo: `harness/tests/test_frontend_antipattern_slop.py`
**Interfaces:**
- Consumes: —
- Produces: luật mới `[FAIL] side-stripe` (border-left ≥3px màu trên thẻ, `::before`/`::after` rộng ≤6px cao 100% có nền màu, `box-shadow: inset Npx 0 0 <màu>`), `[FAIL] no-theme-toggle` (trang không có cơ chế `data-theme` + nút), `[WARN→FAIL sau Task 4] uppercase-misuse` (`text-transform:uppercase` trên h1–h4, button, mục menu, hoặc thiếu `letter-spacing`); cờ `--all` = quét mọi trang framework sinh (danh sách từ hàm `framework_pages()`), `--count` in số đếm theo luật để ghi baseline (dùng bởi Task 2, Task 4, Task 9)
```python
STRIPE_BORDER = re.compile(r"border-left\s*:\s*(\d+(?:\.\d+)?)px\s+solid\s+(?!transparent|var\(--border|rgba\(0,\s*0,\s*0)", re.I)
STRIPE_INSET  = re.compile(r"box-shadow\s*:[^;]*inset\s+-?\d+px\s+0(?:px)?\s+0(?:px)?\s+(?:0(?:px)?\s+)?(?!rgba\(0,\s*0,\s*0)", re.I)
def framework_pages(root) -> list: ...   # overstack.html + mọi trang generator ghi ra (kể cả gitignored khi có mặt) + graph/*.html
```
**Verify:** `python3 -m pytest -q harness/tests/test_frontend_antipattern_slop.py`

### Task 2: cổng chạy-thật bằng Playwright — chữ chìm, khối dính, icon đè chữ, toggle hoạt động
**Kind:** build
**Thoả:** user 20/09 "padding trên dưới giữa cái div không có khoảng trống · cấu trúc vỡ · màu chữ cùng màu nền · mất gương"; bài học cùng ngày: bộ đo nháp của tôi ra 0 ở hai cột mà user thấy lỗi bằng mắt
**Depends:** —
**Files:**
- Tạo: `fdk/tools/html-visual-gate.mjs`
- Tạo: `harness/tests/html-visual-gate-test.sh`
**Interfaces:**
- Consumes: Playwright toàn cục (`NODE_PATH=$(npm root -g)`); không có thì SKIP có đếm, trên CI là FAIL
- Produces: `html-visual-gate.mjs <trang…> [--json] [--shots <dir>]` rc 2 khi có lỗi. Mỗi trang × {light, dark}: (a) chữ có tương phản < 4,5:1 (chữ ≥24px: 3:1), bỏ qua chữ `aria-hidden`; (b) hai khối có nền/viền riêng xếp dọc cách nhau < 8px, hoặc khối con chạm mép khối cha (padding < 8px); (c) hộp chữ giao với hộp icon/svg cùng node > 2px; (d) bấm toggle thì độ sáng nền đổi chiều, tải lại vẫn giữ; (e) trang khai có kính thì phần tử kính phải có `backdrop-filter` khác none ở CẢ hai chế độ. Có fixture xấu cho TỪNG luật để chứng minh luật cắn (dùng bởi Task 9, Task 10)
```bash
NODE_PATH=$(npm root -g) node fdk/tools/html-visual-gate.mjs llmwiki/html/overstack.html --shots scratchpad/shots
```
**Verify:** `bash harness/tests/html-visual-gate-test.sh`

### Task 3: ghi baseline ĐỎ — số đếm theo luật trên trạng thái hiện tại
**Kind:** test
**Thoả:** Global constraint "cổng trước, sửa sau"
**Depends:** Task 1 (data), Task 2 (data)
**Files:**
- Tạo: `fdk/wiki/sources/200926-slop-baseline.md`
**Interfaces:**
- Consumes: `frontend-antipattern.py --all --count`, `html-visual-gate.mjs --json`
- Produces: bảng số đếm theo luật × trang TRƯỚC khi sửa + bộ ảnh "trước" ở `scratchpad/slop-before/` (dùng bởi Task 10)
```bash
python3 fdk/tools/frontend-antipattern.py --all --count > scratchpad/slop-before/static.txt
```
**Verify:** `test -s fdk/wiki/sources/200926-slop-baseline.md && grep -q "side-stripe" fdk/wiki/sources/200926-slop-baseline.md`

### Task 4: html_base.py — một lớp nền chung (màu sáng/tối, khoảng cách, thẻ kính, toggle, quy ước viết hoa)
**Kind:** design
**Thoả:** gốc chung "mỗi generator một bộ CSS"; luật repo toggle + localStorage + chống FOUC; user "mất gương"
**Depends:** Task 1 (contract)
**Files:**
- Tạo: `fdk/tools/html_base.py`
- Tạo: `harness/tests/test_html_base.py`
- Sửa: `fdk/tools/html_font.py`
**Interfaces:**
- Consumes: `html_font.head_css()`
- Produces: `apply(html, *, toggle=True) -> str` (gộp font + nền, idempotent, chỉ chèn vào `<head>` thật và cuối `<body>`); token `--ovs-bg/-surface/-ink/-ink2/-border/-accent` cho hai chế độ, thang `--sp-1…6` (4·8·12·16·24·32), lớp `.ovs-card` (kính, KHÔNG sọc), `.ovs-eyebrow` (chỗ DUY NHẤT được uppercase), nút toggle truy cập được bằng bàn phím, script chống nháy đặt `data-theme` trước khi vẽ (dùng bởi Task 5–8)
```python
def apply(html: str, *, toggle: bool = True) -> str:   # html_font.apply gọi sang đây → generator KHÔNG phải đổi lời gọi
    ...
```
**Verify:** `python3 -m pytest -q harness/tests/test_html_base.py harness/tests/test_html_font.py`

### Task 5: generator không có dark mode — docs-index · health-dashboard · cheatsheet
**Kind:** fix
**Thoả:** 13 trang không toggle, trong đó ba trang này do script sinh; user "dark light mode màu chữ cùng màu nền"
**Depends:** Task 4 (contract)
**Resources:** generator-css(exclusive)
**Files:**
- Sửa: `fdk/tools/build-docs-index.py`
- Sửa: `fdk/tools/build-health-dashboard.py`
- Sửa: `fdk/tools/build-cheatsheet.py`
**Interfaces:**
- Consumes: token + toggle của Task 4
- Produces: ba trang dùng token hai chế độ, bỏ sọc viền thẻ (phân loại bằng chấm/nhãn), tiêu đề hết gradient-text, viết hoa theo quy ước
```python
CSS = CSS.replace("border-left:4px solid var(--kind)", "")   # + chấm màu .dot trong tiêu đề thẻ
```
**Verify:** `python3 fdk/tools/build-docs-index.py >/dev/null && python3 fdk/tools/build-health-dashboard.py >/dev/null && python3 fdk/tools/frontend-antipattern.py llmwiki/html/index.html llmwiki/html/280626-health-dashboard.html`

### Task 6: control-room + problem-tree — 184 thẻ sọc
**Kind:** fix
**Thoả:** số đo 20/09: kanban 100 thẻ sọc, problem-tree 84
**Depends:** Task 4 (contract)
**Resources:** generator-css(exclusive)
**Files:**
- Sửa: `fdk/tools/build-control-room.py`
- Sửa: `fdk/tools/build-wiki-graph.py`
**Interfaces:**
- Consumes: `.ovs-card`, token trạng thái
- Produces: thẻ kanban và node problem-tree phân loại bằng chấm trạng thái + nhãn, không sọc; khoảng cách theo thang `--sp-*`
```css
.kcard{border:1px solid var(--ovs-border)} .kcard .st{width:8px;height:8px;border-radius:50%}
```
**Verify:** `python3 fdk/tools/build-control-room.py >/dev/null && python3 fdk/tools/frontend-antipattern.py llmwiki/html/control-room.html llmwiki/html/control-room-kanban.html llmwiki/html/control-room-detail.html`

### Task 7: overstack.html + các trang con nhúng (memory-map, skill-whiteboard, wiki-graph-static)
**Kind:** fix
**Thoả:** `overstack.html` sáng có nhãn mục tương phản 2,2:1; ba trang nhúng không có toggle; nợ ghi ở review trước: chữ trong iframe srcdoc chưa dùng font chung
**Depends:** Task 4 (contract)
**Resources:** generator-css(exclusive)
**Files:**
- Sửa: `fdk/tools/build-overstack-docs.py`
- Sửa: `fdk/tools/memory-map.py`
- Sửa: `fdk/tools/whiteboard-skill-map.py`
**Interfaces:**
- Consumes: `html_base.apply`
- Produces: nhãn mục đạt 4,5:1 ở cả hai chế độ; trang con nhận lớp nền + theme đồng bộ với trang mẹ (srcdoc được `apply` TRƯỚC khi escape vào thuộc tính)
```python
srcdoc = html.escape(html_base.apply(child_html, toggle=False), quote=True)   # theme theo trang mẹ qua postMessage
```
**Verify:** `python3 fdk/tools/build-overstack-docs.py >/dev/null && python3 fdk/tools/frontend-antipattern.py llmwiki/html/overstack.html`

### Task 8: engine orca-graph (repo module) — graph + atlas theo lớp nền
**Kind:** fix
**Thoả:** trang graph/atlas là HTML framework sinh nhiều nhất; phải cùng quy ước viết hoa, khoảng cách, không sọc
**Depends:** Task 4 (contract)
**Files:**
- Sửa: `fdk/skills.provenance.json`
**Interfaces:**
- Consumes: bản sao `html_base.py` (chép sang `engine/` như `html_font.py`)
- Produces: `Rheinmir/orca-graph` bản 3.1.0 — `graph-viz.py` gọi `html_base.apply`, sửa mọi finding của hai cổng trên trang graph/atlas; ship theo luồng `module` (commit → test + eval + install-test đọc rc → push → CI xanh → tag) rồi re-pin ở đây; parity kiểm cả `html_base.py`
```bash
cp fdk/tools/html_base.py ~/orca/orca-graph/engine/ && python3 fdk/tools/html-font-lint.py --parity
```
**Verify:** `python3 fdk/tools/html-font-lint.py --parity && python3 fdk/tools/frontend-antipattern.py llmwiki/graph/200926-self-slop-gate.graph.html`

### Task 9: archify (fork của ta) — icon đè chữ, nhãn vùng mờ, viết hoa lộn
**Kind:** fix
**Thoả:** ảnh `arch-dark.png`: icon đè tiêu đề node, nhãn `01 / PLAN.md · Ledger` mờ, `GUIDED VIEWS`/`Play story`/`Dark`/`Live` mỗi chỗ một kiểu; memory `diagram-route-and-own-fork`: lỗi renderer sửa ở fork
**Depends:** Task 2 (acceptance)
**Files:**
- Tạo: `fdk/wiki/sources/200926-archify-renderer-fixes.md`
**Interfaces:**
- Consumes: `html-visual-gate.mjs` luật (a)(c)
- Produces: bản sửa ở `Rheinmir/archify` (đệm chữ tránh icon, màu nhãn vùng đạt 4,5:1 ở dark, một quy ước viết hoa cho thanh công cụ); cài lại skill; sinh lại các trang sơ đồ cục bộ; trang nguồn ghi commit của fork. Không truy cập được fork → node `blocked`, ghi lý do, KHÔNG sửa bản cài tại chỗ rồi coi như xong
```bash
NODE_PATH=$(npm root -g) node fdk/tools/html-visual-gate.mjs llmwiki/html/170926-orca-graph-gates-architecture.html
```
**Verify:** `test -s fdk/wiki/sources/200926-archify-renderer-fixes.md`

### Task 10: khuôn của skill + vá bản cục bộ các trang agent dựng tay
**Kind:** fix
**Thoả:** trang do agent dựng từ `docs-site-macos` có gradient-text, sọc callout, thiếu toggle; sửa KHUÔN để trang sau này sạch từ đầu
**Depends:** Task 4 (contract)
**Files:**
- Sửa: `skills/docs-site-macos/SKILL.md`
- Sửa: `llmwiki/skills/utils/docs-site-macos.md`
- Sửa: `skills/orca-onboard/assets/docs-site-skeleton.html`
- Tạo: `fdk/tools/html-slop-fix.py`
**Interfaces:**
- Consumes: luật của Task 1, lớp nền của Task 4
- Produces: khuôn bỏ gradient-text, callout không sọc, bước bắt buộc "chạy hai cổng trước khi giao"; `html-slop-fix.py <trang…>` vá máy-làm-được (bỏ sọc viền, gradient-text → màu đặc, chèn lớp nền + toggle) và IN danh sách thứ không vá tự động được
```bash
python3 fdk/tools/html-slop-fix.py llmwiki/html/*.html      # idempotent; in "còn N finding cần người"
```
**Verify:** `python3 fdk/tools/frontend-antipattern.py skills/orca-onboard/assets/docs-site-skeleton.html && python3 fdk/tools/swh-lint.py --ci`

### Task 11: framework TỰ BẮT chính nó — medic, CI và hook lúc ghi
**Kind:** infra
**Thoả:** user 20/09 "cơ chế bắt slop bắt buộc chưa tự bắt nó" — đây là task trả lời thẳng câu đó
**Depends:** Task 5 (acceptance), Task 6 (acceptance), Task 7 (acceptance), Task 8 (acceptance), Task 10 (acceptance)
**Resources:** ci-workflow(exclusive)
**Files:**
- Sửa: `fdk/tools/medic.py`
- Sửa: `.github/workflows/harness.yml`
- Tạo: `harness/validators/html_slop.py`
- Sửa: `llmwiki/.claude/hooks/post_tool_use.py`
- Sửa: `harness/policy.yaml`
- Sửa: `harness/poc-vendor-neutral/policy.yaml`
- Sửa: `harness/scripts/harness-doctor.py`
**Interfaces:**
- Consumes: hai cổng của Task 1, Task 2
- Produces: probe `frontend` của medic chạy `--all` (không còn một trang); step CI sinh trang vào thư mục tạm rồi chạy cả hai cổng; luật mới R22 `html-slop` ở PostToolUse nhánh `.html`: agent GHI một trang có sọc viền / gradient-text / thiếu toggle thì bị chặn ngay lúc ghi (rc 2) kèm lệnh sửa; fire-drill BAD/GOOD trong harness-doctor
```python
for name in ("report_show_path.py", "html_docs_shell.py", "html_slop.py"):   # post_tool_use nhánh .html
```
**Verify:** `python3 fdk/tools/medic.py --ci && python3 harness/scripts/harness-doctor.py >/dev/null`

### Task 12: trang ảnh TRƯỚC/SAU để user nghiệm thu bằng mắt
**Kind:** docs
**Thoả:** Global constraint "tiêu chí xong là user nhìn ảnh thấy ổn"
**Depends:** Task 3 (data), Task 11 (acceptance), Task 9 (acceptance)
**Mode:** HITL
**Files:**
- Tạo: `fdk/tools/build-slop-gallery.py`
**Interfaces:**
- Consumes: ảnh "trước" của Task 3 + ảnh "sau" chụp lại cùng khung
- Produces: `llmwiki/html/200926-slop-before-after.html` — mỗi trang một hàng: trước/sau × sáng/tối, số finding trước → sau; trang này tự qua cả hai cổng. User xem và nói ổn / chỉ chỗ chưa ổn
```bash
python3 fdk/tools/build-slop-gallery.py --before scratchpad/slop-before --after scratchpad/slop-after
```
**Verify:** `test -s llmwiki/html/200926-slop-before-after.html && python3 fdk/tools/frontend-antipattern.py llmwiki/html/200926-slop-before-after.html`

### Task 13: review độc lập + ship ba repo
**Kind:** release
**Thoả:** Global constraint "đọc gate trước khi đẩy"; `/ship` theo `repo_role`
**Depends:** Task 12 (acceptance)
**Files:**
- Tạo: `llmwiki/wiki/sources/draft/200926-self-slop-gate-review.md`
- Sửa: `fdk/wiki/index.md`
- Sửa: `fdk/wiki/log.md`
**Interfaces:**
- Consumes: mọi thay đổi của Task 1–12
- Produces: reviewer context riêng soi hai cổng (có ca PASS giả không) và lớp nền (có phá trang nào không); ship `framework` (medic + ci-local trên checkout sạch, stamp bump), `module` orca-graph, fork archify; smoke máy khách: trang sinh ở downstream qua cả hai cổng
```bash
python3 harness/scripts/repo_role.py . --json && python3 fdk/tools/medic.py --ci; echo "medic rc=$?"
```
**Verify:** `test -s llmwiki/wiki/sources/draft/200926-self-slop-gate-review.md && test -z "$(git log origin/orca..HEAD --oneline)"`

## Origin

- Báo cáo user ngày 20/09/2026 (ba tin nhắn liên tiếp, kèm nhận xét trên ảnh `scratchpad/slop/*.png`) và duyệt cùng ngày: "dựng qua graph và xử lý hết đi".
- Số đo trước PLAN: `frontend-antipattern.py` trên 41 trang = 52 FAIL · 32 WARN (medic chỉ soi 1 trang); quét Playwright `scratchpad/slop/audit.json`; 198 thẻ sọc trên 5 trang (`scratchpad/slop/stripe.mjs`).
- PLAN liền trước cùng dòng việc HTML: `200926-repo-role-ship-flows-PLAN` (font Lexend Deca, nguồn `fdk/tools/html_font.py`).
