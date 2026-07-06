#!/usr/bin/env python3
"""br-run — the deterministic /br run driver (GH#15): isolated worktree + wired revise.

Turns "/br run <frame>" from SKILL prose into a real, testable command:
  1. frame-lint the frame (structural).
  2. require a CLEAN working tree.
  3. create an ISOLATED git worktree from the baseline (branch br-run/<frame_id>) — the
     loop only ever touches this worktree, never the user's checkout or main.
  4. run loop-runner with the 6 guards + the revise adapter WIRED to fdk/tools/br-revise.py
     (which renders skills/br/assets/revise-prompt.md and calls `claude -p`).
  5. commit-on-success into the worktree branch (never main); print a one-line summary.
  6. record run_log_ref on the frame so `/br status` picks it up. Human reviews + merges.

DETERMINISTIC (built + selftested): frame load, worktree create/remove, the exact
loop-runner command, run-log summary, frame run_log_ref update. QUARANTINED (verified:
false): the `claude -p` call inside br-revise — injected via --revise-cmd so the whole
driver is selftested end-to-end with a deterministic stub (no model).

Usage:
  br-run.py run <frame.md> [--root .] [--baseline <ref>] [--keep-worktree]
                 [--revise-cmd "<override>"] [--print-prompt]
  br-run.py selftest
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve()
_REPO = _HERE.parents[2]
_FL = _HERE.with_name("frame-lint.py")
_spec = importlib.util.spec_from_file_location("frame_lint", _FL)
_frame_lint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_frame_lint)
parse_frontmatter = _frame_lint.parse_frontmatter
check_frames = _frame_lint.check

LOOP_RUNNER = _REPO / "harness" / "scripts" / "loop-runner.py"
BR_REVISE = _REPO / "fdk" / "tools" / "br-revise.py"
DEFAULT_TEMPLATE = _REPO / "skills" / "br" / "assets" / "revise-prompt.md"


def _git(args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def worktree_clean(root):
    r = _git(["status", "--porcelain"], root)
    return r.returncode == 0 and not r.stdout.strip()


def create_worktree(root, frame_id, baseline):
    wt = Path(root) / ".br-worktrees" / frame_id
    branch = f"br-run/{frame_id}"
    _git(["worktree", "remove", "--force", str(wt)], root)  # best-effort clean of a stale one
    _git(["branch", "-D", branch], root)
    r = _git(["worktree", "add", "-B", branch, str(wt), baseline], root)
    if r.returncode != 0:
        raise RuntimeError(f"git worktree add failed: {r.stderr.strip()}")
    return wt, branch


def remove_worktree(root, wt, branch):
    _git(["worktree", "remove", "--force", str(wt)], root)
    _git(["branch", "-D", branch], root)


def default_revise_cmd(frame_path, atest, vout, cwd, template):
    """The WIRING: loop-runner's --revise → br-revise (renders the prompt, calls claude -p)."""
    return (f'python3 {json.dumps(str(BR_REVISE))} run --frame {json.dumps(str(frame_path))} '
            f'--template {json.dumps(str(template))} --verify {json.dumps(atest)} '
            f'--verify-output {json.dumps(str(vout))} --cwd {json.dumps(str(cwd))}')


def build_loop_command(frame_fm, cwd, baseline, revise_cmd, log_path, vout):
    fid = frame_fm.get("frame_id", "frame")
    atest = frame_fm.get("acceptance_test", "false")
    scope = ",".join(frame_fm.get("scope_code") or [])
    protect = ",".join(frame_fm.get("scope_test") or [])
    clauses = ",".join(frame_fm.get("clause_ids") or [])
    guards = frame_fm.get("guards") or {}
    cmd = [
        "python3", str(LOOP_RUNNER), "run",
        "--verify", atest,
        "--revise", revise_cmd,
        "--state", scope, "--scope", scope, "--protect", protect,
        "--baseline", baseline, "--commit-on-success",
        "--commit-message", f"frame({fid}): {frame_fm.get('muc_tieu','')} [{clauses}]",
        "--confirm", "2",   # hermeticity: a frame's green must reproduce (council 2026-07-06)
        "--log", str(log_path), "--cwd", str(cwd),
    ]
    for flag, key in (("--max-iter", "max_iter"), ("--budget-seconds", "budget_seconds"),
                      ("--no-progress-k", "no_progress_k"), ("--escalate-after", "escalate_after_iter")):
        if key in guards:
            cmd += [flag, str(guards[key])]
    return cmd


def _set_run_log_ref(frame_path, ref):
    """Record run_log_ref on the frame frontmatter (so /br status links it), if absent."""
    text = Path(frame_path).read_text(encoding="utf-8")
    if "run_log_ref:" in text:
        return
    lines = text.splitlines()
    # insert before the SECOND '---' (end of frontmatter)
    seen = 0
    for i, ln in enumerate(lines):
        if ln.strip() == "---":
            seen += 1
            if seen == 2:
                lines.insert(i, f"run_log_ref: {ref}")
                break
    Path(frame_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(frame_path, root=".", baseline=None, keep_worktree=True, revise_cmd=None,
        template=None, print_prompt=False, use_worktree=True):
    root = Path(root).resolve()
    frame_path = Path(frame_path)
    fm = parse_frontmatter(frame_path.read_text(encoding="utf-8"))
    fid = fm.get("frame_id", "frame")
    template = template or DEFAULT_TEMPLATE

    # 1. structural gate
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = check_frames(str(frame_path), str(root), skip_verify=True)
    if rc != 0:
        print(f"[br-run] frame-lint FAILED for {fid}:\n{buf.getvalue()}", file=sys.stderr)
        return 1

    if print_prompt:
        subprocess.run(["python3", str(BR_REVISE), "run", "--frame", str(frame_path),
                        "--template", str(template), "--verify", fm.get("acceptance_test", ""),
                        "--print"])
        return 0

    # 2. clean tree required — in-place mode NEEDS this even more: the frame's commit
    # must contain ONLY the frame's work, and a dirty tree would pollute changed_files.
    if not worktree_clean(root):
        print("[br-run] REFUSING: working tree not clean. Commit/stash first.", file=sys.stderr)
        return 1

    baseline = baseline or _git(["rev-parse", "HEAD"], root).stdout.strip()

    # 3. isolated worktree
    wt, branch = (create_worktree(root, fid, baseline) if use_worktree else (root, None))
    log_path = root / "br" / "frames" / f"{fid}.run.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    vout = Path(wt) / f".{fid}.verify.out"
    rcmd = revise_cmd or default_revise_cmd(frame_path, fm.get("acceptance_test", "false"),
                                            vout, wt, template)
    try:
        # 4. run the guarded loop (revise wired to br-revise / claude -p)
        cmd = build_loop_command(fm, wt, baseline, rcmd, log_path, vout)
        subprocess.run(cmd)
        # 5. summary + record
        result = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else {}
        _set_run_log_ref(frame_path, f"br/frames/{fid}.run.json")
        # FAILED frame (in-place): its half-done RED edits would dirty the tree and block
        # every later frame in the queue (learned at scale: 1 stuck frame ERROR'd 27).
        # Save the attempt as a reviewable patch, then revert the scope → the line flows on.
        if result.get("verdict") != "SUCCESS" and not use_worktree:
            changed = result.get("changed_files") or []
            if changed:
                diff = _git(["diff", "--", *changed], root).stdout
                if diff.strip():
                    patch = root / "br" / "frames" / f"{fid}.failed.patch"
                    patch.write_text(diff, encoding="utf-8")
                    print(f"  bản dở    : lưu {patch.relative_to(root)} (xem lại được) rồi revert scope")
                _git(["checkout", "--", *changed], root)
                for rel in changed:  # untracked leftovers
                    fpath = root / rel
                    tracked = _git(["ls-files", "--error-unmatch", "--", rel], root).returncode == 0
                    if not tracked and fpath.exists():
                        fpath.unlink()
        # bookkeeping commit: run-log + frame's run_log_ref are born AFTER the loop's own
        # commit — without this the tree stays dirty and the NEXT frame refuses to start.
        _git(["add", "br/frames"], root)
        _git(["commit", "-q", "--no-verify", "-m", f"chore({fid}): run-log + run_log_ref"], root)
        # frame files may live outside br/frames (custom layout) — commit the ref change too
        _git(["add", str(frame_path)], root)
        _git(["commit", "-q", "--no-verify", "-m", f"chore({fid}): run_log_ref"], root)
        verdict = result.get("verdict")
        changed = result.get("changed_files") or []
        print("\n──────── /br run — TÓM TẮT ────────")
        print(f"  frame     : {fid}")
        print(f"  verdict   : {verdict}  ({result.get('iterations_run')} vòng)")
        print(f"  file đổi  : {', '.join(changed) or '(không)'}")
        print(f"  scope sạch: {result.get('scope_clean')}"
              + (f"  · ĐỊNH ghi ngoài scope (đã revert): {result.get('attempted_out_of_scope')}"
                 if result.get('attempted_out_of_scope') else ""))
        print(f"  commit    : {result.get('commit')}")
        if use_worktree:
            print(f"  worktree  : {wt}  (branch {branch})")
            print(f"  → NGƯỜI duyệt diff rồi merge: git merge {branch}   ·   hoặc bỏ: git worktree remove --force {wt}")
        else:
            print(f"  chế độ    : IN-PLACE — sửa nằm ngay trong cây hiện tại, bật app xem liền.")
            print(f"  → không ưng: git revert {str(result.get('commit'))[:8] if result.get('commit') else '<commit>'}   ·   lỗi ở đâu: python3 fdk/tools/br-find.py <file-hoặc-từ-khoá>")
        return 0 if verdict == "SUCCESS" else 2
    finally:
        if use_worktree and not keep_worktree:
            remove_worktree(root, wt, branch)


def selftest():
    ok = True
    checks = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _git(["init", "-q"], root); _git(["config", "user.email", "t@t"], root); _git(["config", "user.name", "t"], root)
        (root / "src").mkdir(); (root / "tests").mkdir(); (root / "br" / "frames").mkdir(parents=True)
        (root / "src" / "auth.py").write_text("def login(): return False\n")
        (root / "tests" / "test_auth.py").write_text("def test(): pass\n")
        (root / "BR.md").write_text("clause S4.1\n")
        brh = _frame_lint._sha256_file(root / "BR.md")
        atest = f"{sys.executable} -c \"import sys,pathlib;sys.exit(0 if 'return True' in pathlib.Path('src/auth.py').read_text() else 1)\""
        frame = root / "br" / "frames" / "frame-x.md"
        frame.write_text(
            "---\nschema_version: 0\nframe_id: frame-x\ncreated_by: human\nparent_br: BR.md\n"
            f"clause_ids: [S4.1]\nparent_br_hash: {brh}\nmuc_tieu: \"login true\"\n"
            f"scope_code: [\"src/**\"]\nscope_test: [\"tests/**\"]\nacceptance_test: {json.dumps(atest)}\n"
            "guards:\n  max_iter: 4\n  no_progress_k: 2\n---\n# frame-x\n", encoding="utf-8")
        _git(["add", "-A"], root); _git(["commit", "-q", "-m", "base", "--no-verify"], root)

        # STUB revise (stands in for claude -p): edit the in-scope file so verify passes.
        stub = f"{sys.executable} -c \"import pathlib;pathlib.Path('src/auth.py').write_text('def login(): return True')\""
        rc = run(str(frame), root=str(root), baseline="HEAD", keep_worktree=True,
                 revise_cmd=stub, use_worktree=True)
        log = json.loads((root / "br" / "frames" / "frame-x.run.json").read_text())
        # worktree branch exists + committed there
        branches = _git(["branch", "--list", "br-run/frame-x"], root).stdout
        wt_commit_msg = _git(["log", "-1", "--pretty=%s", "br-run/frame-x"], root).stdout.strip()
        checks = [
            ("run returned success", rc == 0),
            ("verdict SUCCESS", log.get("verdict") == "SUCCESS"),
            ("changed_files ⊆ scope (only src)", log.get("changed_files") == ["src/auth.py"]),
            ("scope_clean True", log.get("scope_clean") is True),
            ("commit made", bool(log.get("commit"))),
            ("worktree branch created", "br-run/frame-x" in branches),
            ("commit on branch has frame message", wt_commit_msg.startswith("frame(frame-x):")),
            ("frame got run_log_ref", "run_log_ref:" in frame.read_text(encoding="utf-8")),
            ("main src untouched (still False)", "return False" in (root / "src" / "auth.py").read_text()),
        ]
        remove_worktree(root, root / ".br-worktrees" / "frame-x", "br-run/frame-x")

        # IN-PLACE mode (the DEFAULT): change lands in the live tree + commits on the
        # CURRENT branch — "bật app lên là thấy", one working tree, no folder hunting.
        (root / "src" / "auth.py").write_text("def login(): return False\n")
        _git(["add", "-A"], root); _git(["commit", "-q", "-m", "reset", "--no-verify"], root)
        rc2 = run(str(frame), root=str(root), baseline="HEAD", revise_cmd=stub, use_worktree=False)
        recent = _git(["log", "-5", "--pretty=%s"], root).stdout
        checks += [
            ("in-place run success", rc2 == 0),
            ("in-place: live tree updated (app sees it)", "return True" in (root / "src" / "auth.py").read_text()),
            ("in-place: frame commit on CURRENT branch", "frame(frame-x):" in recent),
            ("in-place: tree clean after run (bookkeeping committed)", worktree_clean(root)),
        ]

    print("br-run self-test — worktree + wired revise (stub, no model)\n" + "-" * 58)
    for name, good in checks:
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] {name}")
    print("-" * 58)
    print(f"  RESULT: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


def build_parser():
    p = argparse.ArgumentParser(prog="br-run.py", description="Deterministic /br run driver (isolated worktree + wired revise).")
    sub = p.add_subparsers(dest="cmd")
    r = sub.add_parser("run", help="run one frame in an isolated worktree")
    r.add_argument("frame")
    r.add_argument("--root", default=".")
    r.add_argument("--baseline", default=None)
    r.add_argument("--keep-worktree", action="store_true", default=True)
    # DEFAULT = IN-PLACE (one working tree — the app you're running sees the change
    # immediately; safety comes from the deterministic guards, not folder isolation).
    # --worktree is the opt-in for when you truly want an isolated copy.
    r.add_argument("--worktree", dest="use_worktree", action="store_true", default=False)
    r.add_argument("--no-worktree", dest="use_worktree", action="store_false")
    r.add_argument("--revise-cmd", default=None, help="override the revise command (default: wired to br-revise.py)")
    r.add_argument("--template", default=None)
    r.add_argument("--print-prompt", action="store_true")
    r.set_defaults(func=lambda a: run(a.frame, a.root, a.baseline, a.keep_worktree,
                                      a.revise_cmd, a.template, a.print_prompt, a.use_worktree))
    s = sub.add_parser("selftest", help="end-to-end worktree run with a deterministic stub revise")
    s.set_defaults(func=lambda a: selftest())
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not getattr(args, "func", None):
        build_parser().parse_args(["--help"]); return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
