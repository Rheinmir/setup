"""test_frontend_antipattern_slop — cổng slop của framework phải BẮT slop do chính framework sinh (user 20/09/2026:
"có cơ chế bắt slop bắt buộc nhưng chưa tự bắt nó"). Mỗi luật: bản BAD bị bắt, bản GOOD được tha."""
import importlib.util, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "fdk/tools/frontend-antipattern.py"
_s = importlib.util.spec_from_file_location("fap", TOOL); fap = importlib.util.module_from_spec(_s); _s.loader.exec_module(fap)

PAD = "body{margin:0;color:#111;background:#fff}" + ".x{padding:1px}" * 40            # > 400 ký tự CSS → tính là trang thật
DARK = '[data-theme="dark"]{--bg:#000}'
TOGGLE = '<button class="theme-toggle" aria-label="Đổi giao diện"></button><script>localStorage.getItem("t");document.documentElement.setAttribute("data-theme","dark")</script>'


def rules(css, body="", extra_head=""):
    html = f"<html><head>{extra_head}<style>{PAD}{css}</style></head><body>{body}</body></html>"
    return {f.get("rule") for f in fap._scan_text(html) if f.get("rule")}


def test_side_stripe_three_ways_are_caught_and_neutral_lines_are_spared():
    assert "side-stripe" in rules(DARK + ".card{border-left:4px solid var(--accent)}", TOGGLE)
    assert "side-stripe" in rules(DARK + ".card{box-shadow:inset 3px 0 0 #0a84ff, 0 1px 2px rgba(0,0,0,.1)}", TOGGLE)
    assert "side-stripe" in rules(DARK + ".card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:#30b0c7}", TOGGLE)
    assert "side-stripe" in rules(DARK, TOGGLE + '<div style="border-left:5px solid #ef4444">x</div>')
    for ok in (".card{border-left:1px solid var(--border)}", ".card{border-left:4px solid #d0d0d4}", "blockquote{border-left:4px solid #0a84ff}",
               ".card{border:1px solid var(--accent)}", ".rule::before{content:'';width:4px;height:100%;background:rgba(0,0,0,.08)}"):
        assert "side-stripe" not in rules(DARK + ok, TOGGLE), ok


def test_page_without_dark_mode_or_without_toggle_fails_but_embedded_child_may_follow_parent():
    assert "no-dark-mode" in rules("", "")
    assert "no-theme-toggle" in rules(DARK, "")
    assert not {"no-dark-mode", "no-theme-toggle"} & rules(DARK, TOGGLE)
    assert not {"no-dark-mode", "no-theme-toggle"} & rules(DARK, '<div data-ovs-theme-follow></div>')
    js_built = "<script>var sw=document.createElement('div');sw.className='theme-switch';localStorage.setItem('theme','dark')</script>"
    assert "no-theme-toggle" not in rules(DARK, js_built)                              # nút dựng bằng JS (graph-viz) vẫn là toggle


def test_uppercase_only_for_small_labels_with_letter_spacing():
    assert "uppercase-misuse" in rules(DARK + "h2{text-transform:uppercase;letter-spacing:.1em}", TOGGLE)
    assert "uppercase-misuse" in rules(DARK + ".btn{text-transform:uppercase;letter-spacing:.1em}", TOGGLE)
    assert "uppercase-misuse" in rules(DARK + ".eyebrow{text-transform:uppercase}", TOGGLE)               # thiếu letter-spacing
    assert "uppercase-misuse" not in rules(DARK + ".eyebrow{text-transform:uppercase;letter-spacing:.08em;font-size:11px}", TOGGLE)


def test_css_in_prose_is_not_a_violation_and_embedded_font_does_not_hang_the_gate():
    assert "side-stripe" not in rules(DARK, TOGGLE + "<p>đừng viết <code>border-left:4px solid red</code></p>")
    big = "@font-face{font-family:'X';src:url(data:font/woff2;base64," + "A" * 60000 + ")}"
    t0 = time.time(); rules(DARK + big + ".card{border-left:4px solid #0a84ff}", TOGGLE)
    assert time.time() - t0 < 3, "regex O(n²) trên font nhúng base64 — đã treo cổng ngày 20/09/2026"


def test_all_scope_covers_every_framework_page_not_just_overstack():
    pages = [p.name for p in fap.framework_pages(ROOT)]
    assert "overstack.html" in pages and len(pages) >= 2
    r = subprocess.run([sys.executable, str(TOOL), "--self-test"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-400:]
