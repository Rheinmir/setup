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


def test_rounded_edge_catches_what_side_stripe_misses_and_spares_uniform_or_unrounded():
    bad = {
        "cascade": ".card{border-radius:12px}.x{color:red}.card{border-left:4px solid #e23b2d}",
        "longhand-color": ".card{border:1px solid #ddd;border-left-color:#2563eb;border-radius:10px}",
        "var-accent": ".card{border-left:3px solid var(--accent);border-radius:8px}",
        "top": ".card{border-top:2px solid #0a84ff;border-radius:0 0 8px 8px}",
        "inline-start": ".card{border-inline-start:3px solid var(--accent);border-top-left-radius:6px}",
        "blockquote": "blockquote{border-left:4px solid #0a84ff;border-radius:8px}",
        "media-cascade": ".card{border-radius:12px}@media (min-width:1px){.card{border-left:4px solid #e23b2d}}",
        "thicker": ".card{border:1px solid var(--accent);border-left-width:4px;border-radius:8px}",
        "opposite": ".card{border-left:3px solid #e23b2d;border-right:3px solid #e23b2d;border-radius:8px}",
        "tab-active": ".tab.active{border:1px solid #d0d0d4;border-bottom:2px solid var(--accent);border-radius:8px 8px 0 0}",
        "three-sides": ".tab{border:2px solid #0a84ff;border-bottom:0;border-radius:8px 8px 0 0}",
    }
    for name, css in bad.items():
        assert "rounded-edge" in rules(DARK + css, TOGGLE), name
    assert "rounded-edge" in rules(DARK, TOGGLE + '<div style="border-radius:8px;border-left:4px solid red">x</div>')
    good = (".card{border:1px solid var(--line);border-radius:12px}", ".card{border-left:4px solid red}",
            ".card{border-bottom:1px solid #e5e5e5;border-radius:8px}", ".card{border-radius:0;border-left:4px solid red}",
            ".avatar{border-radius:50%}", ".avatar{border-radius:50%;border:2px solid #0a84ff}",
            ".sp{border:3px solid #e5e5e5;border-top-color:#0a84ff;border-radius:50%}",          # spinner tải (review t9 F3)
            ".tab{border-bottom:1px solid color-mix(in srgb, var(--ink) 12%, transparent);border-radius:8px}",   # kẻ xám pha màu (F5)
            ".card{border:1px solid #ddd;border-left:1px dashed #ddd;border-radius:8px}",
            ".card{border-bottom:1px solid hsl(220 0% 80%);border-radius:8px}", ".card{border-top:1px solid oklch(0.85 0 0);border-radius:8px}",
            ".card{border:1px solid #0a84ff;border-left-width:1.2px;border-radius:8px}")
    for ok in good:
        assert "rounded-edge" not in rules(DARK + ok, TOGGLE), ok
    # side-stripe giữ nguyên hành vi: cạnh màu KHÔNG bo tròn vẫn do side-stripe bắt
    assert "side-stripe" in rules(DARK + ".card{border-left:4px solid red}", TOGGLE)


def _levels(css, body=TOGGLE):
    html = f"<html><head><style>{PAD}{DARK}{css}</style></head><body>{body}</body></html>"
    return {f["rule"]: f["level"] for f in fap._scan_text(html) if f.get("rule")}


def test_transition_all_caught_in_css_inline_and_tailwind_class_but_listed_properties_spared():
    assert _levels(".btn{transition:all .2s}").get("transition-all") == "FAIL"
    assert _levels(".btn{transition-property:all}").get("transition-all") == "FAIL"
    assert "transition-all" in _levels("", TOGGLE + '<a style="transition: all 150ms">x</a>')
    assert "transition-all" in _levels("", TOGGLE + '<button class="px-2 transition-all duration-200">x</button>')
    for ok in (".btn{transition:background-color .2s,color .2s}", ".btn{transition:allow .2s}", ".btn{--transition:all}"):
        assert "transition-all" not in _levels(ok), ok
    assert "transition-all" not in _levels("", TOGGLE + "<p>đừng dùng <code>transition-all</code></p>")   # văn xuôi không phải vi phạm


def test_reduced_motion_missing_fails_on_animation_warns_on_transform_and_spares_pages_with_media_query():
    anim = "@keyframes f{to{transform:rotate(1turn)}}.s{animation:f 1s infinite}"
    assert _levels(anim).get("reduced-motion-missing") == "FAIL"
    assert _levels(".s{animation-name:spin}").get("reduced-motion-missing") == "FAIL"
    assert _levels(".card{transition:transform .2s}").get("reduced-motion-missing") == "WARN"
    for ok in (anim + "@media (prefers-reduced-motion:reduce){.s{animation:none}}", ".s{animation:none}",
               ".card{transition:opacity .2s}", ".card{transition:transform .2s}@media (prefers-reduced-motion: reduce){.card{transition:none}}"):
        assert "reduced-motion-missing" not in _levels(ok), ok
