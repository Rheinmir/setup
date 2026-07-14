#!/usr/bin/env python3
"""capability-stamp — ÉP framework khai báo khi NĂNG LỰC của nó đổi.

BÀI TOÁN (p-08, xác nhận 2026-07-11): downstream hỏi "tôi có cũ không?" bằng cách so
template_version (stamp dự án ↔ version.json global). Nhưng KHÔNG GÌ ép bump version khi
thêm/sửa năng lực → cả hai đầu đều 1.3.6 → hệ trả lời "current" → **dự án local không bao
giờ biết có chức năng mới**, và model làm việc ở đó không biết mình có thêm đồ nghề.
version.json hiện chỉ hash 60 "pattern" TEMPLATE (00-New-Project.md, .agent…) — KHÔNG phải
skill/rule/engine, nên thêm cả một cổng mới nó vẫn im.

GIẢI: đóng dấu BỀ MẶT NĂNG LỰC (skills + rules + engines) thành một sha. Đổi bề mặt mà chưa
bump → `--check` đỏ → medic đỏ → KHÔNG PUSH ĐƯỢC. Đây là forcing function, không phải lời nhắc.

  capability-stamp.py --check     # sha đĩa ≠ sha ghi trong version.json → exit 1
  capability-stamp.py --update    # ghi sha mới + bump template_version (patch)
  capability-stamp.py --self-test # đổi bề mặt giả → --check phải bắt được

Bề mặt = thứ NGƯỜI DÙNG DOWNSTREAM thật sự nhận:
  · skills/<tên>/SKILL.md   → tên + dòng description (skill mới/đổi trigger = năng lực đổi)
  · policy.yaml             → danh sách rule id (rule mới = luật gác đổi)
  · harness/scripts/*       → engine ship lên global harness
  · llmwiki/.claude/hooks/* → hook ship lên global harness
Cố ý KHÔNG hash nội dung engine: sửa một dòng log trong council.py không phải "năng lực mới".
Hash DANH SÁCH + trigger — thứ downstream cần biết để quyết "tôi có nên update không".
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION_JSON = ROOT / "harness" / "version.json"


# FRONTMATTER YAML HỎNG = SKILL BIẾN MẤT, KHÔNG MỘT DÒNG CẢNH BÁO.
# Verify 2026-07-11: web-crawl + web-clone có `description:` inline chứa `": "` chưa quote →
# YAML ScannerError ("mapping values are not allowed here") → CLI `skills` BỎ QUA im lặng →
# không vào global → KHÔNG vào CAPABILITIES.md → người dùng vĩnh viễn không biết năng lực đó
# tồn tại. Gấp thành block `>-` là parse được: npx 67 → 69 skill, cả hai vào global ngay.
# Đừng đoán theo độ dài hay dấu ':' (đã thử, SAI — brandkit 464 ký tự và ship/raise-issue có ': '
# vẫn ship ngon). Chỉ có PARSER thật mới nói đúng.


def _frontmatter(txt):
    """Khối YAML giữa hai '---' đầu file."""
    m = re.match(r"^---\n(.*?)\n---", txt, re.S)
    return m.group(1) if m else ""


def _parse(fm):
    """(dict|None, lỗi|None). Không có PyYAML → (None, None) = bỏ qua (fail-open)."""
    try:
        import yaml
    except ImportError:
        return None, None
    try:
        d = yaml.safe_load(fm)
        return (d if isinstance(d, dict) else {}), None
    except Exception as e:
        return {}, f"{type(e).__name__}: {str(e).splitlines()[0][:70]}"


def _skills():
    """(tên skill, description) — đổi trigger = downstream cần biết."""
    out = []
    for sk in sorted((ROOT / "skills").glob("*/SKILL.md")):
        d, _ = _parse(_frontmatter(sk.read_text(encoding="utf-8", errors="ignore")))
        desc = str((d or {}).get("description", ""))[:200]
        out.append(f"skill:{sk.parent.name}:{desc}")
    return out


def unshippable():
    """Skill có frontmatter YAML HỎNG → CLI drop im lặng → không bao giờ tới người dùng."""
    bad = []
    for sk in sorted((ROOT / "skills").glob("*/SKILL.md")):
        d, err = _parse(_frontmatter(sk.read_text(encoding="utf-8", errors="ignore")))
        if err:
            bad.append((sk.parent.name, err))
        elif d is not None and not str(d.get("description", "")).strip():
            bad.append((sk.parent.name, "thiếu description"))
    return bad


def _rules():
    pol = ROOT / "harness" / "poc-vendor-neutral" / "policy.yaml"
    if not pol.exists():
        return []
    ids = sorted(set(re.findall(r"id:\s*(R\d+)", pol.read_text(encoding="utf-8"))),
                 key=lambda r: int(r[1:]))
    return [f"rule:{r}" for r in ids]


def _engines():
    out = []
    for d in ("harness/scripts", "llmwiki/.claude/hooks"):
        base = ROOT / d
        if base.is_dir():
            out += [f"engine:{d}/{p.name}" for p in sorted(base.iterdir())
                    if p.suffix in (".py", ".sh") and not p.name.startswith(".")]
    return out


def surface():
    return _skills() + _rules() + _engines()


def surface_sha():
    return hashlib.sha256("\n".join(surface()).encode("utf-8")).hexdigest()[:16]


def _load():
    return json.loads(VERSION_JSON.read_text(encoding="utf-8")) if VERSION_JSON.exists() else {}


def check():
    bad = unshippable()
    if bad:
        print("capability-stamp: SKILL SẼ BỊ DROP IM LẶNG — không bao giờ tới người dùng:",
              file=sys.stderr)
        for n, err in bad:
            print(f"    ✗ {n}: frontmatter {err}", file=sys.stderr)
        print("  CLI `skills` bỏ qua skill có frontmatter YAML hỏng, KHÔNG báo lỗi → skill không vào\n"
              "  global → không vào CAPABILITIES.md → user vĩnh viễn không biết năng lực đó tồn tại.\n"
              "  → Thường do `description:` inline chứa ': ' chưa quote. Sửa bằng block gấp dòng:\n"
              "        description: >-\n          <dòng 1>\n          <dòng 2>", file=sys.stderr)
        return 1
    d = _load()
    have, want = d.get("capability_sha"), surface_sha()
    if have == want:
        print(f"capability-stamp: OK (sha {want}, {len(surface())} mục bề mặt)")
        return 0
    if have is None:
        print(f"capability-stamp: CHƯA ĐÓNG DẤU — bề mặt năng lực chưa từng được ghi.\n"
              f"  → python3 harness/scripts/capability-stamp.py --update", file=sys.stderr)
        return 1
    print(f"capability-stamp: BỀ MẶT NĂNG LỰC ĐÃ ĐỔI mà version CHƯA BUMP\n"
          f"  ghi trong version.json: {have}\n  thực tế trên đĩa       : {want}\n"
          f"  → downstream sẽ so {d.get('template_version')} == {d.get('template_version')} và tưởng mình CURRENT,\n"
          f"    nên KHÔNG BAO GIỜ biết có chức năng mới. Bump đi:\n"
          f"  → python3 harness/scripts/capability-stamp.py --update", file=sys.stderr)
    return 1


def update():
    d = _load()
    old_v = str(d.get("template_version", "0.0.0"))
    parts = old_v.split(".")
    if len(parts) == 3 and parts[2].isdigit():
        new_v = f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"
    else:
        new_v = "1.0.0"
    d["template_version"] = new_v
    d["capability_sha"] = surface_sha()
    d["capability_count"] = len(surface())
    VERSION_JSON.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"capability-stamp: {old_v} → {new_v}  (sha {d['capability_sha']}, {d['capability_count']} mục)")
    print("  downstream giờ sẽ thấy BEHIND và biết phải /harness-update.")
    return 0


def self_test():
    """Bề mặt đổi thì sha PHẢI đổi — nếu không, cổng là đồ trang trí."""
    base = surface_sha()
    faked = hashlib.sha256("\n".join(surface() + ["skill:brand-new-skill:làm việc mới"]).encode()).hexdigest()[:16]
    ok = base != faked and len(surface()) > 0
    print("capability-stamp self-test:", "PASS" if ok else "FAIL",
          f"(bề mặt {len(surface())} mục; thêm 1 skill → sha đổi: {base} → {faked})")
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(self_test() if "--self-test" in a else update() if "--update" in a else check())
