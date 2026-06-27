#!/usr/bin/env python3
"""Canonical wiki content-dir set — THE single source of truth.

Every tool that scans the wiki tree (the R3 index-sync validator, okf-check,
health-check, wiki-health, arch-scan, and any future scanner) MUST import
``CONTENT_DIRS`` from this module instead of hand-copying the tuple into its own
top-of-file constant.

Why this module exists: a hand-copied constant silently drifts. wiki-health.py
and arch-scan.py once still listed only the original FOUR dirs while the rest of
the harness had already grown to SIX — so broken wikilinks living inside
``architecture/`` and ``tours/`` pages slipped through pre-commit unnoticed,
because wiki-health runs there with ``--fail-on broken`` over a set that no
longer covered those two directories. A single weakened copy quietly downgraded
a guardrail. Importing one shared constant removes that whole class of bug:
change the set here and every scanner moves together, in lock-step, by
construction.

Order below is the conventional reading order, but membership is what actually
matters to a scanner — compare as a set, not as an ordered sequence.
"""

CONTENT_DIRS = ("concepts", "entities", "sources", "draft", "architecture", "tours")
