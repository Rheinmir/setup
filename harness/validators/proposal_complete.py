#!/usr/bin/env python3
"""R7 proposal-complete: proposal chờ duyệt phải khai đủ ai làm gì + seq diagram từng task.

Scope: file .md trong wiki draft dir, CÓ section '## Plan', Status còn 'proposed'.
Output-report (không có Plan) và draft đã implemented/done tự miễn.

Điều kiện:
  (a) Bảng '## Agent Task Assignment' ≥1 data row, không ô Agent nào trống
  (b) Link '**Sequence diagram**' trỏ tới file .html TỒN TẠI
  (c) Số '<div class="diagram-box"' trong html ≥ số task '- [ ]' trong '## Plan'
  (d) html KHÔNG ẩn nhãn message bằng 'opacity:0' (.msg phải hiện sẵn — bài học 130626)
  (e) html có ≥1 prose 'class="desc"' mỗi diagram (đọc hiểu không cần animation)

Contract chung: stdin JSON {"action":"write","file_path":...} hoặc argv files. Exit 0/2.
"""
import json
import re
import sys
from pathlib import Path

DRAFT_RE = re.compile(r"(?:^|/)wiki/(?:draft|sources/draft)(?:/|$)")
STATUS_RE = re.compile(r"^\*\*Status:\*\*(.*)$", re.MULTILINE | re.IGNORECASE)
SEQ_LINK_RE = re.compile(r"\*\*Sequence diagram[^*]*\*\*:?\s*\[[^\]]*\]\(([^)]+\.html)\)", re.IGNORECASE)
TASK_RE = re.compile(r"^\s*-\s*\[[ xX]\]", re.MULTILINE)
DIAGRAM_RE = re.compile(r'<div\s+class="diagram-box"')
# nhãn message bị ẩn cứng: rule CSS .msg{...opacity:0...} — chỉ hiện qua JS (bài học 130626).
# Scope vào selector .msg để không bắt nhầm opacity:0 của ripple/animation khác.
HIDDEN_MSG_RE = re.compile(r"\.msg\b[^{}]*\{[^}]*opacity:\s*0\s*[;}]")
DESC_STATIC_RE = re.compile(r'class="desc"')          # prose tĩnh <p class="desc">
DESC_DATA_RE = re.compile(r"\bdesc\s*:\s*['\"`]")     # prose trong data JS: desc:'...'


def section(text, title):
    m = re.search(rf"^##\s+{re.escape(title)}\s*$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None


def is_in_scope(path):
    p = (path or "").replace("\\", "/")
    return p.endswith(".md") and DRAFT_RE.search(p) and Path(p).name not in ("README.md", "_template.md")


def check(path):
    if not is_in_scope(path):
        return
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return

    plan = section(text, "Plan")
    if plan is None:
        return  # output-report / draft không phải plan → miễn
    m = STATUS_RE.search(text)
    status = (m.group(1) if m else "").lower()
    if "proposed" not in status or "implement" in status or "done" in status:
        return  # đã qua gate / đã làm xong → miễn

    problems = []

    # (a) Agent Task Assignment
    agent_sec = section(text, "Agent Task Assignment")
    if agent_sec is None:
        problems.append("(a) thieu section '## Agent Task Assignment' — phai khai task nao do AI/CLI nao lam NGAY LUC PROPOSE")
    else:
        rows = [l for l in agent_sec.splitlines() if l.strip().startswith("|") and "---" not in l]
        data = rows[1:] if rows else []  # bỏ header
        if not data:
            problems.append("(a) bang Agent Task Assignment khong co data row nao")
        else:
            for l in data:
                cells = [c.strip() for c in l.strip().strip("|").split("|")]
                if len(cells) < 2 or not cells[1]:
                    problems.append(f"(a) row thieu o Agent: {l.strip()[:80]}")
                    break

    # (b) + (c) sequence html
    n_tasks = len(TASK_RE.findall(plan))
    mlink = SEQ_LINK_RE.search(text)
    if not mlink:
        problems.append("(b) thieu link '**Sequence diagram**: [..](...html)' trong draft")
    else:
        html_path = (Path(path).parent / mlink.group(1)).resolve()
        if not html_path.is_file():
            problems.append(f"(b) seq html khong ton tai: {mlink.group(1)}")
        else:
            html_text = html_path.read_text(encoding="utf-8", errors="replace")
            n_diagrams = len(DIAGRAM_RE.findall(html_text))
            if n_tasks and n_diagrams < n_tasks:
                problems.append(
                    f"(c) Plan co {n_tasks} task nhung seq html chi co {n_diagrams} diagram-box — "
                    f"MOI task phai co sequence diagram rieng"
                )
            # (d) khong duoc an nhan message — doc ra phai thay chu ngay, khong cho animation reveal
            if HIDDEN_MSG_RE.search(html_text):
                problems.append(
                    "(d) seq html an nhan bang 'opacity:0' — nhan message PHAI hien san "
                    "(.msg opacity >=.82), animation chi lam noi buoc dang chay. Bai hoc 130626."
                )
            # (e) moi diagram phai co 1 doan prose doc hieu khong can xem animation —
            #     dem ca prose tinh (<p class="desc">) lan prose render tu data JS (desc:'...')
            n_desc = max(len(DESC_STATIC_RE.findall(html_text)), len(DESC_DATA_RE.findall(html_text)))
            if n_diagrams and n_desc < n_diagrams:
                problems.append(
                    f"(e) seq html co {n_diagrams} diagram nhung chi {n_desc} doan prose 'class=\"desc\"' — "
                    f"MOI task can 1 doan mo ta text (ai lam gi, du lieu chay, nhanh an toan)"
                )

    if problems:
        print(
            f"[R7 proposal-complete] {path} chua du chuan de hoi duyet:\n  - " + "\n  - ".join(problems),
            file=sys.stderr,
        )
        sys.exit(2)


def main():
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
