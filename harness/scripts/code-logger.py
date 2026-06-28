#!/usr/bin/env python3
"""code-logger — ghi log framework BẰNG CODE, không phụ thuộc agent nhớ.

Vấn đề: AGENT.md/CLAUDE.md bảo "ALWAYS append to wiki/log.md after every operation" —
nhưng đó là kỷ luật con-người/agent, agent QUÊN là chuyện thường → log.md drift, không
phản ánh thực tế. Cùng họ với `hooklib.audit()` (đã ghi raw event BẰNG CODE) và
`harness-events.py _machine_log` ("model không thể quên log"). code-logger nâng cấp ý đó
cho LOG NGHIỆP VỤ (curated), không chỉ raw audit:

1. record(root, event, **fields)  — gọi TỪ HOOK (PostToolUse…). Append 1 dòng JSONL vào
   harness/metrics/events.jsonl. Đây là "sổ cái" framework: mọi thay đổi file framework
   được CODE ghi lại, không nhờ agent. (events.jsonl gitignored — lịch sử local thô.)
2. render_md(root)  — sinh lại block <!-- log:auto:start --> … <!-- log:auto:end --> trong
   llmwiki/wiki/log.md từ events.jsonl. Gọi từ Stop hook → phần "log gần đây" của log.md là
   CODE-generated; phần curated người viết NẰM NGOÀI marker được giữ nguyên.

CLI: code-logger.py [--root DIR] [--tail N | --summary | --render-md | --record EVENT k=v ...]
Fail-open TUYỆT ĐỐI: logging không bao giờ được làm gãy phiên (mọi lỗi → nuốt).
"""
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

AUTO_START = "<!-- log:auto:start -->"
AUTO_END = "<!-- log:auto:end -->"
# loại file framework đáng log (bỏ qua audit/, html render, file tạm)
FRAMEWORK_PREFIXES = ("llmwiki/", "harness/", "skills/", "fdk/", ".github/", ".pre-commit-config")


def _events_path(root: Path) -> Path:
    p = root / "harness" / "metrics"
    p.mkdir(parents=True, exist_ok=True)
    # events.jsonl = lịch sử local thô → gitignore
    gi = root / ".gitignore"
    try:
        if not gi.exists() or "harness/metrics/events.jsonl" not in gi.read_text(encoding="utf-8", errors="ignore"):
            with open(gi, "a", encoding="utf-8") as f:
                f.write("\n# code-logger raw event history (local)\nharness/metrics/events.jsonl\n")
    except Exception:
        pass
    return p / "events.jsonl"


def is_framework_file(rel: str) -> bool:
    rel = (rel or "").replace("\\", "/").lstrip("./")
    return rel.endswith((".md", ".py", ".sh", ".yaml", ".yml", ".json")) and rel.startswith(FRAMEWORK_PREFIXES)


def record(root, event: str, **fields) -> None:
    """Append 1 event vào sổ cái — gọi từ hook. Fail-open."""
    try:
        root = Path(root)
        rec = {"ts": datetime.now().isoformat(timespec="seconds"), "event": event}
        rec.update({k: v for k, v in fields.items() if v is not None})
        with open(_events_path(root), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _read_events(root: Path, limit: int = 0):
    try:
        lines = _events_path(root).read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    out = []
    for ln in lines:
        try:
            out.append(json.loads(ln))
        except Exception:
            continue
    return out[-limit:] if limit else out


def render_md(root, keep: int = 40) -> bool:
    """Sinh lại auto-block trong wiki/log.md từ events.jsonl. Giữ nguyên text ngoài marker. Fail-open."""
    try:
        root = Path(root)
        log = root / "llmwiki" / "wiki" / "log.md"
        if not log.is_file():
            return False
        evs = _read_events(root, keep)
        if not evs:
            return False
        lines = [AUTO_START, "", "### 🤖 Log tự-động (code-logger, không do agent ghi)", "",
                 "| Thời điểm | Event | Chi tiết |", "|---|---|---|"]
        for e in evs:
            ts = e.get("ts", "").replace("T", " ")
            det = e.get("path") or e.get("file") or e.get("detail") or ""
            extra = " · ".join(f"{k}={v}" for k, v in e.items() if k not in ("ts", "event", "path", "file", "detail"))
            cell = (str(det) + (" · " + extra if extra else "")).replace("|", "\\|")[:120]
            lines.append(f"| {ts} | `{e.get('event','')}` | {cell} |")
        lines += ["", AUTO_END]
        block = "\n".join(lines)
        text = log.read_text(encoding="utf-8")
        if AUTO_START in text and AUTO_END in text:
            pre = text.split(AUTO_START)[0]
            post = text.split(AUTO_END, 1)[1]
            new = pre.rstrip() + "\n\n" + block + post
        else:
            new = text.rstrip() + "\n\n" + block + "\n"
        log.write_text(new, encoding="utf-8")
        return True
    except Exception:
        return False


def main() -> None:
    args = sys.argv[1:]
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if "--root" in args:
        i = args.index("--root")
        root = Path(args[i + 1])
        del args[i:i + 2]
    if "--render-md" in args:
        ok = render_md(root)
        print("rendered log.md auto-block" if ok else "skip (no events / no log.md)")
    elif "--summary" in args:
        evs = _read_events(root)
        from collections import Counter
        c = Counter(e.get("event", "?") for e in evs)
        print(f"events.jsonl: {len(evs)} dòng")
        for k, n in c.most_common():
            print(f"  {n:4d}  {k}")
    elif "--record" in args:
        i = args.index("--record")
        ev = args[i + 1] if len(args) > i + 1 else "manual"
        fields = dict(a.split("=", 1) for a in args[i + 2:] if "=" in a)
        record(root, ev, **fields)
        print(f"recorded: {ev} {fields}")
    else:  # --tail N (default 20)
        n = 20
        if "--tail" in args:
            j = args.index("--tail")
            if len(args) > j + 1 and args[j + 1].isdigit():
                n = int(args[j + 1])
        for e in _read_events(root, n):
            print(json.dumps(e, ensure_ascii=False))


if __name__ == "__main__":
    main()
