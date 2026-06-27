#!/usr/bin/env python3
"""artifacts — artifact-lifecycle manifest for local-only render/draft artifacts.

The repo accumulates local-only, gitignored artifacts: HTML renders under
``llmwiki/html/`` and draft markdown under ``llmwiki/wiki/sources/draft/`` and
``llmwiki/wiki/draft/orca/``. They drift: diverging duplicate slugs, orphans that
nothing links to, and ``index.md`` rows that point at files which are gitignored
(dead on a fresh clone). This tool walks those trees, builds a manifest, and
detects those four problems.

Built with /build-now-adapt-later: EVERY retention/lifecycle threshold is read
from ``artifacts.config.yaml`` (the single quarantine boundary) — none is
hard-coded here. While that config says ``verified: false`` every destructive
``--apply`` is refused; until then ``--dedupe``/``--archive`` are DRY-RUN stubs.

Modes:
    --report   (default, READ-ONLY) walk + detect + emit fdk/MANIFEST.{json,md}
    --dedupe   DRY-RUN: list the diverging-dup-slug resolutions it WOULD do
    --archive  DRY-RUN: list the artifacts it WOULD archive per config thresholds
    --apply    with --dedupe/--archive: guarded; refuses while config verified:false

Usage:
    python3 fdk/tools/artifacts.py                 # == --report
    python3 fdk/tools/artifacts.py --report
    python3 fdk/tools/artifacts.py --dedupe         # dry-run
    python3 fdk/tools/artifacts.py --archive        # dry-run
    python3 fdk/tools/artifacts.py --dedupe --apply # refused while verified:false
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path(__file__).resolve().parent / "artifacts.config.yaml"
WIKI_DIR = ROOT / "llmwiki" / "wiki"
INDEX_MD = WIKI_DIR / "index.md"
MANIFEST_JSON = ROOT / "fdk" / "MANIFEST.json"
MANIFEST_MD = ROOT / "fdk" / "MANIFEST.md"

# (directory, glob) pairs to walk. rglob recurses, so any */archive/ subdir is
# picked up automatically.
WALK_TARGETS = [
    (ROOT / "llmwiki" / "html", "*.html"),
    (ROOT / "llmwiki" / "wiki" / "sources" / "draft", "*.md"),
    (ROOT / "llmwiki" / "wiki" / "draft" / "orca", "*.md"),
]
SKIP_BASENAMES = {"README.md", "_template.md", "README.html"}

LINK_RE = re.compile(r"\]\(([^)#\s]+\.(?:md|html))\)")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
DATE_PREFIX_RE = re.compile(r"^(\d{2})(\d{2})(\d{2})-")
DATE_SLUG_RE = re.compile(r"^\d{6}-[a-z0-9]+(?:-[a-z0-9]+)*$")
VN_RE = re.compile(r"-v\d+(?:$|-)")

# Canonical-folder ranking (lower = more canonical) for dedupe dry-run.
FOLDER_RANK = {
    "llmwiki/wiki/sources": 0,
    "llmwiki/wiki/sources/draft": 1,
    "llmwiki/wiki/draft/orca": 2,
    "llmwiki/html": 3,
}


# --------------------------------------------------------------------------- #
# config (the single quarantine boundary)
# --------------------------------------------------------------------------- #
def load_config() -> dict:
    """Load artifacts.config.yaml. Tries PyYAML; falls back to a minimal block
    parser so the read-only report runs with zero external dependencies."""
    text = CONFIG_PATH.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        cfg = yaml.safe_load(text)
        if isinstance(cfg, dict):
            return cfg
    except Exception:
        pass
    return _mini_yaml(text)


def _scalar(raw: str):
    raw = raw.strip()
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return raw.strip("'\"")


def _mini_yaml(text: str) -> dict:
    """Parse the fixed shape of artifacts.config.yaml: top-level scalars and one
    level of indented scalar sub-keys. Strips ``#`` comments."""
    out: dict = {}
    current = None
    for line in text.splitlines():
        # drop trailing comment (no value in this config contains '#')
        line = line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indented = line[0] in " \t"
        key, _, val = line.strip().partition(":")
        key = key.strip()
        if not indented:
            if val.strip():
                out[key] = _scalar(val)
                current = None
            else:
                out[key] = {}
                current = out[key]
        elif current is not None:
            current[key] = _scalar(val)
    return out


# --------------------------------------------------------------------------- #
# git helpers (memoized)
# --------------------------------------------------------------------------- #
_tracked_cache: dict = {}
_ignored_cache: dict = {}


def git_tracked(path: Path) -> bool:
    """tracked == `git ls-files --error-unmatch <path>` exits 0."""
    key = str(path)
    if key not in _tracked_cache:
        rel = os.path.relpath(path, ROOT)
        r = subprocess.run(
            ["git", "ls-files", "--error-unmatch", rel],
            cwd=str(ROOT), capture_output=True,
        )
        _tracked_cache[key] = r.returncode == 0
    return _tracked_cache[key]


def git_ignored(path: Path) -> bool:
    """gitignored == `git check-ignore -q <path>` exits 0 (works for non-existing paths too)."""
    key = str(path)
    if key not in _ignored_cache:
        rel = os.path.relpath(path, ROOT)
        r = subprocess.run(
            ["git", "check-ignore", "-q", rel],
            cwd=str(ROOT), capture_output=True,
        )
        _ignored_cache[key] = r.returncode == 0
    return _ignored_cache[key]


# --------------------------------------------------------------------------- #
# field extraction
# --------------------------------------------------------------------------- #
def sha1_of(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def date_from(stem: str):
    m = DATE_PREFIX_RE.match(stem)
    if not m:
        return None
    dd, mm, yy = m.groups()
    try:
        d, mo = int(dd), int(mm)
        if not (1 <= mo <= 12 and 1 <= d <= 31):
            return None
    except ValueError:
        return None
    return f"20{yy}-{mm}-{dd}"


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm: dict = {}
    for line in text[3:end].splitlines():
        s = line.strip()
        if not s or s.startswith("#") or ":" not in s:
            continue
        k, _, v = s.partition(":")
        fm[k.strip()] = v.strip()
    return fm


def infer_kind_html(path: Path) -> str:
    name = path.name.lower()
    if name.endswith("-seq.html"):
        return "seq"
    if "cheatsheet" in name:
        return "cheatsheet"
    if name.endswith("-docs.html"):
        return "docs"
    return "html"


def infer_kind_md(path: Path, fm: dict, text: str) -> str:
    stem = path.stem.lower()
    blob = (fm.get("tags", "") + " " + text[:600]).lower()
    if "report" in stem or "output-report" in blob:
        return "report"
    if date_from(path.stem) is None:
        # undated reference material (design-pattern*, sync-template, ...)
        return "source"
    return "proposal"


def build_record(f: Path) -> dict:
    is_md = f.suffix == ".md"
    text = f.read_text(encoding="utf-8", errors="replace") if is_md else ""
    fm = parse_frontmatter(text) if is_md else {}
    kind = infer_kind_md(f, fm, text) if is_md else infer_kind_html(f)
    return {
        "slug": f.stem,
        "ext": f.suffix.lstrip("."),
        "kind": kind,
        "status": fm.get("status"),
        "tracked": git_tracked(f),
        "gitignored": git_ignored(f),
        "path": os.path.relpath(f, ROOT),
        "sha1": sha1_of(f),
        "date": date_from(f.stem),
        "folder": os.path.relpath(f.parent, ROOT),
    }


def collect() -> list:
    arts = []
    for d, pat in WALK_TARGETS:
        if not d.is_dir():
            continue
        for f in sorted(d.rglob(pat)):
            if f.name in SKIP_BASENAMES or not f.is_file():
                continue
            arts.append(build_record(f))
    return arts


# --------------------------------------------------------------------------- #
# detections
# --------------------------------------------------------------------------- #
def index_refs():
    """Return (link_targets, referenced_basenames, referenced_stems) from index.md."""
    if not INDEX_MD.is_file():
        return [], set(), set()
    text = INDEX_MD.read_text(encoding="utf-8")
    targets = LINK_RE.findall(text)
    wikilinks = {m.strip() for m in WIKILINK_RE.findall(text)}
    basenames = {os.path.basename(t) for t in targets}
    stems = set(wikilinks) | {os.path.splitext(os.path.basename(t))[0] for t in targets}
    return targets, basenames, stems


def dup_universe() -> list:
    """Slim records for diverging-dup detection. Wider than the lifecycle walk: it
    also covers the *tracked* canonical copies (e.g. wiki/sources/), so a gitignored
    draft that has diverged from its tracked sibling is caught."""
    recs, seen = [], set()
    for d, pat in [(WIKI_DIR, "*.md"), (ROOT / "llmwiki" / "html", "*.html")]:
        if not d.is_dir():
            continue
        for f in sorted(d.rglob(pat)):
            if f.name in SKIP_BASENAMES or not f.is_file() or f in seen:
                continue
            seen.add(f)
            recs.append({
                "slug": f.stem,
                "ext": f.suffix.lstrip("."),
                "sha1": sha1_of(f),
                "tracked": git_tracked(f),
                "folder": os.path.relpath(f.parent, ROOT),
                "path": os.path.relpath(f, ROOT),
            })
    return recs


def detect_diverging_dups(arts: list):
    groups = defaultdict(list)
    for a in arts:
        groups[(a["slug"], a["ext"])].append(a)
    diverging, same = [], []
    for (slug, ext), items in sorted(groups.items()):
        folders = {i["folder"] for i in items}
        if len(items) >= 2 and len(folders) >= 2:
            hashes = {i["sha1"] for i in items}
            rec = {
                "slug": slug,
                "ext": ext,
                "copies": [
                    {"path": i["path"], "sha1": i["sha1"], "tracked": i["tracked"]}
                    for i in sorted(items, key=lambda x: x["path"])
                ],
            }
            (diverging if len(hashes) > 1 else same).append(rec)
    return diverging, same


def detect_orphans(arts: list, basenames: set, stems: set):
    out = []
    for a in arts:
        bn = os.path.basename(a["path"])
        if bn in basenames or a["slug"] in stems:
            continue
        out.append({"path": a["path"], "slug": a["slug"], "kind": a["kind"]})
    return out


def detect_dangling(targets: list):
    out = []
    for t in targets:
        resolved = WIKI_DIR / t
        if not resolved.exists():
            reason = "missing"
        elif git_ignored(resolved):
            reason = "gitignored"
        else:
            continue
        out.append(
            {"target": t, "resolved": os.path.relpath(resolved, ROOT), "reason": reason}
        )
    return out


def detect_naming(arts: list):
    out = []
    for a in arts:
        reasons = []
        if not DATE_SLUG_RE.match(a["slug"]):
            reasons.append("not DDMMYY-slug")
        if VN_RE.search(a["slug"]):
            reasons.append("-vN revision suffix (review: true revision?)")
        if reasons:
            out.append({"path": a["path"], "slug": a["slug"], "reasons": reasons})
    return out


def detect_all(arts: list) -> dict:
    targets, basenames, stems = index_refs()
    diverging, same = detect_diverging_dups(dup_universe())
    return {
        "diverging_dup_slugs": diverging,
        "redundant_same_copies": same,
        "orphans": detect_orphans(arts, basenames, stems),
        "dangling_index_rows": detect_dangling(targets),
        "naming_violations": detect_naming(arts),
    }


# --------------------------------------------------------------------------- #
# emit
# --------------------------------------------------------------------------- #
def write_manifest(arts: list, findings: dict, cfg: dict) -> None:
    counts = {
        "artifacts": len(arts),
        "diverging_dup_slugs": len(findings["diverging_dup_slugs"]),
        "redundant_same_copies": len(findings["redundant_same_copies"]),
        "orphans": len(findings["orphans"]),
        "dangling_index_rows": len(findings["dangling_index_rows"]),
        "naming_violations": len(findings["naming_violations"]),
    }
    doc = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "config_verified": bool(cfg.get("verified")),
        "config": cfg,
        "counts": counts,
        "artifacts": sorted(arts, key=lambda a: a["path"]),
        "findings": findings,
    }
    MANIFEST_JSON.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MANIFEST_MD.write_text(render_md(doc), encoding="utf-8")


def render_md(doc: dict) -> str:
    c = doc["counts"]
    L = []
    L.append("# Artifact Manifest")
    L.append("")
    L.append(f"_Generated {doc['generated']} by `fdk/tools/artifacts.py --report` (read-only)._")
    L.append("")
    L.append(
        "Thresholds come solely from `fdk/tools/artifacts.config.yaml` "
        f"(`verified: {str(doc['config_verified']).lower()}`). While unverified, "
        "every value is a best-guess and `--apply` is refused."
    )
    L.append("")
    L.append("## Summary")
    L.append("")
    L.append("| Metric | Count |")
    L.append("|--------|------:|")
    L.append(f"| Artifacts walked | {c['artifacts']} |")
    L.append(f"| Diverging duplicate slugs | {c['diverging_dup_slugs']} |")
    L.append(f"| Redundant SAME copies (legal) | {c['redundant_same_copies']} |")
    L.append(f"| Orphans (not in index.md) | {c['orphans']} |")
    L.append(f"| Dangling index rows | {c['dangling_index_rows']} |")
    L.append(f"| Naming flags (for review) | {c['naming_violations']} |")
    L.append("")

    f = doc["findings"]
    L.append("## Diverging duplicate slugs")
    L.append("")
    L.append("Same slug + same extension across folders with **different** content hash. "
             "One canonical copy must win; a second copy is legal only if identical.")
    L.append("")
    if f["diverging_dup_slugs"]:
        for d in f["diverging_dup_slugs"]:
            L.append(f"- **{d['slug']}.{d['ext']}**")
            for cp in d["copies"]:
                tag = "tracked" if cp["tracked"] else "local-only"
                L.append(f"    - `{cp['path']}` — {cp['sha1'][:12]} ({tag})")
    else:
        L.append("_none_")
    L.append("")

    L.append("## Dangling index rows")
    L.append("")
    L.append("Rows in `llmwiki/wiki/index.md` whose target is missing or gitignored "
             "(dead on a fresh clone).")
    L.append("")
    if f["dangling_index_rows"]:
        L.append("| Target | Reason |")
        L.append("|--------|--------|")
        for d in f["dangling_index_rows"]:
            L.append(f"| `{d['target']}` | {d['reason']} |")
    else:
        L.append("_none_")
    L.append("")

    L.append("## Orphans")
    L.append("")
    L.append("Artifacts on disk that `index.md` does not reference (by basename or wikilink).")
    L.append("")
    if f["orphans"]:
        for o in f["orphans"]:
            L.append(f"- `{o['path']}` ({o['kind']})")
    else:
        L.append("_none_")
    L.append("")

    L.append("## Naming flags")
    L.append("")
    L.append("Slugs that are not `DDMMYY-slug`, or use a `-vN` suffix — flagged for human review.")
    L.append("")
    if f["naming_violations"]:
        for n in f["naming_violations"]:
            L.append(f"- `{n['path']}` — {', '.join(n['reasons'])}")
    else:
        L.append("_none_")
    L.append("")

    L.append("## All artifacts")
    L.append("")
    L.append("| slug | kind | status | tracked | date | path |")
    L.append("|------|------|--------|:------:|------|------|")
    for a in doc["artifacts"]:
        L.append(
            f"| {a['slug']} | {a['kind']} | {a['status'] or '—'} | "
            f"{'yes' if a['tracked'] else 'no'} | {a['date'] or '—'} | `{a['path']}` |"
        )
    L.append("")
    return "\n".join(L)


def print_summary(arts: list, findings: dict, cfg: dict) -> None:
    print("artifacts --report (read-only)")
    print(f"  config: {os.path.relpath(CONFIG_PATH, ROOT)}  verified={cfg.get('verified')}")
    print(f"  artifacts walked: {len(arts)}")
    print(f"  DIVERGING dup slugs: {len(findings['diverging_dup_slugs'])}")
    for d in findings["diverging_dup_slugs"]:
        paths = " vs ".join(c["path"] for c in d["copies"])
        print(f"      {d['slug']}.{d['ext']}: {paths}")
    print(f"  redundant SAME copies (legal): {len(findings['redundant_same_copies'])}")
    print(f"  DANGLING index rows: {len(findings['dangling_index_rows'])}", end="")
    if findings["dangling_index_rows"]:
        miss = sum(1 for d in findings["dangling_index_rows"] if d["reason"] == "missing")
        ign = sum(1 for d in findings["dangling_index_rows"] if d["reason"] == "gitignored")
        print(f"  ({ign} gitignored, {miss} missing)")
    else:
        print()
    print(f"  ORPHANS (not in index): {len(findings['orphans'])}")
    print(f"  NAMING flags: {len(findings['naming_violations'])}")
    print(f"  wrote {os.path.relpath(MANIFEST_JSON, ROOT)} + {os.path.relpath(MANIFEST_MD, ROOT)}")


# --------------------------------------------------------------------------- #
# modes
# --------------------------------------------------------------------------- #
def cmd_report(cfg: dict) -> int:
    arts = collect()
    findings = detect_all(arts)
    write_manifest(arts, findings, cfg)
    print_summary(arts, findings, cfg)
    return 0


def apply_guard(cfg: dict) -> int:
    if not cfg.get("verified"):
        print(
            "REFUSED: artifacts.config.yaml has verified:false — destructive --apply is "
            "disabled until the lifecycle config is conformance-verified.\n"
            "See fdk/docs/ARTIFACTS.md → ADAPT-CHECKLIST.",
            file=sys.stderr,
        )
        return 12
    print(
        "REFUSED: --apply is not yet implemented (dry-run only). "
        "Implement the destructive action before enabling.",
        file=sys.stderr,
    )
    return 13


def cmd_dedupe(cfg: dict, apply: bool) -> int:
    diverging, _same = detect_diverging_dups(dup_universe())
    print("artifacts --dedupe (DRY-RUN — nothing is changed)")
    if not diverging:
        print("  no diverging duplicate slugs to resolve.")
    for d in diverging:
        ranked = sorted(
            d["copies"],
            key=lambda c: (not c["tracked"], FOLDER_RANK.get(os.path.dirname(c["path"]), 9)),
        )
        keep, drop = ranked[0], ranked[1:]
        print(f"  {d['slug']}.{d['ext']}:")
        print(f"      KEEP (canonical, best-guess): {keep['path']}")
        for c in drop:
            print(f"      would FLAG/ARCHIVE diverging copy: {c['path']}")
    if apply:
        return apply_guard(cfg)
    print("  (dry-run; pass --apply to act — currently refused while verified:false)")
    return 0


def cmd_archive(cfg: dict, apply: bool) -> int:
    arts = collect()
    arch = cfg.get("archive", {}) or {}
    renders = cfg.get("renders", {}) or {}
    trigger = arch.get("trigger", "status")
    stale_days = int(arch.get("stale_days", 30))
    keep_last = int(arch.get("keep_last_renders", 1))
    today = date.today()

    print("artifacts --archive (DRY-RUN — nothing is changed)")
    print(f"  config: trigger={trigger} stale_days={stale_days} "
          f"keep_last_renders={keep_last} renders.disposable={renders.get('disposable')}")

    cand = []
    for a in arts:
        if trigger in ("status", "both") and (a["status"] or "").lower() in ("done", "archived"):
            cand.append((a["path"], f"status={a['status']}"))
            continue
        if trigger in ("age", "both") and a["date"]:
            try:
                age = (today - datetime.strptime(a["date"], "%Y-%m-%d").date()).days
                if age > stale_days:
                    cand.append((a["path"], f"stale {age}d > {stale_days}d"))
            except ValueError:
                pass

    # disposable renders beyond keep_last_renders per slug
    if renders.get("disposable"):
        by_slug = defaultdict(list)
        for a in arts:
            if a["ext"] == "html":
                by_slug[a["slug"]].append(a)
        for slug, items in by_slug.items():
            items.sort(key=lambda x: x["date"] or "", reverse=True)
            for a in items[keep_last:]:
                cand.append((a["path"], f"render beyond keep_last_renders={keep_last}"))

    if cand:
        for path, why in sorted(cand):
            print(f"      would ARCHIVE: {path}  ({why})")
    else:
        print("      nothing meets the (best-guess) archive thresholds right now.")
    if apply:
        return apply_guard(cfg)
    print("  (dry-run; pass --apply to act — currently refused while verified:false)")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Artifact-lifecycle manifest (build-now-adapt-later).")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--report", action="store_true", help="(default) read-only walk + detect + emit manifest")
    g.add_argument("--dedupe", action="store_true", help="DRY-RUN: list diverging-dup resolutions")
    g.add_argument("--archive", action="store_true", help="DRY-RUN: list artifacts to archive per config")
    p.add_argument("--apply", action="store_true", help="with --dedupe/--archive: act (refused while verified:false)")
    args = p.parse_args(argv)

    cfg = load_config()
    if args.dedupe:
        return cmd_dedupe(cfg, args.apply)
    if args.archive:
        return cmd_archive(cfg, args.apply)
    return cmd_report(cfg)


if __name__ == "__main__":
    sys.exit(main())
