#!/usr/bin/env python3
"""L1/PostToolUse: audit log (R4) + kiểm '## Origin' (R2) sau khi file đã ghi.
Exit 2 → stderr đưa lại cho Claude để tự sửa ngay trong phiên."""
import os
import sys

from hooklib import audit, code_log, find_validators, project_dir, read_payload, run_validator


def main() -> None:
    payload = read_payload()
    audit(payload, "PostToolUse")

    tool = payload.get("tool_name", "")
    if tool not in {"Write", "Edit", "MultiEdit"}:
        sys.exit(0)
    root = project_dir(payload)
    fp = (payload.get("tool_input") or {}).get("file_path", "")

    # code-logger: ghi MỌI thay đổi file framework BẰNG CODE (không nhờ agent nhớ log)
    rel = os.path.relpath(fp, root) if fp else ""
    if rel and not rel.startswith("..") and rel.startswith(("llmwiki/", "harness/", "skills/", "fdk/", ".github/")):
        code_log(root, "--record", "file.write", f"path={rel}", f"tool={tool}")

    # wiki-core v2: ledger sự kiện wiki (add/modify/delete-tombstone), flock chống ghi song song (G1)
    if fp:
        try:
            from wiki_ledger import append_event
            append_event(root, fp, tool, payload.get("session_id"))
        except Exception:
            pass  # fail-open

    vdir = find_validators(root)
    if vdir is None:
        sys.exit(0)

    # R16: HTML report phải tự khai đường dẫn của mình
    if fp.endswith(".html"):
        rc, err = run_validator("report_show_path.py", {"action": "write", "file_path": fp}, vdir)
        if rc == 2:
            print(err, file=sys.stderr)
            sys.exit(2)
        sys.exit(0)

    if not fp.endswith(".md"):
        sys.exit(0)

    # không truyền content → validator đọc file đã ghi trên disk (trạng thái cuối)
    for name in ("origin_required.py", "okf_frontmatter.py", "proposal_complete.py"):
        rc, err = run_validator(name, {"action": "write", "file_path": fp}, vdir)
        if rc == 2:
            print(err, file=sys.stderr)
            sys.exit(2)

    # R-rel (warn-only, G4): kiểm toàn vẹn tham chiếu relations — in cảnh báo, không chặn
    rc, err = run_validator("rel_integrity.py", {"action": "write", "file_path": fp}, vdir)
    if err:
        print(err, file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
