# Skill: sync-template

## Purpose
Synchronize structural and template improvements between the current project and the master template repository defined in `.template-manifest.json`.

## When to use
- **Upstream**: After improving a template file locally and wanting to save it to Master.
- **Downstream**: When the Master repo has newer features or fixes that you want to bring into the current project.
- **Cross-branch**: When another local branch of this project has new skills/files not yet on the current branch.

## Steps

1. **Load Manifest**: Read `.template-manifest.json` for the inclusion list and `remote` URL.

2. **Local branch scan (NEW — run before cloning remote)**:
   - Run `git branch -a` to list all local and remote branches of this repo.
   - For each other branch, run `git diff HEAD..<branch> -- llmwiki/skills/ llmwiki/orca/` to detect files that exist on that branch but not on the current branch.
   - Mark any discovered files as `[BRANCH-ONLY]` — they need to be cherry-picked or copied to the current branch AND upstreamed to Master.
   - **This is the most common source of drift**: skills added on a workspace/feature branch never propagated to main.

3. **Clone Master Repo**:
   - Get the target repository URL from `.template-manifest.json`.
   - Clone the target repository to a temporary directory.
   - **Branch Audit (CRITICAL)**: Always run `git branch -a` on the clone. Check if there is an active branch containing newer or more complete template improvements (e.g., `orca`, `orchestrate`, or active development branches). Do not blindly assume the default branch (`master`/`main`) is the only or most up-to-date one. Checkout target branch if needed.
   - **Delete `.opencode/` from the cloned copy** to avoid conflicts.

4. **Compare Manifest Files with Master**:
   - Run `diff` between local template files and Master files listed in the manifest.

5. **Scan for New Files**:
   - Extract all unique directories from the manifest `includes` list.
   - **Local scan**: List all files in those directories, excluding `excludes` patterns.
   - **Master scan**: Same scan on the cloned copy.
   - Cross-reference both lists against the manifest:
     - `[NEW]` — File exists locally but not on Master, not in manifest → upstream + manifest update.
     - `[MISSING]` — File exists on Master but not locally → downstream.
     - `[BRANCH-ONLY]` — File exists on another local branch but not current branch and not on Master → copy to current branch + upstream.

6. **Stage 1: Presentation (Sync Plan)**:
   - Present a table showing the differences:
     - `[UPSTREAM]` → File is newer locally, push to Master.
     - `[DOWNSTREAM]` → File is newer on Master, pull to local.
     - `[CONFLICT]` → Both have changed (manual review required).
     - `[NEW]` → Only exists locally, candidate for upstream + manifest registration.
     - `[MISSING]` → Only exists on Master, candidate for downstream.
     - `[BRANCH-ONLY]` → Only exists on another local branch, copy here + upstream.
   - **STOP**. Ask the user which direction to sync.

7. **Stage 2: Execution**:
   - Copy each file in the requested direction one by one (not bulk `cp -R`).
   - **Downstream (Master → Local)**: Always run `mkdir -p` on the target directory first.
   - **For `[NEW]` and `[BRANCH-ONLY]` files**: Add path to `.template-manifest.json` `includes` before copying upstream.
   - **For `[MISSING]` files**: Add path to `.template-manifest.json` `includes` after copying downstream.
   - If Upstreaming: Commit and push to Master.
   - If Downstreaming or cross-branch copy: Update local files and append to `wiki/log.md`.
   - Cleanup temporary directory.

## Rules
- NEVER sync sensitive data (`.env`, credentials).
- NEVER sync business-specific documentation.
- ALWAYS show the `diff` for any file marked as `[CONFLICT]` and wait for user instruction.
- NEVER use bulk recursive copy (e.g., `cp -R folder/*`). Copy file by file.
- Use `impact-check` if the template change affects shared logic in `skills/`.
- `[NEW]` and `[BRANCH-ONLY]` files MUST be added to `.template-manifest.json` `includes` before upstream commit.
- `[MISSING]` files MUST be added to `.template-manifest.json` `includes` after downstream copy.
- **Always run step 2 (local branch scan) before cloning remote** — cross-branch drift is silent and step 2 catches it before it accumulates.
