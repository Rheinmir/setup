# Artifact Lifecycle

This document explains how the repository treats its local-only artifacts — the
HTML renders under `llmwiki/html/` and the draft markdown under
`llmwiki/wiki/sources/draft/` and `llmwiki/wiki/draft/orca/`. These files are
deliberately gitignored: they are session output that we keep on disk locally but
do not push to the remote. Because nothing has governed their lifecycle, they have
been accumulating, duplicating, and drifting out of sync with `index.md`. This is
the lifecycle contract that fixes that, together with the tooling that enforces it.

The work was built with the **build-now-adapt-later** pattern. Everything that
depends on a stable rule — how we walk the trees, how we detect duplicates and
orphans and dangling rows, how we emit the manifest — is built and working now.
Everything that depends on a value we have **not** yet observed in practice — how
many days makes a draft stale, how many renders to keep, what triggers archival —
is quarantined in a single file, `fdk/tools/artifacts.config.yaml`, defaulted to a
documented best-guess and flagged `verified: false`. Adapting later is a one-file
edit, not a rewrite.

## Lifecycle states

An artifact moves through three states.

- **draft.** The artifact has just been produced by a session. It lives in one of
  the gitignored draft folders, it is referenced from `index.md` so the local index
  stays in sync, and it is freely editable. Most artifacts in the repo today are
  drafts. A draft is provisional: it may be revised, replaced, or discarded.

- **promoted.** The artifact has been reviewed and accepted as canonical. Promotion
  is currently a **manual** step (see `promote.mode` in the config). A promoted
  source of record is the single canonical copy for its slug; any other copy of the
  same slug is either an identical mirror or a problem to be resolved.

- **archived.** The artifact is no longer the working copy but is kept for history.
  Archival moves the file into an `archive/` subdirectory of its current folder.
  What triggers archival — a `status` field, the age of the file, or both — and how
  long a draft may sit before it is considered stale, are the values held in the
  config while we observe real behavior.

Renders are a special case. An `.html` render is treated as **disposable**: it can
be rebuilt from its markdown source, so older renders of the same slug are safe to
archive or drop. Only the markdown carries the canonical content.

## Naming rules

Every artifact name follows the form `DDMMYY-<slug>.<kind>`, where `DDMMYY` is the
day the artifact was first produced (so `210626` means 21 June 2026), `<slug>` is a
short kebab-case description, and `<kind>` is the file extension. The date prefix is
what lets the tooling sort artifacts chronologically and reason about staleness.

A markdown file and its HTML rendering **share the same slug**. For example
`270626-session-review.md` and `270626-session-review.html` are the same artifact in
two representations; the manifest treats them as a source-and-render pair, never as
a duplicate.

A `-vN` suffix (`-v1`, `-v2`, `-v3`) is reserved for **true revisions** of a single
document — successive versions that are meant to coexist. It is not a substitute for
the date prefix and it is not a place to stash near-identical copies. Because the
suffix is so often misused, the tooling flags every `-vN` name for human review
rather than silently accepting it. Names that lack a date prefix entirely (such as
`design-pattern.md` or `sync-template.md`) are likewise flagged for review.

## The deduplication rule

There is **one canonical copy per slug**. A second copy of the same slug, in a
different folder, is legal only when it is byte-for-byte identical to the canonical
copy — that is, when `diff` reports `SAME`. The moment two copies of the same slug
diverge, the repository has two competing sources of truth for the same thing, and
that is a defect.

The `artifacts.py` report detects this by grouping every artifact by `(slug,
extension)` and comparing content hashes across folders. Copies that share a slug
and an extension but differ in hash are reported as **diverging duplicate slugs**;
copies that are identical are reported separately as redundant-but-legal. The
markdown-and-HTML pair described above is never flagged, because the two files have
different extensions and therefore are never compared against each other.

The `harness/validators/duplicate_basename.py` validator enforces the simpler,
stricter guard for continuous integration: under `wiki/`, no markdown basename may
appear in two directories at all. It is intentionally blunt so that the duplicate is
caught at commit time, before the hashes have a chance to diverge.

## The adapter boundary

`fdk/tools/artifacts.config.yaml` is the single quarantine for every lifecycle value
that we cannot yet confirm. `artifacts.py` reads every threshold from it and hard-codes
none. While the config says `verified: false`, the report and the dry-run modes run
freely, but every destructive `--apply` is refused. This is the fail-safe default: we
do not delete or move anything based on a guess.

## ADAPT-CHECKLIST

When you are ready to finalize the lifecycle — after the repository has accumulated
enough artifacts to show real patterns — follow these steps. Each one is a small,
auditable edit; together they flip the system from "best-guess, read-only" to
"verified, enforcing".

1. **Observe growth.** Run `python3 fdk/tools/artifacts.py --report` over several
   weeks and read the manifest. Watch how fast drafts accumulate, how long they
   actually sit before they stop changing, and how many renders pile up per slug.

2. **Set real values.** Replace the best-guess numbers in
   `fdk/tools/artifacts.config.yaml` — `stale_days`, `keep_last_renders`, the
   `archive.trigger`, the `index.local_rows` policy, `manifest.tracked`,
   `promote.mode` — with the values your observations support. Update the
   `# ASSUMPTION (not verified)` comments to record what each value is now based on.

3. **Run conformance.** Re-run `--report`, and run the dry-run modes
   (`--dedupe`, `--archive`) to confirm that, with the real values in place, the tool
   proposes exactly the actions you expect and nothing more.

4. **Enable `--apply`.** Implement the destructive actions behind the `apply_guard`
   in `artifacts.py` so that `--dedupe --apply` and `--archive --apply` actually move
   and remove files. Keep them refused until you have done this.

5. **Flip `verified: true`.** Set `verified: true` in the config. From that point the
   guard allows `--apply`, and the values in the config are trusted as observed fact
   rather than assumption.
