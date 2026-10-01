#!/usr/bin/env python3
"""surface-coverage — "phủ hết" là một phép DIFF với bề mặt thật đọc từ code, không phải một con số (GH#191).

  surface-coverage.py scan  <root> [--modules <glob> ...] [--out surface.json]
      Liệt kê bề mặt TẤT ĐỊNH từ code, ghi kèm commit:
        page:/x    — Next app router (app/**/page.*), pages router (pages/**, trừ _app/_document/api)
        api:/x     — route handler (app/**/route.*), pages/api/**
        module:x   — mỗi thư mục con của --modules (vd 'apps/api/src/modules/*')
      Route group `(x)` và slot `@x` bị bỏ khỏi đường dẫn; node_modules/.next/dist/build/.git bị bỏ qua.

  surface-coverage.py check <surface.json> <coverage.json> [--flows domain-graph.json] [--root <dir>]
      coverage.json = {"commit": "<sha>", "items": {"page:/x": {"by": ["flow:a"]} | {"exclude": "<lý do>"}}}
      ĐỎ (rc 1) khi: mục bề mặt không có dòng sổ · loại trừ không lý do · dòng sổ trỏ mục đã mất ·
      sổ dựng ở commit khác bề mặt · (--flows) `by` trỏ flow không có · bước flow có file:line sai.
      In "N/M mục được phủ, K loại trừ" + danh sách mục chưa phủ. Chỉ in số đếm khi đã diff xong.
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

SKIP = {"node_modules", ".next", "dist", "build", ".git", ".turbo", "out", "coverage"}
EXT = {".tsx", ".ts", ".jsx", ".js", ".mdx"}


def _walk(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in EXT and not SKIP.intersection(p.relative_to(root).parts):
            yield p


def _route(parts) -> str:
    keep = [s for s in parts if not (s.startswith("(") and s.endswith(")")) and not s.startswith("@")]
    return "/" + "/".join(keep)


def scan(root: Path, modules=()) -> dict:
    items = {}
    for p in _walk(root):
        rel = p.relative_to(root).parts
        if "app" in rel:
            sub = rel[rel.index("app") + 1:]
            if p.stem in ("page", "route"):
                items[("page:" if p.stem == "page" else "api:") + _route(sub[:-1])] = "/".join(rel)
        elif "pages" in rel:
            sub = list(rel[rel.index("pages") + 1:])
            if sub[-1].split(".")[0] in ("_app", "_document", "_error"):
                continue
            sub[-1] = p.stem
            if sub[-1] == "index":
                sub = sub[:-1]
            kind = "api:" if sub[:1] == ["api"] else "page:"
            items[kind + _route(sub)] = "/".join(rel)
    for g in modules:
        for d in sorted(root.glob(g)):
            if d.is_dir() and not SKIP.intersection(d.parts):
                items["module:" + d.name] = str(d.relative_to(root))
    try:
        commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() or None
    except OSError:
        commit = None
    return {"commit": commit, "root": str(root), "items": dict(sorted(items.items()))}


def _flows(graph: dict):
    for d in graph.get("domains", []):
        for f in d.get("flows", []):
            yield f


def check(surface: dict, cov: dict, flows=None, root: Path | None = None):
    errs, uncovered, excluded = [], [], []
    items, ledger = surface["items"], cov.get("items", {})
    if surface.get("commit") and cov.get("commit") and surface["commit"] != cov["commit"]:
        errs.append(f"lệch commit: bề mặt @{surface['commit'][:8]} nhưng sổ @{cov['commit'][:8]}")
    flow_ids = {f["id"] for f in _flows(flows)} if flows else None
    for k in items:
        e = ledger.get(k)
        if not e or not (e.get("by") or "exclude" in e):
            uncovered.append(k)
        elif "exclude" in e:
            if not str(e["exclude"]).strip():
                errs.append(f"{k}: loại trừ không có lý do")
            excluded.append(k)
        elif flow_ids is not None:
            errs += [f"{k}: trỏ flow không tồn tại {b}" for b in e["by"] if b not in flow_ids]
    errs += [f"{k}: dòng sổ trỏ mục không còn trên bề mặt" for k in ledger if k not in items]
    if flows and root:
        for f in _flows(flows):
            for s in f.get("steps", []):
                fp = root / s.get("file", "")
                if not fp.is_file():
                    errs.append(f"{f['id']}/{s.get('id')}: file không tồn tại {s.get('file')}")
                elif not 1 <= int(s.get("line", 0)) <= len(fp.read_text(errors="replace").splitlines()):
                    errs.append(f"{f['id']}/{s.get('id')}: dòng {s.get('line')} nằm ngoài {s.get('file')}")
    return uncovered, excluded, errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("scan"); a.add_argument("root"); a.add_argument("--modules", action="append", default=[]); a.add_argument("--out")
    c = sp.add_parser("check"); c.add_argument("surface"); c.add_argument("coverage"); c.add_argument("--flows"); c.add_argument("--root")
    o = ap.parse_args(argv)
    if o.cmd == "scan":
        s = scan(Path(o.root).resolve(), o.modules)
        out = json.dumps(s, ensure_ascii=False, indent=1)
        Path(o.out).write_text(out + "\n") if o.out else print(out)
        if o.out:
            kinds = {}
            for k in s["items"]:
                kinds[k.split(":")[0]] = kinds.get(k.split(":")[0], 0) + 1
            print(f"bề mặt {len(s['items'])} mục @{(s['commit'] or 'không-git')[:8]} · " + " · ".join(f"{k} {v}" for k, v in kinds.items()))
        return 0
    surface, cov = json.loads(Path(o.surface).read_text()), json.loads(Path(o.coverage).read_text())
    flows = json.loads(Path(o.flows).read_text()) if o.flows else None
    root = Path(o.root or surface.get("root") or ".")
    unc, exc, errs = check(surface, cov, flows, root if flows else None)
    m = len(surface["items"])
    print(f"{m - len(unc) - len(exc)}/{m} mục bề mặt được phủ, {len(exc)} loại trừ, {len(unc)} chưa phủ")
    for k in unc:
        print(f"  CHƯA PHỦ {k}  ({surface['items'][k]})")
    for e in errs:
        print(f"  LỖI {e}")
    return 1 if unc or errs else 0


if __name__ == "__main__":
    sys.exit(main())
