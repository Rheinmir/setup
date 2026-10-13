#!/usr/bin/env python3
"""Đối chứng các retriever TẤT ĐỊNH (0 token, 0 dependency) trên LongMemEval 500 câu.
Cùng metric R@k như MemPalace (session-level, index user-turns). Baseline = Jaccard của harness."""
import json, re, math, sys, time
from collections import Counter, defaultdict

STOP = set("""a an the and or but if then than so of to in on at by for from with without into onto as is are was were be been
being am do does did doing have has had having i me my mine you your yours he him his she her hers it its we us our they them
their this that these those there here what which who whom whose when where why how can could would should will shall may
might must not no nor also just very really too about above after again against all any because before below between both
each few more most other some such only own same over under until up down out off once while during s t don ll re ve d m
please help thanks thank hi hello hey okay ok yes yeah like get got going go went want wanted need needed know think make
made let give take one two also well still way thing things something anything everything nothing lot lots much many""".split())

def toks(s):
    return re.findall(r"[a-z0-9]+", (s or "").lower())

def stem(w):                       # Porter-lite, tất định, đủ cho paraphrase hình thái
    for suf in ("ingly", "edly", "ing", "ies", "ied", "ers", "er", "ed", "es", "s", "ly"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            w = w[:-len(suf)]
            if suf == "ies" or suf == "ied": w += "y"
            break
    return w

def norm(s, use_stop=True, use_stem=True):
    out = []
    for w in toks(s):
        if use_stop and w in STOP: continue
        if use_stem: w = stem(w)
        if len(w) > 1 or w.isdigit(): out.append(w)
    return out

def jaccard(q, t):
    a, b = set(toks(q)), set(toks(t))
    return 0.0 if not a or not b else len(a & b) / len(a | b)

class BM25:
    def __init__(self, docs, k1=1.2, b=0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(d) for d in docs]
        self.dl = [len(d) for d in docs]
        self.avgdl = (sum(self.dl) / len(docs)) if docs else 1.0
        df = Counter()
        for d in self.tf: df.update(d.keys())
        N = len(docs)
        self.idf = {w: math.log(1 + (N - n + 0.5) / (n + 0.5)) for w, n in df.items()}
    def score(self, q, i):
        tf, dl = self.tf[i], self.dl[i]
        s = 0.0
        for w in set(q):
            if w not in tf: continue
            f = tf[w]
            s += self.idf.get(w, 0) * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
        return s
    def scores(self, q):
        return [self.score(q, i) for i in range(len(self.tf))]

def entities(s):
    """'Kênh graph' thay thế trên LME: entity = từ viết hoa không ở đầu câu + số. Không LLM."""
    ents = set()
    for sent in re.split(r"[.!?\n]+", s or ""):
        ws = sent.split()
        for j, w in enumerate(ws):
            cw = re.sub(r"[^A-Za-z0-9'-]", "", w)
            if not cw: continue
            if (j > 0 and cw[0].isupper()) or re.fullmatch(r"\d[\d,./-]*", cw):
                ents.add(cw.lower())
    return ents

def rrf(rank_lists, k=60, weights=None):
    sc = defaultdict(float)
    for li, ranks in enumerate(rank_lists):
        w = (weights or [1.0] * len(rank_lists))[li]
        for r, sid in enumerate(ranks):
            sc[sid] += w / (k + r + 1)
    return [sid for sid, _ in sorted(sc.items(), key=lambda x: -x[1])]

def order(scores, ids):
    return [sid for _, sid in sorted(zip(scores, ids), key=lambda x: -x[0])]

def session_docs(q, user_only=True):
    out = []
    for sess in q["haystack_sessions"]:
        parts = [str(t.get("content", "")) for t in sess if isinstance(t, dict) and (not user_only or t.get("role") == "user")]
        out.append(parts)
    return out   # list[session] -> list[turn text]

def run(data, variant, user_only=True):
    rec = {1: 0, 3: 0, 5: 0, 10: 0}; bt = defaultdict(lambda: {"n": 0, 5: 0})
    for q in data:
        ids = q["haystack_session_ids"]; gold = set(q["answer_session_ids"])
        sd = session_docs(q, user_only)
        question = q["question"]
        if variant == "jaccard":
            ranked = order([jaccard(question, " ".join(p)) for p in sd], ids)
        else:
            use_stop = "nostop" not in variant; use_stem = "nostem" not in variant
            qn = norm(question, use_stop, use_stem)
            sess_tok = [norm(" ".join(p), use_stop, use_stem) for p in sd]
            bm_s = BM25(sess_tok)
            r_sess = order(bm_s.scores(qn), ids)
            if variant.startswith("bm25_session"):
                ranked = r_sess
            else:
                # turn-level: mỗi lượt user là một doc; điểm session = max(turn)
                turn_tok, turn_sid = [], []
                for sid, parts in zip(ids, sd):
                    for p in parts:
                        turn_tok.append(norm(p, use_stop, use_stem)); turn_sid.append(sid)
                bm_t = BM25(turn_tok)
                ts = bm_t.scores(qn)
                best = defaultdict(float)
                for s, sid in zip(ts, turn_sid): best[sid] = max(best[sid], s)
                r_turn = order([best.get(sid, 0.0) for sid in ids], ids)
                if variant == "bm25_turnmax":
                    ranked = r_turn
                else:
                    lists = [r_sess, r_turn]; w = [1.0, 1.0]
                    if "ent" in variant:
                        qe = entities(question)
                        es = [len(qe & entities(" ".join(p))) for p in sd]
                        r_ent = order(es, ids)
                        lists.append(r_ent); w.append(0.5)
                    if "rec" in variant:      # recency: phiên mới hơn xếp trước (tất định theo date)
                        dates = q["haystack_dates"]
                        r_rec = [sid for _, sid in sorted(zip(dates, ids), key=lambda x: x[0], reverse=True)]
                        lists.append(r_rec); w.append(0.3)
                    ranked = rrf(lists, weights=w)
        b = bt[q["question_type"]]; b["n"] += 1
        for k in (1, 3, 5, 10):
            if gold & set(ranked[:k]):
                rec[k] += 1
                if k == 5: b[5] += 1
    return rec, bt

if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    variants = sys.argv[2].split(",") if len(sys.argv) > 2 else [
        "jaccard", "bm25_session_nostop_nostem", "bm25_session", "bm25_turnmax",
        "rrf_sess_turn", "rrf_sess_turn_ent", "rrf_sess_turn_ent_rec"]
    n = len(data)
    print(f"LongMemEval_S · {n} câu · index user-turns (như MemPalace) · MemPalace minilm R@5 = 0.966")
    print(f"{'variant':30} {'R@1':>6} {'R@3':>6} {'R@5':>6} {'R@10':>6}  {'s':>5}")
    rows = {}
    for v in variants:
        t0 = time.time(); rec, bt = run(data, v); dt = time.time() - t0
        rows[v] = (rec, bt)
        print(f"{v:30} {rec[1]/n:6.3f} {rec[3]/n:6.3f} {rec[5]/n:6.3f} {rec[10]/n:6.3f}  {dt:5.1f}")
    best = max(rows, key=lambda v: rows[v][0][5])
    print(f"\nper-type R@5 · jaccard vs {best}:")
    for t in sorted(rows["jaccard"][1]):
        a = rows["jaccard"][1][t]; b = rows[best][1][t]
        print(f"  {t:28} {a[5]/a['n']:.3f} -> {b[5]/b['n']:.3f}  (n={a['n']})")
