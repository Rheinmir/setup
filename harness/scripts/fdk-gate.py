#!/usr/bin/env python3
"""fdk-gate — cổng "đủ step mới cho push": chạy TOÀN BỘ định-nghĩa-hoàn-thành của framework.

"Harness của riêng FDK". Một chức năng/thay đổi framework chỉ được push khi MỌI step pass.
Đây là bản MÁY-ĐỌC của checklist con-người ở master-wiki ("dev một cái mới cần update gì để
hợp lệ"): chạy mọi gate chặn, in board ✓/✗, exit 2 nếu bất kỳ step nào fail → chặn push.

Wire: pre-push hook (cạnh R12 pull-gate). Hoặc chạy tay trước khi push để biết "đã đủ chưa".
CLI: fdk-gate.py [--root DIR] [--json]   (exit 0 = đủ điều kiện push · 2 = thiếu step)

Mỗi step trỏ tới một gate đã có (single source — không lặp lại logic). Thêm gate mới =
thêm 1 dòng vào STEPS (và cập nhật master-wiki checklist cho khớp).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

# (tên hiển thị, lệnh, ý nghĩa step khi dev cái mới)
STEPS = [
    ("R3 index-sync", ["python3", "harness/validators/index_sync.py", "--wiki-dir", "llmwiki/wiki"],
     "index.md khớp file wiki (git-aware)"),
    ("L4 wiki-health", ["python3", "harness/scripts/wiki-health.py", "--wiki-dir", "llmwiki/wiki", "--fail-on", "broken"],
     "không broken wikilink"),
    ("arch-scan", ["python3", "harness/scripts/arch-scan.py", "--root", "."],
     "văn bản skill/doc khớp luật R1-R7"),
    ("harness-lint", ["python3", "harness/scripts/harness-lint.py", "--check"],
     "hằng số content-dir + wiring policy→settings không drift"),
    ("agent↔claude parity", ["python3", "harness/validators/agent_claude_parity.py"],
     "bảng skill AGENT.md == CLAUDE.md"),
    ("duplicate-basename", ["python3", "harness/validators/duplicate_basename.py", "--wiki-dir", "llmwiki/wiki"],
     "không basename .md trùng giữa thư mục"),
    ("harness-doctor", ["python3", "harness/scripts/harness-doctor.py", "--ci"],
     "mọi rail còn 'cắn' (validator chưa chết âm thầm)"),
    ("adapt-registry leak-gate", ["python3", "harness/scripts/adapt-registry.py", "--check"],
     "ẩn số quarantine không rò qua adapter (BNAL Step 7)"),
    ("overstack-docs current", ["python3", "fdk/tools/build-overstack-docs.py", "--check"],
     "llmwiki/html/overstack.html khớp đĩa (docs user luôn-mới, travel cùng install)"),
    ("capabilities current", ["python3", "fdk/tools/build-capabilities.py", "--check"],
     "fdk/CAPABILITIES.md khớp đĩa (agent biết đúng đồ nghề)"),
    ("skill mirror parity", ["python3", "harness/scripts/sync-skills.py", "--check"],
     "canonical ↔ mirror skill byte-identical + loop khai đủ"),
    ("skill provenance", ["python3", "fdk/tools/skill-provenance.py", "check", "--ci"],
     "checksum sổ khớp SKILL.md trên đĩa — sửa skill mà quên `record` thì đỏ tại đây, không đỏ ở CI"),
    ("skill cross-surface", ["python3", "harness/scripts/skill-registry.py", "--check"],
     "mọi skill có mặt đủ marketplace + AGENT + CLAUDE + LOOP_MAP (không drift surface)"),
    ("task-lifecycle", ["python3", "harness/validators/task_lifecycle.py", "--root", "."],
     "Trụ 3: task-ID đi đúng proposed→approved→dispatched→done + draft không ref task lạ"),
    ("audit-chain", ["python3", "harness/scripts/code-logger.py", "--audit", "--check"],
     "Trụ 5: hash-chain events.jsonl nguyên vẹn — sửa/chèn/xoá dòng log đã-chained → đỏ"),
    ("code-health", ["python3", "harness/validators/code_health.py", "--root", "."],
     "Trụ 4: cổng CI tất định không-LLM — mọi .py compile sạch (lint sâu khi có ruff/pyflakes)"),
    ("bnal self-test wired", ["python3", "harness/scripts/bnal-selftest.py", "--check"],
     "mọi script có --self-test ĐỀU được fdk-gate chạy (anti-drift: thêm feature quên gate → đỏ)"),
    ("policy↔converters drift", ["bash", "harness/tests/policy-converters-drift-test.sh"],
     "adapter sinh khớp policy.yaml"),
    ("vendor-neutral demo", ["bash", "harness/poc-vendor-neutral/demo.sh"],
     "self-test lõi (demo)"),
    ("vendor-neutral broad", ["bash", "harness/poc-vendor-neutral/test-broad.sh"],
     "self-test lõi (broad)"),
    ("BNAL feature self-tests", ["bash", "-c",
        "python3 harness/scripts/council.py selftest >/dev/null && "
        "python3 harness/scripts/trace-grader.py --self-test >/dev/null && "
        "python3 harness/scripts/loop-runner.py selftest >/dev/null && "
        "python3 harness/scripts/wikieval.py --self-test >/dev/null && "
        "python3 harness/scripts/failure-flywheel.py --root . --report >/dev/null && "
        "python3 harness/scripts/success-flywheel.py --self-test >/dev/null && "
        "python3 harness/scripts/egress-guard.py --self-test >/dev/null && "
        "python3 harness/scripts/trace-otel.py --self-test >/dev/null && "
        "python3 harness/scripts/spec-gate.py --self-test >/dev/null && "
        "python3 harness/scripts/scoped-hooks.py --self-test >/dev/null && "
        "python3 harness/scripts/mem-rank.py --self-test >/dev/null && "
        "python3 harness/scripts/token-budget.py --self-test >/dev/null && "
        "python3 harness/scripts/inject-scan.py --self-test >/dev/null && "
        "python3 harness/scripts/claim-receipts.py --self-test >/dev/null && "
        "python3 harness/scripts/prospect-critic.py --self-test >/dev/null && "
        "python3 harness/scripts/web-crawl.py --self-test >/dev/null && "
        "python3 harness/scripts/web-clone.py --self-test >/dev/null && "
        "python3 harness/scripts/sweep-gate.py --self-test >/dev/null && "
        "python3 harness/scripts/archetype.py --self-test >/dev/null && "
        "python3 harness/scripts/capability-stamp.py --self-test >/dev/null && "
        "python3 harness/scripts/design-variety.py --self-test >/dev/null && "
        "python3 harness/scripts/ledger-snapshot.py --self-test >/dev/null && "
        "python3 harness/scripts/mem-proxy.py --self-test >/dev/null && "
        "python3 harness/scripts/qc-regression.py --self-test >/dev/null && "
        "python3 harness/scripts/retrieval-eval.py --self-test >/dev/null && "
        "python3 harness/scripts/skill-resolve-eval.py --self-test >/dev/null && "
        "python3 harness/scripts/unknown-ledger.py --self-test >/dev/null"],
     "27 chức năng BNAL — self-test phải còn PASS (giữ verified trung thực)"),
]


def run(root: Path, cmd):
    try:
        p = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=120)
        err = (p.stderr or p.stdout or "").strip().splitlines()
        return p.returncode, (err[0][:90] if err else "")
    except FileNotFoundError:
        return 127, "tool/lệnh không tồn tại"
    except Exception as e:
        return 1, str(e)[:90]


def main():
    args = sys.argv[1:]
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if "--root" in args:
        root = Path(args[args.index("--root") + 1])
    results = []
    for name, cmd, why in STEPS:
        rc, msg = run(root, cmd)
        results.append({"step": name, "ok": rc == 0, "rc": rc, "msg": msg, "why": why})
    failed = [r for r in results if not r["ok"]]
    if "--json" in args:
        print(json.dumps({"ok": not failed, "results": results}, ensure_ascii=False, indent=2))
        sys.exit(2 if failed else 0)
    print("FDK-GATE  định-nghĩa-hoàn-thành (đủ step mới cho push)")
    print(f"  repo: {root}\n")
    for r in results:
        mark = "✓" if r["ok"] else "✗"
        line = f"  {mark} {r['step']:<26} {r['why']}"
        print(line if r["ok"] else line + f"\n      ↳ FAIL(rc={r['rc']}): {r['msg']}")
    print()
    if failed:
        print(f"✗ THIẾU {len(failed)}/{len(results)} step → CHƯA đủ điều kiện push. Sửa rồi chạy lại.")
        sys.exit(2)
    print(f"✓ {len(results)}/{len(results)} step pass → đủ điều kiện push.")
    sys.exit(0)


if __name__ == "__main__":
    main()
