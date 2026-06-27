#!/usr/bin/env python3
"""R3 index-sync: wiki/index.md phải liệt kê đúng tập file wiki tồn tại.

Contract: `index_sync.py --wiki-dir path/to/wiki` (CLI/pre-commit/Stop hook)
          hoặc stdin JSON {"action":"stop","wiki_dir":"..."}.
Exit 0 = khớp, exit 2 = lệch (liệt kê thiếu/thừa trên stderr).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

SKIP_BASENAMES = {"README.md", "_template.md"}
_IGN_CACHE: dict[str, bool] = {}


def gitignored(rel: str, wiki: Path) -> bool:
    """True nếu (wiki/rel) bị .gitignore loại — drafts/html local-only cố ý (xem ADR/.gitignore).

    Hoạt động cả trên FRESH CLONE (file vắng mặt nhưng .gitignore tracked → khớp pattern),
    nên index_sync nhất quán giữa máy tác giả và clone sạch: file gitignored được BỎ QUA cả
    hai chiều (không bắt buộc có row, mà row trỏ tới nó cũng không bị coi là 'thừa').
    Fail-open: git lỗi/không có → coi như KHÔNG ignore.
    """
    full = (wiki / rel).as_posix()
    if full not in _IGN_CACHE:
        try:
            r = subprocess.run(["git", "check-ignore", "-q", full], capture_output=True, timeout=5)
            _IGN_CACHE[full] = (r.returncode == 0)
        except Exception:
            _IGN_CACHE[full] = False
    return _IGN_CACHE[full]
CONTENT_DIRS = ("concepts", "entities", "sources", "draft", "architecture", "tours")
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

    # Bỏ qua file gitignored (drafts/html local-only): không bắt buộc index, và row trỏ
    # tới chúng không bị coi là 'thừa' → nhất quán local ↔ fresh clone (đóng gap fresh-clone).
    exist = {f for f in content_files(wiki) if not gitignored(f, wiki)}
    indexed = indexed_files(wiki)
    missing = sorted(exist - indexed)                                   # có file (tracked), index chưa ghi
    stale = sorted(f for f in (indexed - exist) if not gitignored(f, wiki))  # row trỏ file tracked không tồn tại

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
