"""showcase_layout — khối BỐ CỤC của design-showcase (PLAN 220926-design-showcase t3): lưới 1–4 cột, sidebar, topbar,
thang chữ, thang khoảng cách, độ dài dòng. Quy ước khối: xem docstring build-design-showcase.py.

proof: harness/tests/test_design_showcase.py
"""

GROUP = "Bố cục"
_ON = ' class="on"'


def _grid(n: int, fall: str, labels: list) -> dict:
    cells = "".join(f'<div class="cell"><b>{t}</b><span>{d}</span></div>' for t, d in labels)
    # container query: lưới co theo KHUNG chứa nó (sidebar mở/đóng, nhúng trong thẻ) chứ không theo cửa sổ
    rules = {4: "@container (max-width:760px){.sc-grid-4 .row{grid-template-columns:repeat(2,minmax(0,1fr))}}"
                "@container (max-width:420px){.sc-grid-4 .row{grid-template-columns:minmax(0,1fr)}}",
             3: "@container (max-width:680px){.sc-grid-3 .row{grid-template-columns:minmax(0,1fr)}}",
             2: "@container (max-width:520px){.sc-grid-2 .row{grid-template-columns:minmax(0,1fr)}}",
             1: ""}[n]
    return dict(
        id=f"grid-{n}", title=f"Lưới {n} cột", rules=["responsive-columns", "horizontal-scroll", "tight"],
        note=(f"{n} cột bằng nhau (minmax(0,1fr) để chữ dài không đẩy tràn), gap 16px; {fall}." if n > 1
              else f"Một cột, {fall}."),
        html=f'<div class="sc-grid-{n}"><div class="row">{cells}</div></div>',
        css=(f".sc-grid-{n}{{container-type:inline-size}}"
             f".sc-grid-{n} .row{{display:grid;grid-template-columns:repeat({n},minmax(0,1fr));gap:16px}}"
             f".sc-grid-{n} .cell{{display:flex;flex-direction:column;gap:4px;padding:16px;border:1px solid var(--ovs-border);border-radius:12px;background:var(--ovs-surface2)}}"
             f".sc-grid-{n} .cell span{{font-size:14px;color:var(--ovs-ink2)}}" + rules))


_LB = [("Tổng quan", "Một câu tóm tắt."), ("Cài đặt", "Lệnh đầu tiên."), ("Luật", "Điều bắt buộc."), ("Kiểm tra", "Cách đo.")]

# mục lục mẫu cho khối toc-map: (nhãn, cấp heading, top % trên rail 320px — mỗi ô 1.75rem ≈ 8,75%)
_TOC = [("Tên trang", 1, 3), ("2. Cài đặt", 2, 12), ("2.1. Yêu cầu", 3, 21), ("2.2. Lệnh đầu tiên", 3, 30), ("3. Luật thiết kế", 2, 43), ("3.1. Khoảng cách", 3, 52),
        ("3.1.1. Thang 4px", 4, 61), ("3.2. Màu", 3, 70), ("4. Kiểm tra", 2, 81), ("5. Câu hỏi thường gặp", 2, 90)]

BLOCKS = [
    _grid(1, "dùng cho nội dung đọc dài, giới hạn bề rộng bằng --measure", [("Một cột", "Bài viết, hướng dẫn, form dài.")]),
    _grid(2, "khung hẹp hơn 520px thì rơi về 1 cột", _LB[:2]),
    _grid(3, "khung hẹp hơn 680px thì rơi thẳng về 1 cột (3 → 2 để lại ô mồ côi)", _LB[:3]),
    _grid(4, "khung hẹp hơn 760px còn 2 cột, hẹp hơn 420px còn 1 cột", _LB),
    dict(
        id="toc-map", title="TOC map — mục lục chấm mép phải", rules=["tap-target", "motion-ease-out", "transition-all"],
        note=("Điều hướng mặc định của trang tài liệu (user chốt 30/09/2026, mẫu namuwiki-ui-kit): mỗi mục một chấm trên rail mép phải, đặt theo vị trí "
              "heading trong trang; rê chuột vào dải mép phải để bung nhãn, phân cấp bằng font và cỡ chữ. Lớp nền tự dựng rail từ nav của trang."),
        html=('<div class="sc-toc-map">' + "".join(
            f'<div class="pane"><span class="st">{st}</span><div class="demo"><div class="nw-tocmap"{attr}>'
            + "".join(f'<a class="nw-tip{" is-hover" if hov == i else ""}" href="#b-toc-map" data-tooltip="{t}" aria-label="{t}" data-lv="{lv}" style="top:{top}%">'
                      f'<span class="hit"><span class="dot l{lv}"></span></span></a>' for i, (t, lv, top) in enumerate(_TOC))
            + "</div></div></div>"
            for st, attr, hov in (("Nghỉ: chấm mờ, rê chuột để bung nhãn", " data-tooltip-show-children-hover", -1),
                                  ("Bung nhãn: mục 2.1 đang rê", " data-tooltip-show-children", 2)))
              + '<div class="ctl" role="toolbar" aria-label="Điều khiển trang"><button class="toc" type="button" aria-pressed="false" aria-label="Hiện nhãn mục lục">'
              '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6h11M9 12h11M9 18h11M4 6h1M4 12h1M4 18h1"/></svg></button></div></div>'),
        css=(".sc-toc-map{display:flex;flex-wrap:wrap;gap:24px}"
             ".sc-toc-map .ctl{flex:0 0 100%;display:flex;justify-content:flex-end}"
             ".sc-toc-map .toc{width:2.5rem;height:2.5rem;display:grid;place-items:center;padding:0;border:1px solid var(--ovs-border);border-radius:6px;"
             "background:var(--ovs-bg);color:var(--ovs-ink);box-shadow:0 5px 8px -3px rgba(0,0,0,.165);cursor:pointer}"
             ".sc-toc-map .toc[aria-pressed=true]{background:color-mix(in srgb,var(--ovs-accent) 16%,var(--ovs-bg))}"
             ".sc-toc-map .toc svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round}"
             ".sc-toc-map .pane{flex:1;min-width:260px}"
             ".sc-toc-map .st{display:block;margin:0 0 8px;font-size:13px;color:var(--ovs-ink2)}"
             ".sc-toc-map .demo{display:flex;justify-content:flex-end;padding:8px 0;border:1px solid var(--ovs-border);border-radius:8px;background:var(--ovs-bg)}"
             ".sc-toc-map .nw-tocmap{position:relative;flex:none;width:4rem;height:320px}"
             ".sc-toc-map .nw-tip[data-tooltip]::before{content:attr(data-tooltip);position:absolute;right:100%;margin:0 .5rem 0 0;padding:.15rem .4rem;white-space:nowrap;pointer-events:none;"
             "font-family:var(--font-display);font-size:16px;line-height:1.35;color:var(--ovs-ink);font-weight:600;background-color:var(--ovs-surface2);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-radius:6px;"
             "box-shadow:0 1px 2px rgba(15,30,60,.08),0 6px 16px -6px rgba(15,30,60,.22);opacity:0;visibility:hidden;transform:translateX(1rem);"
             "transition:opacity .1s ease-out,transform .1s ease-out,visibility .1s ease-out}"
             ".sc-toc-map .nw-tip[data-tooltip]:focus-visible::before,.sc-toc-map [data-tooltip-show-children] .nw-tip[data-tooltip]::before"
             "{opacity:1;visibility:visible;transform:translateX(0)}"
             "@media(hover:hover){.sc-toc-map .nw-tip[data-tooltip]:hover::before,.sc-toc-map [data-tooltip-show-children-hover]:hover .nw-tip[data-tooltip]::before"
             "{opacity:1;visibility:visible;transform:translateX(0)}}"
             ".sc-toc-map .nw-tocmap a{position:absolute;right:0;display:flex;align-items:center;justify-content:center;text-decoration:none}"
             ".sc-toc-map .nw-tocmap a:hover::before,.sc-toc-map .nw-tocmap a.is-hover::before{background-color:color-mix(in srgb,var(--ovs-accent) 12%,var(--ovs-surface2))}"
             ".sc-toc-map .hit{display:flex;align-items:center;justify-content:flex-end;width:1rem;height:1.75rem;padding:0 .5rem 0 0;box-sizing:content-box}"
             ".sc-toc-map .nw-tocmap:not([data-tooltip-show-children]):not(:hover) .hit{opacity:.22}"
             ".sc-toc-map .dot{display:inline-block;width:5px;height:5px;border-radius:100%;background-color:var(--d);transition:background-color .05s ease-out}"
             ".sc-toc-map .nw-tocmap a:hover .dot,.sc-toc-map .nw-tocmap a.is-hover .dot{background-color:var(--ovs-accent)}"
             ".sc-toc-map .nw-tip[data-lv=\"1\"]::before{font-size:18px;font-weight:700}"
             ".sc-toc-map .nw-tip[data-lv=\"3\"]::before{font-family:var(--font-text);font-size:13.5px;font-weight:400}"
             ".sc-toc-map .nw-tip[data-lv=\"4\"]::before{font-family:var(--font-text);font-size:12px;font-weight:400}"
             ".sc-toc-map .l2{--d:color-mix(in srgb,var(--ovs-ink) 40%,transparent)}"
             ".sc-toc-map .l3{--d:color-mix(in srgb,var(--ovs-ink) 28%,transparent)}"
             ".sc-toc-map .l4{--d:color-mix(in srgb,var(--ovs-ink) 20%,transparent)}"),
        js=("const t=root.querySelector('.toc'),r=root.querySelector('.nw-tocmap');t.addEventListener('click',()=>{const on=r.toggleAttribute('data-tooltip-show-children');"
            "t.setAttribute('aria-pressed',on);t.setAttribute('aria-label',on?'Ẩn nhãn mục lục':'Hiện nhãn mục lục')});"),
    ),
    dict(
        id="topbar", title="Topbar", rules=["title-scale", "tap-target", "clickable-wrap"],
        note="Cao 64px, một đường kẻ dưới; tên trang ≥ 1,2 × mục menu; hẹp thì menu ẩn sau nút, không bẻ chữ.",
        html=('<header class="sc-topbar"><a class="brand" href="#b-topbar">Tên dự án</a>'
              '<div class="links"><a href="#b-topbar">Tài liệu</a><a href="#b-topbar">Bảng giá</a><a href="#b-topbar">Liên hệ</a></div>'
              '<button class="cta" type="button">Bắt đầu</button></header>'),
        css=(".sc-topbar{container-type:inline-size;display:flex;align-items:center;gap:24px;height:64px;padding:0 16px;border-bottom:1px solid var(--ovs-border)}"
             ".sc-topbar .brand{font-family:var(--font-display);font-size:18px;font-weight:var(--fw-heading,600);color:var(--ovs-ink);text-decoration:none;white-space:nowrap}"
             ".sc-topbar .links{display:flex;gap:16px;margin-left:auto}"
             ".sc-topbar .links a{display:inline-flex;align-items:center;min-height:32px;font-size:14px;color:var(--ovs-ink);text-decoration:none;white-space:nowrap}"
             ".sc-topbar .cta{min-height:36px;padding:0 16px;border:0;border-radius:999px;background:var(--ovs-ink);color:var(--ovs-bg);font:inherit;font-weight:600;cursor:pointer;white-space:nowrap}"
             "@container (max-width:520px){.sc-topbar .links{display:none}.sc-topbar .cta{margin-left:auto}}")),
    dict(
        id="type-scale", title="Thang chữ",
        rules=["heading-scale", "sentence-case", "uppercase-misuse", "uppercase-tight-leading", "italic-header", "italic-display", "gradient-text", "font-embedded"],
        note="Hai họ chữ nhúng sẵn: tiêu đề Newsreader 600 (serif), nội dung Be Vietnam Pro 400/1,75. Thang đo từ trang đọc thật (superops tech-hub, 23/09): tiêu đề trang 40 · mục 28 · mục con 22 · nhỏ 18, khoảng TRÊN gấp ~1,7 lần khoảng dưới, luôn đứng thẳng và một màu đặc (không nghiêng, không gradient chữ); nội dung 16/1,6; chữ hoa toàn bộ CHỈ cho nhãn nhỏ.",
        html=('<div class="sc-type-scale"><div class="eyebrow">Nhãn nhỏ</div><div class="t1">Tiêu đề trang 40px — Newsreader</div>'
              '<div class="t2">Tiêu đề mục 28px</div><div class="t3">Tiêu đề mục con 22px</div><div class="t4">Tiêu đề nhỏ 18px</div>'
              '<p class="lead">Câu dẫn 18px, nhạt hơn một bậc, tóm ý cả phần.</p><p>Chữ nội dung 16px, giãn dòng 1,6, độ đậm 400.</p></div>'),
        css=(".sc-type-scale>*{margin:0 0 8px}.sc-type-scale .eyebrow{font-size:11px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--ovs-ink2)}"
             ".sc-type-scale .t1,.sc-type-scale .t2,.sc-type-scale .t3,.sc-type-scale .t4{font-family:var(--font-display);font-weight:var(--fw-heading,600);letter-spacing:var(--ls-heading,-.01em);line-height:1.2}"
             ".sc-type-scale .t1{font-size:40px;line-height:1.25}.sc-type-scale .t2{font-size:28px;line-height:1.42}"
             ".sc-type-scale .t3{font-size:22px;line-height:1.55}.sc-type-scale .t4{font-size:18px;line-height:1.5}"
             ".sc-type-scale .lead{font-size:18px;color:var(--ovs-ink2)}")),
    dict(
        id="prose-columns", title="Chữ dài chia hai cột", rules=["measure-too-wide", "line-height-body"],
        note=("Chữ giải thích dài (chuỗi đoạn từ 600 ký tự, hoặc một đoạn từ 900 ký tự) chia hai cột để mỗi dòng ngắn lại, mắt không phải quét cả bề "
              "ngang trang (user chốt 01/10/2026). Lớp nền tự bọc chuỗi đoạn vào .ovs-cols; khung hẹp hơn hai cột 24em thì tự về một cột."),
        html=('<div class="sc-prose-columns"><div class="ovs-cols">'
              '<p>Một đoạn văn trải hết bề ngang của khung rộng chứa hơn một trăm ký tự mỗi dòng. Mắt phải đi một quãng dài sang phải rồi quay về '
              'đầu dòng kế tiếp, và càng dài thì càng dễ đọc nhầm dòng. Chuẩn WCAG 1.4.8 đặt trần tám mươi ký tự mỗi dòng cho chữ đọc liền.</p>'
              '<p>Thu hẹp khung chữ về chừng ba mươi lăm em giải được bài đó nhưng bỏ trống nửa trang bên phải. Chia hai cột giữ được bề ngang mà '
              'dòng vẫn ngắn: mỗi cột khoảng năm mươi đến sáu mươi ký tự, đúng vùng dễ đọc nhất theo các nghiên cứu về độ dài dòng.</p>'
              '<p>Cột chỉ xuất hiện khi khung đủ rộng cho hai cột hai mươi bốn em. Trên thẻ hẹp, cột phụ hay màn điện thoại, chữ tự quay về một cột '
              'nên không có cột nào hẹp đến mức mỗi dòng chỉ còn vài chữ.</p></div></div>'),
        css=".sc-prose-columns .ovs-cols{margin:0}",
    ),
    dict(
        id="glass-plane", title="Nền khúc xạ và kính ba tầng", rules=["glass", "contrast", "no-cdn"],
        note="Nền KHÔNG phẳng: gradient xanh nhạt + đốm màu trôi rất chậm + lưới chấm mờ (lớp nền tự gắn cho trang docs-shell). Kính ba tầng: điều hướng 55% mờ 24px · thẻ 70% mờ 8px · dữ liệu 88% mờ 4px, mép trên có viền sáng.",
        html=('<div class="sc-glass-plane"><div class="g t1"><b>Tầng 1</b><span>Sidebar, bảng nổi</span></div>'
              '<div class="g t2"><b>Tầng 2</b><span>Thẻ, khung sơ đồ</span></div><div class="g t3"><b>Tầng 3</b><span>Bảng, chữ dài</span></div></div>'),
        css=(".sc-glass-plane{position:relative;overflow:hidden;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(160px,100%),1fr));gap:16px;padding:32px;border-radius:14px;"
             "background:radial-gradient(260px 180px at 12% 20%,rgba(10,132,255,.35),transparent 70%),radial-gradient(240px 200px at 88% 30%,rgba(88,86,214,.28),transparent 70%),"
             "radial-gradient(260px 200px at 50% 110%,rgba(48,176,199,.3),transparent 70%),var(--ovs-bg)}"
             ".sc-glass-plane .g{display:flex;flex-direction:column;gap:4px;padding:16px;border:1px solid var(--ovs-border);border-radius:14px;color:var(--ovs-ink);box-shadow:inset 0 1px 0 rgba(255,255,255,.35)}"
             ".sc-glass-plane .g span{font-size:13px;color:var(--ovs-ink2)}"
             ".sc-glass-plane .t1{background:rgba(var(--ovs-glass-rgb),.55);backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px)}"
             ".sc-glass-plane .t2{background:rgba(var(--ovs-glass-rgb),.7);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}"
             ".sc-glass-plane .t3{background:rgba(var(--ovs-glass-rgb),.88);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px)}")),
    dict(
        id="spacing-scale", title="Thang khoảng cách", rules=["spacing-off-scale", "tight"],
        note="Mọi padding/margin/gap chỉ lấy từ 2 · 4 · 8 · 12 · 16 · 20 · 24 · 32 · 40 · 48 · 64 · 80 · 96px (token --sp-1…--sp-11).",
        html='<div class="sc-spacing-scale">' + "".join(
            f'<div class="r"><code>{v}px</code><i style="width:{v}px"></i></div>' for v in (4, 8, 12, 16, 24, 32, 48, 64, 96)) + "</div>",
        css=(".sc-spacing-scale{display:grid;gap:8px}.sc-spacing-scale .r{display:flex;align-items:center;gap:12px}"
             ".sc-spacing-scale code{width:48px;font-size:12px;color:var(--ovs-ink2)}"
             ".sc-spacing-scale i{display:block;height:12px;border-radius:4px;background:var(--ovs-accent)}")),
    dict(
        id="measure", title="Độ dài dòng và nhịp đoạn", rules=["measure-too-wide", "line-height-body", "heading-proximity"],
        note="Đoạn chữ ≤ 35em (≈ 79 ký tự, vẫn dưới trần 80 của WCAG), giãn dòng 1,75; khoảng TRÊN tiêu đề ≥ 1,5 × khoảng dưới để tiêu đề dính với phần chữ của nó.",
        html=('<div class="sc-measure"><p>Đoạn chữ trước tiêu đề. Dòng dài quá mắt phải quét ngang nhiều, dễ lạc dòng khi xuống; '
              'giới hạn bề rộng giữ nhịp đọc đều.</p><div class="h">Tiêu đề thuộc về đoạn sau</div>'
              '<p>Khoảng trên tiêu đề 32px, khoảng dưới 8px: mắt đọc tiêu đề như mở đầu của đoạn này, không phải kết của đoạn trên.</p></div>'),
        css=(".sc-measure p{max-width:var(--measure,34em);line-height:var(--lh-body,1.6);margin:0}"
             ".sc-measure .h{font-family:var(--font-display);font-size:18px;font-weight:var(--fw-heading,600);margin:32px 0 16px}")),
]
