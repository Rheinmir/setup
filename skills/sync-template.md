# Skill: sync-template

## Purpose
Synchronize structural and template improvements between the current project and the master template repository defined in `.template-manifest.json`.

## When to use
- **Upstream**: After improving a template file localy and wanting to save it to Master.
- **Downstream**: When the Master repo has newer features or fixes that you want to bring into the current project.

## Steps
1. **Load Manifest**: Read `.template-manifest.json` for the inclusion list.
2. **Compare with Master**:
   - Get the target repository URL from `.template-manifest.json`.
   - Clone the target repository to a temporary directory.
   - Run `diff` between local template files and Master files.
3. **Stage 1: Presentation (Sync Plan)**:
   - Present a table showing the differences:
     - `[UPSTREAM]` -> File is newer in Local, can be pushed to Master.
     - `[DOWNSTREAM]` -> File is newer in Master, can be pulled to Local.
     - `[CONFLICT]` -> Both have changed (manual review required).
   - **STOP**. Ask the user which direction to sync (e.g., "Pull all", "Push all", or specific files).
4. **Stage 2: Execution**:
   - Perform the file copy in the requested direction.
   - If Upstreaming: Commit and Push to Master.
   - If Downstreaming: Update local files and log the update in `wiki/log.md`.
   - Cleanup temporary directory.

## Rules
- NEVER sync sensitive data (`.env`, credentials).
- NEVER sync business-specific documentation.
- ALWAYS show the `diff` for any file marked as `[CONFLICT]` and wait for user instruction on which version to keep.
- Use `impact-check` if the template change affects shared logic in `skills/`.
