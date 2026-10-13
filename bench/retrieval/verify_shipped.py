#!/usr/bin/env python3
"""Chạy bench qua ĐÚNG code đã sửa (mem-rank.retrieve, okf-scan.rank) — không qua bản sao bench."""
import sys, json, importlib.util, tempfile, re, subprocess
from pathlib import Path
from collections import defaultdict
SCRIPTS = Path.home() / "orca/setup/harness/scripts"
sys.path.insert(0, str(SCRIPTS))
def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / f"{name}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
memrank = load("mem-rank"); okf = load("okf-scan")

# 1) LongMemEval qua mem-rank.retrieve thật — store = 1 memory / session (user-turns như MemPalace)
data = json.load(open("/private/tmp/claude-501/-Users-admin-orca-openship/5296a522-9972-4632-b80b-e29e4fedd2b8/scratchpad/lme-data/longmemeval_s_cleaned.json"))
rec = {1: 0, 3: 0, 5: 0, 10: 0}
with tempfile.TemporaryDirectory() as d:
    root = Path(d); (root / "harness" / "metrics").mkdir(parents=True)
    (root / "harness" / "mem-rank.config.yaml").write_text("verified: false\neviction:\n  policy: none\n", encoding="utf-8")
    cfg = memrank.load_config(root)
    for q in data:
        with open(root / "harness" / "metrics" / "memory.jsonl", "w", encoding="utf-8") as f:
            for sid, sess in zip(q["haystack_session_ids"], q["haystack_sessions"]):
                txt = " ".join(str(t.get("content", "")) for t in sess if isinstance(t, dict) and t.get("role") == "user")
                f.write(json.dumps({"id": sid, "text": txt, "kind": "note", "type": "note"}) + "\n")
        hits = memrank.retrieve(root, q["question"], k=10, cfg=cfg)
        ranked = [m["id"] for m, _ in hits]; gold = set(q["answer_session_ids"])
        for k in rec:
            if gold & set(ranked[:k]): rec[k] += 1
n = len(data)
print(f"[mem-rank.retrieve THẬT] LongMemEval {n} câu: " + "  ".join(f"R@{k}={rec[k]/n:.3f}" for k in rec))

# 2) bench wiki qua okf-scan.rank thật
ROOT = Path("/Users/admin/orca/openship")
items = okf.collect(ROOT)
bench = json.load(open("bench_wiki_queries.json"))
log = subprocess.run(["git", "log", "--no-merges", "--name-only", "--format=@@%h|%s", "-n800", "--", "apps", "packages"], cwd=ROOT, capture_output=True, text=True).stdout
qfiles, cur = {}, None
for ln in log.splitlines():
    if ln.startswith("@@"): cur = ln[2:].split("|", 1)[1]; qfiles.setdefault(cur, [])
    elif ln.strip() and cur is not None: qfiles[cur].append(ln.strip())
def wiki_rel(p): return p.replace(".llmwiki/wiki/", "")
for label, use_files in (("chỉ chữ (query)", False), ("chữ + --files dirty", True)):
    r = {1: 0, 3: 0, 5: 0}; mrr = 0.0
    for b in bench:
        hits = okf.rank(items, b["q"], k=10, files=qfiles.get(b["q"]) if use_files else None)
        ranked = [wiki_rel(h["path"]) for h in hits]; gold = set(b["gold"])
        for k in r:
            if gold & set(ranked[:k]): r[k] += 1
        for pos, p in enumerate(ranked):
            if p in gold: mrr += 1 / (pos + 1); break
    m = len(bench)
    print(f"[okf-scan.rank THẬT] wiki openship {m} commit · {label:22} R@1={r[1]/m:.3f} R@3={r[3]/m:.3f} R@5={r[5]/m:.3f} MRR={mrr/m:.3f}")
