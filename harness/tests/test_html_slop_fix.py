"""test_html_slop_fix — html-slop-fix.py vá được năm lớp slop MÁY-LÀM-ĐƯỢC trên trang đã có sẵn,
không đụng JS/srcdoc/văn xuôi, và chạy hai lần ra cùng một kết quả (idempotent)."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(name, fname):
    s = importlib.util.spec_from_file_location(name, ROOT / f"fdk/tools/{fname}")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


hsf = _load("html_slop_fix", "html-slop-fix.py")

SLOPPY = """
.hero h1 { background: linear-gradient(90deg, #0a84ff, #5856d6); -webkit-background-clip: text;
           background-clip: text; -webkit-text-fill-color: transparent; }
.card { border-left: 4px solid #0a84ff; padding: 1rem; }
.note::before { content: ""; position: absolute; top: 0; bottom: 0; width: 4px; background: #e11d48; }
.panel { background: rgba(255, 255, 255, 0.72); backdrop-filter: blur(12px); }
a.link { color: #0a84ff; }
small { font-size: .75rem; opacity: .6; }
"""


def test_five_machine_fixable_slop_classes_are_rewritten():
    log = []
    out = hsf.fix_css(SLOPPY, log)
    assert "background-clip" not in out and "text-fill-color" not in out
    assert "var(--ovs-accent" in out                      # gradient-text → chữ màu đặc
    assert "border-left: 4px solid #0a84ff" not in out    # sọc một cạnh màu → bỏ
    assert ".note::before" not in out                     # luật ::before vẽ sọc → bỏ cả luật
    assert "rgba(var(--ovs-glass-rgb,255,255,255)," in out  # kính trắng → token (tối vẫn còn kính)
    assert "color:var(--ovs-accent" in out.replace(" ", "")  # chữ nhấn → token
    assert "opacity: .6" not in out                       # small hạ opacity → bỏ
    assert log, "phải ghi lại từng phép vá để người đọc kiểm được"


def test_running_twice_changes_nothing_more():
    once = hsf.fix_css(SLOPPY, [])
    assert hsf.fix_css(once, []) == once


def test_neutral_border_and_saturated_table_rule_are_left_alone():
    css = ".row { border-left: 4px solid #e2e8f0; }\ntd { border-left: 4px solid #0a84ff; }"
    out = hsf.fix_css(css, [])
    assert "#e2e8f0" in out, "viền trung tính không phải sọc trang trí — giữ"
    assert "td { border-left: 4px solid #0a84ff; }" in out, "viền ô bảng là cấu trúc — giữ"


def test_javascript_and_srcdoc_are_not_touched():
    html = ('<html><head><style>.a{color:#0a84ff}</style></head><body>'
            '<iframe srcdoc="&lt;style&gt;.b{color:#0a84ff}&lt;/style&gt;"></iframe>'
            '<script>var c = "color:#0a84ff";</script></body></html>')
    out = hsf.fix_markup(html, [])
    assert 'var c = "color:#0a84ff"' in out
    assert "srcdoc=" in out and out.count("#0a84ff") >= 2
