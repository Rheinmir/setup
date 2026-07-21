#!/usr/bin/env python3
"""decision-liveness — suy LIVE/STALE/ORPHAN/UNAVAILABLE cho anchor_symbol trong mechanisms.yaml.

Đọc TRỰC TIẾP .graph-agent/index.db (sqlite) — script chạy ngoài context Claude nên KHÔNG
gọi được MCP search_symbols/get_symbol_context (chỉ Claude-agent gọi được). Thay vào đó áp
đúng nguyên tắc dep-health.py ở tầng khác: quảng cáo một năng lực = phải THĂM DÒ, không phải
kiểm tồn tại — ở đây thăm dò là kiểm schema (db_has_schema, tái dùng dep-health.py) + kiểm
checksum file trên đĩa khớp cột `checksum` trong bảng `files` (proxy cho "project đã reindex",
vì không có cách nào khác đọc trạng thái reindex mà không qua MCP).

CLI:
    decision-liveness.py check [--json]      # mọi mục có anchor_symbol/live_probe -> trạng thái
    decision-liveness.py why <symbol>        # tra ngược symbol -> quyết định (mechanisms.yaml)
    decision-liveness.py --self-test

AGENT ĐANG ĐỌC FILE NÀY (before you run `why`/`check`): nếu kết quả là UNAVAILABLE vì "chưa
được index" hoặc "index.db absent/degraded", ĐỪNG báo đó là kết luận cuối ngay — trước tiên
hãy tự gọi `reindex_repo(<ROOT in bao ra>)` qua code-graph MCP (bạn CÓ quyền gọi, script này
thì không) rồi chạy lại lệnh. 5-Why 2026-07-21: bỏ qua bước này khiến `why` trả lời sai-cảm-giác
ở lượt đầu (trông như cơ chế neo hỏng, trong khi chỉ cần reindex) — đúng nguyên nhân đã giết
`touches` trong repo này ("thứ không ai tiêu thụ thì không ai nuôi"). Chỉ báo UNAVAILABLE là
kết luận cuối SAU KHI đã thử reindex mà vẫn vậy (tầng 1 git hoặc tầng 2 DB thật sự hỏng).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MECH_PATH = ROOT / "harness/mechanisms.yaml"
DB_PATH = ROOT / ".graph-agent/index.db"

LIVE, STALE, ORPHAN, UNAVAILABLE = "LIVE", "STALE", "ORPHAN", "UNAVAILABLE"


def _load_dep_health():
    spec = importlib.util.spec_from_file_location(
        "dep_health", ROOT / "harness/scripts/dep-health.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_dh = _load_dep_health()


def parse_mechanisms(text: str) -> list:
    """Regex parse, cùng khuôn medic.py p_narrative() — không thêm dep pyyaml. Mỗi block bắt
    đầu bằng '- id:' (khớp indent 2 dấu cách của mechanisms.yaml thật)."""
    blocks = re.split(r'(?=^\s*-\s*id:\s*)', text, flags=re.M)
    entries = []
    for b in blocks:
        m_id = re.search(r'^\s*-\s*id:\s*(\S+)', b, re.M)
        if not m_id:
            continue

        def field(key, block=b):
            m = re.search(rf'^\s*{key}:\s*"?(.+?)"?\s*$', block, re.M)
            return m.group(1).strip() if m else None

        entries.append({
            "id": m_id.group(1),
            "name": field("name"),
            "desc": field("desc"),
            "live_probe": field("live_probe"),
            "anchor_symbol": field("anchor_symbol"),
            "confirmed": field("confirmed"),
            "status": field("status") or "active",
        })
    return entries


def parse_anchor(anchor_symbol: str):
    """<project>::<file>::<qualified-name> -> (project, file, name) hoặc None nếu sai định dạng."""
    parts = anchor_symbol.split("::")
    return tuple(parts) if len(parts) == 3 else None


def db_status(db_path: Path) -> str:
    """'ok'|'degraded'|'absent' — CHỈ kiểm schema (đọc trực tiếp DB, không cần server process
    sống — khác dep-health.probe_code_graph() vốn kiểm SERVER health cho tool-call qua MCP)."""
    if not db_path.is_file():
        return "absent"
    return "ok" if _dh.db_has_schema(db_path) else "degraded"


def resolve_symbol(anchor_symbol: str, root: Path, db_path: Path):
    """Trả (UNAVAILABLE, reason) | (ORPHAN, reason) | ("RESOLVED", (line_start, line_end))."""
    if not shutil.which("git"):
        return UNAVAILABLE, "git không có trên PATH (tầng 1 dependency chain đứt)"
    status = db_status(db_path)
    if status != "ok":
        # 5-Why 2026-07-21: DB vắng hoàn toàn ở ROOT này thường KHÔNG phải "chưa reindex" —
        # đó là khi DB có schema nhưng thiếu file/symbol (xem nhánh dưới). DB vắng hẳn ở một
        # ROOT tự suy (Path(__file__).parents[2]) thường là dấu hiệu đang chạy bản mirror
        # global_shared (nhân bản cố ý, xem harness/mechanisms.yaml comment đầu file) chứ
        # không phải repo dev thật — hint luôn để không phải mò.
        return UNAVAILABLE, (f"index.db {status} tại ROOT={root} (tầng 2 đứt) — nếu đây là "
                              f"bản global_shared (~/.claude/harness), thử chạy từ repo dev thật "
                              f"để có index đầy đủ, hoặc reindex_repo(root) qua code-graph MCP")
    parsed = parse_anchor(anchor_symbol)
    if not parsed:
        return UNAVAILABLE, f"anchor_symbol sai định dạng: {anchor_symbol!r}"
    _project, file_rel, name = parsed
    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute("SELECT id, checksum FROM files WHERE path = ?", (file_rel,)).fetchone()
        if not row:
            # 5-Why 2026-07-21: "chưa index" gộp chung 2 ca rất khác nhau — (a) project THẬT
            # chưa chạy reindex (tạm, tự khỏi), (b) đang chạy NHẦM ROOT — bản global_shared bị
            # nhân bản (ROOT tự suy theo Path(__file__).parents[2]) không đồng bộ file mà chính
            # mechanisms.yaml của nó tham chiếu chéo sang tầng khác (llmwiki/). Case (b) là lỗi
            # CẤU TRÚC cần sửa ROOT, không phải chờ tự khỏi — tách message để không lẫn hai ca.
            if not (root / file_rel).is_file():
                return UNAVAILABLE, (f"{file_rel} không tồn tại ở ROOT={root} — có thể đang chạy "
                                      f"NHẦM BẢN (global_shared mirror thiếu file tham chiếu chéo "
                                      f"tầng); thử chạy script từ repo dev thật thay vì bản global")
            return UNAVAILABLE, f"{file_rel} chưa được index (tầng 3 đứt — project chưa reindex)"
        file_id, checksum = row
        disk = root / file_rel
        if not disk.is_file():
            return ORPHAN, f"{file_rel} đã bị xoá khỏi đĩa — symbol {name!r} không còn"
        real = hashlib.sha256(disk.read_bytes()).hexdigest()[:16]
        if checksum and real != checksum:
            return UNAVAILABLE, (f"{file_rel} đổi trên đĩa nhưng index chưa bắt kịp "
                                  f"(checksum lệch) — cần reindex trước khi tin liveness")
        sym = conn.execute(
            "SELECT line_start, line_end FROM symbols WHERE file_id = ? AND name = ?",
            (file_id, name)).fetchone()
    finally:
        conn.close()
    if not sym:
        return ORPHAN, f"symbol {name!r} không resolve được trong {file_rel} (đổi tên hoặc xoá)"
    return "RESOLVED", sym


def _commit_before_or_on(date_str: str, root: Path):
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "log", "-1", f"--until={date_str} 23:59:59", "--format=%H"],
            capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None
    except Exception:
        return None


def _touched_since(commit: str, file_rel: str, line_start: int, line_end: int, root: Path) -> bool:
    """True nếu diff commit->HEAD có hunk chạm [line_start, line_end] (số dòng phía NEW)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "diff", "--unified=0", commit, "HEAD", "--", file_rel],
            capture_output=True, text=True, timeout=15)
    except Exception:
        return True  # không đọc được diff -> báo STALE (an toàn hơn im lặng LIVE)
    for m in re.finditer(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', out.stdout, re.M):
        new_start = int(m.group(1))
        new_len = int(m.group(2) or "1")
        new_end = new_start + max(new_len - 1, 0)
        if new_start <= line_end and new_end >= line_start:
            return True
    return False


def compute_state(entry: dict, root: Path, db_path: Path) -> dict:
    result = {"path_state": None, "symbol_state": None, "symbol_info": None}
    if entry.get("live_probe"):
        result["path_state"] = LIVE if (root / entry["live_probe"]).exists() else ORPHAN
    anchor = entry.get("anchor_symbol")
    if not anchor:
        return result
    state, info = resolve_symbol(anchor, root, db_path)
    if state in (UNAVAILABLE, ORPHAN):
        result["symbol_state"], result["symbol_info"] = state, info
        return result
    line_start, line_end = info
    confirmed = entry.get("confirmed")
    if not confirmed:
        result["symbol_state"] = STALE
        result["symbol_info"] = "có anchor_symbol nhưng chưa 'confirmed:' — coi như chưa xác nhận"
        return result
    _project, file_rel, _name = parse_anchor(anchor)
    commit = _commit_before_or_on(confirmed, root)
    if not commit:
        result["symbol_state"] = STALE
        result["symbol_info"] = f"không tìm được commit quanh confirmed={confirmed}"
        return result
    if _touched_since(commit, file_rel, line_start, line_end, root):
        result["symbol_state"] = STALE
        result["symbol_info"] = f"vùng dòng {line_start}-{line_end} đổi kể từ confirmed={confirmed}"
    else:
        result["symbol_state"] = LIVE
        result["symbol_info"] = f"resolve tại {file_rel}:{line_start}-{line_end}, không đổi kể từ {confirmed}"
    return result


def cmd_check(args):
    text = MECH_PATH.read_text(encoding="utf-8")
    entries = [e for e in parse_mechanisms(text) if e.get("anchor_symbol") or e.get("live_probe")]
    rows = []
    for e in entries:
        st = compute_state(e, ROOT, DB_PATH)
        rows.append({"id": e["id"], **st})
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return 0
    icon = {LIVE: "✓", STALE: "⚠", ORPHAN: "✗", UNAVAILABLE: "·", None: "-"}
    for r in rows:
        line = f"{icon[r['path_state']]}path {icon[r['symbol_state']]}symbol  {r['id']}"
        if r["symbol_info"]:
            line += f" — {r['symbol_info']}"
        print(line)
    return 0


def cmd_why(args):
    text = MECH_PATH.read_text(encoding="utf-8")
    entries = parse_mechanisms(text)
    hits = [e for e in entries
            if (e.get("anchor_symbol") and args.symbol in e["anchor_symbol"])
            or (e.get("live_probe") and args.symbol in e["live_probe"])
            or args.symbol == e.get("id")
            or (e.get("name") and args.symbol in e["name"])]
    if not hits:
        print(f"· không tìm thấy quyết định nào neo vào {args.symbol!r}")
        return 1
    for e in hits:
        st = compute_state(e, ROOT, DB_PATH)
        state = st["symbol_state"] or st["path_state"] or "?"
        print(f"[{e['id']}] {e['name']}  ({state})")
        print(f"  WHY: {e['desc']}")
        if st["symbol_info"]:
            print(f"  liveness: {st['symbol_info']}")
    return 0


def ck(name, cond, fails):
    print(f"  {'[OK ]' if cond else '[FAIL]'} {name}")
    if not cond:
        fails.append(name)


def self_test() -> int:
    import tempfile
    import shutil as _sh

    fails = []

    # --- Task 1: mục cũ (không anchor_symbol) không bị đổi trạng thái ---
    text = MECH_PATH.read_text(encoding="utf-8")
    entries = parse_mechanisms(text)
    ck("parse >= 23 mục (không mất mục nào)", len(entries) >= 23, fails)
    legacy = [e for e in entries if not e.get("anchor_symbol")]
    ck("mục cũ (không anchor_symbol) -> symbol_state None",
       all(compute_state(e, ROOT, DB_PATH)["symbol_state"] is None for e in legacy[:23]), fails)

    # --- SC-007: DB không tồn tại -> UNAVAILABLE, KHÔNG ORPHAN ---
    fake_entry = {"id": "x", "anchor_symbol": "setup::nofile.py::foo", "confirmed": "2026-07-21"}
    st = compute_state(fake_entry, ROOT, Path("/khong-ton-tai/index.db"))
    ck("SC-007: DB vắng -> UNAVAILABLE không phải ORPHAN", st["symbol_state"] == UNAVAILABLE, fails)

    # --- FR-010 recovery: gọi lại ngay sau đó với DB thật -> không kẹt cache lý do cũ ---
    if DB_PATH.is_file():
        st2 = compute_state(fake_entry, ROOT, DB_PATH)
        ck("FR-010: recovery không kẹt cache (lý do đổi khi DB đổi từ vắng sang có)",
           st2["symbol_info"] != st["symbol_info"], fails)

    # --- Task 4/5: sandbox git repo + DB tự dựng ---
    def _sandbox_repo():
        td = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q"], cwd=td)
        subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=td)
        subprocess.run(["git", "config", "user.name", "t"], cwd=td)
        return Path(td)

    def _make_db(db_path, file_rel, checksum, symbols):
        if db_path.is_file():
            db_path.unlink()
        conn = sqlite3.connect(str(db_path))
        conn.executescript(
            "CREATE TABLE files(id INTEGER PRIMARY KEY, path TEXT, checksum TEXT);"
            "CREATE TABLE symbols(id INTEGER PRIMARY KEY, file_id INTEGER, name TEXT, "
            "line_start INTEGER, line_end INTEGER);")
        conn.execute("INSERT INTO files(id, path, checksum) VALUES (1, ?, ?)", (file_rel, checksum))
        for i, (name, ls, le) in enumerate(symbols, start=1):
            conn.execute("INSERT INTO symbols(id, file_id, name, line_start, line_end) "
                         "VALUES (?, 1, ?, ?, ?)", (i, name, ls, le))
        conn.commit()
        conn.close()

    def _sha(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]

    root = _sandbox_repo()
    mod = root / "mod.py"
    mod.write_text("def foo():\n    return 1\n\n\ndef bar():\n    return 2\n\n\ndef baz():\n    return 3\n")
    subprocess.run(["git", "add", "."], cwd=root)
    # confirmed: YYYY-MM-DD (FR-004) chỉ có độ phân giải NGÀY — nếu commit "init" và commit
    # "edit" cùng ngày thật (như trong 1 lần chạy self-test), git log --until=<ngày> 23:59:59
    # sẽ trả về HEAD (commit MỚI NHẤT trong ngày đó), không phải baseline mong muốn. Backdate
    # commit init để mô phỏng đúng use-case thật (confirmed cách đây vài ngày/tuần, không phải
    # cùng giờ với lần edit) — đây là hạn chế granularity NGÀY đã biết trước (FR-004), không
    # phải bug của _commit_before_or_on().
    env = {**__import__("os").environ,
           "GIT_AUTHOR_DATE": "2020-01-01T00:00:00", "GIT_COMMITTER_DATE": "2020-01-01T00:00:00"}
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=root, env=env)
    confirmed_date = subprocess.run(
        ["git", "-C", str(root), "log", "-1", "--format=%ad", "--date=short"],
        capture_output=True, text=True).stdout.strip()
    db = root / "index.db"
    _make_db(db, "mod.py", _sha(mod), [("foo", 1, 2), ("bar", 5, 6), ("baz", 9, 10)])

    entry_foo = {"id": "e-foo", "anchor_symbol": "sandbox::mod.py::foo", "confirmed": confirmed_date}
    entry_bar = {"id": "e-bar", "anchor_symbol": "sandbox::mod.py::bar", "confirmed": confirmed_date}
    entry_baz = {"id": "e-baz", "anchor_symbol": "sandbox::mod.py::baz", "confirmed": confirmed_date}

    st0 = compute_state(entry_bar, root, db)
    ck("sandbox baseline: bar chưa đổi -> LIVE", st0["symbol_state"] == LIVE, fails)

    # nhánh 1 — sửa thân foo() giữ tên, đổi tên baz()->baz2()
    mod.write_text("def foo():\n    return 999\n\n\ndef bar():\n    return 2\n\n\ndef baz2():\n    return 3\n")
    subprocess.run(["git", "add", "."], cwd=root)
    subprocess.run(["git", "commit", "-q", "-m", "edit+rename"], cwd=root)
    _make_db(db, "mod.py", _sha(mod), [("foo", 1, 2), ("bar", 5, 6), ("baz2", 9, 10)])

    st_foo = compute_state(entry_foo, root, db)
    ck("SC-003 sửa thân giữ tên -> STALE không phải ORPHAN", st_foo["symbol_state"] == STALE, fails)
    st_baz = compute_state(entry_baz, root, db)
    ck("SC-003 đổi tên -> ORPHAN đúng 1 chỗ (baz cũ)", st_baz["symbol_state"] == ORPHAN, fails)
    st_bar2 = compute_state(entry_bar, root, db)
    ck("SC-003 symbol không đụng (bar) vẫn LIVE, không lan cảnh báo", st_bar2["symbol_state"] == LIVE, fails)

    # nhánh 2 — xoá hẳn bar(), không có thay thế
    mod.write_text("def foo():\n    return 999\n\n\ndef baz2():\n    return 3\n")
    subprocess.run(["git", "add", "."], cwd=root)
    subprocess.run(["git", "commit", "-q", "-m", "delete bar"], cwd=root)
    _make_db(db, "mod.py", _sha(mod), [("foo", 1, 2), ("baz2", 5, 6)])

    st_bar3 = compute_state(entry_bar, root, db)
    ck("SC-003 xoá hẳn -> ORPHAN (cùng tín hiệu như đổi tên, đúng thiết kế FR-002)",
       st_bar3["symbol_state"] == ORPHAN, fails)

    _sh.rmtree(root, ignore_errors=True)

    # --- Task 5: SC-002 — mô phỏng ca harness-local (file có live_probe bị dời) ---
    root2 = _sandbox_repo()
    target = root2 / "harness-local"
    target.mkdir()
    (target / "README.md").write_text("x")
    subprocess.run(["git", "add", "."], cwd=root2)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=root2)

    entry_hl = {"id": "e-hl", "live_probe": "harness-local"}
    st_before = compute_state(entry_hl, root2, root2 / "index.db")
    ck("SC-002 trước khi dời: path_state LIVE", st_before["path_state"] == LIVE, fails)

    subprocess.run(["git", "mv", "harness-local", "llmwiki-harness-local-drift"], cwd=root2)
    subprocess.run(["git", "commit", "-q", "-m", "mv (mô phỏng drift)"], cwd=root2)

    st_after = compute_state(entry_hl, root2, root2 / "index.db")
    ck("SC-002 sau khi dời: path_state ORPHAN NGAY (không cần medic --ci)",
       st_after["path_state"] == ORPHAN, fails)
    _sh.rmtree(root2, ignore_errors=True)

    # --- Task 6: SC-004 — mọi anchor_symbol thật trỏ file TRONG repo ---
    real_entries = parse_mechanisms(MECH_PATH.read_text(encoding="utf-8"))
    anchored = [e for e in real_entries if e.get("anchor_symbol")]

    def _in_repo(e):
        parsed = parse_anchor(e["anchor_symbol"])
        if not parsed:
            return False
        try:
            (ROOT / parsed[1]).resolve().relative_to(ROOT.resolve())
            return True
        except ValueError:
            return False

    ck(f"SC-004: {len(anchored)} mục có anchor_symbol, 100% trỏ file trong repo",
       len(anchored) > 0 and all(_in_repo(e) for e in anchored), fails)

    print(f"\nSELF-TEST: {'ALL PASS' if not fails else str(len(fails)) + ' FAIL'}")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description="decision-anchoring liveness")
    sub = ap.add_subparsers(dest="cmd")
    p_check = sub.add_parser("check")
    p_check.add_argument("--json", action="store_true")
    p_why = sub.add_parser("why")
    p_why.add_argument("symbol")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(self_test())
    if args.cmd == "check":
        sys.exit(cmd_check(args))
    if args.cmd == "why":
        sys.exit(cmd_why(args))
    ap.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
