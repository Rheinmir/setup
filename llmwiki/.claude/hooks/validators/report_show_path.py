#!/usr/bin/env python3
"""R16 report-show-path: HTML report/visualization phải tự khai đường dẫn của mình.

File HTML dưới llmwiki/html/ (trừ archive/, assets/) phải chứa đường dẫn tuyệt đối
của chính nó trong nội dung (footer/titlebar) — người xem biết file nằm đâu để mở lại/sửa.
Nguồn: feedback user 020726 ("file đâu để coi path là gì") + rule skill fdk.

Contract: stdin JSON {"action":"write","file_path":...} hoặc argv files. Exit 0/2.
"""
import json
import sys
from pathlib import Path

SKIP_PARTS = {"archive", "assets"}


def is_report_html(path: str) -> bool:
    p = (path or "").replace("\\", "/")
    if not p.endswith(".html"):
        return False
    if "llmwiki/html/" not in p:
        return False
    rel = p.split("llmwiki/html/", 1)[1]
    return not any(part in SKIP_PARTS for part in Path(rel).parts[:-1])


def check(path: str) -> None:
    if not is_report_html(path):
        return
    try:
        content = Path(path).read_text(encoding="utf-8")
    except OSError:
        return
    abs_path = str(Path(path).resolve())
    if abs_path not in content:
        print(
            f"[R16 report-show-path] {path} khong chua duong dan tuyet doi cua chinh no "
            f"({abs_path}) — them footer/titlebar dang <code>{abs_path}</code> "
            f"de nguoi xem biet file nam dau (rule skill fdk, feedback 020726).",
            file=sys.stderr,
        )
        sys.exit(2)


def main() -> None:
    args = sys.argv[1:]
    if args:
        for p in args:
            check(p)
        sys.exit(0)
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if ev.get("action") == "write":
        check(ev.get("file_path", ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
