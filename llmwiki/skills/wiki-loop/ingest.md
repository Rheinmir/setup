---
name: ingest
description: Process new file in llmwiki/raw/ and distill into wiki pages
---

# Skill: ingest

## Purpose
Process new file in `raw/`, distill knowledge into wiki. Each ingest touches 10-15 wiki files.

## When to invoke
Automatically when new file appears in `raw/`.

## Steps
1. Read source file in `raw/` completely. No premature summarizing.
2. Extract key takeaways: facts, decisions, entities, concepts from source.
3. For each entity or concept:
   - Has wiki page: open it, add/revise relevant info.
   - No page: create in `wiki/concepts/` or `wiki/entities/`.
4. Create or update summary page in `wiki/sources/` for source (link back to `raw/` file).
5. Add `[[wikilinks]]` between all new/updated pages.
6. Update `wiki/index.md` for every file created or modified.
7. Append to `wiki/log.md`: `## YYYY-MM-DD — ingest — <filename>` with bullet list of all pages touched.

## Rules
- **OKF v0.1 (R9):** every wiki page starts with a YAML frontmatter block (`---`) carrying a non-empty `type` (e.g. `concept`, `entity`, `source`) plus optional `title`/`tags`/`timestamp`/`resource`. Copy the matching `_template.md`. Keep the `## Origin` body section (R2).
- Never modify file in `raw/`. Read only.
- No wiki page unless source actually introduces that entity or concept.
- Prefer updating existing page over creating duplicate.