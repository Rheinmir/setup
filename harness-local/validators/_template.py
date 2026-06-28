#!/usr/bin/env python3
"""P<n> <ten> — <mô tả rule project>. COPY file này thành <ten>.py rồi sửa `check()`.

Contract (framework cam kết ỔN ĐỊNH — xem harness-local/README.md):
  - Input: stdin JSON {action,file_path,content,command}  HOẶC  argv là đường dẫn file.
  - exit 0 = PASS · exit 2 = BLOCK (in lý do ra stderr) · lỗi bất ngờ → fail-open (exit 0).
File bắt đầu bằng '_' (như file này) bị runner BỎ QUA → an toàn để làm mẫu.
"""
import json
import sys
from pathlib import Path


def check(path: str, content: str = "") -> list:
    """Trả list lý do vi phạm (rỗng = pass). SỬA logic ở đây."""
    problems = []
    # VÍ DỤ — xoá/thay bằng rule của bạn:
    # if path.endswith(".js") and "console.log(" in content:
    #     problems.append(f"{path}: còn console.log (gỡ trước khi commit)")
    return problems


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    problems = []
    if args:  # pre-commit / CI: argv là file đổi
        for p in args:
            try:
                problems += check(p, Path(p).read_text(encoding="utf-8", errors="replace"))
            except OSError:
                pass
    else:     # hook: stdin JSON event
        try:
            ev = json.load(sys.stdin)
        except Exception:
            sys.exit(0)
        if ev.get("action") == "write":
            problems += check(ev.get("file_path", ""), ev.get("content", "") or "")
    if problems:
        print("[P? <ten>] " + "; ".join(problems), file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)  # fail-open tuyệt đối
