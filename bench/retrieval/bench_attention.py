#!/usr/bin/env python3
"""Self-attention có cần NHẮC LẠI không? — thí nghiệm có đối chứng, LLM trong vòng (claude -p).

Câu hỏi: khối recall (≤4 đường dẫn okf-scan gợi ý) bơm MỘT LẦN đầu phiên, sau N token hội thoại
không liên quan, model còn chọn đúng trang wiki không? So với bơm lặp (nhắc lại mỗi ~40k ký tự)
và không bơm (đối chứng: model đoán mò).

Mỗi ô = 1 lời gọi `claude -p --max-turns 1` không tool; đo HIT (đáp án chứa đúng trang gold đã
nằm trong khối recall) và TOKEN đầu vào thật (usage trong JSON trả về) = cột chi phí.

Dùng: bench_attention.py --repo ~/orca/openship --lme <longmemeval_s_cleaned.json> [--n 10]
      [--sizes 0,100000,300000] [--model haiku] [--jobs 4] [--out out.json]
"""
import argparse
import importlib.util
import json
import os
import random
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SCRIPTS = Path.home() / "orca/setup/harness/scripts"
sys.path.insert(0, str(SCRIPTS))


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


okf = load("okf-scan")

HOOK_TPL = ("🧠 [recall] Quét OKF ({n} mục, có biên lai) → nên đọc:\n{hits}\n"
            "  Đây là NHẮC, không phải sự thật — file trong repo mới là nguồn đúng.")
TASK = ("--- NHIỆM VỤ MỚI ---\nNhiệm vụ: `{q}`.\nTrước khi sửa code, bạn sẽ đọc MỘT trang wiki nào trong repo "
        "(đường dẫn bắt đầu bằng .llmwiki/wiki/)? Trả lời CHỈ một đường dẫn tương đối, không giải thích.")
PRE = ("Bạn là agent lập trình đang làm việc trong repo openship. Bên dưới là ngữ cảnh phiên: thông báo hook "
       "(nếu có), lịch sử trò chuyện trước đó, rồi nhiệm vụ mới ở cuối.\n\n")


def commit_files(repo):
    log = subprocess.run(["git", "log", "--no-merges", "--name-only", "--format=@@%h|%s", "-n800", "--", "apps", "packages"],
                         cwd=repo, capture_output=True, text=True).stdout
    qf, cur = {}, None
    for ln in log.splitlines():
        if ln.startswith("@@"):
            cur = ln[2:].split("|", 1)[1]
            qf.setdefault(cur, [])
        elif ln.strip() and cur is not None:
            qf[cur].append(ln.strip())
    return qf


def pick_cases(repo, n, seed=7):
    items = okf.collect(Path(repo))
    bench = json.load(open(Path(__file__).with_name("bench_wiki_queries.json")))
    qf = commit_files(repo)
    rnd = random.Random(seed)
    rnd.shuffle(bench)
    cases = []
    for b in bench:
        hits = okf.rank(items, b["q"], k=4, files=qf.get(b["q"]))
        paths = [h["path"] for h in hits]
        gold = [".llmwiki/wiki/" + g for g in b["gold"]]
        inblock = [g for g in gold if g in paths]
        wiki_hits = [p for p in paths if p.startswith(".llmwiki")]
        # chỉ lấy case mà gold nằm trong khối recall và khối có ≥2 trang wiki (không phải trivially 1 lựa chọn)
        if not inblock or len(wiki_hits) < 2:
            continue
        block = HOOK_TPL.format(n=len(items), hits="\n".join(f"    {h['path']}  [{h['type']}]" for h in hits))
        cases.append({"q": b["q"], "gold": inblock, "block": block, "returned": paths})
        if len(cases) >= n:
            break
    return cases


def filler_text(lme_path, chars, seed=3):
    """Hội thoại không liên quan từ LongMemEval (tiếng Anh), tránh mọi đường dẫn .md/.ts."""
    data = json.load(open(lme_path))
    rnd = random.Random(seed)
    out, total = [], 0
    qs = data[:]
    rnd.shuffle(qs)
    for q in qs:
        for sess in q["haystack_sessions"]:
            for t in sess:
                if not isinstance(t, dict):
                    continue
                c = str(t.get("content", "")).strip()
                if not c or re.search(r"\.(md|ts|tsx|py)\b", c):
                    continue
                role = "Người dùng" if t.get("role") == "user" else "Trợ lý"
                out.append(f"{role}: {c}")
                total += len(c)
                if total >= chars:
                    return "\n".join(out)
    return "\n".join(out)


def build_prompt(case, filler, variant, chunk=40000):
    parts = [PRE]
    if variant in ("once", "repeat"):
        parts.append("[SessionStart hook]\n" + case["block"] + "\n")
    if filler:
        parts.append("--- LỊCH SỬ TRÒ CHUYỆN ---\n")
        if variant == "repeat":
            for i in range(0, len(filler), chunk):
                parts.append(filler[i:i + chunk] + "\n")
                parts.append("[UserPromptSubmit hook]\n" + case["block"] + "\n")
        else:
            parts.append(filler + "\n")
    parts.append(TASK.format(q=case["q"]))
    return "\n".join(parts)


def run_one(prompt, model, workdir):
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
    cmd = ["claude", "-p", "--model", model, "--output-format", "json", "--max-turns", "1",
           "--no-session-persistence",
           "--disallowedTools", "Read,Bash,Grep,Glob,Edit,Write,Agent,WebSearch,WebFetch,Task,Skill,ToolSearch"]
    p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=workdir, env=env, timeout=600)
    try:
        j = json.loads(p.stdout)
    except Exception:
        return {"error": (p.stderr or p.stdout)[-400:], "text": "", "tokens": 0}
    u = j.get("usage") or {}
    toks = (u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0))
    return {"text": j.get("result") or "", "tokens": toks, "cost": j.get("total_cost_usd", 0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(Path.home() / "orca/openship"))
    ap.add_argument("--lme", required=True)
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--sizes", default="0,100000,300000")
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default="bench_attention_out.json")
    ap.add_argument("--none-cases", type=int, default=None,
                    help="chỉ chạy biến thể 'none' cho N case đầu (đối chứng rẻ khi prompt rất dài)")
    a = ap.parse_args()
    sizes = [int(x) for x in a.sizes.split(",")]
    cases = pick_cases(a.repo, a.n)
    print(f"{len(cases)} case · gold ∈ khối recall · model={a.model}", file=sys.stderr)
    fillers = {s: (filler_text(a.lme, s) if s else "") for s in sizes}
    workdir = Path(os.environ.get("TMPDIR", "/tmp")) / "bench-attention-nohook"
    workdir.mkdir(parents=True, exist_ok=True)
    jobs = []
    for ci, c in enumerate(cases):
        for s in sizes:
            for v in (("none", "once") if s == 0 else ("none", "once", "repeat")):
                if v == "none" and a.none_cases is not None and ci >= a.none_cases:
                    continue
                jobs.append((ci, s, v, build_prompt(c, fillers[s], v)))
    print(f"{len(jobs)} lời gọi", file=sys.stderr)
    results = []

    def work(job):
        ci, s, v, prompt = job
        r = run_one(prompt, a.model, workdir)
        c = cases[ci]
        txt = r.get("text", "")
        r.update({"case": ci, "size": s, "variant": v, "q": c["q"],
                  "hit": any(g in txt for g in c["gold"]),
                  "any_returned": any(p in txt for p in c["returned"] if p.startswith(".llmwiki"))})
        print(f"  [{ci}] size={s:>6} {v:6} hit={int(r['hit'])} tok={r['tokens']:>7} :: {txt.strip()[:70]!r}", file=sys.stderr)
        return r

    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        results = list(ex.map(work, jobs))
    json.dump({"cases": [{k: v for k, v in c.items() if k != "block"} for c in cases], "results": results},
              open(a.out, "w"), ensure_ascii=False, indent=1)
    # bảng
    # use = đáp án là MỘT trang trong khối recall (model có dùng thứ được bơm không);
    # hit = đáp án đúng trang gold (chặt hơn; khối có ≥2 trang wiki nên có phần đoán).
    print(f"\n{'size':>7} {'variant':8} {'use':>5} {'hit':>5} {'tok TB':>9} {'$ TB':>8}")
    for s in sizes:
        for v in ("none", "once", "repeat"):
            rs = [r for r in results if r["size"] == s and r["variant"] == v and not r.get("error")]
            if not rs:
                continue
            use = sum(r["any_returned"] for r in rs) / len(rs)
            hit = sum(r["hit"] for r in rs) / len(rs)
            tok = sum(r["tokens"] for r in rs) / len(rs)
            cost = sum(r.get("cost", 0) for r in rs) / len(rs)
            print(f"{s:>7} {v:8} {use:5.2f} {hit:5.2f} {tok:9.0f} {cost:8.4f}")
    errs = [r for r in results if r.get("error")]
    if errs:
        print(f"{len(errs)} lỗi, ví dụ: {errs[0]['error'][:200]}")


if __name__ == "__main__":
    main()
