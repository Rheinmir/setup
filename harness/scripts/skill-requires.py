#!/usr/bin/env python3
"""skill-requires — kiểm hợp đồng phụ thuộc của từng skill: `metadata.requires` trong frontmatter SKILL.md.

Vì sao có (PLAN 141026-skills-split, T1): skill tách ra repo `Rheinmir/skills`, engine ở lại `Rheinmir/setup`
(cài global `~/.claude/harness`). 40/106 skill gọi script engine; tách văn bản mà không tách HỢP ĐỒNG thì skill mới
gọi script chưa có ở máy người dùng và gãy câm. Hợp đồng là frontmatter:

    metadata:
      loop: dev-loop                      # wiki-loop | dev-loop | orchestrate | utils
      requires:
        harness: ">=1.3.127"              # sàn template_version của ~/.claude/harness/version.json
        bin: [python3, node]              # binary phải có trong PATH
        scripts: [fdk/tools/medic.py]     # phải tồn tại dưới harness home (bản global) hoặc --repo-root
        framework_scripts: [fdk/tools/new-skill.py]   # chỉ có trong checkout repo framework (lớp C)

Dùng:
    python3 harness/scripts/skill-requires.py check                      # skills dir tự dò (xem skills_dir)
    python3 harness/scripts/skill-requires.py check --installed          # ~/.claude/skills (máy người dùng, sau npx)
    python3 harness/scripts/skill-requires.py check --skills-dir ~/orca/skills/skills --repo-root ~/orca/setup --ci
    python3 harness/scripts/skill-requires.py --self-test

rc 0 = mọi skill đủ · rc 2 = có skill thiếu (in bảng) · rc 1 = lỗi vào (không có skills dir).
`framework_scripts` chỉ tính là thiếu khi truyền --repo-root (CI của repo skills); ở máy người dùng chúng là thông tin.
Không cần pyyaml: parser con cho frontmatter (scalar, block/flow list, map lồng 2 tầng); có pyyaml thì dùng pyyaml.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
KNOWN_BINS = ("python3", "node", "npx", "npm", "pnpm", "playwright", "curl", "gh", "docker", "opencode", "agy",
              "orca", "ffmpeg", "ollama", "jq", "rg", "pandoc")
LOOPS = ("wiki-loop", "dev-loop", "orchestrate", "utils")


# ── frontmatter ──────────────────────────────────────────────────────────────
def _split_frontmatter(text: str) -> str | None:
    m = re.match(r"^---[ \t]*\r?\n(.*?)\r?\n---", text, re.S)
    return m.group(1) if m else None


def _scalar(v: str):
    v = v.strip()
    if not v:
        return ""
    if v[0] == v[-1] and v[0] in "\"'" and len(v) >= 2:
        return v[1:-1]
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [_scalar(x) for x in re.split(r",\s*", inner)] if inner else []
    if v in ("true", "True"):
        return True
    if v in ("false", "False"):
        return False
    return v


def _mini_yaml(src: str) -> dict:
    """Tập con YAML đủ cho frontmatter skill: map lồng theo thụt đầu dòng, list block `- x`, list flow `[a, b]`,
    scalar folded `>-`/`|` gom dòng thụt. Không hỗ trợ anchor/tag."""
    root: dict = {}
    stack: list[tuple[int, dict | list]] = [(-1, root)]
    lines = src.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        i += 1
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            stack = [(-1, root)]
        cur = stack[-1][1]
        if line.startswith("- "):
            if not isinstance(cur, list):
                continue
            cur.append(_scalar(line[2:]))
            continue
        m = re.match(r"^([^:]+?):(?:\s+(.*))?$", line)
        if not m:
            continue
        key, val = m.group(1).strip().strip("\"'"), (m.group(2) or "").strip()
        if not isinstance(cur, dict):
            continue
        if val in (">", ">-", "|", "|-", ">+", "|+"):
            buf = []
            while i < len(lines) and (not lines[i].strip() or (len(lines[i]) - len(lines[i].lstrip(" "))) > indent):
                buf.append(lines[i].strip())
                i += 1
            cur[key] = " ".join(x for x in buf if x) if val.startswith(">") else "\n".join(buf)
            continue
        if val == "":
            # map lồng hoặc list block — nhìn dòng kế
            nxt = lines[i].lstrip() if i < len(lines) else ""
            child: dict | list = [] if nxt.startswith("- ") else {}
            cur[key] = child
            stack.append((indent, child))
            continue
        cur[key] = _scalar(val)
    return root


def frontmatter(text: str) -> dict:
    src = _split_frontmatter(text)
    if src is None:
        return {}
    try:
        import yaml  # type: ignore
        d = yaml.safe_load(src)
        return d if isinstance(d, dict) else {}
    except Exception:
        return _mini_yaml(src)


def parse_requires(text: str) -> dict:
    """metadata.requires chuẩn hoá: {harness: str|None, bin: [..], scripts: [..], framework_scripts: [..]}."""
    fm = frontmatter(text)
    meta = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
    req = meta.get("requires") if isinstance(meta.get("requires"), dict) else {}

    def _list(k):
        v = req.get(k) or []
        if isinstance(v, str):
            v = [x for x in re.split(r"[,\s]+", v) if x]
        return [str(x) for x in v]

    h = req.get("harness")
    return {"harness": (str(h).strip() if h else None), "bin": _list("bin"), "scripts": _list("scripts"),
            "framework_scripts": _list("framework_scripts"), "loop": meta.get("loop")}


# ── semver ───────────────────────────────────────────────────────────────────
def cmp_semver(a: str, b: str) -> int:
    def key(v):
        return [int(x) if x.isdigit() else 0 for x in re.split(r"[.\-+]", str(v).strip().lstrip("v"))[:3]] + [0, 0, 0]
    ka, kb = key(a)[:3], key(b)[:3]
    return (ka > kb) - (ka < kb)


# ── kiểm ─────────────────────────────────────────────────────────────────────
def skills_dir(explicit: str | None = None, installed: bool = False) -> Path:
    if installed:
        return Path.home() / ".claude" / "skills"
    if explicit:
        return Path(explicit).expanduser()
    env = os.environ.get("OVERSTACK_SKILLS_DIR")
    if env:
        return Path(env).expanduser()
    if (REPO / "skills").is_dir():
        return REPO / "skills"
    return Path.home() / ".claude" / "skills"


def harness_version(harness_home: Path, repo_root: Path | None) -> str:
    for p in ([repo_root / "harness" / "version.json"] if repo_root else []) + [harness_home / "version.json"]:
        try:
            return str(json.loads(p.read_text(encoding="utf-8")).get("template_version") or "0")
        except Exception:
            continue
    return "0"


def _exists(rel: str, harness_home: Path, repo_root: Path | None) -> bool:
    if (harness_home / rel).is_file():
        return True
    return bool(repo_root) and (repo_root / rel).is_file()


def check_skill(skill_dir: Path, harness_home: Path, have_version: str, repo_root: Path | None = None) -> dict:
    sk = skill_dir / "SKILL.md"
    try:
        req = parse_requires(sk.read_text(encoding="utf-8", errors="ignore"))
    except OSError:
        return {"name": skill_dir.name, "ok": False, "error": "không đọc được SKILL.md"}
    floor = (req["harness"] or "").lstrip(">=~^ ").strip()
    missing_bin = [b for b in req["bin"] if shutil.which(b) is None]
    missing_scripts = [s for s in req["scripts"] if not _exists(s, harness_home, repo_root)]
    fw_missing = [s for s in req["framework_scripts"] if not (repo_root and (repo_root / s).is_file())]
    floor_ok = (not floor) or cmp_semver(have_version, floor) >= 0
    ok = floor_ok and not missing_bin and not missing_scripts and (not repo_root or not fw_missing)
    return {"name": skill_dir.name, "ok": ok, "loop": req["loop"], "harness_floor": floor or None,
            "harness_have": have_version, "floor_ok": floor_ok, "missing_bin": missing_bin,
            "missing_scripts": missing_scripts, "framework_scripts_missing": fw_missing,
            "declared": bool(req["harness"] or req["bin"] or req["scripts"] or req["framework_scripts"])}


def iter_skills(sdir: Path):
    seen = set()
    for p in sorted(list(sdir.glob("*/SKILL.md")) + list(sdir.glob("external/*/SKILL.md"))):
        d = p.parent
        key = d.resolve()
        if key in seen:
            continue
        seen.add(key)
        yield d


def run_check(args) -> int:
    sdir = skills_dir(args.skills_dir, args.installed)
    if not sdir.is_dir():
        print(f"[skill-requires] không có thư mục skill: {sdir}", file=sys.stderr)
        return 1
    hh = Path(args.harness_home).expanduser()
    rr = Path(args.repo_root).expanduser().resolve() if args.repo_root else None
    have = harness_version(hh, rr)
    rows = [check_skill(d, hh, have, rr) for d in iter_skills(sdir)]
    bad = [r for r in rows if not r["ok"]]
    undeclared = [r["name"] for r in rows if not r.get("declared")]
    if args.json:
        print(json.dumps({"skills_dir": str(sdir), "harness_home": str(hh), "harness_have": have,
                          "total": len(rows), "bad": len(bad), "undeclared": undeclared, "rows": rows},
                         ensure_ascii=False, indent=2))
    else:
        print(f"[skill-requires] {sdir} · {len(rows)} skill · harness v{have} ({'repo ' + str(rr) if rr else hh})")
        for r in bad:
            why = []
            if not r.get("floor_ok", True):
                why.append(f"cần harness >= {r['harness_floor']} (máy có {r['harness_have']})")
            if r.get("missing_bin"):
                why.append("thiếu bin: " + ", ".join(r["missing_bin"]))
            if r.get("missing_scripts"):
                why.append("thiếu script: " + ", ".join(r["missing_scripts"]))
            if rr and r.get("framework_scripts_missing"):
                why.append("thiếu script framework: " + ", ".join(r["framework_scripts_missing"]))
            if r.get("error"):
                why.append(r["error"])
            print(f"  ✗ {r['name']:<28} {' · '.join(why)}")
        fw_only = [r["name"] for r in rows if r["ok"] and r.get("framework_scripts_missing") and not rr]
        if fw_only and not args.ci:
            print(f"  ℹ {len(fw_only)} skill chỉ chạy đủ trong checkout repo framework (lớp C): {', '.join(fw_only)}")
        if undeclared and args.ci:
            print(f"  ℹ {len(undeclared)} skill chưa khai metadata.requires (thuần văn bản): "
                  + ", ".join(undeclared[:8]) + (" …" if len(undeclared) > 8 else ""))
        print(f"  → {len(rows) - len(bad)}/{len(rows)} đủ phụ thuộc" + (f" · {len(bad)} THIẾU" if bad else ""))
    return 2 if bad else 0


# ── gen: sinh metadata.loop + metadata.requires từ grep tất định ─────────────
SCRIPT_REF_RE = re.compile(r"(?<![\w/.-])((?:harness/scripts|fdk/tools|harness/validators|harness/poc-vendor-neutral(?:/bin)?)"
                           r"/[A-Za-z0-9_.-]+\.(?:py|sh|mjs|js))")
FENCE_RE = re.compile(r"```[^\n]*\n(.*?)```", re.S)
# vị trí LỆNH trong khối code: đầu dòng (sau `$ `, `env …`, `cd … &&`), hoặc sau && || | ; $(
CMD_POS_RE = re.compile(r"(?:^|&&|\|\||\||;|\$\(|\bsudo\s+|\bnohup\s+|\btime\s+)\s*(?:\$\s*)?(?:env\s+(?:-u\s+\S+\s+|[A-Z_]+=\S+\s+)*)?"
                        r"(" + "|".join(KNOWN_BINS) + r")\b", re.M)
# không bao giờ tới máy người dùng (install-harness.sh STRIP_TIER3 + script cài đặt/CI chỉ chạy trong repo framework)
FRAMEWORK_ONLY_EXTRA = {"fdk/tools/fdk-kit.sh", "fdk/tools/sync-skill.sh", "harness/scripts/fresh-install-smoke.sh",
                        "harness/scripts/install-harness.sh"}
DEFAULT_FLOOR = ">=1.3.127"


def framework_only_set(repo_root: Path) -> set[str]:
    out = set(FRAMEWORK_ONLY_EXTRA)
    ih = repo_root / "harness" / "scripts" / "install-harness.sh"
    try:
        m = re.search(r'STRIP_TIER3="\n(.*?)\n"', ih.read_text(encoding="utf-8"), re.S)
        if m:
            out |= {ln.strip() for ln in m.group(1).splitlines() if ln.strip()}
    except OSError:
        pass
    return out


def load_loop_map(path: str | None) -> dict:
    if not path:
        return {}
    try:
        t = Path(path).read_text(encoding="utf-8")
        m = re.search(r"LOOP_MAP\s*=\s*\{(.*?)\n\}", t, re.S)
        return dict(re.findall(r'"([\w-]+)"\s*:\s*"([\w-]+)"', m.group(1))) if m else {}
    except OSError:
        return {}


def derive_requires(skill_dir: Path, repo_root: Path, floor: str = DEFAULT_FLOOR) -> dict:
    """Quét tất định: script engine được nhắc trong MỌI file văn bản của skill (chỉ giữ path TỒN TẠI trong repo),
    binary ở vị trí lệnh trong khối code của SKILL.md + references/*.md."""
    fw_only = framework_only_set(repo_root)
    refs: set[str] = set()
    for p in sorted(skill_dir.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in (".md", ".sh", ".py", ".txt", ".yaml", ".yml", ".json", ".mjs", ".js", ".ts"):
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for r in SCRIPT_REF_RE.findall(txt):
            if (repo_root / r).is_file():
                refs.add(r)
    scripts = sorted(r for r in refs if r not in fw_only)
    fw_scripts = sorted(r for r in refs if r in fw_only)
    bins: set[str] = set()
    for md in [skill_dir / "SKILL.md", *sorted((skill_dir / "references").glob("*.md"))] if (skill_dir / "references").is_dir() else [skill_dir / "SKILL.md"]:
        try:
            txt = md.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for block in FENCE_RE.findall(txt):
            bins |= set(CMD_POS_RE.findall(block))
    if scripts or fw_scripts:
        bins.add("python3") if any(s.endswith((".py",)) for s in scripts + fw_scripts) else None
        if any(s.endswith(".mjs") for s in scripts + fw_scripts):
            bins.add("node")
    bins.discard("npm") if "npx" in bins and "npm" not in bins else None
    out = {"bin": sorted(bins), "scripts": scripts, "framework_scripts": fw_scripts,
           "harness": floor if (scripts or fw_scripts) else None}
    return out


def _render_requires(req: dict) -> list[str]:
    lines = ["  requires:"]
    if req.get("harness"):
        lines.append(f'    harness: "{req["harness"]}"')
    for k in ("bin", "scripts", "framework_scripts"):
        if req.get(k):
            lines.append(f"    {k}: [" + ", ".join(req[k]) + "]")
    return lines if len(lines) > 1 else []


def rewrite_frontmatter(text: str, loop: str | None, req: dict) -> str:
    """Ghi metadata.loop + metadata.requires vào frontmatter, giữ nguyên mọi khoá khác (idempotent)."""
    m = re.match(r"^(---[ \t]*\r?\n)(.*?)(\r?\n---)", text, re.S)
    if not m:
        raise ValueError("không có frontmatter")
    head, body, tail = m.group(1), m.group(2), m.group(3)
    lines = body.split("\n")
    # tìm khối metadata (top-level)
    mi = next((i for i, ln in enumerate(lines) if re.match(r"^metadata:\s*$", ln)), None)
    new_meta = ([f"  loop: {loop}"] if loop else []) + _render_requires(req)
    if mi is None:
        if not new_meta:
            return text
        lines = lines + ["metadata:"] + new_meta
    else:
        # phạm vi khối: các dòng thụt sau metadata:
        j = mi + 1
        while j < len(lines) and (lines[j].startswith(" ") or not lines[j].strip()):
            j += 1
        blk = lines[mi + 1:j]
        kept, k = [], 0
        while k < len(blk):
            ln = blk[k]
            if re.match(r"^  (loop|requires):", ln):
                k += 1
                while k < len(blk) and (blk[k].startswith("    ") or not blk[k].strip()):
                    k += 1
                continue
            kept.append(ln)
            k += 1
        while kept and not kept[-1].strip():
            kept.pop()
        lines = lines[:mi + 1] + kept + new_meta + lines[j:]
    return head + "\n".join(lines) + tail + text[m.end():]


def run_gen(args) -> int:
    sdir = skills_dir(args.skills_dir, False)
    rr = Path(args.repo_root).expanduser().resolve() if args.repo_root else REPO
    if not sdir.is_dir():
        print(f"[skill-requires] không có thư mục skill: {sdir}", file=sys.stderr)
        return 1
    loop_map = load_loop_map(args.loop_map)
    drift, changed, rows = [], 0, []
    for d in iter_skills(sdir):
        sk = d / "SKILL.md"
        text = sk.read_text(encoding="utf-8")
        cur = parse_requires(text)
        want = derive_requires(d, rr, args.floor)
        loop = cur.get("loop") or loop_map.get(d.name) or "utils"
        if loop not in LOOPS:
            loop = "utils"
        same = (cur["harness"] == want["harness"] and cur["bin"] == want["bin"] and cur["scripts"] == want["scripts"]
                and cur["framework_scripts"] == want["framework_scripts"] and cur.get("loop") == loop)
        rows.append((d.name, loop, want))
        if same:
            continue
        drift.append(d.name)
        if args.write:
            sk.write_text(rewrite_frontmatter(text, loop, want), encoding="utf-8")
            changed += 1
    if args.check:
        if drift:
            print(f"[skill-requires] LỆCH {len(drift)} skill (frontmatter ≠ grep): " + ", ".join(drift[:12])
                  + (" …" if len(drift) > 12 else "") + "\n  → sửa: python3 harness/scripts/skill-requires.py gen --write", file=sys.stderr)
            return 2
        print(f"[skill-requires] gen --check: {len(rows)} skill khớp")
        return 0
    n_scripts = sum(1 for _, _, w in rows if w["scripts"] or w["framework_scripts"])
    print(f"[skill-requires] {sdir} · {len(rows)} skill · {n_scripts} gọi engine · {len(drift)} cần cập nhật"
          + (f" · đã ghi {changed}" if args.write else " (dry-run, thêm --write)"))
    if not args.write:
        for name, loop, w in rows:
            if name in drift:
                print(f"  {name:<28} {loop:<11} harness={w['harness'] or '-'} bin={','.join(w['bin']) or '-'} "
                      f"scripts={len(w['scripts'])} fw={len(w['framework_scripts'])}")
    return 0


# ── self-test ────────────────────────────────────────────────────────────────
def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        hh = t / "harness-home"
        (hh / "fdk" / "tools").mkdir(parents=True)
        (hh / "fdk" / "tools" / "medic.py").write_text("# x\n")
        (hh / "version.json").write_text(json.dumps({"template_version": "1.3.127"}))
        sd = t / "skills"
        (sd / "ok-sk").mkdir(parents=True)
        (sd / "ok-sk" / "SKILL.md").write_text(
            "---\nname: ok-sk\ndescription: >-\n  nhiều dòng\n  gom lại\nmetadata:\n  design-standard: \"solid-what-how/1\"\n"
            "  loop: dev-loop\n  requires:\n    harness: \">=1.3.126\"\n    bin: [python3]\n    scripts: [fdk/tools/medic.py]\n---\n# ok\n")
        (sd / "floor-sk").mkdir()
        (sd / "floor-sk" / "SKILL.md").write_text(
            "---\nname: floor-sk\ndescription: x\nmetadata:\n  requires:\n    harness: \">=9.0.0\"\n---\n")
        (sd / "bin-sk").mkdir()
        (sd / "bin-sk" / "SKILL.md").write_text(
            "---\nname: bin-sk\ndescription: x\nmetadata:\n  requires:\n    bin:\n      - khong-co-binary-nay-9f3a\n---\n")
        (sd / "fw-sk").mkdir()
        (sd / "fw-sk" / "SKILL.md").write_text(
            "---\nname: fw-sk\ndescription: x\nmetadata:\n  requires:\n    framework_scripts: [fdk/tools/new-skill.py]\n---\n")
        (sd / "plain-sk").mkdir()
        (sd / "plain-sk" / "SKILL.md").write_text("---\nname: plain-sk\ndescription: x\n---\n")
        # parser con (không pyyaml) phải ra cùng kết quả
        req = parse_requires((sd / "ok-sk" / "SKILL.md").read_text())
        assert req["harness"] == ">=1.3.126" and req["bin"] == ["python3"] and req["scripts"] == ["fdk/tools/medic.py"], req
        assert req["loop"] == "dev-loop", req
        mini = _mini_yaml(_split_frontmatter((sd / "ok-sk" / "SKILL.md").read_text()))
        assert mini["description"] == "nhiều dòng gom lại", mini
        assert mini["metadata"]["requires"]["bin"] == ["python3"], mini
        mini2 = _mini_yaml(_split_frontmatter((sd / "bin-sk" / "SKILL.md").read_text()))
        assert mini2["metadata"]["requires"]["bin"] == ["khong-co-binary-nay-9f3a"], mini2
        have = harness_version(hh, None)
        rows = {r["name"]: r for r in (check_skill(d, hh, have) for d in iter_skills(sd))}
        assert rows["ok-sk"]["ok"], rows["ok-sk"]
        assert not rows["floor-sk"]["ok"] and not rows["floor-sk"]["floor_ok"], rows["floor-sk"]
        assert rows["bin-sk"]["missing_bin"] == ["khong-co-binary-nay-9f3a"], rows["bin-sk"]
        assert rows["fw-sk"]["ok"] and rows["fw-sk"]["framework_scripts_missing"], rows["fw-sk"]   # không --repo-root: thông tin
        assert rows["plain-sk"]["ok"] and not rows["plain-sk"]["declared"]
        rr = t / "repo"
        (rr / "fdk" / "tools").mkdir(parents=True)
        (rr / "fdk" / "tools" / "new-skill.py").write_text("# x\n")
        assert check_skill(sd / "fw-sk", hh, have, rr)["ok"]
        assert not check_skill(sd / "fw-sk", hh, have, t / "repo-rong")["ok"]
        assert cmp_semver("1.3.127", "1.3.126") > 0 and cmp_semver("1.10.0", "1.9.9") > 0 and cmp_semver("1.3.0", "1.3.0") == 0
        # gen: grep tất định + ghi frontmatter idempotent
        (rr / "harness" / "scripts").mkdir(parents=True)
        (rr / "harness" / "scripts" / "council.py").write_text("# x\n")
        (rr / "harness" / "scripts" / "install-harness.sh").write_text('STRIP_TIER3="\nfdk/tools/new-skill.py\n"\n')
        (rr / "fdk" / "tools" / "medic.py").write_text("# x\n")
        gsd = t / "gen-skills"
        (gsd / "g-sk").mkdir(parents=True)
        (gsd / "g-sk" / "SKILL.md").write_text(
            "---\nname: g-sk\ndescription: >-\n  mô tả\n  hai dòng\nmetadata:\n  design-standard: \"solid-what-how/1\"\n  contract-version: \"1.0.0\"\n---\n"
            "# g\n```bash\npython3 fdk/tools/medic.py --ci && npx playwright test\ncd x && node fdk/tools/khong-co.mjs\n"
            "gh pr list | jq .\n```\nvăn xuôi nhắc docker không tính; python3 fdk/tools/new-skill.py tạo skill.\n")
        want = derive_requires(gsd / "g-sk", rr)
        assert want["scripts"] == ["fdk/tools/medic.py"], want
        assert want["framework_scripts"] == ["fdk/tools/new-skill.py"], want
        assert "docker" not in want["bin"] and {"python3", "npx", "gh", "jq", "node"} <= set(want["bin"]), want
        assert want["harness"] == DEFAULT_FLOOR
        txt = (gsd / "g-sk" / "SKILL.md").read_text()
        new = rewrite_frontmatter(txt, "dev-loop", want)
        assert rewrite_frontmatter(new, "dev-loop", want) == new, "không idempotent"
        got = parse_requires(new)
        assert got["scripts"] == want["scripts"] and got["bin"] == want["bin"] and got["loop"] == "dev-loop", got
        assert frontmatter(new)["metadata"]["design-standard"] == "solid-what-how/1" and frontmatter(new)["description"] == "mô tả hai dòng"
        assert new.endswith("tạo skill.\n") and "\n---\n# g\n" in new
        # skill không có metadata → thêm khối; skill thuần (không script, không bin) → không đổi file
        plain = "---\nname: p\ndescription: x\n---\nbody\n"
        assert rewrite_frontmatter(plain, None, {"bin": [], "scripts": [], "framework_scripts": [], "harness": None}) == plain
        added = rewrite_frontmatter(plain, "utils", {"bin": ["node"], "scripts": [], "framework_scripts": [], "harness": None})
        assert frontmatter(added)["metadata"]["requires"]["bin"] == ["node"] and frontmatter(added)["metadata"]["loop"] == "utils", added
    print("[skill-requires] self-test OK")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Kiểm metadata.requires của từng skill (harness floor · bin · scripts).")
    ap.add_argument("--self-test", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("check")
    c.add_argument("--skills-dir")
    c.add_argument("--installed", action="store_true", help="kiểm ~/.claude/skills (bản đã cài trên máy)")
    c.add_argument("--harness-home", default=os.environ.get("HARNESS_HOME", str(Path.home() / ".claude" / "harness")))
    c.add_argument("--repo-root", help="checkout repo framework (CI repo skills): scripts + framework_scripts phải có ở đây")
    c.add_argument("--json", action="store_true")
    c.add_argument("--ci", action="store_true")
    g = sub.add_parser("gen", help="sinh metadata.loop + metadata.requires từ grep tất định (dry-run mặc định)")
    g.add_argument("--skills-dir")
    g.add_argument("--repo-root", help="repo framework để xác nhận script tồn tại (mặc định: repo chứa script này)")
    g.add_argument("--loop-map", help="file có LOOP_MAP (sync-skills.py) để seed loop cho skill chưa khai")
    g.add_argument("--floor", default=DEFAULT_FLOOR)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true", help="rc 2 nếu frontmatter lệch grep (CI repo skills)")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.cmd == "check":
        return run_check(a)
    if a.cmd == "gen":
        return run_gen(a)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
