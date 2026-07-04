#!/usr/bin/env python3
"""skill-resolve-eval — golden retrieval cho SKILL router (tinh thần SkillResolve-Bench, GH#13).

VÌ SAO: với 74 skill và nhiều cặp CÙNG-NĂNG-LỰC (tour-guide vs tour-guide-supademo,
design-taste-frontend vs -v1, raise-issue vs orca-issue…), router dễ chọn nhầm. Thế
giới đo việc này bằng SkillResolve-Bench. Script này là bản mini nội bộ: một tập câu
golden → skill ĐÚNG (tập chấp nhận được), chạy qua CHÍNH engine BM25 của
build-skill-search.py, chấm hit@1 / hit@3, và CHẶN HỒI QUY qua baseline.

Song song cấu trúc retrieval-eval.py (goldens = md frontmatter, baseline + diff,
--check exit 2 khi hồi quy, self-test) nhưng KHÁC ở chỗ engine chạy INLINE — BM25 tất
định nên không cần nạp --outputs ngoài như retrieval-eval (metric truy hồi wiki cần
model). Ở đây câu → skill là thuần lexical, chạy thẳng.

GOLDEN (llmwiki/wiki/sources/evals/skill-resolve/*.md) — frontmatter:
    query: "..."               # câu người dùng gõ / mô tả việc
    expected: [skill, ...]     # TẬP skill chấp nhận được (chống brittle: cặp nhập nhằng
                               # có thể liệt kê cả 2, hoặc chỉ skill đúng nếu phải phân biệt)

METRIC:
    hit@1 = 1 nếu skill top-1 ∈ expected      (phân giải ĐÚNG ngay lựa chọn đầu)
    hit@3 = 1 nếu top-3 giao expected          (skill đúng ít nhất lọt short-list)

BASELINE (cạnh goldens: baseline.json) — {schema, k, totals:{hit1,hit3,n}, per:{gid:{hit1,hit3}}}.
    --check exit 2 nếu hit@1 HOẶC hit@3 tổng TỤT so baseline (thêm case mới không tự fail:
    case chưa có trong baseline được bỏ qua khỏi phép so tụt, chỉ cảnh báo "cần --write-baseline").

CLI:
    skill-resolve-eval.py --self-test
    skill-resolve-eval.py                 # chạy + in bảng
    skill-resolve-eval.py --write-baseline
    skill-resolve-eval.py --check         # exit 2 nếu hồi quy
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GOLDENS_DIR = REPO / "llmwiki" / "wiki" / "sources" / "evals" / "skill-resolve"
BASELINE = GOLDENS_DIR / "baseline.json"
SKILLS_DIR = REPO / "skills"
SEARCH_PY = REPO / "fdk" / "tools" / "build-skill-search.py"
SCHEMA = "skill-resolve-baseline/v1"
HARD_CAP = 40          # chống mạ vàng eval: quá 40 golden thì từ chối chạy
DEFAULT_K = 3
FRONTMATTER = "---"


def _load_search():
    spec = importlib.util.spec_from_file_location("skill_search", SEARCH_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _require_yaml():
    try:
        import yaml  # noqa
    except Exception:
        sys.exit("[skill-resolve-eval] cần PyYAML (pip install pyyaml)")


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


def load_goldens():
    _require_yaml()
    if not GOLDENS_DIR.is_dir():
        sys.exit(f"[skill-resolve-eval] goldens dir không có: {GOLDENS_DIR}")
    out, seen = [], {}
    for p in sorted(GOLDENS_DIR.rglob("*.md")):
        if p.name in ("README.md", "index.md", "_template.md"):
            continue
        data = _parse_frontmatter(p.read_text(encoding="utf-8"))
        if not data or "query" not in data or "expected" not in data:
            continue
        gid = str(data.get("id") or p.stem)
        if gid in seen:
            sys.exit(f"[skill-resolve-eval] golden id trùng '{gid}': {seen[gid]} và {p}")
        seen[gid] = p
        exp = data["expected"]
        exp = [exp] if isinstance(exp, str) else list(exp)
        out.append({"id": gid, "query": str(data["query"]), "expected": exp})
    if not out:
        sys.exit(f"[skill-resolve-eval] không tìm thấy golden hợp lệ trong {GOLDENS_DIR}")
    if len(out) > HARD_CAP:
        sys.exit(f"[skill-resolve-eval] {len(out)} golden > HARD_CAP {HARD_CAP} — "
                 f"giữ bộ eval mỏng, đừng phình thành dự án nghiên cứu.")
    return out


def run(k=DEFAULT_K):
    mod = _load_search()
    index = mod.build_index(str(SKILLS_DIR))
    per, t1, t3 = {}, 0, 0
    for g in load_goldens():
        hits = [h[0] for h in mod.score_query(index, g["query"], k)]
        exp = set(g["expected"])
        h1 = 1 if hits[:1] and hits[0] in exp else 0
        h3 = 1 if set(hits[:k]) & exp else 0
        per[g["id"]] = {"hit1": h1, "hit3": h3, "top": hits[:k]}
        t1 += h1
        t3 += h3
    n = len(per)
    return {"k": k, "totals": {"hit1": t1, "hit3": t3, "n": n}, "per": per}


def _print(res):
    n = res["totals"]["n"]
    print(f"\n  skill-resolve golden — {n} case (k={res['k']})")
    for gid, r in sorted(res["per"].items()):
        m1 = "✓" if r["hit1"] else "·"
        m3 = "✓" if r["hit3"] else "✗"
        print(f"   h@1 {m1}  h@3 {m3}  {gid:28} → {', '.join(r['top'])}")
    print(f"\n   hit@1 = {res['totals']['hit1']}/{n}   hit@3 = {res['totals']['hit3']}/{n}")


def cmd_write(res):
    payload = {"schema": SCHEMA, "k": res["k"], "totals": res["totals"],
               "per": {g: {"hit1": r["hit1"], "hit3": r["hit3"]}
                       for g, r in res["per"].items()}}
    BASELINE.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"✓ baseline ghi → {BASELINE.relative_to(REPO)}  "
          f"(hit@1 {res['totals']['hit1']}/{res['totals']['n']}, "
          f"hit@3 {res['totals']['hit3']}/{res['totals']['n']})")


def cmd_check(res):
    if not BASELINE.exists():
        sys.exit("✗ chưa có baseline — chạy `--write-baseline` trước.")
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    regress = []
    for gid, br in base.get("per", {}).items():
        cur = res["per"].get(gid)
        if cur is None:
            regress.append(f"{gid}: MẤT khỏi bộ golden")
            continue
        if cur["hit1"] < br["hit1"]:
            regress.append(f"{gid}: hit@1 {br['hit1']}→{cur['hit1']} (top={cur['top']})")
        if cur["hit3"] < br["hit3"]:
            regress.append(f"{gid}: hit@3 {br['hit3']}→{cur['hit3']} (top={cur['top']})")
    new = [g for g in res["per"] if g not in base.get("per", {})]
    _print(res)
    if new:
        print(f"\n  ⚠ {len(new)} case mới chưa vào baseline: {', '.join(new)} "
              f"→ chạy --write-baseline để chốt.")
    if regress:
        print("\n✗ HỒI QUY skill-resolve:")
        for r in regress:
            print(f"    - {r}")
        return 2
    print("\n✓ không hồi quy so baseline.")
    return 0


def self_test():
    # engine load được + mọi golden có expected là skill THẬT trên đĩa.
    mod = _load_search()
    index = mod.build_index(str(SKILLS_DIR))
    on_disk = {d.name for d in SKILLS_DIR.iterdir() if (d / "SKILL.md").exists()}
    for g in load_goldens():
        for s in g["expected"]:
            assert s in on_disk, f"golden {g['id']}: expected '{s}' không phải skill thật"
        assert mod.score_query(index, g["query"], 3) is not None
    print("✓ self-test passed")
    return 0


def main():
    ap = argparse.ArgumentParser(prog="skill-resolve-eval.py")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--write-baseline", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--k", type=int, default=DEFAULT_K)
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    res = run(a.k)
    if a.write_baseline:
        cmd_write(res)
        return 0
    if a.check:
        return cmd_check(res)
    _print(res)
    return 0


if __name__ == "__main__":
    sys.exit(main())
