#!/usr/bin/env python3
"""sync-skill-catalog — kéo `catalog.json` của repo Rheinmir/skills về `fdk/skills.catalog.json` (ảnh chụp cam kết).

Vì sao có (PLAN 141026-skills-split T3): skill tách sang repo riêng, nhưng docs của framework (overstack.html,
CAPABILITIES.md), dấu năng lực (capability-stamp) và parity hứa↔giao (fresh-install-smoke) vẫn cần MỘT danh sách skill
TẤT ĐỊNH, không phụ thuộc máy nào đang cài gì trong ~/.claude/skills. Ảnh chụp này là nguồn đó: cập nhật khi phát hành
setup, commit cùng bump version.

    python3 fdk/tools/sync-skill-catalog.py             # kéo từ SKILLS_RAW (mặc định raw main của Rheinmir/skills) → ghi ảnh chụp
    python3 fdk/tools/sync-skill-catalog.py --from ~/orca/skills/catalog.json   # từ checkout local (offline)
    python3 fdk/tools/sync-skill-catalog.py --check     # rc 2 nếu ảnh chụp khác remote (advisory — cần mạng, không vào CI)
    python3 fdk/tools/sync-skill-catalog.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "fdk" / "skills.catalog.json"
DEFAULT_RAW = "https://raw.githubusercontent.com/Rheinmir/skills/main/catalog.json"


def fetch(src: str, timeout: int = 15) -> dict:
    if src.startswith(("http://", "https://")):
        with urllib.request.urlopen(src, timeout=timeout) as r:
            return json.load(r)
    return json.loads(Path(src).expanduser().read_text(encoding="utf-8"))


def slim(cat: dict) -> dict:
    """Giữ phần docs/stamp cần: version, catalog_sha, count, và per-skill name/loop/description/external/requires."""
    return {"schema": 1, "version": cat.get("version"), "harness_floor": cat.get("harness_floor"),
            "catalog_sha": cat.get("catalog_sha"), "count": cat.get("count", len(cat.get("skills", []))),
            "source": cat.get("source") or DEFAULT_RAW,
            "skills": [{k: s.get(k) for k in ("name", "loop", "description", "external", "requires") if s.get(k) is not None}
                       for s in cat.get("skills", [])]}


def load_snapshot(root: Path = ROOT) -> dict | None:
    p = root / "fdk" / "skills.catalog.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "catalog.json"
        src.write_text(json.dumps({"version": "1.2.3", "catalog_sha": "abc", "skills": [
            {"name": "a", "loop": "utils", "description": "x", "external": False, "sha": "zzz", "dir": "skills/a"}]}))
        s = slim(fetch(str(src)))
        assert s["version"] == "1.2.3" and s["count"] == 1 and s["skills"][0] == {"name": "a", "loop": "utils", "description": "x", "external": False}, s
        assert "sha" not in s["skills"][0]
    print("[sync-skill-catalog] self-test OK")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", default=os.environ.get("SKILLS_RAW", DEFAULT_RAW), help="URL hoặc file catalog.json")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    try:
        remote = slim(fetch(a.src))
    except Exception as e:
        print(f"[sync-skill-catalog] không đọc được {a.src}: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    remote["source"] = a.src
    if a.check:
        cur = load_snapshot()
        if cur and cur.get("catalog_sha") == remote.get("catalog_sha"):
            print(f"[sync-skill-catalog] ✓ ảnh chụp khớp remote: v{cur.get('version')} · {cur.get('count')} skill · {cur.get('catalog_sha')}")
            return 0
        print(f"[sync-skill-catalog] LỆCH: ảnh chụp {cur.get('version') if cur else '(chưa có)'}/{cur.get('catalog_sha') if cur else '-'} "
              f"≠ remote {remote.get('version')}/{remote.get('catalog_sha')} → python3 fdk/tools/sync-skill-catalog.py rồi capability-stamp --update",
              file=sys.stderr)
        return 2
    SNAPSHOT.write_text(json.dumps(remote, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[sync-skill-catalog] ghi {SNAPSHOT.relative_to(ROOT)}: v{remote.get('version')} · {remote.get('count')} skill · {remote.get('catalog_sha')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
