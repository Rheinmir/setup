#!/usr/bin/env python3
"""Bench "làm rõ truy vấn": prompt TIẾNG VIỆT → okf-scan có tìm đúng trang wiki không?
Case: 275 commit openship (gold = trang trích dẫn file commit chạm, như bench_wiki), mỗi commit có 2 prompt Việt do haiku
viết (data/wiki_queries_vi.json: plain = không định danh; ident = có 1 tên file/định danh).
Biến thể truy vấn (cùng gold, cùng okf.rank đã cài):
  en          : commit subject tiếng Anh (trần trên, = bench_wiki)
  vi_raw      : prompt Việt nguyên văn
  vi_terms    : prompt Việt qua okf.prompt_terms (định danh → từ vựng chỉ mục → bảng cầu) — thứ sẽ cài vào hook
  vi_llm      : (--llm) haiku viết lại prompt thành ≤8 từ khoá tiếng Anh rồi BM25 — tầng 4, tốn token
Mỗi biến thể đo 2 cột: chỉ chữ (files=None) và chữ + cạnh file commit (như lúc có file dirty).
Chạy: python3 bench_prompt_query.py <repo> [--llm] [--n N]"""
import importlib.util, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).parent
SCRIPTS = Path.home() / ".claude" / "harness" / "harness" / "scripts"
def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / f"{name}.py")
    m = importlib.util.module_from_spec(spec); sys.path.insert(0, str(SCRIPTS)); spec.loader.exec_module(m); return m
okf = load("okf-scan")
REPO = Path(sys.argv[1]); LLM = "--llm" in sys.argv
N = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 10**9
HALF = "--half" in sys.argv      # chỉ nửa SAU (held-out: bảng cầu mở rộng khi nhìn nửa đầu)
HUB = {"concepts/active-work.md", "concepts/architecture.md", "index.md"}
cases = [c for c in json.load(open(HERE / "data" / "wiki_queries_vi.json")) if c.get("vi_plain") and c.get("vi_ident")][:N]
if HALF: cases = cases[len(cases) // 2:]
items = okf.collect(REPO)
items = [it for it in items if it.get("source") != "memory"]   # chỉ wiki: bench đo trang, không đo episode
bridge = okf.load_bridge(REPO)
K = 4

def llm_keywords(prompt):
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
    cmd = ["claude", "-p", "--model", "haiku", "--output-format", "json", "--max-turns", "1", "--no-session-persistence",
           "--disallowedTools", "Read,Bash,Grep,Glob,Edit,Write,Agent,WebSearch,WebFetch,Task,Skill,ToolSearch"]
    ask = ("Prompt của lập trình viên (tiếng Việt):\n" + prompt + "\n\nViết lại thành tối đa 8 từ khoá TIẾNG ANH kỹ thuật để tìm trang wiki "
           "của repo (tên module, khái niệm, tên file nếu có). Chỉ in các từ khoá cách nhau bằng dấu cách, không giải thích.")
    try:
        p = subprocess.run(cmd, input=ask, capture_output=True, text=True, env=env, timeout=120)
        j = json.loads(p.stdout); return (j.get("result") or "").strip()[:200], j.get("total_cost_usd", 0)
    except Exception:
        return "", 0

if LLM:
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(lambda c: (llm_keywords(c["vi_plain"]), llm_keywords(c["vi_ident"])), cases))
    for c, ((kp, cp), (ki, ci)) in zip(cases, res):
        c["llm_plain"], c["llm_ident"], c["llm_cost"] = kp, ki, cp + ci

def variants(c):
    tp, ti = okf.prompt_terms(c["vi_plain"], items, bridge), okf.prompt_terms(c["vi_ident"], items, bridge)
    v = {"en": (c["q"], []), "vi_plain_raw": (c["vi_plain"], []), "vi_plain_terms": (tp["q"], tp["files"]),
         "vi_ident_raw": (c["vi_ident"], []), "vi_ident_terms": (ti["q"], ti["files"])}
    if LLM:
        v["vi_plain_llm"] = (c.get("llm_plain") or c["vi_plain"], []); v["vi_ident_llm"] = (c.get("llm_ident") or c["vi_ident"], [])
    return v

def strip(p):  # okf path → rel như gold ("concepts/x.md")
    return p.split("/wiki/", 1)[-1] if "/wiki/" in p else p

score = {}
for c in cases:
    gold = set(c["gold"])
    for name, (q, pf) in variants(c).items():
        for col, files in (("chữ", pf or None), ("chữ+cạnh", list(dict.fromkeys(pf + c["files"])))):
            hits = [strip(h["path"]) for h in okf.rank(items, q, k=K, files=files)]
            d = score.setdefault((name, col), {"r1": 0, "r4": 0, "n": 0, "r1x": 0, "r4x": 0, "nx": 0})
            d["n"] += 1; d["r1"] += bool(hits and hits[0] in gold); d["r4"] += bool(set(hits[:K]) & gold)
            gx = gold - HUB                      # gold KHÔNG tính trang hub (active-work chép nguyên commit subject → en được "ăn gian")
            if gx:
                hx = [h for h in hits if h not in HUB]
                d["nx"] += 1; d["r1x"] += bool(hx and hx[0] in gx); d["r4x"] += bool(set(hx[:K]) & gx)
print(f"cases {len(cases)}{' (nửa sau, held-out)' if HALF else ''} · wiki items {len(items)} · k={K} · gold¬hub = bỏ active-work/architecture")
print(f"{'biến thể':16s} {'R@1 chữ':>9s} {'R@4 chữ':>9s} {'R@1 +cạnh':>10s} {'R@4 +cạnh':>10s} │ {'R@1 chữ¬hub':>11s} {'R@4 chữ¬hub':>11s}")
order = ["en", "vi_plain_raw", "vi_plain_terms", "vi_plain_llm", "vi_ident_raw", "vi_ident_terms", "vi_ident_llm"]
for name in order:
    if (name, "chữ") not in score: continue
    a, b = score[(name, "chữ")], score[(name, "chữ+cạnh")]
    print(f"{name:16s} {a['r1']/a['n']:9.3f} {a['r4']/a['n']:9.3f} {b['r1']/b['n']:10.3f} {b['r4']/b['n']:10.3f} │ {a['r1x']/max(1,a['nx']):11.3f} {a['r4x']/max(1,a['nx']):11.3f}")
if LLM:
    print(f"llm cost ${sum(c.get('llm_cost', 0) for c in cases):.2f} cho {2*len(cases)} lượt")
out = {"cases": len(cases), "k": K, "scores": {f"{n}|{c}": v for (n, c), v in score.items()}}
json.dump(out, open(HERE / "data" / f"bench_prompt_query_{'llm_' if LLM else ''}2026-10-13.json", "w"), ensure_ascii=False, indent=1)
