#!/usr/bin/env python3
"""prospect-critic — PROSPECTIVE reflection: check a PLAN before execution against the distilled
failure taxonomy and flag the classes it is walking into (2026 prospective-reflection trend; the
counterpart to retrospective trace-grading). It consumes failure-flywheel's taxonomy — the
negative flywheel labels failure CLASSES, this critic catches a plan heading into one.

  --check PLAN_TEXT_OR_FILE   match the plan against per-class trigger phrases; report hit classes;
                              exit 2 if hits >= revision_threshold AND verified (force revision).
  --self-test                 deterministic match (a sloppy plan flags, a tight plan passes).

The ONE adapter = harness/prospect-critic.config.yaml (triggers, revision_threshold, match.mode;
flagged verified=false). The keyword match is deterministic, built now. The trigger phrases + a
semantic matcher are the unknowns; default is advisory (report, never blocks) until verified.
"""
import json
import os
import sys
from pathlib import Path

import bnal_config

_FALLBACK = {"verified": False, "taxonomy_source": "harness/failure-flywheel.config.yaml",
             "revision_threshold": 1, "match": {"mode": "keyword"},
             "triggers": {"overcomplication": ["flexible", "future-proof", "just in case"],
                          "scope-creep": ["also refactor", "while we're at it"],
                          "missing-verification": ["should work", "no need to test"]}}


def _config_file(root: Path) -> Path:
    return root / "harness" / "prospect-critic.config.yaml"


def load_config(root: Path) -> dict:
    cfg = bnal_config.load(root, "prospect-critic", _FALLBACK)
    return cfg


def known_classes(root: Path, cfg: dict):
    """Canonical failure classes from the negative flywheel (advisory cross-check)."""
    try:
        import yaml
        src = root / cfg.get("taxonomy_source", _FALLBACK["taxonomy_source"])
        data = yaml.safe_load(src.read_text(encoding="utf-8")) or {}
        return set(data.get("taxonomy") or [])
    except Exception:
        return set()


def critique(plan_text, cfg: dict):
    """Deterministic: which failure classes the plan's wording triggers, with the matched phrase."""
    text = (plan_text or "").lower()
    hits = {}
    for cls, phrases in (cfg.get("triggers") or {}).items():
        for ph in phrases:
            if ph.lower() in text:
                hits.setdefault(cls, []).append(ph)
    return hits


def self_test() -> int:
    cfg = json.loads(json.dumps(_FALLBACK))
    sloppy = "Let's also refactor everything and add a flexible future-proof framework; it should work."
    tight = "Add one validator for rule P1, write its failing test, then make it pass."
    h_sloppy = critique(sloppy, cfg)
    h_tight = critique(tight, cfg)
    ok = len(h_sloppy) >= 2 and not h_tight
    print("prospect-critic self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> None:
    args = sys.argv[1:]
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if "--root" in args:
        i = args.index("--root"); root = Path(args[i + 1]); del args[i:i + 2]
    if "--self-test" in args:
        sys.exit(self_test())
    cfg = load_config(root)
    if "--check" in args:
        i = args.index("--check")
        if len(args) <= i + 1:
            print("usage: prospect-critic.py --check PLAN_TEXT_OR_FILE", file=sys.stderr); sys.exit(2)
        arg = args[i + 1]
        text = arg
        try:
            p = Path(arg)
            if p.is_file():
                text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            pass
        hits = critique(text, cfg)
        kc = known_classes(root, cfg)
        if not hits:
            print("[prospect-critic] plan clean — no failure-class triggers ✓"); sys.exit(0)
        lines = [f"  {cls}{'' if not kc or cls in kc else ' (not in taxonomy)'}: {', '.join(set(ph))}"
                 for cls, ph in hits.items()]
        msg = f"[prospect-critic] plan triggers {len(hits)} failure class(es) — revise before executing:\n" + "\n".join(lines)
        thr = int(cfg.get("revision_threshold", 1))
        if len(hits) >= thr and cfg.get("verified") is True:
            print(msg + "\n  (forcing revision — verified)", file=sys.stderr); sys.exit(2)
        print(msg + "\n  (advisory — verified:true makes this force revision)", file=sys.stderr); sys.exit(0)
    print(__doc__)


if __name__ == "__main__":
    main()
