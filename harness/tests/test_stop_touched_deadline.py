"""sig `hook-timeout|Stop:stop.py|` (3×/24h, 2026-11-17, project root = $HOME là git repo): _emit_touched chạy SAU main()
— main() đã được phép tiêu tới trần _HARD_S=27s — rồi gọi session_touched_files / session_new_html với timeout git cố định
(10+5+10s, 5+10s), không kẹp theo deadline như running_servers. `git status -uall` ở $HOME mất ~8s → hook vượt 30s, bị kill.
Repro: git giả ngủ 20s, giả lập main() đã tiêu 25s; _emit_touched phải xong trước trần _HARD_S (+1.5s biên)."""
import importlib.util, json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / "llmwiki/.claude/hooks"
sys.path.insert(0, str(HOOKS))


def _stop():
    spec = importlib.util.spec_from_file_location("stop_under_test", HOOKS / "stop.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_emit_touched_respects_hard_deadline(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / ".llmwiki" / "html").mkdir(parents=True)              # session_new_html cũng gọi git
    ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() - 60)) + ".000Z"
    tp = tmp_path / "t.jsonl"
    tp.write_text(json.dumps({"type": "user", "timestamp": ts, "message": {"content": "x"}}))

    shim = tmp_path / "bin"
    shim.mkdir()
    (shim / "git").write_text("#!/bin/sh\nsleep 20\n")             # git chậm như `git status -uall` ở $HOME lúc máy tải
    (shim / "git").chmod(0o755)
    monkeypatch.setenv("PATH", f"{shim}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(repo))
    monkeypatch.setenv("OVERSTACK_TOUCHED_SERVERS", "0")

    stop = _stop()
    stop._T0 = time.monotonic() - 25                               # main() đã tiêu 25s trong 27s trần cứng
    t = time.monotonic()
    stop._emit_touched({"transcript_path": str(tp), "session_id": "deadline-test", "cwd": str(repo)})
    dt = time.monotonic() - t
    assert dt < (stop._HARD_S - 25) + 1.5, f"_emit_touched chạy {dt:.1f}s sau main() — vượt trần hook 30s"
