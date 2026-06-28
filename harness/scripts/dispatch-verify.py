#!/usr/bin/env python3
"""dispatch-verify — hau-kiem R7: doi chieu loi-hua cua proposal voi thuc te tren dia.

R7 (harness/validators/proposal_complete.py) la PRE-gate manh: 1 draft 'proposed' phai khai
'## Agent Task Assignment' + seq diagram TRUOC khi fan-out. Nhung SAU dispatch khong co gi
kiem chung cong viec da dap dat — proposal van co the khai "agent X build file Y" + "- [x] done"
ma khong check nao xac nhan Y co that. Tool nay dong vong lap do.

Cach lam (doc cung shape voi proposal_complete.py):
  - Parse bang '## Agent Task Assignment' (Task | Agent | ... | Status) + checklist '## Plan'
    '- [ ]'/'- [x]'. Match theo nhan task (T1, T2, R11...).
  - Rut artifact moi task khai: duong dan file / wiki page / link '*-seq.html' nhac trong
    o (row) hoac dong checklist (token trong backtick + token path-ish tran trong o Agent).
  - Doi chieu dia: moi artifact co ton tai khong? Gan verdict:
      delivered                 — co tren dia
      missing (open)            — vang, nhung task CHUA danh dau xong (khong phai loi)
      CLAIMED-DONE BUT ABSENT   — task danh '[x]'/status 'done' MA file vang (lo hong that)
  - In bang reconcile + tong ket. '--strict' exit 2 neu co bat ky claimed-done-but-absent.

Fail-open: draft khong doc/parse duoc (khong co Plan lan Agent Task Assignment) -> bo qua,
khong crash, khong fail (tru khi --strict gap claimed-done-but-absent that).

Dung:
  python3 harness/scripts/dispatch-verify.py <draft.md> [<draft.md> ...] [--strict]
  python3 harness/scripts/dispatch-verify.py --scan [--strict]   # quet draft da implemented/done
  python3 harness/scripts/dispatch-verify.py                      # = --scan
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# ── parsing (mirror proposal_complete.py shape) ──────────────────────────────
SEQ_LINK_RE = re.compile(
    r"\*\*Sequence diagram[^*]*\*\*:?\s*\[[^\]]*\]\(([^)]+\.html)\)", re.IGNORECASE
)
PLAN_ITEM_RE = re.compile(r"^\s*[-*]\s*\[([ xX])\]\s*(.*)$")
LABEL_RE = re.compile(r"\*{0,2}\s*([A-Za-z]{1,4}\d{1,3})\b")
FM_RE = re.compile(r"^---[ \t]*\n(.*?)\n---", re.DOTALL)
FM_STATUS_RE = re.compile(r"^status[ \t]*:[ \t]*(.+)$", re.MULTILINE | re.IGNORECASE)
BODY_STATUS_RE = re.compile(r"^\*\*Status:\*\*[ \t]*(.+)$", re.MULTILINE | re.IGNORECASE)

# token la 1 "deliverable path" neu: het bang '/', HOAC co duoi file biet, HOAC co '/'
EXTS = (
    "py sh md markdown htm html yaml yml json toml txt js ts tsx jsx css scss "
    "cfg ini conf sql rs go java rb env lock cjs mjs xml csv tsv mdx"
).split()
EXT_RE = re.compile(r"\.(" + "|".join(EXTS) + r")$", re.IGNORECASE)
HAS_EXT_RE = re.compile(r"\.[A-Za-z0-9]{1,6}$")
TOKEN_OK_RE = re.compile(r"^[~\w][\w\-./@+]*$")
BACKTICK_RE = re.compile(r"`([^`]+)`")

# Status 'da xong': cac token nay trong o Status / inline danh dau task la done.
DONE_RE = re.compile(
    r"(?:^|[\s|(])(done|completed?|implement(?:ed)?|merged|shipped|landed|closed|✓|✔|✅)"
    r"(?:$|[\s|.)])",
    re.IGNORECASE,
)
NOT_DONE = {
    "pending", "todo", "open", "wip", "blocked", "planned", "n/a", "-", "—",
    "tbd", "in progress", "in-progress", "none", "skip", "skipped", "deferred",
}

PRUNE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache",
    ".pytest_cache", ".idea", ".ruff_cache",
}
SCAN_DIRS = (
    "llmwiki/wiki/sources/draft",
    "llmwiki/wiki/draft/orca",
    "llmwiki/wiki/draft",
)
SKIP_NAMES = {"README.md", "_template.md"}


def section(text, title):
    m = re.search(
        rf"^##\s+{re.escape(title)}\s*$(.*?)(?=^##\s|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return m.group(1) if m else None


def read(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError:
        return None


def draft_status(text):
    s = ""
    fm = FM_RE.match(text)
    if fm:
        ms = FM_STATUS_RE.search(fm.group(1))
        if ms:
            s = ms.group(1).strip()
    mb = BODY_STATUS_RE.search(text)
    if mb:
        s = (s + " " + mb.group(1).strip()).strip()
    return s.lower()


def is_draft_done(status):
    return "implement" in status or "done" in status


def is_done_status(cell):
    s = (cell or "").strip().lower()
    if not s or s in NOT_DONE:
        return False
    return bool(DONE_RE.search(" " + s + " "))


# ── artifact extraction ──────────────────────────────────────────────────────
def _is_pathish(tok):
    if not tok or "://" in tok:
        return False
    if tok.startswith("~") or tok.startswith("/"):
        return False  # home/absolute install target (~/.claude/...) — ngoai pham vi repo
    if tok == ".git" or tok.startswith(".git/") or "/.git/" in tok:
        return False  # installed hooks etc. — khong phai deliverable cua repo
    if not TOKEN_OK_RE.match(tok):
        return False
    if tok.endswith("/"):
        return True
    if EXT_RE.search(tok):
        return True
    return "/" in tok


def _clean_tok(s):
    s = s.strip().strip("`*\"'“”‘’")
    s = s.lstrip("([")          # giu lai leading '.' cho dotfile (.git/, .pre-commit...)
    return s.rstrip(",.;:)]")   # khong rstrip '/' — do la dau hieu thu muc


def paths_in_backticks(text):
    out = []
    for m in BACKTICK_RE.finditer(text or ""):
        inner = m.group(1).strip()
        parts = inner.split()
        cands = [inner]
        if parts:
            cands.append(parts[0])  # `cmd.sh arg` -> lay 'cmd.sh'
        for c in cands:
            c = _clean_tok(c)
            if _is_pathish(c):
                out.append(c)
                break
    return out


def paths_in_words(text):
    out = []
    for w in re.split(r"\s+", text or ""):
        c = _clean_tok(w)
        if _is_pathish(c):
            out.append(c)
    return out


def parse_plan(plan_text):
    items = []
    if not plan_text:
        return items
    idx = 0
    for line in plan_text.splitlines():
        m = PLAN_ITEM_RE.match(line)
        if not m:
            continue
        idx += 1
        checked = m.group(1).lower() == "x"
        body = m.group(2).strip()
        lm = LABEL_RE.match(body)
        label = lm.group(1).upper() if lm else "P%d" % idx
        items.append({"label": label, "checked": checked, "arts": paths_in_backticks(body)})
    return items


def parse_agent_table(sec_text):
    rows = []
    if not sec_text:
        return rows
    lines = [l for l in sec_text.splitlines() if l.strip().startswith("|")]
    data = [l for l in lines if "---" not in l]
    data = data[1:] if data else []  # bo header
    for l in data:
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if not cells:
            continue
        task = cells[0]
        agent = cells[1] if len(cells) >= 2 else ""
        status = cells[-1] if len(cells) >= 2 else ""
        lm = LABEL_RE.match(task)
        label = lm.group(1).upper() if lm else None
        arts = paths_in_backticks(task) + paths_in_words(task)
        rows.append({"label": label, "task": task, "agent": agent, "status": status, "arts": arts})
    return rows


SEQ_SECTION_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+\.html)\)")


def seq_link(text):
    # 2 quy uoc: '**Sequence diagram**: [..](..html)' (inline) HOAC section '## Sequence diagram'
    m = SEQ_LINK_RE.search(text)
    if m:
        return m.group(1)
    sec = section(text, "Sequence diagram")
    if sec:
        m2 = SEQ_SECTION_LINK_RE.search(sec)
        if m2:
            return m2.group(1)
    return None


# ── disk resolution ──────────────────────────────────────────────────────────
def build_index(repo_root):
    files, stems, dirs = {}, {}, {}
    for dp, dn, fn in os.walk(repo_root):
        dn[:] = [d for d in dn if d not in PRUNE_DIRS]
        rdir = os.path.relpath(dp, repo_root).replace("\\", "/")
        for d in dn:
            rel = d if rdir == "." else rdir + "/" + d
            dirs.setdefault(d, []).append(rel)
        for f in fn:
            rel = f if rdir == "." else rdir + "/" + f
            files.setdefault(f, []).append(rel)
            stem = f.rsplit(".", 1)[0]
            if stem != f:
                stems.setdefault(stem, []).append(rel)
    return {"files": files, "stems": stems, "dirs": dirs}


def _rel(p, root):
    try:
        return str(Path(p).resolve().relative_to(Path(root).resolve())).replace("\\", "/")
    except Exception:
        return str(p)


def _bases(repo_root, draft_path):
    bases, seen, out = [repo_root, repo_root / "llmwiki"], set(), []
    d = draft_path.parent
    while True:
        bases.append(d)
        if d.resolve() == repo_root.resolve() or d.parent == d:
            break
        d = d.parent
    for b in bases:
        rb = b.resolve()
        if rb not in seen:
            seen.add(rb)
            out.append(b)
    return out


def _suffix_match(rel_parts, want_parts):
    if len(want_parts) > len(rel_parts):
        return False
    tail = rel_parts[-len(want_parts):]
    for i, (a, b) in enumerate(zip(tail, want_parts)):
        if i == len(want_parts) - 1:
            if a == b or a.rsplit(".", 1)[0] == b or a == b + ".md":
                continue
            return False
        if a != b:
            return False
    return True


def resolve(token, repo_root, draft_path, index):
    raw = token.strip()
    is_dir = raw.endswith("/")
    clean = raw.strip("/").strip()
    if not clean:
        return False, None
    for b in _bases(repo_root, draft_path):
        cand = b / clean
        try:
            if is_dir:
                if cand.is_dir():
                    return True, _rel(cand, repo_root)
            else:
                if cand.is_file():
                    return True, _rel(cand, repo_root)
                if not HAS_EXT_RE.search(clean) and (b / (clean + ".md")).is_file():
                    return True, _rel(b / (clean + ".md"), repo_root)
        except OSError:
            pass
    segs = [s for s in clean.split("/") if s]
    name = segs[-1]
    table = index["dirs"] if is_dir else index["files"]
    cands = list(table.get(name, []))
    if not is_dir:
        cands += index["stems"].get(name.rsplit(".", 1)[0], [])
    for rel in cands:
        if _suffix_match(rel.split("/"), segs):
            return True, rel
    if cands:
        # basename/stem ton tai noi khac repo (file da doi cho) -> deliverable VAN dap dat.
        # Hop dong tool la "file co ton tai khong", khong phai "dung y duong dan da khai".
        return True, cands[0]
    return False, None


# ── reconcile ────────────────────────────────────────────────────────────────
def reconcile(draft_path, repo_root, index):
    text = read(draft_path)
    if text is None:
        return {"skip": "khong doc duoc file"}
    plan_items = parse_plan(section(text, "Plan"))
    agent_rows = parse_agent_table(section(text, "Agent Task Assignment"))
    status = draft_status(text)
    if not plan_items and not agent_rows:
        return {"skip": "khong co '## Plan' lan '## Agent Task Assignment'", "status": status}

    by_label, order = {}, []

    def task(label, display):
        if label not in by_label:
            by_label[label] = {
                "display": display, "agent": "—", "status": "", "claimed": False, "arts": []
            }
            order.append(label)
        return by_label[label]

    for it in plan_items:
        t = task(it["label"], it["label"])
        t["arts"].extend(it["arts"])
        if it["checked"]:
            t["claimed"] = True

    for r in agent_rows:
        label = r["label"] or ("ROW:" + (r["task"][:28] or "?"))
        t = task(label, r["label"] or (r["task"][:28] or "?"))
        if r["agent"]:
            t["agent"] = r["agent"]
        if r["status"]:
            t["status"] = r["status"]
        t["arts"].extend(r["arts"])
        if is_done_status(r["status"]):
            t["claimed"] = True

    results = []
    for label in order:
        t = by_label[label]
        # 1 file co the duoc khai 2 cach (Plan: 'wiki/x/a.md' + Agent cell: 'a.md') -> gop:
        # key = duong dan da resolve (neu co tren dia), nguoc lai = basename. Giu chuoi dai hon.
        best = {}
        for a in t["arts"]:
            ok, where = resolve(a, repo_root, draft_path, index)
            key = (where or "").lower() if ok else "∅:" + a.rstrip("/").split("/")[-1].lower()
            cur = best.get(key)
            if cur is None or len(a) > len(cur["artifact"]):
                best[key] = {
                    "task": t["display"], "agent": t["agent"], "claimed": t["claimed"],
                    "artifact": a, "disk": ok, "where": where,
                }
        results.extend(best.values())

    sl = seq_link(text)
    if sl:
        p = draft_path.parent / sl
        ok, where = False, None
        try:
            if p.is_file():
                ok, where = True, _rel(p, repo_root)
        except OSError:
            pass
        if not ok:
            ok, where = resolve(sl.split("/")[-1], repo_root, draft_path, index)
        results.append({
            "task": "(seq-diagram)", "agent": "—", "claimed": True,
            "artifact": sl, "disk": ok, "where": where,
        })

    return {"results": results, "status": status, "seq": sl,
            "n_plan": len(plan_items), "n_agent": len(agent_rows)}


# ── reporting ────────────────────────────────────────────────────────────────
DELIVERED = "✓ delivered"
OPEN_MISS = "· missing (open)"
CLAIMED_X = "✗ CLAIMED-DONE BUT ABSENT"


def _shorten(s, w):
    if len(s) <= w:
        return s
    return "…" + s[-(w - 1):]


def report(draft_path, rec):
    name = Path(draft_path).name
    print()
    if "skip" in rec:
        st = rec.get("status", "")
        print(f"── {name}   (status: {st or '?'})")
        print(f"   ⤳ bo qua (fail-open): {rec['skip']}")
        return 0, 0, 0
    rows = rec["results"]
    print(f"── {name}   (status: {rec['status'] or '?'})")
    print(f"   plan tasks: {rec['n_plan']}   agent rows: {rec['n_agent']}   "
          f"seq: {Path(rec['seq']).name if rec['seq'] else '∅'}")
    if not rows:
        print("   ⤳ khong co artifact nao duoc khai trong Plan/Agent rows — khong co gi de doi chieu.")
        return 0, 0, 0

    delivered = missing = absent = 0
    table = []
    for r in rows:
        if r["disk"]:
            verdict = DELIVERED
            delivered += 1
        elif r["claimed"]:
            verdict = CLAIMED_X
            absent += 1
        else:
            verdict = OPEN_MISS
            missing += 1
        table.append((
            r["task"], r["agent"], "yes" if r["claimed"] else "no",
            _shorten(r["artifact"], 46), "yes" if r["disk"] else "NO", verdict,
        ))

    head = ("TASK", "AGENT", "DONE?", "ARTIFACT", "DISK", "VERDICT")
    cols = list(zip(*([head] + table)))
    w = [min(max(len(str(c)) for c in col), 46) for col in cols]
    fmt = "   " + "  ".join("{:<%d}" % wi for wi in w)
    print(fmt.format(*head))
    for row in table:
        print(fmt.format(*row))

    print(f"   Σ  delivered={delivered}  missing-open={missing}  "
          f"claimed-done-but-absent={absent}")
    if absent:
        print(f"   ↳ {absent} artifact khai DONE nhung VANG tren dia "
              f"(R7 cho qua truoc fan-out, sau dispatch khong ai check) — "
              f"chay --strict de fail CI:")
        for r in rows:
            if not r["disk"] and r["claimed"]:
                print(f"       - {r['task']:<8} {r['artifact']}")
    return delivered, missing, absent


# ── discovery / cli ──────────────────────────────────────────────────────────
def find_repo_root(start):
    p = Path(start).resolve()
    for d in [p] + list(p.parents):
        if (d / ".git").exists():
            return d
    return Path(start).resolve()


def scan_targets(repo_root):
    out = []
    for rel in SCAN_DIRS:
        d = repo_root / rel
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            if p.name in SKIP_NAMES:
                continue
            text = read(p)
            if text and is_draft_done(draft_status(text)):
                out.append(p)
    # dedupe (draft & sources/draft co the chong)
    seen, uniq = set(), []
    for p in out:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            uniq.append(p)
    return uniq


def main():
    ap = argparse.ArgumentParser(
        description="Hau-kiem R7: doi chieu loi-hua proposal (Agent Task Assignment + Plan) voi dia."
    )
    ap.add_argument("drafts", nargs="*", help="duong dan draft .md; bo trong = --scan")
    ap.add_argument("--scan", action="store_true",
                    help="quet draft da implemented/done trong cac draft dir")
    ap.add_argument("--strict", action="store_true",
                    help="exit 2 neu co bat ky artifact claimed-done-but-absent")
    ap.add_argument("--root", default=None, help="repo root (mac dinh: tu dong tim .git)")
    args = ap.parse_args()

    seed = args.drafts[0] if args.drafts else "."
    repo_root = Path(args.root).resolve() if args.root else find_repo_root(seed)

    if args.drafts:
        targets = [Path(p) for p in args.drafts]
        mode = "explicit"
    else:
        targets = scan_targets(repo_root)
        mode = "scan"

    print(f"[dispatch-verify] hau-kiem R7 — proposal claims vs disk  ({mode})")
    print(f"  repo: {repo_root}")
    if not targets:
        if mode == "scan":
            print("  khong co draft nao o trang thai implemented/done de doi chieu. (OK)")
        else:
            print("  khong co draft hop le.")
        sys.exit(0)

    index = build_index(repo_root)
    tot_d = tot_m = tot_a = 0
    for t in targets:
        d, m, a = report(t, reconcile(t, repo_root, index))
        tot_d += d
        tot_m += m
        tot_a += a

    print()
    print(f"[dispatch-verify] TONG: delivered={tot_d}  missing-open={tot_m}  "
          f"claimed-done-but-absent={tot_a}  ({len(targets)} draft)")
    if args.strict and tot_a:
        print(f"[dispatch-verify] STRICT FAIL — {tot_a} artifact khai done nhung vang tren dia.",
              file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
