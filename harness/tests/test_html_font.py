"""test_html_font — nguồn token font DUY NHẤT của framework: Lexend Deca Light nhúng base64 (user chốt 20/09/2026 "nhúng hết")."""
import base64, importlib.util, io, subprocess, sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_s = importlib.util.spec_from_file_location("html_font", ROOT / "fdk/tools/html_font.py")
hf = importlib.util.module_from_spec(_s); _s.loader.exec_module(hf)


def test_head_css_embeds_font_and_sets_light_as_content_default():
    css = hf.head_css()
    assert "@font-face" in css and "src:url(data:font/woff2;base64," in css and "font-weight:300 700" in css
    assert "fonts.googleapis.com" not in css and "http" not in css            # nhúng hết — trang không gọi ra ngoài
    assert "--font-text:'Lexend Deca'," in css and "font-weight:var(--fw-text)" in css and "--fw-text:300" in css
    assert "sans-serif" in hf.FONT_TEXT                                       # luôn có fallback hệ thống
    assert "Lexend" not in hf.FONT_MONO and "code,pre,kbd,samp{font-family:var(--font-mono)}" in css   # code giữ mono
    assert hf.MARK in css


def test_data_module_is_in_sync_with_the_woff2_asset():
    # html_font_data.py = dữ liệu base64 dạng .py để ĐI CÙNG đợt copy fdk/tools/*.py xuống global (asset nhị phân không được copy)
    assert (ROOT / "fdk/tools/html_font_data.py").is_file()
    assert subprocess.run([sys.executable, str(ROOT / "fdk/tools/html_font.py"), "--check"], capture_output=True).returncode == 0
    raw = base64.b64decode(hf._load_b64())
    assert raw[:4] == b"wOF2" and len(raw) < 60_000                           # trần dung lượng: mỗi trang gánh thêm < ~80 KB base64
    assert (ROOT / "fdk/tools/assets/fonts/LexendDeca-NOTICE.txt").read_text(encoding="utf-8").count("Open Font License") >= 1


def test_embedded_font_covers_vietnamese_and_keeps_the_weight_axis():
    ft = pytest.importorskip("fontTools.ttLib")
    pytest.importorskip("brotli")
    f = ft.TTFont(io.BytesIO(base64.b64decode(hf._load_b64())))
    cmap = f.getBestCmap()
    missing = [c for c in "Đường dẫn tiếng Việt ằẵữợỹễộặ ƯƠ đĩũ" if c != " " and ord(c) not in cmap]
    assert not missing, missing
    ax = f["fvar"].axes[0]
    assert (ax.axisTag, ax.minValue, ax.maxValue) == ("wght", 300.0, 700.0)   # 300 cho nội dung, nét đậm THẬT cho tiêu đề
