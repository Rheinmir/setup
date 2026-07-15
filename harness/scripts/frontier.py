#!/usr/bin/env python3
"""frontier — việc nào LẤY ĐƯỢC bây giờ (tất định, 0 token).

Đọc ledger `ISSUES.md` (nguồn chân lý, không cần mạng) và in ra FRONTIER =
issue *open* ∧ *mọi blocker đã đóng* ∧ *chưa ai claim*. Đây là câu trả lời cho
"giờ lấy việc gì là hợp lệ" — trước đây hệ không trả lời được, nên hai agent
song song có thể ôm cùng một việc.

Cột ledger dùng: id · status · labels · blocked_by (danh sách id, '_(none)_' = rỗng)
                 · claim ('<phiên>@<ts>', '_(none)_' = chưa ai nhận)

Dùng:
  python3 harness/scripts/frontier.py              # mọi issue takeable
  python3 harness/scripts/frontier.py --agent      # chỉ nhãn ready-for-agent (bỏ ready-for-human)
  python3 harness/scripts/frontier.py --map <id>   # chỉ ticket con của một wayfinder map
  python3 harness/scripts/frontier.py --json
"""
import argparse
import json
import re
import sys
from pathlib import Path

LEDGER = Path("llmwiki/wiki/sources/ISSUES.md")
NONE = {"", "_(none)_", "_(ledger-only)_", "-", "—"}


def parse(path):
    """Đọc mọi data-row của bảng markdown (kể cả các đoạn bị mục Origin chen giữa)."""
    rows = []
    header = None
    for line in path.read_text(encoding="utf-8").split("\n"):
        s = line.strip()
        if s.startswith("| id | kind |"):
            header = [c.strip() for c in s.strip("|").split("|")]
            continue
        if not header or not s.startswith("| ["):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < len(header):
            continue
        row = dict(zip(header, cells))
        # id: '[slug](path)' → slug
        m = re.match(r"\[([^\]]+)\]", row.get("id", ""))
        row["_id"] = m.group(1) if m else row.get("id", "")
        rows.append(row)
    return rows


def id_status(rows):
    return {r["_id"]: r.get("status", "").lower() for r in rows}


def deps(cell):
    if cell.strip() in NONE:
        return []
    # tách theo dấu phẩy / khoảng trắng; lấy phần trông như id (chứa chữ-số-gạch)
    return [x.strip().strip("[]") for x in re.split(r"[,\s]+", cell) if x.strip() and x.strip() not in NONE]


def frontier(rows, agent_only=False, map_id=None):
    st = id_status(rows)
    out = []
    for r in rows:
        if r.get("status", "").lower() != "open":
            continue
        if r.get("claim", "").strip() not in NONE:
            continue  # đã có người nhận
        blockers = deps(r.get("blocked_by", ""))
        if any(st.get(b, "open") != "done" for b in blockers):
            continue  # còn blocker chưa đóng
        labels = r.get("labels", "")
        if agent_only and "ready-for-agent" not in labels:
            continue
        if map_id and map_id not in (r.get("blocked_by", "") + r.get("tracker", "") + r.get("labels", "")):
            # ticket con của map: quy ước blocked_by hoặc labels chứa map id (best-effort)
            if map_id not in r.get("_id", ""):
                continue
        out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--agent", action="store_true", help="chỉ ready-for-agent")
    ap.add_argument("--map", default=None, help="chỉ ticket con của wayfinder map <id>")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    path = Path(a.ledger)
    if not path.is_file():
        print(f"frontier: không thấy ledger {path}", file=sys.stderr)
        sys.exit(0)  # fail-open
    rows = parse(path)
    fr = frontier(rows, agent_only=a.agent, map_id=a.map)

    if a.json:
        print(json.dumps([{k: v for k, v in r.items() if not k.startswith("_")} for r in fr],
                         ensure_ascii=False, indent=2))
        sys.exit(0)

    scope = " (ready-for-agent)" if a.agent else ""
    print(f"frontier{scope} · {len(fr)}/{len(rows)} issue lấy được (open ∧ không-bị-chặn ∧ chưa-claim):")
    for r in fr:
        lbl = r.get("labels", "")
        print(f"  {r['_id']:<44} [{lbl}]  {r.get('tiêu đề', '')[:50]}")
    if not fr:
        print("  (không có — mọi issue open đều đang bị chặn hoặc đã có người nhận)")
    print("\nClaim TRƯỚC khi làm: ghi '<phiên>@<ts>' vào ô claim của dòng đó (thao tác GHI ĐẦU TIÊN).")
    sys.exit(0)


if __name__ == "__main__":
    main()
