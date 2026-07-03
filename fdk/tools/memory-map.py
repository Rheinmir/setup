#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""memory-map — VIEW bộ nhớ thứ cấp: gom scratch-log + ledger + events theo SESSION/FILE
→ đồ thị visualizable (proposal 030726-secondary-memory T3), TÁI DÙNG engine build-wiki-graph.

Council-024: reuse build-wiki-graph (KHÔNG renderer mới, KHÔNG RAG); cạnh 'elaborates' nối
session → file đã chạm; why (context vụn) hiện ở tooltip node session. File-first, nhìn bằng mắt.

CLI:
  memory-map.py            # ghi llmwiki/html/memory-map.html (JS đồ thị)
  memory-map.py --static   # bản HTML thuần 0-JS
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "llmwiki" / "html" / "memory-map.html"


def _load(modpath, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / modpath)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


WG = _load("fdk/tools/build-wiki-graph.py", "wg")
WG.REL_COLORS["elaborates"] = "#5856d6"     # session → file đã chạm
WG.REL_VI["elaborates"] = "phiên chạm/làm rõ file"


def _read(p):
    p = ROOT / p
    if not p.is_file():
        return []
    out = []
    for ln in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except ValueError:
                pass
    return out


def build():
    scratch = _read("harness/metrics/scratch-log.jsonl")
    ledger = _read("llmwiki/wiki/ledger.jsonl")
    events = _read("harness/metrics/events.jsonl")

    # gom theo session → {files:set, whys:[]}
    sess = {}

    def touch(sid, fp, why=None):
        sid = (sid or "").strip()[:8]
        if not sid:
            return
        s = sess.setdefault(sid, {"files": set(), "whys": []})
        if fp:
            s["files"].add(fp)
        if why and why.strip():
            s["whys"].append(why.strip())

    for r in scratch:
        touch(r.get("session"), r.get("file"), r.get("why"))
    for r in ledger:
        touch(r.get("session"), r.get("target"))
    for r in events:
        touch(r.get("session"), r.get("path"))

    nodes, edges, seen_files = [], [], set()
    for sid, s in sorted(sess.items()):
        why_tip = " · ".join(s["whys"][:4]) or "(chưa có why)"
        nodes.append({"id": f"s:{sid}", "path": f"session/{sid}", "group": "session", "type": "session",
                      "title": why_tip[:120], "wiki": "memory", "label": f"⏱ {sid}"})
        for fp in sorted(s["files"]):
            if fp not in seen_files:
                nodes.append({"id": fp, "path": fp, "group": "file", "type": "file",
                              "title": fp, "wiki": "memory", "label": fp.rsplit("/", 1)[-1]})
                seen_files.add(fp)
            edges.append({"from": f"s:{sid}", "rel": "elaborates", "to": fp, "kind": "to"})
    return nodes, edges


def main():
    nodes, edges = build()
    if not nodes:
        print("memory-map: chưa có dữ liệu (scratch-log/ledger/events trống)")
        return 0
    fn = WG.build_static if "--static" in sys.argv else WG.build_html
    OUT.write_text(fn("memory", str(OUT), nodes, edges, [], {}), encoding="utf-8")
    n_sess = sum(1 for n in nodes if n["type"] == "session")
    print(f"✓ wrote {OUT.relative_to(ROOT)} — {n_sess} phiên, {len(nodes)-n_sess} file, {len(edges)} cạnh (reuse build-wiki-graph)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
