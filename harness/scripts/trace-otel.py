#!/usr/bin/env python3
"""trace-otel — turn the flat audit log into structured OpenTelemetry-GenAI spans, then
root-cause a failing run against a golden trace (2026 agent-observability trend).

Today the harness audit log is a flat list of {ts,action,tool,...} events. This builds a
hierarchical span tree in the OTel GenAI shape so a wrong answer at step 10 can be traced to a
tool call at step 3, and a CI gate can flag a run that diverged from a golden trace.

  --emit [events.jsonl]   read events (file or stdin), print OTel-GenAI spans as JSON.
  --root-cause RUN GOLD   print the first span where RUN diverges from GOLD (the causal root).
  --self-test             deterministic build+diff in-memory (fdk-gate BNAL self-test).

The ONE adapter = harness/trace-otel.config.yaml (attribute_map, span_name_field,
regression.threshold — verified:false). Span construction + diff are deterministic, built now.
"""
import json
import os
import sys
from pathlib import Path

_FALLBACK = {
    "verified": False,
    "attribute_map": {"action": "gen_ai.operation.name", "tool": "gen_ai.tool.name",
                      "model": "gen_ai.request.model", "input_tokens": "gen_ai.usage.input_tokens",
                      "output_tokens": "gen_ai.usage.output_tokens"},
    "span_name_field": "action",
    "regression": {"threshold": 0},
}


def _config_file(root: Path) -> Path:
    return root / "harness" / "trace-otel.config.yaml"


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


def to_spans(events, cfg: dict):
    """Deterministic: each event -> one OTel-GenAI span; linear causal chain (step i parent = i-1).
    Span ids are the event index (stable, no clock) so diffs are reproducible."""
    amap = cfg.get("attribute_map", {})
    name_field = cfg.get("span_name_field", "action")
    spans = []
    for i, ev in enumerate(events):
        attrs = {amap[k]: ev[k] for k in amap if k in ev and ev[k] is not None}
        spans.append({
            "span_id": i,
            "parent_span_id": (i - 1) if i > 0 else None,
            "name": str(ev.get(name_field, ev.get("action", "step"))),
            "attributes": attrs,
        })
    return spans


def root_cause(run_spans, gold_spans):
    """First index where run diverges from golden (name or attributes). None = conformant."""
    for i in range(min(len(run_spans), len(gold_spans))):
        r, g = run_spans[i], gold_spans[i]
        if r["name"] != g["name"] or r["attributes"] != g["attributes"]:
            return {"index": i, "run": r, "gold": g,
                    "reason": "name differs" if r["name"] != g["name"] else "attributes differ"}
    if len(run_spans) != len(gold_spans):
        return {"index": min(len(run_spans), len(gold_spans)),
                "reason": f"length differs (run={len(run_spans)} gold={len(gold_spans)})"}
    return None


def _read_events(path_or_none):
    raw = ""
    if path_or_none:
        try:
            raw = Path(path_or_none).read_text(encoding="utf-8")
        except Exception:
            return []
    else:
        raw = sys.stdin.read()
    raw = raw.strip()
    if not raw:
        return []
    if raw[0] == "[":                       # a JSON array
        try:
            return json.loads(raw)
        except Exception:
            return []
    out = []                                # else JSONL
    for ln in raw.splitlines():
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    return out


def self_test() -> int:
    cfg = _FALLBACK
    events = [{"action": "user", "tool": None},
              {"action": "tool", "tool": "Read"},
              {"action": "tool", "tool": "Write"}]
    spans = to_spans(events, cfg)
    has_otel = all("gen_ai.operation.name" in s["attributes"] for s in spans)
    chain_ok = spans[0]["parent_span_id"] is None and spans[2]["parent_span_id"] == 1
    gold = to_spans([{"action": "user"}, {"action": "tool", "tool": "Read"},
                     {"action": "tool", "tool": "Grep"}], cfg)   # diverges at step 3 (Write vs Grep)
    rc = root_cause(spans, gold)
    rc_ok = rc is not None and rc["index"] == 2
    same_ok = root_cause(spans, spans) is None
    ok = has_otel and chain_ok and rc_ok and same_ok
    print("trace-otel self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> None:
    args = sys.argv[1:]
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if "--root" in args:
        i = args.index("--root"); root = Path(args[i + 1]); del args[i:i + 2]
    if "--self-test" in args:
        sys.exit(self_test())
    cfg = load_config(root)
    if "--root-cause" in args:
        i = args.index("--root-cause")
        if len(args) < i + 3:
            print("usage: trace-otel.py --root-cause RUN.jsonl GOLD.jsonl", file=sys.stderr); sys.exit(2)
        run = to_spans(_read_events(args[i + 1]), cfg)
        gold = to_spans(_read_events(args[i + 2]), cfg)
        rc = root_cause(run, gold)
        if rc is None:
            print("conformant — no divergence from golden trace"); sys.exit(0)
        print(json.dumps(rc, ensure_ascii=False, indent=2))
        thr = int((cfg.get("regression") or {}).get("threshold", 0))
        sys.exit(2 if thr <= 0 else 0)
    if "--emit" in args:
        i = args.index("--emit")
        path = args[i + 1] if len(args) > i + 1 and not args[i + 1].startswith("-") else None
        print(json.dumps(to_spans(_read_events(path), cfg), ensure_ascii=False, indent=2)); return
    print(__doc__)


if __name__ == "__main__":
    main()
