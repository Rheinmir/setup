---
type: draft
title: "PLAN — trang showcase thiết kế mặc định (design-showcase.html): mọi khối có index + code, xuống máy khách, là chuẩn để harness và agent audit theo"
status: proposed
tags: [plan, design, hallmark, showcase, orca-graph, downstream]
timestamp: 2026-09-22
---

# PLAN 220926 — design-showcase: một trang mẫu chuẩn cho mọi thiết kế mặc định

Quan hệ với file đã có: `skills/hallmark/references/design-default.md` là LỜI (token + luật). Trang showcase là CODE CHẠY ĐƯỢC của đúng các luật đó, mỗi khối một mẫu. Hai file phải khớp nhau; test ở Task 7 gác điều đó.

## Global constraints
- Trang KHÔNG viết tay: sinh bằng `fdk/tools/build-design-showcase.py` từ lớp nền có sẵn (`html_base.py`, `html_font.py`, `html_shell.py`) để luật đổi thì trang đổi theo. Đích: `skills/hallmark/references/design-showcase.html` (đường skill xuống máy khách qua `npx skills add`, cả thư mục) + builder ở `fdk/tools/` (xuống `~/.claude/harness/fdk/tools/`).
- Installer chỉ copy `fdk/tools/*.py` phẳng, KHÔNG copy thư mục con → mọi module khối là file phẳng `fdk/tools/showcase_<nhóm>.py`.
- Mỗi khối có: `id` (neo `#b-<id>`, ổn định, dùng làm index), tiêu đề, `data-rules="<luật,…>"` (luật nó minh hoạ), bản chạy thật + khối code (HTML/CSS/JS đúng như bản chạy, escape) + nút sao chép. CLI: `--list` in index, `--get <id>` in code một khối (agent đọc bằng lệnh, không cần mở trình duyệt).
- Trang phải qua SẠCH chính các cổng của framework: `html-visual-gate.mjs` 0 FAIL (WARN phải có lý do ghi trong khối), `frontend-antipattern.py` 0 finding. Toggle sáng/tối + localStorage + chống nháy. Font Be Vietnam Pro nhúng. Không CDN ngoài (xem được offline ở máy khách).
- Chart/graph theo quy ước skill `diagram`: SVG inline tất định, chữ trong sơ đồ cùng font trang, không thư viện ngoài.
- Đường dẫn downstream không ghi cứng `llmwiki/`/`harness/` — dùng `overstack_paths.*`/`hooklib.*` nếu builder cần.
- Không AI-attribution trong commit.

### Task 1: Kiểm kê luật thiết kế thành danh sách máy đọc được
**Kind:** research
**Thoả:** user 22/09 "nó có sẵn toàn bộ các phần thiết kế có trong luật của dự án"
**Depends:** —
**Files:**
- Tạo: `fdk/tools/showcase_rules.py`
**Interfaces:**
- Produces: `RULES: dict[id → {"gate": "visual|static|doc", "level": "FAIL|WARN|MUST", "text": str}]` gom từ `html-visual-gate.mjs` (header), `frontend-antipattern.py`, mục MUST của `skills/docs-site-macos/SKILL.md`, RULE-14 + "Defaults khi user không nói" của `design-default.md`
**Bước:** (1) parse header luật của html-visual-gate.mjs; (2) liệt kê rule id của frontend-antipattern.py; (3) thêm luật chỉ-có-trong-tài-liệu (kanban-uniform, eye-rest…); (4) `python3 fdk/tools/showcase_rules.py` in bảng id · cổng · mức
**Code:**
```python
# fdk/tools/showcase_rules.py — mức FAIL/WARN suy từ CHÍNH code cổng, không chép tay
def visual_rules(src: str) -> dict:
    head = src.split("\nimport ", 1)[0]
    ids = re.findall(r"^//   ([a-z][a-z-]+[a-z])\s{2,}(?:FAIL|WARN)?\s*(.+)$", head, re.M)
    warn = set(re.findall(r"warns\.push\(`([a-z-]+):", src))
    return {i: {"gate": "visual", "level": "WARN" if i in warn else "FAIL", "text": t.strip()} for i, t in ids}
```
**Verify:** `python3 fdk/tools/showcase_rules.py | grep -c . | awk '$1>=20{exit 0}{exit 1}'`

### Task 2: Builder + khung trang + index
**Kind:** build
**Thoả:** user 22/09 "file này sẽ có index từng block code và làm tham chiếu xem được"
**Depends:** Task 1 (data)
**Files:**
- Tạo: `fdk/tools/build-design-showcase.py`
**Interfaces:**
- Consumes: `showcase_rules.RULES`
- Produces: `Block = dict(id, title, group, rules: list[str], html, css, js, note)`; builder gom `BLOCKS` từ mọi `showcase_*.py` có biến `BLOCKS`; CLI `--list`, `--get <id>`, `--out <path>` (mặc định `skills/hallmark/references/design-showcase.html`)
**Bước:** (1) khung docs-shell chuẩn (sidebar = index nhóm → khối, tên trang ≥ 1,2 × mục nav); (2) render mỗi khối: bản chạy + `<details>` code + nút sao chép; (3) CSS/JS của khối gom một lần, có tiền tố `.sc-<id>` để không đè nhau; (4) chạy `html_font.apply` + `html_base.apply`
**Code:**
```python
# fdk/tools/build-design-showcase.py — gom BLOCKS từ mọi showcase_*.py phẳng; CLI --list/--get/--out
def groups() -> list:
    files = sorted(HERE.glob("showcase_*.py"), key=lambda p: (GROUP_ORDER.index(p.stem) if p.stem in GROUP_ORDER else 99, p.stem))
    return [(m.GROUP, f.stem.replace("showcase_", ""), m.BLOCKS) for f in files if hasattr(m := _load(f), "BLOCKS")]

def snippet(b: dict) -> str:            # code dán thẳng được: HTML + <style> + <script>
    parts = [b["html"].strip()]
    if b.get("css"): parts.append("<style>\n" + b["css"].strip() + "\n</style>")
    if b.get("js"):  parts.append("<script>\n(() => {\n  const root = document.querySelector('.sc-" + b["id"] + "');\n" + b["js"].strip() + "\n})();\n</script>")
    return "\n".join(parts)
```
**Verify:** `python3 fdk/tools/build-design-showcase.py --out scratchpad/sc.html && grep -c 'data-block=' scratchpad/sc.html`

### Task 3: Khối bố cục — cột 1/2/3/4 responsive, sidebar chuẩn, topbar, thang chữ, thang khoảng cách
**Kind:** design
**Thoả:** user 22/09 "các dạng 1 2 3 4 column responsive xử lý ra sao, sidebar như thế nào là chuẩn"
**Depends:** Task 2 (contract)
**Files:**
- Tạo: `fdk/tools/showcase_layout.py`
**Interfaces:**
- Consumes: kiểu `Block` của Task 2
- Produces: `BLOCKS` gồm `grid-1`…`grid-4` (điểm gãy 1360/1024/768/375 và cách cột rơi xuống), `sidebar`, `topbar`, `type-scale`, `spacing-scale`, `measure`
**Bước:** mỗi khối ghi rõ ở `note` luật nó minh hoạ (`heading-scale`, `title-scale`, `hierarchy-flat`, `horizontal-scroll`, `measure-too-wide`, `spacing-off-scale`…)
**Code:**
```python
# fdk/tools/showcase_layout.py — lưới co theo KHUNG (container query), không theo cửa sổ
def _grid(n: int, fall: str, labels: list) -> dict:
    rules = {4: "@container (max-width:760px){.sc-grid-4 .row{grid-template-columns:repeat(2,minmax(0,1fr))}}"
                "@container (max-width:420px){.sc-grid-4 .row{grid-template-columns:minmax(0,1fr)}}", ...}[n]
    return dict(id=f"grid-{n}", title=f"Lưới {n} cột", rules=["responsive-columns", "horizontal-scroll", "tight"],
                css=f".sc-grid-{n}{{container-type:inline-size}}"
                    f".sc-grid-{n} .row{{display:grid;grid-template-columns:repeat({n},minmax(0,1fr));gap:16px}}" + rules)
```
**Verify:** `python3 fdk/tools/build-design-showcase.py --list | grep -c -E 'grid-[1-4]|sidebar' | awk '$1>=5{exit 0}{exit 1}'`

### Task 4: Khối thành phần — thẻ, list mặc định, kanban, nút/CTA, tab, disclosure, dialog, bảng, form, toggle
**Kind:** design
**Thoả:** user 22/09 "như khối kanban … list mặc định"
**Depends:** Task 2 (contract)
**Files:**
- Tạo: `fdk/tools/showcase_components.py`
**Interfaces:**
- Consumes: kiểu `Block` của Task 2
- Produces: `BLOCKS` gồm `card`, `list`, `kanban` (thẻ cố định size, bấm mở dialog), `button`, `tabs`, `disclosure`, `dialog`, `table`, `form`, `theme-toggle`, `status-dot`
**Bước:** trạng thái đủ 8 (default · hover · focus-visible · active · disabled · loading · error · success) cho nút và input; không sọc màu một cạnh
**Code:**
```python
# fdk/tools/showcase_components.py — kanban: thẻ CỐ ĐỊNH size + kéo thả + bàn phím
css=(".sc-kanban .card{display:flex;flex-direction:column;height:112px;box-sizing:border-box;overflow:hidden;cursor:grab;touch-action:none}"
     ".sc-kanban .title{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}"
     ".sc-kanban .who{margin-top:auto;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}")
js=("let g=null;root.addEventListener('pointerdown',e=>{const c=e.target.closest('.card');if(!c||e.button)return;"
    "g={c,x:e.clientX,y:e.clientY,on:false};c.setPointerCapture(e.pointerId)});"
    "root.addEventListener('pointerup',e=>{if(!g)return;const c=g.c;if(g.on){const l=laneAt(e.clientX,e.clientY);"
    "if(l){const nx=[...l.querySelectorAll('.card')].find(k=>k!==c&&k.getBoundingClientRect().top+k.offsetHeight/2>e.clientY);"
    "l.insertBefore(c,nx||null);count()}}else open(c);g=null});")
```
**Verify:** `python3 fdk/tools/build-design-showcase.py --get kanban | grep -q 'kanban'`

### Task 5: Khối motion mặc định + hướng dẫn sử dụng + trạng thái rỗng/tải/lỗi
**Kind:** design
**Thoả:** user 22/09 "hướng dẫn sử dụng, motion mặc định"
**Depends:** Task 2 (contract)
**Files:**
- Tạo: `fdk/tools/showcase_motion.py`
**Interfaces:**
- Consumes: kiểu `Block` của Task 2
- Produces: `BLOCKS` gồm `motion-reveal` (ease-out ≤ 240ms), `motion-theme` (circle-reveal), `reduced-motion`, `guide-steps` (hướng dẫn sử dụng từng bước), `empty-state`, `loading`, `error-state`, `progress-read`
**Code:**
```python
# fdk/tools/showcase_motion.py — mở chi tiết bằng grid-template-rows 0fr→1fr, ease-out 220ms
css=(".sc-motion-reveal .p{display:grid;grid-template-rows:0fr;opacity:0;transition:grid-template-rows .22s ease-out,opacity .22s ease-out}"
     ".sc-motion-reveal .p>div{overflow:hidden}.sc-motion-reveal.open .p{grid-template-rows:1fr;opacity:1}"
     "@media (prefers-reduced-motion:reduce){.sc-motion-reveal .p{transition:opacity .15s linear}}")
```
**Verify:** `python3 fdk/tools/build-design-showcase.py --get guide-steps | grep -q 'guide'`

### Task 6: Khối graph + chart theo quy ước `diagram`
**Kind:** design
**Thoả:** user 22/09 "graph, chart vv"
**Depends:** Task 2 (contract)
**Files:**
- Tạo: `fdk/tools/showcase_dataviz.py`
**Interfaces:**
- Consumes: kiểu `Block` của Task 2
- Produces: `BLOCKS` gồm `chart-bar`, `chart-line`, `stat-tile`, `graph-flow` (hộp + mũi tên), `mind-map`; SVG inline, màu từ token, chữ cùng font, đọc được ở cả hai chế độ
**Code:**
```python
# fdk/tools/showcase_dataviz.py — toạ độ TÍNH từ dữ liệu, không vẽ tay
def _bar() -> str:
    data = [(_GATE_VI[g], n) for g, n in _by_gate.items()]
    W, lw, bh, gap = 560, 150, 28, 16
    mx = max(n for _, n in data)
    rows = [f'<rect class="bar" x="{lw}" y="{4 + i*(bh+gap)}" width="{(W-lw-48)*n/mx:.0f}" height="{bh}" rx="6"/>'
            for i, (lb, n) in enumerate(data)]
    return f'<svg viewBox="0 0 {W} {len(data)*(bh+gap)+8}" role="img" aria-labelledby="sc-bar-t">…</svg>'
```
**Verify:** `python3 fdk/tools/build-design-showcase.py --get chart-bar | grep -q '<svg'`

### Task 7: Cổng tự gác — trang qua mọi luật và phủ mọi luật
**Kind:** test
**Thoả:** user 22/09 "mốt code harness và agent cứ thế mà audit theo"
**Depends:** Task 3 (acceptance), Task 4 (acceptance), Task 5 (acceptance), Task 6 (acceptance)
**Files:**
- Tạo: `harness/tests/test_design_showcase.py`
- Sửa: `harness/tests/html-visual-gate-test.sh`
**Interfaces:**
- Consumes: builder + `showcase_rules.RULES`
- Produces: test (a) mọi luật trong RULES có ≥ 1 khối khai trong `data-rules` (luật mới thêm mà chưa có mẫu → đỏ); (b) id khối duy nhất, `--get` mọi id rc 0; (c) trang committed khớp bản build lại (không trôi); (d) html-visual-gate trên trang: 0 FAIL; frontend-antipattern: 0 finding
**Code:**
```python
# harness/tests/test_design_showcase.py — luật mới mà chưa có khối mẫu thì ĐỎ
def test_every_rule_has_a_showcase_block():
    covered = {r for b in BLOCKS for r in b["rules"]}
    missing = sorted(set(sr.RULES) - covered)
    assert not missing, f"luật chưa có khối mẫu (thêm vào showcase_*.py): {missing}"

def test_committed_page_matches_a_fresh_build():
    assert PAGE.read_text(encoding="utf-8") == ds.build(), \
        "design-showcase.html trôi khỏi bản build — chạy: python3 fdk/tools/build-design-showcase.py"
```
**Verify:** `python3 -m pytest -q harness/tests/test_design_showcase.py && node fdk/tools/html-visual-gate.mjs skills/hallmark/references/design-showcase.html`

### Task 8: Nối vào luật + luồng audit + downstream
**Kind:** docs
**Thoả:** user 22/09 "tất nhiên để làm được vậy thì nó phải downstream" · "cho mọi thiết kế mặc định xem vào"
**Depends:** Task 7 (acceptance)
**Files:**
- Sửa: `skills/hallmark/SKILL.md` (RULE-14 trỏ tới showcase: thiếu mẫu thì lấy khối theo id)
- Sửa: `skills/hallmark/references/design-default.md`
- Sửa: `skills/qc-uiux/SKILL.md` (audit so với khối chuẩn: `build-design-showcase.py --get <id>`)
- Sửa: `skills/docs-site-macos/SKILL.md`
- Sửa: `fdk/CAPABILITIES.md`
- Sửa: mirror `llmwiki/skills/utils/hallmark.md`, `llmwiki/skills/dev-loop/qc-uiux.md`, `llmwiki/skills/utils/docs-site-macos.md`
**Interfaces:**
- Consumes: đường dẫn trang + CLI `--get` của Task 2
- Produces: skill chỉ tới showcase; builder chạy được ở layout máy khách
**Bước:** (1) sửa 4 skill + mirror; (2) chạy `bash harness/tests/dot-layout-runtime-test.sh` xác nhận builder chạy được ở layout máy khách (gọi từ `~/.claude/harness/fdk/tools`, ghi ra thư mục tạm)
**Code:**
```python
# skills/hallmark/SKILL.md — RULE-14 trỏ khối mẫu; áp cho mọi trục brief bỏ ngỏ
RULE-14 (MUST): Project chưa có `design.md` → đọc references/design-default.md ở Step 0 …
  **Code mẫu cho từng phần**: references/design-showcase.html — lấy code bằng
  `python3 fdk/tools/build-design-showcase.py --get <id>` (máy khách: ~/.claude/harness/fdk/tools/…).
```
**Verify:** `grep -q design-showcase skills/hallmark/SKILL.md && grep -q design-showcase skills/qc-uiux/SKILL.md && bash harness/tests/dot-layout-runtime-test.sh .`

### Task 9: Duyệt bằng mắt (người)
**Kind:** review
**Thoả:** user 22/09 "như 1 file showcase chuẩn mặc định luôn" — chuẩn thì người phải chốt bằng mắt
**Depends:** Task 7 (acceptance)
**Files:**
- Tạo: `scratchpad/showcase-shots/page-light-1360.png` (và 5 ảnh cùng thư mục)
**Interfaces:**
- Consumes: trang đã qua Task 7
- Produces: 6 ảnh (sáng/tối × 375 · 768 · 1360) + lời chốt của user
**Bước:** chụp; user xem và chốt. Node HITL: KHÔNG dispatch headless.
**Code:**
```bash
# chụp 6 ảnh (sáng/tối × 375·768·1360) rồi user chốt
node scratchpad/shots.cjs        # ghi scratchpad/showcase-shots/page-<mode>-<width>.png
ls scratchpad/showcase-shots/page-*.png | wc -l    # phải ra 6
```
**Verify:** `ls scratchpad/showcase-shots/*.png | grep -c . | awk '$1>=6{exit 0}{exit 1}'`

## Origin
- Yêu cầu user ngày 22/09/2026 qua `/orca-graph` (phiên 745ad856), nguyên văn: "làm 1 file html code mẫu và file này sẽ có index từng block code và làm tham chiếu xem được cho mọi thiết kế mặc định xem vào, tất nhiên để làm được vậy thì nó phải downstream, nó có sẵn toàn bộ các phần thiết kế có trong luật của dự án, như khối kanban, hướng dẫn sử dụng, motion mặc định, list mặc định, các dạng 1 2 3 4 column responsive xử lý ra sao, sidebar như thế nào là chuẩn, graph, chart vv, như 1 file showcase chuẩn mặc định luôn, mốt code harness và agent cứ thế mà audit theo".
- Tiếp nối: `skills/hallmark/references/design-default.md` + RULE-14 (cùng phiên), luật `kanban-uniform` trong `fdk/tools/html-visual-gate.mjs`.
