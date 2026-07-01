#!/usr/bin/env python3
"""query-proxy — bản TẤT ĐỊNH mô phỏng chiến lược truy hồi của skill `query`, để
retrieval-eval có baseline tái-lập-được mà KHÔNG gọi model (đúng triết lý wikieval).

Bối cảnh: query production là AGENTIC (model theo skill tự Read) → phi-tất-định, đo baseline
trên nó thì nhiễu (case xấu #2). Proxy này tách phần TẤT ĐỊNH — *chiến lược đọc trang* — ra
để đo token của chiến lược, không đo tính khí model:

  L0 (hiện tại, "read each page in full"):  xếp trang theo keyword khớp trong TOÀN VĂN, rồi
      MỞ FULL MỌI trang khớp. Không lọc → đọc nhiều → token cao. Đây là hành vi L0 thật.
  L1 (progressive disclosure 3 tầng):        tầng-1 quét RẺ (chỉ title + heading, ~1 dòng/trang)
      để xếp hạng; tầng-2 chỉ MỞ FULL top-N; (tầng-3 wikilinks bỏ qua ở proxy). Đọc ít → token thấp.

Token ước tính = len(text)//4. pages_hit = stem trang (khớp expected_pages của golden theo stem).

Output: JSON map golden-id -> {"pages":[stem...], "tokens":int} — nạp thẳng vào
retrieval-eval.py --outputs. Cùng bộ golden, cùng wiki → cùng kết quả (tất định).

CLI:
  query-proxy.py --mode L0|L1 [--topn 3] [--wiki DIR ...] [--evals-dir DIR] --out FILE
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVALS = REPO_ROOT / "llmwiki" / "wiki" / "sources" / "evals" / "retrieval"
DEFAULT_WIKIS = [REPO_ROOT / "fdk" / "wiki", REPO_ROOT / "llmwiki" / "wiki"]
SKIP = {"README.md", "index.md", "log.md", "_template.md"}
STOP = set("the and cho của là ở ra vào thế nào gì sao khi có không một với để và làm được ntn "
           "how what why is are do the a an of to in for".split())
WORD = re.compile(r"[0-9A-Za-zÀ-ỹ]+", re.UNICODE)


def _tokens(text: str) -> int:
    return len(text) // 4


def _terms(q: str):
    return {w.lower() for w in WORD.findall(q or "") if len(w) >= 4 and w.lower() not in STOP}


def _headings(text: str) -> str:
    """title (frontmatter) + các dòng heading markdown — 'chỉ mục' rẻ cho tầng-1."""
    out = []
    m = re.search(r'(?m)^title:\s*"?(.+?)"?\s*$', text)
    if m:
        out.append(m.group(1))
    out += re.findall(r"(?m)^#{1,3}\s+(.+)$", text)
    return " ".join(out)


def load_pages(wikis):
    pages = []
    for w in wikis:
        w = Path(w)
        if not w.is_dir():
            continue
        for p in sorted(w.rglob("*.md")):
            if p.name in SKIP or "/draft/" in str(p) or "/evals/" in str(p):
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            pages.append({"stem": p.stem, "full": text, "head": _headings(text),
                          "tokens_full": _tokens(text)})
    # trùng stem giữ bản dài hơn (nội dung thật hơn seed)
    best = {}
    for pg in pages:
        cur = best.get(pg["stem"])
        if cur is None or pg["tokens_full"] > cur["tokens_full"]:
            best[pg["stem"]] = pg
    return list(best.values())


def _score(terms, hay: str) -> int:
    low = hay.lower()
    return sum(1 for t in terms if t in low)


def retrieve_L0(question, pages):
    terms = _terms(question)
    matched = [(pg, _score(terms, pg["full"])) for pg in pages]
    matched = [(pg, s) for pg, s in matched if s > 0]
    matched.sort(key=lambda x: (-x[1], x[0]["stem"]))
    # L0: MỞ FULL mọi trang khớp
    stems = [pg["stem"] for pg, _ in matched]
    tokens = sum(pg["tokens_full"] for pg, _ in matched)
    return {"pages": stems, "tokens": tokens}


def retrieve_L1(question, pages, topn):
    terms = _terms(question)
    # tầng-1: quét RẺ chỉ trên title+heading; token quét ~ 1 dòng chỉ-mục / trang
    # tầng-1 = ripgrep trên NỘI DUNG: xếp hạng bằng ĐỘ PHỦ TERM (cùng hàm _score với L0 — rg
    # cho biết trang nào chứa term nào mà KHÔNG nạp full vào context). Deferred-read: chỉ top-N
    # mới đọc full ở tầng-2. Vì cùng thứ hạng với L0, top-N ⊆ thứ tự L0 → recall được giữ.
    # Chi phí quét ~ vài dòng khớp/trang mà rg trả về, không phải cả trang.
    scan_tokens = 0
    ranked = []
    for pg in pages:
        hit_lines = sum(1 for ln in pg["full"].splitlines() if _score(terms, ln) > 0)
        scan_tokens += min(hit_lines, 12) * 20
        ranked.append((pg, _score(terms, pg["full"])))   # cùng ranking L0, khác ở chỗ đọc full
    ranked.sort(key=lambda x: (-x[1], x[0]["stem"]))
    top = [pg for pg, s in ranked if s > 0][:topn]
    # tầng-2: chỉ đọc FULL top-N
    tokens = scan_tokens + sum(pg["tokens_full"] for pg in top)
    return {"pages": [pg["stem"] for pg in top], "tokens": tokens}


def load_questions(evals_dir):
    import yaml
    base = Path(evals_dir)
    out = []
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


def main():
    ap = argparse.ArgumentParser(description="query-proxy — chiến lược truy hồi tất định (baseline).")
    ap.add_argument("--mode", choices=["L0", "L1"], required=True)
    ap.add_argument("--topn", type=int, default=3)
    ap.add_argument("--wiki", nargs="*", default=[str(w) for w in DEFAULT_WIKIS])
    ap.add_argument("--evals-dir", default=str(DEFAULT_EVALS))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    pages = load_pages(args.wiki)
    if not pages:
        sys.exit("[query-proxy] không tìm thấy trang wiki nào.")
    qs = load_questions(args.evals_dir)
    result = {}
    for gid, q in qs:
        result[gid] = retrieve_L0(q, pages) if args.mode == "L0" else retrieve_L1(q, pages, args.topn)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    tot = sum(v["tokens"] for v in result.values())
    print(f"[query-proxy] mode={args.mode} qs={len(result)} total_tokens={tot} -> {args.out}")


if __name__ == "__main__":
    sys.exit(main())
