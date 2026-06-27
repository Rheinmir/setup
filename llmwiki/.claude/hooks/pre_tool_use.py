#!/usr/bin/env python3
"""L1/PreToolUse: chặn trước khi tool chạy. Exit 2 = block, stderr được đưa lại cho Claude."""
import os
import subprocess
import sys

from hooklib import find_validators, project_dir, read_payload, run_validator

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


def _gate1(root: str) -> None:
    """R12 gate1: pull-before-change. Chỉ chạy trong repo framework (có pull-gate.sh);
    fail-open mọi lỗi hạ tầng (offline/timeout/không git). Block (exit 2) khi local SAU remote."""
    if not root:
        return
    script = os.path.join(root, "harness", "poc-vendor-neutral", "bin", "pull-gate.sh")
    if not os.path.isfile(script):
        return  # không phải repo framework → bỏ qua
    try:
        r = subprocess.run(["bash", script, "gate1"], cwd=root,
                           capture_output=True, text=True, timeout=20)
    except Exception:
        return  # offline/timeout → fail-open
    if r.returncode == 2:
        sys.stderr.write((r.stdout or "") + (r.stderr or ""))
        sys.exit(2)


def main() -> None:
    payload = read_payload()
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input") or {}
    root = project_dir(payload)
    vdir = find_validators(root)
    if vdir is None:
        sys.exit(0)  # không tìm thấy validators → fail-open, còn L2 đỡ

    if tool in WRITE_TOOLS:
        _gate1(root)  # R12 gate1 — pull trước khi sửa framework (fail-open ngoài repo framework)
        event = {
            "action": "write",
            "file_path": ti.get("file_path", ""),
            "content": ti.get("content") or ti.get("new_string") or "",
        }
        checks = ["no_write_raw.py", "folder_structure.py"]
    elif tool == "Bash":
        event = {"action": "bash", "command": ti.get("command", "")}
        checks = ["no_write_raw.py"]
    else:
        sys.exit(0)

    for name in checks:
        rc, err = run_validator(name, event, vdir)
        if rc == 2:
            print(err, file=sys.stderr)
            sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
