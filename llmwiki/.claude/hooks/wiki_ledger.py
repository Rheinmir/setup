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


def detect_action(root: str, fp: str, wiki_dir=None, rel=None) -> str:
    """delete (tombstone) > add (chưa từng thấy) > modify.

    Nguồn chân lý ưu tiên là git (file đã theo dõi = modify, chưa = add). Nếu git KHÔNG
    có mặt (vd container slim, máy không cài git) thì KHÔNG mù quáng trả 'modify' — fallback
    tự chứa: quét ledger xem `rel` đã từng xuất hiện chưa (chưa = add). Bug này do stress
    container bắt được (python:3.11-slim không có git) — xem break-task-stress T1-01.
    """
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
        if rc == 0:
            return "modify"            # git xác nhận file đã theo dõi → sửa
        # rc != 0: file chưa track HOẶC thư mục không phải git repo (rc 128).
        # Không thể tin "add" mù quáng — dùng ledger fallback: đã thấy rel chưa?
    except FileNotFoundError:
        pass                          # git không cài — cũng rơi xuống fallback
    except Exception:
        return "modify"
    # Fallback tự chứa (git vắng / không-repo / chưa-track): lần đầu thấy `rel` = add
    if wiki_dir is not None and rel is not None:
        ledger = pathlib.Path(wiki_dir) / "ledger.jsonl"
        try:
            needle = json.dumps(rel, ensure_ascii=False)
            for ln in ledger.read_text(encoding="utf-8").splitlines():
                if needle in ln:
                    return "modify"
        except OSError:
            pass
    return "add"


ID_LINE_RE = re.compile(r"^id[ \t]*:[ \t]*(\S.*?)[ \t]*$", re.MULTILINE)
REL_TO_RE = re.compile(r"\{[^}]*\brel[ \t]*:[ \t]*[\w-]+[^}]*\bto[ \t]*:[ \t]*([\w./-]+)[^}]*\}")


def _page_id(text: str, stem: str) -> str:
    m = FRONTMATTER_RE.match(text)
    if m:
        i = ID_LINE_RE.search(m.group(1))
        if i:
            return i.group(1).strip().strip("'\"")
    return stem


def propagate_stale(wiki_dir, rel, action, session_id=None) -> int:
    """G2 (council 020726): lan truyền stale ĐÚNG 1 BƯỚC, không đệ quy.

    Trang `rel` bị modify/delete → mọi trang có relations.to == id(rel) bị đánh
    stale trong <wiki_dir>/stale.json (kèm by/ts). Chính trang vừa sửa được XÓA
    cờ stale (nó vừa tươi lại). Không lan tiếp từ trang bị đánh dấu (cap=1 —
    chống stale-storm, miễn nhiễm chu trình by construction). Trả số trang đánh dấu.
    """
    wiki_dir = pathlib.Path(wiki_dir)
    target = pathlib.Path(wiki_dir) / rel
    try:
        tid = _page_id(target.read_text(encoding="utf-8", errors="ignore"), target.stem)
    except OSError:
        tid = target.stem
    marked = []
    if action in ("modify", "delete"):
        for d in CONTENT_DIRS:
            base = wiki_dir / d.rstrip("/")
            if not base.is_dir():
                continue
            for p in base.rglob("*.md"):
                prel = p.relative_to(wiki_dir).as_posix()
                if prel == rel:
                    continue
                try:
                    head = p.read_text(encoding="utf-8", errors="ignore")[:2000]
                except OSError:
                    continue
                m = FRONTMATTER_RE.match(head)
                if m and tid in {t for t in REL_TO_RE.findall(m.group(1))}:
                    marked.append(prel)
    stale_path = wiki_dir / "stale.json"
    lock_path = wiki_dir / ".stale.lock"
    with open(lock_path, "w") as lk:
        if fcntl is not None:
            fcntl.flock(lk.fileno(), fcntl.LOCK_EX)
        try:
            try:
                stale = json.loads(stale_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                stale = {}
            stale.pop(rel, None)  # trang vừa ghi = tươi
            ts = datetime.datetime.now().isoformat(timespec="seconds")
            for prel in marked:
                stale[prel] = {"by": rel, "action": action, "ts": ts,
                               "session": (session_id or "")[:8] or None}
            stale_path.write_text(json.dumps(stale, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        finally:
            if fcntl is not None:
                fcntl.flock(lk.fileno(), fcntl.LOCK_UN)
    return len(marked)


def append_event(root: str, fp: str, tool: str, session_id=None) -> None:
    """Append 1 sự kiện vào <wiki_dir>/ledger.jsonl dưới flock. Fail-open."""
    try:
        hit = wiki_dir_of(fp)
        if hit is None:
            return
        wiki_dir, rel = hit
        action = detect_action(root, fp, wiki_dir, rel)
        rec = {
            "ts": datetime.datetime.now().isoformat(timespec="seconds"),
            "session": (session_id or "")[:8] or None,
            "action": action,
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
        n = propagate_stale(wiki_dir, rel, action, session_id)
        if n:
            print(f"[wiki-core] {n} trang trỏ tới '{rel}' đã đánh dấu stale (xem {wiki_dir}/stale.json)")
    except Exception:
        pass  # ledger không bao giờ làm gãy phiên
