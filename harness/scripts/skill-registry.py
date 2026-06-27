#!/usr/bin/env python3
"""skill-registry — one truth set for skill identity, cross-checked across surfaces.

`skills/*/SKILL.md` is canonical. Skill identity ALSO appears on four OTHER surfaces
that drift independently and are NOT covered by `sync-skills.py --check` (that one only
guards the skills/ ↔ llmwiki/skills/ mirror):

  • .claude-plugin/marketplace.json      — publish set (refs skills by ./skills/<dir>)
  • llmwiki/AGENT.md   ## Skills table   — human-facing skill table
  • llmwiki/CLAUDE.md  ## Skills table   — human-facing skill table
  • harness/scripts/sync-skills.py LOOP_MAP — loop assignment (imported, single source)

Usage:
  python3 harness/scripts/skill-registry.py            # human report table (default)
  python3 harness/scripts/skill-registry.py --emit     # write harness/skill-registry.json
  python3 harness/scripts/skill-registry.py --check    # exit 2 on any cross-surface drift

Matching rules (faithful to how each surface refers to a skill):
  • loop / in_marketplace  → matched by DIRECTORY name (LOOP_MAP keys & marketplace paths
                              both use the folder name).
  • in_agent_table / in_claude_table → matched by frontmatter `name` (the table column is
                              the skill's declared display identity).
"""
import importlib.util
import json
import re
import sys
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT_JSON = REPO / "harness" / "skill-registry.json"

# Skills intentionally NOT published to marketplace.json (explicit allowlist).
# fdk = self-contained framework-dev kit (ADR-004: not for normal project dev), never shipped.
UNPUBLISHED = {"fdk"}

SKILL_ROW_RE = re.compile(r"^\|\s*`([a-z0-9-]+)`\s*\|")
SKILLS_HEADING_RE = re.compile(r"^##\s+Skills\s*$")


# ── LOOP_MAP: import the real dict from sync-skills.py (single source of truth) ──────────
def load_loop_map():
    p = REPO / "harness" / "scripts" / "sync-skills.py"
    try:
        spec = importlib.util.spec_from_file_location("sync_skills_loopmap", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)          # top-level only defines data + funcs (main() guarded)
        return dict(mod.LOOP_MAP)
    except Exception:                          # resilient fallback: parse the literal block
        txt = p.read_text(encoding="utf-8")
        m = re.search(r"LOOP_MAP\s*=\s*\{(.*?)\n\}", txt, re.S)
        out = {}
        if m:
            for k, v in re.findall(r'"([a-z0-9-]+)"\s*:\s*"([a-z0-9-]+)"', m.group(1)):
                out[k] = v
        return out


# ── minimal YAML frontmatter parser (name + description; no PyYAML dependency) ───────────
def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return {}
    body, data, i = lines[1:end], {}, 0
    while i < len(body):
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", body[i])
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2)
        if val in (">", ">-", ">+", "|", "|-", "|+", ""):     # block scalar (folded/literal/empty)
            block, j = [], i + 1
            while j < len(body):
                bl = body[j]
                if bl.strip() == "":
                    block.append("")
                elif len(bl) - len(bl.lstrip()) == 0:          # back to column 0 → block ends
                    break
                else:
                    block.append(bl.strip())
                j += 1
            if val.startswith("|"):                            # literal: keep line breaks
                data[key] = "\n".join(block).strip()
            else:                                              # folded / empty: join with spaces
                data[key] = " ".join(x for x in block if x).strip()
            i = j
        else:
            data[key] = val.strip().strip('"').strip("'")
            i += 1
    return data


# ── surface readers ─────────────────────────────────────────────────────────────────────
def marketplace_dirs():
    data = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    out = set()
    for plug in data.get("plugins", []):
        for s in plug.get("skills", []):
            out.add(Path(s).name)              # basename of ./skills/<dir>
    return out


def table_skills(md_path):
    out, in_section = set(), False
    for ln in md_path.read_text(encoding="utf-8").splitlines():
        if SKILLS_HEADING_RE.match(ln):
            in_section = True
            continue
        if in_section and ln.startswith("## "):
            break
        if in_section:
            m = SKILL_ROW_RE.match(ln)
            if m:
                out.add(m.group(1))
    return out


# ── build the truth set ─────────────────────────────────────────────────────────────────
def build():
    loop_map = load_loop_map()
    mkt = marketplace_dirs()
    agent = table_skills(REPO / "llmwiki" / "AGENT.md")
    claude = table_skills(REPO / "llmwiki" / "CLAUDE.md")
    entries = []
    for d in sorted((REPO / "skills").iterdir()):
        src = d / "SKILL.md"
        if not (d.is_dir() and src.is_file()):
            continue
        fm = parse_frontmatter(src.read_text(encoding="utf-8"))
        name = fm.get("name", d.name)
        entries.append({
            "name": name,
            "loop": loop_map.get(d.name, "?"),
            "description": fm.get("description", ""),
            "path": f"skills/{d.name}/SKILL.md",
            "in_marketplace": d.name in mkt,
            "in_agent_table": name in agent,
            "in_claude_table": name in claude,
        })
    entries.sort(key=lambda e: (e["name"], e["path"]))
    return entries, mkt, agent, claude


def _wrap(names, indent="    "):
    return textwrap.fill(", ".join(names) or "(none)", width=100,
                         initial_indent=indent, subsequent_indent=indent)


# ── modes ───────────────────────────────────────────────────────────────────────────────
def emit():
    entries, *_ = build()
    OUT_JSON.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[skill-registry] wrote {OUT_JSON.relative_to(REPO)} — {len(entries)} skills.")


def report():
    entries, mkt, agent, claude = build()
    yn = lambda b: "✓" if b else "·"
    print(f"SKILL REGISTRY — {len(entries)} skills (truth: skills/*/SKILL.md)\n")
    print(f"  {'NAME':<28} {'LOOP':<11} MKT AGT CLD")
    print(f"  {'-'*28} {'-'*11} --- --- ---")
    for e in entries:
        print(f"  {e['name']:<28} {e['loop']:<11}  {yn(e['in_marketplace'])}   "
              f"{yn(e['in_agent_table'])}   {yn(e['in_claude_table'])}")
    print(f"\n  legend: MKT=marketplace.json · AGT=AGENT.md table · CLD=CLAUDE.md table  (✓ present · · absent)")
    print(f"  totals: marketplace {sum(e['in_marketplace'] for e in entries)}"
          f" · AGENT {sum(e['in_agent_table'] for e in entries)}"
          f" · CLAUDE {sum(e['in_claude_table'] for e in entries)}"
          f" · unmapped-loop {sum(e['loop']=='?' for e in entries)}")


def check():
    entries, mkt, agent, claude = build()
    dirs = {Path(e["path"]).parent.name for e in entries}
    names = {e["name"] for e in entries}

    miss_mkt = sorted(d for d in dirs if d not in mkt and d not in UNPUBLISHED)
    miss_agent = sorted(names - agent)
    miss_claude = sorted(names - claude)
    unmapped = sorted({e["name"] for e in entries if e["loop"] == "?"})
    dangling_agent = sorted(agent - names)      # table row with no such skill
    dangling_claude = sorted(claude - names)

    print(f"[skill-registry] cross-surface drift check")
    print(f"  truth: {len(entries)} skill dirs · {len(names)} unique names\n")
    print(f"  SURFACE COVERAGE")
    print(f"    marketplace.json : {len(mkt & dirs):>2} listed · {len(miss_mkt)} not published"
          f" (+{len(dirs & UNPUBLISHED)} allowlisted: {', '.join(sorted(dirs & UNPUBLISHED)) or '—'})")
    print(f"    AGENT.md  table  : {len(agent):>2} listed · {len(miss_agent)} skills not in table")
    print(f"    CLAUDE.md table  : {len(claude):>2} listed · {len(miss_claude)} skills not in table")
    print(f"    LOOP_MAP         : {len(entries)-len(unmapped):>2} mapped · {len(unmapped)} unmapped\n")

    drift = False
    if miss_mkt:
        drift = True
        print(f"  DRIFT — missing from marketplace.json ({len(miss_mkt)}):")
        print(_wrap(miss_mkt))
    if miss_agent:
        drift = True
        print(f"  DRIFT — missing from AGENT.md ## Skills ({len(miss_agent)}):")
        print(_wrap(miss_agent))
    if miss_claude:
        drift = True
        print(f"  DRIFT — missing from CLAUDE.md ## Skills ({len(miss_claude)}):")
        print(_wrap(miss_claude))
    if unmapped:
        drift = True
        print(f"  DRIFT — unmapped in sync-skills LOOP_MAP ({len(unmapped)}):")
        print(_wrap(unmapped))
    if dangling_agent:
        drift = True
        print(f"  DRIFT — AGENT.md table row with no such skill ({len(dangling_agent)}):")
        print(_wrap(dangling_agent))
    if dangling_claude:
        drift = True
        print(f"  DRIFT — CLAUDE.md table row with no such skill ({len(dangling_claude)}):")
        print(_wrap(dangling_claude))

    if drift:
        print(f"\n[skill-registry] FAIL (exit 2): cross-surface drift detected.", file=sys.stderr)
        sys.exit(2)
    print(f"\n[skill-registry] ✓ all surfaces agree.")


def main():
    args = sys.argv[1:]
    if "--emit" in args:
        emit()
    elif "--check" in args:
        check()
    else:
        report()


if __name__ == "__main__":
    main()
