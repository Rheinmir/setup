#!/usr/bin/env python3
"""Cột CHI PHÍ và cột CHẤT LƯỢNG đo trên transcript THẬT của Claude Code.

Chi phí  = ký tự/token hook bơm vào context, tách theo hook (SessionStart recall, docs-gate, ...),
           và số lần bơm lặp lại trong một phiên.
Chất lượng = gợi ý recall (đường dẫn okf-scan trả về đầu phiên) có được agent MỞ THẬT không —
           chỉ đếm tool_use input (Read.file_path, Bash.command, Grep.path...), KHÔNG đếm chữ
           trong hook output (đó là lỗi của okf-scan verify cũ: coverage luôn 1.0).

Dùng: bench_cost_sessions.py <transcript_dir> [--json]
Token ước lượng = ký tự / 3.3 (văn bản Việt+Anh+đường dẫn; sai số ±15%, chỉ để so trước/sau).
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

CPT = 3.3  # ký tự / token


def tool_paths(inp):
    out = []
    if isinstance(inp, dict):
        for k, v in inp.items():
            if isinstance(v, str) and k in ("file_path", "path", "command", "pattern", "notebook_path"):
                out.append(v)
            elif isinstance(v, (dict, list)):
                out += tool_paths(v)
    elif isinstance(inp, list):
        for v in inp:
            out += tool_paths(v)
    return out


def analyze(path: Path) -> dict:
    inj = Counter()          # hookName → ký tự
    inj_n = Counter()        # hookName → số lần
    recall_paths = []        # đường dẫn okf-scan gợi ý
    opened_blob = []         # chuỗi tool input sau khi recall xuất hiện
    seen_recall = False
    prompts = 0
    for ln in path.open(encoding="utf-8", errors="ignore"):
        try:
            r = json.loads(ln)
        except Exception:
            continue
        t = r.get("type")
        if t == "attachment" and (r.get("attachment") or {}).get("type") == "hook_success":
            a = r["attachment"]
            c = a.get("content") or ""
            name = a.get("hookName") or a.get("hookEvent") or "?"
            if "docs-gate" in c:
                name = "docs-gate"
            elif "[recall]" in c:
                name = "recall"
            elif "self-report" in c:
                name = "self-report"
            elif "orca-graph" in c:
                name = "orca-graph"
            inj[name] += len(c)
            inj_n[name] += 1
            if "[recall]" in c and not seen_recall:
                seen_recall = True
                m = re.search(r"nên đọc:\n((?:\s+\S+\s+\[\w+\]\n?)+)", c)
                if m:
                    recall_paths = [x.strip().split()[0] for x in m.group(1).strip().splitlines()]
        elif t == "user":
            cnt = (r.get("message") or {}).get("content")
            if isinstance(cnt, str) or (isinstance(cnt, list) and any(
                    isinstance(x, dict) and x.get("type") == "text" for x in cnt)):
                if not r.get("isMeta"):
                    prompts += 1
        elif t == "assistant" and seen_recall:
            for x in (r.get("message") or {}).get("content") or []:
                if isinstance(x, dict) and x.get("type") == "tool_use":
                    opened_blob += tool_paths(x.get("input"))
    blob = "\n".join(opened_blob)
    wiki = [p for p in recall_paths if not p.startswith(".harness/metrics/memory.jsonl")]
    opened = [p for p in recall_paths if p.split("#")[0] in blob]
    wiki_opened = [p for p in wiki if p in blob]
    return {"session": path.stem[:8], "prompts": prompts,
            "inject_chars": dict(inj), "inject_n": dict(inj_n),
            "inject_tokens_total": round(sum(inj.values()) / CPT),
            "recall_returned": recall_paths, "recall_opened": opened,
            "wiki_returned": wiki, "wiki_opened": wiki_opened}


def main():
    d = Path(sys.argv[1])
    rows = [analyze(p) for p in sorted(d.glob("*.jsonl"))]
    if "--json" in sys.argv:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return
    tot = Counter(); totn = Counter(); prompts = 0
    ret = op = wret = wop = 0
    for r in rows:
        for k, v in r["inject_chars"].items():
            tot[k] += v
        for k, v in r["inject_n"].items():
            totn[k] += v
        prompts += r["prompts"]
        ret += len(r["recall_returned"]); op += len(r["recall_opened"])
        wret += len(r["wiki_returned"]); wop += len(r["wiki_opened"])
    print(f"{len(rows)} phiên · {prompts} prompt")
    print(f"{'hook':14} {'lần':>5} {'ký tự':>9} {'≈token':>8} {'token/phiên':>12}")
    for k, v in tot.most_common():
        print(f"{k:14} {totn[k]:5d} {v:9d} {v/CPT:8.0f} {v/CPT/len(rows):12.0f}")
    print(f"recall gợi ý {ret} mục → mở thật {op} ({op/ret if ret else 0:.2f}); "
          f"riêng wiki: gợi ý {wret} → mở {wop} ({wop/wret if wret else 0:.2f})")


if __name__ == "__main__":
    main()
