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
    assert msg.count("file://") == 10 and "+10 trang nữa" in msg
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


def test_running_servers_lists_project_listeners_with_clickable_url(tmp_path):
    """Feedback 200926: Stop kèm link server ĐANG CHẠY. Server có cwd TRONG dự án → có link; ngoài dự án → không."""
    import shutil, socket
    if not shutil.which("lsof"):
        import pytest; pytest.skip("không có lsof")
    def free_port():
        s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p
    root = tmp_path / "proj"; (root / "site").mkdir(parents=True); outside = tmp_path / "other"; outside.mkdir()
    pin, pout = free_port(), free_port()
    procs = [subprocess.Popen([sys.executable, "-m", "http.server", str(pin), "--bind", "127.0.0.1"], cwd=root / "site", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL),
             subprocess.Popen([sys.executable, "-m", "http.server", str(pout), "--bind", "127.0.0.1"], cwd=outside, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)]
    try:
        for _ in range(50):
            urls = [s["url"] for s in hooklib.running_servers(str(root))]
            if f"http://localhost:{pin}/" in urls:
                break
            time.sleep(0.1)
        assert f"http://localhost:{pin}/" in urls and f"http://localhost:{pout}/" not in urls, urls
        srv = next(s for s in hooklib.running_servers(str(root)) if s["url"].endswith(f":{pin}/"))
        assert "http.server" in srv["what"] and "site" in srv["what"]                  # ghi rõ nó LÀ GÌ, chạy ở đâu
    finally:
        for q in procs:
            q.terminate()


def test_servers_message_shows_public_link_next_to_localhost():
    msg = hooklib.servers_message([{"url": "http://localhost:3000/", "what": "node server.js · chạy ở web/", "public": ["https://app.example.vn"]}])
    assert "http://localhost:3000/  ⇄  https://app.example.vn" in msg and "node server.js" in msg
    assert hooklib.servers_message([]) == ""


def test_stop_collapses_r21_to_graph_only_and_dedupes_double_hook(tmp_path, monkeypatch):
    """Feedback 280926 "tui cần cái graph phân việc thôi" + "phiên không có graph thì không show": dòng gọn CHỈ còn link
    orca-graph [graph] + link "chi tiết" (bản đủ); không graph → không in. Hook dự án + global cùng chạy thì lần 2 im."""
    import importlib.util, tempfile
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))
    spec = importlib.util.spec_from_file_location("stop_mod", ROOT / "llmwiki/.claude/hooks/stop.py")
    st = importlib.util.module_from_spec(spec); spec.loader.exec_module(st)
    full = ("📖 [R21] 3 trang để ĐỌC (x):\n  • [HTML] Báo cáo\n      file:///r/a.html\n  • [graph] Graph phân việc · g1\n      file:///r/graph/g1.graph.html\n"
            "  • [PLAN] Kế hoạch\n      file:///r/g1-PLAN.md\n🗂 10 file khác (x):\n  · code: 1 — x.py\n🌐 [R21] 1 server đang chạy (bấm mở):\n  • https://uiux.giatbh.io.vn\n      link thật")
    line = st._collapse(full, "s1")
    assert "\n" not in line
    assert "\x1b]8;;file:///r/graph/g1.graph.html\x1b\\Graph phân việc · g1\x1b]8;;\x1b\\" in line     # OSC 8: chữ hiện, URL ẩn
    for gone in ("a.html", "g1-PLAN.md", "uiux.giatbh.io.vn", "file khác"):
        assert gone not in line, gone
    detail = line.rsplit("\x1b]8;;file://", 1)[1].split("\x1b")[0]
    assert open(detail, encoding="utf-8").read().strip() == full                    # bản đủ vẫn còn sau "chi tiết"
    assert st._collapse(full, "s1") is None                                          # hook thứ hai, cùng nội dung → không in lại
    assert st._collapse(full.replace("[graph]", "[HTML]"), "s2") is None            # phiên không có graph → không in
    monkeypatch.setenv("OVERSTACK_TOUCHED_FULL", "1")
    assert st._collapse(full + "\n  • b", "s1").startswith("📖 [R21] 3 trang để ĐỌC")
    monkeypatch.setenv("OVERSTACK_TOUCHED_FULL", "0"); monkeypatch.setenv("OVERSTACK_TOUCHED_OSC8", "0")
    raw = st._collapse(full + "\n  • c", "s1")
    assert "\x1b" not in raw and "Graph phân việc · g1 <file:///r/graph/g1.graph.html>" in raw


def test_graph_is_the_one_this_session_worked_on_not_by_mtime(tmp_path, monkeypatch):
    """Feedback 280926: 'graph' = trang orca-graph `<id>.graph.html` mà phiên này GỌI TỚI (id nằm trong input tool_use);
    PLAN/graph cũ bị ghi lại (mtime mới) không được lọt ('graph này cũ rồi mà'); wiki-graph.html không phải trang để đọc."""
    ov = tmp_path / "llmwiki"; (ov / "graph").mkdir(parents=True); (ov / "html").mkdir()
    for g in ("200926-old", "280926-mine"):
        (ov / "graph" / f"{g}.graph.html").write_text(f"<title>Graph phân việc · {g}</title>")
    (ov / "html/wiki-graph.html").write_text("<title>wg</title>")
    monkeypatch.setattr(hooklib, "overstack_dir", lambda r: ov)
    t = tmp_path / "t.jsonl"
    t.write_text("\n".join(json.dumps(r) for r in [
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash",
                                                       "input": {"command": "orca-graph build llmwiki/wiki/sources/draft/280926-mine-PLAN.md"}}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "content": "200926-old.graph.html"}]}}]))   # chỉ ở OUTPUT → không tính
    got = [Path(p).name for p in hooklib.session_graphs(str(tmp_path), str(t))]
    assert got == ["280926-mine.graph.html"], got
    old_plan = ov / "wiki/sources/draft/200926-old-PLAN.md"; old_plan.parent.mkdir(parents=True); old_plan.write_text("# p")
    msg = hooklib.touched_message([str(ov / "html/wiki-graph.html"), str(old_plan), str(ov / "graph/200926-old.graph.html")])
    assert "[graph]" not in msg and "file://" + str(ov / "html/wiki-graph.html") not in msg
    assert "trang tự sinh lại: 1 — wiki-graph.html" in msg


def test_new_html_only_created_not_edited_and_joins_stop_line(tmp_path, monkeypatch):
    """Feedback 280926: dòng Stop thứ hai = HTML TẠO MỚI trong phiên ở <overstack>/html (sửa file cũ không tính; wiki-graph.html loại)."""
    root = _repo(tmp_path / "repo")
    html = root / "llmwiki/html"; html.mkdir(parents=True)
    (html / "old.html").write_text("<title>Cũ</title>")                     # sinh TRƯỚC phiên
    time.sleep(1.1)
    t = _transcript(tmp_path, root / "x")                                     # mốc phiên = now-60s → lùi old.html ra trước bằng birthtime thật
    monkeypatch.setattr(hooklib, "overstack_dir", lambda r: html.parent)
    start = time.time() - 0.5
    ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(start)) + ".%03dZ" % int((start % 1) * 1000)
    t.write_text(t.read_text().replace(json.loads(t.read_text().splitlines()[0])["timestamp"], ts))
    time.sleep(0.6)
    (html / "old.html").write_text("<title>Cũ sửa</title>")                 # SỬA trong phiên → không tính
    (html / "new.html").write_text("<title>Trang mới</title>")               # TẠO trong phiên → tính
    (html / "wiki-graph.html").write_text("<title>wg</title>")               # tự sinh → loại
    got = [Path(p).name for p in hooklib.session_new_html(str(root), str(t))]
    assert got == ["new.html"], got
    import importlib.util, tempfile
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))
    spec = importlib.util.spec_from_file_location("stop_mod2", ROOT / "llmwiki/.claude/hooks/stop.py")
    st = importlib.util.module_from_spec(spec); spec.loader.exec_module(st)
    msg = "  • [graph] G\n      file:///r/g.graph.html\n" + hooklib.new_html_message(hooklib.session_new_html(str(root), str(t)))
    line = st._collapse(msg, "s9")
    assert line.index("g.graph.html") < line.index("new.html") and "🆕" in line
