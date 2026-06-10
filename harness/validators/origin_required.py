#!/usr/bin/env python3
"""R2 origin-required: file nội dung wiki phải có section '## Origin'.

Contract: stdin JSON {"action":"write","file_path":...,"content":...} hoặc argv files.
Nếu không có "content" thì đọc file từ disk (dùng cho PostToolUse — file đã ghi xong).
Exit 0/2.
"""
import json
import re
import sys
from pathlib import Path

ORIGIN_RE = re.compile(r"^##\s+Origin\b", re.MULTILINE)
SKIP_BASENAMES = {"README.md", "_template.md", "index.md", "log.md"}
CONTENT_DIRS = ("concepts/", "entities/", "sources/", "draft/")
# boundary (^|/) để không dính nhầm "llmwiki/" hay "mywiki/"
WIKI_REL_RE = re.compile(r"(?:^|/)wiki/(.+)$")


def is_wiki_content_file(path: str) -> bool:
    p = (path or "").replace("\\", "/")
    if not p.endswith(".md"):
        return False
    m = WIKI_REL_RE.search(p)
    if not m:
        return False
    rel = m.group(1)
    if Path(rel).name in SKIP_BASENAMES:
        return False
    return rel.startswith(CONTENT_DIRS)


def check(path, content):
    if not is_wiki_content_file(path):
        return
    if content is None:
        try:
            content = Path(path).read_text(encoding="utf-8")
        except OSError:
            return
    if not ORIGIN_RE.search(content):
        print(
            f"[R2 origin-required] {path} thieu section '## Origin' — "
            f"them vao de truy duoc nguon goc (raw file / commit / URL).",
            file=sys.stderr,
        )
        sys.exit(2)


def main() -> None:
    args = sys.argv[1:]
    if args:
        for p in args:
            check(p, None)
        sys.exit(0)
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if ev.get("action") == "write":
        check(ev.get("file_path", ""), ev.get("content") or None)
    sys.exit(0)


if __name__ == "__main__":
    main()
