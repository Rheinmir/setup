#!/usr/bin/env python3
import sys, re, json
from pathlib import Path
sys.argv = [sys.argv[0], "/Users/admin/orca/openship", "800"]
exec(open(Path(__file__).parent / "bench_wiki.py").read().split("variants = {")[0])   # tái dùng corpus/bench/BM25
from collections import defaultdict
def headings_text(i):
    b = pages[i]["body"]
    heads = " ".join(re.findall(r"^#+\s*(.+)$", b, re.M))
    first = re.sub(r"\s+", " ", b.strip().split("\n\n")[1] if "\n\n" in b else "")[:300]
    return " ".join([pages[i]["title"], i, pages[i]["tags"], heads, first])
bm_head = BM25([norm(headings_text(i)) for i in ids])
bm_body1 = BM25([norm(body_text(i)) for i in ids], b=1.0)
def file_edge(files):
    """Cạnh file→trang (entity graph tất định): trang trích dẫn file đang dirty / được nhắc. 0 token."""
    sc = [0.0] * len(ids); idx = {i: k for k, i in enumerate(ids)}
    for f in files:
        for i in file_pages.get(f, ()): sc[idx[i]] += 2.0
        for d in sorted(dirs(f), key=len, reverse=True):
            if d in dir_pages:
                for i in dir_pages[d]: sc[idx[i]] += 1.0 * len(d.split("/")) / 8
                break
    return sc
def path_tokens(files):
    return " ".join(t for f in files for t in toks(f) if t not in STOP and len(t) > 2 and t not in ("apps", "packages", "src", "ts", "tsx", "components", "app", "index"))
by_h = {b["h"]: b for b in bench}
qfiles = {c["h"]: c["files"] for c in queries}
variants = {
  "BM25 frontmatter":                      lambda b: order(bm_fm.scores(norm(b["q"]))),
  "BM25 title+tags+headings+đoạn đầu":     lambda b: order(bm_head.scores(norm(b["q"]))),
  "BM25 body b=1.0":                       lambda b: order(bm_body1.scores(norm(b["q"]))),
  "RRF(fm, headings)":                     lambda b: rrf([order(bm_fm.scores(norm(b["q"]))), order(bm_head.scores(norm(b["q"])))]),
  "BM25 headings + token đường dẫn dirty": lambda b: order(bm_head.scores(norm(b["q"] + " " + path_tokens(qfiles[b["h"]])))),
  "cạnh file→trang (dirty files) [≈oracle]": lambda b: order(file_edge(qfiles[b["h"]])),
  "RRF(headings+path, cạnh file)":         lambda b: rrf([order(bm_head.scores(norm(b["q"] + " " + path_tokens(qfiles[b["h"]])))), order(file_edge(qfiles[b["h"]]))]),
}
n = len(bench)
print(f"bench={n} · {'retriever':40} {'R@1':>6} {'R@3':>6} {'R@5':>6} {'MRR':>6}")
for name, fn in variants.items():
    r = {1: 0, 3: 0, 5: 0}; mrr = 0.0
    for b in bench:
        ranked = fn(b)
        for k in r:
            if b["gold"] & set(ranked[:k]): r[k] += 1
        for pos, i in enumerate(ranked):
            if i in b["gold"]: mrr += 1 / (pos + 1); break
    print(f"{'':10} {name:40} {r[1]/n:6.3f} {r[3]/n:6.3f} {r[5]/n:6.3f} {mrr/n:6.3f}")
