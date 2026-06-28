#!/usr/bin/env python3
"""LoopRunner — deterministic guardrailed agent-loop driver (loop-engineering).

Wrap ANY step with `propose → deterministic-verify → (critique → revise)` and
enforce hard termination guards so an autonomous agent loop can never spin forever,
burn unbounded budget, or "argue its way around" a failing check.

BUILD-NOW / ADAPT-LATER boundary
--------------------------------
DETERMINISTIC, built-and-tested now (this file):
  • the control loop                       propose → verify → guards → revise → repeat
  • the VERIFY step                        a shell cmd; exit-code 0 == pass (pytest/tsc/lint)
  • all termination guards                 max_iter, wall-clock budget, no-progress, escalate
  • progress detection                     sha256 state-hash of workspace-relevant paths
  • the run-log artifact                   JSON: iterations, verdicts, termination reason
  • reflexion                              append a one-line "lesson" to a wiki episodic page

QUARANTINED, the ONE adapter (verified:false, see harness/loop-runner.config.yaml):
  • the LLM critique/revise step           NOT implemented here. The loop calls a `revise.cmd`
                                           shell hook (stub/no-op by default) so the whole loop
                                           is runnable + testable WITHOUT any LLM. Wiring the
                                           real LLM = edit one config field, then flip verified.

KEY INVARIANT: deterministic verify (exit code) is preferred over LLM self-judgment — the
agent cannot talk a failing test into passing. The guards are MANDATORY and all enforced.

Usage
-----
  loop-runner.py run --verify "<cmd>" [--config harness/loop-runner.config.yaml]
                     [--revise "<cmd>"] [--state "<glob>" ...] [--log <path>]
                     [--max-iter N] [--budget-seconds S] [--no-progress-k K]
                     [--escalate-after N] [--episodic <path>] [--cwd <dir>] [--quiet]
  loop-runner.py selftest        # 5 deterministic scenarios, no LLM, no external deps

CLI flags override config; config provides the (quarantined) defaults.
Process exit code: 0 = SUCCESS, 2 = MAX_ITER, 3 = TIMEOUT, 4 = NO_PROGRESS, 5 = ESCALATE.
"""
import argparse
import datetime as _dt
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    import yaml
except ImportError:  # fail-soft: the loop + selftest never depend on PyYAML
    yaml = None

# ── Verdicts (the deterministic contract every consumer reads) ──────────────
SUCCESS = "SUCCESS"
MAX_ITER = "MAX_ITER"
TIMEOUT = "TIMEOUT"
NO_PROGRESS = "NO_PROGRESS"
ESCALATE = "ESCALATE"

EXIT_CODE = {SUCCESS: 0, MAX_ITER: 2, TIMEOUT: 3, NO_PROGRESS: 4, ESCALATE: 5}

# Fail-safe defaults, used when no config file is present. A guard set to 0/None
# is DISABLED — except max_iter, which is the always-on hard backstop.
DEFAULTS = {
    "guards": {
        "max_iter": 6,
        "budget_seconds": 900,
        "no_progress_k": 2,
        "escalate_after_iter": 0,
    },
    "progress": {"state_paths": []},
    "reflexion": {"episodic_memory_page": None, "enabled": True},
    "run_log": {"path": None},
    "revise": {"cmd": None},
}

_OUTPUT_TAIL = 600  # chars of verify/revise output kept per iteration in the run-log


def _now_iso():
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Progress detection: deterministic state-hash ────────────────────────────
def compute_state_hash(state_paths, cwd):
    """sha256 over the workspace-relevant state. Empty paths → constant sentinel
    so the caller can DISABLE no-progress detection (fail-safe: never stop on a
    signal we cannot actually measure)."""
    if not state_paths:
        return None  # no measurable state → no-progress detection is off
    base = Path(cwd)
    h = hashlib.sha256()
    seen = []
    for pat in state_paths:
        if any(c in pat for c in "*?["):
            seen.extend(sorted(base.glob(pat)))
        else:
            seen.append(base / pat)
    files = []
    for m in sorted(set(seen), key=str):
        if m.is_dir():
            files.extend(sorted(p for p in m.rglob("*") if p.is_file()))
        else:
            files.append(m)
    for f in sorted(set(files), key=str):
        try:
            rel = f.relative_to(base)
        except ValueError:
            rel = f
        h.update(str(rel).encode())
        try:
            if f.is_file():
                h.update(b"\x00")
                h.update(f.read_bytes())
            else:
                h.update(b"\xff")  # path absent this iteration
        except OSError:
            h.update(b"\xfe")
    return h.hexdigest()


# ── Reflexion: append one short lesson line to a managed wiki episodic page ──
_EPISODIC_HEADER = """---
type: concept
tags: [loop-runner, episodic-memory, reflexion]
---

# loop-runner — episodic memory (reflexion lessons)

Append-only lesson log written by `harness/scripts/loop-runner.py` on each failed
verify iteration. Managed file: code owns it, humans read it to carry lessons into the
next loop run. Created lazily on the first failing run (never at plan time).

## Origin
- Auto-managed by `harness/scripts/loop-runner.py` (reflexion step).

## Lessons
"""


def append_lesson(page_path, iteration, verify_cmd, exit_code, state_moved):
    """Append a one-line lesson on failure. Lazily creates the page with a valid
    OKF frontmatter + `## Origin` so it stays a structurally-valid wiki file."""
    if not page_path:
        return
    page = Path(page_path)
    page.parent.mkdir(parents=True, exist_ok=True)
    fresh = not page.exists()
    if state_moved is False:
        why = "state unchanged — revise made no progress (wrong edit target / non-actionable critique)"
    elif state_moved is True:
        why = "state changed but verify still red — critique may be off-target"
    else:
        why = "verify still red (progress detection off)"
    line = (
        f"- [{_now_iso()}] iter {iteration} · verify `{verify_cmd}` exit {exit_code} "
        f"· lesson: {why}\n"
    )
    with page.open("a", encoding="utf-8") as fh:
        if fresh:
            fh.write(_EPISODIC_HEADER)
        fh.write(line)


# ── The deterministic control loop ──────────────────────────────────────────
def _run_cmd(cmd, cwd):
    proc = subprocess.run(cmd, shell=True, cwd=str(cwd), capture_output=True, text=True)
    tail = ((proc.stdout or "") + (proc.stderr or ""))[-_OUTPUT_TAIL:]
    return proc.returncode, tail


def run_loop(
    *,
    verify_cmd,
    revise_cmd=None,
    max_iter=6,
    budget_seconds=0,
    no_progress_k=0,
    escalate_after_iter=0,
    state_paths=None,
    episodic_page=None,
    reflexion_enabled=True,
    cwd=".",
    clock=time.monotonic,
    log_path=None,
    quiet=False,
):
    """Drive propose → verify → (critique → revise) under MANDATORY guards.

    Returns a run-log dict (also written to `log_path` as JSON if given).
    `clock` is injectable so the wall-clock guard is testable without sleeping.
    """
    if max_iter < 1:
        raise ValueError("max_iter must be >= 1 (it is the hard backstop guard)")
    cwd = Path(cwd)
    state_paths = state_paths or []
    started_at = _now_iso()
    start = clock()
    iterations = []
    verdict = None
    reason = ""
    prev_hash = None
    streak = 0  # consecutive iterations with an unchanged state-hash
    it = 0

    while True:
        # GUARD 1 — wall-clock budget (checked before doing more work)
        elapsed = clock() - start
        if budget_seconds and elapsed >= budget_seconds:
            verdict, reason = TIMEOUT, f"wall-clock budget {budget_seconds}s exceeded ({elapsed:.1f}s)"
            break
        # GUARD 2 — max iterations (always-on hard backstop)
        if it >= max_iter:
            verdict, reason = MAX_ITER, f"reached max_iter={max_iter} without a passing verify"
            break

        it += 1
        # PROPOSE is the prior state (initial proposal, or last iter's revise).
        # VERIFY — deterministic; exit-code 0 == pass. The agent cannot override this.
        t0 = clock()
        exit_code, out_tail = _run_cmd(verify_cmd, cwd)
        rec = {
            "iter": it,
            "ts": _now_iso(),
            "verify_exit": exit_code,
            "duration_s": round(clock() - t0, 4),
            "verify_output_tail": out_tail,
        }

        if exit_code == 0:
            rec["state_hash"] = None
            rec["unchanged_streak"] = streak
            iterations.append(rec)
            verdict, reason = SUCCESS, f"verify passed on iteration {it}"
            break

        # progress detection on this failed iteration
        cur_hash = compute_state_hash(state_paths, cwd)
        if cur_hash is not None and prev_hash is not None and cur_hash == prev_hash:
            streak += 1
        else:
            streak = 0
        prev_hash = cur_hash
        rec["state_hash"] = cur_hash
        rec["unchanged_streak"] = streak
        iterations.append(rec)

        # REFLEXION — record a lesson from this failure
        if reflexion_enabled and episodic_page:
            state_moved = None
            if cur_hash is not None:
                state_moved = streak == 0  # streak 0 here means hash differed from prev
            append_lesson(episodic_page, it, verify_cmd, exit_code, state_moved)

        # GUARD 3 — no-progress (state-hash unchanged for K consecutive iterations)
        if no_progress_k and cur_hash is not None and streak >= no_progress_k:
            verdict, reason = NO_PROGRESS, (
                f"state-hash unchanged for {no_progress_k} consecutive iterations"
            )
            break
        # GUARD 4 — escalate-to-human (soft cap: hand off, don't silently give up)
        if escalate_after_iter and it >= escalate_after_iter:
            verdict, reason = ESCALATE, (
                f"reached escalate_after_iter={escalate_after_iter} — handing off to a human"
            )
            break

        # CRITIQUE → REVISE: THE QUARANTINED ADAPTER.
        # Real system: revise_cmd invokes the LLM (read verify output → edit code).
        # Default: stub/no-op so the loop runs deterministically without any LLM.
        if revise_cmd:
            r_exit, r_tail = _run_cmd(revise_cmd, cwd)
            rec["revise_exit"] = r_exit
            rec["revise_output_tail"] = r_tail
        else:
            rec["revise_exit"] = None  # no-op stub (LLM adapter not wired)

    log = {
        "tool": "loop-runner",
        "verdict": verdict,
        "reason": reason,
        "iterations_run": it,
        "verify_cmd": verify_cmd,
        "revise_cmd": revise_cmd,
        "guards": {
            "max_iter": max_iter,
            "budget_seconds": budget_seconds,
            "no_progress_k": no_progress_k,
            "escalate_after_iter": escalate_after_iter,
        },
        "state_paths": state_paths,
        "started_at": started_at,
        "ended_at": _now_iso(),
        "elapsed_s": round(clock() - start, 4),
        "iterations": iterations,
    }
    if log_path:
        lp = Path(log_path)
        lp.parent.mkdir(parents=True, exist_ok=True)
        lp.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not quiet:
        _print_summary(log, log_path)
    return log


def _print_summary(log, log_path):
    print(f"\nLoopRunner verdict: {log['verdict']}  ({log['reason']})")
    print(f"  iterations run : {log['iterations_run']}   elapsed: {log['elapsed_s']}s")
    for r in log["iterations"]:
        sh = (r.get("state_hash") or "—")
        sh = sh[:8] if sh != "—" else sh
        print(
            f"  iter {r['iter']}: verify exit={r['verify_exit']} "
            f"state={sh} streak={r.get('unchanged_streak', 0)}"
        )
    if log_path:
        print(f"  run-log: {log_path}")


# ── Config loading + CLI override merge ─────────────────────────────────────
def load_config(path):
    cfg = json.loads(json.dumps(DEFAULTS))  # deep copy of defaults
    if not path:
        return cfg
    p = Path(path)
    if not p.exists():
        print(f"[loop-runner] config not found: {path} — using built-in defaults", file=sys.stderr)
        return cfg
    if yaml is None:
        print("[loop-runner] PyYAML missing — using built-in defaults", file=sys.stderr)
        return cfg
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    for section, vals in data.items():
        if isinstance(vals, dict) and isinstance(cfg.get(section), dict):
            cfg[section].update(vals)
        else:
            cfg[section] = vals
    return cfg


def cmd_run(args):
    cfg = load_config(args.config)
    g = cfg["guards"]
    settings = dict(
        verify_cmd=args.verify,
        revise_cmd=args.revise if args.revise is not None else cfg["revise"].get("cmd"),
        max_iter=args.max_iter if args.max_iter is not None else g["max_iter"],
        budget_seconds=args.budget_seconds if args.budget_seconds is not None else g["budget_seconds"],
        no_progress_k=args.no_progress_k if args.no_progress_k is not None else g["no_progress_k"],
        escalate_after_iter=args.escalate_after if args.escalate_after is not None else g["escalate_after_iter"],
        state_paths=args.state if args.state else cfg["progress"].get("state_paths") or [],
        episodic_page=args.episodic if args.episodic is not None else cfg["reflexion"].get("episodic_memory_page"),
        reflexion_enabled=cfg["reflexion"].get("enabled", True),
        cwd=args.cwd,
        log_path=args.log if args.log is not None else cfg["run_log"].get("path"),
        quiet=args.quiet,
    )
    log = run_loop(**settings)
    return EXIT_CODE.get(log["verdict"], 1)


# ── Embedded unit self-test (no LLM, no external deps) ──────────────────────
def _py(code):
    """Build a shell cmd running an inline python snippet with the SAME interpreter."""
    return f'{sys.executable} -c {json.dumps(code)}'


def _scenario(name, **kw):
    quiet = kw.pop("_quiet", True)
    log = run_loop(quiet=quiet, **kw)
    return name, log


def selftest():
    results = []
    fake = {"n": 0}

    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        episodic = d / "episodic.md"  # redirected: self-test NEVER touches the real wiki

        # 1) SUCCESS — counter file; verify passes on the 3rd call. Verify mutates
        #    the counter, so the state-hash moves each iter → no-progress can't fire.
        counter = d / "counter"
        counter.write_text("0")
        verify_pass3 = _py(
            "import pathlib,sys;"
            f"p=pathlib.Path({json.dumps(str(counter))});"
            "n=int(p.read_text() or 0)+1;p.write_text(str(n));"
            "sys.exit(0 if n>=3 else 1)"
        )
        results.append(_scenario(
            "SUCCESS@3", verify_cmd=verify_pass3, revise_cmd=None,
            max_iter=10, no_progress_k=2, state_paths=[str(counter)],
            episodic_page=str(episodic), cwd=str(d),
        ))

        # 2) MAX_ITER — verify never passes; revise APPENDS a line each iter so the
        #    state-hash moves → no-progress never fires → only max_iter stops it.
        work = d / "work.txt"
        work.write_text("")
        verify_fail = _py("import sys;sys.exit(1)")
        revise_touch = _py(
            "import pathlib,time;"
            f"p=pathlib.Path({json.dumps(str(work))});"
            "p.write_text(p.read_text()+f'edit-{time.time_ns()}\\n')"
        )
        results.append(_scenario(
            "MAX_ITER@3", verify_cmd=verify_fail, revise_cmd=revise_touch,
            max_iter=3, no_progress_k=2, state_paths=[str(work)],
            episodic_page=str(episodic), cwd=str(d),
        ))

        # 3) NO_PROGRESS — verify never passes; revise is a no-op stub → state frozen
        #    → unchanged for k=2 consecutive iters → stops at iter 3.
        frozen = d / "frozen.txt"
        frozen.write_text("constant")
        results.append(_scenario(
            "NO_PROGRESS@3", verify_cmd=verify_fail, revise_cmd=None,
            max_iter=10, no_progress_k=2, state_paths=[str(frozen)],
            episodic_page=str(episodic), cwd=str(d),
        ))

        # 4) TIMEOUT — fake clock; wall-clock budget enforced without sleeping.
        def fake_clock():
            fake["n"] += 1
            return (fake["n"] - 1) * 3  # 0,3,6,9,... seconds
        results.append(_scenario(
            "TIMEOUT", verify_cmd=verify_fail, revise_cmd=None,
            max_iter=100, no_progress_k=0, budget_seconds=5,
            state_paths=[], cwd=str(d), clock=fake_clock,
        ))

        # 5) ESCALATE — soft cap hands off to a human at iter 2.
        results.append(_scenario(
            "ESCALATE@2", verify_cmd=verify_fail, revise_cmd=None,
            max_iter=100, no_progress_k=0, escalate_after_iter=2,
            state_paths=[], cwd=str(d),
        ))

        episodic_written = episodic.exists()

    # Assertions (required scenarios 1-3 + guard-proof scenarios 4-5)
    expect = {
        "SUCCESS@3": (SUCCESS, 3),
        "MAX_ITER@3": (MAX_ITER, 3),
        "NO_PROGRESS@3": (NO_PROGRESS, 3),
        "TIMEOUT": (TIMEOUT, None),
        "ESCALATE@2": (ESCALATE, 2),
    }
    print("LoopRunner self-test (no LLM) — deterministic guard scenarios\n" + "-" * 62)
    ok = True
    for name, log in results:
        want_verdict, want_iter = expect[name]
        got_iter = log["iterations_run"]
        passed = log["verdict"] == want_verdict and (want_iter is None or got_iter == want_iter)
        ok = ok and passed
        tag = "PASS" if passed else "FAIL"
        iters = f"iter={got_iter}" + (f"/exp {want_iter}" if want_iter is not None else "")
        print(f"  [{tag}] {name:<14} verdict={log['verdict']:<11} {iters:<14} ({log['reason']})")
    print("-" * 62)
    print(f"  reflexion: episodic page written by failing runs = {episodic_written}")
    print(f"  RESULT: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


# ── Entry point ─────────────────────────────────────────────────────────────
def build_parser():
    p = argparse.ArgumentParser(
        prog="loop-runner.py",
        description="Deterministic guardrailed agent-loop driver (propose→verify→revise + guards).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="run the guarded loop around a VERIFY shell command")
    r.add_argument("--verify", required=True, help="shell cmd; exit 0 == pass (e.g. 'pytest -q')")
    r.add_argument("--config", default=None, help="path to loop-runner.config.yaml")
    r.add_argument("--revise", default=None, help="shell cmd for the (adapter) revise step; default = config/no-op")
    r.add_argument("--state", action="append", default=None, help="state-hash path/glob (repeatable)")
    r.add_argument("--log", default=None, help="run-log JSON output path")
    r.add_argument("--max-iter", type=int, default=None)
    r.add_argument("--budget-seconds", type=float, default=None)
    r.add_argument("--no-progress-k", type=int, default=None)
    r.add_argument("--escalate-after", type=int, default=None)
    r.add_argument("--episodic", default=None, help="episodic-memory wiki page for reflexion lessons")
    r.add_argument("--cwd", default=".", help="working directory for verify/revise commands")
    r.add_argument("--quiet", action="store_true")
    r.set_defaults(func=cmd_run)

    s = sub.add_parser("selftest", help="run 5 deterministic guard scenarios (no LLM)")
    s.set_defaults(func=lambda _a: selftest())
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
