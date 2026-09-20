"""test_touched_paths (R21, mechanism touched-paths) — Stop hook in cho user path tuyệt đối file phiên này tạo/sửa:
lấy từ Write/Edit trong transcript + git status mtime >= mốc đầu phiên; trang người-đọc trong wiki có tiêu đề + link (trần 15), file khác gom nhóm; bỏ file cũ/noise."""
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


def test_reader_pages_get_title_and_link_everything_else_is_grouped(tmp_path):
    """Feedback 200926: link CHỈ cho trang người-đọc trong wiki, mỗi dòng ghi nó LÀ GÌ; file khác gom nhóm, không rải path."""
    def mk(rel, body="x"):
        p = tmp_path / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(body, encoding="utf-8"); return str(p)
    page = mk("llmwiki/wiki/sources/a.md", '---\ntype: source\ntitle: "Trang A nói về X"\n---\n# khác\n')
    html = mk("llmwiki/html/r.html", "<html><head><title>Báo cáo R</title></head></html>")
    nohd = mk("fdk/wiki/concepts/c.md", "không có tiêu đề")
    others = [mk("llmwiki/wiki/index.md"), mk("llmwiki/wiki/sources/provenance/p.md"), mk("llmwiki/raw/big.md", "# RAW"),
              mk("llmwiki/graph/atlas.html"), mk("harness/scripts/e.py"), mk("harness/tests/test_e.py"), mk(".github/workflows/ci.yml"), mk("README.md")]
    msg = hooklib.touched_message([html, page, nohd] + others)
    assert msg.count("file://") == 3                                           # chỉ 3 trang người-đọc có link
    assert "Trang A nói về X" in msg and "Báo cáo R" in msg and "c.md" in msg    # tiêu đề thật; không có thì lùi về tên file
    for o in others:
        assert f"file://{o}" not in msg
    assert "8 file khác" in msg
    for label in ("test: 1", "code / script: 1", "CI / cấu hình: 1", "nguồn thô raw/: 1", "dữ liệu graph / sổ máy: 3", "tài liệu ngoài wiki: 1"):
        assert label in msg, (label, msg)


def test_cap_applies_to_reader_pages(tmp_path):
    pages = []
    for i in range(20):
        p = tmp_path / f"llmwiki/wiki/sources/s{i}.md"; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(f"# S{i}\n"); pages.append(str(p))
    msg = hooklib.touched_message(pages)
    assert msg.count("file://") == 15 and "+5 trang nữa" in msg
    assert hooklib.touched_message([]) == ""


def test_order_html_graph_plan_rest(tmp_path):
    import hooklib as hl
    fs = {}
    for rel in ("fdk/tools/x.py", "llmwiki/wiki/sources/draft/190926-a-PLAN.md", "llmwiki/graph/g.graph.html",
                "llmwiki/html/report.html"):
        p = tmp_path / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text("x"); fs[rel] = str(p)
    order = sorted(fs.values(), key=lambda p: (hl._touched_rank(p), 0))
    assert [Path(p).name for p in order] == ["report.html", "g.graph.html", "190926-a-PLAN.md", "x.py"]


def test_committed_in_session_still_listed(tmp_path):
    repo = _repo(tmp_path / "repo")
    (repo / "done.py").write_text("x")
    subprocess.run(["git", "-C", str(repo), "add", "done.py"], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "c"], check=True)
    files = hooklib.session_touched_files(str(repo), str(_transcript(tmp_path, tmp_path / "khac.md")))  # done.py KHÔNG có trong transcript
    assert "done.py" in {Path(f).name for f in files}
