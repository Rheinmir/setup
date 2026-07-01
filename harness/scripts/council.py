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
import html as _html
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
# Stage-4 HTML report (GENERIC + deterministic + offline)
# Feeds PURELY from the transcript already built above. Every seat-supplied
# string is escaped here (Taleb fix): no unescaped author/text can break or
# inject into the report. No CDN -> self-contained/offline (docs-site spec).
# --------------------------------------------------------------------------- #
_PALETTE = ["#7a5c86", "#3f7d74", "#b06a2c", "#4a6d99", "#9a5560", "#5f7a3f"]


def _hue_for(name: str) -> str:
    h = int(hashlib.sha256(name.encode("utf-8")).hexdigest(), 16)
    return _PALETTE[h % len(_PALETTE)]


def _fmt_answer(text: str) -> str:
    """Turn a raw seat answer into tidy HTML: split '(1)/(2)' or '1.' enumerations
    into <li>, keep the rest as <p>. Pure presentation, adds no new content."""
    import re
    esc = _html.escape
    parts = re.split(r"(?:(?<=[.\s])|^)\((\d+)\)\s*", text)
    if len(parts) >= 3:  # had (1) (2) ... markers
        lead = esc(parts[0].strip())
        items = []
        for i in range(1, len(parts) - 1, 2):
            items.append(f"<li>{esc(parts[i + 1].strip())}</li>")
        body = (f"<p>{lead}</p>" if lead else "") + f"<ol class='ans'>{''.join(items)}</ol>"
        return body
    return "".join(f"<p>{esc(s.strip())}</p>" for s in text.split("\n") if s.strip())


_MEDAL = {1: "\U0001F947", 2: "\U0001F948", 3: "\U0001F331"}


def render_report_html(t) -> str:
    e = lambda x: _html.escape(str(x), quote=True)
    agg = t["aggregate"]
    jr = t["judge_rankings"]
    pres = t["anchor_guard"].get("presentation_order", {})
    answers = {a["author"]: a for a in t["answers"]}
    order = [(r["author"], r["label"], r["mean_rank"], r["ranks"], r["consensus_rank"]) for r in agg]
    w, mc = t["winner"], t["most_contested"]
    seed, verified = t.get("seed"), t.get("verified", False)
    synth = t.get("chairman_synthesis", "") or ""
    q = t.get("question") or "Council evaluation"

    cards = ""
    for author, label, mean, ranks, crank in order:
        ac = _hue_for(author)
        medal = _MEDAL.get(crank, f"#{crank}")
        cards += f'''
    <article class="pcard" style="--ac:{ac}">
      <div class="phead">
        <div class="pav" style="background:{ac}">{e(str(author)[:1].upper())}</div>
        <div><div class="pname">{e(author)} <span class="rankpill tabnum">{medal} #{e(crank)} · mean {e(mean)}</span></div></div>
        <div class="blindtag">blind {e(label)}</div>
      </div>
      <div class="ansbody">{_fmt_answer(answers[author]["text"])}</div>
    </article>'''

    vote_rows = "".join(
        f'<tr><td>{e(j["judge"])}</td><td class="mono">{" › ".join(e(x) for x in j["ranking_labels"])}</td>'
        f'<td class="mono dim">{" → ".join(e(x) for x in pres.get(j["judge"], []))}</td></tr>' for j in jr)
    reveal = "".join(
        f'<span class="chip" style="--c:{_hue_for(a)}">{e(l)} = {e(a)}</span>' for a, l, _, _, _ in order)
    dash = "".join(
        f'<tr><td class="mono"><b>{e(l)}</b></td><td>{_MEDAL.get(cr,"")} {e(a)}</td>'
        f'<td class="mono tabnum">{e(m)}</td><td class="mono dim tabnum">{e(rk)}</td></tr>'
        for a, l, m, rk, cr in order)
    unan = all(j["ranking_labels"] == jr[0]["ranking_labels"] for j in jr) if jr else False

    syn = ""
    if synth:
        for ln in synth.split("\n"):
            ln = ln.strip()
            if not ln:
                continue
            if ln[:2] in ("1.", "2.", "3.", "4.", "5.", "6."):
                if "<ul" not in syn.rsplit("<p", 1)[-1]:
                    pass
                syn += f'<li>{e(ln[2:].strip())}</li>'
            else:
                syn += f'<p>{e(ln)}</p>'
    syn = syn.replace("<li>", "<ul class='synlist'><li>", 1)
    if "<li>" in syn:
        syn = syn[::-1].replace(">il/<", ">lu/<>il/<", 1)[::-1]
    warn = "" if verified else (
        '<div class="warn"><b>⚠️ verified: false</b> — model identities đã quarantine trong '
        'council.config.yaml. Đây là <b>consensus mean-rank</b>, không phải chân lý.</div>')
    mc_cell = (f'<b>{e(mc["author"])}</b><em class="tabnum">blind {e(mc["label"])} · var {e(mc["variance"])}</em>'
               if mc else "<b>—</b><em>n/a</em>")

    fav = ("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
           "<rect width='32' height='32' rx='7' fill='%23232028'/>"
           "<path d='M8 22h16M16 7l7 5H9z' stroke='%23c9a24b' stroke-width='2' fill='none' stroke-linejoin='round'/></svg>")

    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Council Stage-4 report — blind peer-rank. Deterministic từ council.transcript.json.">
<title>Council · báo cáo Stage-4</title><link rel="icon" href="{fav}">
<style>
:root{{--paper:#f4f1ea;--ink:#26221c;--dim:#7a7266;--faint:#a79e90;--line:rgba(60,52,40,.13);
 --card:rgba(255,253,249,.74);--stroke:rgba(255,255,255,.9);--accent:#8a6d2f;--shadow:24px 40px 24px rgba(60,48,28,.10)}}
*{{box-sizing:border-box}} html{{scroll-behavior:smooth}}
body{{margin:0;font:15px/1.6 "Iowan Old Style","Palatino",Georgia,ui-serif,serif;color:var(--ink);background:var(--paper);
 background-image:radial-gradient(120% 80% at 15% -5%,rgba(214,198,160,.35),transparent 55%),radial-gradient(90% 70% at 100% 0%,rgba(150,168,178,.22),transparent 50%);
 min-height:100dvh;-webkit-font-smoothing:antialiased}}
body::after{{content:"";position:fixed;inset:0;pointer-events:none;z-index:99;opacity:.5;mix-blend-mode:multiply;
 background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.045'/%3E%3C/svg%3E")}}
.wrap{{max-width:940px;margin:0 auto;padding:56px 22px 90px}}
.tabnum{{font-variant-numeric:tabular-nums}}
.body-sans{{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
.eyebrow{{font:600 12px/1 ui-monospace,Menlo,monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}}
h1{{font-weight:600;font-size:clamp(30px,5vw,44px);line-height:1.04;letter-spacing:-.015em;margin:12px 0 10px;text-wrap:balance;max-width:22ch}}
.q{{color:var(--dim);font-size:16px;max-width:60ch;text-wrap:pretty}}
.meta{{margin-top:14px;font:500 12.5px/1 ui-monospace,Menlo,monospace;color:var(--faint)}}
.warn{{background:rgba(176,106,44,.09);border:1px solid rgba(176,106,44,.32);border-left:3px solid #b06a2c;border-radius:13px;
 padding:14px 16px;margin:26px 0 8px;font-size:13.5px;color:#5f4a2e;font-family:ui-sans-serif,system-ui,sans-serif}}
.sect{{margin:46px 0 18px;display:flex;align-items:baseline;gap:14px}}
.sect .n{{font-size:26px;color:var(--accent);line-height:1}} .sect h2{{font-weight:600;font-size:21px;margin:0;letter-spacing:-.01em}}
.sect .rule{{flex:1;height:1px;background:var(--line)}}
.pcard{{background:var(--card);border:1px solid var(--stroke);border-radius:20px;padding:22px 24px;margin:18px 0;position:relative;overflow:hidden;
 box-shadow:0 1px 0 rgba(255,255,255,.7) inset,var(--shadow);transition:transform .28s cubic-bezier(.2,.7,.2,1),box-shadow .28s}}
.pcard::before{{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--ac)}}
.pcard:hover{{transform:translateY(-3px);box-shadow:0 1px 0 rgba(255,255,255,.8) inset,32px 54px 30px rgba(60,48,28,.14)}}
.phead{{display:flex;align-items:center;gap:14px;margin-bottom:12px}}
.pav{{width:46px;height:46px;border-radius:14px;color:#fff;font-weight:600;font-size:20px;display:grid;place-items:center;flex:0 0 46px}}
.pname{{font-size:19px;font-weight:600;letter-spacing:-.01em;text-transform:capitalize}}
.rankpill{{font:600 11.5px/1 ui-monospace,Menlo,monospace;color:var(--dim);margin-left:6px}}
.blindtag{{margin-left:auto;align-self:flex-start;font:600 11px/1 ui-monospace,Menlo,monospace;color:var(--ac);
 border:1px solid var(--ac);border-radius:7px;padding:5px 9px}}
.ansbody{{font-family:ui-sans-serif,system-ui,sans-serif;font-size:13.5px}}
.ansbody p{{margin:6px 0;color:#3a342c}} ol.ans{{margin:8px 0 2px;padding-left:0;list-style:none;counter-reset:a}}
ol.ans li{{position:relative;padding-left:26px;margin-bottom:8px;line-height:1.55}}
ol.ans li::before{{counter-increment:a;content:counter(a);position:absolute;left:0;top:1px;width:18px;height:18px;border-radius:6px;
 background:var(--ac);color:#fff;font:700 11px/18px ui-monospace,Menlo,monospace;text-align:center}}
.tblwrap{{border:1px solid var(--line);border-radius:16px;overflow:hidden;background:rgba(255,253,249,.6);box-shadow:var(--shadow)}}
table{{width:100%;border-collapse:collapse;font-size:13.5px;font-family:ui-sans-serif,system-ui,sans-serif}}
th,td{{text-align:left;padding:12px 15px;border-bottom:1px solid var(--line)}} tbody tr:last-child td{{border-bottom:0}}
tbody tr{{transition:background .18s}} tbody tr:hover{{background:rgba(138,109,47,.06)}}
th{{color:var(--faint);font:600 11px/1 ui-monospace,Menlo,monospace;text-transform:uppercase;letter-spacing:.06em;background:rgba(60,52,40,.03)}}
.mono{{font-family:ui-monospace,Menlo,monospace}} .dim{{color:var(--dim)}}
.chip{{display:inline-flex;align-items:center;gap:6px;background:color-mix(in srgb,var(--c) 12%,var(--paper));
 border:1px solid color-mix(in srgb,var(--c) 55%,transparent);color:var(--c);border-radius:9px;padding:5px 11px;margin:9px 8px 0 0;
 font:600 12.5px/1 ui-sans-serif,system-ui,sans-serif;transition:transform .2s}}
.chip:hover{{transform:translateY(-2px)}} .chip::before{{content:"";width:8px;height:8px;border-radius:50%;background:var(--c)}}
.kpi{{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin:0 0 18px}}
@media(max-width:640px){{.kpi{{grid-template-columns:1fr}}}}
.kpi div{{background:var(--card);border:1px solid var(--stroke);border-radius:16px;padding:16px 18px;box-shadow:var(--shadow);transition:transform .26s}}
.kpi div:hover{{transform:translateY(-3px)}}
.kpi b{{display:block;font-size:22px;font-weight:600;margin:5px 0 3px;text-transform:capitalize}}
.kpi span{{color:var(--faint);font:600 10.5px/1 ui-monospace,Menlo,monospace;text-transform:uppercase;letter-spacing:.07em}}
.kpi em{{font-style:normal;color:var(--dim);font-size:12px;font-family:ui-sans-serif,system-ui,sans-serif}}
.synth{{background:linear-gradient(158deg,rgba(138,109,47,.10),rgba(63,125,116,.06));border:1px solid rgba(138,109,47,.26);
 border-radius:20px;padding:24px 26px;margin-top:16px;box-shadow:var(--shadow)}}
.synth .lbl{{font:600 11px/1 ui-monospace,Menlo,monospace;text-transform:uppercase;letter-spacing:.09em;color:var(--accent)}}
.synth p{{margin:7px 0;font-size:13.5px;line-height:1.6;font-family:ui-sans-serif,system-ui,sans-serif}}
ul.synlist{{margin:6px 0 10px;padding:0;list-style:none;counter-reset:s;font-family:ui-sans-serif,system-ui,sans-serif}}
ul.synlist li{{position:relative;padding-left:26px;margin-bottom:8px;font-size:13.5px;line-height:1.55}}
ul.synlist li::before{{counter-increment:s;content:counter(s);position:absolute;left:0;top:0;width:18px;height:18px;border-radius:6px;
 background:var(--accent);color:#fff;font:700 11px/18px ui-monospace,Menlo,monospace;text-align:center}}
.reveal{{margin-top:16px}} .reveal .lbl{{font:600 11px/1 ui-monospace,Menlo,monospace;text-transform:uppercase;letter-spacing:.06em;color:var(--faint)}}
footer{{margin-top:40px;padding-top:20px;border-top:1px solid var(--line);color:var(--faint);font-size:12.5px;text-align:center;
 font-family:ui-sans-serif,system-ui,sans-serif}}
a:focus-visible,tr:focus-visible{{outline:2px solid var(--accent);outline-offset:3px}}
</style></head><body><div class="wrap">
<header>
  <div class="eyebrow">🏛 Council · Stage-4</div>
  <h1>Hội đồng chấm mù</h1>
  <p class="q">{e(q)}</p>
  <div class="meta tabnum">seed {e(seed)} · council.py/1.0 · {len(jr)} giám khảo · {len(order)} ghế</div>
</header>
{warn}
<section><div class="sect"><span class="n tabnum">1</span><h2>Ý kiến hội đồng</h2><span class="rule"></span></div>{cards}</section>
<section><div class="sect"><span class="n tabnum">2</span><h2>Bỏ phiếu kín</h2><span class="rule"></span></div>
<div class="tblwrap"><table><thead><tr><th>Giám khảo</th><th>Ranking (nhãn ẩn)</th><th>Thứ tự trình bày · anchor guard</th></tr></thead><tbody>{vote_rows}</tbody></table></div>
<div class="reveal"><span class="lbl">Reveal map — chỉ lộ ở cuối</span><br>{reveal}</div></section>
<section><div class="sect"><span class="n tabnum">3</span><h2>Dashboard chốt</h2><span class="rule"></span></div>
<div class="kpi">
 <div><span>Winner</span><b>{_MEDAL[1]} {e(w["author"])}</b><em class="tabnum">blind {e(w["label"])} · mean {e(w["mean_rank"])}</em></div>
 <div><span>Most contested</span>{mc_cell}</div>
 <div><span>Đồng thuận</span><b class="tabnum">{len(jr)} GK</b><em>{"nhất trí tuyệt đối ✓" if unan else "phân hoá"}</em></div>
</div>
<div class="tblwrap"><table><thead><tr><th>Blind</th><th>Ghế</th><th>Mean rank</th><th>Judge ranks</th></tr></thead><tbody>{dash}</tbody></table></div>
{"<div class='synth'><span class='lbl'>Chairman synthesis — câu trả lời chốt</span>" + syn + "</div>" if synth else ""}
</section>
<footer>Mọi số liệu từ council.transcript.json — report chỉ là lớp trình bày, không thêm phán xét mới.</footer>
</div></body></html>'''


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
    # Stage-4 HTML report — ALWAYS rendered (mandatory), self-contained/offline,
    # written to the repo's canonical html folder. Feeds purely from `t`.
    repo_root = Path(__file__).resolve().parents[2]
    html_dir = repo_root / "llmwiki" / "html" / "council"
    html_dir.mkdir(parents=True, exist_ok=True)
    html_path = html_dir / "council.report.html"
    html_path.write_text(render_report_html(t), encoding="utf-8")
    w = t["winner"]
    mc = t["most_contested"]
    print(f"[council] wrote {out}/council.transcript.{{json,md}}")
    print(f"[council] wrote {html_path} (Stage-4 HTML, mandatory)")
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
