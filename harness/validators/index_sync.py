#!/usr/bin/env python3
"""R3 index-sync: wiki/index.md phải liệt kê đúng tập file wiki tồn tại.

Contract: `index_sync.py --wiki-dir path/to/wiki` (CLI/pre-commit/Stop hook)
          hoặc stdin JSON {"action":"stop","wiki_dir":"..."}.
Exit 0 = khớp, exit 2 = lệch (liệt kê thiếu/thừa trên stderr).
"""
import json
import re
import sys
from pathlib import Path

SKIP_BASENAMES = {"README.md", "_template.md"}
CONTENT_DIRS = ("concepts", "entities", "sources", "draft")
LINK_RE = re.compile(r"\]\(([^)#\s]+\.md)\)")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")


def content_files(wiki: Path) -> set[str]:
    out = set()
    for d in CONTENT_DIRS:
        base = wiki / d
        if not base.is_dir():
            continue
        for f in base.rglob("*.md"):
            if f.name not in SKIP_BASENAMES:
                out.add(f.relative_to(wiki).as_posix())
    return out


def indexed_files(wiki: Path) -> set[str]:
    idx = wiki / "index.md"
    if not idx.is_file():
        return set()
    text = idx.read_text(encoding="utf-8")
    refs = {m.lstrip("./") for m in LINK_RE.findall(text)}
    # wikilink trong index: [[name]] → khớp theo basename không đuôi
    names = {m.strip() for m in WIKILINK_RE.findall(text)}
    if names:
        for f in content_files(wiki):
            if Path(f).stem in names:
                refs.add(f)
    return refs


def main() -> None:
    wiki_dir = None
    args = sys.argv[1:]
    if "--wiki-dir" in args:
        wiki_dir = args[args.index("--wiki-dir") + 1]
    elif not sys.stdin.isatty():
        try:
            ev = json.load(sys.stdin)
            wiki_dir = ev.get("wiki_dir")
        except Exception:
            pass
    if not wiki_dir:
        print("usage: index_sync.py --wiki-dir <path>", file=sys.stderr)
        sys.exit(0)

    wiki = Path(wiki_dir)
    if not wiki.is_dir():
        sys.exit(0)

    exist = content_files(wiki)
    indexed = indexed_files(wiki)
    missing = sorted(exist - indexed)   # có file, index chưa ghi
    stale = sorted(indexed - exist)     # index ghi, file không còn

    if missing or stale:
        lines = ["[R3 index-sync] wiki/index.md lech voi thuc te:"]
        lines += [f"  THIEU trong index: {f}" for f in missing]
        lines += [f"  THUA trong index (file khong ton tai): {f}" for f in stale]
        lines.append("  → Cap nhat wiki/index.md cho khop roi tiep tuc.")
        print("\n".join(lines), file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
