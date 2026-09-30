"""test_unknown_ledger_args — thiếu --file/--id thì unknown-ledger báo lỗi usage, KHÔNG ném Traceback.

Chữ ký gốc: tool-error|Bash|... unknown-ledger.py line 87, in add: path = DIR / args.file
TypeError: unsupported operand type(s) for /: 'PosixPath' and 'NoneType' (gọi --add không kèm --file)."""
import subprocess, sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "harness/scripts/unknown-ledger.py"


@pytest.mark.parametrize("argv", [["--add", "--q", "x"], ["--resolve", "--id", "U-01"],
                                  ["--trace", "--id", "U-01"], ["--resolve", "--file", "a.md"]])
def test_missing_required_is_usage_error(argv, tmp_path):
    p = subprocess.run([sys.executable, str(SCRIPT), *argv], capture_output=True, text=True, cwd=tmp_path)
    assert "Traceback" not in p.stderr, p.stderr
    assert p.returncode == 2 and "--" in p.stderr
