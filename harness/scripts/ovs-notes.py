#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ovs-notes — VIEWER release-notes overstack tức thì (kiểu /release-notes của Claude CLI).

Sống ở harness/scripts/ nên TRAVEL xuống mọi project cài overstack (council-advisory 030726:
fdk/tools KHÔNG travel → path gãy câm downstream; harness/scripts travel → path sống sót clone).

Hợp đồng council (Rams+Taleb):
  • Tên `ovs-` = LỜI HỨA "của overstack" → MẶC ĐỊNH xem changelog FRAMEWORK (Rheinmir/setup),
    dù bạn đang đứng ở project nào. Không suy nguồn từ CWD (chống mạo danh).
  • `--here` = xem release của PROJECT hiện tại (git tag local, offline-ok).
  • NHÃN NGUỒN bắt buộc ở header mỗi lần in — không bao giờ để release framework mạo danh project.
  • FAIL TO LỚN (via-negativa): gh vắng/chưa login/offline → in rõ "không xác nhận được" + exit≠0;
    KHÔNG giả vờ danh sách rỗng (rỗng ≠ không có bản).

Dùng:
  ovs-notes.py                 # changelog OVERSTACK framework (mặc định) — list newest-first
  ovs-notes.py latest          # notes bản framework mới nhất
  ovs-notes.py --here          # release của PROJECT hiện tại (git tag local)
  ovs-notes.py --repo o/n      # release của một repo GitHub khác
  ovs-notes.py --json          # máy đọc
Self-contained stdlib.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRAMEWORK_REPO = "Rheinmir/setup"          # nguồn chân lý changelog overstack (đóng đinh theo tên ovs-)


def sh(args, timeout=20):
    try:
        r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or ""), (r.stderr or "")
    except FileNotFoundError:
        return 127, "", "gh-not-found"
    except Exception as e:
        return 127, "", str(e)


def _semver_key(tag):
    m = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag or "")
    return tuple(int(x) for x in m.groups()) if m else (-1, -1, -1)


class NotesError(Exception):
    """gh vắng/offline/repo lỗi — KHÔNG được nuốt thành rỗng (Taleb via-negativa)."""


def _here_slug():
    rc, out, _ = sh(["git", "remote", "get-url", "origin"])
    if rc == 0 and out.strip():
        m = re.search(r"[/:]([^/:]+/[^/]+?)(?:\.git)?\s*$", out.strip())
        if m:
            return m.group(1)
    return "(repo local)"


def releases_remote(repo):
    """gh release list -R <repo> → rows; lỗi → NotesError (không nuốt thành rỗng)."""
    rc, out, err = sh(["gh", "release", "list", "-R", repo, "--limit", "100"])
    if rc != 0:
        if "gh-not-found" in err or rc == 127:
            raise NotesError(f"`gh` (GitHub CLI) không có/không chạy được — không xác nhận được release của {repo}.")
        raise NotesError(f"không đọc được release của {repo} (gh lỗi: {err.strip()[:120] or 'offline/chưa login?'}).")
    rows = []
    for ln in out.splitlines():
        p = ln.split("\t")
        if len(p) >= 3:
            title, _mark, tag, date = (p + ["", "", "", ""])[:4]
            rows.append((tag.strip(), date.strip()[:10], title.strip() or tag.strip()))
    rows.sort(key=lambda r: _semver_key(r[0]), reverse=True)
    return rows


def releases_here():
    """git tag của repo hiện tại (offline-ok)."""
    rc, out, _ = sh(["git", "tag", "-l", "--sort=-creatordate",
                     "--format=%(refname:short)\t%(creatordate:short)\t%(contents:subject)"])
    rows = []
    for ln in out.splitlines():
        p = ln.split("\t")
        if p and p[0]:
            rows.append((p[0], (p[1] if len(p) > 1 else ""), (p[2] if len(p) > 2 else p[0])))
    rows.sort(key=lambda r: _semver_key(r[0]), reverse=True)
    return rows


def body_remote(repo, tag):
    rc, out, _ = sh(["gh", "release", "view", tag, "-R", repo, "--json", "body,name,publishedAt"])
    if rc == 0 and out.strip():
        try:
            d = json.loads(out)
            head = f"# {d.get('name') or tag}"
            if d.get("publishedAt"):
                head += f"   ({d['publishedAt'][:10]})"
            return head + "\n\n" + (d.get("body") or "(không có body)")
        except ValueError:
            pass
    raise NotesError(f"không đọc được notes của {tag} @ {repo} (gh offline/chưa login?).")


def body_here(tag):
    rc, out, _ = sh(["git", "tag", "-l", "--format=%(contents)", tag])
    if rc == 0 and out.strip():
        return f"# {tag}\n\n{out.strip()}"
    return f"# {tag}\n\n(tag không có annotation — thử `git show {tag}`)"


def resolve(ref, rows):
    if ref in ("latest", "-l", "--latest") and rows:
        return rows[0][0]
    for tag, _d, _t in rows:
        if ref in (tag, tag.lstrip("v"), "v" + ref):
            return tag
    return None


def main():
    argv = sys.argv[1:]
    here = "--here" in argv
    repo = FRAMEWORK_REPO
    if "--repo" in argv:
        i = argv.index("--repo")
        if i + 1 < len(argv):
            repo = argv[i + 1]
    # nhãn nguồn BẮT BUỘC (chống mạo danh — Taleb)
    src_label = f"project hiện tại: {_here_slug()}" if here else f"overstack framework ({repo})"
    pos = [a for a in argv if not a.startswith("-") and a != repo]

    try:
        rows = releases_here() if here else releases_remote(repo)
    except NotesError as e:
        # via-negativa: nói TO "không xác nhận được", KHÔNG giả rỗng
        print(f"ovs-notes [{src_label}]: {e}\n  → rỗng KHÔNG nghĩa là không có bản. "
              f"Cài/login `gh` (hoặc dùng `--here` cho release project offline).", file=sys.stderr)
        return 3

    if "--json" in argv:
        print(json.dumps({"source": src_label,
                          "releases": [{"tag": t, "date": d, "title": ti} for t, d, ti in rows]},
                         ensure_ascii=False, indent=2))
        return 0
    if not rows:
        print(f"ovs-notes [{src_label}]: chưa có release nào.")
        return 0
    if pos:  # xem một bản
        tag = resolve(pos[0], rows)
        if not tag:
            print(f"ovs-notes [{src_label}]: không thấy bản '{pos[0]}'. Có: "
                  + ", ".join(t for t, _, _ in rows[:8]))
            return 1
        print(f"[nguồn: {src_label}]\n")
        print(body_here(tag) if here else body_remote(repo, tag))
        return 0
    # LIST
    print(f"release notes — nguồn: {src_label} (newest-first). Đọc một bản: `ovs-notes <version|latest>`"
          + ("" if here else "  ·  release project hiện tại: `ovs-notes --here`") + "\n")
    for tag, date, title in rows:
        print(f"  {tag:20} {date:12} {title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
