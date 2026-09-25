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

BLOCKS = [
    _grid(1, "dùng cho nội dung đọc dài, giới hạn bề rộng bằng --measure", [("Một cột", "Bài viết, hướng dẫn, form dài.")]),
    _grid(2, "khung hẹp hơn 520px thì rơi về 1 cột", _LB[:2]),
    _grid(3, "khung hẹp hơn 680px thì rơi thẳng về 1 cột (3 → 2 để lại ô mồ côi)", _LB[:3]),
    _grid(4, "khung hẹp hơn 760px còn 2 cột, hẹp hơn 420px còn 1 cột", _LB),
    dict(
        id="sidebar", title="Sidebar chuẩn", rules=["hierarchy-flat", "title-scale", "sentence-case", "tap-target", "clickable-wrap", "band-misaligned"],
        note="Rộng 240–256px, nút thu về thanh icon 64px (nhãn còn trong title); tên trang 18px/800; nhãn nhóm 11px/700 chữ hoa giãn chữ, cùng độ đậm màu với mục; mục 13px, cao ≥ 32px; mục đang xem = nền viên + chấm màu. Hàng cuối (công tắc giao diện) thẳng cột với mục, chung nền sidebar, không margin âm hay nền riêng (luật band-misaligned).",
        html=('<nav class="sc-sidebar" aria-label="Ví dụ sidebar"><div class="top"><a class="logo" href="#b-sidebar"><span class="lb">Tên dự án</span></a>'
              '<button class="fold" type="button" aria-expanded="true" aria-label="Thu gọn sidebar"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="3"/><path d="M9 4v16"/></svg></button></div>'
              '<div class="grp">Bắt đầu</div>'
              + "".join(f'<a{_ON if i == 0 else ""} href="#b-sidebar" title="{t}"><span class="ic">{t[0]}</span><span class="lb">{t}</span></a>'
                        for i, t in enumerate(["Tổng quan", "Cài đặt"]))
              + '<div class="grp">Tham khảo</div>'
              + "".join(f'<a href="#b-sidebar" title="{t}"><span class="ic">{t[0]}</span><span class="lb">{t}</span></a>' for t in ["Luật thiết kế", "Câu hỏi thường gặp"])
              + '</nav>'),
        css=(".sc-sidebar{width:248px;max-width:100%;box-sizing:border-box;padding:16px;border:1px solid var(--ovs-border);border-radius:14px;background:var(--ovs-surface2);overflow:hidden;transition:width .2s ease-out}"
             ".sc-sidebar .top{display:flex;align-items:center;justify-content:space-between;gap:8px}"
             ".sc-sidebar .fold{flex:none;width:32px;height:32px;display:grid;place-items:center;border:1px solid var(--ovs-border);border-radius:8px;background:none;color:var(--ovs-ink);cursor:pointer}"
             ".sc-sidebar .fold svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:1.8}"
             ".sc-sidebar .ic{flex:none;width:24px;height:24px;border-radius:7px;display:grid;place-items:center;font-size:12px;font-weight:700;background:var(--ovs-accent-bg);color:var(--ovs-ink)}"
             ".sc-sidebar .lb{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
             ".sc-sidebar.rail{width:64px;padding:16px 12px}.sc-sidebar.rail .lb,.sc-sidebar.rail .grp,.sc-sidebar.rail .logo{display:none}"
             ".sc-sidebar.rail .top{justify-content:center}.sc-sidebar.rail a:not(.logo){justify-content:center;padding:4px}"
             ".sc-sidebar .logo{display:block;font-family:var(--font-display);font-size:18px;font-weight:var(--fw-heading,600);padding:0 8px 8px;color:var(--ovs-ink);text-decoration:none}"
             ".sc-sidebar .grp{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ovs-ink);margin:16px 8px 4px}"
             ".sc-sidebar a:not(.logo){display:flex;align-items:center;gap:8px;min-height:32px;padding:4px 8px;border-radius:8px;font-size:13px;color:var(--ovs-ink);text-decoration:none}"
             ".sc-sidebar a.on{background:var(--ovs-accent-bg);font-weight:600}.sc-sidebar a.on .ic{background:var(--ovs-accent);color:#fff}"
             ".sc-sidebar a:not(.logo):hover{background:var(--ovs-accent-bg)}"),
        js=("const f=root.querySelector('.fold');f.addEventListener('click',()=>{const r=root.classList.toggle('rail');"
            "f.setAttribute('aria-expanded',!r);f.setAttribute('aria-label',r?'Mở rộng sidebar':'Thu gọn sidebar')});")),
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
