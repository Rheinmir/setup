#!/usr/bin/env python3
"""retrieval-eval — đo TRUY HỒI của skill `query` (mảnh 2 của gói L0→L1).

wikieval.py đo ĐÚNG NỘI DUNG (assert trên output). Script này đo thứ khác: query có
TÌM RA đúng trang không (hit@k) và tốn bao nhiêu token — thứ mà không ai đang đo. Nó
song song cấu trúc wikieval (goldens = md frontmatter, baseline + diff, self-test,
--check exit 2 khi hồi quy) nhưng KHÔNG import engine assert của wikieval vì metric khác.

GOLDEN (llmwiki/wiki/sources/evals/retrieval/*.md) — frontmatter:
    question: "..."                      # câu hỏi đưa vào query pipeline
    expected_pages: [slug1, slug2, ...]  # TẬP trang chấp nhận được (case xấu #4: KHÔNG phải 1 trang)

OUTPUT (--outputs file, JSON) — golden-id -> {"pages": [slug thứ tự truy hồi], "tokens": <int>}
    Đây là cái query pipeline THỰC SỰ trả về (L0 baseline hoặc L1), nạp ngoài để engine
    chạy được mà KHÔNG gọi model — giống hợp đồng --outputs của wikieval.

METRIC:
    hit@k  = 1 nếu top-k trang trả về giao với expected_pages (tìm ĐƯỢC ít nhất 1 trang chấp
             nhận được) — metric CHỐNG-BRITTLE, vì expected_pages là tập (case xấu #4).
    recall = |set(pages) ∩ expected| / |expected|   (phụ, khi câu hỏi cần nhiều trang)
    tokens = chi phí token pipeline báo (thấp hơn = tốt hơn — mục tiêu progressive disclosure)

CASE XẤU #1 (mạ vàng eval) chốt bằng CODE: HARD-CAP 30 golden — quá 30 thì script TỪ CHỐI
chạy, buộc giữ bộ eval mỏng thay vì phình thành dự án nghiên cứu.

CLI:
    retrieval-eval.py --self-test
    retrieval-eval.py --outputs out.json [--k 5]
    retrieval-eval.py --outputs out.json --write-baseline
    retrieval-eval.py --outputs out.json --check      # exit 2 nếu hit@k tụt hoặc token phình
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVALS_DIR = REPO_ROOT / "llmwiki" / "wiki" / "sources" / "evals" / "retrieval"
DEFAULT_BASELINE = REPO_ROOT / "harness" / "metrics" / "retrieval-baseline.json"
SCHEMA = "retrieval-baseline/v1"
HARD_CAP = 30            # case xấu #1: cấm phình eval — quá 30 golden thì từ chối
DEFAULT_K = 5
TOKEN_REL_EPS = 0.15     # ngưỡng MỀM: token chỉ là hồi quy khi phình > +15% so baseline/golden.
                         # Wiki lớn lên tự nhiên (thêm/sửa trang) nhích token vài % → KHÔNG spam;
                         # phình đột biến (>15%, dấu hiệu context-bloat) mới đỏ. hit@k tụt vẫn là
                         # hồi quy CỨNG tuyệt đối (không nới) — đó mới là mất khả năng truy hồi.
SKIP_BASENAMES = {"README.md", "index.md", "_template.md", "log.md"}

FRONTMATTER = "---"


def _require_yaml():
    try:
        import yaml  # noqa
    except Exception:
        sys.exit("[retrieval-eval] cần PyYAML (pip install pyyaml)")


def _parse_frontmatter(text: str):
    if not text.startswith(FRONTMATTER):
        return None
    end = text.find("\n" + FRONTMATTER, len(FRONTMATTER))
    if end == -1:
        return None
    import yaml
    try:
        data = yaml.safe_load(text[len(FRONTMATTER):end])
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def load_goldens(evals_dir: Path):
    _require_yaml()
    base = Path(evals_dir)
    if not base.is_dir():
        sys.exit(f"[retrieval-eval] evals dir not found: {base}")
    out, seen = [], {}
    for p in sorted(base.rglob("*.md")):
        if p.name in SKIP_BASENAMES:
            continue
        data = _parse_frontmatter(p.read_text(encoding="utf-8"))
        if not data or "question" not in data or "expected_pages" not in data:
            continue
        gid = str(data.get("id") or p.stem)
        if gid in seen:
            sys.exit(f"[retrieval-eval] duplicate golden id '{gid}': {seen[gid]} and {p}")
        exp = data.get("expected_pages") or []
        if not isinstance(exp, list) or not exp:
            sys.exit(f"[retrieval-eval] golden '{gid}': expected_pages phải là list không rỗng (một TẬP)")
        seen[gid] = p
        out.append({"id": gid, "path": str(p), "question": data.get("question"),
                    "expected": {str(s).strip() for s in exp}})
    # CASE XẤU #1: hard-cap — chốt kỷ luật bằng code, không nới
    if len(out) > HARD_CAP:
        sys.exit(f"[retrieval-eval] {len(out)} golden > cap {HARD_CAP}. Giữ eval MỎNG (case xấu #1: "
                 f"mạ vàng → tê liệt). Gộp/bỏ golden dư trước khi chạy.")
    return out


def load_outputs(path: str):
    if not path:
        return {}
    p = Path(path)
    if not p.is_file():
        sys.exit(f"[retrieval-eval] --outputs file not found: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        sys.exit("[retrieval-eval] --outputs phải là JSON object: golden-id -> {pages, tokens}")
    return data


def score_golden(g, output, k):
    """output = {"pages":[...], "tokens":int} hoặc None nếu chưa có candidate."""
    if not output:
        return {"id": g["id"], "hit": None, "recall": None, "tokens": None, "decided": False}
    pages = [str(s).strip() for s in (output.get("pages") or [])]
    topk = set(pages[:k])
    exp = g["expected"]
    hit = 1 if topk & exp else 0                       # chống-brittle: trúng ≥1 trang chấp nhận
    recall = round(len(set(pages) & exp) / len(exp), 4) if exp else None
    toks = output.get("tokens")
    toks = toks if isinstance(toks, int) else None
    return {"id": g["id"], "hit": hit, "recall": recall, "tokens": toks, "decided": True}


def run(goldens, outputs, k):
    return [score_golden(g, outputs.get(g["id"]), k) for g in goldens]


# ───────────── baseline + diff ─────────────

def build_baseline(results, evals_dir, k):
    decided = [r for r in results if r["decided"]]
    return {
        "schema": SCHEMA, "generated_by": "harness/scripts/retrieval-eval.py",
        "generated_at": date.today().isoformat(), "k": k,
        "evals_dir": str(Path(evals_dir).resolve().relative_to(REPO_ROOT)) if str(evals_dir).startswith(str(REPO_ROOT)) else str(evals_dir),
        "summary": {"goldens": len(results), "decided": len(decided),
                    "hits": sum(r["hit"] for r in decided) if decided else 0,
                    "total_tokens": sum(r["tokens"] for r in decided if isinstance(r["tokens"], int))},
        "goldens": {r["id"]: {"hit": r["hit"], "recall": r["recall"], "tokens": r["tokens"]} for r in results},
    }


def diff_against_baseline(baseline, results):
    """Hồi quy CỨNG = hit@k tụt (1→0) HOẶC token phình > +TOKEN_REL_EPS so baseline. Token tăng
    trong ngưỡng mềm chỉ WARN (wiki lớn lên hợp lệ, không đỏ CI). Token GIẢM = cải tiến (ok)."""
    cur = {r["id"]: r for r in results}
    base = baseline.get("goldens", {})
    regressions, notes = [], []
    for gid in sorted(base):
        b, c = base[gid], cur.get(gid)
        if c is None or not c["decided"]:
            regressions.append((gid, "golden mất/không có output (coverage tụt)"))
            continue
        if b.get("hit") == 1 and c["hit"] != 1:
            regressions.append((gid, f"hit@k 1 -> {c['hit']} (không còn tìm ra trang đúng)"))
        bt, ct = b.get("tokens"), c["tokens"]
        if isinstance(bt, int) and isinstance(ct, int) and ct > bt:
            limit = bt * (1 + TOKEN_REL_EPS)
            pct = (ct - bt) / bt * 100 if bt else 0
            if ct > limit:
                regressions.append((gid, f"token {bt} -> {ct} (phình +{pct:.0f}% > +{TOKEN_REL_EPS*100:.0f}% mềm)"))
            else:
                notes.append((gid, f"token {bt} -> {ct} (+{pct:.0f}%, trong ngưỡng mềm — chỉ cảnh báo)"))
    for gid in sorted(cur):
        if gid not in base:
            notes.append((gid, "golden mới (chưa có trong baseline)"))
    return regressions, notes


def print_report(results, k):
    decided = [r for r in results if r["decided"]]
    hits = sum(r["hit"] for r in decided) if decided else 0
    toks = sum(r["tokens"] for r in decided if isinstance(r["tokens"], int))
    print(f"RetrievalEval — {len(results)} goldens | decided: {len(decided)} | k={k}")
    width = max((len(r["id"]) for r in results), default=4)
    for r in sorted(results, key=lambda x: x["id"]):
        if not r["decided"]:
            print(f"  ----  {r['id']:<{width}}  (chưa có output)")
            continue
        mark = "HIT " if r["hit"] else "MISS"
        print(f"  {mark}  {r['id']:<{width}}  recall={r['recall']}  tokens={r['tokens']}")
    print(f"Summary: hit@{k} {hits}/{len(decided)} | tokens {toks}")


# ───────────── self-test (tất định, không model) ─────────────

def self_test(evals_dir, k):
    """Mỗi golden: dùng CHÍNH expected_pages làm output → hit@k PHẢI = 1 (trang kỳ vọng
    hiển nhiên chứa trang kỳ vọng). Chứng minh scorer coherent, tất định, không gọi model —
    đúng tinh thần self-test của wikieval."""
    goldens = load_goldens(evals_dir)
    if not goldens:
        print("[retrieval-eval] self-test: 0 golden — chưa có gì để kiểm.")
        return 1
    bad = []
    for g in goldens:
        synthetic = {"pages": sorted(g["expected"]), "tokens": 0}
        r = score_golden(g, synthetic, k)
        if r["hit"] != 1 or r["recall"] != 1.0:
            bad.append((g["id"], r))
    if bad:
        for gid, r in bad:
            print(f"  FAIL  {gid}: hit={r['hit']} recall={r['recall']} (expected hit=1 recall=1.0)")
        print(f"[retrieval-eval] self-test FAIL: {len(bad)}/{len(goldens)}")
        return 2
    print(f"[retrieval-eval] self-test OK: {len(goldens)}/{len(goldens)} golden coherent (cap {HARD_CAP}).")
    return 0


def main():
    ap = argparse.ArgumentParser(description="RetrievalEval — đo hit@k + token của query pipeline.")
    ap.add_argument("--evals-dir", default=str(DEFAULT_EVALS_DIR))
    ap.add_argument("--outputs", default=None)
    ap.add_argument("--baseline", default=str(DEFAULT_BASELINE))
    ap.add_argument("--k", type=int, default=DEFAULT_K)
    ap.add_argument("--write-baseline", action="store_true")
    ap.add_argument("--check", action="store_true", help="so baseline; exit 2 nếu hồi quy")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test(args.evals_dir, args.k))

    goldens = load_goldens(args.evals_dir)
    outputs = load_outputs(args.outputs)
    results = run(goldens, outputs, args.k)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_report(results, args.k)

    if args.write_baseline:
        Path(args.baseline).parent.mkdir(parents=True, exist_ok=True)
        Path(args.baseline).write_text(
            json.dumps(build_baseline(results, args.evals_dir, args.k), ensure_ascii=False, indent=2),
            encoding="utf-8")
        print(f"[retrieval-eval] baseline -> {args.baseline}")

    if args.check:
        bp = Path(args.baseline)
        if not bp.is_file():
            sys.exit(f"[retrieval-eval] --check: chưa có baseline {bp} (chạy --write-baseline trước)")
        baseline = json.loads(bp.read_text(encoding="utf-8"))
        regressions, notes = diff_against_baseline(baseline, results)
        for gid, why in notes:
            print(f"  note: {gid}: {why}")
        if regressions:
            for gid, why in regressions:
                print(f"  REGRESSION: {gid}: {why}")
            sys.exit(2)
        print("[retrieval-eval] --check OK: không hồi quy hit@k, token không phình.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
