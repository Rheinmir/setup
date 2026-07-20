#!/usr/bin/env python3
"""travel-policy-sync: `travel-policy.yaml` phải khớp cái `install-harness.sh` thật sự copy.

travel-policy.yaml là VĂN BẢN MÔ TẢ; thứ sinh ra hành vi là installer. Khi hai bên
lệch, mọi câu trả lời "cái gì tới tay user" đọc từ policy đều sai mà không ai biết.
Validator này đọc khối `--global` của installer, dựng tập pattern thực sự được copy
xuống `~/.claude/harness/`, rồi đối chiếu hai chiều với policy:

  - tầng `framework_only` khai "không đi xuống" mà installer VẪN copy  → lỗi
  - tầng `global_shared` khai "đi xuống" mà installer KHÔNG copy       → lỗi

Contract: `travel_policy_sync.py [--root path]` (CLI / pre-commit / CI).
Exit 0 = khớp, exit 2 = lệch (liệt kê trên stderr). Thiếu file → 0 (fail-open,
downstream không có repo framework).
"""
from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Đường dẫn trong policy nhưng KHÔNG do installer --global lo:
#   llmwiki/.claude/hooks/*.py → copy phẳng vào $GH/hooks/ (đã kiểm qua entry engine_core khác)
#   research_reach → skill ngoài, cài bằng `agent-reach install`, không qua installer
SKIP_SECTIONS = {"research_reach"}


def copied_patterns(installer: Path) -> list[str]:
    """Pattern repo-relative mà khối --global của install-harness.sh copy xuống global."""
    text = installer.read_text(encoding="utf-8")
    start = text.find('= "--global" ]')
    if start < 0:
        return []
    end = text.find('SETTINGS="$HOME/.claude/settings.json"', start)
    block = text[start:end if end > 0 else len(text)]

    pats = []
    # glob hay nằm NGOÀI dấu nháy: `cp "$SRC/harness/scripts/"*.py` — phải ghép đuôi lại,
    # bỏ đuôi thì pattern cụt thành thư mục và mọi file trong đó bị coi là không travel.
    for m in re.finditer(r'^\s*cp\s+(-R\s+)?"\$SRC/([^"]+)"(\S*)', block, re.M):
        recursive, src = bool(m.group(1)), m.group(2) + m.group(3)
        if recursive:
            # `cp -R "$SRC/dir/." "$GH/dir/"` → cả cây con
            pats.append(src.rstrip("/.") + "/**")
        else:
            pats.append(src)
    return pats


def travels(path: str, pats: list[str]) -> bool:
    parts = path.split("/")
    for p in pats:
        if p.endswith("/**"):
            if path.startswith(p[:-2]):
                return True
            continue
        # khớp theo TỪNG segment: `*` của shell không vượt `/`, fnmatch thì có
        pp = p.split("/")
        if len(pp) == len(parts) and all(fnmatch.fnmatch(a, b) for a, b in zip(parts, pp)):
            return True
    return False


def policy_paths(policy: Path) -> tuple[list[str], list[str]]:
    """(framework_only, global_shared) — path repo-relative rút từ YAML, không cần pyyaml.

    framework_only là map `path: "mô tả"`; global_shared là map section → list các
    dòng `"a/b.py + c/d.py — mô tả"`.
    """
    fw, gl = [], []
    section = None       # 'framework_only' | 'global_shared' | None
    subsection = None
    for raw in policy.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if not line.strip():
            continue
        if not line[0].isspace():
            section = line.split(":", 1)[0].strip()
            subsection = None
            continue
        stripped = line.strip()
        if section == "framework_only" and ":" in stripped:
            fw.append(stripped.split(":", 1)[0].strip())
        elif section == "global_shared":
            if not stripped.startswith("-"):
                subsection = stripped.rstrip(":").strip()
            elif subsection not in SKIP_SECTIONS:
                item = stripped.lstrip("- ").strip('"').split("—")[0]
                # `a/b/x.py + y.py` — vế sau viết tắt, thiếu prefix; kế thừa dir của vế trước
                prefix = ""
                for hit in re.findall(r"[\w./*-]+\.(?:py|yaml|json|md)", item):
                    if "/" in hit:
                        prefix = hit.rsplit("/", 1)[0] + "/"
                    else:
                        hit = prefix + hit
                    gl.append(hit)
    return fw, gl


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(args[args.index("--root") + 1]) if "--root" in args else ROOT
    installer = root / "harness" / "scripts" / "install-harness.sh"
    policy = root / "harness" / "travel-policy.yaml"
    if not installer.is_file() or not policy.is_file():
        return 0

    pats = copied_patterns(installer)
    if not pats:
        print("[travel-policy-sync] không đọc được khối --global của install-harness.sh",
              file=sys.stderr)
        return 2

    fw, gl = policy_paths(policy)
    leaked = [p for p in fw if travels(p, pats)]
    # `llmwiki/.claude/hooks/*.py` copy phẳng vào $GH/hooks/ — pattern khớp thẳng, không cần trừ.
    missing = [p for p in gl if not travels(p, pats)]

    if not leaked and not missing:
        return 0

    out = ["[travel-policy-sync] travel-policy.yaml LỆCH so với install-harness.sh:"]
    if leaked:
        out.append(f"  khai framework_only (không đi xuống) nhưng installer VẪN copy — {len(leaked)}:")
        out += [f"      {p}" for p in leaked]
    if missing:
        out.append(f"  khai global_shared (đi xuống) nhưng installer KHÔNG copy — {len(missing)}:")
        out += [f"      {p}" for p in missing]
    out.append("  -> sửa MỘT bên: policy mô tả, installer mới là hành vi thật.")
    print("\n".join(out), file=sys.stderr)
    return 2


def demo():
    pats = ["fdk/tools/*.py", "harness/poc-vendor-neutral/**", "harness/version.json"]
    assert travels("fdk/tools/medic.py", pats)
    assert travels("harness/poc-vendor-neutral/bin/x.sh", pats)
    assert not travels("harness/scripts/medic.py", pats)
    assert not travels("fdk/tools/sub/deep.py", pats), "fnmatch * không được vượt thư mục"
    print("demo ok")


if __name__ == "__main__":
    sys.exit(demo() if "--demo" in sys.argv else main())
