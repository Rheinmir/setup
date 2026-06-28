---
name: new-skill
description: Scaffold a new skill into both publish trees at once — skills/<name>/SKILL.md plus its byte-identical llmwiki mirror — via fdk/tools/new-skill.py, then print the exact commands to register it on the curated surfaces (LOOP_MAP, marketplace.json, AGENT.md/CLAUDE.md). Use when the user says "create a skill", "add a new skill", "scaffold a skill", "make a new skill", "new skill", or invokes /new-skill.
---

# Skill: new-skill

Adding a skill touches four places — the canonical `skills/<name>/SKILL.md`, its `llmwiki/skills/<loop>/<name>.md` mirror, the `sync-skills.py` LOOP_MAP, the `marketplace.json` publish list, and a row in the AGENT.md/CLAUDE.md `## Skills` table. Miss one and the trees drift (that is how `marketplace.json` fell ~30 skills behind). This skill drives `fdk/tools/new-skill.py`, which writes the two mechanical files identically and prints the exact lines for the three curated places — it never edits them itself.

## When to use
- The user asks to create / add / scaffold a new skill, or invokes `/new-skill`.
- You are about to hand-create a `skills/<name>/SKILL.md` and would otherwise forget the mirror or the registry surfaces.

## Steps
1. Settle three inputs: a kebab-case `<name>`, a `--loop` (`dev-loop` | `orchestrate` | `wiki-loop` | `utils`), and a `--desc` that is **rich with trigger phrases** (the description is what the skill router matches on).
2. Preview first, then create:
   ```bash
   python3 fdk/tools/new-skill.py <name> --loop <loop> --desc "<description>" --dry-run   # preview body + next steps
   python3 fdk/tools/new-skill.py <name> --loop <loop> --desc "<description>"             # write both files
   ```
   It refuses if `skills/<name>/` already exists.
3. Fill in the generated `skills/<name>/SKILL.md` — replace the TODO `When to use` / `Steps` / `Rules` placeholders with real, verifiable content.
4. Re-mirror after editing so the llmwiki copy stays byte-identical:
   ```bash
   python3 harness/scripts/sync-skills.py
   ```
5. Register on the curated surfaces by pasting the exact lines the tool printed: add the LOOP_MAP entry in `harness/scripts/sync-skills.py`, (optionally) the `./skills/<name>` line in `.claude-plugin/marketplace.json`, and one row in BOTH `llmwiki/AGENT.md` and `llmwiki/CLAUDE.md` `## Skills` tables.
6. Verify every surface agrees — both must pass:
   ```bash
   python3 harness/scripts/sync-skills.py --check        # mirror parity
   python3 harness/scripts/skill-registry.py --check      # cross-surface drift
   ```

## Rules
- The tool writes ONLY the two mechanical files (canonical + mirror). It never edits LOOP_MAP, marketplace.json, AGENT.md, or CLAUDE.md — those are user-curated; you add the printed lines by hand.
- After editing the generated skeleton, ALWAYS re-run `sync-skills.py` — parity is enforced, and your edits will have made the mirror stale.
- A vague `--desc` is a skill that never fires. Put concrete trigger phrases and `/`-commands in it.
- Never overwrite an existing skill — if the name is taken, edit `skills/<name>/SKILL.md` in place or pick another name.
