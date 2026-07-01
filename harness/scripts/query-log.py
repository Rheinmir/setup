#!/usr/bin/env python3
"""query-log — telemetry BẰNG CODE cho skill `query` (mảnh 1 của gói L0→L1).

Vấn đề đã xác minh: gọi query KHÔNG ghi dòng nào xác nhận nó chạy → không đo được, không
cải tiến được. Script này là CẢM BIẾN tối thiểu: mỗi lần skill `query` chạy xong, nó append
1 dòng JSONL vào harness/metrics/query-log.jsonl:

    {ts, question, pages_hit:[slug...], tokens_est, tier_reached, note}

GIỚI HẠN CÓ CHỦ ĐÍCH (case xấu #3 "telemetry nói dối" trong proposal):
  query là AGENTIC — model có thể bỏ qua skill, tự Read thẳng. Khi đó không có dòng nào được
  ghi. Vì vậy log này đo TOOL-USAGE (đường query được-gọi + nó tìm ra gì), KHÔNG phải mọi
  retrieval xảy ra trong phiên. Đây là ranh giới đã ghi rõ, không phải bug.

Cùng họ fail-open với code-logger.py / hooklib.audit: telemetry KHÔNG BAO GIỜ được làm gãy
phiên — mọi lỗi đều nuốt, exit 0.

CLI:
  query-log.py --record --question "..." [--pages a,b,c] [--tokens N] [--tier 1|2|3] [--note ...] [--root DIR]
  query-log.py --tail [N] [--root DIR]
  query-log.py --summary [--root DIR]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def _find_root(start: str | None) -> Path:
    # ưu tiên --root; nếu không, leo tìm thư mục có harness/
    p = Path(start).resolve() if start else Path.cwd()
    for cand in [p, *p.parents]:
        if (cand / "harness").is_dir():
            return cand
    return p


def _log_path(root: Path) -> Path:
    d = root / "harness" / "metrics"
    d.mkdir(parents=True, exist_ok=True)
    # query-log.jsonl = lịch sử local thô → gitignore (giống events.jsonl)
    gi = root / ".gitignore"
    try:
        rel = "harness/metrics/query-log.jsonl"
        if not gi.exists() or rel not in gi.read_text(encoding="utf-8", errors="ignore"):
            with open(gi, "a", encoding="utf-8") as f:
                f.write(f"\n{rel}\n")
    except Exception:
        pass
    return d / "query-log.jsonl"


def record(root: Path, question: str, pages: list[str], tokens: int | None, tier: int | None, note: str) -> None:
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "question": (question or "")[:500],
        "pages_hit": [s.strip() for s in pages if s.strip()],
        "tokens_est": tokens,
        "tier_reached": tier,
        "note": note or "",
    }
    with open(_log_path(root), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _read(root: Path) -> list[dict]:
    p = _log_path(root)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def main() -> int:
    ap = argparse.ArgumentParser(prog="query-log")
    ap.add_argument("--root", default=None)
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--question", default="")
    ap.add_argument("--pages", default="")
    # parse tay (không type=int) — giá trị rác → None thay vì argparse hard-exit(2), giữ fail-open
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--tier", default=None)
    ap.add_argument("--note", default="")
    ap.add_argument("--tail", nargs="?", const=10, type=int, default=None)
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()

    root = _find_root(args.root)

    def _as_int(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    if args.record:
        record(root, args.question, args.pages.split(","), _as_int(args.tokens), _as_int(args.tier), args.note)
        return 0

    rows = _read(root)
    if args.summary:
        n = len(rows)
        toks = [r.get("tokens_est") for r in rows if isinstance(r.get("tokens_est"), int)]
        tiers = {}
        for r in rows:
            t = r.get("tier_reached")
            tiers[t] = tiers.get(t, 0) + 1
        print(json.dumps({
            "queries": n,
            "avg_tokens": round(sum(toks) / len(toks), 1) if toks else None,
            "by_tier": tiers,
        }, ensure_ascii=False, indent=2))
        return 0

    if args.tail is not None:
        for r in rows[-args.tail:]:
            print(json.dumps(r, ensure_ascii=False))
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # fail-open tuyệt đối: telemetry không được làm gãy phiên
        sys.exit(0)
