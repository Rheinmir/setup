#!/usr/bin/env python3
"""R-rel (wiki-core v2 Bước 3, WARN-ONLY): kiểm toàn vẹn tham chiếu của `relations:` frontmatter.

Ba luật (draft 020726-wiki-core-relations §2.3, đã sửa theo council G4/G7):
  R-rel-1 dangling      : relations.to trỏ tới id không tồn tại trong wiki (và không phải tombstone hợp lệ)
  R-rel-2 code-drift    : relations.path trỏ tới file không còn tồn tại trên disk
  R-rel-3 supersedes    : trang bị trang khác `supersedes` mà vẫn có trang `depends-on` nó

GIỚI HẠN (G7 — ghi tường minh): validator này chỉ đảm bảo TOÀN VẸN THAM CHIẾU,
KHÔNG đảm bảo quan hệ đúng ngữ nghĩa (gắn nhầm implements/touches vẫn PASS).

WARN-ONLY (G4): giai đoạn migrate chạy song song — vi phạm in stderr nhưng exit 0,
KHÔNG chặn. Nâng lên exit 2 (chặn thật) sau khi migrate ổn định (quyết định riêng, có ADR).

Contract: stdin JSON {"action":"write","file_path":...} hoặc argv paths (quét cả wiki).
"""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

FRONTMATTER_RE = re.compile(r"^---[ \t]*\n(.*?)\n---", re.DOTALL)
CONTENT_DIRS = ("concepts", "entities", "sources", "draft", "architecture", "tours")


def warn(msg: str) -> None:
    print(f"[R-rel warn-only] {msg}", file=sys.stderr)


def parse_fm(path: Path):
    try:
        m = FRONTMATTER_RE.match(path.read_text(encoding="utf-8", errors="ignore"))
        if m and yaml is not None:
            data = yaml.safe_load(m.group(1))
            return data if isinstance(data, dict) else {}
    except Exception:
        pass
    return {}


def wiki_root_of(fp: Path):
    for parent in [fp, *fp.parents]:
        if parent.name == "wiki" and parent.is_dir():
            return parent
    return None


def load_wiki(wiki: Path):
    """Trả {id: (path, frontmatter)} — id = frontmatter.id hoặc slug tên file."""
    pages = {}
    for d in CONTENT_DIRS:
        base = wiki / d
        if not base.is_dir():
            continue
        for p in base.rglob("*.md"):
            fm = parse_fm(p)
            pid = str(fm.get("id") or p.stem)
            pages[pid] = (p, fm)
    return pages


def check_file(fp: Path) -> int:
    """Kiểm 1 file mới ghi trong ngữ cảnh cả wiki. Trả số cảnh báo."""
    wiki = wiki_root_of(fp)
    if wiki is None or not fp.suffix == ".md":
        return 0
    fm = parse_fm(fp)
    rels = fm.get("relations")
    n = 0
    if not isinstance(rels, list):
        return 0
    pages = load_wiki(wiki)
    repo_root = wiki
    while repo_root.parent != repo_root and not (repo_root / ".git").exists():
        repo_root = repo_root.parent
    for r in rels:
        if not isinstance(r, dict):
            warn(f"{fp}: relation khong phai mapping: {r!r}")
            n += 1
            continue
        to, path_ = r.get("to"), r.get("path")
        if to is not None and str(to) not in pages:
            warn(f"{fp}: R-rel-1 dangling — relations.to '{to}' khong ton tai trong wiki {wiki}")
            n += 1
        if path_ is not None and not (repo_root / str(path_)).exists():
            warn(f"{fp}: R-rel-2 code-drift — relations.path '{path_}' khong con ton tai")
            n += 1
    # R-rel-3: trang này supersedes X → X không được còn ai depends-on
    superseded = {str(r.get("to")) for r in rels if isinstance(r, dict) and r.get("rel") == "supersedes" and r.get("to")}
    if superseded:
        for pid, (pp, pfm) in pages.items():
            for r2 in pfm.get("relations") or []:
                if isinstance(r2, dict) and r2.get("rel") == "depends-on" and str(r2.get("to")) in superseded:
                    warn(f"{fp}: R-rel-3 — '{r2.get('to')}' bi supersede nhung {pp} van depends-on no")
                    n += 1
    return n


def main() -> None:
    args = sys.argv[1:]
    total = 0
    if args:
        for p in args:
            total += check_file(Path(p).resolve())
    else:
        try:
            ev = json.load(sys.stdin)
        except Exception:
            sys.exit(0)
        if ev.get("action") == "write" and ev.get("file_path"):
            total += check_file(Path(ev["file_path"]).resolve())
    if total:
        warn(f"tong {total} canh bao (warn-only, khong chan — nang len chan that sau khi migrate on dinh)")
    sys.exit(0)  # WARN-ONLY: luon exit 0 trong giai doan nay


if __name__ == "__main__":
    main()
