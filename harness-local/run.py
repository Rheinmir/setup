#!/usr/bin/env python3
"""harness-local/run.py — chạy rule RIÊNG của dự án (harness-local/validators/*.py).

Modes:
  run.py hook         # stdin JSON event → chạy mọi validator với event (PreToolUse/Stop)
  run.py files <f...> # pre-commit/CI: chạy validator trên file đổi
  run.py check        # self-test: id P<n> hợp lệ/không trùng/không đụng R · validator compile
  run.py list         # liệt kê rule từ policy.yaml
Exit 0 = pass · 2 = có rule block (hoặc check fail). Fail-open per-validator (1 cái lỗi
không làm gãy phiên/commit). File validator bắt đầu '_' bị BỎ QUA (mẫu/helper).
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VDIR = HERE / "validators"


def _validators():
    return sorted(p for p in VDIR.glob("*.py") if not p.name.startswith("_")) if VDIR.is_dir() else []


def _run_one(vpath, args, stdin_text):
    try:
        r = subprocess.run([sys.executable, str(vpath), *args], input=stdin_text,
                           capture_output=True, text=True, timeout=20)
        return r.returncode, (r.stderr or "").strip()
    except Exception:
        return 0, ""   # fail-open: 1 validator lỗi không chặn cả phiên


def _run_all(args, stdin_text):
    fails = []
    for v in _validators():
        rc, err = _run_one(v, args, stdin_text)
        if rc == 2:
            fails.append(err or f"[{v.name}] block")
    if fails:
        print("[harness-local] rule dự án chặn:\n" + "\n".join(fails), file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


def _rules():
    try:
        import yaml
        data = yaml.safe_load((HERE / "policy.yaml").read_text(encoding="utf-8")) or {}
        rs = data.get("rules") or []
        return rs if isinstance(rs, list) else []
    except Exception:
        return []


def mode_check():
    probs, seen = [], set()
    for r in _rules():
        rid = str(r.get("id", "")).strip()
        if re.fullmatch(r"R\d+", rid):
            probs.append(f"id {rid}: ĐỤNG namespace framework (R<n>) — đổi sang P<n>")
        elif not re.fullmatch(r"P\d+", rid):
            probs.append(f"id '{rid}': sai format — phải P<n>")
        if rid and rid in seen:
            probs.append(f"id {rid}: trùng")
        seen.add(rid)
        vp = str(r.get("validator", "")).strip()
        if vp and not ((HERE.parent / vp).is_file() or Path(vp).is_file()):
            probs.append(f"{rid}: validator '{vp}' không tồn tại")
    for v in _validators():
        if subprocess.run([sys.executable, "-m", "py_compile", str(v)], capture_output=True).returncode != 0:
            probs.append(f"{v.name}: không compile")
    if probs:
        print("[harness-local check] vi phạm:\n  - " + "\n  - ".join(probs), file=sys.stderr)
        sys.exit(2)
    print(f"[harness-local] OK — {len(_validators())} validator · {len(seen - {''})} rule (P-namespace, không đụng R)")
    sys.exit(0)


def mode_list():
    for r in _rules():
        print(f"  {r.get('id', '?')} {r.get('name', '')} — {r.get('statement', '')}")
    print(f"  ({len(_validators())} validator file)")
    sys.exit(0)


def main():
    a = sys.argv[1:]
    if not a:
        mode_check()
    m = a[0]
    if m == "hook":
        _run_all([], sys.stdin.read())
    elif m == "files":
        _run_all(a[1:], "")
    elif m in ("check", "--check"):
        mode_check()
    elif m in ("list", "--list"):
        mode_list()
    else:
        mode_check()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)  # fail-open tuyệt đối
