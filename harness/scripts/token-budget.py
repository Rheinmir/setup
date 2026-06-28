#!/usr/bin/env python3
"""token-budget — a per-session / per-task token + dollar governor (2026 AI-FinOps trend).

Providers cap spend only at org/project granularity; agents need per-session/per-task caps, and
no agent framework ships one. This counts tokens by code, sums per session, computes $ from
configured rates, and warns/blocks when a cap is crossed.

  record SESSION --in N --out M [--model X] [--task T]   append usage (BY CODE, fail-open).
  --report                                               per-session totals + $ + over-cap flag.
  check SESSION                                          exit 2 if over cap AND mode:block.
  --self-test                                            deterministic cost + cap logic in temp dir.

The ONE adapter = harness/token-budget.config.yaml (rates, budgets, mode — verified:false).
Counting + cost math are deterministic, built now. Rates + caps are the unknowns; default
mode 'warn' so an un-tuned cap never kills a session.
"""
import json
import os
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

_FALLBACK = {"verified": False, "mode": "warn",
             "budgets": {"per_session_tokens": 2000000, "per_task_usd": 5.0},
             "rates": {"default": {"input": 0.003, "output": 0.015}}}


def _metrics_file(root: Path) -> Path:
    return root / "harness" / "metrics" / "tokens.jsonl"


def _config_file(root: Path) -> Path:
    return root / "harness" / "token-budget.config.yaml"


def _ensure_gitignored(root: Path) -> None:
    try:
        (root / "harness" / "metrics").mkdir(parents=True, exist_ok=True)
        gi = root / ".gitignore"
        cur = gi.read_text(encoding="utf-8", errors="ignore") if gi.exists() else ""
        if "harness/metrics/tokens.jsonl" not in cur:
            with open(gi, "a", encoding="utf-8") as f:
                f.write("\n# token-budget local usage log\nharness/metrics/tokens.jsonl\n")
    except Exception:
        pass


def load_config(root: Path) -> dict:
    cfg = json.loads(json.dumps(_FALLBACK))
    try:
        import yaml
        data = yaml.safe_load(_config_file(root).read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for k, v in data.items():
                if v is not None:
                    cfg[k] = v
    except Exception:
        pass
    return cfg


def cost_usd(in_tok, out_tok, model, rates) -> float:
    """Deterministic $ from tokens. Unknown model -> 'default' rate."""
    r = rates.get(model) or rates.get("default") or {"input": 0, "output": 0}
    return (in_tok / 1000.0) * float(r.get("input", 0)) + (out_tok / 1000.0) * float(r.get("output", 0))


def record(root, session, in_tok, out_tok, model=None, task=None) -> dict:
    root = Path(root)
    rec = {"session": session or "default", "in": int(in_tok or 0), "out": int(out_tok or 0),
           "model": model or "default", "task": task or ""}
    try:
        _ensure_gitignored(root)
        with open(_metrics_file(root), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass
    return rec


def _read(root: Path):
    try:
        lines = _metrics_file(root).read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    out = []
    for ln in lines:
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    return out


def totals(root, cfg):
    rates = cfg.get("rates", {})
    by_sess = defaultdict(lambda: {"in": 0, "out": 0, "usd": 0.0})
    for r in _read(Path(root)):
        s = by_sess[r.get("session", "default")]
        s["in"] += int(r.get("in", 0)); s["out"] += int(r.get("out", 0))
        s["usd"] += cost_usd(int(r.get("in", 0)), int(r.get("out", 0)), r.get("model", "default"), rates)
    return by_sess


def over_budget(sess_row, cfg):
    """Returns list of breached caps (empty = within budget)."""
    b = cfg.get("budgets", {})
    out = []
    if sess_row["in"] + sess_row["out"] > int(b.get("per_session_tokens", 1e18)):
        out.append(f"session tokens {sess_row['in']+sess_row['out']} > cap {b.get('per_session_tokens')}")
    if sess_row["usd"] > float(b.get("per_task_usd", 1e18)):
        out.append(f"session ${sess_row['usd']:.2f} > cap ${b.get('per_task_usd')}")
    return out


def report(root) -> str:
    cfg = load_config(Path(root))
    by = totals(root, cfg)
    out = [f"TokenBudget — {len(by)} session(s)  (mode={cfg.get('mode')}, verified={cfg.get('verified')})"]
    for s, row in sorted(by.items()):
        flag = " ⚠ OVER" if over_budget(row, cfg) else ""
        out.append(f"  {s:<16} in={row['in']:<9} out={row['out']:<9} ${row['usd']:.3f}{flag}")
    return "\n".join(out)


def self_test() -> int:
    cfg = {"verified": True, "mode": "block",
           "budgets": {"per_session_tokens": 1000, "per_task_usd": 0.05},
           "rates": {"default": {"input": 0.003, "output": 0.015}, "opus": {"input": 0.015, "output": 0.075}}}
    c = cost_usd(1000, 1000, "opus", cfg["rates"])           # 0.015 + 0.075 = 0.09
    cost_ok = abs(c - 0.09) < 1e-9
    within = over_budget({"in": 100, "out": 100, "usd": 0.01}, cfg)
    over = over_budget({"in": 800, "out": 800, "usd": 0.2}, cfg)   # tokens 1600>1000, $0.2>0.05
    ok = cost_ok and not within and len(over) == 2
    print("token-budget self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def _opt(args, flag):
    if flag in args:
        i = args.index(flag); v = args[i + 1] if len(args) > i + 1 else None; del args[i:i + 2]; return v
    return None


def main() -> None:
    args = sys.argv[1:]
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    r = _opt(args, "--root")
    if r:
        root = Path(r)
    in_tok = _opt(args, "--in"); out_tok = _opt(args, "--out"); model = _opt(args, "--model"); task = _opt(args, "--task")
    if "--self-test" in args:
        sys.exit(self_test())
    if "--report" in args:
        print(report(root)); return
    if args and args[0] == "record":
        if len(args) < 2:
            print("usage: token-budget.py record SESSION --in N --out M [--model X]", file=sys.stderr); sys.exit(2)
        rec = record(root, args[1], in_tok or 0, out_tok or 0, model, task)
        print(f"recorded {rec['session']}: in={rec['in']} out={rec['out']} model={rec['model']}"); return
    if args and args[0] == "check":
        if len(args) < 2:
            print("usage: token-budget.py check SESSION", file=sys.stderr); sys.exit(2)
        cfg = load_config(root)
        row = totals(root, cfg).get(args[1], {"in": 0, "out": 0, "usd": 0.0})
        breaches = over_budget(row, cfg)
        if not breaches:
            print(f"[token-budget] {args[1]} within budget (${row['usd']:.3f})"); sys.exit(0)
        msg = f"[token-budget] {args[1]} OVER: " + "; ".join(breaches)
        if str(cfg.get("mode")).lower() == "block" and cfg.get("verified") is True:
            print(msg + "  (mode:block)", file=sys.stderr); sys.exit(2)
        print(msg + "  (mode:warn — set mode:block + verified:true to enforce)", file=sys.stderr); sys.exit(0)
    print(__doc__)


if __name__ == "__main__":
    main()
