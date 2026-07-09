#!/usr/bin/env python3
"""br-queue — resumable RUN QUEUE for /br run (GH#15).

A queue file (br/queue.yaml) is a LIST of frames to run. Each entry points at a
frame and — optionally — a prompt: either `prompt_file` (a template path) or
`prompt` (inline text written straight into the queue). The driver runs entries in
order, writes each entry's outcome (status/verdict/commit) BACK to the queue file
after every run, so re-running the queue SKIPS `done` entries and continues where it
left off (resume).

DETERMINISTIC (built + selftested here): parsing the queue, resolving each entry's
prompt (inline > prompt_file > default template), skip-done resume logic, and writing
the queue back. QUARANTINED (verified:false): the per-frame run itself (loop-runner +
`claude -p` revise) — injected as `runner_fn` so the queue logic is testable without a
model.

Usage:
  br-queue.py run  --queue br/queue.yaml [--root .] [--stop-on-fail] [--dry-run]
  br-queue.py list --queue br/queue.yaml
  br-queue.py selftest
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

_HERE = Path(__file__).resolve()
_REPO = _HERE.parents[2]
_FL = _HERE.with_name("frame-lint.py")
_spec = importlib.util.spec_from_file_location("frame_lint", _FL)
_frame_lint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_frame_lint)
parse_frontmatter = _frame_lint.parse_frontmatter

DEFAULT_TEMPLATE = _REPO / "skills" / "br" / "assets" / "revise-prompt.md"
LOOP_RUNNER = _REPO / "harness" / "scripts" / "loop-runner.py"
BR_REVISE = _REPO / "fdk" / "tools" / "br-revise.py"
_QHEADER = ("# QUEUE prompt cho /br run — driver: fdk/tools/br-queue.py (resumable).\n"
            "# status: pending|done|failed do driver TỰ cập nhật. Chạy lại = bỏ qua done, chạy tiếp.\n")


def load_queue(path):
    if yaml is None:
        raise RuntimeError("PyYAML required to read the queue file")
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or []
    if not isinstance(data, list):
        raise ValueError("queue must be a YAML list of entries")
    return data


def save_queue(path, entries):
    body = yaml.safe_dump(entries, allow_unicode=True, sort_keys=False, default_flow_style=False)
    Path(path).write_text(_QHEADER + body, encoding="utf-8")


def resolve_prompt(entry, tmpdir, idx):
    """inline `prompt` > `prompt_file` > default template. Returns a template path."""
    inline = entry.get("prompt")
    if inline is not None and str(inline).strip():
        p = Path(tmpdir) / f"entry-{idx}.prompt.md"
        p.write_text(str(inline), encoding="utf-8")
        return str(p), "inline"
    pf = entry.get("prompt_file")
    if pf:
        return str(pf), "prompt_file"
    return str(DEFAULT_TEMPLATE), "default"


def _default_runner(entry, frame_fm, template_path, root):
    """Per-frame run — delegates to br-run (frame-lint gate + clean-tree check +
    bookkeeping commit, so 40 frames in a row don't pollute each other's commits).
    Optional entry field `revise_cmd:` overrides the LLM adapter (stubs/tests)."""
    fid = frame_fm.get("frame_id", "frame")
    frame_path = entry["frame"] if Path(entry["frame"]).is_absolute() else str(Path(root) / entry["frame"])
    cmd = ["python3", str(_HERE.with_name("br-run.py")), "run", frame_path,
           "--root", str(root), "--template", str(template_path)]
    if entry.get("revise_cmd"):
        cmd += ["--revise-cmd", str(entry["revise_cmd"])]
    subprocess.run(cmd, capture_output=True, text=True)
    log_path = Path(root) / "br" / "frames" / f"{fid}.run.json"
    if log_path.exists():
        d = json.loads(log_path.read_text(encoding="utf-8"))
        return {"verdict": d.get("verdict"), "commit": d.get("commit"),
                "scope_clean": d.get("scope_clean"), "changed_files": d.get("changed_files")}
    return {"verdict": "ERROR", "commit": None}


def run_queue(queue_path, root=".", stop_on_fail=False, dry_run=False, runner_fn=None):
    entries = load_queue(queue_path)
    runner_fn = runner_fn or _default_runner
    ran, skipped = 0, 0
    with tempfile.TemporaryDirectory() as td:
        for i, entry in enumerate(entries):
            fid = entry.get("frame", f"#{i}")
            if entry.get("status") == "done":
                skipped += 1
                print(f"  [skip] {fid} (done)")
                continue
            tmpl, src = resolve_prompt(entry, td, i)
            if dry_run:
                print(f"  [plan] {fid}  prompt={src}:{tmpl}")
                continue
            try:
                frame_fm = parse_frontmatter(Path(root, entry["frame"]).read_text(encoding="utf-8")) \
                    if not Path(entry["frame"]).is_absolute() else parse_frontmatter(Path(entry["frame"]).read_text(encoding="utf-8"))
            except (OSError, ValueError, KeyError) as e:
                entry["status"] = "failed"; entry["verdict"] = f"frame-load-error: {e}"
                save_queue(queue_path, entries)
                print(f"  [FAIL] {fid}: cannot load frame — {e}")
                if stop_on_fail:
                    break
                continue
            res = runner_fn(entry, frame_fm, tmpl, root)
            ran += 1
            verdict = res.get("verdict")
            entry["status"] = "done" if verdict == "SUCCESS" else "failed"
            entry["verdict"] = verdict
            entry["commit"] = res.get("commit")
            save_queue(queue_path, entries)     # write-back after EACH entry → resumable
            # bookkeeping: the write-back dirties the tree, which would make br-run REFUSE
            # the next frame (clean-tree gate). Commit the queue state right away.
            # NOTE: `(root/".git").exists()` only holds when --root IS the repo top-level;
            # for a nested --root (e.g. br/payroll inside a bigger repo, no .git of its
            # own) this was always False and the commit silently never ran, leaving
            # queue.yaml dirty forever after the first frame (bug found running the
            # payroll pipeline, GH#15 — same "assume root == repo root" class as the
            # loop-runner path-prefix bugs).
            in_repo = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                                     cwd=str(root), capture_output=True, text=True
                                     ).stdout.strip() == "true"
            if in_repo:
                subprocess.run(["git", "add", str(Path(queue_path).resolve())], cwd=str(root),
                               capture_output=True, text=True)
                subprocess.run(["git", "commit", "-q", "--no-verify", "-m",
                                f"chore(queue): {fid} → {entry['status']}"], cwd=str(root),
                               capture_output=True, text=True)
            tag = "done" if entry["status"] == "done" else "FAIL"
            print(f"  [{tag}] {fid}: {verdict} (prompt={src})")
            if entry["status"] == "failed" and stop_on_fail:
                print("  (stop-on-fail: dừng, chạy lại queue để tiếp tục sau khi sửa)")
                break
    print("-" * 56)
    print(f"  queue: ran={ran} · skipped(done)={skipped} · total={len(entries)}")
    return 0


def list_queue(queue_path):
    for i, e in enumerate(load_queue(queue_path)):
        print(f"  {i}. {e.get('frame')}  [{e.get('status','pending')}]"
              + (f"  verdict={e.get('verdict')}" if e.get('verdict') else "")
              + (f"  @{str(e.get('commit'))[:8]}" if e.get('commit') else ""))
    return 0


def selftest():
    ok = True
    if yaml is None:
        print("  [FAIL] PyYAML missing"); return 1
    with tempfile.TemporaryDirectory() as td:
        root = Path(td); (root / "br" / "frames").mkdir(parents=True)
        def frame(fid):
            (root / "br" / "frames" / f"{fid}.md").write_text(
                "---\nschema_version: 0\nframe_id: %s\ncreated_by: human\nparent_br: BR.md\n"
                "clause_ids: [S1.1]\nparent_br_hash: x\nmuc_tieu: \"m\"\nscope_code: [\"src/**\"]\n"
                "scope_test: [\"tests/**\"]\nacceptance_test: \"true\"\n---\n# %s\n" % (fid, fid),
                encoding="utf-8")
        for f in ("f1", "f2", "f3"):
            frame(f)
        q = root / "queue.yaml"
        save_queue(q, [
            {"frame": "br/frames/f1.md", "status": "pending"},
            {"frame": "br/frames/f2.md", "prompt": "inline {{muc_tieu}}", "status": "pending"},
            {"frame": "br/frames/f3.md", "status": "done"},   # already done → must be skipped
        ])
        # fake runner: f1 succeeds, f2 fails (records what prompt source it saw)
        seen = {}
        def fake(entry, fm, tmpl, root_):
            seen[fm["frame_id"]] = Path(tmpl).read_text(encoding="utf-8")
            return {"verdict": "SUCCESS" if fm["frame_id"] == "f1" else "NO_PROGRESS",
                    "commit": "abc123" if fm["frame_id"] == "f1" else None}
        run_queue(str(q), root=str(root), runner_fn=fake)
        after = load_queue(q)
        checks = [
            ("f1 → done", after[0]["status"] == "done" and after[0]["commit"] == "abc123"),
            ("f2 → failed", after[1]["status"] == "failed" and after[1]["verdict"] == "NO_PROGRESS"),
            ("f3 stayed done (skipped)", after[2]["status"] == "done"),
            ("f2 used INLINE prompt (raw, rendered later by br-revise)", "inline {{muc_tieu}}" in seen.get("f2", "")),
            ("f3 never ran (skip-done)", "f3" not in seen),
        ]
        # RESUME: fix f2 to succeed, re-run → only f2 runs (f1/f3 done), queue completes
        seen.clear()
        def fake2(entry, fm, tmpl, root_):
            seen[fm["frame_id"]] = tmpl
            return {"verdict": "SUCCESS", "commit": "def456"}
        run_queue(str(q), root=str(root), runner_fn=fake2)
        after2 = load_queue(q)
        checks += [
            ("resume ran ONLY f2", set(seen) == {"f2"}),
            ("f2 now done after resume", after2[1]["status"] == "done" and after2[1]["commit"] == "def456"),
            ("f1 untouched on resume", after2[0]["commit"] == "abc123"),
        ]
    print("br-queue self-test — resumable queue logic (fake runner)\n" + "-" * 56)
    for name, good in checks:
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] {name}")
    print("-" * 56)
    print(f"  RESULT: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


def build_parser():
    p = argparse.ArgumentParser(prog="br-queue.py", description="Resumable run queue for /br run.")
    sub = p.add_subparsers(dest="cmd")
    r = sub.add_parser("run", help="run pending entries in order (skips done); writes status back")
    r.add_argument("--queue", required=True)
    r.add_argument("--root", default=".")
    r.add_argument("--stop-on-fail", action="store_true")
    r.add_argument("--dry-run", action="store_true", help="print the plan (which prompt each entry uses)")
    r.set_defaults(func=lambda a: run_queue(a.queue, a.root, a.stop_on_fail, a.dry_run))
    l = sub.add_parser("list", help="show queue entries + status")
    l.add_argument("--queue", required=True)
    l.set_defaults(func=lambda a: list_queue(a.queue))
    s = sub.add_parser("selftest", help="deterministic resumable-queue checks (fake runner)")
    s.set_defaults(func=lambda a: selftest())
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not getattr(args, "func", None):
        build_parser().parse_args(["--help"]); return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
