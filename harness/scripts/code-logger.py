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


# ─── Cost Attribution (Trụ 1 Outer Harness) ──────────────────────────────────
# build-now-adapt-later: ĐƠN GIÁ token là ẩn số (đổi theo provider/thời điểm) → nhốt vào
# harness/cost-rates.json (verified:false). Engine không bao giờ hardcode con số "đúng"; nó
# dùng DEFAULT_RATES để chạy được ngay, file override (nếu có) đè lên. USD trên 1 TRIỆU token.
DEFAULT_RATES = {  # ASSUMPTION (not verified) — sửa trong harness/cost-rates.json
    "opus":   {"in": 15.0, "out": 75.0, "cache_write": 18.75, "cache_read": 1.50},
    "sonnet": {"in": 3.0,  "out": 15.0, "cache_write": 3.75,  "cache_read": 0.30},
    "haiku":  {"in": 1.0,  "out": 5.0,  "cache_write": 1.25,  "cache_read": 0.10},
    "_default": {"in": 15.0, "out": 75.0, "cache_write": 18.75, "cache_read": 1.50},
}


def _load_rates(root: Path) -> dict:
    rates = {k: dict(v) for k, v in DEFAULT_RATES.items()}
    try:
        f = root / "harness" / "cost-rates.json"
        if f.is_file():
            ov = json.loads(f.read_text(encoding="utf-8"))
            for k, v in (ov.get("rates") or {}).items():
                if isinstance(v, dict):
                    rates.setdefault(k, {}).update(v)
    except Exception:
        pass
    return rates


def _rates_verified(root: Path) -> bool:
    try:
        f = root / "harness" / "cost-rates.json"
        return bool(f.is_file() and json.loads(f.read_text(encoding="utf-8")).get("_verified"))
    except Exception:
        return False


def _rate_for(model: str, rates: dict) -> dict:
    m = (model or "").lower()
    for key in rates:
        if key not in ("_default",) and key in m:
            return rates[key]
    return rates.get("_default", DEFAULT_RATES["_default"])


def _cost_path(root: Path) -> Path:
    p = root / "harness" / "metrics"
    p.mkdir(parents=True, exist_ok=True)
    gi = root / ".gitignore"
    try:
        if not gi.exists() or "harness/metrics/cost-by-session.json" not in gi.read_text(encoding="utf-8", errors="ignore"):
            with open(gi, "a", encoding="utf-8") as f:
                f.write("harness/metrics/cost-by-session.json\n")
    except Exception:
        pass
    return p / "cost-by-session.json"


def run_cost(root, transcript: str, session: str = "") -> dict:
    """Đọc transcript JSONL của 1 RUN, cộng token theo model, quy ra cost (đơn giá adapter),
    rồi UPSERT 1 bản ghi theo session vào cost-by-session.json (idempotent — Stop bắn nhiều lần
    không nhân đôi). Đây là Trụ 1 Cost Attribution: 1 dòng cost / 1 run. Fail-open."""
    try:
        root = Path(root)
        tp = Path(transcript)
        if not tp.is_file():
            return {}
        rates = _load_rates(root)
        per_model = {}   # model → {input_tokens, output_tokens, cache_creation, cache_read}
        seen = {}        # message id → usage (dedupe streamed updates, lấy bản cuối)
        first_ts = last_ts = None
        for ln in tp.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                o = json.loads(ln)
            except Exception:
                continue
            if o.get("type") != "assistant":
                continue
            msg = o.get("message") or {}
            u = msg.get("usage") or {}
            if not u:
                continue
            mid = msg.get("id") or o.get("uuid") or id(o)
            seen[mid] = (msg.get("model") or "?", u)
            ts = o.get("timestamp") or o.get("ts")
            if ts:
                first_ts = first_ts or ts
                last_ts = ts
        for model, u in seen.values():
            acc = per_model.setdefault(model, {"input_tokens": 0, "output_tokens": 0,
                                               "cache_creation": 0, "cache_read": 0})
            acc["input_tokens"] += int(u.get("input_tokens") or 0)
            acc["output_tokens"] += int(u.get("output_tokens") or 0)
            acc["cache_creation"] += int(u.get("cache_creation_input_tokens") or 0)
            acc["cache_read"] += int(u.get("cache_read_input_tokens") or 0)
        if not per_model:
            return {}
        cost = 0.0
        totals = {"input_tokens": 0, "output_tokens": 0, "cache_creation": 0, "cache_read": 0}
        for model, t in per_model.items():
            r = _rate_for(model, rates)
            cost += (t["input_tokens"] * r["in"] + t["output_tokens"] * r["out"]
                     + t["cache_creation"] * r["cache_write"] + t["cache_read"] * r["cache_read"]) / 1_000_000
            for k in totals:
                totals[k] += t[k]
        rec = {
            "session": session or tp.stem,
            "project": root.resolve().name,
            "models": sorted(per_model),
            "turns": len(seen),
            "tokens": totals,
            "cost_usd": round(cost, 4),
            "rates_verified": _rates_verified(root),
            "first_ts": first_ts,
            "last_ts": last_ts,
        }
        cp = _cost_path(root)
        try:
            ledger = json.loads(cp.read_text(encoding="utf-8")) if cp.is_file() else {}
        except Exception:
            ledger = {}
        ledger[rec["session"]] = rec  # upsert: 1 run = 1 dòng, luôn mới
        cp.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")
        return rec
    except Exception:
        return {}


def cost_summary(root) -> None:
    """Break down cost theo project/model/run từ cost-by-session.json (Trụ 1)."""
    root = Path(root)
    try:
        ledger = json.loads(_cost_path(root).read_text(encoding="utf-8"))
    except Exception:
        print("cost-by-session.json: chưa có dữ liệu")
        return
    from collections import defaultdict
    by_proj = defaultdict(lambda: [0.0, 0])
    by_model = defaultdict(float)
    total = 0.0
    for r in ledger.values():
        c = float(r.get("cost_usd") or 0)
        total += c
        by_proj[r.get("project", "?")][0] += c
        by_proj[r.get("project", "?")][1] += 1
        for m in r.get("models", []):
            by_model[m] += c
    unverified = any(not r.get("rates_verified") for r in ledger.values())
    print(f"Cost Attribution — {len(ledger)} run, tổng ${total:.2f} USD"
          + ("  ⚠️ đơn giá CHƯA verify (DEFAULT_RATES)" if unverified else ""))
    print("  theo project:")
    for p, (c, n) in sorted(by_proj.items(), key=lambda x: -x[1][0]):
        print(f"    ${c:8.2f}  {n:3d} run  {p}")
    print("  theo model:")
    for m, c in sorted(by_model.items(), key=lambda x: -x[1]):
        print(f"    ${c:8.2f}  {m}")


def main() -> None:
    args = sys.argv[1:]
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if "--root" in args:
        i = args.index("--root")
        root = Path(args[i + 1])
        del args[i:i + 2]
    if "--run-cost" in args:
        def _opt(name):
            for a in args:
                if a.startswith(name + "="):
                    return a.split("=", 1)[1]
            return ""
        rec = run_cost(root, _opt("--transcript"), _opt("--session"))
        print(f"run.cost: ${rec.get('cost_usd')} ({rec.get('turns')} turns)" if rec else "skip (no transcript/usage)")
    elif "--cost-summary" in args:
        cost_summary(root)
    elif "--render-md" in args:
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
