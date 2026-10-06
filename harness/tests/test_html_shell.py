"""test_html_shell — bộ khung trang tài liệu tự gắn (PLAN 220926-docs-shell-kit)."""
import importlib.util, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(name):
    s = importlib.util.spec_from_file_location(name, ROOT / f"fdk/tools/{name}.py"); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


sh, hb = _load("html_shell"), _load("html_base")
NAV = ('<nav><div class="logo">Tài liệu<small>phụ đề</small></div>'
       '<a href="#sec-0">01 · Vấn đề</a><a href="#sec-1">02 · Bản đồ layout</a>'
       '<a href="#sec-2">03 · Đường giao hàng</a><a href="#sec-3">04 · Nghiệm thu</a></nav>')
SECS = ('<section id="sec-0"><h1>Tiêu đề trang</h1></section>'
        '<section id="sec-1"><h2>Phần một</h2><h3>Ý a</h3><h3>Ý b</h3></section>'
        '<section id="sec-2"><h2>Phần hai</h2></section><section id="sec-3"><h2>Phần ba</h2></section>')


def page(extra_head="", body_tail="</body></html>", nav=NAV, secs=SECS):
    return f"<!doctype html><html><head><title>t</title><style>body{{margin:0}}{extra_head}</style></head><body>{nav}{secs}{body_tail}"


def test_non_docs_shell_page_is_untouched():
    p = "<html><head></head><body><nav><a href='#'>x</a></nav><p>y</p></body></html>"
    assert sh.apply(p) == p


def test_nav_becomes_tocmap_rail_of_dots_with_labels_in_tooltip():
    """User 30/09/2026 (/goal): điều hướng = TOC map của m3e-canvas docs/namuwiki-ui-kit.html — mỗi mục là một chấm, chữ nằm trong tooltip."""
    out = sh.apply(page())
    nav = re.search(r"<nav\b.*?</nav>", out, re.S).group(0)
    tag = re.search(r"<nav\b[^>]*>", nav).group(0)
    assert 'class="ovs-side nw-tocmap"' in tag and "data-tooltip-show-children-hover" in tag and 'id="ovs-sidebar"' in tag
    assert nav.count('class="ovs-na nw-tip"') == 4 and nav.count('<span class="hit"><span class="dot l2"></span></span>') == 4
    assert 'data-tooltip="01 · Vấn đề" aria-label="01 · Vấn đề" style="top:12.50%"' in nav and 'style="top:87.50%"' in nav
    assert "ovs-lbl" not in nav and "title=" not in nav and "ovs-mark" not in nav and 'class="ovs-progress"' not in nav
    assert out.count('class="ovs-progress"') == 1 and "JS_NAV" not in out and "nav.nw-tocmap" in out
    css = re.search(r'<style id="ovs-shell">(.*?)</style>', out, re.S).group(1)
    for rule in ("a.ovs-na .dot{flex:none;margin:0", "a.ovs-na.active .dot{background:var(--ovs-accent", 'a.ovs-na[data-lv="1"]::before{font-size:18px;font-weight:700}', 'a.ovs-na[data-lv="3"]::before{font-family:var(--font-text,sans-serif);font-size:13.5px', "a.ovs-na.active::before{background-color:color-mix(", "background-color:var(--ovs-surface2,#fff);backdrop-filter:blur(12px)",
                 "a.ovs-na>:not(.hit){display:none}", "[data-dense][data-hover] a.ovs-na{position:static", "a.ovs-na .hit{opacity:.22"):
        assert rule in css, rule
    assert "setAttribute('data-lv'" in out and "e.clientX>=innerWidth-176" in out and "nw-tocmap{width:4rem}" not in css      # vùng rê do JS đo từ mép phải, không phải hộp bắt chuột vô hình


def test_controls_are_a_floating_group_before_nav_theme_toggle_and_label_button():
    """User 30/09: bỏ dải trên ("top menu"), điều khiển thành cụm nổi góc phải dưới — nút sáng/tối + nút bật nhãn mục lục, không tên trang, nằm ngoài <main>."""
    out = hb.apply(page())
    nav = re.search(r"<nav\b.*?</nav>", out, re.S).group(0)
    assert "ovs-theme-row" not in out and 'class="ovs-theme"' not in nav
    bar = re.search(r'<div class="ovs-bar" role="toolbar".*?<!--/ovs-bar--></div>', out, re.S).group(0)
    assert "ovs-brand" not in out and "ovs-mark" not in out and "ovs-ctl" not in out
    assert out.index('class="ovs-bar"') < out.index("<nav") < out.index("<main") and "position:fixed;right:12px;bottom:16px" in out
    assert 'class="ovs-navbtn" aria-controls="ovs-sidebar" aria-pressed="false" aria-label="Hiện nhãn mục lục"' in bar
    assert 'class="ovs-theme"' in bar and out.count('class="ovs-theme"') == 1 and out.count('class="ovs-bar"') == 1
    assert sh.apply(out) == out


def test_pages_already_carrying_the_old_sidebar_are_migrated_to_the_rail():
    """Trang đã áp bản sidebar cũ (icon tile / nhãn .ovs-lbl + số thứ tự trong title / brand bọc ô chữ) → cùng kết quả như trang mới."""
    fresh = sh.apply(page())
    old_nav = ('<nav class="ovs-side" id="ovs-sidebar"><div class="logo"><span class="ovs-mark" aria-hidden="true">T</span>'
               '<span class="ovs-brand">Tài liệu<small>phụ đề</small></span></div>'
               '<a href="#sec-0" class="ovs-na" title="01 · Vấn đề"><span class="ic" style="--ic:#0a84ff"><b aria-hidden="true">V</b></span><span class="ovs-lbl">Vấn đề</span></a>'
               '<a href="#sec-1" class="ovs-na" title="02 · Bản đồ layout"><span class="ovs-lbl">Bản đồ layout</span></a>'
               '<a href="#sec-2" class="ovs-na" title="03 · Đường giao hàng"><span class="ovs-lbl">Đường giao hàng</span></a>'
               '<a href="#sec-3" class="ovs-na" title="04 · Nghiệm thu"><span class="ovs-lbl">Nghiệm thu</span></a></nav>')
    out = sh.apply(page(nav=old_nav))
    nav = re.search(r"<nav\b.*?</nav>", out, re.S).group(0)
    assert 'class="ic"' not in nav and "ovs-lbl" not in nav and "ovs-mark" not in nav and "title=" not in nav
    assert nav.count("nw-tip") == 4 and 'data-tooltip="01 · Vấn đề"' in nav and '<div class="logo">Tài liệu<small>phụ đề</small></div>' in nav
    assert re.search(r'<div class="ovs-bar".*?</div>', out, re.S).group(0) == re.search(r'<div class="ovs-bar".*?</div>', fresh, re.S).group(0)
    assert sh.apply(out) == out


def test_other_sidebars_get_the_rail_but_not_the_docs_shell_extras():
    """User 30/09 "thay thế mặc định thì áp hết": trang có sidebar `.brand` (graph của engine, control-room, atlas) cũng đổi sang rail — kể cả link
    sang trang khác — nhưng KHÔNG nhận mind map / skip-link / favicon / vạch tiến độ của docs-shell."""
    nav = ('<nav><div class="brand">orca-graph</div><a href="#top">G</a><div class="grp">Mục</div><a href="#a">Đồ thị</a>'
           '<a href="atlas.html">Atlas</a><a href="#b">Node</a></nav>')
    p = page(nav=nav)
    assert not sh.is_docs_shell(p) and sh.is_side_nav(p)
    out = sh.apply(p)
    n = re.search(r"<nav\b.*?</nav>", out, re.S).group(0)
    assert "nw-tocmap" in n and n.count("nw-tip") == 4 and 'href="atlas.html" class="ovs-na nw-tip" data-tooltip="Atlas"' in n
    assert 'class="ovs-navbtn"' in out and "JS_TOC" not in out and "nav.nw-tocmap" in out
    for extra in ('class="ovs-mindmap"', 'class="skip-link"', 'rel="icon"', 'class="ovs-progress"', "pointerdown", 'style="display:contents"'):
        assert extra not in out, extra
    assert sh.apply(out) == out
    few = page(nav='<nav><div class="brand">X</div><a href="#a">A</a><a href="b.html">B</a></nav>')
    assert sh.apply(few) == few                                       # dưới 4 link → không phải sidebar, không đụng


def test_page_with_its_own_theme_gets_the_rail_on_the_first_apply():
    """overstack.html (30/09): trang tự có chế độ tối + nút đổi → html_base trả thẳng ở lần áp đầu, bỏ qua bộ khung; lần hai mới gắn →
    generator ra sidebar còn `--apply` ra rail, medic báo "docs cũ so đĩa". Lần đầu phải ra đúng như lần hai."""
    own = page(extra_head='[data-theme="dark"]{--x:1}', body_tail='<button class="theme-toggle"></button><script>localStorage.getItem("t")</script></body></html>')
    once = hb.apply(own)
    assert "nw-tocmap" in once and 'class="ovs-theme"' not in once and hb.apply(once) == once


def test_a11y_skip_link_main_and_favicon_are_added():
    out = sh.apply(page())
    assert 'class="skip-link" href="#main"' in out and re.search(r'<main id="main" style="display:contents">', out)
    assert re.search(r'<link rel="icon" href="data:', out)


def test_main_is_not_wrapped_when_css_uses_body_child_selector():
    out = sh.apply(page(extra_head="body>section{padding:1px}"))
    assert '<main id="main"' not in out


def test_page_without_closing_body_still_gets_js():
    out = sh.apply(page(body_tail=""))
    assert out.rstrip().endswith("</script>") and 'id="ovs-shell-js"' in out


def test_mind_map_is_built_from_h2_h3_only_when_page_has_none():
    out = sh.apply(page())
    assert out.count("ovs-mindmap") >= 1 and '<span class="nm">Phần một</span>' in out and '<span class="nm">Ý a</span>' in out
    own = page(secs=SECS + '<div class="mm">tự vẽ</div>')
    assert '<section class="ovs-mindmap"' not in sh.apply(own)


def test_draggable_js_only_when_page_has_diagram_box():
    assert "initDraggableDiagrams" not in sh.apply(page())
    out = sh.apply(page(secs=SECS + '<div class="diagram-box"><svg><rect x="0" y="0" width="80" height="40"/></svg></div>'))
    assert "initDraggableDiagrams" in out


def test_apply_is_idempotent_and_goes_through_html_base():
    once = hb.apply(page())
    assert hb.apply(once) == once and once.count('id="ovs-shell"') == 1 and once.count('id="ovs-shell-js"') == 1


def test_vendor_blocks_are_verbatim_copies_of_the_skill():
    """Luật repo: code gốc chép NGUYÊN — sửa ở skill rồi `html_shell.py --sync`, không sửa tay bản trích."""
    b = sh.skill_blocks((ROOT / "skills/docs-site-macos/SKILL.md").read_text(encoding="utf-8"))
    v = sh._vendor()
    assert all(getattr(v, k) == b[k] for k in b), "html_shell_vendor.py lệch skill — chạy: python3 fdk/tools/html_shell.py --sync"


# ── hồi quy review t8 (22/09/2026) ──
def test_R2_idempotent_on_page_that_already_has_its_own_spy_and_ripple():
    own = page(body_tail="<script>new IntersectionObserver(()=>{});/*ripple*/</script></body></html>")
    once = sh.apply(own)
    assert sh.apply(once) == once
    js = re.search(r'<script id="ovs-shell-js">(.*?)</script>', once, re.S).group(1)
    assert "IntersectionObserver" not in js and "ovs-ripple" not in js      # trang tự có → không chèn đôi


def test_R3_skip_link_targets_existing_main_id_and_body_child_css_is_not_wrapped():
    out = sh.apply(page(secs='<main id="content">' + SECS + "</main>"))
    assert 'href="#content"' in out and 'id="main"' not in out
    out2 = sh.apply(page(extra_head="body>section{padding:1px}"))
    assert "<main" not in out2 and 'class="skip-link"' not in out2                # không có đích thì không chèn skip-link trỏ vào hư không


def test_R6_logo_anchor_is_not_a_nav_item():
    nav = NAV.replace('<div class="logo">Tài liệu<small>phụ đề</small></div>', '<a class="logo" href="#top">Brand<small>sub</small></a>')
    out = sh.apply(page(nav=nav))
    n = re.search(r"<nav\b.*?</nav>", out, re.S).group(0)
    assert n.count("ovs-na") == 4 and '<a class="logo" href="#top">Brand<small>sub</small></a>' in n      # logo giữ nguyên trong nav (ẩn), không thành chấm


def test_R7_nav_inside_header_or_sibling_css_blocks_main_wrap():
    hdr = page(nav="<header>" + NAV + "</header>")
    assert '<main id="main" style="display:contents">' not in sh.apply(hdr)
    sib = page(extra_head="nav~section{margin-left:200px}")
    assert '<main id="main" style="display:contents">' not in sh.apply(sib)


def test_R8_meta_opt_out_leaves_page_untouched():
    p = page(extra_head="").replace("<title>t</title>", '<title>t</title><meta name="overstack-shell" content="none">')
    assert sh.apply(p) == p


def test_R9_favicon_in_any_attribute_order_counts():
    p = page().replace("<title>t</title>", '<title>t</title><link href="/f.ico" rel="icon">')
    assert sh.apply(p).count('rel="icon"') == 1
