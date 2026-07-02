#!/usr/bin/env python3
"""wiki-core v2 Bước 1: ledger sự kiện wiki — máy ghi, máy đọc (draft 020726-wiki-core-relations).

Mỗi thao tác Write/Edit vào file nội dung wiki append MỘT dòng JSON vào
`<wiki_dir>/ledger.jsonl`. Guardrail G1 (council 020726): append qua fcntl.flock
(khóa độc quyền) để nhiều phiên/agent ghi song song không interleave dòng.

Quy ước tombstone (thay xóa cứng): file đổi frontmatter `type: tombstone`
→ ledger ghi action "delete". File chưa được git theo dõi → "add", còn lại "modify".

Fail-open: ledger không bao giờ được phép làm gãy phiên làm việc (giống audit).
"""
import datetime
import json
import pathlib
import re
import subprocess

try:
    import fcntl  # POSIX only — Windows adapter sẽ thay bằng msvcrt (chưa cần)
except ImportError:
    fcntl = None

FRONTMATTER_RE = re.compile(r"^---[ \t]*\n(.*?)\n---", re.DOTALL)
TYPE_LINE_RE = re.compile(r"^type[ \t]*:[ \t]*(\S.*?)[ \t]*$", re.MULTILINE)
CONTENT_DIRS = ("concepts/", "entities/", "sources/", "draft/", "architecture/", "tours/")


def wiki_dir_of(fp: str):
    """Trả thư mục wiki chứa file (segment .../wiki/) nếu file là nội dung wiki, else None."""
    p = pathlib.PurePosixPath(str(fp).replace("\\", "/"))
    parts = p.parts
    for i in range(len(parts) - 1, 0, -1):
        if parts[i - 1] == "wiki":
            rel = "/".join(parts[i:])
            if rel.endswith(".md") and rel.startswith(CONTENT_DIRS):
                return pathlib.Path(*parts[: i]), rel
            return None
    return None


def detect_action(root: str, fp: str) -> str:
    """delete (tombstone) > add (git chưa theo dõi) > modify."""
    try:
        text = pathlib.Path(fp).read_text(encoding="utf-8", errors="ignore")
        m = FRONTMATTER_RE.match(text)
        if m:
            t = TYPE_LINE_RE.search(m.group(1))
            if t and t.group(1).strip().strip("'\"") == "tombstone":
                return "delete"
    except OSError:
        pass
    try:
        rc = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--error-unmatch", fp],
            capture_output=True, timeout=5,
        ).returncode
        return "modify" if rc == 0 else "add"
    except Exception:
        return "modify"


def append_event(root: str, fp: str, tool: str, session_id=None) -> None:
    """Append 1 sự kiện vào <wiki_dir>/ledger.jsonl dưới flock. Fail-open."""
    try:
        hit = wiki_dir_of(fp)
        if hit is None:
            return
        wiki_dir, rel = hit
        rec = {
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
            "session": (session_id or "")[:8] or None,
            "action": detect_action(root, fp),
            "target": rel,
            "tool": tool,
        }
        rec = {k: v for k, v in rec.items() if v is not None}
        line = json.dumps(rec, ensure_ascii=False) + "\n"
        ledger = pathlib.Path(wiki_dir) / "ledger.jsonl"
        # G1: khóa độc quyền quanh append — nhiều process ghi song song không xé dòng
        with open(ledger, "a", encoding="utf-8") as f:
            if fcntl is not None:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(line)
                f.flush()
            finally:
                if fcntl is not None:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception:
        pass  # ledger không bao giờ làm gãy phiên
