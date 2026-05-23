---
name: query
description: >-
  Synthesize an answer from the wiki; persist new insights as wiki entries
---

# Skill: query

## Purpose
Answer a question by synthesizing knowledge from the wiki. Valuable findings that are not yet in the wiki become new pages, compounding knowledge over time.

## When to invoke
When the user asks a question that requires synthesizing information across multiple wiki pages or raw sources.

## Steps
1. Identify which wiki pages are relevant to the question. List them.
2. Read each relevant page in full.
3. If the answer requires information not in the wiki, check `raw/` for unprocessed sources that may contain it.
4. Synthesize and answer the question directly.
5. Evaluate: does this answer contain a non-obvious insight, connection, or conclusion not already captured in the wiki?
   - If yes: create a new wiki page (concept or source) capturing the insight, update `wiki/index.md`, and log in `wiki/log.md`.
   - If no: skip.
6. Append to `wiki/log.md`: `## YYYY-MM-DD — query — <question summary>` with a note on whether a new page was created.

## Rules
- Never invent facts. Only synthesize from wiki and `raw/` content.
- A query that reveals a gap (missing entity, missing concept) should trigger an `ingest` of the relevant `raw/` source if one exists.
