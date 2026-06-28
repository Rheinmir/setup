#!/usr/bin/env python3
"""build-capabilities — sinh BẢN ĐỒ NĂNG LỰC framework BẰNG CODE, luôn-mới.

Vấn đề: framework đã quá lớn (57 skill + rule + tool) → agent KHÔNG chắc biết hết cái
gì có để dùng → nhiều thứ không bao giờ được dùng tới. Không thể dựa vào agent "nhớ".
Giải: một file CAPABILITIES.md SINH TỪ ĐĨA bằng code (không hardcode, không drift), liệt kê
gọn mọi skill + rule + tool; AGENT.md trỏ tới nó (auto-load mỗi phiên); và `--check` chặn
commit nếu nó cũ → nên nó LUÔN khớp thực tế. Agent đọc AGENT.md là biết "toàn bộ đồ nghề".

CLI:
  build-capabilities.py            # ghi fdk/CAPABILITIES.md từ đĩa
  build-capabilities.py --check    # exit 2 nếu CAPABILITIES.md cũ (khác bản sinh từ đĩa)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAP = ROOT / "fdk" / "CAPABILITIES.md"


def parse_frontmatter_desc(p: Path):
    """Lấy `description` từ YAML frontmatter (hỗ trợ inline + folded >-)."""
    try:
        t = p.read_text(encoding="utf-8")
    except Exception:
        return ""
    m = re.match(r"^---\n(.*?)\n---", t, re.S)
    if not m:
        return ""
    fm = m.group(1)
    dm = re.search(r"^description:\s*(.*)$", fm, re.M)
    if not dm:
        return ""
    val = dm.group(1).strip()
    if val in (">", ">-", "|", "|-"):  # folded/literal → gom dòng thụt sau
        body = []
        for ln in fm[dm.end():].splitlines():
            if ln.strip() and (ln.startswith(" ") or ln.startswith("\t")):
                body.append(ln.strip())
            elif ln.strip():
                break
        val = " ".join(body)
    return val.strip().strip('"').strip("'")


def load_loops():
    """LOOP_MAP từ sync-skills.py (nguồn duy nhất)."""
    try:
        t = (ROOT / "harness" / "scripts" / "sync-skills.py").read_text(encoding="utf-8")
        m = re.search(r"LOOP_MAP\s*=\s*\{(.*?)\}", t, re.S)
        return dict(re.findall(r'"([a-z0-9-]+)"\s*:\s*"([a-z-]+)"', m.group(1))) if m else {}
    except Exception:
        return {}


def first_sentence(s, n=90):
    s = re.split(r"(?<=[.!?。])\s|—| - |\. ", s or "", 1)[0].strip()
    return (s[:n] + "…") if len(s) > n else s


def build() -> str:
    loops = load_loops()
    skills = []
    for d in sorted((ROOT / "skills").glob("*/")):
        name = d.name
        sk = d / "SKILL.md"
        if sk.is_file():
            skills.append((name, loops.get(name, "utils"), first_sentence(parse_frontmatter_desc(sk))))
    by_loop = {}
    for name, loop, desc in skills:
        by_loop.setdefault(loop, []).append((name, desc))

    rules = []
    pol = ROOT / "harness" / "poc-vendor-neutral" / "policy.yaml"
    if pol.is_file():
        for blk in re.findall(r"id:\s*(R\d+).*?name:\s*([^\n]+)", pol.read_text(encoding="utf-8"), re.S):
            rules.append((blk[0], blk[1].strip().strip('"')))
        rules = sorted(set(rules), key=lambda r: int(r[0][1:]))

    tools = sorted(p.name for p in (ROOT / "fdk" / "tools").glob("*.py"))
    scripts = sorted(p.name for p in (ROOT / "harness" / "scripts").glob("*.py"))

    out = ["<!-- SINH BẰNG CODE: fdk/tools/build-capabilities.py — ĐỪNG sửa tay; chạy lại để cập nhật. -->",
           "# CAPABILITIES — toàn bộ đồ nghề framework (luôn-mới, đếm từ đĩa)", "",
           f"**{len(skills)} skill · {len(rules)} rule · {len(tools)} fdk-tool · {len(scripts)} harness-script.** "
           "Agent: đây là danh sách ĐẦY ĐỦ những gì bạn có để dùng. Tìm nhanh: `python3 fdk/tools/build-skill-search.py` "
           "rồi `find-skill \"<việc cần làm>\"`. Phát triển framework: gọi `/fdk`.", ""]

    LOOP_ORDER = ["wiki-loop", "dev-loop", "orchestrate", "utils"]
    out.append("## Skills (gọi bằng `/<tên>`)")
    for loop in LOOP_ORDER + [l for l in by_loop if l not in LOOP_ORDER]:
        if loop not in by_loop:
            continue
        out.append(f"\n### {loop} ({len(by_loop[loop])})")
        for name, desc in sorted(by_loop[loop]):
            out.append(f"- **`/{name}`** — {desc}" if desc else f"- **`/{name}`**")

    out.append("\n## Harness rules (gác tự động — vi phạm bị chặn)")
    for rid, rname in rules:
        out.append(f"- **{rid}** — {rname}")

    out.append("\n## FDK tools (`python3 fdk/tools/<x>`)")
    out += [f"- `{t}`" for t in tools]
    out.append("\n## Harness scripts (`python3 harness/scripts/<x>`)")
    out += [f"- `{s}`" for s in scripts]
    out.append("\n## Origin\n- Sinh bằng `fdk/tools/build-capabilities.py` từ đĩa (skills/, policy.yaml, fdk/tools/, harness/scripts/, sync-skills LOOP_MAP). KHÔNG hardcode.")
    return "\n".join(out) + "\n"


def main():
    content = build()
    if "--check" in sys.argv[1:]:
        cur = CAP.read_text(encoding="utf-8") if CAP.is_file() else ""
        if cur.strip() != content.strip():
            print("[build-capabilities] fdk/CAPABILITIES.md CŨ so với đĩa — chạy "
                  "`python3 fdk/tools/build-capabilities.py` để cập nhật (agent cần map đúng).", file=sys.stderr)
            sys.exit(2)
        print("CAPABILITIES.md khớp đĩa ✓")
        sys.exit(0)
    CAP.parent.mkdir(parents=True, exist_ok=True)
    CAP.write_text(content, encoding="utf-8")
    print(f"✓ wrote {CAP.relative_to(ROOT)} ({content.count(chr(10))} dòng)")


if __name__ == "__main__":
    main()
