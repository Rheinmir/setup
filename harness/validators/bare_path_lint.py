#!/usr/bin/env python3
"""bare_path_lint — file ĐI XUỐNG GLOBAL không được ghi cứng đường trần llmwiki/ · harness/ lúc chạy.

Vì sao: repo framework để llmwiki/ + harness/ trần, downstream là .llmwiki/ + .harness/ (installer
migrate, resolver overstack_paths chấp cả hai). Code viết trong repo chạy đúng ở repo, xuống máy
khách thì câm/đẻ thư mục lạc (GH#111 #112 #153, đo 2026-09-11: 55 file). Lint này là van CI:
nợ cũ nằm trong baseline (ratchet), nợ MỚI đỏ ngay.
Miễn: dòng comment; dòng đánh dấu `# bare-path: ok <lý do>` (ngoại lệ HIỆN, grep được).
KHÔNG miễn theo cả file: file đã import resolver vẫn có thể còn literal trần (đo 2026-09-11:
okf-scan.py import overstack_paths nhưng hằng MEMORY vẫn trần). Baseline ratchet đếm hết.
"""
import json, re, sys
from pathlib import Path

BARE = re.compile(r'''(?<![\w./~-])["'(]?(?:llmwiki|harness)/(?:wiki|html|raw|\.harness-stamp|\.claude|metrics|scripts|validators|poc-vendor-neutral|evals|scratch-log|personas)''')
OK_MARK = "# bare-path: ok"

def strip_tier3(root):
    s = (root / "harness/scripts/install-harness.sh").read_text(encoding="utf-8")
    m = re.search(r'STRIP_TIER3="(.*?)"', s, re.S)
    return {x.strip() for x in (m.group(1).split() if m else [])}

def shipped_files(root):
    t3 = strip_tier3(root)
    pats = ["llmwiki/.claude/hooks/*.py", "llmwiki/.claude/hooks/validators/*.py",
            "harness/validators/*.py", "harness/scripts/*.py", "fdk/tools/*.py",
            "harness/poc-vendor-neutral/bin/*.py", "harness/poc-vendor-neutral/*.sh"]
    out = []
    for p in pats:
        out += [f for f in root.glob(p) if f.relative_to(root).as_posix() not in t3]
    return sorted(set(out))

def scan_file(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    hits = []
    for i, ln in enumerate(text.splitlines(), 1):
        s = ln.strip()
        if s.startswith("#") or OK_MARK in ln:
            continue
        if BARE.search(ln):
            hits.append((i, s[:100]))
    return hits

def scan(root):
    return {f.relative_to(root).as_posix(): scan_file(f) for f in shipped_files(root)}

def parity(root):
    """Thứ tự ứng viên ở hooklib phải khớp overstack_paths — hai nguồn cùng một sự thật."""
    import importlib.util
    def load(p, n):
        spec = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
    a = load(root / "harness/scripts/overstack_paths.py", "op")
    b = load(root / "llmwiki/.claude/hooks/hooklib.py", "hl")
    # Thiếu hằng ở một bên (vd hooklib chưa có Task 2) → coi là LỆCH, báo rõ, không traceback.
    return all(getattr(a, k, None) is not None and getattr(a, k, None) == getattr(b, k, None)
               for k in ("OVERSTACK_DIRS", "HARNESS_DIRS"))

def self_test():
    import tempfile
    t = Path(tempfile.mkdtemp())
    (t / "a.py").write_text('p = "llmwiki/wiki/x.md"\n')
    (t / "b.py").write_text('from overstack_paths import wiki_dir\np = "llmwiki/wiki/x.md"\n')
    (t / "c.py").write_text('# llmwiki/wiki chỉ là comment\nq = 1\n')
    (t / "d.py").write_text('p = "llmwiki/wiki/x.md"  # bare-path: ok fixture demo\n')
    assert scan_file(t / "a.py") == [(1, 'p = "llmwiki/wiki/x.md"')], "bare literal phải bị bắt"
    assert scan_file(t / "b.py") == [(2, 'p = "llmwiki/wiki/x.md"')], "file có import resolver KHÔNG được miễn theo file"
    assert scan_file(t / "c.py") == [], "comment không tính"
    assert scan_file(t / "d.py") == [], "đánh dấu ok được miễn"
    print("self-test: PASS"); return 0

def main():
    args = sys.argv[1:]
    if "--self-test" in args:
        return self_test()
    root = Path(args[args.index("--root") + 1] if "--root" in args else ".").resolve()
    base_p = root / "harness/metrics/bare-path-baseline.json"
    found = {k: v for k, v in scan(root).items() if v}
    if "--write-baseline" in args:
        base_p.write_text(json.dumps({"schema": 1, "files": {k: len(v) for k, v in found.items()}}, indent=1, ensure_ascii=False) + "\n")
        print(f"baseline: {len(found)} file · {sum(len(v) for v in found.values())} chỗ"); return 0
    base = json.loads(base_p.read_text())["files"] if base_p.is_file() else {}
    new = {k: v for k, v in found.items() if len(v) > base.get(k, 0)}
    if not parity(root):
        print("✗ hooklib.OVERSTACK_DIRS/HARNESS_DIRS lệch overstack_paths — sửa cho khớp"); return 2
    if new:
        for k, v in new.items():
            for ln, s in v:
                print(f"{k}:{ln}: {s}")
        print(f"\n✗ {len(new)} file có NỢ MỚI bare-path (đi xuống global). Dùng overstack_paths.* / hooklib.*; "
              f"ngoại lệ thật thì đánh dấu `{OK_MARK} <lý do>`."); return 2
    fixed = {k: base[k] - len(found.get(k, [])) for k in base if base[k] > len(found.get(k, []))}
    if fixed:
        print(f"↓ trả nợ ở {len(fixed)} file — chạy --write-baseline để chốt: {' '.join(fixed)}")
    print(f"✓ bare-path: không nợ mới ({len(found)} file nợ tồn, baseline {len(base)})"); return 0

if __name__ == "__main__":
    sys.exit(main())
