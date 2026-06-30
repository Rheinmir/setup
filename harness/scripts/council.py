#!/usr/bin/env python3
"""council.py - deterministic protocol engine for the LLM-Council feature.

Karpathy's 3-stage llm-council (https://github.com/karpathy/llm-council):
  Stage 1 "First Opinions" : N seats independently answer one question.
  Stage 2 "Review"         : judges peer-rank the answers with identities
                             anonymized, "so that the LLM can't play favorites
                             when judging their outputs."
  Stage 3 "Final Response" : a chairman synthesizes the final answer.

This file owns ONLY the DETERMINISTIC half of that protocol. It NEVER calls a
model. Everything here is pure, reproducible code:

  - anonymize    : strip author, relabel A/B/C... by stable sha256(id) order
  - mean-rank    : pure-code aggregation of every judge's ordering
  - dissent      : surface the answers the judges disagree about most
  - anchor guard : seed-driven, per-judge presentation order to cancel position
                   bias -- NO global RNG, NO Math.random; the seed is an argument
  - transcript   : write a json + a human-readable md audit artifact

The model GENERATIONS (the seat answers, each judge's ranking, the chairman
synthesis) are produced by the orca orchestration, NOT here -- see
skills/council/SKILL.md. WHICH model fills each role is an unverified assumption
quarantined in harness/council.config.yaml (verified: false). This engine reads
that config only to STAMP provenance into the transcript; none of the math above
ever branches on a model identity. That is the adapter boundary: finalize the
council later by editing one config file, not this engine.

CLI
  council.py rank <answers.json> [--judges judges.json] [--seed N]
                                 [--out DIR] [--config council.config.yaml]
        Full protocol. With judges -> writes the transcript (mean-rank, dissent,
        chairman brief). Without judges -> emits the blind packet to hand to the
        judge models, then stops (re-run with --judges once they have ranked).

  council.py prepare <answers.json> [--seed N] [--out DIR] [--config ...]
        Stage-2 setup only: anonymize + per-judge presentation order (the blind
        packet). Alias for `rank` without --judges.

  council.py selftest
        Run the bundled conformance vectors; assert the mean-rank aggregation
        and dissent are deterministic and correct. Exit 0 = PASS.

Schemas (the stable contract -- contains NO unverified value)
  answers.json : [{"id": str, "author": str, "text": str}, ...]
  judges.json  : [{"judge": str, "ranking": [<anon label>, ...]}, ...]  # best first
"""
import argparse
import difflib
import hashlib
import json
import math
import random
import sys
from pathlib import Path

# Static generator tag. Deliberately no wall-clock timestamp anywhere in the
# artifact -- a timestamp would break byte-for-byte determinism, which is the
# property the self-test proves.
GENERATOR = "council.py/1.0"


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _die(msg: str) -> "None":
    print(f"[council] error: {msg}", file=sys.stderr)
    sys.exit(2)


def _round(x: float) -> float:
    """Fixed precision keeps the json stable and readable; rounding is itself
    deterministic, so two runs still match byte-for-byte."""
    return round(x, 6)


def label_for(index: int) -> str:
    """0->A, 1->B, ... 25->Z, 26->AA (Excel-style). Deterministic, unbounded."""
    s = ""
    n = index
    while True:
        s = chr(ord("A") + n % 26) + s
        n = n // 26 - 1
        if n < 0:
            return s


def stable_hash(s: str) -> str:
    """Salt-free hash -- unlike Python's hash(), identical across processes."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# Stage 2a: anonymization (strip author -> A/B/C by stable hash order)
# --------------------------------------------------------------------------- #
def anonymize(answers):
    """Assign labels A/B/C... to answers ordered by ascending sha256(id).

    Hashing the id (not the input position, not the author) makes the label
    assignment stable AND independent of input order, so neither authorship nor
    list position leaks to the judges. Returns (label_of_id, id_of_label, anon)
    where anon is [{"label", "text"}, ...] in label order.
    """
    ids = [a["id"] for a in answers]
    if len(set(ids)) != len(ids):
        _die("answer ids must be unique")
    ordered = sorted(answers, key=lambda a: stable_hash(a["id"]))
    label_of_id, id_of_label, anon = {}, {}, []
    for i, a in enumerate(ordered):
        lab = label_for(i)
        label_of_id[a["id"]] = lab
        id_of_label[lab] = a["id"]
        anon.append({"label": lab, "text": a["text"]})
    return label_of_id, id_of_label, anon


# --------------------------------------------------------------------------- #
# Stage 2b: anchor guard (seed-driven per-judge presentation order)
# --------------------------------------------------------------------------- #
def _seed_int(base_seed, judge_id: str) -> int:
    h = hashlib.sha256(f"{base_seed}:{judge_id}".encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big")


def presentation_orders(labels, judge_ids, seed):
    """A reproducible shuffle of the presentation order, one per judge.

    Position bias (judges favouring whatever is shown first) is cancelled by
    showing each judge a different order. The order is derived from `seed` via a
    PER-JUDGE local random.Random -- never the global RNG, never Math.random --
    so it is identical on every run for a given seed. The label->answer mapping
    is untouched; only the sequence each judge SEES changes.
    """
    out = {}
    for jid in judge_ids:
        rng = random.Random(_seed_int(seed, jid))
        order = list(labels)
        rng.shuffle(order)
        out[jid] = order
    return out


# --------------------------------------------------------------------------- #
# Stage 2c: mean-rank aggregation + dissent (pure code)
# --------------------------------------------------------------------------- #
def _ranks_by_judge(labels, judges):
    """Validate each judge's ranking is a permutation of `labels`; return
    {judge_id: {label: position}} with position 1 = best."""
    label_set = set(labels)
    by_judge = {}
    for j in judges:
        jid = j["judge"]
        ranking = list(j["ranking"])
        if jid in by_judge:
            _die(f"duplicate judge id: {jid}")
        if len(set(ranking)) != len(ranking):
            _die(f"judge {jid}: ranking has duplicate labels")
        if set(ranking) != label_set:
            _die(f"judge {jid}: ranking {ranking} is not a permutation of {sorted(label_set)}")
        by_judge[jid] = {lab: pos + 1 for pos, lab in enumerate(ranking)}
    return by_judge


def aggregate(labels, judges):
    """MEAN-RANK consensus. Lower mean rank = better. Ties broken by label so
    the ordering is fully deterministic. Returns (rows, by_judge)."""
    by_judge = _ranks_by_judge(labels, judges)
    judge_ids = [j["judge"] for j in judges]
    rows = []
    for lab in labels:
        ranks = [by_judge[jid][lab] for jid in judge_ids]
        rows.append({"label": lab, "ranks": ranks, "mean_rank": _round(sum(ranks) / len(ranks))})
    rows.sort(key=lambda r: (r["mean_rank"], r["label"]))
    for i, r in enumerate(rows):
        r["consensus_rank"] = i + 1
    return rows, by_judge


def dissent(labels, judges):
    """Per-label spread of ranks across judges. Most contested first
    (variance desc, then range desc, then label). Deterministic."""
    by_judge = _ranks_by_judge(labels, judges)
    judge_ids = [j["judge"] for j in judges]
    rows = []
    for lab in labels:
        ranks = [by_judge[jid][lab] for jid in judge_ids]
        mean = sum(ranks) / len(ranks)
        var = sum((r - mean) ** 2 for r in ranks) / len(ranks)
        rows.append({
            "label": lab,
            "ranks": ranks,
            "min_rank": min(ranks),
            "max_rank": max(ranks),
            "range": max(ranks) - min(ranks),
            "variance": _round(var),
            "stdev": _round(math.sqrt(var)),
        })
    rows.sort(key=lambda r: (-r["variance"], -r["range"], r["label"]))
    return rows


# --------------------------------------------------------------------------- #
# transcript assembly
# --------------------------------------------------------------------------- #
def _author_lookup(answers, id_of_label, labels):
    by_id = {a["id"]: a for a in answers}
    return {lab: by_id[id_of_label[lab]]["author"] for lab in labels}


def build_packet(answers, seed, config):
    """Stage-2 blind packet: what the judges are shown, plus each judge's
    presentation order. No rankings yet."""
    label_of_id, id_of_label, anon = anonymize(answers)
    labels = [a["label"] for a in anon]
    judge_ids = [j["id"] for j in config.get("judges", [])] or [s["id"] for s in config.get("seats", [])]
    pres = presentation_orders(labels, judge_ids, seed)
    return {
        "generator": GENERATOR,
        "stage": "2-review-setup",
        "verified": bool(config.get("verified", False)),
        "question": config.get("question"),
        "seed": seed,
        "blind_answers": anon,
        "anchor_guard": {
            "seed": seed,
            "presentation_order": pres,
            "note": "Show each judge its answers in THIS order to cancel position bias.",
        },
        "judges_expected": judge_ids,
    }


def build_transcript(answers, judges, seed, config):
    """Full Stage 1-2-3 audit record. Deterministic given the same inputs."""
    label_of_id, id_of_label, anon = anonymize(answers)
    labels = [a["label"] for a in anon]
    author_of = _author_lookup(answers, id_of_label, labels)
    judge_ids = [j["judge"] for j in judges]

    pres = presentation_orders(labels, judge_ids, seed)
    rows, by_judge = aggregate(labels, judges)
    diss = dissent(labels, judges)

    winner = rows[0]
    most_contested = diss[0] if diss else None

    # De-anonymized judge rankings for the audit trail.
    judge_rankings = [{
        "judge": j["judge"],
        "ranking_labels": list(j["ranking"]),
        "ranking_authors": [author_of[lab] for lab in j["ranking"]],
    } for j in judges]

    aggregate_rows = [{
        "consensus_rank": r["consensus_rank"],
        "label": r["label"],
        "author": author_of[r["label"]],
        "mean_rank": r["mean_rank"],
        "ranks": r["ranks"],
    } for r in rows]

    dissent_rows = [{**d, "author": author_of[d["label"]]} for d in diss]

    chairman_brief = {
        "instruction": (
            "Synthesize ONE final answer. Lead with the consensus winner, fold in "
            "unique correct points from the others, and explicitly resolve the "
            "contested answer(s) below rather than averaging them away."
        ),
        "consensus_order": [
            {"rank": r["consensus_rank"], "author": author_of[r["label"]], "mean_rank": r["mean_rank"]}
            for r in rows
        ],
        "dissent_points": [
            {"author": author_of[d["label"]], "ranks": d["ranks"], "variance": d["variance"]}
            for d in diss if d["range"] > 0
        ],
    }

    verified = bool(config.get("verified", False))
    pending = []
    if not verified:
        pending = [
            "Models in harness/council.config.yaml are ASSUMPTIONS (verified: false).",
            "Adapt: edit harness/council.config.yaml seats/judges/chairman, run a real "
            "council, then flip verified: true. The math above does not change.",
        ]

    return {
        "generator": GENERATOR,
        "stage": "1-2-3-complete",
        "verified": verified,
        "question": config.get("question"),
        "seed": seed,
        "config_provenance": {
            "seats": config.get("seats", []),
            "judges": config.get("judges", []),
            "chairman": config.get("chairman", {}),
            "anchor_seed": config.get("anchor_seed"),
            "note": "Adapter values (model identities). Provenance only -- the engine never branches on these.",
        },
        # Stage 1
        "answers": [
            {"id": id_of_label[lab], "author": author_of[lab], "label": lab,
             "text": next(a["text"] for a in answers if a["id"] == id_of_label[lab])}
            for lab in labels
        ],
        "anonymization": {"label_to_id": id_of_label, "label_to_author": author_of},
        # Stage 2
        "anchor_guard": {
            "seed": seed,
            "presentation_order": pres,
            "note": "Each judge was shown the blind answers in this order (position-bias guard).",
        },
        "judge_rankings": judge_rankings,
        "aggregate": aggregate_rows,
        "winner": {"label": winner["label"], "author": author_of[winner["label"]],
                   "mean_rank": winner["mean_rank"]},
        "dissent": dissent_rows,
        "most_contested": (
            {"label": most_contested["label"], "author": author_of[most_contested["label"]],
             "variance": most_contested["variance"], "ranks": most_contested["ranks"]}
            if most_contested else None
        ),
        # Stage 3
        "chairman_brief": chairman_brief,
        "chairman_synthesis": None,  # filled by the chairman model via orchestration
        "pending_adapter_steps": pending,
    }


# --------------------------------------------------------------------------- #
# markdown rendering (human-readable audit doc)
# --------------------------------------------------------------------------- #
def render_packet_md(packet) -> str:
    L = ["# Council - Blind Review Packet (Stage 2 setup)", ""]
    if not packet["verified"]:
        L += ["> WARNING: models are UNVERIFIED assumptions (council.config.yaml `verified: false`).", ""]
    if packet.get("question"):
        L += [f"**Question:** {packet['question']}", ""]
    L += ["## Blind answers (identities stripped)", "",
          "| Label | Answer |", "|-------|--------|"]
    for a in packet["blind_answers"]:
        L.append(f"| {a['label']} | {a['text']} |")
    L += ["", "## Anchor guard - per-judge presentation order", "",
          f"Seed: `{packet['anchor_guard']['seed']}`. {packet['anchor_guard']['note']}", "",
          "| Judge | Show in this order |", "|-------|--------------------|"]
    for jid, order in packet["anchor_guard"]["presentation_order"].items():
        L.append(f"| {jid} | {' -> '.join(order)} |")
    L += ["", "Hand each judge its blind answers in its row's order; collect a ranking "
          "of the labels (best first) into judges.json, then re-run `council.py rank ... --judges judges.json`.", ""]
    return "\n".join(L) + "\n"


def render_transcript_md(t) -> str:
    L = ["# Council Transcript", "",
         f"_{t['generator']} - DETERMINISTIC artifact (seed `{t['seed']}`)._", ""]
    if not t["verified"]:
        L += ["> WARNING: this run used UNVERIFIED model assumptions "
              "(`harness/council.config.yaml` `verified: false`). Treat the synthesis as a draft.", ""]
    if t.get("question"):
        L += [f"**Question:** {t['question']}", ""]

    L += ["## Stage 1 - First Opinions", "",
          "| Author (seat) | Blind label | Answer |", "|---------------|-------------|--------|"]
    for a in t["answers"]:
        L.append(f"| {a['author']} | {a['label']} | {a['text']} |")

    L += ["", "## Stage 2 - Review (blind peer-rank)", "",
          "### Anchor guard", "",
          f"Seed `{t['anchor_guard']['seed']}`. {t['anchor_guard']['note']}", "",
          "| Judge | Presentation order |", "|-------|--------------------|"]
    for jid, order in t["anchor_guard"]["presentation_order"].items():
        L.append(f"| {jid} | {' -> '.join(order)} |")

    L += ["", "### Judge rankings (best first)", "",
          "| Judge | Ranking (blind) |", "|-------|-----------------|"]
    for jr in t["judge_rankings"]:
        L.append(f"| {jr['judge']} | {' > '.join(jr['ranking_labels'])} |")

    L += ["", "### Mean-rank consensus", "",
          "| Consensus | Author | Blind | Mean rank | Judge ranks |",
          "|-----------|--------|-------|-----------|-------------|"]
    for r in t["aggregate"]:
        L.append(f"| {r['consensus_rank']} | {r['author']} | {r['label']} | "
                 f"{r['mean_rank']} | {r['ranks']} |")
    w = t["winner"]
    L += ["", f"**Consensus winner:** {w['author']} (blind {w['label']}, mean rank {w['mean_rank']}).", ""]

    L += ["### Dissent - where the judges disagree most", ""]
    if t["most_contested"]:
        mc = t["most_contested"]
        L += [f"**Most contested:** {mc['author']} (blind {mc['label']}) - "
              f"ranks {mc['ranks']}, variance {mc['variance']}.", ""]
    L += ["| Author | Blind | Ranks | Range | Variance |",
          "|--------|-------|-------|-------|----------|"]
    for d in t["dissent"]:
        L.append(f"| {d['author']} | {d['label']} | {d['ranks']} | {d['range']} | {d['variance']} |")

    L += ["", "## Stage 3 - Final Response (chairman brief)", "",
          t["chairman_brief"]["instruction"], "", "Consensus order to lead with:"]
    for c in t["chairman_brief"]["consensus_order"]:
        L.append(f"- {c['rank']}. {c['author']} (mean rank {c['mean_rank']})")
    if t["chairman_brief"]["dissent_points"]:
        L += ["", "Must explicitly resolve:"]
        for d in t["chairman_brief"]["dissent_points"]:
            L.append(f"- {d['author']} - split ranks {d['ranks']} (variance {d['variance']})")
    L += ["", "_chairman_synthesis: pending (produced by the chairman model via orca orchestration)._", ""]

    if t["pending_adapter_steps"]:
        L += ["## Adapter boundary - pending", ""]
        for s in t["pending_adapter_steps"]:
            L.append(f"- {s}")
        L.append("")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------- #
# io
# --------------------------------------------------------------------------- #
def serialize(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        _die(f"file not found: {path}")
    except json.JSONDecodeError as e:
        _die(f"invalid json in {path}: {e}")


def load_config(path):
    """Read the adapter config. Missing/unreadable -> fail-safe empty config
    with verified:false (the engine still runs; the transcript says unverified)."""
    if not path:
        return {"verified": False}
    p = Path(path)
    if not p.is_file():
        print(f"[council] note: config {p} not found; treating as unverified.", file=sys.stderr)
        return {"verified": False}
    try:
        import yaml  # optional dependency
    except ImportError:
        print("[council] note: PyYAML missing; config not parsed (unverified).", file=sys.stderr)
        return {"verified": False}
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    data.setdefault("verified", False)
    return data


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #
def _resolve_seed(args, config) -> int:
    if args.seed is not None:
        return args.seed
    if config.get("anchor_seed") is not None:
        return int(config["anchor_seed"])
    return 0


def _write_packet(answers, seed, config, out: Path):
    packet = build_packet(answers, seed, config)
    out.mkdir(parents=True, exist_ok=True)
    (out / "council.packet.json").write_text(serialize(packet), encoding="utf-8")
    (out / "council.packet.md").write_text(render_packet_md(packet), encoding="utf-8")
    print(f"[council] wrote blind packet to {out}/council.packet.{{json,md}}")
    print("[council] give each judge model its answers (see council.packet.md), collect "
          "judges.json, then run: council.py rank <answers.json> --judges judges.json")


def cmd_rank(args):
    config = load_config(args.config)
    answers = _load_json(Path(args.answers))
    seed = _resolve_seed(args, config)
    out = Path(args.out) if args.out else Path(args.answers).resolve().parent

    # `prepare` forces packet-only; `rank` may auto-detect a sibling judges.json.
    if getattr(args, "packet_only", False):
        _write_packet(answers, seed, config, out)
        return

    judges_path = args.judges
    if judges_path is None:
        sib = Path(args.answers).resolve().parent / "judges.json"
        judges_path = str(sib) if sib.is_file() else None

    if judges_path is None:
        # No rankings yet -> emit the blind packet and stop.
        _write_packet(answers, seed, config, out)
        return

    judges = _load_json(Path(judges_path))
    t = build_transcript(answers, judges, seed, config)
    out.mkdir(parents=True, exist_ok=True)
    (out / "council.transcript.json").write_text(serialize(t), encoding="utf-8")
    (out / "council.transcript.md").write_text(render_transcript_md(t), encoding="utf-8")
    w = t["winner"]
    mc = t["most_contested"]
    print(f"[council] wrote {out}/council.transcript.{{json,md}}")
    print(f"[council] consensus winner: {w['author']} (blind {w['label']}, mean rank {w['mean_rank']})")
    if mc:
        print(f"[council] most contested : {mc['author']} (blind {mc['label']}, variance {mc['variance']})")
    if not t["verified"]:
        print("[council] verified: false -- models are assumptions; see pending_adapter_steps.")


def cmd_prepare(args):
    args.judges = None
    args.packet_only = True
    cmd_rank(args)


# --------------------------------------------------------------------------- #
# self-test (conformance vectors)
# --------------------------------------------------------------------------- #
EMBED_ANSWERS = [
    {"id": "ans-claude", "author": "claude-opus", "text": "Use a hash map for O(1) average lookups."},
    {"id": "ans-gpt", "author": "gpt-5", "text": "Sort once then binary-search, O(log n) per query."},
    {"id": "ans-gemini", "author": "gemini-pro", "text": "A linear scan is simplest at O(n)."},
]
EMBED_JUDGES = [
    {"judge": "seat-1", "ranking": ["A", "B", "C"]},
    {"judge": "seat-2", "ranking": ["A", "C", "B"]},
    {"judge": "seat-3", "ranking": ["C", "A", "B"]},
]
EMBED_CONFIG = {
    "verified": False,
    "question": "Fastest way to test membership in a large static set?",
    "seats": [{"id": "seat-1", "model": "m1"}, {"id": "seat-2", "model": "m2"}, {"id": "seat-3", "model": "m3"}],
    "judges": [{"id": "seat-1", "model": "m1"}, {"id": "seat-2", "model": "m2"}, {"id": "seat-3", "model": "m3"}],
    "chairman": {"model": "m1"},
    "anchor_seed": 42,
}


def _load_or(path: Path, fallback):
    return _load_json(path) if path.is_file() else fallback


def cmd_selftest(args):
    fix = Path(__file__).resolve().parent.parent / "tests" / "council"
    answers = _load_or(fix / "answers.json", EMBED_ANSWERS)
    judges = _load_or(fix / "judges.json", EMBED_JUDGES)
    src = "fixture files" if (fix / "answers.json").is_file() else "embedded vectors"

    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    print(f"council.py selftest -- vectors from {src}\n")

    # 1. Determinism: build the transcript twice, compare bytes.
    a = serialize(build_transcript(answers, judges, 42, EMBED_CONFIG))
    b = serialize(build_transcript(answers, judges, 42, EMBED_CONFIG))
    check("transcript byte-identical across two runs (determinism)", a == b)

    # 2. Anonymization is invariant to INPUT ORDER (no positional leak).
    m1 = anonymize(answers)[1]
    m2 = anonymize(list(reversed(answers)))[1]
    check("anonymization invariant under input reordering", m1 == m2)

    # 3. Anchor-guard order is reproducible AND seed-sensitive.
    labels = [x["label"] for x in anonymize(answers)[2]]
    jids = [j["judge"] for j in judges]
    check("anchor-guard order reproducible for a fixed seed",
          presentation_orders(labels, jids, 42) == presentation_orders(labels, jids, 42))
    check("anchor-guard order changes with the seed",
          presentation_orders(labels, jids, 42) != presentation_orders(labels, jids, 7))

    # 4. Mean-rank correctness (hand-computed; independent of the id->label map).
    #    Ranks 1=best:  A=[1,1,2] mean 4/3 | B=[2,3,3] mean 8/3 | C=[3,2,1] mean 2.
    rows, _ = aggregate(labels, judges)
    mean = {r["label"]: r["mean_rank"] for r in rows}
    check("mean rank A == 4/3", math.isclose(mean["A"], 4 / 3, abs_tol=1e-6))
    check("mean rank B == 8/3", math.isclose(mean["B"], 8 / 3, abs_tol=1e-6))
    check("mean rank C == 2.0", math.isclose(mean["C"], 2.0, abs_tol=1e-6))
    order = [r["label"] for r in rows]
    check("consensus order == [A, C, B]", order == ["A", "C", "B"])
    check("winner == A (lowest mean rank)", rows[0]["label"] == "A")

    # 5. Dissent correctness: C is most contested (variance 2/3, full range).
    diss = dissent(labels, judges)
    cvar = next(d["variance"] for d in diss if d["label"] == "C")
    check("most contested == C", diss[0]["label"] == "C")
    check("C variance == 2/3", math.isclose(cvar, 2 / 3, abs_tol=1e-6))
    check("C has the full rank range (2)", next(d["range"] for d in diss if d["label"] == "C") == 2)

    failed = [n for n, ok in checks if not ok]
    print()
    if failed:
        print(f"SELFTEST FAILED ({len(failed)}/{len(checks)}): {failed}")
        sys.exit(1)
    print(f"SELFTEST PASSED ({len(checks)}/{len(checks)} checks)")
    print("\n--- deterministic transcript excerpt (winner + most-contested) ---")
    t = build_transcript(answers, judges, 42, EMBED_CONFIG)
    print(json.dumps({"winner": t["winner"], "most_contested": t["most_contested"],
                      "aggregate": [{"rank": r["consensus_rank"], "author": r["author"],
                                     "mean_rank": r["mean_rank"]} for r in t["aggregate"]]},
                     indent=2, ensure_ascii=False))


# --------------------------------------------------------------------------- #
# argparse
# --------------------------------------------------------------------------- #
def cmd_roster(args):
    """Bốc 3-5 persona theo case/profile/--personas — THUẦN LOOKUP, không gọi model.
    In lens + cặp đối-trọng + lý do (log-được vào transcript). Đây là lớp ADDITIVE; engine
    rank/anonymize/mean-rank KHÔNG đụng tới. Nguồn: harness/council.personas.yaml."""
    try:
        import yaml  # optional dependency (giống cmd_rank)
    except ImportError:
        _die("roster cần pyyaml — pip install pyyaml")
    data = yaml.safe_load(Path(args.personas).read_text(encoding="utf-8")) or {}
    P, pairs = data.get("personas", {}), [tuple(p) for p in data.get("polarity_pairs", [])]
    cases, profiles = data.get("cases", {}), data.get("profiles", {})

    # Khỏi nhớ tên ai: `roster --list` hoặc `roster` trống → in catalog (bốc theo CASE/việc).
    if args.list or not (args.case or args.profile or args.personas_list):
        print("Bốc theo CASE (theo VIỆC — không cần nhớ tên ai):")
        for tag, c in cases.items():
            print(f"  --case {tag:<10} → {' · '.join(P[i]['name'] for i in c.get('base', []))}")
        print("Hoặc PROFILE:")
        for pf, ids in profiles.items():
            print(f"  --profile {pf:<12} ({len(ids)} người)")
        print("18 PERSONA (id → tên · lens) — chỉ cần khi muốn --personas tay:")
        for i, v in P.items():
            print(f"  {i:<12} {v['name']:<17} · {v['lens']}")
        print("\nVí dụ:  council.py roster --case risk   ·   --profile lean   ·   --personas feynman,taleb,rams")
        return

    # GỌI CHÍNH XÁC kể cả khi nhớ nhầm: khớp không-phân-biệt-hoa/thường, theo id LẪN tên,
    # gõ sai → gợi ý gần nhất (difflib) thay vì fail trơ.
    def _sug(tok, opts):
        m = difflib.get_close_matches(tok.lower(), [o.lower() for o in opts], n=1, cutoff=0.5)
        return f" — ý bạn là '{m[0]}'?" if m else " (xem: roster --list)"

    def _resolve_persona(tok):
        t = tok.strip()
        low = t.lower()
        if t in P:
            return t
        for i in P:                                    # id không phân biệt hoa/thường
            if i.lower() == low:
                return i
        for i, v in P.items():                         # theo TÊN (đầy đủ hoặc 1 từ: "Feynman"/"taleb")
            nm = v.get("name", "").lower()
            if low == nm or low in nm.split():
                return i
        cand = list(P) + [v.get("name", "") for v in P.values()]
        m = difflib.get_close_matches(t, cand, n=1, cutoff=0.5)
        _die(f"persona lạ '{tok}'" + (f" — ý bạn là '{m[0]}'?" if m else " (xem: roster --list)"))

    if args.personas_list:
        ids = [_resolve_persona(x) for x in args.personas_list.split(",") if x.strip()]
        why = "chỉ định tay"
    elif args.profile:
        key = next((k for k in profiles if k.lower() == args.profile.strip().lower()), None)
        if not key:
            _die(f"profile lạ '{args.profile}' (có: {', '.join(profiles)}){_sug(args.profile, profiles)}")
        ids, why = profiles[key], f"profile {key}"
    elif args.case:
        key = next((k for k in cases if k.lower() == args.case.strip().lower()), None)
        if not key:
            _die(f"case lạ '{args.case}' (có: {', '.join(cases)}){_sug(args.case, cases)}")
        c = cases[key]
        ids = list(c.get("base", []))
        if args.size and args.size >= 5:
            ids += list(c.get("extra", []))[:max(0, args.size - len(ids))]
        why = f"case {key} (size {len(ids)})"
    else:
        _die("cần --case <tag> | --profile <name> | --personas a,b,c")

    idset = set(ids)
    tensions = [list(p) for p in pairs if p[0] in idset and p[1] in idset]
    if not tensions and len(ids) > 1:
        sys.stderr.write(f"[roster] ⚠ KHÔNG có cặp đối-trọng trong {ids} — nguy cơ phòng vọng âm.\n")

    roster = [{"id": i, **{k: P[i][k] for k in ("name", "lens", "sig")}} for i in ids]
    out = {"why": why, "personas": roster, "tensions": tensions}
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"[roster] {why} · {len(ids)} ghế · tension: {tensions or '⚠ THIẾU'}")
        for r in roster:
            print(f"  • {r['name']:<17} — {r['lens']}  | {r['sig']}")
    return out


def main():
    ap = argparse.ArgumentParser(prog="council.py", description="Deterministic LLM-council protocol engine.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("rank", help="full protocol; with --judges -> transcript, without -> blind packet")
    r.add_argument("answers", help="answers.json: [{id,author,text}, ...]")
    r.add_argument("--judges", help="judges.json: [{judge, ranking:[labels]}, ...]")
    r.add_argument("--seed", type=int, help="anchor-guard seed (overrides config anchor_seed)")
    r.add_argument("--out", help="output dir (default: alongside answers.json)")
    r.add_argument("--config", default="harness/council.config.yaml", help="adapter config")
    r.set_defaults(func=cmd_rank)

    p = sub.add_parser("prepare", help="emit the blind packet only (alias for rank without --judges)")
    p.add_argument("answers")
    p.add_argument("--seed", type=int)
    p.add_argument("--out")
    p.add_argument("--config", default="harness/council.config.yaml")
    p.set_defaults(func=cmd_prepare)

    s = sub.add_parser("selftest", help="run conformance vectors; assert determinism + correctness")
    s.set_defaults(func=cmd_selftest)

    ro = sub.add_parser("roster", help="bốc 3-5 persona theo case/profile (thuần lookup, log-được)")
    ro.add_argument("--case", help="design|strategy|debug|risk|product|decision|simplify|ml-ai")
    ro.add_argument("--profile", help="classic|exploration|lean")
    ro.add_argument("--personas", dest="personas_list", help="chỉ định tay: a,b,c")
    ro.add_argument("--list", action="store_true", help="in catalog case/profile/persona (khỏi nhớ tên)")
    ro.add_argument("--size", type=int, default=3, help="3 (mặc định) hoặc 5")
    ro.add_argument("--personas-file", dest="personas", default="harness/council.personas.yaml")
    ro.add_argument("--json", action="store_true")
    ro.set_defaults(func=cmd_roster)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
