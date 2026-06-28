#!/usr/bin/env python3
"""harness-lint — the harness guarding itself against silent guardrail drift.

A guardrail is only as strong as its weakest copy. Two kinds of copy quietly rot:

  --constants  Every wiki-scanning tool needs the SAME content-dir set. When the
               set is hand-copied into each file, one copy can fall behind (it
               did: wiki-health.py and arch-scan.py kept scanning only four dirs
               while the canon grew to six, so broken wikilinks under
               architecture/ and tours/ passed pre-commit). This check extracts
               each file's dir-set literal by regex and asserts it equals the
               canonical set in harness/wikidirs.py — printing exactly which file
               diverged and how.

  --wiring     Every policy rule of kind `hook_event` declares an `event:`
               (Stop, PostToolUse, SessionStart, UserPromptSubmit). This check
               asserts each such event is actually present in the deployed
               llmwiki/.claude/settings.json hooks object, so a rule can't be
               declared in policy yet sit un-deployed. It also reports settings
               hooks that have no backing hook_event rule — informational, since
               those may legitimately be driven by a non-hook_event rule
               (e.g. PreToolUse by the R1 deny-write rule, SessionEnd by
               housekeeping).

  --scanners   Every tool that walks the wiki tree — R3 index-membership and R9 OKF —
               must skip gitignored local-only files (archive/draft/html). When the
               skip is hand-copied into each scanner, one copy can lose it (it did:
               harness-events.py and audit.py both flagged archived files until the
               skip was restored). This check asserts each scanner still carries a
               `git check-ignore` / gitignored() marker.

  --copies     The R3 index-sync validator ships in two trees that must stay
               byte-identical: harness/validators (used by pre-commit/audit) and
               llmwiki/.claude/hooks/validators (the deployed Stop-hook copy, kept
               self-contained for downstream clones without harness/). They drifted
               once — the deployed copy lost the self-heal fix() master had. This
               check asserts each synced pair is identical.

  --check      Run all; exit 2 if any reports drift. Wire this into
               pre-commit and CI.
  (no flags)   Report all and exit 0 (non-gating).

Fail-open by design: a missing harness/wikidirs.py, policy.yaml, or settings.json
(or absent pyyaml) is reported and skipped — harness-lint never crashes a commit
on its own missing inputs.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parents[1]      # <repo>/harness
REPO_ROOT = HARNESS_DIR.parent                         # <repo>

# Each wiki-scanning file plus the name of the variable that holds its
# content-dir-set literal. The variable names deliberately differ across files
# (CONTENT_DIRS / dirs / R5_DIRS) and the literal is a tuple in some and a set in
# others — we anchor the regex on the variable name so we never mistake an
# unrelated literal (e.g. okf-check's DIR_TYPE = {"concepts": ...}) for the set.
CONSTANT_FILES = [
    ("harness/validators/index_sync.py", "CONTENT_DIRS"),
    ("harness/scripts/okf-check.py",     "CONTENT_DIRS"),
    ("harness/scripts/health-check.py",  "dirs"),
    ("harness/scripts/wiki-health.py",   "CONTENT_DIRS"),
    ("harness/scripts/arch-scan.py",     "R5_DIRS"),
]

POLICY_PATH = "harness/poc-vendor-neutral/policy.yaml"
SETTINGS_PATH = "llmwiki/.claude/settings.json"

# A quoted lowercase-ish identifier token, e.g. "concepts" or 'tours'.
_TOKEN_RE = re.compile(r"""['"]([A-Za-z][A-Za-z0-9_-]*)['"]""")

# Wiki-tree scanners that walk the wiki tree and so MUST skip gitignored local-only files
# (archive/draft/html) — else they false-positive on them. Covers R3 index-membership
# (harness-events.py, the two index_sync.py, audit.py) AND R9 OKF (okf-check.py). It bit
# twice: harness-events.py m_stop and audit.py both flagged archived files until the skip was
# added. This asserts each still carries the skip, so a future edit can't silently drop it.
# Marker = a `git check-ignore` call or a gitignored() helper.
WIKI_TREE_SCANNERS = [
    "harness/poc-vendor-neutral/bin/harness-events.py",
    "harness/scripts/audit.py",
    "harness/scripts/okf-check.py",
    "harness/validators/index_sync.py",
    "llmwiki/.claude/hooks/validators/index_sync.py",
]
_SKIP_RE = re.compile(r"check-ignore|gitignored")

# Hand-synced validator copies that MUST stay byte-identical: the R3 index-sync validator
# lives in the framework repo (harness/validators) AND ships in the deployed llmwiki hook tree
# (which must be self-contained for downstream clones that don't carry harness/). They drifted
# once — the deployed copy lost the self-heal fix() that master gained. This asserts they match.
SYNCED_COPIES = [
    ("harness/validators/index_sync.py", "llmwiki/.claude/hooks/validators/index_sync.py"),
]


def _canonical_dirs():
    """Read CONTENT_DIRS from harness/wikidirs.py (the single source of truth).

    Returns the tuple, or None to fail-open if the module is missing/unreadable.
    """
    if str(HARNESS_DIR) not in sys.path:
        sys.path.insert(0, str(HARNESS_DIR))
    try:
        import wikidirs  # harness/wikidirs.py
    except Exception:
        return None
    return tuple(getattr(wikidirs, "CONTENT_DIRS", ())) or None


def _extract_dirset(text, varname):
    """Return the tuple of quoted tokens in the literal assigned to `varname`.

    Matches `varname = ( ... )` or `varname = { ... }` (the literal is a flat
    list/set/tuple of quoted dir names). Returns None if no such assignment is
    found. Anchored at line start so it ignores comments and unrelated uses.
    """
    pat = re.compile(
        r"(?m)^[ \t]*" + re.escape(varname) + r"[ \t]*=[ \t]*[(\[{](.*?)[)\]}]",
        re.DOTALL,
    )
    m = pat.search(text)
    if not m:
        return None
    return tuple(_TOKEN_RE.findall(m.group(1)))


def check_constants():
    """Assert every wiki-scanner's dir-set equals harness/wikidirs.py.

    Returns (drift_count, report_lines).
    """
    lines = ["== --constants : wiki content-dir set is single-sourced =="]
    canonical = _canonical_dirs()
    if canonical is None:
        lines.append("  fail-open: harness/wikidirs.py not importable — skipping "
                     "constants check.")
        return 0, lines
    canon_set = set(canonical)
    lines.append("  canonical (harness/wikidirs.py): %s  [%d dirs]"
                 % (", ".join(canonical), len(canonical)))

    drift = 0
    for rel, varname in CONSTANT_FILES:
        path = REPO_ROOT / rel
        if not path.is_file():
            lines.append("  WARN  %s : file missing (fail-open, not counted)" % rel)
            continue
        got = _extract_dirset(
            path.read_text(encoding="utf-8", errors="replace"), varname)
        if got is None:
            lines.append("  DRIFT %s : no `%s = (...)` dir-set literal found"
                         % (rel, varname))
            drift += 1
            continue
        got_set = set(got)
        if got_set == canon_set:
            lines.append("  ok    %s : %s matches canonical (%d dirs)"
                         % (rel, varname, len(got_set)))
            continue
        how = []
        missing = sorted(canon_set - got_set)
        extra = sorted(got_set - canon_set)
        if missing:
            how.append("missing %s" % ",".join(missing))
        if extra:
            how.append("extra %s" % ",".join(extra))
        lines.append("  DRIFT %s : %s={%s} (%d dirs)  ->  %s"
                     % (rel, varname, ",".join(got), len(got_set), "; ".join(how)))
        drift += 1
    return drift, lines


def check_scanners():
    """Assert every wiki-tree scanner skips gitignored files.

    Returns (drift_count, report_lines). A missing file is WARN (fail-open), not drift.
    """
    lines = ["== --scanners : every wiki-tree scanner skips gitignored =="]
    drift = 0
    for rel in WIKI_TREE_SCANNERS:
        path = REPO_ROOT / rel
        if not path.is_file():
            lines.append("  WARN  %s : file missing (fail-open, not counted)" % rel)
            continue
        if _SKIP_RE.search(path.read_text(encoding="utf-8", errors="replace")):
            lines.append("  ok    %s : skips gitignored" % rel)
        else:
            lines.append("  DRIFT %s : no `git check-ignore` / gitignored() — will "
                         "false-positive on archive/draft local-only files" % rel)
            drift += 1
    return drift, lines


def check_copies():
    """Assert hand-synced validator copies are byte-identical.

    Returns (drift_count, report_lines). A missing copy is WARN (fail-open), not drift.
    """
    lines = ["== --copies : hand-synced validator copies stay byte-identical =="]
    drift = 0
    for a, b in SYNCED_COPIES:
        pa, pb = REPO_ROOT / a, REPO_ROOT / b
        if not pa.is_file() or not pb.is_file():
            lines.append("  WARN  %s <-> %s : a copy is missing (fail-open, not counted)" % (a, b))
            continue
        if pa.read_text(encoding="utf-8") == pb.read_text(encoding="utf-8"):
            lines.append("  ok    %s == %s : identical" % (a, b))
        else:
            lines.append("  DRIFT %s != %s : copies diverged — re-sync (cp master -> deployed)" % (a, b))
            drift += 1
    return drift, lines


def check_wiring():
    """Assert every hook_event policy rule is wired in the deployed settings.json.

    Returns (drift_count, report_lines). Fail-open on any missing/unparseable input.
    """
    lines = ["== --wiring : every hook_event policy rule is deployed in settings.json =="]
    try:
        import yaml
    except Exception:
        lines.append("  fail-open: pyyaml not available — skipping wiring check.")
        return 0, lines

    policy_file = REPO_ROOT / POLICY_PATH
    settings_file = REPO_ROOT / SETTINGS_PATH
    if not policy_file.is_file():
        lines.append("  fail-open: %s missing — skipping wiring check." % POLICY_PATH)
        return 0, lines
    if not settings_file.is_file():
        lines.append("  fail-open: %s missing — skipping wiring check." % SETTINGS_PATH)
        return 0, lines
    try:
        policy = yaml.safe_load(policy_file.read_text(encoding="utf-8")) or {}
        settings = json.loads(settings_file.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        lines.append("  fail-open: could not parse policy/settings (%s) — skipping." % exc)
        return 0, lines

    # event -> "R3 index-sync"  for each rule of kind hook_event
    policy_events = {}
    for key, rule in (policy.get("rules") or {}).items():
        if isinstance(rule, dict) and rule.get("kind") == "hook_event":
            event = rule.get("event")
            if event:
                policy_events.setdefault(
                    event, "%s %s" % (rule.get("id", "?"), rule.get("name", key)))
    settings_events = set((settings.get("hooks") or {}).keys())

    lines.append("  policy hook_event events : %s"
                 % (", ".join("%s=%s" % (e, r) for e, r in sorted(policy_events.items()))
                    or "(none)"))
    lines.append("  settings.json hooks      : %s"
                 % (", ".join(sorted(settings_events)) or "(none)"))

    drift = 0
    missing = sorted(set(policy_events) - settings_events)
    for event in missing:
        lines.append("  DRIFT policy event '%s' (%s) is NOT wired in settings.json hooks"
                     % (event, policy_events[event]))
        drift += 1
    if not missing:
        lines.append("  ok    all %d policy hook_event events are wired in settings.json"
                     % len(policy_events))

    # Reverse direction is informational, not drift: a deployed hook may be driven
    # by a non-hook_event rule (PreToolUse <- R1 deny-write, SessionEnd <- housekeeping).
    for event in sorted(settings_events - set(policy_events)):
        lines.append("  note  settings hook '%s' has no backing hook_event policy rule "
                     "(ok if a non-hook_event rule covers it)" % event)
    return drift, lines


def main():
    ap = argparse.ArgumentParser(
        description="harness-lint — the harness guarding itself against guardrail drift")
    ap.add_argument("--constants", action="store_true",
                    help="check the wiki content-dir set is single-sourced from wikidirs.py")
    ap.add_argument("--wiring", action="store_true",
                    help="check every hook_event policy rule is deployed in settings.json")
    ap.add_argument("--scanners", action="store_true",
                    help="check every wiki-tree scanner skips gitignored")
    ap.add_argument("--copies", action="store_true",
                    help="check hand-synced validator copies are byte-identical")
    ap.add_argument("--check", action="store_true",
                    help="run both; exit 2 on any drift (use in pre-commit / CI)")
    args = ap.parse_args()

    do_constants = args.constants or args.check
    do_wiring = args.wiring or args.check
    do_scanners = args.scanners or args.check
    do_copies = args.copies or args.check
    gating = args.constants or args.wiring or args.scanners or args.copies or args.check
    if not (do_constants or do_wiring or do_scanners or do_copies):  # no flags -> default report, non-gating
        do_constants = do_wiring = do_scanners = do_copies = True
        gating = False

    total_drift = 0
    out = []
    if do_constants:
        d, ls = check_constants()
        total_drift += d
        out += ls + [""]
    if do_scanners:
        d, ls = check_scanners()
        total_drift += d
        out += ls + [""]
    if do_copies:
        d, ls = check_copies()
        total_drift += d
        out += ls + [""]
    if do_wiring:
        d, ls = check_wiring()
        total_drift += d
        out += ls + [""]

    out.append("== summary : %d drift finding(s) ==" % total_drift)
    if total_drift:
        out.append("FAIL — a guardrail constant or wiring has drifted from its single source.")
    else:
        out.append("OK — harness is self-consistent.")
    print("\n".join(out))

    sys.exit(2 if (gating and total_drift) else 0)


if __name__ == "__main__":
    main()
