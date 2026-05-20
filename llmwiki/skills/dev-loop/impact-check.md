# Skill: impact-check

## Purpose
Before modifying any symbol (function, class, variable, config key), map everything that depends on it so no callers are blindsided.

## When to use
- Before any edit to a shared utility, base class, or widely-imported module
- Before renaming or deleting anything
- As the first step of `safe-change` or `propose`

## Steps
1. Identify the exact symbol(s) to be changed.
2. Search the entire codebase for all imports, calls, or references to each symbol.
3. For each reference found, note: file path, line number, how it uses the symbol.
4. Classify each reference as:
   - **Direct** — calls or imports the symbol itself
   - **Indirect** — depends on behaviour the symbol produces (e.g. reads its output)
5. Report the full list. If zero references found outside the file, state that explicitly.
6. Flag any reference in a test file separately — those must be updated or will give false confidence.
7. If the symbol being checked is not yet documented in `wiki/`, note it as a gap — do not create the entry now. Wiki entries are only written after code is committed (see `verify-before-commit`).

## Rules
- Do not modify anything during this skill — output only.
- If the codebase is large, search by symbol name AND by file pattern (e.g. all `*.ts` files).
- Do not assume a symbol is unused because it has no direct callers — check indirect dependents too.
