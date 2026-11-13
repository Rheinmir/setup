#!/usr/bin/env bash
# fdk-gate --jobs: chạy song song phải cho ĐÚNG kết quả của chạy tuần tự (cùng thứ tự, cùng rc từng step)
# và phải nhanh hơn thật. Dùng step giả (sleep) nên không phụ thuộc trạng thái repo.
set -euo pipefail
ROOT="${1:-.}"
python3 - "$ROOT" <<'PY'
import importlib.util, sys, time
from pathlib import Path
root = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("fdk_gate", root / "harness/scripts/fdk-gate.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
steps = [("a ok", ["bash", "-c", "sleep 0.4"], "w"), ("b fail", ["bash", "-c", "sleep 0.1; echo boom >&2; exit 3"], "w"),
         ("c ok", ["bash", "-c", "sleep 0.4; echo fine"], "w"), ("d missing", ["no-such-tool-xyz"], "w"),
         ("e ok", ["bash", "-c", "sleep 0.4"], "w"), ("f ok", ["bash", "-c", "sleep 0.4"], "w")]
ok = fail = 0
def check(name, cond):
    global ok, fail
    print(("  ✓ " if cond else "  ✗ ") + name)
    if cond: ok += 1
    else: fail += 1
t = time.time(); serial = g.run_all(root, steps, 1); ts = time.time() - t
t = time.time(); par = g.run_all(root, steps, 4); tp = time.time() - t
check("song song cho kết quả y hệt tuần tự (thứ tự + ok + rc + msg)", serial == par)
check("thứ tự kết quả theo STEPS, không theo step nào xong trước", [r["step"] for r in par] == [s[0] for s in steps])
check("rc từng step giữ nguyên (0 · 3 · 0 · 127 · 0 · 0)", [r["rc"] for r in par] == [0, 3, 0, 127, 0, 0])
check(f"song song nhanh hơn tuần tự ít nhất 2 lần ({ts:.2f}s → {tp:.2f}s)", tp * 2 < ts)
import os
os.environ["FDK_GATE_JOBS"] = "3"; check("FDK_GATE_JOBS=3 được dùng", g.default_jobs() == 3)
os.environ["FDK_GATE_JOBS"] = "0"; check("FDK_GATE_JOBS=0 → kẹp về 1 (tuần tự)", g.default_jobs() == 1)
os.environ["FDK_GATE_JOBS"] = "abc"; check("FDK_GATE_JOBS rác → mặc định min(4, CPU)", g.default_jobs() == min(4, os.cpu_count() or 1))
print(f"  {ok}/{ok + fail} pass")
sys.exit(1 if fail else 0)
PY
