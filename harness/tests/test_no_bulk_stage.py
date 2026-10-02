"""test_no_bulk_stage — P1 (issue 030726-multi-session-add-guard): 2 phiên chung cây, phiên A không được commit file phiên B."""
import json
import subprocess
import sys
from pathlib import Path

V = Path(__file__).resolve().parents[2] / "harness-local/validators/no_bulk_stage.py"


def run(ev):
    r = subprocess.run([sys.executable, str(V)], input=json.dumps(ev), capture_output=True, text=True)
    return r.returncode, r.stderr


def repo(tmp: Path):
    subprocess.run(["git", "init", "-q", str(tmp)], check=True)
    (tmp / "harness/metrics").mkdir(parents=True)
    (tmp / "mine.py").write_text("a\n"); (tmp / "theirs.py").write_text("b\n")
    evs = [{"event": "file.write", "path": "mine.py", "session": "aaaaaaaa"},
           {"event": "file.write", "path": "theirs.py", "session": "bbbbbbbb"}]
    (tmp / "harness/metrics/events.jsonl").write_text("\n".join(map(json.dumps, evs)) + "\n")
    return tmp


def ev(cmd, root, session="aaaaaaaa-1111"):
    return {"action": "bash", "command": cmd, "session": session, "root": str(root)}


def test_bulk_stage_blocked_explicit_pathspec_passes(tmp_path):
    for cmd in ["git add -A", "git add . && git commit --no-verify -m x", "git add --all", "git commit --no-verify -am x"]:
        assert run({"action": "bash", "command": cmd})[0] == 2, cmd
    for cmd in ["git add src/a.py", "git commit --no-verify -m 'add a feature'", "git commit --no-verify --amend --no-edit", "git status"]:
        assert run({"action": "bash", "command": cmd})[0] == 0, cmd


def test_commit_of_other_session_file_is_blocked(tmp_path):
    r = repo(tmp_path)
    assert run(ev("git add mine.py && git commit --no-verify -m x", r))[0] == 0
    rc, err = run(ev("git add mine.py theirs.py && git commit --no-verify -m x", r))
    assert rc == 2 and "theirs.py (phiên bbbbbbbb)" in err
    subprocess.run(["git", "-C", str(r), "add", "theirs.py"], check=True)       # đã stage sẵn từ trước
    rc, err = run(ev("git commit --no-verify -m x", r))
    assert rc == 2 and "theirs.py" in err
    assert run(ev("OVS_ALLOW_CROSS_SESSION=1 git commit --no-verify -m x", r))[0] == 0      # cố ý commit hộ
    assert run(ev("git commit --no-verify -m x", r, session="bbbbbbbb-2222"))[0] == 0        # chính phiên B commit


def test_other_worktree_is_not_the_shared_tree(tmp_path):
    r = repo(tmp_path / "main"); other = tmp_path / "wt"; other.mkdir()
    subprocess.run(["git", "-C", str(r), "add", "theirs.py"], check=True)
    assert run(ev(f"cd {other} && git commit --no-verify -m x", r))[0] == 0
    assert run(ev(f"git -C {other} commit -m x", r))[0] == 0
    assert run(ev(f"cd {r} && git commit --no-verify -m x", r))[0] == 2
