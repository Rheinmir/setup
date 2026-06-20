#!/usr/bin/env python3
"""L1/PostToolUse: audit log (R4) + kiểm '## Origin' (R2) sau khi file đã ghi.
Exit 2 → stderr đưa lại cho Claude để tự sửa ngay trong phiên."""
import sys

from hooklib import audit, find_validators, project_dir, read_payload, run_validator


def main() -> None:
    payload = read_payload()
    audit(payload, "PostToolUse")

    tool = payload.get("tool_name", "")
    if tool not in {"Write", "Edit", "MultiEdit"}:
        sys.exit(0)
    fp = (payload.get("tool_input") or {}).get("file_path", "")
    if not fp.endswith(".md"):
        sys.exit(0)
    vdir = find_validators(project_dir(payload))
    if vdir is None:
        sys.exit(0)

    # không truyền content → validator đọc file đã ghi trên disk (trạng thái cuối)
    for name in ("origin_required.py", "okf_frontmatter.py", "proposal_complete.py"):
        rc, err = run_validator(name, {"action": "write", "file_path": fp}, vdir)
        if rc == 2:
            print(err, file=sys.stderr)
            sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
