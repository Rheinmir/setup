#!/usr/bin/env python3
"""new-skill — scaffold a skill in BOTH publish trees at once, then print the
registration commands (NEVER auto-edits the curated registry surfaces).

WHY: adding a skill is a 4-place chore — create `skills/<name>/SKILL.md`, map it
in `sync-skills.py` LOOP_MAP, list it in `.claude-plugin/marketplace.json`, and add
a row to the AGENT.md/CLAUDE.md `## Skills` table. Forget one → drift (that is how
marketplace.json fell 30 skills behind). This tool removes the two MECHANICAL,
always-identical places — the canonical `skills/<name>/SKILL.md` and its byte-for-byte
mirror `llmwiki/skills/<loop>/<name>.md` (sync-skills.py enforces that parity) — and
hands you the exact lines for the three CURATED places, which stay human-owned by policy.

Usage:
    python3 fdk/tools/new-skill.py <name> --loop <loop> --desc "<description>"
    python3 fdk/tools/new-skill.py <name> --loop <loop> --desc "..." --dry-run

    <name>   kebab-case (^[a-z0-9]+(-[a-z0-9]+)*$); refuses if skills/<name>/ exists
    --loop   one of: dev-loop | orchestrate | wiki-loop | utils
    --desc   one-line description WITH trigger phrases (this is what the router matches)
    --dry-run  print what WOULD be created (full file body + next steps); write nothing
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILLS = REPO / "skills"                  # canonical (npx publish set)
LLMWIKI = REPO / "llmwiki" / "skills"     # mirror (bundle llmwiki / sync-template)

# Loop folders that exist under llmwiki/skills/ — keep in sync with sync-skills.py groups.
KNOWN_LOOPS = ("dev-loop", "orchestrate", "wiki-loop", "utils")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# YAML 1.x plain-scalar indicators — if the description opens with one, it must be quoted.
_YAML_INDICATORS = set("!&*?|>@`\"'%#,[]{}:")


def yaml_scalar(s: str) -> str:
    """Emit `s` as a valid YAML scalar — plain when safe, double-quoted when not.

    The hazards for a plain scalar are a colon-space (`: ` reads as a mapping), a
    trailing colon, a space-hash (`' #'` starts a comment), a leading indicator
    character, or leading/trailing whitespace. Otherwise plain — matching the simple
    skills (safe-change, impact-check) — which keeps generated frontmatter readable.
    """
    if (": " in s or s.endswith(":") or " #" in s
            or (s and s[0] in _YAML_INDICATORS) or s != s.strip()):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def render(name: str, desc: str) -> str:
    """The SKILL.md body. Written ONCE, then byte-for-byte to both trees."""
    return f"""---
name: {name}
description: {yaml_scalar(desc)}
---

# Skill: {name}

## When to use
<!-- The `description` above is what the skill router matches on — keep concrete
     trigger phrases there. Below, spell out the situations that should invoke this skill. -->
- TODO: a user phrasing / situation that should trigger this skill
- TODO: another trigger

## Steps
1. TODO: first concrete, verifiable step.
2. TODO: next step.
3. TODO: confirm the result, then hand off to the next skill if any.

## Rules
- TODO: a hard constraint or anti-pattern this skill must respect.
- Touch only what the task requires — no opportunistic changes.
"""


def rel(p: Path) -> str:
    return str(p.relative_to(REPO))


def next_steps(name: str, loop: str) -> str:
    """The three CURATED surfaces this tool deliberately does NOT touch (policy:
    registry surfaces are user-curated). Exact copy-paste lines + a verify command."""
    return f"""
NEXT — register `{name}` on the curated surfaces (this tool does NOT edit them — policy: user-curated):

  1. LOOP_MAP — add this line inside the `{loop}` group of LOOP_MAP in
     harness/scripts/sync-skills.py  (so the mirror parity check knows its loop):

         "{name}": "{loop}",

  2. marketplace.json (optional — the publish set) — add to the right plugin's
     "skills" array in .claude-plugin/marketplace.json:

         "./skills/{name}",

  3. AGENT.md / CLAUDE.md ## Skills table — add ONE row to BOTH
     llmwiki/AGENT.md and llmwiki/CLAUDE.md:

         | `{name}` | <when to invoke> | `skills/{loop}/{name}.md` | {loop} |

  4. Verify every surface agrees:

         python3 harness/scripts/sync-skills.py --check        # mirror parity (skills/ <-> llmwiki/skills/)
         python3 harness/scripts/skill-registry.py --check      # cross-surface drift (marketplace + AGENT + CLAUDE + LOOP_MAP)
"""


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="new-skill.py",
        description="Scaffold skills/<name>/SKILL.md + its llmwiki mirror, then print registration steps.",
    )
    ap.add_argument("name", help="skill name, kebab-case (e.g. my-new-skill)")
    ap.add_argument("--loop", required=True, choices=KNOWN_LOOPS,
                    help="loop folder under llmwiki/skills/")
    ap.add_argument("--desc", required=True,
                    help="one-line description WITH trigger phrases (drives router matching)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be created (incl. full body); write nothing")
    args = ap.parse_args()

    name = args.name.strip()
    if not NAME_RE.match(name):
        sys.exit(f"✗ invalid name '{name}' — use kebab-case: ^[a-z0-9]+(-[a-z0-9]+)*$")

    skill_dir = SKILLS / name
    skill_md = skill_dir / "SKILL.md"
    mirror_md = LLMWIKI / args.loop / f"{name}.md"

    if skill_dir.exists():
        sys.exit(f"✗ skills/{name}/ already exists — refusing to overwrite. "
                 f"Edit {rel(skill_md)} directly, or pick another name.")

    body = render(name, args.desc)
    tag = "[dry-run] would create" if args.dry_run else "✓ created"

    if args.dry_run:
        print(f"[dry-run] no files written. Body that WOULD go to both paths:\n")
        print("─" * 72)
        print(body, end="")
        print("─" * 72)
    else:
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_md.write_text(body, encoding="utf-8")
        mirror_md.parent.mkdir(parents=True, exist_ok=True)
        mirror_md.write_text(body, encoding="utf-8")  # byte-identical: same string, both trees

    print(f"\n{tag}  {rel(skill_md)}")
    print(f"{tag}  {rel(mirror_md)}  (mirror — byte-identical, sync-skills enforces parity)")
    print(next_steps(name, args.loop))


if __name__ == "__main__":
    main()
