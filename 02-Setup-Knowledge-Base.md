# CONTEXT
We have defined the project goals and tech stack. Now, we must establish the Agentic Knowledge Base following the LLM Wiki pattern — a persistent, compounding artifact that the agent maintains over time. Humans curate raw sources; the agent handles summarization, cross-referencing, and maintenance.

The knowledge base has three layers:
- **`raw/`** — immutable source documents. Humans write here, agent never touches.
- **`wiki/`** — agent-maintained markdown pages: entities, concepts, sources. The agent owns this layer.
- **`AGENT.md`** — the schema: defines structure, conventions, and the three core operations (ingest, query, lint).

# INSTRUCTIONS

**IMPORTANT — before doing anything else:** Do NOT create any `.md` documentation or knowledge files in the project root. The only `.md` files allowed in root are: `AGENT.md`, `README.md`, and numbered step files (e.g. `01-*.md`).

You must execute the following file system operations:

1. Create the following folders directly in the project root (note: `.agent` already exists as a config file — do not create a `.agent/` folder):
   - `skills/` — multi-step reusable workflows the agent invokes autonomously (e.g. `propose`, `safe-change`).
   - `commands/` — single-shot, parameterized instructions triggered explicitly by the user (e.g. `scaffold-feature`, `add-env-var`).

2. Create a `raw/` folder in the root. This is the **immutable source-of-truth layer**:
   - Humans drop original documents here: articles, specs, meeting notes, vendor docs, papers, images, data files.
   - The agent NEVER writes, modifies, or deletes anything in `raw/`.
   - The agent reads `raw/` only during the `ingest` operation to distill knowledge into `wiki/`.

3. Create a `wiki/` folder. This is the **agent-maintained knowledge layer**. Use the table below to decide which subfolder:

   | Subfolder | Put here when... | Example |
   |-----------|-----------------|---------|
   | `concepts/` | Abstract idea, pattern, or domain term — explained to a new team member, not pointed to in the codebase | `rag.md`, `graph-memory.md` |
   | `entities/` | Concrete named thing in the system — service, model, API, tool, component, config | `cognee.md`, `neo4j.md` |
   | `sources/` | Distilled reference or decision record from `raw/` — URL summary, ADR, paper takeaway | `why-neo4j.md`, `cognee-docs.md` |
   | `sources/draft/` | Proposal not yet implemented (created by the `propose` skill) | `260425-new-approval-button-fe.md` |

   Each wiki file must follow this format:
   ```
   # <Title>
   **Type:** concept | entity | source
   **Tags:** tag1, tag2

   <1-3 sentence description>

   ## Notes
   <extra detail, [[wikilinks]] to related entries>

   ## Origin
   - **Source:** raw/<filename> | wiki/sources/draft/<filename> | https://...
   - **Commit:** <hash> (if created from a code change)
   - **Date:** YYYY-MM-DD
   ```
   A wiki file without `## Origin` is considered incomplete.

4. Create `wiki/index.md`:
   ```
   # Wiki Index
   | File | Type | Summary |
   |------|------|---------|
   ```
   A row must be added every time a wiki file is created or removed.

5. Create `wiki/log.md`:
   ```
   # Operation Log
   ## YYYY-MM-DD — <operation: ingest | query | lint | init> — <summary>
   - <detail>
   ```
   Log today's initialization as the first entry.

6. Create `AGENT.md` in the root with the following content:

   **Rules:**
   - NEVER write to `raw/`
   - ALWAYS update `wiki/index.md` when adding or removing a wiki file
   - ALWAYS append to `wiki/log.md` after every operation
   - Use `[[wikilinks]]` to cross-reference entries in `wiki/`
   - Wiki files live in `concepts/`, `entities/`, or `sources/` — never in `wiki/` root
   - Wiki entries are only created AFTER code is committed — never during proposal or planning

   **Core operations** (read the skill file before invoking):

   | Operation | When to invoke | Skill file |
   |-----------|---------------|------------|
   | `ingest` | A new file appears in `raw/` | `skills/ingest.md` |
   | `query` | User asks a question that requires synthesizing wiki knowledge | `skills/query.md` |
   | `lint` | Periodically or when wiki feels stale | `skills/lint.md` |
   | `propose` | Any new feature or change is requested | `skills/propose.md` |
   | `impact-check` | Before modifying any shared symbol | `skills/impact-check.md` |
   | `safe-change` | Editing code called from more than one place | `skills/safe-change.md` |
   | `verify-before-commit` | Before every commit | `skills/verify-before-commit.md` |

   **Invocation rules:**
   - New file in `raw/` → invoke `ingest` immediately
   - New feature request → invoke `propose` first, stop, wait for approval
   - Edit to shared code → invoke `impact-check` then `safe-change`
   - Before every commit → invoke `verify-before-commit`

7. Scan the project root for any stray `.md` files that are NOT `AGENT.md`, `README.md`, or numbered step files (`01-*.md`, `02-*.md`, etc.).
   - For each found: classify as concept, entity, or source; move to correct `wiki/` subfolder; add row to `wiki/index.md`; log the move in `wiki/log.md`.
   - If none found: skip silently.

# ACTION
For each folder and file listed above:
- IF it does not exist: create it exactly as specified.
- IF it already exists: verify it contains the required sections and format. If anything is missing or malformed, fix only the missing parts — do not overwrite valid content.

Reply with a checklist: each item marked ✅ (already valid), 🔧 (created or fixed), or ❌ (could not create — explain why).
