#!/usr/bin/env python3
"""L1/PreToolUse: chặn trước khi tool chạy. Exit 2 = block, stderr được đưa lại cho Claude."""
import sys

from hooklib import find_validators, project_dir, read_payload, run_validator

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


def main() -> None:
    payload = read_payload()
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input") or {}
    vdir = find_validators(project_dir(payload))
    if vdir is None:
        sys.exit(0)  # không tìm thấy validators → fail-open, còn L2 đỡ

    if tool in WRITE_TOOLS:
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
