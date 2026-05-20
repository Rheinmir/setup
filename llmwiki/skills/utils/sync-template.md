Skill: sync-template
Purpose
Synchronize structural and template improvements between the current project and the Orca template repository https://github.com/Rheinmir/setup.git.

When to use
Upstream: After improving a template file localy and wanting to save it to Orca.
Downstream: When the Orca repo has newer features or fixes that you want to bring into the current project.
Steps
Load Manifest: Read .template-manifest.json for the inclusion list.
Clone Orca Repo:
Get the target repository URL from .template-manifest.json.
Clone the target repository to a temporary directory.
Delete .opencode/ from the cloned copy to avoid conflicts (Remove-Item -Recurse -Force "$tmpDir\.opencode").
Compare Manifest Files with Orca:
Run diff between local template files and Orca files listed in the manifest.
Scan for New Files:
Extract all unique directories from the manifest includes list (e.g., skills/, wiki/concepts/).
Local scan: List all files in those directories, excluding excludes patterns.
Orca scan: Same scan on the cloned copy.
Cross-reference both lists against the manifest:
[NEW] — File exists locally but not on Orca, and not in manifest. Candidate for upstream + manifest update.
[MISSING] — File exists on Orca but not locally. Candidate for downstream.
Stage 1: Presentation (Sync Plan):
Present a table showing the differences:
[UPSTREAM] -> File is newer in Local, can be pushed to Orca.
[DOWNSTREAM] -> File is newer in Orca, can be pulled to Local.
[CONFLICT] -> Both have changed (manual review required).
[NEW] -> File only exists locally, candidate for upstream + manifest registration.
[MISSING] -> File only exists on Orca, candidate for downstream.
STOP. Ask the user which direction to sync (e.g., "Pull all", "Push all", or specific files).
Stage 2: Execution:
Copy each file in the requested direction one by one (not bulk cp -R).
Downstream (Orca → Local): Before copying any file, always run mkdir -p on the target directory — the local project may not yet have the folder structure from Orca.
For [NEW] files: Add the file path to .template-manifest.json includes before copying upstream.
For [MISSING] files: Add the file path to .template-manifest.json includes after copying downstream.
If Upstreaming: Commit and push to Orca.
If Downstreaming: Update local files and log the update in wiki/log.md.
Cleanup temporary directory.
Rules
NEVER sync sensitive data (.env, credentials).
NEVER sync business-specific documentation.
ALWAYS show the diff for any file marked as [CONFLICT] and wait for user instruction on which version to keep.
NEVER use bulk recursive copy (e.g., cp -R folder/*). Copy file by file based on the inclusion list.
Use impact-check if the template change affects shared logic in skills/.
[NEW] files MUST be added to .template-manifest.json includes before upstream commit so the manifest stays in sync.
[MISSING] files MUST be added to .template-manifest.json includes after downstream copy so the manifest stays in sync.
