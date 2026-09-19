#!/usr/bin/env python3
"""swh-lint — lint CẤU TRÚC chuẩn solid-what-how/1 (SWH) cho skill native (0 token).

Concept chính chủ: [[solid-what-how]] trong wiki framework (PRD §13).
Chỉ chứng minh HÌNH DẠNG gói (structural). Hành vi đúng hay không thì KHÔNG suy ra từ
regex: report luôn ghi behavioral=review_required, runtime=not_claimed (profile documented).

Bỏ qua skills/external/ — skill kéo từ upstream, viết lại sẽ bị đè khi cập nhật.

Dùng:
  python3 fdk/tools/swh-lint.py                       # bảng mọi skill native, exit 0
  python3 fdk/tools/swh-lint.py --skills a,b --ci     # exit 1 nếu có blocking finding
  python3 fdk/tools/swh-lint.py --json                # report swh.report/1 máy đọc
  python3 fdk/tools/swh-lint.py --skills a --preserve HEAD
      # + mọi khối code và `path/lệnh` của bản HEAD phải còn trong bản mới (migrate giữ hành vi)
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STANDARD = "solid-what-how/1"


def section(body, name):
    """Nội dung giữa '## <name>' và heading cấp 2 kế tiếp ('' nếu không có)."""
    m = re.search(rf"^## {name}\b.*?$(.*?)(?=^## |\Z)", body, re.M | re.S)
    return m.group(1) if m else ""


def check(text):
    """→ list finding (rule_id, message). Rỗng = structural pass."""
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    front, body = (fm.group(1), text[fm.end():]) if fm else ("", text)
    bare = re.sub(r"^(`{3,}|~{3,}).*?^\1", "", body, flags=re.M | re.S)  # heading trong khối code không cắt mục
    what, how = section(bare, "WHAT"), section(bare, "HOW")
    lw, lh = what.lower(), how.lower()
    out = []
    if not what.strip() or not how.strip():
        out.append(("SWH-001", "thiếu mục '## WHAT' hoặc '## HOW' (hoặc mục rỗng)"))
    need = {"purpose/trigger": ("purpose", "mục đích"),
            "input/output contract": ("contract", "hợp đồng"),
            "failure boundaries": ("failure", "thất bại", "blocked")}
    miss = [k for k, alts in need.items() if not any(a in lw for a in alts)]
    if what.strip() and miss:
        out.append(("SWH-002", "WHAT thiếu: " + ", ".join(miss)))
    if how.strip() and not re.search(r"^\|\s*W0?1\b", how, re.M):
        out.append(("SWH-003", "HOW thiếu bảng main workflow có step W01 (cột exit/next)"))
    if how.strip() and not re.search(r"(?i)^###.*(branch|nhánh)", how, re.M):
        out.append(("SWH-004", "HOW thiếu mục Branches (bảng guard/rejoin hoặc ghi rõ 'không có nhánh phụ')"))
    if how.strip() and not (re.search(r"positive|đúng", lh) and re.search(r"boundary|failure|biên|lỗi", lh)):
        out.append(("SWH-011", "HOW thiếu ví dụ positive + boundary/failure có expected result"))
    if STANDARD not in front:
        out.append(("SWH-META", f"frontmatter thiếu metadata.design-standard: \"{STANDARD}\""))
    return out


def preserve_tokens(text):
    """Dòng code trong khối ``` + span `...` trông như path/lệnh — thứ migrate không được làm mất."""
    toks = set()
    for block in re.findall(r"^[ \t]*```[^\n]*\n(.*?)^[ \t]*```", text, re.S | re.M):  # fence đầu dòng, ``` inline không tính
        toks.update(ln.strip() for ln in block.splitlines() if len(ln.strip()) >= 4)
    for span in re.findall(r"`([^`\n]{4,})`", text):
        if "/" in span or span.startswith(("python", "bash", "git ", "npx", "node ")):
            toks.add(span.strip())
    return toks


def lost_tokens(old, new):
    return sorted(t for t in preserve_tokens(old) if t not in new)


def package_hash(d):
    h = hashlib.sha256()
    for f in sorted(p for p in d.rglob("*") if p.is_file()):
        h.update(str(f.relative_to(d)).encode() + b"\0" + f.read_bytes() + b"\0")
    return h.hexdigest()


def git_show(rev, rel):
    r = subprocess.run(["git", "-C", str(REPO), "show", f"{rev}:{rel}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def report(d, preserve=None):
    text = (d / "SKILL.md").read_text(encoding="utf-8")
    findings = [{"rule_id": r, "severity": "blocking", "message": m} for r, m in check(text)]
    if preserve:
        old = git_show(preserve, f"skills/{d.name}/SKILL.md")
        lost = lost_tokens(old, text) if old else []
        if lost:
            findings.append({"rule_id": "SWH-PRESERVE", "severity": "blocking",
                             "message": f"{len(lost)} dòng code/path của {preserve} bị mất: " + " | ".join(lost[:5])})
    return {"schema_version": "swh.report/1", "skill_id": d.name, "standard_version": STANDARD,
            "package_hash": package_hash(d), "profile": "documented",
            "structural": "fail" if findings else "pass", "behavioral": "review_required",
            "runtime": "not_claimed", "release_eligible": False, "findings": findings}


def skill_dirs(root, only=None):
    dirs = sorted(p.parent for p in (root / "skills").glob("*/SKILL.md"))  # skills/external/* không khớp glob này
    if only:
        want = set(only)
        dirs = [d for d in dirs if d.name in want]
        missing = want - {d.name for d in dirs}
        if missing:
            sys.exit(f"swh-lint: không có skill native: {', '.join(sorted(missing))}")
    return dirs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skills", help="danh sách tên, phân cách dấu phẩy (mặc định: mọi skill native)")
    ap.add_argument("--ci", action="store_true", help="exit 1 nếu có blocking finding")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--preserve", metavar="REV", help="so với bản ở git REV: không được mất code/path")
    ap.add_argument("--root", default=str(REPO))
    a = ap.parse_args(argv)
    reps = [report(d, a.preserve) for d in skill_dirs(Path(a.root), a.skills.split(",") if a.skills else None)]
    bad = [r for r in reps if r["structural"] == "fail"]
    if a.json:
        print(json.dumps(reps, ensure_ascii=False, indent=2))
    else:
        for r in reps:
            mark = "✗" if r["findings"] else "✓"
            print(f"{mark} {r['skill_id']:<28} " + "; ".join(f"{f['rule_id']}" for f in r["findings"]))
            for f in r["findings"]:
                print(f"    {f['rule_id']}: {f['message']}")
        print(f"\n{len(reps) - len(bad)}/{len(reps)} skill native đạt cấu trúc SWH (profile documented; "
              "hành vi = review_required, không suy ra từ lint)")
    return 1 if (a.ci and bad) else 0


if __name__ == "__main__":
    sys.exit(main())
