#!/usr/bin/env python3
"""build-capabilities — sinh BẢN ĐỒ NĂNG LỰC BẰNG CODE, luôn-mới, ở CẢ HAI bối cảnh.

Vấn đề: framework đã quá lớn (57 skill + rule + tool) → agent KHÔNG chắc biết hết cái
gì có để dùng → nhiều thứ không bao giờ được dùng tới. Không thể dựa vào agent "nhớ".
Giải: một file CAPABILITIES.md SINH TỪ ĐĨA bằng code (không hardcode, không drift), liệt kê
gọn mọi skill + rule (+ tool nếu là repo framework); AGENT.md trỏ tới nó; `--check` chặn
commit nếu nó cũ → nên nó LUÔN khớp thực tế.

HAI BỐI CẢNH (quyết định scope 2026-06-28, xem ADR-005):
  • Repo framework (có fdk/tools + harness/scripts): map ĐẦY ĐỦ skill+rule+fdk-tool+script,
    ghi fdk/CAPABILITIES.md. `--check` là cổng cứng trong fdk-gate.
  • Dự án downstream (cài framework, KHÔNG có fdk/): skill là GLOBAL ~/.claude/skills, rule
    từ policy.yaml đã cài → map GỌN "đồ nghề bạn có Ở DỰ ÁN NÀY", ghi <root>/CAPABILITIES.md.
    KHÔNG có cổng `--check` cứng ở đây (skill global đổi ngoài project → không phải lỗi của họ).

CLI:
  build-capabilities.py                 # tự nhận bối cảnh, ghi CAPABILITIES.md
  build-capabilities.py --root <path>   # ép root (deployed cạnh hooks gọi với --root <project>)
  build-capabilities.py --check         # exit 2 nếu CAPABILITIES.md cũ (CHỈ dùng ở repo framework)
"""
import re
import subprocess
import sys
from pathlib import Path


def detect_root() -> Path:
    """Repo framework (script ở fdk/tools/) → parents[2]. Nếu script đã được DEPLOY cạnh hooks
    (parents[2] không có fdk/tools) → dùng dự án đang gọi: git-root của CWD, hoặc CWD."""
    repo = Path(__file__).resolve().parents[2]
    if (repo / "fdk" / "tools").is_dir() and (repo / "harness" / "scripts").is_dir():
        return repo
    try:
        r = subprocess.run(["git", "-C", str(Path.cwd()), "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, timeout=3)
        if r.returncode == 0 and r.stdout.strip():
            return Path(r.stdout.strip())
    except Exception:
        pass
    return Path.cwd()


ROOT = detect_root()


def is_framework_repo(root: Path) -> bool:
    return (root / "fdk" / "tools").is_dir() and (root / "harness" / "scripts").is_dir()


def cap_path(root: Path) -> Path:
    """Repo framework → fdk/CAPABILITIES.md. Downstream → <root>/CAPABILITIES.md."""
    return (root / "fdk" / "CAPABILITIES.md") if (root / "fdk").is_dir() else (root / "CAPABILITIES.md")


def skills_dir(root: Path) -> Path:
    """Repo có skills/ nguồn → dùng nó. Downstream KHÔNG có → skill là GLOBAL ~/.claude/skills."""
    local = root / "skills"
    if local.is_dir() and any(local.glob("*/SKILL.md")):
        return local
    return Path.home() / ".claude" / "skills"


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


def load_loops(root: Path):
    """LOOP_MAP từ sync-skills.py (nguồn duy nhất). Downstream không có file này → {} (mọi skill về utils)."""
    try:
        t = (root / "harness" / "scripts" / "sync-skills.py").read_text(encoding="utf-8")
        m = re.search(r"LOOP_MAP\s*=\s*\{(.*?)\}", t, re.S)
        return dict(re.findall(r'"([a-z0-9-]+)"\s*:\s*"([a-z-]+)"', m.group(1))) if m else {}
    except Exception:
        return {}


def first_sentence(s, n=90):
    s = re.split(r"(?<=[.!?。])\s|—| - |\. ", s or "", 1)[0].strip()
    return (s[:n] + "…") if len(s) > n else s


def build(root: Path) -> str:
    repo = is_framework_repo(root)
    loops = load_loops(root)
    skills = []
    for d in sorted(skills_dir(root).glob("*/")):
        name = d.name
        sk = d / "SKILL.md"
        if sk.is_file():
            skills.append((name, loops.get(name, "utils"), first_sentence(parse_frontmatter_desc(sk))))
    by_loop = {}
    for name, loop, desc in skills:
        by_loop.setdefault(loop, []).append((name, desc))

    rules = []
    # policy.yaml ở vị trí khác nhau tuỳ bối cảnh: repo framework dùng poc-vendor-neutral/;
    # dự án CÀI per-project để ở harness/policy.yaml (xem install-harness.sh). Tìm cả hai.
    pol = next((p for p in (
        root / "harness" / "poc-vendor-neutral" / "policy.yaml",   # repo framework
        root / "harness" / "policy.yaml",                          # dự án đã cài (per-project)
    ) if p.is_file()), None)
    if pol and pol.is_file():
        for blk in re.findall(r"id:\s*(R\d+).*?name:\s*([^\n]+)", pol.read_text(encoding="utf-8"), re.S):
            rules.append((blk[0], blk[1].strip().strip('"')))
        rules = sorted(set(rules), key=lambda r: int(r[0][1:]))

    out = ["<!-- SINH BẰNG CODE: build-capabilities.py — ĐỪNG sửa tay; chạy lại để cập nhật. -->",
           "# CAPABILITIES — toàn bộ đồ nghề (luôn-mới, đếm từ đĩa)", ""]

    if repo:
        tools = sorted(p.name for p in (root / "fdk" / "tools").glob("*.py"))
        scripts = sorted(p.name for p in (root / "harness" / "scripts").glob("*.py"))
        out += [f"**{len(skills)} skill · {len(rules)} rule · {len(tools)} fdk-tool · {len(scripts)} harness-script.** "
                "Agent: đây là danh sách ĐẦY ĐỦ những gì bạn có để dùng. Tìm nhanh: `python3 fdk/tools/build-skill-search.py` "
                "rồi `find-skill \"<việc cần làm>\"`. Phát triển framework: gọi `/fdk`.", ""]
    else:
        out += [f"**{len(skills)} skill · {len(rules)} rule** khả dụng Ở DỰ ÁN NÀY "
                "(skill là global `~/.claude/skills`; rule do harness đã cài ở đây gác). "
                "Agent: đây là đồ nghề bạn CÓ — đừng làm lại thứ đã tồn tại. Tìm nhanh: `find-skills \"<việc>\"`. "
                "(Đồ nghề DEV framework — fdk-gate, build-capabilities… — chỉ có trong repo framework.)", ""]

    LOOP_ORDER = ["wiki-loop", "dev-loop", "orchestrate", "utils"]
    out.append("## Skills (gọi bằng `/<tên>`)")
    out += [
        "",
        "> **HAI cách tiếp cận KHÁC NHAU HOÀN TOÀN — chọn trước khi bới danh sách:**",
        "> - **`/br` (oneshot mockup)** — nhắm *một phát ra MOCKUP* từ dữ liệu tổng hợp sẵn có (`raw/`), rồi *sửa agile NGAY trên mockup*. Đi bề rộng nhanh. Dùng khi có tài liệu thô và cần sản phẩm chạy được sớm để bàn tiếp. (`/br auto` = interview tự-điền.)",
        "> - **`/orca-workflow` (plan + spec)** — xử lý *task PLAN + SPEC chức năng* bài bản: khi làm dần *từng phần* dự án, hoặc *sửa vài chức năng trên dự án cũ*. Đi bề sâu, gate từng bước (propose→gate→dispatch→verify).",
        ">",
        "> KHÔNG thay thế nhau: `/br` = oneshot rồi agile trên mockup · `/orca-workflow` = plan/spec truy vết từng bước. Các skill dev-loop bên dưới phần lớn là *bước con* do `/orca-workflow` điều phối.",
        "",
    ]
    for loop in LOOP_ORDER + [l for l in by_loop if l not in LOOP_ORDER]:
        if loop not in by_loop:
            continue
        out.append(f"\n### {loop} ({len(by_loop[loop])})")
        for name, desc in sorted(by_loop[loop]):
            out.append(f"- **`/{name}`** — {desc}" if desc else f"- **`/{name}`**")

    out.append("\n## Harness rules (gác tự động — vi phạm bị chặn)")
    for rid, rname in rules:
        out.append(f"- **{rid}** — {rname}")

    if repo:
        out.append("\n## FDK tools (`python3 fdk/tools/<x>`)")
        out += [f"- `{t}`" for t in tools]
        out.append("\n## Harness scripts (`python3 harness/scripts/<x>`)")
        out += [f"- `{s}`" for s in scripts]
        out.append("\n## Origin\n- Sinh bằng `fdk/tools/build-capabilities.py` từ đĩa (skills/, policy.yaml, fdk/tools/, harness/scripts/, sync-skills LOOP_MAP). KHÔNG hardcode.")
    else:
        out.append("\n## Đồ nghề dev-framework")
        out.append("- Chỉ có trong repo framework (dự án này chỉ CÀI framework, không phát triển nó). "
                   "Cần sửa chính skill/rule/validator → làm ở repo framework với `/fdk`.")
        out.append("\n## Origin\n- Sinh bằng `build-capabilities.py` (deploy cạnh hooks) từ global skills + policy.yaml đã cài. KHÔNG hardcode.")
    return "\n".join(out) + "\n"


def main():
    global ROOT
    args = sys.argv[1:]
    if "--root" in args:
        i = args.index("--root")
        ROOT = Path(args[i + 1]).resolve()
    elif any(a.startswith("--root=") for a in args):
        ROOT = Path(next(a.split("=", 1)[1] for a in args if a.startswith("--root="))).resolve()
    cap = cap_path(ROOT)
    content = build(ROOT)
    if "--check" in args:
        if not is_framework_repo(ROOT):
            # Downstream: skill global đổi ngoài project → KHÔNG chặn commit của họ. Chỉ thông báo.
            print("[build-capabilities] downstream: --check chỉ là cổng cứng ở repo framework; bỏ qua.")
            sys.exit(0)
        cur = cap.read_text(encoding="utf-8") if cap.is_file() else ""
        if cur.strip() != content.strip():
            print("[build-capabilities] CAPABILITIES.md CŨ so với đĩa — chạy "
                  "`python3 fdk/tools/build-capabilities.py` để cập nhật (agent cần map đúng).", file=sys.stderr)
            sys.exit(2)
        print("CAPABILITIES.md khớp đĩa ✓")
        sys.exit(0)
    cap.parent.mkdir(parents=True, exist_ok=True)
    cap.write_text(content, encoding="utf-8")
    try:
        shown = cap.relative_to(ROOT)
    except ValueError:
        shown = cap
    print(f"✓ wrote {shown} ({content.count(chr(10))} dòng)")


if __name__ == "__main__":
    main()
