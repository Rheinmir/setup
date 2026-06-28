#!/usr/bin/env python3
"""failure-flywheel — capture failures BY CODE, bucket+count them deterministically, and
DRAFT a candidate rule/skill stub into the existing propose->gate flow. Self-evolving.

Hamel's flywheel: create -> LABEL -> fix -> repeat. The slow, forgettable, human step is
"notice the same failure keeps happening and turn it into a rule." This makes the mechanical
90% deterministic and refuses to fake the 10% that needs judgement:

  - record <category> "<summary>" [--detail "..."]  -> append 1 failure to
    harness/metrics/failures.jsonl (BY CODE, like code-logger; gitignored local history).
  - --report  -> deterministic taxonomy: group by category, COUNT, leaderboard of the top
    recurring failure classes (most-frequent first) + first/last seen + draft-eligible flag.
  - --draft <category>  -> if that class recurs >= recurrence_threshold, scaffold a STUB
    proposal at llmwiki/wiki/sources/draft/DDMMYY-failure-<category>.md (valid OKF frontmatter
    + ## Origin, no ## Plan -> passes R9/R2/R7 as a SEED) and STOP for human approval. It does
    NOT auto-promote — it feeds /propose. The "distill failures into a rule" summary is the
    quarantined adapter: until a distill model is wired (config, verified:false), --draft
    inserts a templated "TODO: distill rule from these N failures" + the failure list.

The ONE adapter = harness/failure-flywheel.config.yaml (recurrence_threshold, taxonomy,
absent distill model — each verified:false). Everything else here is deterministic and built
now. Fail-open on capture: recording a failure must never break the session.

CLI:
  failure-flywheel.py [--root DIR] record <category> "<summary>" [--detail "..."]
  failure-flywheel.py [--root DIR] --report
  failure-flywheel.py [--root DIR] --draft <category> [--date YYYY-MM-DD]
"""
import json
import os
import re
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

# Fixed default — no datetime.now() in the draft FILENAME (determinism in test). Real use can
# stamp today via --date.
DEFAULT_DATE = "2026-06-28"

# Fail-safe defaults IF the adapter config is missing/unparseable. The config is the source of
# truth; these only keep the tool running and stay conservative (treat as unverified).
_FALLBACK = {"verified": False, "recurrence_threshold": 3, "taxonomy": [], "distill": {"model": None}}


# ── paths ───────────────────────────────────────────────────────────────────────────────
def _metrics_file(root: Path) -> Path:
    return root / "harness" / "metrics" / "failures.jsonl"


def _config_file(root: Path) -> Path:
    return root / "harness" / "failure-flywheel.config.yaml"


def _ensure_gitignored(root: Path) -> None:
    """failures.jsonl = raw local history -> gitignore BY CODE (same as code-logger). Fail-open."""
    try:
        (root / "harness" / "metrics").mkdir(parents=True, exist_ok=True)
        gi = root / ".gitignore"
        cur = gi.read_text(encoding="utf-8", errors="ignore") if gi.exists() else ""
        if "harness/metrics/failures.jsonl" not in cur:
            with open(gi, "a", encoding="utf-8") as f:
                f.write("\n# failure-flywheel raw failure history (local)\nharness/metrics/failures.jsonl\n")
    except Exception:
        pass


# ── adapter (the ONE quarantine boundary) ───────────────────────────────────────────────
def load_config(root: Path) -> dict:
    """Read the ONE adapter. Best-guess fallback if absent (build-now-adapt-later)."""
    cfg = {**_FALLBACK, "distill": dict(_FALLBACK["distill"])}
    try:
        import yaml
        data = yaml.safe_load(_config_file(root).read_text(encoding="utf-8"))
        if isinstance(data, dict):
            cfg.update({k: v for k, v in data.items() if v is not None})
            if not isinstance(cfg.get("distill"), dict):
                cfg["distill"] = dict(_FALLBACK["distill"])
    except Exception:
        pass  # missing / no pyyaml / unparseable -> conservative defaults
    return cfg


# ── capture (deterministic, by code, fail-open) ─────────────────────────────────────────
def record(root, category: str, summary: str, detail: str = None) -> dict:
    """Append 1 failure to failures.jsonl. BY CODE, fail-open — never breaks the session."""
    root = Path(root)
    rec = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "category": (category or "uncategorized").strip(),
        "summary": (summary or "").strip(),
    }
    if detail:
        rec["detail"] = detail.strip()
    try:
        _ensure_gitignored(root)
        with open(_metrics_file(root), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass
    return rec


def _read(root: Path):
    try:
        lines = _metrics_file(root).read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    out = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        try:
            out.append(json.loads(ln))
        except Exception:
            continue
    return out


# ── taxonomy + counting (deterministic) ─────────────────────────────────────────────────
def taxonomy(root: Path):
    """group-by-category with COUNT + first/last seen. Returns leaderboard (most-frequent first)."""
    groups = {}
    failures = _read(root)
    for f in failures:
        cat = f.get("category") or "uncategorized"
        ts = f.get("ts") or ""
        g = groups.setdefault(cat, {"count": 0, "first": ts, "last": ts, "summaries": Counter()})
        g["count"] += 1
        if ts:
            g["first"] = min(g["first"], ts) if g["first"] else ts
            g["last"] = max(g["last"], ts) if g["last"] else ts
        g["summaries"][f.get("summary", "")] += 1
    # most-frequent first; ties broken by category name -> fully deterministic
    ordered = sorted(groups.items(), key=lambda kv: (-kv[1]["count"], kv[0]))
    return ordered, failures


def report(root) -> str:
    root = Path(root)
    cfg = load_config(root)
    threshold = int(cfg.get("recurrence_threshold", 3))
    known = set(cfg.get("taxonomy") or [])
    ordered, failures = taxonomy(root)

    out = [
        f"FailureFlywheel report — {len(failures)} failures across {len(ordered)} categories",
        f"recurrence_threshold = {threshold}  "
        f"(adapter: harness/failure-flywheel.config.yaml, verified={cfg.get('verified')})",
        "",
    ]
    if not ordered:
        out.append('(no failures recorded — failure-flywheel.py record <category> "<summary>")')
        return "\n".join(out)

    out.append("Leaderboard (top recurring failure classes, most-frequent first):")
    out.append(f"  {'#':>2}  {'count':>5}  {'category':<22}  {'eligible':<8}  first .. last")
    for i, (cat, g) in enumerate(ordered, 1):
        eligible = "DRAFT" if g["count"] >= threshold else "-"
        tag = "" if (not known or cat in known) else "  (unlisted in taxonomy)"
        first = (g["first"] or "").replace("T", " ")
        last = (g["last"] or "").replace("T", " ")
        out.append(f"  {i:>2}  {g['count']:>5}  {cat:<22}  {eligible:<8}  {first} .. {last}{tag}")

    eligible = [cat for cat, g in ordered if g["count"] >= threshold]
    out.append("")
    if eligible:
        out.append("Eligible for --draft (recurs >= threshold) — seeds /propose, not auto-promoted:")
        out += [f"  failure-flywheel.py --draft {cat}" for cat in eligible]
    else:
        out.append(f"No class has reached the threshold ({threshold}) yet — nothing to draft.")
    return "\n".join(out)


# ── draft a STUB into propose->gate (deterministic scaffold; distill = adapter) ──────────
def _ddmmyy(date_str: str) -> str:
    try:
        return date.fromisoformat(date_str).strftime("%d%m%y")
    except Exception:
        return date.fromisoformat(DEFAULT_DATE).strftime("%d%m%y")


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", (s or "").lower()).strip("-") or "uncategorized"


def draft(root, category: str, date_str: str = DEFAULT_DATE):
    """If <category> recurs >= threshold, write a valid STUB draft and STOP for approval.
    Returns (path_or_None, message)."""
    root = Path(root)
    cfg = load_config(root)
    threshold = int(cfg.get("recurrence_threshold", 3))
    distill_model = (cfg.get("distill") or {}).get("model")

    failures = [f for f in _read(root) if (f.get("category") or "uncategorized") == category]
    n = len(failures)
    if n < threshold:
        return None, (f"category '{category}' recurs {n}x < threshold {threshold} — not "
                      f"eligible to draft yet (run --report to see which classes are).")

    ddmmyy = _ddmmyy(date_str)
    slug = _slug(category)
    out_dir = root / "llmwiki" / "wiki" / "sources" / "draft"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{ddmmyy}-failure-{slug}.md"

    summ_counts = Counter(f.get("summary", "") for f in failures)
    distill_repr = "null" if distill_model is None else str(distill_model)

    md = []
    md += ["---", "type: draft",
           f"title: Candidate rule to prevent recurring {category} failures",
           "status: proposed",
           f"tags: [failure-flywheel, draft, {slug}]",
           f"timestamp: {date_str}", "---", ""]
    md += [f"# {ddmmyy}-failure-{slug}", "", "**Status:** proposed", ""]
    md += ["## What",
           f"The `{category}` failure class has recurred **{n} times** (threshold "
           f"{threshold}). FailureFlywheel seeds this stub so the same mistake becomes a "
           f"rule/skill instead of repeating. This is a SEED, not a finished proposal: a "
           f"human runs `/propose` to turn it into a complete, gated change. It does NOT "
           f"auto-promote.", ""]
    md += ["## Candidate rule (TODO — needs human distillation)"]
    if distill_model:
        md += [f"<!-- distill model configured ({distill_model}) — replace this stub with its summary -->"]
    md += [f"> TODO: distill rule from these {n} `{category}` failures. State the one "
           f"preventable root cause and the single check/guard that would have caught it. "
           f"(The LLM distillation step is the quarantined adapter — "
           f"`harness/failure-flywheel.config.yaml` `distill.model` is `{distill_repr}`; "
           f"while unset, a human writes this.)", ""]
    md += [f"## Failures observed ({n})", "",
           "| Count | Summary | First seen | Last seen |",
           "|------:|---------|------------|-----------|"]
    for summary, c in sorted(summ_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        rows = [f for f in failures if f.get("summary", "") == summary]
        first = min((r.get("ts", "") for r in rows), default="").replace("T", " ")
        last = max((r.get("ts", "") for r in rows), default="").replace("T", " ")
        cell = (summary or "").replace("|", "\\|").replace("\n", " ")[:120]
        md += [f"| {c} | {cell} | {first} | {last} |"]
    md += [""]
    md += ["## Next step (human)",
           "- If these share a preventable cause, run `/propose` to draft the actual "
           "rule/skill (with Plan + Agent Task Assignment + sequence diagram so it passes "
           "the R7 gate).",
           "- If they are noise / unrelated, delete this stub. FailureFlywheel never "
           "auto-promotes — the gate stays human.", ""]
    md += ["## Origin",
           f"- **Source:** generated by `harness/scripts/failure-flywheel.py --draft "
           f"{category}` from `harness/metrics/failures.jsonl` ({n} failures of class "
           f"`{category}`, recurrence >= threshold {threshold}).",
           f"- **Adapter:** `harness/failure-flywheel.config.yaml` "
           f"(verified={cfg.get('verified')}, distill.model={distill_repr}) — the distilled "
           f"rule text is a human/LLM step, quarantined behind that one file.",
           f"- **Date:** {date_str}", ""]

    out.write_text("\n".join(md), encoding="utf-8")
    return out, (f"drafted STUB {out} from {n} '{category}' failures — STOPS for human "
                 f"approval. Run /propose to complete; FailureFlywheel does NOT auto-promote.")


# ── CLI ─────────────────────────────────────────────────────────────────────────────────
def main() -> None:
    args = sys.argv[1:]
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if "--root" in args:
        i = args.index("--root")
        root = Path(args[i + 1])
        del args[i:i + 2]

    date_str = DEFAULT_DATE
    if "--date" in args:
        i = args.index("--date")
        date_str = args[i + 1] if len(args) > i + 1 else DEFAULT_DATE
        del args[i:i + 2]

    detail = None
    if "--detail" in args:
        i = args.index("--detail")
        detail = args[i + 1] if len(args) > i + 1 else None
        del args[i:i + 2]

    if "--report" in args:
        print(report(root))
        return

    if "--draft" in args:
        i = args.index("--draft")
        if len(args) <= i + 1:
            print("usage: failure-flywheel.py --draft <category>", file=sys.stderr)
            sys.exit(2)
        out, msg = draft(root, args[i + 1], date_str)
        print(msg, file=sys.stdout if out is not None else sys.stderr)
        sys.exit(0 if out is not None else 1)

    if args and args[0] == "record":
        if len(args) < 3:
            print('usage: failure-flywheel.py record <category> "<summary>" [--detail "..."]',
                  file=sys.stderr)
            sys.exit(2)
        rec = record(root, args[1], args[2], detail)
        print(f"recorded: [{rec['category']}] {rec['summary']}")
        return

    print(__doc__)


if __name__ == "__main__":
    main()
