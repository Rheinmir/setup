#!/usr/bin/env python3
"""scoped-hooks — let a SKILL.md declare its OWN guard validator in frontmatter and fire it ONLY
while that skill is active (2026 Claude Code trend: component-scoped lifecycle hooks).

The harness has global hooks (every session) and project hooks (harness-local). This adds the
third granularity: a skill ships a `guard:` in its frontmatter; the dispatcher runs that guard
only when the skill is the active one — so a skill's guardrail travels with the skill.

  --list SKILLS_DIR            list skills that declare a guard (frontmatter_key).
  --run SKILL.md EVENT_JSON    if SKILL is active for this event, run its guard; propagate exit 2.
  --self-test                  deterministic parse+activation checks (fdk-gate BNAL self-test).

The ONE adapter = harness/scoped-hooks.config.yaml (frontmatter_key, activation.detector;
flagged verified=false). Parsing + dispatch are deterministic, built now. The "is this skill
active?" detector is the quarantined unknown; while unverified an undecidable case dispatches nothing.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

_FALLBACK = {"verified": False, "frontmatter_key": "guard",
             "activation": {"detector": "prompt-token"}}


def _config_file(root: Path) -> Path:
    return root / "harness" / "scoped-hooks.config.yaml"


def load_config(root: Path) -> dict:
    cfg = json.loads(json.dumps(_FALLBACK))
    try:
        import yaml
        data = yaml.safe_load(_config_file(root).read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for k, v in data.items():
                if v is not None:
                    cfg[k] = v
            cfg.setdefault("activation", {}).setdefault("detector", "prompt-token")
    except Exception:
        pass
    return cfg


def parse_frontmatter(text: str) -> dict:
    """Deterministic: parse the leading --- ... --- YAML block. Empty dict if none."""
    t = text or ""
    if not t.startswith("---"):
        return {}
    end = t.find("\n---", 3)
    if end == -1:
        return {}
    block = t[3:end]
    try:
        import yaml
        data = yaml.safe_load(block)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def declared_guard(skill_text: str, key: str):
    fm = parse_frontmatter(skill_text)
    g = fm.get(key)
    return str(g) if g else None


def skill_name(skill_text: str, fallback: str = "") -> str:
    return str(parse_frontmatter(skill_text).get("name") or fallback)


def is_active(name: str, context: str, detector: str) -> bool:
    """Quarantined heuristic. prompt-token: the skill is active iff /name (or its bare name)
    appears in the latest context. Unknown detector -> False (fail-safe: dispatch nothing)."""
    if not name:
        return False
    if detector == "prompt-token":
        ctx = (context or "").lower()
        return f"/{name.lower()}" in ctx or name.lower() in ctx.split()
    return False


def run_guard(root: Path, skill_path: str, event: dict, cfg: dict):
    """If the skill is active and declares a guard, run it with the event on stdin.
    Returns (ran: bool, returncode: int). Fail-open."""
    try:
        text = Path(skill_path).read_text(encoding="utf-8")
    except Exception:
        return False, 0
    key = cfg.get("frontmatter_key", "guard")
    guard = declared_guard(text, key)
    if not guard:
        return False, 0
    name = skill_name(text, Path(skill_path).stem)
    detector = cfg.get("activation", {}).get("detector", "prompt-token")
    context = event.get("prompt") or event.get("context") or ""
    if not is_active(name, context, detector):
        return False, 0
    guard_path = (root / guard) if not os.path.isabs(guard) else Path(guard)
    if not guard_path.is_file():
        return False, 0
    try:
        r = subprocess.run([sys.executable, str(guard_path)], input=json.dumps(event),
                           capture_output=True, text=True, timeout=20)
        if r.returncode == 2 and r.stderr:
            print(r.stderr.strip(), file=sys.stderr)
        return True, r.returncode
    except Exception:
        return False, 0   # fail-open


def list_guards(root: Path, skills_dir: str, cfg: dict):
    key = cfg.get("frontmatter_key", "guard")
    base = Path(skills_dir)
    rows = []
    if base.is_dir():
        for p in sorted(base.rglob("*.md")):
            try:
                g = declared_guard(p.read_text(encoding="utf-8"), key)
            except Exception:
                g = None
            if g:
                rows.append((skill_name(p.read_text(encoding="utf-8"), p.stem), str(p), g))
    return rows


def self_test() -> int:
    cfg = _FALLBACK
    with_guard = "---\nname: demo\nguard: harness/validators/no_write_raw.py\n---\n# demo\n"
    without = "---\nname: plain\n---\n# plain\n"
    g1 = declared_guard(with_guard, "guard")
    g2 = declared_guard(without, "guard")
    a_yes = is_active("demo", "please /demo this", "prompt-token")
    a_no = is_active("demo", "unrelated request", "prompt-token")
    a_unknown = is_active("demo", "/demo", "mystery-detector")   # unknown detector -> fail-safe False
    ok = (g1 and "no_write_raw" in g1) and g2 is None and a_yes and not a_no and not a_unknown
    print("scoped-hooks self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> None:
    args = sys.argv[1:]
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if "--root" in args:
        i = args.index("--root"); root = Path(args[i + 1]); del args[i:i + 2]
    if "--self-test" in args:
        sys.exit(self_test())
    cfg = load_config(root)

    if "--list" in args:
        i = args.index("--list")
        d = args[i + 1] if len(args) > i + 1 else "llmwiki/skills"
        rows = list_guards(root, d, cfg)
        for name, path, guard in rows:
            print(f"  {name:<20} {guard}   ({path})")
        print(f"  ({len(rows)} skill(s) declare a '{cfg.get('frontmatter_key')}' guard)")
        return

    if "--run" in args:
        i = args.index("--run")
        if len(args) < i + 3:
            print("usage: scoped-hooks.py --run SKILL.md EVENT_JSON", file=sys.stderr); sys.exit(2)
        try:
            event = json.loads(args[i + 2])
        except Exception:
            sys.exit(0)
        ran, rc = run_guard(root, args[i + 1], event, cfg)
        if ran and rc == 2:
            sys.exit(2)
        sys.exit(0)

    print(__doc__)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)   # fail-open absolute
