#!/usr/bin/env python3
"""wiki-core v2 Bước 2: migrate frontmatter `id` + `relations` cho trang wiki hiện có.

Chạy SONG SONG với validator warn-only (G4 — council 020726): script này chỉ GHI
quan hệ suy được từ tín hiệu KHÁCH QUAN, không đoán ngữ nghĩa (G7):
  - id           : slug tên file (bất biến khi đổi title)
  - derives-from : path trong dòng `- **Source:** \\`...\\`` của ## Origin, nếu path tồn tại
Các kiểu khác (implements/supersedes/depends-on/touches) do agent tự suy lúc
verify-before-commit về sau (G5) — KHÔNG bulk-migrate ở đây.

Usage: python3 fdk/tools/wiki-relations.py <wiki_dir> [--dry-run]
"""
import re
import sys
from pathlib import Path

CONTENT_DIRS = ("concepts", "entities", "sources", "draft", "architecture", "tours")
FRONTMATTER_RE = re.compile(r"^(---[ \t]*\n)(.*?)(\n---)", re.DOTALL)
SOURCE_RE = re.compile(r"^\s*-\s*\*\*Source:\*\*\s*`([^`]+)`", re.MULTILINE)


def migrate(path: Path, repo_root: Path, dry: bool):
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None  # không có frontmatter — để validator OKF xử, không tự chế
    block = m.group(2)
    if re.search(r"^id[ \t]*:", block, re.MULTILINE):
        return None  # đã migrate — idempotent
    add = [f"id: {path.stem}"]
    rels = []
    origin = SOURCE_RE.search(text)
    if origin:
        src = origin.group(1).split(" ")[0].strip()
        if (repo_root / src).exists():
            rels.append(f"  - {{rel: derives-from, path: {src}}}")
    if rels:
        add.append("relations:")
        add.extend(rels)
    new_block = block + "\n" + "\n".join(add)
    new_text = text[: m.start(2)] + new_block + text[m.end(2):]
    if not dry:
        path.write_text(new_text, encoding="utf-8")
    return f"{path}: +id" + (" +derives-from" if rels else "")


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry = "--dry-run" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(1)
    wiki = Path(args[0]).resolve()
    repo_root = wiki
    while repo_root.parent != repo_root and not (repo_root / ".git").exists():
        repo_root = repo_root.parent
    changed = 0
    for d in CONTENT_DIRS:
        base = wiki / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            if p.name in {"README.md", "_template.md"}:
                continue
            msg = migrate(p, repo_root, dry)
            if msg:
                print(("[dry] " if dry else "") + msg)
                changed += 1
    print(f"{'would migrate' if dry else 'migrated'}: {changed} page(s)")


if __name__ == "__main__":
    main()
