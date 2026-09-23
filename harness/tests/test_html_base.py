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
    full = css.replace("::first-letter{text-transform:uppercase}", "")      # chữ HOA ĐẦU (sentence-case) ≠ viết HOA toàn bộ
    assert full.count("text-transform:uppercase") == 1 and ".ovs-eyebrow{" in css and "letter-spacing" in css.split(".ovs-eyebrow{")[1].split("}")[0]
    assert "border-left" not in css and "inset" not in css.split(".ovs-theme i")[0]


def test_applied_page_passes_the_runtime_gate_in_both_themes(tmp_path):
    if not shutil.which("node"):
        pytest.skip("không có node")
    f = tmp_path / "p.html"; f.write_text(hb.apply(PLAIN), encoding="utf-8")
    r = subprocess.run(["node", str(ROOT / "fdk/tools/html-visual-gate.mjs"), str(f)], capture_output=True, text=True, cwd=ROOT)
    if r.returncode == 4:
        pytest.skip("không có Playwright")
    assert r.returncode == 0, r.stdout[-700:]


def test_base_css_honours_reduced_motion_on_every_page():
    """Luật reduced-motion-missing (21/09/2026): lớp nền tắt hiệu ứng khi hệ điều hành bật giảm chuyển động."""
    assert "@media (prefers-reduced-motion: reduce)" in hb.base_css(family_dark=True)


def test_apply_refreshes_a_stale_base_block_in_templates():
    """Template nhúng sẵn lớp nền CŨ (problem-tree, 21/09/2026) không được 'bỏ qua vì đã có' — phải nhận CSS nền hiện tại."""
    page = hb.apply("<html><head><title>t</title></head><body><p>x</p></body></html>")
    stale = page.replace("@media (prefers-reduced-motion: reduce)", "@media (x-old)")
    out = hb.apply(stale)
    assert "@media (prefers-reduced-motion: reduce)" in out and out.count(f'id="{hb.STYLE_ID}"') == 1
    assert hb.apply(out) == out


def test_base_css_carries_spacing_scale_and_reading_rhythm_tokens():
    """PLAN 220926-spacing-system: một thang khoảng cách + line-height chữ nội dung 1,6 + độ dài dòng 34em (~68 ký tự thật; 70ch = ~89 vì "0" rộng hơn chữ trung bình), độ ưu tiên 0."""
    css = hb.base_css(family_dark=True)
    assert all(f"--sp-{i}:" in css for i in range(1, 12)) and "--lh-body:1.75" in css and "--measure:35em" in css
    assert ":where(p,li,dd,blockquote){line-height:var(--lh-body)}" in css
