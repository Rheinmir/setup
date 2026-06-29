#!/usr/bin/env python3
"""mem-rank — a small agent-memory layer: ADD/UPDATE/DELETE/NOOP ops + RANKED retrieval that
returns the few relevant memories instead of dumping full context (2026 agent-memory trend).

The harness already has the wiki (curated knowledge) + .claude/memory (flat facts). This adds
the missing piece: a queryable store you write to by code and retrieve top-k from by relevance.

  add "<text>" [--kind k] [--id ID]   append/replace a memory (ADD/UPDATE).
  delete ID                           remove a memory (DELETE).
  retrieve "<query>" [--k N]          top-N memories by relevance (NOOP if nothing relevant).
  --report                            list stored memories + count.
  --self-test                         deterministic add->retrieve ranking in a temp store.

The ONE adapter = harness/mem-rank.config.yaml (relevance.scorer, embedding_model, eviction;
flagged verified=false). The token-overlap ranker + store + ops are deterministic, built now.
The embedding scorer is the quarantined unknown; absent => token-overlap.
"""
import json
import os
import re
import sys
import tempfile
from pathlib import Path

import bnal_config

_FALLBACK = {"verified": False, "relevance": {"scorer": "token-overlap", "embedding_model": None},
             "eviction": {"policy": "score", "max_entries": 500}}


def _store_file(root: Path) -> Path:
    return root / "harness" / "metrics" / "memory.jsonl"


def _config_file(root: Path) -> Path:
    return root / "harness" / "mem-rank.config.yaml"


def _ensure_gitignored(root: Path) -> None:
    try:
        (root / "harness" / "metrics").mkdir(parents=True, exist_ok=True)
        gi = root / ".gitignore"
        cur = gi.read_text(encoding="utf-8", errors="ignore") if gi.exists() else ""
        if "harness/metrics/memory.jsonl" not in cur:
            with open(gi, "a", encoding="utf-8") as f:
                f.write("\n# mem-rank local memory store\nharness/metrics/memory.jsonl\n")
    except Exception:
        pass


def load_config(root: Path) -> dict:
    cfg = bnal_config.load(root, "mem-rank", _FALLBACK)
    return cfg


def _read(root: Path):
    try:
        lines = _store_file(root).read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    out = []
    for ln in lines:
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    return out


def _write_all(root: Path, mems) -> None:
    try:
        _ensure_gitignored(root)
        with open(_store_file(root), "w", encoding="utf-8") as f:
            for m in mems:
                f.write(json.dumps(m, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _next_id(mems):
    n = 0
    for m in mems:
        try:
            n = max(n, int(str(m.get("id", "0")).lstrip("m") or 0))
        except Exception:
            pass
    return f"m{n + 1}"


def add(root, text, kind=None, mid=None):
    """ADD (new id) or UPDATE (existing id). Evicts per policy if over cap."""
    root = Path(root)
    cfg = load_config(root)
    mems = _read(root)
    rec = {"id": mid or _next_id(mems), "text": (text or "").strip(), "kind": kind or "note"}
    mems = [m for m in mems if m.get("id") != rec["id"]]   # UPDATE = replace same id
    mems.append(rec)
    mems = _evict(mems, cfg)
    _write_all(root, mems)
    return rec


def delete(root, mid) -> int:
    root = Path(root)
    mems = _read(root)
    kept = [m for m in mems if m.get("id") != mid]
    _write_all(root, kept)
    return len(mems) - len(kept)


def _toks(s):
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))


def _overlap(query, text):
    q, t = _toks(query), _toks(text)
    if not q or not t:
        return 0.0
    return len(q & t) / len(q | t)            # Jaccard — deterministic


def retrieve(root, query, k=5):
    """Top-k by relevance. NOOP (empty) if nothing overlaps — don't return noise."""
    root = Path(root)
    scored = [(m, _overlap(query, m.get("text", ""))) for m in _read(root)]
    scored = [(m, s) for m, s in scored if s > 0]
    scored.sort(key=lambda ms: (-ms[1], ms[0].get("id", "")))
    return scored[:max(1, int(k))]


def _evict(mems, cfg):
    cap = int(cfg.get("eviction", {}).get("max_entries", 500))
    policy = cfg.get("eviction", {}).get("policy", "score")
    if len(mems) <= cap or policy == "none":
        return mems
    if policy == "lru":
        return mems[-cap:]                    # keep most-recent
    return mems[-cap:]                         # 'score' w/o query at write-time => recency fallback


def report(root) -> str:
    mems = _read(Path(root))
    out = [f"MemRank — {len(mems)} memories"]
    for m in mems:
        out.append(f"  {m.get('id'):<5} [{m.get('kind','')}] {m.get('text','')[:70]}")
    return "\n".join(out)


def self_test() -> int:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "harness").mkdir()
        _config_file(root).write_text("verified: false\neviction:\n  max_entries: 2\n  policy: lru\n", encoding="utf-8")
        add(root, "deploy the web app with docker compose", "ops")
        add(root, "fix the flaky retry test in CI", "test")
        hits = retrieve(root, "docker deploy", k=2)
        top_ok = hits and "docker" in hits[0][0]["text"]
        none_ok = retrieve(root, "completely unrelated zebra", k=2) == []   # NOOP
        add(root, "third memory triggers eviction (cap 2)", "note")          # cap=2 evicts oldest
        evict_ok = len(_read(root)) == 2
        ok = bool(top_ok) and none_ok and evict_ok
    print("mem-rank self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def _opt(args, flag):
    if flag in args:
        i = args.index(flag)
        val = args[i + 1] if len(args) > i + 1 else None
        del args[i:i + 2]
        return val
    return None


def main() -> None:
    args = sys.argv[1:]
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    r = _opt(args, "--root")
    if r:
        root = Path(r)
    kind = _opt(args, "--kind")
    mid = _opt(args, "--id")
    k = _opt(args, "--k") or 5
    if "--self-test" in args:
        sys.exit(self_test())
    if "--report" in args:
        print(report(root)); return
    if args and args[0] == "add":
        if len(args) < 2:
            print('usage: mem-rank.py add "<text>" [--kind k]', file=sys.stderr); sys.exit(2)
        rec = add(root, args[1], kind, mid); print(f"added {rec['id']}: {rec['text'][:60]}"); return
    if args and args[0] == "delete":
        if len(args) < 2:
            print("usage: mem-rank.py delete ID", file=sys.stderr); sys.exit(2)
        n = delete(root, args[1]); print(f"deleted {n}"); return
    if args and args[0] == "retrieve":
        if len(args) < 2:
            print('usage: mem-rank.py retrieve "<query>" [--k N]', file=sys.stderr); sys.exit(2)
        hits = retrieve(root, args[1], k)
        if not hits:
            print("(NOOP — no relevant memory)"); return
        for m, s in hits:
            print(f"  {s:.2f}  {m.get('id')}  {m.get('text','')[:70]}")
        return
    print(__doc__)


if __name__ == "__main__":
    main()
