"""test_goal_hook — từ khoá `goal` (nguyên từ, ngoài khối code) → hook inject chỉ thị kèm /orca-graph;
không khớp 'goals'/'goalkeeper'/'my-goal-x'; tắt được bằng OVERSTACK_GOAL_HOOK=0; hook chạy thật ra JSON hợp lệ."""
import importlib.util, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / "llmwiki/.claude/hooks"
sys.path.insert(0, str(HOOKS))
_spec = importlib.util.spec_from_file_location("ups", HOOKS / "user_prompt_submit.py")
ups = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(ups)


def test_keyword_matches():
    for p in ("goal: ship SWH", "Goal tuần này", "đặt /goal cho sprint", "mục tiêu (goal) là X"):
        assert ups.goal_directive(p) and "orca-graph" in ups.goal_directive(p), p


def test_non_keyword_ignored():
    for p in ("goals list", "goalkeeper", "my-goal-x", "không có gì", "```\ngoal = 1\n```"):
        assert ups.goal_directive(p) is None, p


def test_atlas_link_and_disable(monkeypatch):
    assert "file:///x/atlas.html" in ups.goal_directive("goal", "/x/atlas.html")
    monkeypatch.setenv("OVERSTACK_GOAL_HOOK", "0")
    assert ups.goal_directive("goal") is None


def test_hook_end_to_end():
    payload = {"session_id": "t-goal", "prompt": "goal: chuẩn hoá skill", "cwd": str(ROOT), "transcript_path": ""}
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(ROOT), "OVERSTACK_SELF_REPORT_EVERY": "0",
           "LLMWIKI_DOCS_GATE_EVERY": "0"}
    p = subprocess.run([sys.executable, str(HOOKS / "user_prompt_submit.py")], input=json.dumps(payload),
                       capture_output=True, text=True, env=env, cwd=str(ROOT), timeout=160)
    ctx = [json.loads(l)["hookSpecificOutput"]["additionalContext"] for l in p.stdout.splitlines() if l.startswith("{")]
    assert any("[goal→orca-graph]" in c for c in ctx), p.stdout + p.stderr


def test_two_messages_still_one_json(monkeypatch, capsys):
    """Audit 280926 F3: orca-graph đang chạy + goal cùng lượt → trước đây hook print 2 object JSON
    nối liền → Claude Code báo 'not valid JSON' và VỨT CẢ HAI context. stdout phải là ĐÚNG MỘT JSON."""
    monkeypatch.setenv("OVERSTACK_SELF_REPORT_EVERY", "0")
    monkeypatch.setenv("LLMWIKI_DOCS_GATE_EVERY", "0")
    monkeypatch.setattr(ups, "read_payload", lambda: {"session_id": "t-two", "prompt": "goal: x",
                                                      "cwd": str(ROOT), "transcript_path": ""})
    monkeypatch.setattr(ups, "orca_graph_running", lambda root: (["p/t1", "p/t2"], "/x/graph.html"))
    monkeypatch.setattr(ups, "resolve_tool", lambda root, rel: None)   # không gọi session-continue/self-report
    try:
        ups.main()
    except SystemExit:
        pass
    out = capsys.readouterr().out
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]      # 2 object nối liền → JSONDecodeError
    assert "[orca-graph]" in ctx and "[goal→orca-graph]" in ctx, out
