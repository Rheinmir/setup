#!/usr/bin/env python3
"""Bench truy hồi WIKI 0 token. Query = tiêu đề commit thật; gold = trang wiki trích dẫn file commit chạm.
Retriever: (a) okf-scan hiện tại (Jaccard trên frontmatter) (b) BM25 frontmatter (c) BM25 body
(d) BM25 body + lan toả qua cạnh [[wikilink]] (e) RRF các kênh. Không LLM, không dependency."""
import json, re, sys, subprocess, math
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(__file__).parent))
from bench_lme import BM25, norm, toks, rrf, STOP

ROOT = Path(sys.argv[1]); WIKI = ROOT / ".llmwiki" / "wiki"
N_COMMITS = int(sys.argv[2]) if len(sys.argv) > 2 else 600

def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = {}
    if m:
        for ln in m.group(1).splitlines():
            if ":" in ln:
                k, v = ln.split(":", 1); fm[k.strip()] = v.strip().strip('"').strip("[]")
    return fm, text[m.end():] if m else text

pages = {}
for p in WIKI.rglob("*.md"):
    t = p.read_text(encoding="utf-8", errors="ignore")
    fm, body = frontmatter(t)
    if not fm.get("type"): continue
    rel = p.relative_to(WIKI).as_posix()
    pages[rel] = {"title": fm.get("title") or p.stem, "tags": fm.get("tags", ""), "body": body,
                  "stem": p.stem,
                  "links": set(re.findall(r"\[\[([^\]|#]+)", t)) | {Path(x).stem for x in re.findall(r"\]\(([^)]*\.md)", t)},
                  "files": set(re.findall(r"`((?:apps|packages)/[A-Za-z0-9_./-]+\.[a-z]+)", t))}
ids = sorted(pages)
by_stem = {pages[i]["stem"]: i for i in ids}
# cạnh wikilink (vô hướng) — sinh từ chữ đã viết, 0 token
adj = defaultdict(set)
for i in ids:
    for l in pages[i]["links"]:
        j = by_stem.get(Path(l).stem)
        if j and j != i: adj[i].add(j); adj[j].add(i)

# file -> pages (khớp file đúng, hoặc cùng thư mục module ≥4 cấp)
def dirs(f):
    parts = f.split("/")
    return {"/".join(parts[:d]) for d in range(4, len(parts))}
file_pages, dir_pages = defaultdict(set), defaultdict(set)
for i in ids:
    for f in pages[i]["files"]:
        file_pages[f].add(i)
        for d in dirs(f): dir_pages[d].add(i)

log = subprocess.run(["git", "log", "--no-merges", "--name-only", "--format=@@%h|%s", f"-n{N_COMMITS}", "--", "apps", "packages"],
                     cwd=ROOT, capture_output=True, text=True).stdout
queries, cur = [], None
for ln in log.splitlines():
    if ln.startswith("@@"):
        h, s = ln[2:].split("|", 1); cur = {"q": s, "h": h, "files": []}; queries.append(cur)
    elif ln.strip() and cur: cur["files"].append(ln.strip())
bench = []
for c in queries:
    gold = set()
    for f in c["files"]:
        gold |= file_pages.get(f, set())
    if not gold:
        for f in c["files"]:
            for d in sorted(dirs(f), key=len, reverse=True):
                if d in dir_pages: gold |= dir_pages[d]; break
    gold -= {i for i in gold if "provenance" in i or i.startswith("sources/draft")}
    if gold and len(gold) <= 4: bench.append({"q": c["q"], "gold": gold, "h": c["h"]})

def fm_text(i): return " ".join([pages[i]["title"], i, pages[i]["tags"]])
def body_text(i): return " ".join([pages[i]["title"], i, pages[i]["tags"], pages[i]["body"]])
bm_fm = BM25([norm(fm_text(i)) for i in ids]); bm_body = BM25([norm(body_text(i)) for i in ids])

def jaccard_fm(q):
    qt = set(toks(q)); out = []
    for i in ids:
        h = set(toks(fm_text(i))); out.append(len(qt & h) / len(qt | h) if qt and h else 0.0)
    return out
def order(sc): return [i for _, i in sorted(zip(sc, ids), key=lambda x: -x[0])]
def graph_spread(sc, alpha=0.5, m=5):
    """Lan toả: top-m ứng viên đẩy alpha*score sang hàng xóm wikilink. Trang được NHIỀU ứng viên trỏ tới nổi lên."""
    idx = {i: k for k, i in enumerate(ids)}; out = list(sc)
    for i in order(sc)[:m]:
        for j in adj[i]: out[idx[j]] += alpha * sc[idx[i]] / max(1, len(adj[i])) ** 0.5
    return out

variants = {
  "okf-scan hiện tại (Jaccard fm)": lambda q: order(jaccard_fm(q)),
  "BM25 frontmatter":              lambda q: order(bm_fm.scores(norm(q))),
  "BM25 body":                     lambda q: order(bm_body.scores(norm(q))),
  "BM25 body + cạnh wikilink":     lambda q: order(graph_spread(bm_body.scores(norm(q)))),
  "RRF(fm, body, body+graph)":     lambda q: rrf([order(bm_fm.scores(norm(q))), order(bm_body.scores(norm(q))), order(graph_spread(bm_body.scores(norm(q))))]),
}
n = len(bench)
print(f"wiki={len(ids)} trang · cạnh wikilink={sum(len(v) for v in adj.values())//2} · bench={n} commit có trang đúng (từ {len(queries)} commit)")
print(f"{'retriever':34} {'R@1':>6} {'R@3':>6} {'R@5':>6} {'MRR':>6}")
res = {}
for name, fn in variants.items():
    r = {1: 0, 3: 0, 5: 0}; mrr = 0.0
    for b in bench:
        ranked = fn(b["q"])
        for k in r:
            if b["gold"] & set(ranked[:k]): r[k] += 1
        for pos, i in enumerate(ranked):
            if i in b["gold"]: mrr += 1 / (pos + 1); break
    res[name] = r
    print(f"{name:34} {r[1]/n:6.3f} {r[3]/n:6.3f} {r[5]/n:6.3f} {mrr/n:6.3f}")
json.dump([{"q": b["q"], "gold": sorted(b["gold"])} for b in bench], open("bench_wiki_queries.json", "w"), ensure_ascii=False, indent=1)
print("\nví dụ 5 truy vấn:")
for b in bench[:5]: print("  ", b["q"][:70], "->", sorted(b["gold"]))
