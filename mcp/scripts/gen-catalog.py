#!/usr/bin/env python3
"""gen-catalog.py — sinh `mcp/catalog.json`: toàn bộ skill, rule và tool của overstack ĐỌC TỪ ĐĨA, không chép tay.

MCP server (mcp/src) chỉ phục vụ những gì có trong catalog này: một skill là một prompt + một resource, một rule là một
mục của `rule_check`, một script là một tool chạy với argv cố định. Catalog sinh bằng code để không drift với đĩa —
`--check` so bản trên đĩa với bản sinh lại và rc 2 khi lệch (test của server và CI gọi nó).

Dùng (từ gốc repo overstack):
    python3 mcp/scripts/gen-catalog.py             # ghi mcp/catalog.json
    python3 mcp/scripts/gen-catalog.py --check     # rc 0 khớp · rc 2 lệch
    python3 mcp/scripts/gen-catalog.py --no-help   # bỏ bước probe --help (nhanh, chỉ để thử)

Nguồn:
    skills/*/SKILL.md, skills/external/*/SKILL.md   → skills[]  (frontmatter name/description/disable-model-invocation)
    harness/scripts/sync-skills.py LOOP_MAP          → group của skill (wiki-loop · dev-loop · orchestrate · utils)
    harness/policy.yaml rules[]                      → rules[]   (id, name, validator, statement, enforce_at, applies_to)
    harness/scripts/*.{py,sh} fdk/tools/*.{py,mjs,sh} harness/validators/*.py → tools[]
      mỗi tool chạy `--help` với stdin đóng, cwd tạm, timeout 10 s; help thô + option parse từ usage của argparse.
      Script không trả lời --help (hook đọc stdin, shim thiếu engine…) vẫn được liệt kê với help = null.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "mcp" / "catalog.json"
SCHEMA_VERSION = 1

TOOL_DIRS = (
    ("harness/scripts", "harness-script", (".py", ".sh")),
    ("fdk/tools", "fdk-tool", (".py", ".mjs", ".sh")),
    ("harness/validators", "validator", (".py",)),
)
# Module thư viện: import bởi script khác, không phải tool.
LIB_NAMES = {
    "overstack_paths.py", "wikidirs.py", "repo_role.py", "bnal_config.py", "bnal_guard.py", "bnal_metrics.py",
    "html_base.py", "html_font.py", "html_font_data.py", "html_shell.py", "html_shell_vendor.py", "code_imports.py",
    "showcase_components.py", "showcase_dataviz.py", "showcase_layout.py", "showcase_motion.py", "showcase_rules.py",
    "__init__.py",
}
RUNNERS = {".py": "python3", ".mjs": "node", ".sh": "bash"}
HELP_TIMEOUT_S = 10
HELP_MAX_CHARS = 12000

# Một dòng option của argparse: hai khoảng trắng, cờ (có thể kèm metavar), rồi help cách ≥ 2 khoảng trắng hoặc ở dòng sau.
OPT_LINE_RE = re.compile(r"^\s{2}(-{1,2}[\w][\w-]*(?:[ =][A-Z_\[\]{}|,.0-9a-z-]+)?(?:,\s+-{1,2}[\w][\w-]*(?:[ =][A-Z_\[\]{}|,.0-9a-z-]+)?)*)(?:\s{2,}(.*))?$")
FLAG_RE = re.compile(r"(-{1,2}[\w][\w-]*)(?:[ =]([A-Z_\[\]{}|,.0-9a-z-]+))?")


# ── frontmatter ──────────────────────────────────────────────────────────────
def frontmatter(text: str) -> dict:
    """YAML frontmatter tối giản: scalar một dòng, folded/literal (>- | |-) gom dòng thụt. Không cần pyyaml."""
    m = re.match(r"^---[ \t]*\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    out: dict = {}
    lines = m.group(1).splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        km = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", ln)
        if not km:
            i += 1
            continue
        key, val = km.group(1), km.group(2).strip()
        if val in (">", ">-", "|", "|-"):
            body = []
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i][:1] in (" ", "\t")):
                if lines[i].strip():
                    body.append(lines[i].strip())
                i += 1
            out[key] = " ".join(body) if val.startswith(">") else "\n".join(body)
            continue
        if val == "":
            # khối con (metadata:) — gom thành dict phẳng một cấp
            sub: dict = {}
            i += 1
            while i < len(lines) and lines[i][:1] in (" ", "\t") and lines[i].strip():
                sm = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
                if sm:
                    sub[sm.group(1)] = sm.group(2).strip().strip('"').strip("'")
                i += 1
            out[key] = sub
            continue
        out[key] = val.strip('"').strip("'")
        i += 1
    return out


def load_loops() -> dict:
    """LOOP_MAP của sync-skills.py — nguồn duy nhất cho nhóm skill (như build-capabilities.py)."""
    try:
        t = (ROOT / "harness" / "scripts" / "sync-skills.py").read_text(encoding="utf-8")
        m = re.search(r"LOOP_MAP\s*=\s*\{(.*?)\}", t, re.S)
        return dict(re.findall(r'"([a-z0-9-]+)"\s*:\s*"([a-z-]+)"', m.group(1))) if m else {}
    except OSError:
        return {}


def skills_root() -> Path:
    """Skill tách sang repo Rheinmir/skills (141026): OVERSTACK_SKILLS_ROOT (Docker: /opt/skills/skills) > <repo>/skills (bản cũ)
    > ~/orca/skills/skills (checkout dev) > ~/.claude/skills (bản cài global)."""
    env = os.environ.get("OVERSTACK_SKILLS_ROOT")
    if env:
        return Path(env).expanduser()
    for c in (ROOT / "skills", Path.home() / "orca" / "skills" / "skills", Path.home() / ".claude" / "skills"):
        if any(c.glob("*/SKILL.md")):
            return c
    return ROOT / "skills"


def skills_version() -> dict:
    """version.json của repo skills (cạnh thư mục skills/) — để /healthz công bố bản skill đang phục vụ."""
    for c in (skills_root().parent / "version.json", Path.home() / ".claude" / "harness" / "skills-version.json"):
        try:
            d = json.loads(c.read_text(encoding="utf-8"))
            return {"version": d.get("version"), "catalog_sha": d.get("catalog_sha"), "count": d.get("count")}
        except (OSError, ValueError):
            continue
    return {"version": None, "catalog_sha": None, "count": None}


def collect_skills() -> list:
    loops = load_loops()
    skills = []
    sroot = skills_root()
    for sk in sorted([*sroot.glob("*/SKILL.md"), *sroot.glob("external/*/SKILL.md")]):
        fm = frontmatter(sk.read_text(encoding="utf-8", errors="replace"))
        name = fm.get("name") or sk.parent.name
        dmi = str(fm.get("disable-model-invocation", "false")).lower() == "true"
        meta = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
        fm_loop = re.search(r"^\s{2}loop:\s*([\w-]+)\s*$", sk.read_text(encoding="utf-8", errors="replace")[:4000], re.M)
        skills.append({
            "name": name,
            "dir": sk.parent.name,
            "path": sk.relative_to(sroot).as_posix(),   # tương đối skills root — ảnh Docker (/opt/skills/skills) và máy dev dùng chung catalog
            "external": sk.parent.parent.name == "external",
            "group": loops.get(name) or (fm_loop.group(1) if fm_loop else "utils"),
            "description": fm.get("description", ""),
            "modelInvocable": not dmi,
            "bytes": sk.stat().st_size,
        })
    return skills


# ── rules ────────────────────────────────────────────────────────────────────
def collect_rules() -> list:
    """policy.yaml là YAML đơn giản (list of maps, scalar + list inline). Parse bằng regex theo khối `- id:`."""
    text = (ROOT / "harness" / "policy.yaml").read_text(encoding="utf-8")
    blocks = re.split(r"\n(?=  - id: )", text)
    rules = []
    for blk in blocks:
        m = re.match(r"\s*- id:\s*(\S+)", blk)
        if not m:
            continue
        def field(k):
            fm = re.search(rf"^\s+{k}:\s*(.*)$", blk, re.M)
            return fm.group(1).split("#", 1)[0].strip() if fm else None
        def listf(k):
            v = field(k)
            if not v or not v.startswith("["):
                return []
            return [x.strip().strip('"') for x in v.strip("[]").split(",") if x.strip()]
        validator = field("validator")
        if validator in (None, "null", "~"):
            validator = None
        # policy.yaml ghi tên file (`okf_frontmatter.py`) hoặc đường dẫn (`harness/validators/decision_adr.py`); hook phiên
        # (`stop.py`, `session_end.py`) không nằm trong validators/ → validatorPath None, rule chỉ để đọc.
        vpath = None
        if validator:
            cand = ROOT / validator if "/" in validator else ROOT / "harness" / "validators" / validator
            vpath = cand.relative_to(ROOT).as_posix() if cand.is_file() else None
        statement = field("statement") or ""
        rules.append({
            "id": m.group(1),
            "name": field("name"),
            "validator": validator,
            "validatorPath": vpath,
            "statement": statement.strip('"'),
            "enforce_at": listf("enforce_at"),
            "applies_to": listf("applies_to"),
            "scope": (field("scope") or "").strip('"') or None,
        })
    return rules


# ── tools ────────────────────────────────────────────────────────────────────
def parse_help(text: str) -> dict:
    """Rút usage, mô tả, option và positional từ output argparse. Script không dùng argparse → chỉ có help thô."""
    usage_m = re.search(r"^usage:\s*(.*?)(?=\n\n|\n\S|\Z)", text, re.S | re.M)
    usage = re.sub(r"\s+", " ", usage_m.group(1)).strip() if usage_m else None
    options, positionals = [], []
    section = None
    for ln in text.splitlines():
        low = ln.strip().lower()
        if low in ("positional arguments:", "positionals:"):
            section = "pos"; continue
        if low.startswith(("options:", "optional arguments:")) or low.endswith("options:") or low.endswith("arguments:"):
            section = "opt"; continue
        if section == "pos":
            pm = re.match(r"^\s{2}([\w{}|,.-]+)(?:\s{2,}(.*))?$", ln)
            if pm:
                positionals.append({"name": pm.group(1), "help": (pm.group(2) or "").strip()})
            elif ln.startswith("    ") and positionals:
                positionals[-1]["help"] = (positionals[-1]["help"] + " " + ln.strip()).strip()
            elif not ln.strip():
                section = None
            continue
        if section == "opt":
            om = OPT_LINE_RE.match(ln)
            if om:
                flags = [{"flag": f, "metavar": mv or None} for f, mv in FLAG_RE.findall(om.group(1))]
                options.append({"flags": [f["flag"] for f in flags], "metavar": next((f["metavar"] for f in flags if f["metavar"]), None), "help": (om.group(2) or "").strip()})
            elif ln.startswith("    ") and options:
                options[-1]["help"] = (options[-1]["help"] + " " + ln.strip()).strip()
            elif not ln.strip():
                section = None
    desc = None
    if usage_m:
        after = text[usage_m.end():].strip("\n")
        para = after.split("\n\n", 1)[0].strip()
        if para and not re.match(r"^(positional|optional|options)", para, re.I):
            desc = re.sub(r"\s+", " ", para)
    return {"usage": usage, "description": desc, "options": options, "positionals": positionals}


def probe_help(runner: str, path: Path, tmp: str) -> tuple:
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": tmp, "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1",
           "NO_COLOR": "1", "TERM": "dumb"}
    # Shim orca-graph/graph-viz/graph-atlas cần engine; HOME là thư mục tạm nên chỉ đường qua biến môi trường.
    engine = os.environ.get("ORCA_GRAPH_ENGINE_DIR") or str(Path.home() / ".orca-graph" / "repo" / "engine")
    if Path(engine, "orca-graph.py").is_file():
        env["ORCA_GRAPH_ENGINE_DIR"] = engine
    try:
        p = subprocess.run([runner, str(path), "--help"], stdin=subprocess.DEVNULL, cwd=tmp, env=env,
                           capture_output=True, text=True, errors="replace", timeout=HELP_TIMEOUT_S)
        out = (p.stdout or "") + (("\n" + p.stderr) if p.stderr.strip() else "")
        return p.returncode, out.strip()[:HELP_MAX_CHARS]
    except subprocess.TimeoutExpired:
        return -1, None
    except OSError as e:
        return -2, str(e)


def module_doc(path: Path) -> str:
    try:
        t = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    if path.suffix == ".py":
        m = re.search(r'^(?:#![^\n]*\n)?(?:#[^\n]*\n|\s*\n)*(?:from __future__[^\n]*\n\s*)?[rub]*("""|\'\'\')(.*?)\1', t, re.S)
        return re.sub(r"\s+", " ", m.group(2)).strip()[:600] if m else ""
    # sh/mjs: khối comment đầu file
    lines = []
    for ln in t.splitlines()[1:40]:
        if ln.startswith("#") or ln.startswith("//"):
            lines.append(ln.lstrip("#/ ").rstrip())
        elif ln.strip():
            break
    return " ".join(lines).strip()[:600]


def collect_tools(with_help: bool) -> list:
    tools = []
    with tempfile.TemporaryDirectory(prefix="overstack-catalog-") as tmp:
        for rel, kind, exts in TOOL_DIRS:
            for f in sorted((ROOT / rel).iterdir()):
                if not f.is_file() or f.suffix not in exts or f.name in LIB_NAMES or f.name.startswith("_"):
                    continue
                runner = RUNNERS[f.suffix]
                rc, text = (None, None)
                if with_help:
                    rc, text = probe_help(runner, f, tmp)
                parsed = parse_help(text) if text and rc == 0 else {"usage": None, "description": None, "options": [], "positionals": []}
                tools.append({
                    "name": f.stem,
                    "file": f.name,
                    "kind": kind,
                    "path": f.relative_to(ROOT).as_posix(),
                    "runner": runner,
                    "summary": parsed["description"] or module_doc(f),
                    "usage": parsed["usage"],
                    "options": parsed["options"],
                    "positionals": parsed["positionals"],
                    "help": text if rc == 0 else None,
                    "helpRc": rc,
                    "stdinJson": kind == "validator",
                })
    # tên trùng giữa hai thư mục (vd orca-graph shim) → thêm hậu tố kind để id duy nhất
    seen: dict = {}
    for t in tools:
        seen.setdefault(t["name"], []).append(t)
    for name, group in seen.items():
        if len(group) > 1:
            for t in group:
                t["name"] = f"{name}.{t['kind']}"
    return tools


def build(with_help: bool) -> dict:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "root": "Rheinmir/setup",
        "skillsRoot": skills_root().as_posix(),
        "skillsVersion": skills_version(),
        "skills": collect_skills(),
        "rules": collect_rules(),
        "tools": collect_tools(with_help),
    }


def stable(cat: dict) -> str:
    return json.dumps(cat, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def projection(cat: dict) -> dict:
    """Phần `--check` so sánh: danh tính và hợp đồng, KHÔNG gồm help thô (help đổi theo máy: đường dẫn tạm, engine có hay không)."""
    return {
        "skills": [{k: s[k] for k in ("name", "path", "group", "modelInvocable", "external")} for s in cat["skills"]],
        "rules": [{k: r[k] for k in ("id", "name", "validator", "validatorPath", "enforce_at", "applies_to")} for r in cat["rules"]],
        "tools": [{k: t[k] for k in ("name", "path", "runner", "kind", "stdinJson")} for t in cat["tools"]],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Sinh mcp/catalog.json từ skills/, harness/policy.yaml và các thư mục script của overstack.")
    ap.add_argument("--check", action="store_true", help="so với mcp/catalog.json trên đĩa; rc 2 khi lệch")
    ap.add_argument("--no-help", action="store_true", help="bỏ bước probe --help từng script (help=null)")
    ap.add_argument("--out", default=str(OUT), help="đường dẫn ghi (mặc định mcp/catalog.json)")
    a = ap.parse_args()
    if a.check:
        # --check không probe --help: so danh tính + hợp đồng (projection), chạy < 1 s, ổn định giữa máy dev và container.
        cat = build(with_help=False)
        counts = {k: len(v) for k, v in cat.items() if isinstance(v, list)}
        try:
            old = json.loads(Path(a.out).read_text(encoding="utf-8")) if Path(a.out).is_file() else {}
        except json.JSONDecodeError:
            old = {}
        if not old or projection(old) != projection(cat):
            for k in ("skills", "rules", "tools"):
                on = {x.get("name") or x.get("id") for x in old.get(k, [])}
                nn = {x.get("name") or x.get("id") for x in cat[k]}
                if on != nn:
                    print(f"  {k}: +{sorted(nn - on)} -{sorted(on - nn)}", file=sys.stderr)
            print(f"catalog LỆCH đĩa ({counts}) — chạy: python3 mcp/scripts/gen-catalog.py", file=sys.stderr)
            return 2
        print(f"catalog khớp đĩa {counts}")
        return 0
    cat = build(with_help=not a.no_help)
    text = stable(cat)
    counts = {k: len(v) for k, v in cat.items() if isinstance(v, list)}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(text, encoding="utf-8")
    helped = sum(1 for t in cat["tools"] if t["help"])
    print(f"→ {a.out}  {counts}  help ok {helped}/{len(cat['tools'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
