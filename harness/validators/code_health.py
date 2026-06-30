#!/usr/bin/env python3
"""code-health: Trụ 4 (Quality Gates) — cổng CI NGÔN-NGỮ, TẤT ĐỊNH, KHÔNG-LLM.

GỐC: các cổng chất lượng cũ (council/wikieval/trace-grader) đều LLM-phán-xử hoặc kỷ-luật-quy-trình
→ giám khảo cùng "gen" với bị cáo, có thể bị lừa. Trụ 4 PARTIAL vì THIẾU một cổng máy-kiểm-được-
mà-không-cãi-được. Validator này là cái floor đó: mọi .py phải biên dịch sạch — lỗi CÚ PHÁP ở BẤT KỲ
script/hook/validator nào → ĐỎ, không cần model.

build-now-adapt-later:
  • CONTRACT (chắc, dựng now, HARD-GATE): mọi file Python phải `py_compile` không lỗi cú pháp (stdlib,
    luôn có). py_compile CHỈ bắt cú pháp — KHÔNG bắt import-gãy/undefined-name (đó là việc của lint sâu).
  • QUARANTINE (unknown): lint SÂU (undefined-name, unused, import gãy, style) cần `ruff`/`pyflakes` —
    HIỆN CHƯA CÀI, và 81 file CHƯA từng lint nên bật-chặn ngay sẽ đỏ giả. Adapter `_deep_lint()`: có tool
    → CHẠY nhưng **ADVISORY** (in số finding, KHÔNG exit 2) — fail-safe, không phá CI/gate đang xanh.
    Adapt later: dọn code cho ruff-clean → thêm `--enforce-lint` (hoặc CI step riêng) để nâng lint sâu
    thành hard-gate. 0 sửa engine.

Exit 0 = compile sạch · exit 2 = có file lỗi cú pháp (HOẶC lint sâu lỗi khi có `--enforce-lint`).
Dùng: code_health.py [--root DIR] [--enforce-lint]   (mặc định ".")
"""
import argparse
import py_compile
import shutil
import subprocess
import sys
from pathlib import Path

# Thư mục chứa Python của repo (tracked). Bỏ qua rác build/cache.
PY_ROOTS = ("harness", "fdk", "llmwiki/.claude")
SKIP_PARTS = {"__pycache__", ".git", "node_modules", ".overstack-kit", "template-cache"}


def _py_files(root: Path):
    seen = []
    for sub in PY_ROOTS:
        base = root / sub
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            if any(part in SKIP_PARTS for part in p.parts):
                continue
            seen.append(p)
    return sorted(set(seen))


def _compile_floor(files):
    """CONTRACT: mọi file phải compile. Trả list (file, error)."""
    errs = []
    for f in files:
        try:
            py_compile.compile(str(f), doraise=True)
        except py_compile.PyCompileError as e:
            errs.append((f, str(e.msg if hasattr(e, "msg") else e)))
        except Exception as e:  # SyntaxError hiếm khi lọt ra ngoài PyCompileError
            errs.append((f, f"{type(e).__name__}: {e}"))
    return errs


def _deep_lint(root: Path, files):
    """QUARANTINE adapter: lint sâu NẾU tool có mặt. Trả (verified, tool, errors)."""
    if shutil.which("ruff"):
        r = subprocess.run(["ruff", "check", "--quiet", *[str(f) for f in files]],
                           cwd=root, capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip()
        return True, "ruff", (out.splitlines() if r.returncode != 0 else [])
    try:
        import pyflakes  # noqa: F401
        r = subprocess.run([sys.executable, "-m", "pyflakes", *[str(f) for f in files]],
                           cwd=root, capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip()
        return True, "pyflakes", (out.splitlines() if r.returncode != 0 else [])
    except Exception:
        return False, None, []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--enforce-lint", action="store_true",
                    help="nâng lint sâu (ruff/pyflakes) thành hard-gate; mặc định advisory")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    files = _py_files(root)
    if not files:
        print("[code-health] không thấy .py nào — bỏ qua.")
        sys.exit(0)

    # HARD-GATE: floor compile (cú pháp)
    floor_errs = _compile_floor(files)
    if floor_errs:
        sys.stderr.write(f"[code-health] {len(floor_errs)} file LỖI CÚ PHÁP (không compile):\n")
        for f, e in floor_errs:
            sys.stderr.write(f"  ✗ {f.relative_to(root)}: {(e.splitlines()[0] if e else '').strip()}\n")
        sys.exit(2)

    # QUARANTINE: lint sâu — advisory mặc định, chỉ chặn khi --enforce-lint
    verified, tool, deep_errs = _deep_lint(root, files)
    if deep_errs:
        flag = "✗ HARD" if args.enforce_lint else "ℹ ADVISORY (chưa enforce)"
        sys.stderr.write(f"[code-health] {tool}: {len(deep_errs)} finding [{flag}]:\n")
        for line in deep_errs[:30]:
            sys.stderr.write(f"  · {line}\n")
        if args.enforce_lint:
            sys.exit(2)

    if not verified:
        depth = "lint-depth: verified=false (chưa có ruff/pyflakes — chỉ compile floor)"
    elif deep_errs:
        depth = f"lint sâu {tool}: {len(deep_errs)} finding (advisory)"
    else:
        depth = f"lint sâu: ✓ {tool} sạch"
    print(f"[code-health] ✓ {len(files)} file Python compile sạch · {depth}.")
    sys.exit(0)


if __name__ == "__main__":
    main()
