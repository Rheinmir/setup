"""test_html_slop_fix_spacing — phép vá 7: khoảng cách về MỘT thang, line-height chữ nội dung ≥ 1,5 (PLAN 220926-spacing-system)."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_s = importlib.util.spec_from_file_location("hsf", ROOT / "fdk/tools/html-slop-fix.py"); hsf = importlib.util.module_from_spec(_s); _s.loader.exec_module(hsf)
_v = importlib.util.spec_from_file_location("ssv", ROOT / "fdk/tools/spacing-survey.py"); ssv = importlib.util.module_from_spec(_v); _v.loader.exec_module(ssv)


def test_snap_goes_to_nearest_step_ties_up_keeps_hairlines():
    assert [hsf.snap(x) for x in (3, 6, 10, 14, 18, 22, 28, 36, 100)] == [4, 8, 12, 16, 20, 24, 32, 40, 96]
    assert hsf.snap(1) == 1 and hsf.snap(0) == 0 and hsf.snap(-6) == -4


def test_spacing_and_body_line_height_fixed_but_headings_buttons_calc_untouched():
    css, ns, nl = hsf.fix_spacing(".a{padding:6px 10px;margin:.9rem}p{line-height:1.35}h2{line-height:1.2}"
                                  ".btn{line-height:1;padding:7px}.w{margin:calc(10px + 1rem)}")
    assert ".a{padding:8px 12px;margin:1rem}" in css and "p{line-height:var(--lh-body,1.6)}" in css
    assert "h2{line-height:1.2}" in css and ".btn{line-height:1;padding:8px}" in css and "calc(10px + 1rem)" in css
    assert (ns, nl) == (4, 1)


def test_fixed_css_is_on_scale_by_the_survey_and_idempotent():
    css = ".x{padding:5px 7px 9px 11px;gap:13px;margin:0 auto}"
    once, _, _ = hsf.fix_spacing(css)
    assert ssv.off_scale(once) == [] and hsf.fix_spacing(once)[0] == once


def test_review_t8_fix_markup_never_touches_js_code_samples_data_style_or_srcdoc():
    h = ('<style>.a{padding:6px}</style><script>var t="<style>.b{padding:6px}</style>";</script>'
         '<pre>&lt;div style="padding:6px"&gt;</pre><p data-style="padding:6px">style="padding:6px"</p>'
         "<iframe srcdoc='<style>.c{padding:6px}</style>'></iframe><div style=\"padding:6px\">x</div>")
    o = hsf.fix_markup(h, [])
    assert ".a{padding:8px}" in o and '<div style="padding:8px">' in o
    assert '.b{padding:6px}' in o and '&lt;div style="padding:6px"&gt;' in o and 'data-style="padding:6px"' in o
    assert ">style=\"padding:6px\"</p>" in o and ".c{padding:6px}" in o


def test_review_t8_body_selector_is_word_based_and_negative_ties_go_toward_zero():
    css, _, nl = hsf.fix_spacing(".text-muted{line-height:1.2}.lead-in{line-height:1.2}.summary{line-height:1.2}.sidebar li{line-height:1.2}.desc{line-height:1.2}")
    assert nl == 1 and ".desc{line-height:var(--lh-body,1.6)}" in css
    assert hsf.snap(-6) == -4 and hsf.snap(6) == 8
    assert ssv.off_scale(".x{gap:var(--sp,10px)}") == []          # var(): survey khớp cổng tĩnh + phép vá


def test_fix_case_capitalizes_labels_but_spares_identifiers_brands_code_and_keep():
    h = ('<nav><div class="brand">bảng dispatch · kanban</div><a href="#a">t1 · chốt</a><a href="#b">atlas graph</a><a>overstack</a></nav>'
         '<h3>xét lại</h3><button>⤢ mở hết</button><label><input type="checkbox"> hiện cả wiki</label><h3 data-case="keep">herdr</h3>'
         '<p>chữ thường giữ</p><code><button>x</button></code>')
    o = hsf.fix_markup(h, [])
    assert "Bảng dispatch" in o and ">t1 · chốt<" in o and ">Atlas graph<" in o and ">overstack<" in o
    assert "<h3>Xét lại</h3>" in o and "⤢ Mở hết" in o and "> Hiện cả wiki" in o and ">herdr<" in o
    assert "<p>chữ thường giữ</p>" in o and "<code><button>x</button></code>" in o and hsf.fix_markup(o, []) == o


def test_ink_token_skips_blocks_with_fixed_solid_background():
    # viên trạng thái: nền cam cố định + chữ tối do ink_on() chọn → KHÔNG đổi sang --ovs-ink (tối sẽ ra chữ sáng trên cam, 2,26:1)
    out = hsf.fix_css('<span style="background:#f97316;color:#0f0f12">x</span><p style="color:#0f0f12">y</p>.a{background:#fff;color:#111}', [])
    assert 'background:#f97316;color:#0f0f12"' in out
    assert 'color:var(--ovs-ink,#0f0f12)' in out and 'color:var(--ovs-ink,#111)' in out
