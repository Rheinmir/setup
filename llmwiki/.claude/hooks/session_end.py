#!/usr/bin/env python3
"""L1/SessionEnd: audit + tự sinh dòng tổng kết phiên vào wiki/log.md (R4 bằng máy).
SessionEnd không block được — chỉ ghi nhận."""
import datetime
import json
import pathlib
import sys

from hooklib import audit, find_wiki_dir, project_dir, read_payload


def summarize_today(root: pathlib.Path, session_id: str):
    f = root / ".claude" / "audit" / (datetime.date.today().isoformat() + ".jsonl")
    if not f.is_file():
        return None
    tools = 0
    files = set()
    for line in f.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if session_id and rec.get("session_id") != session_id:
            continue
        if rec.get("event") == "PostToolUse":
            tools += 1
            if rec.get("file_path"):
                files.add(pathlib.Path(rec["file_path"]).name)
    return tools, sorted(files)


def main() -> None:
    payload = read_payload()
    audit(payload, "SessionEnd")

    root = pathlib.Path(project_dir(payload))
    wiki = find_wiki_dir(str(root))
    if wiki is None:
        sys.exit(0)
    summary = summarize_today(root, payload.get("session_id", ""))
    if not summary or summary[0] == 0:
        sys.exit(0)
    tools, files = summary
    sid = (payload.get("session_id") or "")[:8]
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    shown = ", ".join(files[:8]) + (" …" if len(files) > 8 else "")
    line = f"- {stamp} — session `{sid}` — {tools} tool calls — files: {shown or '(none)'}\n"
    try:
        with open(wiki / "log.md", "a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
