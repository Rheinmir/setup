#!/usr/bin/env python3
"""Audit + backfill nợ wiki trong MỘT process — thay 4-5 python3 spawn rời.

Gộp 3 kiểm tra (kết quả y hệt validator gốc, import lại logic — không nhân bản):
  - R2 Origin   : file nội dung thiếu '## Origin'      (origin_required.py)
  - R3 index    : index.md lệch file thật               (index_sync.py)
  - R9 OKF v0.1 : thiếu YAML frontmatter `type`         (okf-check.py)

Hai chế độ:
  (mặc định)  detect → in JSON debt-report ra stdout. exit 3 nếu CÓ nợ, 0 nếu sạch.
  --fix       backfill TỰ ĐỘNG (chỉ THÊM, không sửa/xóa nội dung cũ):
              Origin  → append section, hash/date lấy bằng 1 LƯỢT `git log` cho cả lô
              index   → thêm row cho file thiếu (summary từ H1/title)
              OKF     → migrate bold **Type:** → YAML (okf-check.migrate_text)
              In tóm tắt số file đã sửa. exit 0.

Usage:
  python3 harness/scripts/audit.py --wiki-dir <wiki> [--json]
  python3 harness/scripts/audit.py --wiki-dir <wiki> --fix
"""
import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # harness/scripts
VALIDATORS = HERE.parent / "validators"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


origin_mod = _load(VALIDATORS / "origin_required.py", "_origin")
index_mod = _load(VALIDATORS / "index_sync.py", "_indexsync")
okf_mod = _load(HERE / "okf-check.py", "_okf")

H1_RE = re.compile(r"^#\s+(.*?)\s*$", re.MULTILINE)
TITLE_RE = re.compile(r"^title:\s*(.+?)\s*$", re.MULTILINE)


# ---------- detect ----------
def detect(wiki: Path) -> dict:
    # R2 Origin: dùng đúng bộ lọc của validator gốc
    missing_origin = []
    for d in index_mod.CONTENT_DIRS:
        base = wiki / d
        if not base.is_dir():
            continue
        for f in base.rglob("*.md"):
            rel = f.relative_to(wiki).as_posix()
            if not origin_mod.is_wiki_content_file(f.as_posix()):
                continue
            if not origin_mod.ORIGIN_RE.search(f.read_text(encoding="utf-8", errors="replace")):
                missing_origin.append(rel)

    # R3 index — content_files() đã loại gitignored (an-toàn-mặc-định); chiều 'stale' vẫn phải lọc.
    exist = index_mod.content_files(wiki)
    indexed = index_mod.indexed_files(wiki)
    index_missing = sorted(exist - indexed)
    index_stale = sorted(f for f in (indexed - exist) if not index_mod.gitignored(f, wiki))

    # R9 OKF
    okf_bad = [
        p.relative_to(wiki).as_posix()
        for p in okf_mod.content_files(wiki)
        if not okf_mod.has_okf_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
    ]

    debt = bool(missing_origin or index_missing or index_stale or okf_bad)
    return {
        "debt": debt,
        "missing_origin": sorted(missing_origin),
        "index_missing": index_missing,
        "index_stale": index_stale,
        "okf_bad": sorted(okf_bad),
    }


# ---------- fix ----------
def _git_last_commits(root: Path, rel_paths):
    """1 LƯỢT git log cho cả lô → {path: 'hash date'}. File chưa commit không có key."""
    out = {}
    if not rel_paths:
        return out
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "log", "--format=C|%h|%ad", "--date=short", "--name-only"],
            capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return out
    want = set(rel_paths)
    cur = None
    for line in res.stdout.splitlines():
        if line.startswith("C|"):
            _, h, d = line.split("|", 2)
            cur = f"{h} {d}"
        elif line.strip() and cur:
            # path trong git là relative tới root; wiki rel = 'llmwiki/wiki/...'
            for w in list(want):
                if line.strip().endswith(w) or w.endswith(line.strip()):
                    out[w] = cur
                    want.discard(w)
    return out


def fix(wiki: Path, root: Path) -> dict:
    rep = detect(wiki)
    fixed = {"origin": 0, "index": 0, "okf": 0}

    # --- Origin: 1 lượt git log cho cả lô ---
    if rep["missing_origin"]:
        # path tương đối với root để git nhận
        wiki_rel_root = wiki.relative_to(root).as_posix() if wiki.is_relative_to(root) else "llmwiki/wiki"
        full_rels = [f"{wiki_rel_root}/{p}" for p in rep["missing_origin"]]
        commits = _git_last_commits(root, full_rels)
        for p, full in zip(rep["missing_origin"], full_rels):
            f = wiki / p
            src = commits.get(full, "chưa commit")
            text = f.read_text(encoding="utf-8")
            if not text.endswith("\n"):
                text += "\n"
            text += (
                "\n## Origin\n"
                f"- legacy backfill (harness-update) — commit gần nhất: {src}\n"
            )
            f.write_text(text, encoding="utf-8")
            fixed["origin"] += 1

    # --- index: thêm row cho file thiếu ---
    if rep["index_missing"]:
        idx = wiki / "index.md"
        rows = []
        for rel in rep["index_missing"]:
            text = (wiki / rel).read_text(encoding="utf-8", errors="replace")
            mt = TITLE_RE.search(text) or H1_RE.search(text)
            summary = (mt.group(1).strip() if mt else Path(rel).stem)[:120]
            typ = Path(rel).parts[0].rstrip("s") if Path(rel).parts else "wiki"
            name = Path(rel).stem
            rows.append(f"| [{name}]({rel}) | {typ} | {summary} |")
        with idx.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(rows) + "\n")
        fixed["index"] += len(rows)

    # --- OKF migrate ---
    okf_files = okf_mod.content_files(wiki)
    for p in okf_files:
        text = p.read_text(encoding="utf-8")
        if okf_mod.has_okf_frontmatter(text):
            continue
        new, changed = okf_mod.migrate_text(text, p, wiki)
        if changed:
            p.write_text(new, encoding="utf-8")
            fixed["okf"] += 1

    return fixed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki-dir", required=True)
    ap.add_argument("--root", default=None, help="git root cho Origin backfill (mặc định: 3 cấp trên wiki)")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    wiki = Path(args.wiki_dir).resolve()
    if not wiki.is_dir():
        print(f"[audit] khong tim thay wiki dir: {wiki}", file=sys.stderr)
        sys.exit(1)
    root = Path(args.root).resolve() if args.root else wiki.parent.parent.parent

    if args.fix:
        fixed = fix(wiki, root)
        print(f"[audit] backfill xong — Origin:{fixed['origin']} index:{fixed['index']} OKF:{fixed['okf']}")
        sys.exit(0)

    rep = detect(wiki)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False))
    else:
        print(f"[audit] debt={rep['debt']} "
              f"missing_origin={len(rep['missing_origin'])} "
              f"index_missing={len(rep['index_missing'])} "
              f"index_stale={len(rep['index_stale'])} "
              f"okf_bad={len(rep['okf_bad'])}")
        for k in ("missing_origin", "index_missing", "index_stale", "okf_bad"):
            for f in rep[k]:
                print(f"  {k}: {f}")
    sys.exit(3 if rep["debt"] else 0)


if __name__ == "__main__":
    main()
