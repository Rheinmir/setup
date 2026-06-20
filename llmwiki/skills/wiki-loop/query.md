---
name: query
description: Synthesize answer from wiki; persist new insights as wiki entries
---

# Skill: query

## Purpose
Answer question by synthesizing wiki knowledge. Valuable findings not in wiki become new pages, compounding knowledge over time.

## When to invoke
When user asks question requiring synthesis across multiple wiki pages or raw sources.

## Steps
1. Identify relevant wiki pages. List them.
2. Read each relevant page in full.
3. If answer needs info not in wiki, check `raw/` for unprocessed sources.
4. Synthesize and answer directly.
5. Evaluate: does answer contain non-obvious insight, connection, or conclusion not already in wiki?
   - If yes: create new wiki page (concept or source), update `wiki/index.md`, log in `wiki/log.md`.
   - If no: skip.
6. Append to `wiki/log.md`: `## YYYY-MM-DD — query — <question summary>` with note on whether new page created.

## Rules
- **OKF v0.1 (R9):** any new wiki page starts with a YAML frontmatter block (`---`) with a non-empty `type`; copy the matching `_template.md` and keep the `## Origin` section.
- Never invent facts. Synthesize from wiki and `raw/` only.
- Query revealing gap (missing entity, missing concept) should trigger `ingest` of relevant `raw/` source if one exists.