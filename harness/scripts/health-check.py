#!/usr/bin/env python3
"""L4 eval (0 token): sức khỏe PATTERN sync — version vs remote + drift + completeness.

So "pattern chuẩn" (tập file trong .template-manifest.json) giữa 3 mốc:
  1. local disk  ↔  harness/version.json   → DRIFT  (file đã bị sửa kể từ lần sync/generate)
  2. local       ↔  remote version.json    → BEHIND (remote có bản mới, cần /sync-template)
  3. manifest    ↔  local disk             → MISSING (pattern khai báo nhưng thiếu file)

Usage:
  health-check.py [--root .] [--manifest .template-manifest.json]
                  [--version-file harness/version.json] [--branch orca]
                  [--offline] [--remote-timeout 4] [--json] [--quiet]
                  [--update] [--bump major|minor|patch]
                  [--fail-on behind,drift,missing]

  --update : sinh/refresh version.json từ file trên disk (hash lại toàn bộ pattern).
             Dùng khi tạo file lần đầu, hoặc sau mỗi downstream /sync-template.

Output: JSON ra stdout (mặc định human summary). Exit 2 nếu nhóm trong --fail-on có vi phạm.
Lỗi mạng KHÔNG fail (fail-open): remote_reachable=false, vẫn báo cáo phần local.
"""
import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

SCHEMA = 1
SELF = "harness/version.json"  # không tự hash chính mình
# File "sống" theo từng project (mỗi project tự sửa) → loại khỏi fingerprint để
# không báo drift giả. Vẫn ở trong manifest để seed lần đầu.
VOLATILE = {
    "llmwiki/wiki/index.md",
    "llmwiki/wiki/log.md",
    "llmwiki/wiki/active-context.md",
    "llmwiki/wiki/decisions.md",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]


def manifest_patterns(manifest: Path) -> list[str]:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    return [p for p in data.get("includes", []) if p != SELF and p not in VOLATILE]


def manifest_remote(manifest: Path) -> str:
    return json.loads(manifest.read_text(encoding="utf-8")).get("remote", "")


def owner_repo(remote: str):
    m = re.search(r"github\.com[:/]+([^/]+)/([^/.]+)", remote or "")
    return (m.group(1), m.group(2)) if m else (None, None)


def git_commit(root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=root,
            capture_output=True, text=True, timeout=10,
        ).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def disk_hashes(root: Path, patterns: list[str]) -> dict:
    out = {}
    for rel in patterns:
        f = root / rel
        if f.is_file():
            out[rel] = sha(f)
    return out


def fetch_remote_version(remote: str, branch: str, timeout: int):
    owner, repo = owner_repo(remote)
    if not owner:
        return None, "remote URL không parse được owner/repo"
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{SELF}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "llmwiki-health-check"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code} khi GET {url}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def bump_version(v: str, part: str) -> str:
    try:
        a, b, c = (int(x) for x in v.split("."))
    except Exception:
        a, b, c = 0, 0, 0
    if part == "major":
        return f"{a + 1}.0.0"
    if part == "minor":
        return f"{a}.{b + 1}.0"
    return f"{a}.{b}.{c + 1}"


def cmp_semver(a: str, b: str) -> int:
    def t(v):
        try:
            return tuple(int(x) for x in v.split("."))
        except Exception:
            return (0, 0, 0)
    ta, tb = t(a), t(b)
    return (ta > tb) - (ta < tb)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--manifest", default=".template-manifest.json")
    ap.add_argument("--version-file", default="harness/version.json")
    ap.add_argument("--branch", default="orca")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--remote-timeout", type=int, default=4)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="chỉ in khi có vấn đề")
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--bump", choices=["major", "minor", "patch"])
    ap.add_argument("--fail-on", default="")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    manifest = root / args.manifest
    vfile = root / args.version_file
    if not manifest.is_file():
        print(f"manifest không tồn tại: {manifest}", file=sys.stderr)
        sys.exit(1)

    patterns = manifest_patterns(manifest)
    remote = manifest_remote(manifest)
    cur = disk_hashes(root, patterns)
    missing = sorted(p for p in patterns if p not in cur)

    # ---------- --update: sinh/refresh version.json ----------
    if args.update:
        old = json.loads(vfile.read_text(encoding="utf-8")) if vfile.is_file() else {}
        ver = old.get("template_version", "1.0.0")
        if args.bump:
            ver = bump_version(ver, args.bump)
        doc = {
            "schema": SCHEMA,
            "template_version": ver,
            "remote": remote,
            "branch": args.branch,
            "generated_at": datetime.date.today().isoformat(),
            "generated_commit": git_commit(root),
            "pattern_count": len(cur),
            "patterns": dict(sorted(cur.items())),
        }
        vfile.parent.mkdir(parents=True, exist_ok=True)
        vfile.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[health-check] version.json: v{ver}, {len(cur)} pattern, commit {doc['generated_commit']}")
        if missing:
            print(f"[health-check] ⚠ {len(missing)} pattern thiếu file (không hash): {', '.join(missing[:5])}"
                  + (" …" if len(missing) > 5 else ""))
        sys.exit(0)

    # ---------- đọc version.json local ----------
    local = json.loads(vfile.read_text(encoding="utf-8")) if vfile.is_file() else {}
    local_ver = local.get("template_version")
    local_pat = local.get("patterns", {})

    # DRIFT: disk khác hash đã ghi trong version.json
    drift = sorted(p for p, h in cur.items() if p in local_pat and local_pat[p] != h)
    untracked = sorted(p for p in cur if p not in local_pat) if local_pat else []

    # ---------- remote ----------
    remote_doc, remote_err, behind = None, None, []
    remote_reachable = False
    if not args.offline:
        remote_doc, remote_err = fetch_remote_version(remote, args.branch, args.remote_timeout)
        remote_reachable = remote_doc is not None
    if remote_doc:
        rpat = remote_doc.get("patterns", {})
        base = local_pat or cur
        for p, rh in rpat.items():
            if base.get(p) != rh:
                behind.append(p)
        behind.sort()
        for p in (set(base) - set(rpat)):
            pass  # local có pattern remote không có → upstream candidate (không tính behind)

    version_behind = bool(remote_doc) and bool(local_ver) and remote_doc.get("template_version") \
        and cmp_semver(local_ver, remote_doc["template_version"]) < 0

    status = "ok"
    if missing or behind or version_behind:
        status = "needs-sync"
    elif drift:
        status = "drift"

    report = {
        "status": status,
        "date": datetime.date.today().isoformat(),
        "local_version": local_ver,
        "remote_version": remote_doc.get("template_version") if remote_doc else None,
        "remote_reachable": remote_reachable,
        "remote_error": remote_err,
        "branch": args.branch,
        "pattern_count": len(patterns),
        "version_behind": bool(version_behind),
        "behind": behind,           # pattern remote mới hơn local → cần downstream sync
        "drift": drift,             # pattern local đã sửa kể từ lần sync
        "untracked": untracked,     # pattern trên disk chưa ghi vào version.json
        "missing": missing,         # pattern khai báo trong manifest nhưng thiếu file
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif not (args.quiet and status == "ok"):
        icon = {"ok": "✓", "drift": "✎", "needs-sync": "⟳"}[status]
        print(f"{icon} pattern-health: {status.upper()}  (local v{local_ver or '?'}"
              + (f" · remote v{report['remote_version']}" if remote_reachable else " · remote: offline")
              + f" · {len(patterns)} pattern)")
        if missing:
            print(f"  ⚠ thiếu {len(missing)} file: {', '.join(missing[:6])}" + (" …" if len(missing) > 6 else ""))
        if behind:
            print(f"  ⟳ {len(behind)} pattern cũ hơn remote → chạy /sync-template (downstream): "
                  + ", ".join(b.split('/')[-1] for b in behind[:6]) + (" …" if len(behind) > 6 else ""))
        if version_behind:
            print(f"  ⟳ version local v{local_ver} < remote v{report['remote_version']}")
        if drift:
            print(f"  ✎ {len(drift)} pattern đã sửa local (cân nhắc upstream hoặc revert): "
                  + ", ".join(d.split('/')[-1] for d in drift[:6]) + (" …" if len(drift) > 6 else ""))
        if not remote_reachable and not args.offline:
            print(f"  ℹ remote không tới được ({remote_err}) — chỉ kiểm tra local.")
        if status == "ok":
            print("  pattern đã đủ và khớp remote — không cần sync.")

    groups = {g.strip() for g in args.fail_on.split(",") if g.strip()}
    failed = (("behind" in groups and (behind or version_behind))
              or ("drift" in groups and drift)
              or ("missing" in groups and missing))
    sys.exit(2 if failed else 0)


if __name__ == "__main__":
    main()
