# -*- coding: utf-8 -*-
"""
code_imports.py — trích quan hệ `imports` LANGUAGE-AGNOSTIC, SELF-CONTAINED.

Thay vai trò code-graph MCP cho quan hệ imports ở tầng graph tĩnh:
- KHÔNG gọi MCP/tool ngoài, KHÔNG dependency cài ngoài (chỉ stdlib: ast/re/pathlib/json).
- Fail-open: lỗi parse/regex trên một file KHÔNG giết build — trả rỗng, bỏ qua file đó.
- Language-agnostic: bảng EXTRACTORS = {ext: fn}, ngôn ngữ chưa có extractor → 0 cạnh, không lỗi.
- Chỉ nối cạnh khi RESOLVE được về file thật (relative / tsconfig-alias); còn lại đếm unresolved,
  KHÔNG bịa đích (chống hallucination — đúng đòn 1 benchmark).

API: extract(abs_path, repo_root, tsconfig_paths=None) -> {"symbols","resolved","unresolved"}
  resolved   = list[str] đường dẫn repo-relative của các đích import giải được
  unresolved = int số import không giải tĩnh được (dynamic, alias không map, package ngoài)
"""
import ast
import re
from pathlib import Path

SUPPORTED_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".go", ".rs"}
_TS_EXTS = (".ts", ".tsx", ".js", ".jsx", ".mjs", "/index.ts", "/index.tsx", "/index.js")


def _strip_comments_generic(src: str) -> str:
    """Bỏ // dòng, /* */ khối, và chuỗi backtick/nháy — để 'require trong comment' KHÔNG bị tính."""
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.DOTALL)
    src = re.sub(r"(?m)//.*$", " ", src)
    return src


# ---------------- Python (ast, giữ nguyên độ chính xác) ----------------
def _py(abs_path, repo_root, _tsp):
    try:
        tree = ast.parse(Path(abs_path).read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return [], set(), 0
    syms = [n.name for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    mods = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                mods.add(a.name)                      # dotted đầy đủ (app.core / os); import phẳng = 1 segment
        elif isinstance(n, ast.ImportFrom) and n.module:
            mods.add(n.module)                        # module dotted (app.core) hoặc phẳng (store)
            for a in n.names:                         # from pkg import sub → pkg.sub (sub có thể là module)
                mods.add(n.module + "." + a.name)
    # Python resolve theo module-name để lại cho caller (khác cơ chế path); nay cả dotted-path lẫn basename
    return syms, {("mod", m) for m in mods}, 0


# ---------------- TS/JS ----------------
_TS_IMPORT = re.compile(
    r"""(?:import\b[^'"]*?from\s*|export\b[^'"]*?from\s*|import\s*|require\s*\(\s*)['"]([^'"]+)['"]""")
_TS_DYN = re.compile(r"import\s*\(\s*[`'\"]?\s*[^)'\"`]*[`)]")  # import(var) / template → dynamic


def _ts(abs_path, repo_root, tsp):
    src = _strip_comments_generic(Path(abs_path).read_text(encoding="utf-8", errors="ignore"))
    specs = _TS_IMPORT.findall(src)
    unresolved = len(_TS_DYN.findall(src))
    return [], {("path", s) for s in specs}, unresolved


# ---------------- Go ----------------
_GO_SINGLE = re.compile(r'(?m)^\s*import\s+"([^"]+)"')
_GO_BLOCK = re.compile(r"import\s*\((.*?)\)", re.DOTALL)
_GO_INBLOCK = re.compile(r'"([^"]+)"')


def _go(abs_path, repo_root, _tsp):
    src = _strip_comments_generic(Path(abs_path).read_text(encoding="utf-8", errors="ignore"))
    specs = set(_GO_SINGLE.findall(src))
    for blk in _GO_BLOCK.findall(src):
        specs |= set(_GO_INBLOCK.findall(blk))
    return [], {("go", s) for s in specs}, 0


# ---------------- Rust ----------------
_RS_USE = re.compile(r"(?m)^\s*use\s+([A-Za-z_][\w:]*)")


def _rs(abs_path, repo_root, _tsp):
    src = _strip_comments_generic(Path(abs_path).read_text(encoding="utf-8", errors="ignore"))
    return [], {("rs", m) for m in _RS_USE.findall(src)}, 0


EXTRACTORS = {".py": _py, ".ts": _ts, ".tsx": _ts, ".js": _ts, ".jsx": _ts, ".mjs": _ts,
              ".go": _go, ".rs": _rs}


# ---------------- resolve specifier → file repo-relative ----------------
def _exists_rel(repo_root, rel):
    p = Path(repo_root) / rel
    if p.is_file():
        return rel
    for ext in (".ts", ".tsx", ".js", ".jsx", ".mjs"):
        if (Path(repo_root) / (rel + ext)).is_file():
            return rel + ext
    for idx in ("/index.ts", "/index.tsx", "/index.js"):
        if (Path(repo_root) / (rel + idx)).is_file():
            return rel + idx
    return None


def _resolve_ts(spec, abs_path, repo_root, tsp):
    if spec.startswith("."):                      # relative import
        base = (Path(abs_path).parent / spec).resolve()
        try:
            rel = base.relative_to(Path(repo_root).resolve()).as_posix()
        except ValueError:
            return None
        return _exists_rel(repo_root, rel)
    if tsp:                                        # tsconfig paths alias (@core/* -> ...)
        for pat, targets in tsp.items():
            star = pat.rstrip("*")
            if pat.endswith("*") and spec.startswith(star):
                tail = spec[len(star):]
                for t in targets:
                    cand = t.replace("*", tail)
                    r = _exists_rel(repo_root, cand)
                    if r:
                        return r
            elif pat == spec:
                for t in targets:
                    r = _exists_rel(repo_root, t)
                    if r:
                        return r
    return None                                    # package ngoài / alias không map → unresolved


def load_tsconfig_paths(repo_root):
    """Đọc paths từ tsconfig*.json (self-contained, fail-open) → {pattern: [targets]}."""
    out = {}
    for name in ("tsconfig.base.json", "tsconfig.json"):
        p = Path(repo_root) / name
        if not p.is_file():
            continue
        try:
            import json
            raw = re.sub(r"(?m)//.*$", "", p.read_text(encoding="utf-8"))
            data = json.loads(raw)
            paths = data.get("compilerOptions", {}).get("paths", {})
            for k, v in paths.items():
                out[k] = v if isinstance(v, list) else [v]
        except Exception:
            continue
    return out


def extract(abs_path, repo_root, tsconfig_paths=None):
    ext = Path(abs_path).suffix.lower()
    fn = EXTRACTORS.get(ext)
    if not fn:
        return {"symbols": [], "resolved": [], "unresolved": 0}
    try:
        syms, specs, unresolved = fn(abs_path, repo_root, tsconfig_paths)
    except Exception:
        return {"symbols": [], "resolved": [], "unresolved": 0}
    resolved = []
    for kind, spec in specs:
        if kind == "path":                         # TS/JS
            r = _resolve_ts(spec, abs_path, repo_root, tsconfig_paths)
            if r:
                resolved.append(r)
            else:
                unresolved += 1
        # ('mod'/'go'/'rs') → module-name based, để caller resolve qua index (giữ hành vi Python cũ)
    return {"symbols": syms[:20], "resolved": sorted(set(resolved)),
            "unresolved": unresolved, "_modspecs": [s for k, s in specs if k in ("mod", "go", "rs")]}


if __name__ == "__main__":
    import sys, json
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    tsp = load_tsconfig_paths(root)
    print("tsconfig paths:", tsp)
    for f in sys.argv[2:]:
        print(f, "→", json.dumps(extract(f, root, tsp), ensure_ascii=False))
