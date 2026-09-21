"""test_html_base — lớp nền chung: token sáng/tối, toggle có nhớ + chống nháy, trang con theo trang mẹ, không chèn trùng, không đụng JS/srcdoc."""
import importlib.util, shutil, subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
def _load(n):
    s = importlib.util.spec_from_file_location(n, ROOT / f"fdk/tools/{n}.py"); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
hb, hf = _load("html_base"), _load("html_font")

PLAIN = ('<html><head><style>:root{--t1:#0f0f12;--t2:#4a4a55;--glass-2:rgba(255,255,255,.7);--border:rgba(30,90,170,.14)}'
         'body{margin:0;padding:32px;color:var(--t1);background:#eaf2fd}.card{background:var(--glass-2);border:1px solid var(--border);'
         'border-radius:12px;padding:16px;margin-bottom:16px;color:var(--t1)}.m{color:var(--t2)}</style></head>'
         '<body><div class="card"><h2>Tiêu đề</h2><p class="m">Nội dung phụ</p></div><div class="card"><p>Thẻ hai</p></div></body></html>')
OWN = ('<html><head><style>[data-theme=dark]{--t1:#eee}</style></head><body><div class="theme-switch"></div>'
       '<script>localStorage.getItem("x-theme")</script></body></html>')


def test_page_without_dark_mode_gets_tokens_toggle_and_fouc_guard():
    out = hb.apply(PLAIN)
    assert out.count('id="ovs-base"') == 1 and out.count('id="ovs-font"') == 1 and out.count('class="ovs-theme"') == 1
    assert out.index('id="ovs-theme-boot"') < out.index("<style>")                 # chống nháy chạy TRƯỚC mọi CSS
    assert "html[data-theme=dark]{" in out and "--t1:#e6e9f0" in out and "--glass-2:" in out   # gán lại ĐÚNG tên biến của họ generator
    assert 'role="switch"' in out and "aria-label=" in out and "localStorage.setItem('ovs-theme'" in out
    assert hb.apply(out) == out and hf.apply(out) == out                            # idempotent qua cả hai cửa


def test_html_font_apply_forwards_to_base_so_generators_need_no_change():
    assert 'id="ovs-base"' in hf.apply(PLAIN)


def test_page_with_its_own_theme_is_not_given_a_second_toggle_nor_overridden_dark_tokens():
    out = hb.apply(OWN)
    assert 'class="ovs-theme"' not in out and 'id="ovs-theme-boot"' not in out
    assert "--t1:#e6e9f0" not in out and "--ovs-ink:" in out


def test_embedded_child_follows_parent_and_has_no_button():
    out = hb.apply(PLAIN, toggle=False)
    assert "data-ovs-theme-follow" in out and 'class="ovs-theme"' not in out and "ovsTheme" in out


def test_toggle_goes_before_the_LAST_body_close_not_one_inside_a_script():
    page = PLAIN.replace("</body>", "<script>var s='</body>';</script></body>")
    out = hb.apply(page)
    assert out.index('class="ovs-theme"') > out.index("var s=")


def test_only_eyebrow_may_be_uppercase_and_cards_have_no_side_stripe():
    css = hb.base_css(family_dark=True)
    assert css.count("text-transform:uppercase") == 1 and ".ovs-eyebrow{" in css and "letter-spacing" in css.split(".ovs-eyebrow{")[1].split("}")[0]
    assert "border-left" not in css and "inset" not in css.split(".ovs-theme i")[0]


def test_applied_page_passes_the_runtime_gate_in_both_themes(tmp_path):
    if not shutil.which("node"):
        pytest.skip("không có node")
    f = tmp_path / "p.html"; f.write_text(hb.apply(PLAIN), encoding="utf-8")
    r = subprocess.run(["node", str(ROOT / "fdk/tools/html-visual-gate.mjs"), str(f)], capture_output=True, text=True, cwd=ROOT)
    if r.returncode == 4:
        pytest.skip("không có Playwright")
    assert r.returncode == 0, r.stdout[-700:]
