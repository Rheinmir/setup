#!/usr/bin/env python3
"""agent_claude_parity — llmwiki/AGENT.md ↔ llmwiki/CLAUDE.md ## Skills tables must agree.

Closes a real gap: sync-skills.py enforces skills/ ↔ llmwiki/skills/ parity, but NOTHING
enforced that the two human-facing skill tables list the same skills. They had drifted
(AGENT.md = 14 rows, CLAUDE.md = 9 rows). This validator fails (exit 2) with a per-side
diff whenever the two ## Skills tables differ.

Contract: `agent_claude_parity.py [files...]`  — argv files (pre-commit) are IGNORED;
          both tables are ALWAYS checked. Exit 0 = identical, exit 2 = drift (diff on stderr).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL_ROW_RE = re.compile(r"^\|\s*`([a-z0-9-]+)`\s*\|")
SKILLS_HEADING_RE = re.compile(r"^##\s+Skills\s*$")


def table_skills(md_path: Path) -> set:
    """Skill names from the `## Skills` markdown table (rows `| `name` | ... |`)."""
    if not md_path.is_file():
        return set()
    out, in_section = set(), False
    for ln in md_path.read_text(encoding="utf-8").splitlines():
        if SKILLS_HEADING_RE.match(ln):
            in_section = True
            continue
        if in_section and ln.startswith("## "):   # next level-2 heading ends the section
            break
        if in_section:
            m = SKILL_ROW_RE.match(ln)
            if m:
                out.add(m.group(1))
    return out


def main() -> None:
    agent = table_skills(REPO / "llmwiki" / "AGENT.md")
    claude = table_skills(REPO / "llmwiki" / "CLAUDE.md")

    only_agent = sorted(agent - claude)
    only_claude = sorted(claude - agent)

    if only_agent or only_claude:
        lines = [f"[agent-claude-parity] LECH — AGENT.md ({len(agent)}) vs CLAUDE.md ({len(claude)}) "
                 "## Skills tables khong khop:"]
        if only_agent:
            lines.append("  only in AGENT.md: " + ", ".join(only_agent))
        if only_claude:
            lines.append("  only in CLAUDE.md: " + ", ".join(only_claude))
        lines.append("  → Dong bo hai bang ## Skills cho khop roi commit lai.")
        print("\n".join(lines), file=sys.stderr)
        sys.exit(2)

    print(f"[agent-claude-parity] ✓ AGENT.md & CLAUDE.md ## Skills tables match ({len(agent)} skills).")
    sys.exit(0)


if __name__ == "__main__":
    main()
