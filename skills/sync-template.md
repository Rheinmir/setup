# Skill: sync-template

## Purpose
Synchronize structural and template improvements made in the current project back to the master template repository (https://github.com/Rheinmir/setup.git).

## When to use
- After creating or improving a reusable skill, command, or template.
- When you want to "upstream" a new feature (like the HTML visualization layer) to the base setup.

## Steps
1. **Load Manifest**: Read `.template-manifest.json` to identify the "Source of Truth" for template files. **DO NOT** sync any file not listed in the `includes` section or explicitly blocked by `excludes`.
2. **Identify Template Files**: Based on the manifest, scan the current project for matching files.
3. **Stage 1: Presentation (Preview)**:
   - Present a table to the user listing all files identified for sync.
   - Categorize them as: `[NEW]`, `[MODIFIED]`, or `[DELETED]`.
   - **STOP**. Ask the user to review the list.
4. **Stage 2: Execution (Push)**:
   - ONLY after the user provides explicit approval (e.g., "Push", "Approve", "Proceed"), continue to the next steps.
5. **Setup Workspace**:
   - Clone `https://github.com/Rheinmir/setup.git` to a temporary directory.
6. **Sync & Commit**:
   - Copy files, run `git add`, and `git commit`.
7. **Final Push**:
   - `git push origin main` and cleanup.

## Rules
- NEVER sync sensitive data (`.env`, credentials).
- NEVER sync business-specific documentation.
- Always use `diff` or `impact-check` before overwriting in the master repo.
