# CONTEXT
The architecture is set and the wiki is ready. It's time to scaffold the MVP.

# INSTRUCTIONS
1. Read `AGENT-business.md` and `AGENT-code.md` to understand the project deeply.
2. Generate the foundational folder structure for the chosen framework (e.g., MVC structure, React components folder, API routes, etc.).
3. Write a `health` check endpoint or a basic landing page to verify the app runs.
4. Create a `README.md` containing commands on how to run the project locally.
5. Create `llmwiki/wiki/concepts/architecture.md` in the overstack OKF format — **YAML frontmatter (rule R9), not the old `**Type:**` bold**:
   ```
   ---
   type: concept
   title: Architecture
   tags: [architecture, scaffold]
   timestamp: <today>
   ---

   # Architecture

   <1-3 sentence description of the scaffolded structure and why it was chosen.>

   ## Notes
   - [[link to related entities if any]]

   ## Origin
   - **Source:** `AGENT-code.md`
   - **Commit:** <hash of the scaffold commit>
   - **Date:** <today>
   ```
    Add a row for this file in `llmwiki/wiki/index.md` (rule R3).
6. Add an entry to `llmwiki/wiki/log.md` detailing the components scaffolded today.

# ACTION
Scaffold the codebase, update the wiki, and present a summary of what was built. Ask the user what feature they want to build first.
