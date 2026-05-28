---
name: impact-check
description: Map all callers and dependents of a symbol before modifying shared code
---

# Skill: impact-check

## Purpose
Before modifying any symbol (function, class, variable, config key), map all dependents so no callers blindsided.

## When to use
- Before editing shared utility, base class, or widely-imported module
- Before renaming or deleting anything
- As first step of `safe-change` or `propose`

## Steps
1. Identify exact symbol(s) to change.
2. Search entire codebase for all imports, calls, references to each symbol.
3. For each reference: note file path, line number, how it uses symbol.
4. Classify each reference:
   - **Direct** — calls or imports symbol itself
   - **Indirect** — depends on behaviour symbol produces (e.g. reads its output)
5. Report full list. If zero references found outside file, state explicitly.
6. Flag any reference in test file separately — those must update or give false confidence.
7. If symbol not yet documented in `wiki/`, note as gap — do not create entry now. Wiki entries only written after code committed (see `verify-before-commit`).

## Rules
- Do not modify anything during this skill — output only.
- If codebase large, search by symbol name AND file pattern (e.g. all `*.ts` files).
- Do not assume symbol unused because no direct callers — check indirect dependents too.