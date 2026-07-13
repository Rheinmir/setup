#!/usr/bin/env python3
"""claim-receipts — a live hallucination gate: extract the file/path references an agent CITES
and verify they actually resolve (2026 "Tool Receipts" / CiteAudit trend — agents fabricate
tool results and cite files/APIs that do not exist). Turns failure-flywheel's "hallucination"
class from a post-mortem into a pre-commit check.

  --check TEXT_OR_FILE     extract references from the text (or file), verify each resolves on
                           disk; report unresolved ones. exit 2 if any unresolved AND strict.
  --self-test              deterministic resolve check (real ref passes, fake ref flagged).

The ONE adapter = harness/claim-receipts.config.yaml (resolver, strictness, claim_taxonomy,
ref_extensions — verified:false). Extraction + filesystem resolve are deterministic, built now.
The symbol-aware resolver (code-graph) is the unknown; default strictness 'advisory'.
"""
import json
import os
import re
import sys
from pathlib import Path

import bnal_config

_FALLBACK = {"verified": False, "resolver": "filesystem", "strictness": "advisory",
             "ref_extensions": ["py", "md", "yaml", "yml", "json", "sh", "js", "ts", "html", "txt", "toml", "cfg"],
             # observed-metric guard (distill: "cấm bịa số của NGƯỜI HỌC/thế-giới agent không đo được").
             # A number ABOUT a subject, with a metric-noun nearby, and NO source marker → candidate fabrication.
             "metric_subjects": ["user", "người dùng", "người học", "learner", "the learner", "customer", r"họ\b", "their", "the human"],
             "metric_sources": ["said", "stated", "reported", "self-report", "khai", "nói", r"theo\b", "measured", r"đo\b",
                                "observed", "from input", "tool result", "confidence:", "rated", "answered"],
             "metric_nouns": ["confidence", "score", "điểm", "tỉ lệ", "tỷ lệ", "rate", "độ tự tin", "calibration",
                              "accuracy", "mastery", "nắm", "retention", "satisfaction", "engagement"],
             "metric_window": 60}


def _config_file(root: Path) -> Path:
    return root / "harness" / "claim-receipts.config.yaml"


def load_config(root: Path) -> dict:
    cfg = bnal_config.load(root, "claim-receipts", _FALLBACK)
    return cfg


def extract_refs(text, exts):
    """Path-like tokens ending in a known extension (conservative — not every word)."""
    if not text:
        return []
    ext_alt = "|".join(re.escape(e) for e in exts)
    rx = re.compile(r"(?<![\w./-])([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:" + ext_alt + r"))\b")
    # strip surrounding backticks/quotes already excluded; dedupe, keep order
    seen, out = set(), []
    for m in rx.finditer(text):
        r = m.group(1).strip("`'\"")
        if r not in seen:
            seen.add(r); out.append(r)
    return out


def resolve(ref, root: Path) -> bool:
    """filesystem resolver: does the ref exist (as-is, under root, or by basename anywhere shallow)?"""
    try:
        if Path(ref).exists():
            return True
        if (root / ref).exists():
            return True
        # basename fallback: a bare filename that exists somewhere tracked-ish (shallow guard)
        base = Path(ref).name
        if "/" not in ref:
            for p in list(root.rglob(base))[:1]:
                if p.exists():
                    return True
    except Exception:
        return True   # fail-open: never flag on a resolver error
    return False


def extract_observed_metrics(text, cfg):
    """Numbers stated ABOUT a subject (user/learner/họ…) with a metric-noun nearby but NO
    source marker → the "cấm bịa số của người học" law: a measurement the agent could not
    have observed (self-reported confidence, mastery %, etc.) asserted without a source.
    ponytail: regex heuristic — the metric-noun + subject gate keeps it precise, but it
    misses paraphrase and can false-positive; stays ADVISORY (never blocks) by config."""
    if not text:
        return []
    subjects = cfg.get("metric_subjects", _FALLBACK["metric_subjects"])
    sources = cfg.get("metric_sources", _FALLBACK["metric_sources"])
    nouns = cfg.get("metric_nouns", _FALLBACK["metric_nouns"])
    window = int(cfg.get("metric_window", 60))
    subj_rx = re.compile("|".join(subjects), re.IGNORECASE)
    src_rx = re.compile("|".join(sources), re.IGNORECASE)
    noun_rx = re.compile("|".join(nouns), re.IGNORECASE)
    num_rx = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?\s*%?)")
    seen, out = set(), []
    for m in num_rx.finditer(text):
        tok = m.group(1).strip()
        s, e = m.start(), m.end()
        ctx = text[max(0, s - window): min(len(text), e + window)]
        is_metric = ("%" in tok) or ("." in tok) or bool(noun_rx.search(ctx))
        if is_metric and subj_rx.search(ctx) and not src_rx.search(ctx):
            if tok not in seen:
                seen.add(tok); out.append(tok)
    return out


def check(text, root: Path, cfg: dict):
    refs = extract_refs(text, cfg.get("ref_extensions", _FALLBACK["ref_extensions"]))
    unresolved = [r for r in refs if not resolve(r, root)]
    metrics = extract_observed_metrics(text, cfg)
    return refs, unresolved, metrics


def self_test() -> int:
    root = Path(__file__).resolve().parents[1].parent   # repo root (…/harness/scripts -> repo)
    cfg = json.loads(json.dumps(_FALLBACK))
    real = "see harness/policy.yaml and harness/scripts/fdk-gate.py for details"
    fake = "edited src/totally/made-up-nonexistent-file.py per the plan"
    _, u_real, _ = check(real, root, cfg)
    _, u_fake, _ = check(fake, root, cfg)
    ok_ref = not u_real and any("made-up-nonexistent" in r for r in u_fake)
    # observed-metric: a fabricated user confidence is flagged; a SOURCED one is not.
    fab = "the learner's confidence is 87% on this concept, they clearly mastered it"
    legit = "the learner said their confidence is 87%"
    m_fab = extract_observed_metrics(fab, cfg)
    m_legit = extract_observed_metrics(legit, cfg)
    ok_metric = ("87%" in m_fab) and (not m_legit)
    ok = ok_ref and ok_metric
    print("claim-receipts self-test:", "PASS" if ok else "FAIL",
          f"(ref={'ok' if ok_ref else 'FAIL'}, observed-metric={'ok' if ok_metric else 'FAIL'})")
    return 0 if ok else 1


def main() -> None:
    args = sys.argv[1:]
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    if "--root" in args:
        i = args.index("--root"); root = Path(args[i + 1]); del args[i:i + 2]
    if "--self-test" in args:
        sys.exit(self_test())
    cfg = load_config(root)
    if "--check" in args:
        i = args.index("--check")
        if len(args) <= i + 1:
            print("usage: claim-receipts.py --check TEXT_OR_FILE", file=sys.stderr); sys.exit(2)
        arg = args[i + 1]
        text = arg
        try:
            p = Path(arg)
            if p.is_file():
                text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            pass
        refs, unresolved, metrics = check(text, root, cfg)
        strict = str(cfg.get("strictness")).lower() == "strict" and cfg.get("verified") is True
        if metrics:
            mm = f"[claim-receipts] {len(metrics)} number(s) ABOUT a subject with no source — possible fabricated metric (bịa số của người học): " + ", ".join(metrics)
            print(mm + ("  (strict)" if strict else "  (advisory)"), file=sys.stderr)
        if not unresolved:
            if not metrics:
                print(f"[claim-receipts] {len(refs)} reference(s), all resolve ✓")
            sys.exit(2 if (metrics and strict) else 0)
        msg = f"[claim-receipts] {len(unresolved)}/{len(refs)} reference(s) DO NOT resolve (possible hallucination): " + ", ".join(unresolved)
        if strict:
            print(msg + "  (strict)", file=sys.stderr); sys.exit(2)
        print(msg + "  (advisory — set strictness:strict + verified:true to enforce)", file=sys.stderr); sys.exit(0)
    print(__doc__)


if __name__ == "__main__":
    main()
