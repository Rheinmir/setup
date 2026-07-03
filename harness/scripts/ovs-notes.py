#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ovs-notes — VIEWER release-notes overstack tức thì (kiểu /release-notes của Claude CLI).

Gõ là hiện NGAY danh sách các bản (newest-first) để chọn + đọc. READ-ONLY, không side-effect
(khác /ship = quy trình CẮT release). Nguồn sự thật: GH release body (giàu) → fallback annotated
git tag. Self-contained stdlib; gh không có/không login → tự lùi về git tag, không chết.

Dùng:
  ovs-notes.py               # liệt kê mọi bản: vX.Y.Z  <ngày>  <tiêu đề>  (newest-first)
  ovs-notes.py latest        # in đầy đủ notes của bản mới nhất
  ovs-notes.py v1.0.5        # in đầy đủ notes của một bản
  ovs-notes.py --json        # máy đọc (cho skill dựng picker)
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sh(args, timeout=20):
    try:
        r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or ""), (r.stderr or "")
    except Exception:
        return 127, "", ""


def _semver_key(tag):
    m = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag or "")
    return tuple(int(x) for x in m.groups()) if m else (-1, -1, -1)


def releases():
    """List (tag, date, title) newest-first. GH release trước; thiếu thì git tag."""
    rc, out, _ = sh(["gh", "release", "list", "--limit", "100"])
    rows = []
    if rc == 0 and out.strip():
        for ln in out.splitlines():
            parts = ln.split("\t")
            if len(parts) >= 3:
                title, _mark, tag, date = (parts + ["", "", "", ""])[:4]
                rows.append((tag.strip(), date.strip()[:10], title.strip() or tag.strip()))
    if not rows:  # fallback: annotated git tags
        rc, out, _ = sh(["git", "tag", "-l", "--sort=-creatordate",
                         "--format=%(refname:short)\t%(creatordate:short)\t%(contents:subject)"])
        for ln in out.splitlines():
            p = ln.split("\t")
            if p and p[0]:
                rows.append((p[0], (p[1] if len(p) > 1 else ""), (p[2] if len(p) > 2 else p[0])))
    # ưu tiên sắp theo semver desc (tag không-semver xuống cuối, giữ thứ tự nguồn)
    rows.sort(key=lambda r: _semver_key(r[0]), reverse=True)
    return rows


def body(tag):
    """Nội dung đầy đủ một bản: GH release body → fallback git tag annotation."""
    rc, out, _ = sh(["gh", "release", "view", tag, "--json", "body,name,publishedAt"])
    if rc == 0 and out.strip():
        try:
            d = json.loads(out)
            head = f"# {d.get('name') or tag}"
            if d.get("publishedAt"):
                head += f"   ({d['publishedAt'][:10]})"
            return head + "\n\n" + (d.get("body") or "(không có body)")
        except ValueError:
            pass
    rc, out, _ = sh(["git", "tag", "-l", "--format=%(contents)", tag])
    if rc == 0 and out.strip():
        return f"# {tag}\n\n{out.strip()}"
    return f"# {tag}\n\n(không tìm thấy notes — thử `gh release view {tag}`)"


def resolve(ref, rows):
    if ref in ("latest", "-l", "--latest") and rows:
        return rows[0][0]
    for tag, _d, _t in rows:
        if ref == tag or ref == tag.lstrip("v") or ("v" + ref) == tag:
            return tag
    return None


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    rows = releases()
    if "--json" in sys.argv:
        print(json.dumps([{"tag": t, "date": d, "title": ti} for t, d, ti in rows], ensure_ascii=False, indent=2))
        return 0
    if not rows:
        print("ovs-notes: chưa có release nào (git tag / GH release trống).")
        return 0
    if args:  # xem một bản
        tag = resolve(args[0], rows)
        if not tag:
            print(f"ovs-notes: không thấy bản '{args[0]}'. Các bản có: "
                  + ", ".join(t for t, _, _ in rows[:8]))
            return 1
        print(body(tag))
        return 0
    # mặc định: LIST để chọn+đọc
    print("overstack — release notes (newest-first). Đọc một bản: `ovs-notes <version|latest>`\n")
    for tag, date, title in rows:
        print(f"  {tag:20} {date:12} {title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
