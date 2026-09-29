"""test_run_validator_timeout — validator chạy quá timeout thì hooklib.run_validator KHÔNG được ném Traceback.

Chữ ký gốc: non_blocking_error|PreToolUse:Bash:pre_tool_use.py|...Traceback — patterns_guard.py quá 30s
lúc máy tải cao → subprocess.TimeoutExpired lọt khỏi run_validator, hook in Traceback ra mọi lượt Bash.
Test thu timeout xuống 0.5s bằng cách bọc subprocess.run, validator ngủ thật 5s → TimeoutExpired thật."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "llmwiki/.claude/hooks"))
import hooklib  # noqa: E402


def test_timeout_is_fail_open(tmp_path, monkeypatch):
    (tmp_path / "slow.py").write_text("import time; time.sleep(5)\n")
    real = subprocess.run
    monkeypatch.setattr(hooklib.subprocess, "run", lambda *a, **k: real(*a, **{**k, "timeout": 0.5}))
    rc, err = hooklib.run_validator("slow.py", {"action": "bash", "command": "ls"}, tmp_path)
    assert rc != 2, "timeout không được biến thành chặn"
    assert "slow.py" in err and "Traceback" not in err


def test_normal_block_still_works(tmp_path):
    (tmp_path / "deny.py").write_text("import sys; print('[R0 x] chặn', file=sys.stderr); sys.exit(2)\n")
    assert hooklib.run_validator("deny.py", {"action": "bash", "command": "ls"}, tmp_path) == (2, "[R0 x] chặn")
