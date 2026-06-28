#!/usr/bin/env python3
"""success-flywheel — the POSITIVE mirror of failure-flywheel. Capture SUCCESSFUL
trajectories by code, rank the recurring high-value patterns deterministically, and DRAFT a
reusable "playbook" stub into the propose->gate flow. Self-improving context (the 2026
"Agentic Context Engineering" trend: distil wins into a ranked, reusable playbook).

  record <task> "<summary>" [--score N] [--detail ...]  -> append 1 win to
    harness/metrics/successes.jsonl (BY CODE, gitignored local history; fail-open).
  --report  -> group by task, COUNT wins at score>=success_threshold, leaderboard
    (most-frequent first) + avg score + draft-eligible flag.
  --draft <task>  -> if that task recurs (at success) >= recurrence_threshold, scaffold a
    STUB playbook at llmwiki/wiki/sources/draft/DDMMYY-playbook-<task>.md and STOP for a
    human. The "distil wins into a playbook" summary is the quarantined adapter: until a
    distill model is wired (config, verified:false), --draft inserts a human-TODO stub.
  --self-test -> deterministic record->report in a temp dir (fdk-gate BNAL self-test).

The ONE adapter = harness/success-flywheel.config.yaml (success_threshold, recurrence_threshold,
absent distill model — verified:false). Everything else is deterministic, built now.
"""
import json
import os
import re
import sys
import tempfile
from collections import Counter
from datetime import date, datetime
from pathlib import Path

DEFAULT_DATE = "2026-06-29"
_FALLBACK = {"verified": False, "success_threshold": 8, "recurrence_threshold": 3, "distill": {"model": None}}


def _metrics_file(root: Path) -> Path:
    return root / "harness" / "metrics" / "successes.jsonl"


def _config_file(root: Path) -> Path:
    return root / "harness" / "success-flywheel.config.yaml"


def _ensure_gitignored(root: Path) -> None:
    try:
        (root / "harness" / "metrics").mkdir(parents=True, exist_ok=True)
        gi = root / ".gitignore"
        cur = gi.read_text(encoding="utf-8", errors="ignore") if gi.exists() else ""
        if "harness/metrics/successes.jsonl" not in cur:
            with open(gi, "a", encoding="utf-8") as f:
                f.write("\n# success-flywheel raw win history (local)\nharness/metrics/successes.jsonl\n")
    except Exception:
        pass


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
        pass
    return cfg


def record(root, task: str, summary: str, score=None, detail: str = None) -> dict:
    """Append 1 win. BY CODE, fail-open — never breaks the session."""
    root = Path(root)
    rec = {"ts": datetime.now().isoformat(timespec="seconds"),
           "task": (task or "uncategorized").strip(), "summary": (summary or "").strip()}
    try:
        rec["score"] = float(score)
    except (TypeError, ValueError):
        rec["score"] = None
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


def leaderboard(root: Path, success_threshold: float):
    """group-by-task over WINS (score>=threshold, or unscored counts as a win). Most-frequent first."""
    groups = {}
    for f in _read(root):
        sc = f.get("score")
        if sc is not None and sc < success_threshold:
            continue  # not a strong-enough win to distil
        task = f.get("task") or "uncategorized"
        ts = f.get("ts") or ""
        g = groups.setdefault(task, {"count": 0, "scores": [], "first": ts, "last": ts})
        g["count"] += 1
        if sc is not None:
            g["scores"].append(sc)
        if ts:
            g["first"] = min(g["first"], ts) if g["first"] else ts
            g["last"] = max(g["last"], ts) if g["last"] else ts
    return sorted(groups.items(), key=lambda kv: (-kv[1]["count"], kv[0]))


def report(root) -> str:
    root = Path(root)
    cfg = load_config(root)
    st = float(cfg.get("success_threshold", 8))
    rt = int(cfg.get("recurrence_threshold", 3))
    ordered = leaderboard(root, st)
    out = [f"SuccessFlywheel report — {len(ordered)} task-classes with wins (score>={st})",
           f"recurrence_threshold = {rt}  (adapter: harness/success-flywheel.config.yaml, "
           f"verified={cfg.get('verified')})", ""]
    if not ordered:
        out.append('(no wins recorded — success-flywheel.py record <task> "<summary>" --score N)')
        return "\n".join(out)
    out.append("Leaderboard (recurring high-value patterns, most-frequent first):")
    out.append(f"  {'#':>2}  {'wins':>4}  {'avg':>4}  {'task':<22}  {'eligible':<8}")
    for i, (task, g) in enumerate(ordered, 1):
        avg = (sum(g["scores"]) / len(g["scores"])) if g["scores"] else float("nan")
        elig = "DRAFT" if g["count"] >= rt else "-"
        out.append(f"  {i:>2}  {g['count']:>4}  {avg:>4.1f}  {task:<22}  {elig:<8}")
    eligible = [t for t, g in ordered if g["count"] >= rt]
    out.append("")
    out.append("Eligible for --draft (distil into playbook — seeds /propose, not auto-promoted):"
               if eligible else f"No task has reached the threshold ({rt}) yet.")
    out += [f"  success-flywheel.py --draft {t}" for t in eligible]
    return "\n".join(out)


def _ddmmyy(date_str: str) -> str:
    try:
        return date.fromisoformat(date_str).strftime("%d%m%y")
    except Exception:
        return date.fromisoformat(DEFAULT_DATE).strftime("%d%m%y")


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", (s or "").lower()).strip("-") or "uncategorized"


def draft(root, task: str, date_str: str = DEFAULT_DATE):
    root = Path(root)
    cfg = load_config(root)
    st = float(cfg.get("success_threshold", 8))
    rt = int(cfg.get("recurrence_threshold", 3))
    distill_model = (cfg.get("distill") or {}).get("model")
    wins = [f for f in _read(root) if (f.get("task") or "uncategorized") == task
            and (f.get("score") is None or f.get("score") >= st)]
    n = len(wins)
    if n < rt:
        return None, (f"task '{task}' has {n} wins < threshold {rt} — not eligible to draft yet.")
    ddmmyy, slug = _ddmmyy(date_str), _slug(task)
    out_dir = root / "llmwiki" / "wiki" / "sources" / "draft"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{ddmmyy}-playbook-{slug}.md"
    distill_repr = "null" if distill_model is None else str(distill_model)
    md = ["---", "type: draft", f"title: Reusable playbook distilled from recurring {task} wins",
          "status: proposed", f"tags: [success-flywheel, draft, playbook, {slug}]",
          f"timestamp: {date_str}", "---", "", f"# {ddmmyy}-playbook-{slug}", "",
          "## What",
          f"The `{task}` task succeeded **{n} times** (threshold {rt}, score>={st}). "
          f"SuccessFlywheel seeds this stub so the winning approach becomes a reusable playbook/"
          f"skill instead of being re-derived each time. SEED, not finished — a human runs "
          f"`/propose`. It does NOT auto-promote.", "",
          "## Playbook (TODO — needs human distillation)",
          f"> TODO: distil the reusable recipe from these {n} `{task}` wins. State the steps that "
          f"made them work and when to apply them. (The LLM distillation step is the quarantined "
          f"adapter — `harness/success-flywheel.config.yaml` `distill.model` is `{distill_repr}`.)",
          "", f"## Wins observed ({n})", "", "| Score | Summary | Seen |",
          "|------:|---------|------|"]
    for w in sorted(wins, key=lambda r: -(r.get("score") or 0)):
        cell = (w.get("summary") or "").replace("|", "\\|").replace("\n", " ")[:120]
        md.append(f"| {w.get('score')} | {cell} | {(w.get('ts') or '').replace('T', ' ')} |")
    md += ["", "## Origin",
           f"- **Source:** `harness/scripts/success-flywheel.py --draft {task}` from "
           f"`harness/metrics/successes.jsonl` ({n} wins, recurrence >= {rt}).",
           f"- **Adapter:** `harness/success-flywheel.config.yaml` (verified={cfg.get('verified')}, "
           f"distill.model={distill_repr}).", f"- **Date:** {date_str}", ""]
    out.write_text("\n".join(md), encoding="utf-8")
    return out, (f"drafted playbook STUB {out} from {n} '{task}' wins — STOPS for human approval.")


def self_test() -> int:
    """Deterministic record->report in a temp dir (no real metrics touched). fdk-gate hook."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "harness").mkdir()
        _config_file(root).write_text("verified: false\nsuccess_threshold: 8\nrecurrence_threshold: 2\n", encoding="utf-8")
        for i in range(2):
            record(root, "demo-task", f"win {i}", score=9)
        record(root, "weak", "barely", score=3)          # below threshold -> excluded
        rep = report(root)
        ok = ("demo-task" in rep and "DRAFT" in rep and "weak" not in rep)
        out, _ = draft(root, "demo-task")
        ok = ok and out is not None and out.exists()
    print("success-flywheel self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> None:
    args = sys.argv[1:]
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if "--root" in args:
        i = args.index("--root"); root = Path(args[i + 1]); del args[i:i + 2]
    date_str = DEFAULT_DATE
    if "--date" in args:
        i = args.index("--date"); date_str = args[i + 1]; del args[i:i + 2]
    detail = None
    if "--detail" in args:
        i = args.index("--detail"); detail = args[i + 1]; del args[i:i + 2]
    score = None
    if "--score" in args:
        i = args.index("--score"); score = args[i + 1]; del args[i:i + 2]

    if "--self-test" in args:
        sys.exit(self_test())
    if "--report" in args:
        print(report(root)); return
    if "--draft" in args:
        i = args.index("--draft")
        if len(args) <= i + 1:
            print("usage: success-flywheel.py --draft <task>", file=sys.stderr); sys.exit(2)
        out, msg = draft(root, args[i + 1], date_str)
        print(msg, file=sys.stdout if out is not None else sys.stderr)
        sys.exit(0 if out is not None else 1)
    if args and args[0] == "record":
        if len(args) < 3:
            print('usage: success-flywheel.py record <task> "<summary>" [--score N]', file=sys.stderr)
            sys.exit(2)
        rec = record(root, args[1], args[2], score, detail)
        print(f"recorded win: [{rec['task']}] {rec['summary']} (score={rec['score']})"); return
    print(__doc__)


if __name__ == "__main__":
    main()
