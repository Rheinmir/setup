#!/usr/bin/env python3
"""L1/Stop: trước khi Claude kết thúc lượt — nếu phiên có sửa wiki thì index.md phải khớp (R3).
Exit 2 = chặn dừng, Claude phải sửa index trước. Có guard chống lặp vô hạn."""
import subprocess
import sys

from hooklib import audit, find_validators, find_wiki_dir, project_dir, read_payload, run_validator


def wiki_changed(root: str) -> bool:
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root, capture_output=True, text=True, timeout=10,
        ).stdout
        return "wiki/" in out
    except Exception:
        return False


def main() -> None:
    payload = read_payload()
    audit(payload, "Stop")

    if payload.get("stop_hook_active"):
        sys.exit(0)  # đã block một lần rồi → không lặp vô hạn

    root = project_dir(payload)
    if not wiki_changed(root):
        sys.exit(0)  # phiên không đụng wiki → không can thiệp

    wiki = find_wiki_dir(root)
    vdir = find_validators(root)
    if wiki is None or vdir is None:
        sys.exit(0)

    rc, err = run_validator("index_sync.py", {"action": "stop", "wiki_dir": str(wiki)}, vdir)
    if rc == 2:
        print(err, file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
