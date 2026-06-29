#!/usr/bin/env python3
"""spec-gate — Spec-Driven Development gate: make the spec a tracked, checkable source of truth
and verify a change is grounded in one (2026 anti-drift trend; cf. GitHub Spec Kit).

Our /propose is a one-time gate; this adds the durable spec->plan->tasks artifact + a
conformance check that a change cites its spec — so implementation can't quietly drift from intent.

  --check SPEC.md          validate a spec has the required sections; exit 2 if malformed (strict).
  --scaffold NAME          write a spec template into spec_dir (spec->plan->tasks backbone).
  --conformance SPEC TEXT  does TEXT (a commit message / diff) cite SPEC via link_token?
  --self-test              deterministic checks in-memory (fdk-gate BNAL self-test).

The ONE adapter = harness/spec-gate.config.yaml (required_sections, spec_dir, conformance.mode
+ link_token — verified:false). Parsing/checking is deterministic, built now. Default mode
'advisory' so an un-settled schema never blocks a commit.
"""
import json
import os
import sys
from pathlib import Path

import bnal_config

_FALLBACK = {
    "verified": False,
    "required_sections": ["## Intent", "## Plan", "## Tasks", "## Success criteria"],
    "spec_dir": "llmwiki/wiki/sources/spec",
    "conformance": {"mode": "advisory", "link_token": "Spec:"},
}


def _config_file(root: Path) -> Path:
    return root / "harness" / "spec-gate.config.yaml"


def load_config(root: Path) -> dict:
    cfg = bnal_config.load(root, "spec-gate", _FALLBACK)
    return cfg


def missing_sections(text: str, required):
    """Deterministic: which required headings are absent (line-anchored)."""
    lines = [ln.strip() for ln in (text or "").splitlines()]
    return [s for s in required if s.strip() not in lines]


def cites_spec(change_text: str, spec_path: str, link_token: str) -> bool:
    """True iff the change text references the spec via the link token (e.g. 'Spec: path')."""
    txt = change_text or ""
    if link_token and link_token in txt:
        # token present; accept if the spec path or its basename also appears, or token alone if no path given
        if not spec_path:
            return True
        return spec_path in txt or Path(spec_path).name in txt
    return False


SPEC_TEMPLATE = """# {name}

## Intent
<One paragraph: WHAT this must do and WHY. The source of truth — code is derived from this.>

## Plan
<Architectural decisions that satisfy the intent. No code yet.>

## Tasks
- [ ] <atomic, testable task>
- [ ] <atomic, testable task>

## Success criteria
<How we verify the implementation matches THIS spec (the conformance gate).>
"""


def scaffold(root: Path, name: str, cfg: dict):
    d = root / cfg.get("spec_dir", _FALLBACK["spec_dir"])
    d.mkdir(parents=True, exist_ok=True)
    out = d / (name if name.endswith(".md") else f"{name}.md")
    out.write_text(SPEC_TEMPLATE.format(name=name.replace('.md', '')), encoding="utf-8")
    return out


def _enforced(cfg: dict) -> bool:
    return str(cfg.get("conformance", {}).get("mode", "advisory")).lower() == "strict" and cfg.get("verified") is True


def self_test() -> int:
    cfg = json.loads(json.dumps(_FALLBACK))
    good = "# X\n## Intent\na\n## Plan\nb\n## Tasks\n- c\n## Success criteria\nd\n"
    bad = "# X\n## Intent\na\n## Tasks\n- c\n"   # missing ## Plan + ## Success criteria
    miss_good = missing_sections(good, cfg["required_sections"])
    miss_bad = missing_sections(bad, cfg["required_sections"])
    lk = cfg["conformance"]["link_token"]
    c_ok = cites_spec("fix bug\n\nSpec: sources/spec/x.md", "sources/spec/x.md", lk)
    c_no = cites_spec("fix bug, no reference", "sources/spec/x.md", lk)
    ok = (not miss_good) and set(miss_bad) == {"## Plan", "## Success criteria"} and c_ok and not c_no
    print("spec-gate self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> None:
    args = sys.argv[1:]
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if "--root" in args:
        i = args.index("--root"); root = Path(args[i + 1]); del args[i:i + 2]
    if "--self-test" in args:
        sys.exit(self_test())
    cfg = load_config(root)

    if "--scaffold" in args:
        i = args.index("--scaffold")
        if len(args) <= i + 1:
            print("usage: spec-gate.py --scaffold NAME", file=sys.stderr); sys.exit(2)
        out = scaffold(root, args[i + 1], cfg)
        print(f"scaffolded spec {out} — fill ## Intent/## Plan/## Tasks/## Success criteria"); return

    if "--check" in args:
        i = args.index("--check")
        if len(args) <= i + 1:
            print("usage: spec-gate.py --check SPEC.md", file=sys.stderr); sys.exit(2)
        try:
            text = Path(args[i + 1]).read_text(encoding="utf-8")
        except Exception:
            print(f"[spec-gate] cannot read {args[i + 1]}", file=sys.stderr); sys.exit(0)
        miss = missing_sections(text, cfg.get("required_sections", []))
        if not miss:
            print(f"[spec-gate] {args[i + 1]} ✓ has all required sections"); sys.exit(0)
        msg = f"[spec-gate] {args[i + 1]} missing: {', '.join(miss)}"
        if _enforced(cfg):
            print(msg + "  (strict)", file=sys.stderr); sys.exit(2)
        print(msg + "  (advisory — set conformance.mode:strict + verified:true to enforce)", file=sys.stderr)
        sys.exit(0)

    if "--conformance" in args:
        i = args.index("--conformance")
        if len(args) < i + 3:
            print("usage: spec-gate.py --conformance SPEC TEXT", file=sys.stderr); sys.exit(2)
        lk = cfg.get("conformance", {}).get("link_token", "Spec:")
        if cites_spec(args[i + 2], args[i + 1], lk):
            print(f"[spec-gate] change cites its spec ({lk} {args[i + 1]}) ✓"); sys.exit(0)
        msg = f"[spec-gate] change does NOT cite spec '{args[i + 1]}' via '{lk}'"
        if _enforced(cfg):
            print(msg + "  (strict)", file=sys.stderr); sys.exit(2)
        print(msg + "  (advisory)", file=sys.stderr); sys.exit(0)

    print(__doc__)


if __name__ == "__main__":
    main()
