# CONTEXT
We have defined the project goals and tech stack. Now, we must establish the Agentic Knowledge Base so all future AI Agents can share context.

# INSTRUCTIONS
You must execute the following file system operations:
1. Create a `.agent/` folder in the root directory. Inside it, create `commands/` and `skills/` folders.
2. Create a `wiki/` folder with `concepts/`, `entities/`, and `sources/` subdirectories.
3. Create `wiki/index.md` with an empty catalog.
4. Create `AGENT.md` in the root folder. This file must contain the following strict rules:
   - "NEVER write to raw/"
   - "ALWAYS update wiki/index.md and wiki/log.md after every operation"
   - "Use [[wikilinks]] for documentation"
5. Update `wiki/log.md` with today's date logging the initialization of the Knowledge Base.

# ACTION
Create the directories and files exactly as specified. Reply ONLY with "Knowledge Base Structure Initialized." when finished.
