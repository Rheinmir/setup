#!/usr/bin/env python3
"""Harness doctor — a guardrail fire-drill that PROVES each rule still bites today.

Why this exists
---------------
The harness is fail-open at every layer on purpose, so a broken rail never bricks
a working session:

  * hooklib.find_validators() returns None when no validators dir is found, and the
    hooks then exit 0 (allow);
  * the poc llmwiki-validate fails open on any internal error;
  * the L1 hooks swallow exceptions.

That safety has a dark side: a validator that has silently stopped working — a bad
edit, a stale copy, a missing interpreter — will pass EVERYTHING, and nobody is
told the rails went dark. This script is the smoke detector. For each content
validator it ships a tiny known-BAD and known-GOOD fixture in a throwaway temp
dir, runs the REAL validator through its REAL contract, and asserts the bad input
is blocked and the good input is allowed. A rule whose BAD fixture is not blocked
is a DARK RAIL.

The contract (harness/recipe.md, section 2)
-------------------------------------------
Every validator accepts either:
  * argv file paths   :  validator.py path1 path2 ...            (L2 / pre-commit)
  * stdin event JSON  :  {"action":"write","file_path":...,
                          "content":...}                          (L1 / realtime)
and exits 2 to block (reason on stderr) or 0 to allow. This doctor exercises BOTH
contracts for every rule, because a validator can break in one mode while still
passing in the other.

Usage
-----
  harness-doctor.py            print the green/red board, exit 0
  harness-doctor.py --ci       exit non-zero if any rule's bite-test failed
  harness-doctor.py --json     machine-readable board to stdout
  harness-doctor.py --keep     leave the temp fixtures on disk (debugging)
  harness-doctor.py --no-color plain ASCII, no ANSI

Exit code: default always 0. With --ci, exit 1 if any rule is a dark rail (its BAD
fixture was not blocked, or its GOOD fixture was wrongly blocked). Install probes
are advisory — they are reported but never change the exit code.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo layout. This file lives at <repo>/harness/scripts/harness-doctor.py, so
# the repo root is two parents up. Everything below is resolved from there.
# ---------------------------------------------------------------------------
SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
HARNESS_VALIDATORS = REPO / "harness" / "validators"
HOOKS_DIR = REPO / "llmwiki" / ".claude" / "hooks"
HOOKS_VALIDATORS = HOOKS_DIR / "validators"
SETTINGS = REPO / "llmwiki" / ".claude" / "settings.json"
PRECOMMIT_CFG = REPO / ".pre-commit-config.yaml"
GIT_PRECOMMIT_HOOK = REPO / ".git" / "hooks" / "pre-commit"

PY = sys.executable  # validators run under the same interpreter as the doctor

# Hooks referenced by settings.json (each invoked as `python3 <hook>.py`, so the
# executable bit is irrelevant — we still report it as information).
EXPECTED_HOOKS = [
    "hooklib.py",
    "user_prompt_submit.py",
    "pre_tool_use.py",
    "orca_guard.py",
    "post_tool_use.py",
    "stop.py",
    "session_end.py",
    "session_start.py",
]


# ---------------------------------------------------------------------------
# Validator resolution — mirror hooklib.find_validators() so we bite-test the
# exact validator that actually fires in a live session:
#   env LLMWIKI_VALIDATORS  ->  copy beside the hooks  ->  harness/validators.
# ---------------------------------------------------------------------------
def resolve_validator(name):
    env = os.environ.get("LLMWIKI_VALIDATORS")
    if env and (Path(env) / name).is_file():
        return Path(env) / name, "env:LLMWIKI_VALIDATORS"
    if (HOOKS_VALIDATORS / name).is_file():
        return HOOKS_VALIDATORS / name, "hooks-copy"
    if (HARNESS_VALIDATORS / name).is_file():
        return HARNESS_VALIDATORS / name, "harness-src"
    return None, "UNRESOLVED"


def run_argv(validator, argv):
    p = subprocess.run([PY, str(validator), *argv], capture_output=True, text=True, timeout=30)
    return p.returncode


def run_stdin(validator, event):
    p = subprocess.run([PY, str(validator)], input=json.dumps(event),
                       capture_output=True, text=True, timeout=30)
    return p.returncode


# ---------------------------------------------------------------------------
# Fixtures. Each builder writes a tiny BAD and GOOD file under <base>/<rule>/ and
# returns the argv paths plus the equivalent stdin events for both contracts.
# Fixtures NEVER touch the repo tree — only the temp base passed in.
# ---------------------------------------------------------------------------
def _w(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def fixture(bad_path, good_path, bad_content=None, good_content=None):
    """Package a bad/good pair into argv + stdin events for both contracts.

    For content-driven validators we pass `content` inline on the stdin event so
    the realtime path is exercised exactly as the L1 hook would deliver it; the
    argv path always reads the same bytes from disk.
    """
    bad_ev = {"action": "write", "file_path": str(bad_path)}
    good_ev = {"action": "write", "file_path": str(good_path)}
    if bad_content is not None:
        bad_ev["content"] = bad_content
    if good_content is not None:
        good_ev["content"] = good_content
    return {
        "bad_argv": [str(bad_path)],
        "good_argv": [str(good_path)],
        "bad_event": bad_ev,
        "good_event": good_ev,
    }


def build_r1(base):
    # R1: bad = a path inside raw/ (the human inbox); good = a normal path.
    bad = _w(base / "llmwiki" / "raw" / "inbox.md", "# dropped by a human\n")
    good = _w(base / "llmwiki" / "wiki" / "concepts" / "clean.md", "# normal path\n")
    return fixture(bad, good)


def build_r2(base):
    # R2: bad = wiki content file with no '## Origin'; good = the same with one.
    bad_c = "# Concept\n\nBody text but no origin section.\n"
    good_c = ("# Concept\n\nBody text.\n\n## Origin\n\n"
              "Distilled from raw/example.md (commit abc1234).\n")
    bad = _w(base / "wiki" / "concepts" / "no-origin.md", bad_c)
    good = _w(base / "wiki" / "concepts" / "with-origin.md", good_c)
    return fixture(bad, good, bad_c, good_c)


def build_r5(base):
    # R5: bad = a .md loose at wiki/ root; good = the same under concepts/.
    bad = _w(base / "wiki" / "loose.md", "# wrong place\n")
    good = _w(base / "wiki" / "concepts" / "proper.md", "# right place\n")
    return fixture(bad, good)


def build_r7(base):
    # R7: bad  = a proposed draft missing the Agent table and the sequence link.
    #     good = a complete draft + a matching sequence html (one diagram with a
    #            visible prose description per planned task).
    draft = base / "wiki" / "sources" / "draft"
    seq_html = (
        "<!doctype html><html><head><style>.msg{opacity:1}</style></head><body>\n"
        '<div class="diagram-box"><p class="desc">Task one: claude distills the raw '
        "file into a concept on a safe branch.</p></div>\n"
        '<div class="diagram-box"><p class="desc">Task two: codex updates wiki/index.md '
        "for the new concept.</p></div>\n"
        "</body></html>\n"
    )
    _w(draft / "feature-seq.html", seq_html)
    good_c = (
        "---\ntype: draft\n---\n"
        "# Feature X — proposal\n\n"
        "**Status:** proposed\n\n"
        "## Context\n"
        "Da query wiki: lien quan [[rule-registry]] va ADR-008 ve the kit (force-query R7-f).\n\n"
        "## Plan\n"
        "- [ ] task one — distill raw\n"
        "- [ ] task two — update index\n\n"
        "## Agent Task Assignment\n"
        "| Task | Agent | Notes |\n"
        "|------|-------|-------|\n"
        "| task one | claude | distill |\n"
        "| task two | codex | index |\n\n"
        "**Sequence diagram**: [seq](feature-seq.html)\n"
    )
    bad_c = (
        "---\ntype: draft\n---\n"
        "# Feature Y — proposal\n\n"
        "**Status:** proposed\n\n"
        "## Plan\n"
        "- [ ] only task\n"
    )
    good = _w(draft / "feature.md", good_c)
    bad = _w(draft / "feature-bad.md", bad_c)
    # R7 always reads from disk and ignores stdin `content`, so no inline content.
    return fixture(bad, good)


def build_r9(base):
    # R9: bad = wiki concept with no YAML frontmatter; good = with `type:`.
    bad_c = "# Concept\n\nNo frontmatter block at the top.\n"
    good_c = "---\ntype: concept\n---\n\n# Concept\n\nHas frontmatter.\n"
    bad = _w(base / "wiki" / "concepts" / "no-fm.md", bad_c)
    good = _w(base / "wiki" / "concepts" / "with-fm.md", good_c)
    return fixture(bad, good, bad_c, good_c)


RULES = [
    ("R1", "no_write_raw.py", "no-write-raw", build_r1),
    ("R2", "origin_required.py", "origin-required", build_r2),
    ("R5", "folder_structure.py", "folder-structure", build_r5),
    ("R7", "proposal_complete.py", "proposal-complete", build_r7),
    ("R9", "okf_frontmatter.py", "okf-frontmatter", build_r9),
]


# ---------------------------------------------------------------------------
# Run the bite-tests.
# ---------------------------------------------------------------------------
def run_bite_tests(base):
    results = []
    resolved_src = None
    for rid, fname, label, builder in RULES:
        validator, src = resolve_validator(fname)
        if resolved_src is None and src != "UNRESOLVED":
            resolved_src = src
        rule = {"id": rid, "validator": fname, "label": label, "source": src}
        if validator is None:
            rule.update({
                "green": False,
                "argv": {"bad": None, "good": None},
                "stdin": {"bad": None, "good": None},
                "note": "validator file not found — find_validators() would return "
                        "None and the rail fails OPEN (dark rail).",
            })
            results.append(rule)
            continue
        fx = builder(base / rid)
        argv_bad = run_argv(validator, fx["bad_argv"])
        argv_good = run_argv(validator, fx["good_argv"])
        stdin_bad = run_stdin(validator, fx["bad_event"])
        stdin_good = run_stdin(validator, fx["good_event"])
        rule["argv"] = {"bad": argv_bad, "good": argv_good}
        rule["stdin"] = {"bad": stdin_bad, "good": stdin_good}
        green = argv_bad == 2 and argv_good == 0 and stdin_bad == 2 and stdin_good == 0
        rule["green"] = green
        notes = []
        if argv_bad != 2:
            notes.append("argv BAD not blocked (exit %s, want 2)" % argv_bad)
        if argv_good != 0:
            notes.append("argv GOOD wrongly blocked (exit %s, want 0)" % argv_good)
        if stdin_bad != 2:
            notes.append("stdin BAD not blocked (exit %s, want 2)" % stdin_bad)
        if stdin_good != 0:
            notes.append("stdin GOOD wrongly blocked (exit %s, want 0)" % stdin_good)
        rule["note"] = "; ".join(notes)
        results.append(rule)
    return results, (resolved_src or "UNRESOLVED")


# ---------------------------------------------------------------------------
# Install probes (advisory). Each returns (state, label, detail) where state is
# True (ok), False (problem), or None (neutral / info).
# ---------------------------------------------------------------------------
def probe_hooks():
    present = [h for h in EXPECTED_HOOKS if (HOOKS_DIR / h).is_file()]
    all_py = sorted(HOOKS_DIR.glob("*.py")) if HOOKS_DIR.is_dir() else []
    execable = sum(1 for h in all_py if os.access(h, os.X_OK))
    ok = len(present) == len(EXPECTED_HOOKS)
    detail = ("%d/%d expected hooks in llmwiki/.claude/hooks (%d/%d +x; "
              "invoked via `python3` per settings.json, so +x not required)"
              % (len(present), len(EXPECTED_HOOKS), execable, len(all_py)))
    if not ok:
        missing = [h for h in EXPECTED_HOOKS if h not in present]
        detail += " — MISSING: " + ", ".join(missing)
    return ok, "hooks present", detail


def probe_settings():
    ok = SETTINGS.is_file()
    return ok, "settings.json", ("llmwiki/.claude/settings.json"
                                 if ok else "MISSING llmwiki/.claude/settings.json")


def probe_validators_resolvable():
    names = [fname for _, fname, _, _ in RULES] + ["index_sync.py"]
    srcs = {}
    unresolved = []
    for n in names:
        v, s = resolve_validator(n)
        srcs[s] = srcs.get(s, 0) + 1
        if v is None:
            unresolved.append(n)
    ok = not unresolved
    via = ", ".join("%s=%d" % (k, v) for k, v in srcs.items() if k != "UNRESOLVED")
    detail = "%d/%d resolvable (%s)" % (len(names) - len(unresolved), len(names), via or "none")
    if unresolved:
        detail += " — UNRESOLVED: " + ", ".join(unresolved)
    return ok, "validators resolvable", detail


def probe_validator_drift():
    if not (HOOKS_VALIDATORS.is_dir() and HARNESS_VALIDATORS.is_dir()):
        return None, "validator drift", "only one validators dir present — nothing to compare"
    drifted = []
    checked = 0
    for src in HARNESS_VALIDATORS.glob("*.py"):
        twin = HOOKS_VALIDATORS / src.name
        if twin.is_file():
            checked += 1
            if src.read_bytes() != twin.read_bytes():
                drifted.append(src.name)
    if drifted:
        return False, "validator drift", ("hooks-copy differs from harness-src for: "
                                          + ", ".join(drifted) + " — one copy is stale")
    return True, "validator drift", "hooks-copy == harness-src across %d validators" % checked


def probe_pyyaml():
    try:
        import yaml  # noqa: F401
        return True, "pyyaml", "import yaml OK (v%s)" % getattr(yaml, "__version__", "?")
    except Exception:
        return None, "pyyaml", ("not importable — R9 falls back to a regex `type:` "
                                "check, so the rail still bites")


def probe_precommit_config():
    ok = PRECOMMIT_CFG.is_file()
    return ok, "pre-commit config", (".pre-commit-config.yaml present"
                                     if ok else "MISSING .pre-commit-config.yaml (no L2 backstop)")


def probe_precommit_installed():
    binary = shutil.which("pre-commit")
    py = shutil.which("python")
    installed = GIT_PRECOMMIT_HOOK.is_file()
    bits = []
    bits.append("binary " + ("found" if binary else "NOT on PATH"))
    if py is None:
        bits.append("`python` NOT on PATH (only python3) — pre-commit's generated git "
                    "shim historically calls `python`; install with a python3 on PATH")
    if installed:
        return True, "pre-commit in .git/hooks", "installed (" + "; ".join(bits) + ")"
    return False, "pre-commit in .git/hooks", ("NOT installed — run `pre-commit install` "
                                               "(L2 git backstop inactive). " + "; ".join(bits))


def run_install_probes():
    return [
        probe_hooks(),
        probe_settings(),
        probe_validators_resolvable(),
        probe_validator_drift(),
        probe_pyyaml(),
        probe_precommit_config(),
        probe_precommit_installed(),
    ]


# ---------------------------------------------------------------------------
# Rendering.
# ---------------------------------------------------------------------------
def colorize(enabled):
    palette = {
        "green": "\033[32m", "red": "\033[31m", "yellow": "\033[33m",
        "dim": "\033[2m", "bold": "\033[1m", "reset": "\033[0m",
    }

    def c(text, name):
        if not enabled:
            return text
        return "%s%s%s" % (palette.get(name, ""), text, palette["reset"])
    return c


def fmt_cell(actual, expected, c):
    if actual is None:
        return c("--", "dim")
    s = "%s" % actual
    return c(s, "green" if actual == expected else "red")


def print_board(rules, resolved_src, probes, c):
    green_rules = sum(1 for r in rules if r["green"])
    total = len(rules)
    print(c("HARNESS DOCTOR", "bold") + c("  fire-drill: does each rail still bite?", "dim"))
    print(c("  repo: %s" % REPO, "dim"))
    print(c("  active validators resolved via: %s" % resolved_src, "dim"))
    print()
    print(c("RULE BITE-TESTS", "bold")
          + c("  (BAD must block -> exit 2 | GOOD must pass -> exit 0)", "dim"))
    for r in rules:
        icon = c("✓", "green") if r["green"] else c("✗", "red")
        argv = "argv bad->%s good->%s" % (
            fmt_cell(r["argv"]["bad"], 2, c), fmt_cell(r["argv"]["good"], 0, c))
        std = "stdin bad->%s good->%s" % (
            fmt_cell(r["stdin"]["bad"], 2, c), fmt_cell(r["stdin"]["good"], 0, c))
        line = "  %s %-3s %-17s %s | %s" % (icon, r["id"], r["label"], argv, std)
        print(line)
        if r["note"]:
            print(c("        ^ %s" % r["note"], "red" if not r["green"] else "dim"))
    summary = "  %d/%d rails bite." % (green_rules, total)
    print(c(summary, "green" if green_rules == total else "red"))
    print()
    print(c("INSTALL PROBES", "bold") + c("  (advisory — --ci gates only on dark rails)", "dim"))
    for state, label, detail in probes:
        if state is True:
            icon = c("✓", "green")
        elif state is False:
            icon = c("✗", "red")
        else:
            icon = c("ℹ", "yellow")
        print("  %s %-26s %s" % (icon, label, c(detail, "dim")))
    print()
    n_ok = sum(1 for s, _, _ in probes if s is True)
    n_bad = sum(1 for s, _, _ in probes if s is False)
    n_info = sum(1 for s, _, _ in probes if s is None)
    verdict = "VERDICT: %d/%d rails bite | install %d ok / %d problem / %d info" % (
        green_rules, total, n_ok, n_bad, n_info)
    print(c(verdict, "bold"))
    if green_rules < total:
        print(c("  DARK RAIL DETECTED — a validator stopped blocking its bad fixture.", "red"))
    return green_rules, total


def build_json(rules, resolved_src, probes):
    green_rules = sum(1 for r in rules if r["green"])
    return {
        "repo": str(REPO),
        "resolved_via": resolved_src,
        "rails_bite": green_rules,
        "rails_total": len(rules),
        "dark_rails": [r["id"] for r in rules if not r["green"]],
        "rules": rules,
        "install_probes": [
            {"ok": s, "label": label, "detail": detail} for s, label, detail in probes
        ],
    }


def main():
    ap = argparse.ArgumentParser(
        description="Fire-drill that proves each harness rule still blocks bad input.")
    ap.add_argument("--ci", action="store_true",
                    help="exit non-zero if any rule's bite-test failed (a dark rail)")
    ap.add_argument("--json", action="store_true", help="emit the board as JSON")
    ap.add_argument("--keep", action="store_true", help="keep temp fixtures (debugging)")
    ap.add_argument("--no-color", action="store_true", help="disable ANSI color")
    args = ap.parse_args()

    base = Path(tempfile.mkdtemp(prefix="harness-doctor-"))
    try:
        rules, resolved_src = run_bite_tests(base)
        probes = run_install_probes()
    finally:
        if args.keep:
            sys.stderr.write("[harness-doctor] kept fixtures in %s\n" % base)
        else:
            shutil.rmtree(base, ignore_errors=True)

    green_rules = sum(1 for r in rules if r["green"])
    total = len(rules)

    if args.json:
        print(json.dumps(build_json(rules, resolved_src, probes), ensure_ascii=False, indent=2))
    else:
        color_on = (not args.no_color) and sys.stdout.isatty()
        print_board(rules, resolved_src, probes, colorize(color_on))

    if args.ci and green_rules < total:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
