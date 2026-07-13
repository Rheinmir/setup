#!/usr/bin/env python3
"""mdstore — file-first storage cho memos (frame-n04, giai đoạn 1 PoC).

memos hiện lưu DB (SQLite). Frame N04 đổi sang FILE-FIRST: mỗi memo là một file
`.md` (YAML frontmatter + body) làm nguồn chân lý người-đọc-được. `store.Driver`
của memos khoá chặt SQL (`GetDB() *sql.DB` + migrator SQL) → swap driver sống là
rewrite lớn; giai đoạn này chứng minh MÔ HÌNH DỮ LIỆU file-first bằng export +
import round-trip lossless. Đây là hình dạng dữ liệu mà driver file-first sẽ đọc/ghi.

DETERMINISTIC (build + selftest): export record→md, import md→record, round-trip
so khớp. Không đụng memos runtime.

Usage:
  mdstore.py export --db <memos.db> --out <dir>     # DB → thư mục .md
  mdstore.py import --dir <dir>                       # .md → in ra records (JSON)
  mdstore.py selftest
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

FIELDS = ["uid", "creator_id", "created_ts", "updated_ts", "row_status", "visibility", "pinned"]


def _fm_dump(meta):
    """YAML frontmatter tối giản (flat scalar) — đủ cho memo, không cần PyYAML."""
    lines = ["---"]
    for k in FIELDS:
        lines.append(f"{k}: {meta[k]}")
    lines.append("---")
    return "\n".join(lines)


def _fm_parse(text):
    """Đọc frontmatter + body từ file .md file-first."""
    if not text.startswith("---"):
        raise ValueError("thiếu frontmatter")
    _, fm, body = text.split("---", 2)
    meta = {}
    for ln in fm.strip().splitlines():
        k, _, v = ln.partition(":")
        meta[k.strip()] = v.strip()
    return meta, body.lstrip("\n")


def record_to_md(rec):
    """rec: dict cột memo → nội dung file .md file-first."""
    meta = {k: rec[k] for k in FIELDS}
    return _fm_dump(meta) + "\n\n" + (rec.get("content") or "")


def md_to_record(text):
    meta, body = _fm_parse(text)
    rec = dict(meta)
    rec["creator_id"] = int(rec["creator_id"])
    rec["created_ts"] = int(rec["created_ts"])
    rec["updated_ts"] = int(rec["updated_ts"])
    rec["pinned"] = int(rec["pinned"])
    rec["content"] = body.rstrip("\n")
    return rec


def export(db_path, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    n = 0
    for row in con.execute("SELECT uid,creator_id,created_ts,updated_ts,row_status,content,visibility,pinned FROM memo"):
        rec = dict(row)
        (out / f"{rec['uid']}.md").write_text(record_to_md(rec), encoding="utf-8")
        n += 1
    con.close()
    print(f"  file-first export: {n} memo → {out}/*.md")
    return 0


def import_dir(dir_path):
    recs = []
    for f in sorted(Path(dir_path).glob("*.md")):
        recs.append(md_to_record(f.read_text(encoding="utf-8")))
    print(json.dumps(recs, ensure_ascii=False, indent=2))
    return 0


def selftest():
    ok = True

    def chk(c, m):
        nonlocal ok
        if not c:
            ok = False
            print("  [FAIL]", m)

    samples = [
        {"uid": "aaa", "creator_id": 1, "created_ts": 1700000000, "updated_ts": 1700000001,
         "row_status": "NORMAL", "visibility": "PUBLIC", "pinned": 1,
         "content": "# Tiêu đề\n\nNội dung memo\n- gạch đầu dòng\n\n```py\nprint('x')\n```"},
        {"uid": "bbb", "creator_id": 2, "created_ts": 1700000100, "updated_ts": 1700000100,
         "row_status": "ARCHIVED", "visibility": "PRIVATE", "pinned": 0, "content": ""},
        {"uid": "ccc", "creator_id": 1, "created_ts": 1700000200, "updated_ts": 1700000300,
         "row_status": "NORMAL", "visibility": "PROTECTED", "pinned": 0,
         "content": "memo có --- dấu gạch giữa\nvà nhiều dòng"},
    ]
    for s in samples:
        back = md_to_record(record_to_md(s))
        for k in FIELDS:
            chk(str(back[k]) == str(s[k]), f"round-trip lệch field {k}: {back.get(k)} != {s[k]}")
        chk(back["content"] == s["content"], f"round-trip lệch content cho {s['uid']}")
    # frontmatter đọc được bằng mắt
    md = record_to_md(samples[0])
    chk(md.startswith("---\nuid: aaa"), "frontmatter không human-readable")
    chk("visibility: PUBLIC" in md, "thiếu visibility trong frontmatter")
    print("mdstore self-test:", "ALL PASS" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


def build_parser():
    p = argparse.ArgumentParser(prog="mdstore.py", description="File-first storage PoC cho memos (frame-n04).")
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export"); e.add_argument("--db", required=True); e.add_argument("--out", required=True)
    e.set_defaults(func=lambda a: export(a.db, a.out))
    i = sub.add_parser("import"); i.add_argument("--dir", required=True)
    i.set_defaults(func=lambda a: import_dir(a.dir))
    s = sub.add_parser("selftest"); s.set_defaults(func=lambda a: selftest())
    return p


if __name__ == "__main__":
    _a = build_parser().parse_args()
    sys.exit(_a.func(_a))
