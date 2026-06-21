# Skill: ingest

## Purpose
Process a new file in `raw/` and distill its knowledge into the wiki. Each ingest typically touches 10-15 wiki files.

## When to invoke
Automatically when a new file appears in `raw/`.

## Steps
1. Read the source file in `raw/` completely. Do not summarize prematurely.
2. Extract key takeaways: facts, decisions, entities, concepts introduced by the source.
3. For each entity or concept found:
   - If it already has a wiki page: open it and add/revise relevant information.
   - If it does not exist: create the appropriate file in `wiki/concepts/` or `wiki/entities/`.
4. Create or update a summary page in `wiki/sources/` for the source itself (link back to the `raw/` file).
5. Add `[[wikilinks]]` between all newly created or updated pages.
6. Update `wiki/index.md` for every file created or modified.
7. Append to `wiki/log.md`: `## YYYY-MM-DD — ingest — <filename>` with a bullet list of all pages touched.

## Rules
- Never modify the file in `raw/`. Read only.
- Do not create a wiki page unless the source actually introduces that entity or concept.
- Prefer updating an existing page over creating a duplicate.
- **OKF v0.1 (R9):** every wiki page starts with a YAML frontmatter block (`---`) carrying a non-empty `type` (e.g. `concept`, `entity`, `source`) plus optional `title`/`tags`/`timestamp`/`resource`. Copy the matching `_template.md`. Keep the `## Origin` body section (R2).
