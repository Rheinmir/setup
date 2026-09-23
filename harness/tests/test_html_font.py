"""test_html_font — nguồn token font DUY NHẤT của framework: Be Vietnam Pro 400/600/800 nhúng base64 (user chốt "nhúng hết" 20/09, đổi font 21/09/2026)."""
import base64, importlib.util, io, subprocess, sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_s = importlib.util.spec_from_file_location("html_font", ROOT / "fdk/tools/html_font.py")
hf = importlib.util.module_from_spec(_s); _s.loader.exec_module(hf)


def test_head_css_embeds_three_static_weights_and_sets_400_as_content_default():
    css = hf.head_css()
    assert css.count("@font-face") == 6 and "src:url(data:font/woff2;base64," in css        # nội dung ×3 + tiêu đề Newsreader ×1 + Lexend chart ×2
    assert all(f"font-weight:{w};" in css for w in (400, 600, 800))
    assert "fonts.googleapis.com" not in css and "http" not in css            # nhúng hết — trang không gọi ra ngoài
    assert "--font-text:'Be Vietnam Pro'," in css and "font-weight:var(--fw-text)" in css and "--fw-text:400" in css
    assert "--fw-heading:600" in css and "h1,h2{letter-spacing:var(--ls-heading)}" in css
    # TIÊU ĐỀ tách họ riêng (user chốt 22/09/2026): Newsreader nhúng, có fallback serif, và h1–h4 trỏ về --font-display
    assert "--font-display:'Newsreader'," in css and "serif" in hf.FONT_DISPLAY
    assert "font-family:'Newsreader';font-style:normal;font-weight:600" in css
    assert "h1,h2,h3,h4{font-family:var(--font-display);font-weight:var(--fw-heading)}" in css
    assert "sans-serif" in hf.FONT_TEXT                                       # luôn có fallback hệ thống
    assert "Vietnam" not in hf.FONT_MONO and "code,pre,kbd,samp{font-family:var(--font-mono)}" in css   # code giữ mono
    assert hf.MARK in css


def test_data_module_is_in_sync_with_the_woff2_asset():
    # html_font_data.py = dữ liệu base64 dạng .py để ĐI CÙNG đợt copy fdk/tools/*.py xuống global (asset nhị phân không được copy)
    assert (ROOT / "fdk/tools/html_font_data.py").is_file()
    assert all(hf.woff2(w).is_file() for w in hf.WEIGHTS)                    # repo framework PHẢI mang woff2 gốc — thiếu thì --check chỉ tự-nhất-quán (review t9 F2)
    assert subprocess.run([sys.executable, str(ROOT / "fdk/tools/html_font.py"), "--check"], capture_output=True).returncode == 0
    raws = [base64.b64decode(b) for b in hf._load_b64().values()]
    raws += [base64.b64decode(b) for b in hf._load_data().CHART_B64.values()]
    assert all(r[:4] == b"wOF2" for r in raws) and sum(map(len, raws)) < 150_000   # trần PLAN 210926: Be Vietnam Pro ×3 + Lexend chart ×2 < 150 KB
    assert (ROOT / "fdk/tools/assets/fonts/BeVietnamPro-NOTICE.txt").read_text(encoding="utf-8").count("Open Font License") >= 1


def test_embedded_fonts_cover_vietnamese_at_every_weight():
    ft = pytest.importorskip("fontTools.ttLib")
    pytest.importorskip("brotli")
    for w, b in hf._load_b64().items():
        f = ft.TTFont(io.BytesIO(base64.b64decode(b)))
        cmap = f.getBestCmap()
        missing = [c for c in "Đường dẫn tiếng Việt ằẵữợỹễộặ ƯƠ đĩũ" if c != " " and ord(c) not in cmap]
        assert not missing, (w, missing)
        assert f["OS/2"].usWeightClass == w                                   # nét THẬT của từng weight, không giả đậm


def test_review_C2_apply_only_touches_css_in_head_never_body_js_or_srcdoc():
    """Hồi quy review 20/09/2026: regex quét toàn trang từng phá iframe srcdoc, cắt đôi stack có "Segoe UI", ăn nháy đóng chuỗi JS."""
    page = ('<html><HEAD><style>body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:red}'
            'code{font-family:-apple-system-mono,ui-monospace,monospace}</style></HEAD><body>'
            "<iframe srcdoc=\"&lt;style&gt;body{font-family:-apple-system,sans-serif}&lt;/style&gt;\"></iframe>"
            "<script>el.style.cssText='font-family:-apple-system,sans-serif';go();var t=`<span style='font-family:-apple-system,sans-serif'>${x}</span>`;var s='</head>';</script></body></html>")
    out = hf.apply(page)
    assert 'body{font-family:var(--font-text);color:red}' in out                      # stack trong <head> → token, KHÔNG để sót đuôi `"Segoe UI",…`
    assert "code{font-family:-apple-system-mono,ui-monospace,monospace}" in out          # mono không bị đụng
    assert "srcdoc=\"&lt;style&gt;body{font-family:-apple-system,sans-serif}" in out      # tài liệu con trong iframe: nguyên vẹn
    assert "el.style.cssText='font-family:-apple-system,sans-serif';go();" in out and "${x}</span>`" in out   # JS nguyên vẹn
    assert out.count('id="ovs-font"') == 1 and out.index('id="ovs-font"') < out.index("<body>")   # chèn vào </HEAD> THẬT (không phân biệt hoa thường), không phải chuỗi '</head>' trong JS
    assert hf.apply(out) == out


def test_apply_refreshes_a_stale_embedded_font_block_instead_of_skipping_it():
    """Đổi font 21/09/2026: template/skeleton nhúng sẵn khối font CŨ; bản trước coi 'đã có id' là xong → kẹt Lexend mãi."""
    stale = "<html><head><style id=\"ovs-font\">@font-face{font-family:'Lexend Deca'}</style></head><body>x</body></html>"
    out = hf.apply(stale)
    assert "font-family:'Lexend Deca'}</style>" not in out and hf.MARK in out and out.count('id="ovs-font"') == 1
    assert hf.apply(out) == out


def test_chart_text_uses_lexend_light_and_bold_maps_to_regular():
    """User chốt 22/09/2026: trong sơ đồ/graph mặc định Lexend Deca Light, đậm = Lexend Deca thường (Regular).
    Hai bản TĨNH chia theo dải độ đậm — không ép font-weight (bản ép làm nhãn đậm của graph mất đậm)."""
    css = hf.head_css()
    assert "font-weight:1 499" in css and "font-weight:500 1000" in css and css.count(f"font-family:'{hf.CHART_FAMILY}'") >= 2
    assert "--font-chart:'Lexend Deca'" in css and "font-synthesis:none" in hf.chart_css()
    assert "font-weight" not in hf.chart_css()                                # KHÔNG ép — để dải @font-face quyết nét
    ft = pytest.importorskip("fontTools.ttLib"); pytest.importorskip("brotli")
    for w, b in hf._load_data().CHART_B64.items():
        f = ft.TTFont(io.BytesIO(base64.b64decode(b)))
        assert f["OS/2"].usWeightClass == w and "fvar" not in f                 # bản tĩnh: trình duyệt không vẽ được 700 từ nó
        assert all(ord(c) in f.getBestCmap() for c in "Đườngữợỹ")
