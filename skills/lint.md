# Skill: lint

## Purpose
Periodic health check of the wiki. Finds contradictions, stale claims, orphaned pages, missing cross-references, and knowledge gaps.

## When to invoke
- Periodically (after every 10 ingests or on user request)
- When the wiki feels stale or inconsistent

## Steps
1. **Orphans** — find wiki pages not linked from any other page or `wiki/index.md`. Flag each one.
2. **Missing links** — find mentions of entity or concept names that exist as wiki pages but are not written as `[[wikilinks]]`. Fix them in place.
3. **Contradictions** — find claims across pages that directly contradict each other. List each pair with file paths and line numbers. Do not silently pick a winner — flag for human review.
4. **Stale claims** — find pages that reference `raw/` sources. Check if a newer version of that source exists in `raw/`. Flag if so.
5. **Index gaps** — find wiki files not listed in `wiki/index.md`. Add missing rows.
6. **Empty pages** — find pages with no content beyond the header. Flag for deletion or population.
7. **Missing Origin** — find wiki files without an `## Origin` section. Flag each one as incomplete — do not guess the source.
8. Append to `wiki/log.md`: `## YYYY-MM-DD — lint` with a summary of issues found and fixed vs flagged.

## Rules
- Fix what can be fixed automatically (missing links, index gaps).
- Flag but do not resolve contradictions or delete pages — those need human decision.
