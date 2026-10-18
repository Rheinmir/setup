"""R23 qua ĐƯỜNG HOOK THẬT: pre_tool_use.py nhận payload Read/Bash → chặn trang máy sinh, cho qua nguồn + lượt audit slash."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "llmwiki/.claude/hooks/pre_tool_use.py"


def run(payload):
    env = {k: v for k, v in os.environ.items() if k != "OVERSTACK_READ_HTML"}
    env["CLAUDE_PROJECT_DIR"] = str(ROOT)
    r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True, text=True, env=env, timeout=30)
    return r.returncode, r.stderr


def page(tmp):
    p = tmp / "p-seq.html"
    p.write_text("<html><body><p>x</p><footer><p>Sinh từ <code>/x/p.md</code> bởi <code>md-render.py</code></p></footer></body></html>")
    return p


def test_read_generated_page_blocked_with_source_hint(tmp_path):
    rc, err = run({"tool_name": "Read", "tool_input": {"file_path": str(page(tmp_path))}, "cwd": str(ROOT)})
    assert rc == 2 and "R23" in err and "/x/p.md" in err


def test_non_html_and_handwritten_html_pass(tmp_path):
    (tmp_path / "a.md").write_text("# x")
    (tmp_path / "landing.html").write_text("<html><body>viết tay</body></html>")
    assert run({"tool_name": "Read", "tool_input": {"file_path": str(tmp_path / "a.md")}, "cwd": str(ROOT)})[0] == 0
    assert run({"tool_name": "Read", "tool_input": {"file_path": str(tmp_path / "landing.html")}, "cwd": str(ROOT)})[0] == 0


def test_bash_dump_blocked_grep_allowed(tmp_path):
    p = page(tmp_path)
    assert run({"tool_name": "Bash", "tool_input": {"command": f"cat {p}"}, "cwd": str(ROOT)})[0] == 2
    assert run({"tool_name": "Bash", "tool_input": {"command": f"grep -c desc {p}"}, "cwd": str(ROOT)})[0] == 0


def test_audit_slash_turn_may_read(tmp_path):
    tr = tmp_path / "t.jsonl"
    tr.write_text(json.dumps({"type": "user", "message": {"content": "<command-name>/qc-uiux</command-name>"}}) + "\n")
    payload = {"tool_name": "Read", "tool_input": {"file_path": str(page(tmp_path))}, "cwd": str(ROOT), "transcript_path": str(tr)}
    assert run(payload)[0] == 0
