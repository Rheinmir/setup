#!/usr/bin/env python3
"""dep-health — dependency NGOÀI còn dùng được không. Tất định, 0 token, fail-open.

Vì sao tồn tại (bài học đắt, 2026-07-20):
  Hook orientation quảng cáo code-graph ở MỌI phiên dựa trên đúng một câu hỏi:

      has_cg = (root / ".graph-agent" / "index.db").is_file()

  Tức là **"file có tồn tại không"**. Nhưng file tồn tại KHÔNG có nghĩa tool dùng được:
  DB 0 byte, DB thiếu schema, server chết, server chạy code cũ — tất cả đều lọt qua
  câu hỏi đó. Thực tế: code-graph hỏng nhiều tuần (một DB thiếu bảng `symbols` giết cả
  fan-out) mà framework vẫn lùa mọi phiên vào nó; agent gọi, ăn lỗi, rồi mới quay về
  grep — trả phí cả hai đường. Đo được: nhánh code-graph tốn 37 tool-call so với 14.

  Nguyên tắc rút ra, áp cho MỌI dependency ngoài:
      quảng cáo một năng lực = phải THĂM DÒ nó, không phải kiểm sự tồn tại của nó.

TRẦN ĐÃ BIẾT — nói thẳng, đừng để ai tin quá mức:
  Probe này bắt được: thiếu hẳn · DB hỏng/thiếu schema · tiến trình server chết ·
  CLI không có trên PATH · runtime không phản hồi.
  Nó KHÔNG bắt được: server đang chạy CODE CŨ (đúng ca đã xảy ra — sửa xong phải
  restart mới có hiệu lực). Muốn bắt ca đó thì phải gọi thật một truy vấn qua MCP,
  mà hook thì không nói được giao thức MCP. Đó là giới hạn thật, không phải thiếu sót
  tạm.

CLI:
    dep-health.py [--json]        # bảng người đọc / JSON cho máy
    dep-health.py --quiet-ok      # chỉ in khi CÓ vấn đề (dùng ở hook)
    dep-health.py --self-test
"""
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

OK, DEGRADED, ABSENT = "ok", "degraded", "absent"


def db_has_schema(db_path: Path) -> bool:
    """DB sqlite này query được không — mở được VÀ có bảng thật.

    Đây là câu hỏi mà `.is_file()` không trả lời được, và chính chỗ hụt đó đã để
    code-graph hỏng lọt lưới nhiều tuần.
    """
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            names = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
        finally:
            conn.close()
        return {"symbols", "files"} <= names
    except sqlite3.Error:
        return False


def _proc_alive(needle: str) -> bool:
    try:
        out = subprocess.run(["pgrep", "-f", needle], capture_output=True, text=True, timeout=5)
        return out.returncode == 0 and bool(out.stdout.strip())
    except Exception:  # noqa: BLE001
        return False


def probe_code_graph(root: Path) -> dict:
    dbs = [p for p in [root / ".graph-agent" / "index.db"] if p.is_file()]
    if not dbs:
        try:
            dbs = [d / ".graph-agent" / "index.db" for d in root.iterdir()
                   if d.is_dir() and (d / ".graph-agent" / "index.db").is_file()]
        except OSError:
            dbs = []
    if not dbs:
        return {"name": "code-graph", "status": ABSENT,
                "reason": "không có .graph-agent/index.db nào trong project"}
    usable = [p for p in dbs if db_has_schema(p)]
    if not usable:
        return {"name": "code-graph", "status": DEGRADED,
                "reason": f"{len(dbs)} index.db có mặt nhưng KHÔNG cái nào có schema "
                          f"(0 byte hoặc index chưa chạy xong)",
                "fix": "chạy lại reindex cho repo, hoặc xoá .graph-agent/index.db rỗng"}
    if not _proc_alive("graph/server.py"):
        return {"name": "code-graph", "status": DEGRADED, "dbs_usable": len(usable),
                "reason": "DB lành nhưng KHÔNG thấy tiến trình server đang chạy",
                "fix": "khởi động lại Claude Code để MCP server lên lại"}
    return {"name": "code-graph", "status": OK, "dbs_usable": len(usable),
            "note": "KHÔNG kiểm được server có đang chạy code MỚI hay không (trần đã biết)"}


def probe_orca(root: Path) -> dict:
    if shutil.which("orca") is None:
        return {"name": "orca", "status": ABSENT, "reason": "orca không có trên PATH"}
    try:
        out = subprocess.run(["orca", "status", "--json"], capture_output=True,
                             text=True, timeout=20)
        d = json.loads(out.stdout)
        rt = ((d.get("result") or {}).get("runtime") or {})
        if rt.get("reachable") and rt.get("state") == "ready":
            return {"name": "orca", "status": OK, "runtime": rt.get("state")}
        return {"name": "orca", "status": DEGRADED,
                "reason": f"runtime state={rt.get('state')!r} reachable={rt.get('reachable')}",
                "fix": "mở app Orca, hoặc `orca open`"}
    except Exception as e:  # noqa: BLE001
        return {"name": "orca", "status": DEGRADED, "reason": f"orca status lỗi: {str(e)[:60]}"}


def collect(root: Path) -> list:
    return [probe_code_graph(root), probe_orca(root)]


def self_test() -> int:
    """Tất định, KHÔNG cần dependency nào — chạy được ở CI."""
    import tempfile
    fails = []

    def ck(name, cond):
        print(f"  {'[OK ]' if cond else '[FAIL]'} {name}")
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        empty = tmp / "empty.db"
        empty.touch()
        ck("DB 0 byte → KHÔNG có schema (đúng ca đã để lọt lưới)", not db_has_schema(empty))
        ck("file không tồn tại → không có schema", not db_has_schema(tmp / "khong-co.db"))

        good = tmp / "good.db"
        c = sqlite3.connect(good)
        c.executescript("CREATE TABLE symbols(a); CREATE TABLE files(b);")
        c.close()
        ck("DB có đủ bảng symbols+files → usable", db_has_schema(good))

        half = tmp / "half.db"
        c = sqlite3.connect(half)
        c.executescript("CREATE TABLE symbols(a);")  # thiếu files
        c.close()
        ck("DB THIẾU một bảng → vẫn coi là hỏng (không nửa vời)", not db_has_schema(half))

        r = probe_code_graph(tmp)
        ck("project không có index.db → absent, không phải degraded", r["status"] == ABSENT)

        (tmp / "sub" / ".graph-agent").mkdir(parents=True)
        (tmp / "sub" / ".graph-agent" / "index.db").touch()
        r = probe_code_graph(tmp)
        ck("có index.db nhưng rỗng → DEGRADED (KHÔNG được quảng cáo)", r["status"] == DEGRADED)

        ck("mọi probe luôn trả dict có 'status'",
           all(isinstance(p, dict) and "status" in p for p in collect(tmp)))
        ck("tiến trình không tồn tại → _proc_alive False", not _proc_alive("khong-co-tien-trinh-nao-ten-nay"))

    print(f"\nSELF-TEST: {'ALL PASS' if not fails else str(len(fails)) + ' FAIL'}")
    return 1 if fails else 0


def main() -> None:
    ap = argparse.ArgumentParser(description="dependency ngoài còn dùng được không")
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet-ok", action="store_true", help="chỉ in khi có vấn đề")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    try:
        deps = collect(Path(a.root).resolve())
    except Exception:  # noqa: BLE001 — fail-open tuyệt đối
        sys.exit(0)
    if a.json:
        print(json.dumps({"deps": deps}, ensure_ascii=False, indent=1))
        sys.exit(0)
    bad = [d for d in deps if d["status"] == DEGRADED]
    if a.quiet_ok and not bad:
        sys.exit(0)
    for d in deps:
        icon = {"ok": "✓", "degraded": "⚠", "absent": "·"}[d["status"]]
        line = f"{icon} {d['name']}: {d['status']}"
        if d.get("reason"):
            line += f" — {d['reason']}"
        print(line)
        if d.get("fix"):
            print(f"    → {d['fix']}")
    sys.exit(0)


if __name__ == "__main__":
    main()
