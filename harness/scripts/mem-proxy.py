#!/usr/bin/env python3
"""mem-proxy — deterministic EPISODIC retrieval generator for retrieval-eval (no model).

query-proxy.py does this for the wiki (semantic pages); this does it for the EPISODIC memory
layer. It seeds a temp mem-rank store from harness/evals/episodic-fixtures.json, then for each
episodic golden (llmwiki/wiki/sources/evals/episodic/*.md) runs mem-rank retrieve(question,
kind_filter='episode') and emits the outputs contract retrieval-eval expects:

    golden-id -> {"pages": [episode-id ranked...], "tokens": <int>}

Same fixtures + same goldens + token-overlap ranker => same result (deterministic). This proves
DoD #9: query/wiki-room retrieve by MEANING (an episode id nobody linked), not just [[wikilink]].
Token = sum len(text)//4 of episodes actually returned (the few surfaced, not the whole store).

CLI:
  mem-proxy.py [--fixtures F] [--evals-dir D] [--k N] --out FILE
  mem-proxy.py --self-test
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURES = REPO_ROOT / "harness" / "evals" / "episodic-fixtures.json"
DEFAULT_EVALS = REPO_ROOT / "llmwiki" / "wiki" / "sources" / "evals" / "episodic"
SKIP = {"README.md", "index.md", "_template.md", "log.md"}


def _load_memrank():
    """mem-rank.py has a hyphen — import it by path."""
    path = Path(__file__).resolve().parent / "mem-rank.py"
    spec = importlib.util.spec_from_file_location("mem_rank", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))     # so its `import bnal_config` resolves
    spec.loader.exec_module(mod)
    return mod


def _seed_store(mr, root: Path, fixtures: Path):
    data = json.loads(Path(fixtures).read_text(encoding="utf-8"))
    eps = data.get("episodes") or []
    store = root / "harness" / "metrics" / "memory.jsonl"
    store.parent.mkdir(parents=True, exist_ok=True)
    with open(store, "w", encoding="utf-8") as f:
        for e in eps:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return eps


def _load_goldens(evals_dir: Path):
    import yaml
    out = []
    base = Path(evals_dir)
    if not base.is_dir():
        return out
    for p in sorted(base.rglob("*.md")):
        if p.name in SKIP:
            continue
        t = p.read_text(encoding="utf-8")
        if not t.startswith("---"):
            continue
        end = t.find("\n---", 3)
        if end == -1:
            continue
        data = yaml.safe_load(t[3:end])
        if not isinstance(data, dict) or "question" not in data:
            continue
        out.append((str(data.get("id") or p.stem), data["question"]))
    return out


def generate(fixtures, evals_dir, k):
    mr = _load_memrank()
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "harness").mkdir()
        (root / "harness" / "mem-rank.config.yaml").write_text(
            "verified: false\neviction:\n  policy: none\n", encoding="utf-8")
        _seed_store(mr, root, fixtures)
        outputs = {}
        for gid, question in _load_goldens(evals_dir):
            hits = mr.retrieve(root, question, k=k, kind_filter="episode")
            pages = [m.get("id") for m, _ in hits]
            tokens = sum(len(m.get("text", "")) // 4 for m, _ in hits)
            outputs[gid] = {"pages": pages, "tokens": tokens}
    return outputs


def self_test():
    outs = generate(DEFAULT_FIXTURES, DEFAULT_EVALS, k=5)
    if not outs:
        print("[mem-proxy] self-test: 0 episodic golden — chưa có gì để sinh."); return 1
    ok = all(o["pages"] for o in outs.values())
    print("[mem-proxy] self-test:", "PASS" if ok else "FAIL",
          f"({len(outs)} golden, every one retrieved ≥1 episode)")
    return 0 if ok else 2


def main():
    ap = argparse.ArgumentParser(description="mem-proxy — episodic retrieval outputs for retrieval-eval.")
    ap.add_argument("--fixtures", default=str(DEFAULT_FIXTURES))
    ap.add_argument("--evals-dir", default=str(DEFAULT_EVALS))
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--out", default=None)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(self_test())
    outputs = generate(args.fixtures, args.evals_dir, args.k)
    text = json.dumps(outputs, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"[mem-proxy] {len(outputs)} episodic outputs -> {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
