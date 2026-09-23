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


def test_sidebar_gets_icon_tiles_label_and_number_in_title_without_wrapping_chip():
    out = sh.apply(page())
    nav = re.search(r"<nav\b.*?</nav>", out, re.S).group(0)
    assert nav.count('class="ic"') == 4 and nav.count("ovs-na") == 4
    assert 'title="01 · Vấn đề"' in nav and '<span class="ovs-lbl">Vấn đề</span>' in nav
    assert "ovs-num" not in nav                                       # chip số làm nhãn bẻ 2 dòng ở sidebar 200px
    assert "<svg" in nav and 'class="ovs-progress"' in nav


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
    assert n.count('class="ic"') == 4 and "Brandsub" not in n


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
