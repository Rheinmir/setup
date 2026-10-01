#!/usr/bin/env python3
"""P1 no-bulk-stage — nhiều phiên dev framework chung MỘT working tree: cấm stage hàng loạt, cấm commit file phiên khác.

Issue 030726-multi-session-add-guard (2 sự cố thật 03/07/2026: `git add -A` của phiên này cuốn file dang dở
của phiên kia vào commit, và ngược lại).
  1. Chặn `git add -A|--all|.` và `git commit -a|-am…` → stage pathspec tường minh của việc mình chạm.
  2. Lệnh có `git commit` (event có `session`): file sắp commit (staged + pathspec `git add` trong cùng lệnh)
     mà lần GHI CUỐI trong harness/metrics/events.jsonl thuộc session KHÁC → chặn, nêu tên file + session.
     Cố ý commit hộ phiên khác: đặt OVS_ALLOW_CROSS_SESSION=1 trong lệnh.

Contract: stdin JSON {action:"bash", command, session?, root?} · exit 0 pass · exit 2 block · lỗi → fail-open.
"""
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

BULK_ADD = re.compile(r"\bgit\s+add\s+(?:[^;&|]*\s)?(?:-A|--all|\.)(?=\s|$|;|&|\|)")
COMMIT_ALL = re.compile(r"\bgit\s+commit\s+(?:[^;&|]*\s)?-(?:a|am|[a-z]*a[a-z]*)(?=\s|$)")
ALLOW = "OVS_ALLOW_CROSS_SESSION=1"


def _explicit_adds(cmd: str) -> set:
    out = set()
    for seg in re.split(r"&&|;|\|\|", cmd):
        try:
            t = shlex.split(seg)
        except ValueError:
            continue
        if len(t) > 2 and t[0] == "git" and t[1] == "add":
            out |= {a for a in t[2:] if not a.startswith("-") and a != "--"}
    return out


def _targets(cmd: str, root: Path) -> Path:
    """Repo mà lệnh commit nhắm tới: `cd X &&` / `git -C X`. Khác cây chung (vd worktree riêng) → không kiểm chéo phiên."""
    m = re.search(r"\bgit\s+-C\s+(\S+)", cmd) or re.match(r"\s*cd\s+(\S+)\s*(?:&&|;)", cmd)
    d = Path(m.group(1).strip("'\"")).expanduser() if m else root
    return (d if d.is_absolute() else root / d).resolve()


def _last_writer(root: Path) -> dict:
    last = {}
    ev = root / "harness" / "metrics" / "events.jsonl"
    if not ev.is_file():
        return last
    for line in ev.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("event") == "file.write" and e.get("path") and e.get("session"):
            last[e["path"]] = e["session"]
    return last


def check(ev: dict) -> list:
    cmd = ev.get("command", "") or ""
    if ev.get("action") != "bash" or "git" not in cmd:
        return []
    problems = []
    if BULK_ADD.search(cmd) or COMMIT_ALL.search(cmd):
        problems.append("stage hàng loạt (git add -A/./--all hoặc commit -a) — repo có nhiều phiên chung cây, "
                        "hãy `git add <đúng các file mình sửa>`")
    sess = (ev.get("session") or "")[:8]
    root = Path(ev.get("root") or os.getcwd())
    if sess and re.search(r"\bgit\s+commit\b", cmd) and ALLOW not in cmd and _targets(cmd, root) == root.resolve():
        try:
            staged = set(subprocess.run(["git", "-C", str(root), "diff", "--cached", "--name-only"],
                                        capture_output=True, text=True, timeout=10).stdout.split())
        except Exception:
            staged = set()
        last = _last_writer(root)
        foreign = sorted(f"{p} (phiên {last[p]})" for p in staged | _explicit_adds(cmd)
                         if p in last and last[p] != sess)
        if foreign:
            problems.append("sắp commit file mà phiên KHÁC ghi lần cuối: " + ", ".join(foreign[:8])
                            + (f" … +{len(foreign) - 8}" if len(foreign) > 8 else "")
                            + f" — bỏ khỏi stage, hoặc thêm {ALLOW} nếu cố ý commit hộ")
    return problems


def main() -> None:
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    try:
        problems = check(ev)
    except Exception:
        sys.exit(0)
    if problems:
        print("[P1 no-bulk-stage] " + "; ".join(problems), file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
