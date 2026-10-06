"""Stop hook: HTML do CHÍNH hook sinh lại cuối lượt phải hiện ở dòng R21 (user 06/10/2026: giảm HTML sinh ra mà không ai biết)."""
import importlib.util
import os
import sys
import time
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[2] / "llmwiki/.claude/hooks"
sys.path.insert(0, str(HOOKS))
s = importlib.util.spec_from_file_location("stop_hook", HOOKS / "stop.py"); stop = importlib.util.module_from_spec(s); s.loader.exec_module(stop)


def test_regenerated_pages_are_reported(tmp_path):
    html = tmp_path / "llmwiki" / "html"; html.mkdir(parents=True)
    (tmp_path / "llmwiki" / ".harness-stamp").write_text("x")
    a, b = html / "wiki-graph.html", html / "mine.html"
    a.write_text("1"); b.write_text("1")
    before = stop._html_mtimes(str(tmp_path))
    assert str(a) in before and str(b) in before
    time.sleep(0.01); a.write_text("2"); os.utime(a, (time.time() + 5, time.time() + 5))   # hook ghi lại wiki-graph
    changed = sorted(f for f, t in stop._html_mtimes(str(tmp_path)).items() if before.get(f) != t)
    assert changed == [str(a)]
    msg = stop.regen_message(changed)
    assert "TỰ SINH LẠI 1 HTML" in msg and "wiki-graph.html" in msg and "mine.html" not in msg
    assert stop.regen_message([]) == ""
