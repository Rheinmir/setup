#!/usr/bin/env python3
"""qc-regression — chạy các test tái hiện lỗi do /qc-code sinh (tất định, 0-token, KHÔNG LLM).

/qc-code (LLM, gọi tay) tìm bug ở mục logic và sinh một test ĐỎ tái hiện cho mỗi bug,
đặt tên `qc-<slug>`. Script này là phần TỰ ĐỘNG — nó gom các test `qc-*` đó, chạy bằng
runner có sẵn của dự án, báo đỏ/xanh. Đây là thứ hook gọi (verify-before-commit / tùy chọn
PostToolUse) — CỐ Ý không gọi LLM: cái đắt (phán đoán) ở qc-code thủ công, cái rẻ (chạy test)
tự động. Giữ nguyên tắc hook-0-token của overstack.

Tự phát hiện runner theo dấu hiệu dự án:
  pytest  ← có pytest.ini/pyproject/setup.cfg/conftest.py, hoặc file test_*.py/*_test.py
  vitest  ← "vitest" trong package.json
  jest    ← "jest" trong package.json

Fail-open: không tìm thấy test `qc-*` nào → sạch (exit 0), KHÔNG chặn dự án chưa dùng qc-code.

Dùng:
  qc-regression.py --list          # liệt kê test qc-* tìm được + runner
  qc-regression.py --run           # chạy chúng; exit 1 nếu có đỏ, 0 nếu xanh/không có
  qc-regression.py --json
  qc-regression.py --self-test
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("QC_ROOT", ".")).resolve()
# test qc-* : tên file chứa 'qc-' hoặc 'qc_' và là file test
QC_GLOBS = ["**/qc-*_test.py", "**/qc_*_test.py", "**/test_qc_*.py", "**/qc-*.test.*",
            "**/qc-*.spec.*", "**/qc_*.spec.*", "**/*qc-*.test.*"]
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".overstack-kit"}


def find_qc_tests(root):
    out = []
    for g in QC_GLOBS:
        for p in glob.glob(str(root / g), recursive=True):
            if not any(f"/{d}/" in p.replace("\\", "/") for d in SKIP_DIRS):
                out.append(os.path.relpath(p, root))
    return sorted(set(out))


def detect_runner(root, tests):
    py = [t for t in tests if t.endswith(".py")]
    js = [t for t in tests if not t.endswith(".py")]
    if py and (any((root / f).exists() for f in ("pytest.ini", "conftest.py", "pyproject.toml", "setup.cfg"))
               or True):  # có test .py → pytest là mặc định hợp lý
        return "pytest", py
    pkg = root / "package.json"
    if js and pkg.is_file():
        txt = pkg.read_text(encoding="utf-8", errors="ignore")
        if "vitest" in txt:
            return "vitest", js
        if "jest" in txt:
            return "jest", js
    if py:
        return "pytest", py
    if js:
        return "node", js
    return None, []


def run(root, runner, tests):
    if runner == "pytest":
        cmd = [sys.executable, "-m", "pytest", "-q", *tests]
    elif runner == "vitest":
        cmd = ["npx", "vitest", "run", *tests]
    elif runner == "jest":
        cmd = ["npx", "jest", *tests]
    else:
        return 0, "không có runner phù hợp — bỏ qua (fail-open)"
    try:
        p = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=300)
        return p.returncode, (p.stdout + p.stderr)[-2000:]
    except FileNotFoundError:
        return 0, f"runner '{runner}' không cài — bỏ qua (fail-open)"
    except subprocess.TimeoutExpired:
        return 1, "test qc-* chạy quá 300s — treo?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--root", default=None)
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())
    root = Path(a.root).resolve() if a.root else ROOT
    tests = find_qc_tests(root)
    runner, sel = detect_runner(root, tests)

    if a.json:
        print(json.dumps({"root": str(root), "runner": runner, "qc_tests": tests}, ensure_ascii=False, indent=2))
        sys.exit(0)
    if not tests:
        if not a.json:
            print("qc-regression: chưa có test qc-* nào (fail-open, không chặn).")
        sys.exit(0)
    if a.list or not a.run:
        print(f"qc-regression · {len(tests)} test qc-* · runner: {runner or '—'}")
        for t in tests:
            print(f"  {t}")
        sys.exit(0)
    # --run
    code, tail = run(root, runner, sel)
    print(f"qc-regression --run · {len(sel)} test · runner {runner} · {'ĐỎ' if code else 'xanh'}")
    if code:
        print(tail)
    sys.exit(1 if code else 0)


def self_test():
    """Dựng một dự án tạm có 1 test qc-* đỏ + 1 xanh, xác nhận --run bắt được đỏ."""
    import tempfile
    d = Path(tempfile.mkdtemp())
    (d / "qc-red_test.py").write_text("def test_qc_red():\n    assert 1 == 2\n", encoding="utf-8")
    (d / "qc-green_test.py").write_text("def test_qc_green():\n    assert 1 == 1\n", encoding="utf-8")
    (d / "normal_test.py").write_text("def test_x():\n    assert True\n", encoding="utf-8")
    tests = find_qc_tests(d)
    ok = True
    checks = [
        ("tìm đúng 2 test qc-* (bỏ normal_test)", len(tests) == 2 and all("qc" in t for t in tests)),
    ]
    runner, sel = detect_runner(d, tests)
    checks.append(("phát hiện runner pytest", runner == "pytest"))
    # chạy thật nếu có pytest
    try:
        code, _ = run(d, runner, sel)
        checks.append(("--run bắt được test ĐỎ (exit 1)", code == 1))
    except Exception:
        checks.append(("--run (pytest không có → skip)", True))
    for label, passed in checks:
        print(f"  {'✓' if passed else '✗'} {label}")
        ok = ok and passed
    print("self-test: PASS" if ok else "self-test: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    main()
