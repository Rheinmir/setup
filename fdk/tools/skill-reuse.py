#!/usr/bin/env python3
"""skill-reuse — SWH v1.1 Reuse Layer mức local MVP (PRD §22–27; concept [[solid-what-how]] mục Reuse Layer).

Skill mới kế thừa phần đã chuẩn hoá qua catalog pattern/template thay vì viết lại từ đầu:
  search   lọc CỨNG (kind=template · status=active · effect_class không rộng hơn yêu cầu) TRƯỚC,
           rồi mới xếp hạng theo tag — mẫu phổ biến mà sai effect contract không bao giờ thắng (RE-05)
  resolve  pin sha256 base + dependency closure; cycle/độ sâu > 3 → lỗi có đường tham chiếu (RE-09)
  render   thay placeholder ${...} theo schema typed — KHÔNG eval, KHÔNG shell; giá trị chèn được
           heading/frontmatter/${ bị từ chối; còn slot chưa điền → UNRESOLVED_SLOT (RE-06)
  verify   recipe đã pin còn khớp bytes hiện tại không (RE-04) — swh-lint gọi hàm này

Catalog: fdk/skill-catalog/catalog.json (framework-only). Seed = limited_evidence, không claim tiết kiệm.

Dùng:
  python3 fdk/tools/skill-reuse.py search --desc "đọc PRD sinh ticket" [--effect file_only]
  python3 fdk/tools/skill-reuse.py render --from evidence-to-artifact --params p.json [--out SKILL.md]
  python3 fdk/tools/skill-reuse.py verify <skill>
  python3 fdk/tools/skill-reuse.py episode <skill> --decision reuse --minutes 42 --event-id <uuid>
  python3 fdk/tools/skill-reuse.py report      # median/p75, benefit_unproven khi thiếu baseline
"""
import argparse
import hashlib
import json
import math
import statistics
import time
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CATALOG_DIR = REPO / "fdk" / "skill-catalog"
EFFECT_RANK = {"none": 0, "file_only": 1, "external": 2}
MAX_DEPTH = 3
SLOT_RE = re.compile(r"\$\{(\w+)\}")


class ReuseError(Exception):
    def __init__(self, code, detail=""):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail = code, detail


def load_catalog(cat_dir=CATALOG_DIR):
    try:
        d = json.loads((Path(cat_dir) / "catalog.json").read_text(encoding="utf-8"))
    except Exception as e:
        raise ReuseError("CATALOG_UNAVAILABLE", str(e))
    if d.get("schema_version") != "swh.reuse/1":
        raise ReuseError("CATALOG_UNAVAILABLE", "schema_version khác swh.reuse/1")
    return {a["asset_id"]: a for a in d["assets"]}


def _words(s):
    return set(re.findall(r"[a-zà-ỹ0-9]+", (s or "").lower()))


def search(desc, effect="file_only", assets=None, k=3):
    """Lọc cứng trước, xếp hạng sau. Trả tối đa k {asset_id, score, gaps}."""
    assets = assets if assets is not None else load_catalog()
    want = EFFECT_RANK.get(effect, 1)
    words, hits = _words(desc), []
    for a in assets.values():
        if a.get("kind") != "template" or a.get("status") != "active":
            continue
        if EFFECT_RANK.get(a.get("effect_class"), 9) > want:      # effect rộng hơn yêu cầu → loại
            continue
        tags = set(a.get("problem_tags", []))
        score = len(tags & words)
        hits.append({"asset_id": a["asset_id"], "score": score, "applicable_when": a.get("applicable_when", ""),
                     "gaps": sorted(tags - words)[:5]})
    return sorted(hits, key=lambda h: (-h["score"], h["asset_id"]))[:k]


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def resolve(base_id, assets=None, cat_dir=CATALOG_DIR):
    """Pin closure của base: {asset_id: {version, path, sha256}}; cycle / độ sâu > MAX_DEPTH → lỗi."""
    assets = assets if assets is not None else load_catalog(cat_dir)
    lock = {}

    def walk(aid, path):
        if aid in path:
            raise ReuseError("DEPENDENCY_CYCLE", " → ".join(path + [aid]))
        if len(path) > MAX_DEPTH:
            raise ReuseError("DEPTH_LIMIT", " → ".join(path + [aid]))
        a = assets.get(aid)
        if a is None:
            raise ReuseError("MISSING_DEPENDENCY", " → ".join(path + [aid]))
        if a.get("status") in ("quarantined", "retired"):
            raise ReuseError("REVOKED_ASSET", aid)
        lock[aid] = {"version": a["version"], "path": a["path"], "sha256": _sha(Path(cat_dir) / a["path"])}
        for dep in a.get("depends", []):
            walk(dep, path + [aid])

    walk(base_id, [])
    closure = hashlib.sha256(json.dumps(lock, sort_keys=True).encode()).hexdigest()
    return {"assets": lock, "closure_hash": closure, "lock_status": "resolved"}


def render(text, params, schema):
    """Thay ${slot} theo schema typed. Không eval. Lỗi: INVALID_PARAMETER · UNRESOLVED_SLOT."""
    vals = {}
    for key, spec in schema.items():
        v = params.get(key, spec.get("default"))
        if v is None:
            if spec.get("required"):
                raise ReuseError("INVALID_PARAMETER", f"{key}: thiếu")
            continue
        if spec.get("type") == "int":
            if isinstance(v, bool) or not isinstance(v, int):
                raise ReuseError("INVALID_PARAMETER", f"{key}: phải là số nguyên")
            if ("min" in spec and v < spec["min"]) or ("max" in spec and v > spec["max"]):
                raise ReuseError("INVALID_PARAMETER", f"{key}: ngoài [{spec.get('min')}, {spec.get('max')}]")
        else:
            if not isinstance(v, str):
                raise ReuseError("INVALID_PARAMETER", f"{key}: phải là chuỗi")
            if "enum" in spec and v not in spec["enum"]:
                raise ReuseError("INVALID_PARAMETER", f"{key}: ngoài {spec['enum']}")
            if "${" in v or ("\n" in v and not spec.get("multiline")):
                raise ReuseError("INVALID_PARAMETER", f"{key}: chứa ${{ hoặc xuống dòng")
            if any(ln.lstrip().startswith(("#", "---")) for ln in v.splitlines()):
                raise ReuseError("INVALID_PARAMETER", f"{key}: không được chèn heading/frontmatter")
        vals[key] = str(v)
    unknown = sorted(set(params) - set(schema))
    if unknown:
        raise ReuseError("INVALID_PARAMETER", f"tham số lạ: {unknown}")
    out = SLOT_RE.sub(lambda m: vals.get(m.group(1), m.group(0)), text)   # một lượt — không render đệ quy
    left = sorted(set(SLOT_RE.findall(out)))
    if left:
        raise ReuseError("UNRESOLVED_SLOT", left)
    return out


def recipe_path(skill, cat_dir=CATALOG_DIR):
    return Path(cat_dir) / "recipes" / f"{skill}.recipe.json"


def verify(skill, cat_dir=CATALOG_DIR):
    """[] nếu recipe (nếu có) khớp bytes hiện tại; ngược lại list lỗi (RE-04)."""
    p = recipe_path(skill, cat_dir)
    if not p.exists():
        return []
    r = json.loads(p.read_text(encoding="utf-8"))
    if r.get("decision") in ("scratch", "catalog_unavailable"):
        return []
    lock = r.get("lock") or {}
    if lock.get("lock_status") != "resolved":
        return [f"recipe {p.name}: lock_status={lock.get('lock_status')} — chưa được phát hành"]
    errs = []
    for aid, pin in lock.get("assets", {}).items():
        f = Path(cat_dir) / pin["path"]
        if not f.exists():
            errs.append(f"{aid}: file pin không còn ({pin['path']})")
        elif _sha(f) != pin["sha256"]:
            errs.append(f"{aid}@{pin['version']}: HASH_MISMATCH — bytes đổi mà version giữ nguyên")
    return errs


def write_recipe(skill, decision, candidates, reason="", base=None, params=None, cat_dir=CATALOG_DIR):
    """Ghi reuse_decision (+ lock khi reuse). Luôn ghi — scratch cũng là quyết định có lý do (§22.1)."""
    rec = {"schema_version": "swh.reuse/1", "recipe_id": skill, "decision": decision,
           "candidates": candidates, "reason": reason}
    if decision == "reuse":
        rec.update(base=base, parameters=params or {}, lock=resolve(base, cat_dir=cat_dir))
    p = recipe_path(skill, cat_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


LEDGER = REPO / "harness" / "metrics" / "skill-authoring.jsonl"


def breakeven(F, scratch, reuse, maint=0):
    """Số lần dùng để hòa vốn (PRD §22.2): None khi reuse ≥ scratch — không có điểm hòa vốn hữu hạn."""
    return None if reuse >= scratch else math.ceil((F + maint) / (scratch - reuse))


def episode(skill, decision, minutes, outcome, event_id, ledger=LEDGER):
    """Ghi 1 episode authoring (idempotent theo event_id — ghi lại không đếm hai lần). Không lưu prompt/nguồn."""
    ledger.parent.mkdir(parents=True, exist_ok=True)
    seen = {json.loads(l).get("event_id") for l in ledger.read_text(encoding="utf-8").splitlines() if l.strip()} \
        if ledger.exists() else set()
    if event_id in seen:
        return False
    rec = {"event_id": event_id, "skill": skill, "decision": decision, "minutes": float(minutes), "outcome": outcome,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return True


def report(ledger=LEDGER):
    """median/p75/n theo decision, TÍNH CẢ episode thất bại. Thiếu baseline scratch → benefit_unproven."""
    rows = [json.loads(l) for l in ledger.read_text(encoding="utf-8").splitlines() if l.strip()] if ledger.exists() else []
    by = {}
    for r in rows:
        by.setdefault(r["decision"], []).append(r["minutes"])
    stats = {}
    for dec, xs in by.items():
        xs = sorted(xs)
        stats[dec] = {"n": len(xs), "median": statistics.median(xs), "p75": xs[min(len(xs) - 1, math.ceil(0.75 * len(xs)) - 1)],
                      "failed": sum(1 for r in rows if r["decision"] == dec and r["outcome"] != "succeeded")}
    if "scratch" not in stats or "reuse" not in stats:
        verdict = "benefit_unproven"          # thiếu baseline cùng cohort → không tự báo tiết kiệm
    else:
        verdict = "observed_lower" if stats["reuse"]["median"] < stats["scratch"]["median"] else "observed_not_lower"
    return {"stats": stats, "verdict": verdict, "note": "mẫu nhỏ không chứng minh nhân quả (PRD §27.1)"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("--desc", required=True); s.add_argument("--effect", default="file_only")
    r = sub.add_parser("render"); r.add_argument("--from", dest="base", required=True)
    r.add_argument("--params", required=True); r.add_argument("--out")
    v = sub.add_parser("verify"); v.add_argument("skill")
    e = sub.add_parser("episode", help="ghi 1 episode authoring vào ledger")
    e.add_argument("skill"); e.add_argument("--decision", required=True,
                   choices=["reuse", "compose", "scratch", "catalog_unavailable"])
    e.add_argument("--minutes", type=float, required=True); e.add_argument("--outcome", default="succeeded")
    e.add_argument("--event-id", required=True)
    sub.add_parser("report", help="median/p75 theo decision + verdict benefit")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "search":
            print(json.dumps(search(a.desc, a.effect), ensure_ascii=False, indent=2))
        elif a.cmd == "render":
            assets = load_catalog()
            base = assets[a.base]
            text = (CATALOG_DIR / base["path"]).read_text(encoding="utf-8")
            out = render(text, json.loads(Path(a.params).read_text(encoding="utf-8")), base.get("params", {}))
            (Path(a.out).write_text(out, encoding="utf-8") if a.out else sys.stdout.write(out))
        elif a.cmd == "episode":
            print("✓ ghi" if episode(a.skill, a.decision, a.minutes, a.outcome, a.event_id) else "· đã có event_id này")
        elif a.cmd == "report":
            print(json.dumps(report(), ensure_ascii=False, indent=2))
        elif a.cmd == "verify":
            errs = verify(a.skill)
            print("\n".join(errs) or f"✓ {a.skill}: recipe khớp (hoặc không có recipe)")
            return 1 if errs else 0
    except ReuseError as e:
        print(f"✗ {e.code}: {e.detail}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
