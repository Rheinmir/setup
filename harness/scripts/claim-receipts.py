#!/usr/bin/env python3
"""claim-receipts — a live hallucination gate: extract the file/path references an agent CITES
and verify they actually resolve (2026 "Tool Receipts" / CiteAudit trend — agents fabricate
tool results and cite files/APIs that do not exist). Turns failure-flywheel's "hallucination"
class from a post-mortem into a pre-commit check.

  --check TEXT_OR_FILE     extract references from the text (or file), verify each resolves on
                           disk; report unresolved ones. exit 2 if any unresolved AND strict.
  --self-test              deterministic resolve check (real ref passes, fake ref flagged).

The ONE adapter = harness/claim-receipts.config.yaml (resolver, strictness, claim_taxonomy,
ref_extensions — verified:false). Extraction + filesystem resolve are deterministic, built now.
The symbol-aware resolver (code-graph) is the unknown; default strictness 'advisory'.
"""
import json
import os
import re
import sys
from pathlib import Path

import bnal_config

_FALLBACK = {"verified": False, "resolver": "filesystem", "strictness": "advisory",
             "ref_extensions": ["py", "md", "yaml", "yml", "json", "sh", "js", "ts", "html", "txt", "toml", "cfg"]}


def _config_file(root: Path) -> Path:
    return root / "harness" / "claim-receipts.config.yaml"


def load_config(root: Path) -> dict:
    cfg = bnal_config.load(root, "claim-receipts", _FALLBACK)
    return cfg


def extract_refs(text, exts):
    """Path-like tokens ending in a known extension (conservative — not every word)."""
    if not text:
        return []
    ext_alt = "|".join(re.escape(e) for e in exts)
    rx = re.compile(r"(?<![\w./-])([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:" + ext_alt + r"))\b")
    # strip surrounding backticks/quotes already excluded; dedupe, keep order
    seen, out = set(), []
    for m in rx.finditer(text):
        r = m.group(1).strip("`'\"")
        if r not in seen:
            seen.add(r); out.append(r)
    return out


def resolve(ref, root: Path) -> bool:
    """filesystem resolver: does the ref exist (as-is, under root, or by basename anywhere shallow)?"""
    try:
        if Path(ref).exists():
            return True
        if (root / ref).exists():
            return True
        # basename fallback: a bare filename that exists somewhere tracked-ish (shallow guard)
        base = Path(ref).name
        if "/" not in ref:
            for p in list(root.rglob(base))[:1]:
                if p.exists():
                    return True
    except Exception:
        return True   # fail-open: never flag on a resolver error
    return False


def check(text, root: Path, cfg: dict):
    refs = extract_refs(text, cfg.get("ref_extensions", _FALLBACK["ref_extensions"]))
    unresolved = [r for r in refs if not resolve(r, root)]
    return refs, unresolved


def self_test() -> int:
    root = Path(__file__).resolve().parents[1].parent   # repo root (…/harness/scripts -> repo)
    cfg = json.loads(json.dumps(_FALLBACK))
    real = "see harness/policy.yaml and harness/scripts/fdk-gate.py for details"
    fake = "edited src/totally/made-up-nonexistent-file.py per the plan"
    _, u_real = check(real, root, cfg)
    _, u_fake = check(fake, root, cfg)
    ok = not u_real and any("made-up-nonexistent" in r for r in u_fake)
    print("claim-receipts self-test:", "PASS" if ok else "FAIL")
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
            print("usage: claim-receipts.py --check TEXT_OR_FILE", file=sys.stderr); sys.exit(2)
        arg = args[i + 1]
        text = arg
        try:
            p = Path(arg)
            if p.is_file():
                text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            pass
        refs, unresolved = check(text, root, cfg)
        if not unresolved:
            print(f"[claim-receipts] {len(refs)} reference(s), all resolve ✓"); sys.exit(0)
        msg = f"[claim-receipts] {len(unresolved)}/{len(refs)} reference(s) DO NOT resolve (possible hallucination): " + ", ".join(unresolved)
        if str(cfg.get("strictness")).lower() == "strict" and cfg.get("verified") is True:
            print(msg + "  (strict)", file=sys.stderr); sys.exit(2)
        print(msg + "  (advisory — set strictness:strict + verified:true to enforce)", file=sys.stderr); sys.exit(0)
    print(__doc__)


if __name__ == "__main__":
    main()
