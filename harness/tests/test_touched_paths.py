"""test_touched_paths (R21, mechanism touched-paths) — Stop hook in cho user path tuyệt đối file phiên này tạo/sửa:
lấy từ Write/Edit trong transcript + git status mtime >= mốc đầu phiên; trần 40 link; bỏ file cũ/noise."""
import json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "llmwiki/.claude/hooks"))
import hooklib  # noqa: E402


def _repo(tmp):
    tmp.mkdir()
    subprocess.run(["git", "init", "-q", str(tmp)], check=True)
    (tmp / "old.txt").write_text("x")
    os.utime(tmp / "old.txt", (time.time() - 3600,) * 2)       # sửa TRƯỚC phiên → không liệt kê
    return tmp


def _transcript(tmp, written):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() - 60)) + ".000Z"
    recs = [{"type": "user", "timestamp": ts, "message": {"content": "x"}},
            {"type": "assistant", "timestamp": ts, "message": {"content": [
                {"type": "tool_use", "name": "Write", "input": {"file_path": str(written)}}]}}]
    t = tmp / "t.jsonl"
    t.write_text("\n".join(json.dumps(r) for r in recs))
    return t


def test_lists_session_files_only(tmp_path):
    repo = _repo(tmp_path / "repo")
    (repo / "new.py").write_text("x")                           # sửa qua Bash → bắt bằng git mtime
    w = repo / "wrote.md"; w.write_text("x")                    # sửa qua Write → bắt bằng transcript
    (repo / "harness/metrics").mkdir(parents=True); (repo / "harness/metrics/m.json").write_text("{}")
    files = hooklib.session_touched_files(str(repo), str(_transcript(tmp_path, w)))
    names = {Path(f).name for f in files}
    assert names == {"new.py", "wrote.md"}, names
    assert all(os.path.isabs(f) for f in files)


def test_cap_40():
    files = [f"/x/f{i}" for i in range(45)]
    msg = hooklib.touched_message(files)
    assert msg.count("file://") == 40 and "+5 file nữa" in msg
    assert hooklib.touched_message([]) == ""
