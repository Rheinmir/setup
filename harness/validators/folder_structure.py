#!/usr/bin/env python3
"""R5 folder-structure: file .md trong wiki/ chỉ được nằm ở subfolder hợp lệ.

Contract: stdin JSON {"action":"write","file_path":...} hoặc argv files. Exit 0/2.
"""
import json
import re
import sys

ALLOWED_ROOT_FILES = {"index.md", "log.md", "README.md", "active-context.md", "decisions.md"}
ALLOWED_SUBDIRS = {"concepts", "entities", "sources", "draft"}
# boundary (^|/) để không dính nhầm "llmwiki/" hay "mywiki/"
WIKI_REL_RE = re.compile(r"(?:^|/)wiki/(.+)$")


def fail(reason: str) -> None:
    print(
        f"[R5 folder-structure] {reason} — file wiki phai nam trong "
        f"{sorted(ALLOWED_SUBDIRS)}, khong duoc o wiki/ root.",
        file=sys.stderr,
    )
    sys.exit(2)


def check_path(path: str) -> None:
    p = (path or "").replace("\\", "/")
    if not p.endswith(".md"):
        return
    m = WIKI_REL_RE.search(p)
    if not m:
        return
    rel = m.group(1)
    if "/" not in rel:
        if rel not in ALLOWED_ROOT_FILES:
            fail(f"File la o wiki/ root: {path}")
    else:
        top = rel.split("/", 1)[0]
        if top not in ALLOWED_SUBDIRS:
            fail(f"Subfolder khong hop le '{top}': {path}")


def main() -> None:
    args = sys.argv[1:]
    if args:
        for p in args:
            check_path(p)
        sys.exit(0)
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if ev.get("action") == "write":
        check_path(ev.get("file_path", ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
