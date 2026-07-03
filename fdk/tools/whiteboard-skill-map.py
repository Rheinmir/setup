#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""whiteboard-skill-map — BẢN ĐỒ QUAN HỆ SKILL dạng ĐỒ THỊ (giống wiki-graph).

Quyết định council 012: tái dùng CHÍNH engine build-wiki-graph.py để render → node + cạnh
tương tác y hệt wiki-graph, KHÔNG dựng layout riêng. Dữ liệu cha-con LIVE từ LOOP_GROUPS +
LOOP_MAP; mỗi loop = một HUB, mỗi skill = một node, cạnh loop→skill (rel 'contains').
Cỡ/vị trí do force-layout của engine tự dàn (hub bậc cao tự về giữa) — không bịa usage.

CLI:
  whiteboard-skill-map.py            # ghi llmwiki/html/skill-whiteboard.html (JS tương tác)
  whiteboard-skill-map.py --static   # bản HTML thuần 0-JS (bake toạ độ)
  whiteboard-skill-map.py --check    # exit 2 nếu cũ so bản sinh
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "llmwiki" / "html" / "skill-whiteboard.html"


def _load(modpath, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / modpath)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


WG = _load("fdk/tools/build-wiki-graph.py", "wg")          # engine đồ thị (tái dùng)
BO = _load("fdk/tools/build-overstack-docs.py", "bo")      # LOOP_GROUPS
SS = _load("harness/scripts/sync-skills.py", "ss")         # LOOP_MAP
LOOP_GROUPS = getattr(BO, "LOOP_GROUPS", {})
LOOP_MAP = getattr(SS, "LOOP_MAP", getattr(SS, "SKILL_LOOP", {}))

# rel mới cho quan hệ skill (nhét vào legend/màu của engine, chỉ in-memory — không sửa source)
WG.REL_COLORS["contains"] = "#5856d6"      # loop → skill
WG.REL_COLORS["orchestrates"] = "#ff9500"  # skill bao trùm → skill con
WG.REL_VI["contains"] = "loop chứa skill"
WG.REL_VI["orchestrates"] = "skill bao trùm điều phối skill con"

LOOP_TITLE = {"wiki-loop": "📚 wiki-loop", "dev-loop": "🛠️ dev-loop",
              "orchestrate": "🐳 orchestrate", "utils": "🔧 utils"}
# skill bao trùm → skill con thật (từ SKILL.md steps — quan hệ điều phối)
ORCHESTRATES = {
    "orca-workflow": ["propose", "impact-check", "safe-change", "verify-before-commit"],
    "orca-issue": ["impact-check", "safe-change", "verify-before-commit"],
    "fdk": ["new-skill", "sync-template", "health-check", "medic"],
}


def all_skills():
    grouped = {s for _, (_, smap) in LOOP_GROUPS.items() for s in smap}
    out = dict(LOOP_MAP)                    # skill → loop
    for loop, (_, smap) in LOOP_GROUPS.items():
        for s in smap:
            out[s] = loop
    return out


def desc_of(skill):
    for p in (ROOT / "skills" / skill / "SKILL.md", ROOT / "llmwiki" / "skills" / "utils" / f"{skill}.md"):
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"(?ms)^description:\s*>-?\s*\n((?:[ \t]+.+\n)+)", t)
        s = " ".join(l.strip() for l in m.group(1).splitlines()) if m else ""
        if not s:
            m = re.search(r'^description:\s*["\']?(.+)', t)
            s = m.group(1).strip().strip("\"'") if m else ""
        return re.split(r"Trigger", s)[0][:140].rstrip(" .,-")
    return ""


def build():
    skills = all_skills()
    loops = ["wiki-loop", "dev-loop", "orchestrate", "utils"]
    nodes, edges = [], []
    for loop in loops:
        nodes.append({"id": loop, "path": loop, "group": "hub", "type": "loop",
                      "title": loop, "wiki": "skill", "label": LOOP_TITLE.get(loop, loop)})
    for skill, loop in sorted(skills.items()):
        nodes.append({"id": skill, "path": f"skills/{skill}/SKILL.md", "group": loop or "?",
                      "type": "skill", "title": desc_of(skill), "wiki": "skill", "label": skill})
        if loop:
            edges.append({"from": loop, "rel": "contains", "to": skill, "kind": "to"})
    for hub, members in ORCHESTRATES.items():
        for m in members:
            if m in skills:
                edges.append({"from": hub, "rel": "orchestrates", "to": m, "kind": "to"})
    return nodes, edges


def render(static=False):
    nodes, edges = build()
    fn = WG.build_static if static else WG.build_html
    return fn("skill", str(OUT), nodes, edges, [], {})


def main():
    static = "--static" in sys.argv
    html = render(static)
    if "--check" in sys.argv:
        cur = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if cur.strip() != html.strip():
            print("[skill-whiteboard] CŨ so đĩa → chạy lại", file=sys.stderr)
            return 2
        print("skill-whiteboard.html khớp đĩa ✓")
        return 0
    OUT.write_text(html, encoding="utf-8")
    print(f"✓ wrote {OUT.relative_to(ROOT)} ({len(html)} bytes) — đồ thị {'tĩnh' if static else 'JS'} qua build-wiki-graph engine")
    return 0


if __name__ == "__main__":
    sys.exit(main())
