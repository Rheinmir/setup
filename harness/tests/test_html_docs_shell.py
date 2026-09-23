"""test_html_docs_shell — R20 (c): trang tài liệu thiếu bộ khung MUST bị chặn; sau `html_font.py --apply` thì qua (PLAN 220926)."""
import importlib.util, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V = ROOT / "harness/validators/html_docs_shell.py"


def _load(p, name):
    s = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


val, survey = _load(V, "r20"), _load(ROOT / "fdk/tools/docs-shell-survey.py", "survey")
PAGE = ("<!doctype html><html><head><title>t</title><style>body{margin:0}</style></head><body>"
        '<nav><div class="logo">Tài liệu</div><a href="#a">01 · Vấn đề</a><a href="#b">02 · Luồng</a>'
        '<a href="#c">03 · Kiểm</a><a href="#d">04 · Bài học</a><button class="nav-toggle">≡</button></nav>'
        '<section id="a"><h1>Trang</h1></section><section id="b"><h2>Một</h2></section>'
        '<section id="c"><h2>Hai</h2></section><section id="d"><h2>Ba</h2></section></body></html>')


def _r20(path):
    return subprocess.run([sys.executable, str(V)], input=json.dumps({"action": "write", "file_path": str(path)}),
                          capture_output=True, text=True)


def test_fire_drill_bad_page_blocked_then_apply_makes_it_pass(tmp_path):
    d = tmp_path / "llmwiki" / "html"; d.mkdir(parents=True); f = d / "p.html"
    f.write_text(PAGE, encoding="utf-8")
    bad = _r20(f)
    assert bad.returncode == 2 and "bộ khung MUST" in bad.stderr and "--apply" in bad.stderr
    subprocess.run([sys.executable, str(ROOT / "fdk/tools/html_font.py"), "--apply", str(f)], check=True, capture_output=True)
    good = _r20(f)
    assert good.returncode == 0, good.stderr


def test_manual_gap_is_not_promised_to_apply():
    msg = val.shell_problem("x.html", PAGE.replace('<button class="nav-toggle">≡</button>', ""))
    assert "nav-toggle phải dựng tay" in msg


def test_validator_and_survey_checks_do_not_drift():
    assert set(val.SHELL_CHECKS) == set(survey.CHECKS)
    samples = [PAGE, PAGE.replace("nav-toggle", "x"), PAGE + '<div class="diagram-box"></div>',
               PAGE + '<link rel="icon" href="data:x"><main id="main"></main><div class="mm"></div> IntersectionObserver ripple skip-link']
    for h in samples:
        assert [k for k, ok in val.SHELL_CHECKS.items() if not ok(h)] == survey.gaps(h)


def test_R3_body_child_css_page_gets_honest_manual_message():
    p = PAGE.replace("body{margin:0}", "body{margin:0}body>section{padding:1px}")
    msg = val.shell_problem("x.html", p)
    assert "main-id + skip-link phải dựng tay" in msg
    assert "tự chèn" not in msg.split("—")[0] or "main-id" not in msg.split("tự chèn")[1].split("—")[0]
