#!/usr/bin/env python3
"""list-subrepos — discovery subrepo của workspace cho R12 v3 (dùng chung sweep + installer).

Nguồn ưu tiên: <root>/.harness-workspace.yaml. Thiếu → fallback find .git (maxdepth N) +
lọc "harnessed-repo" (có harness/ hoặc llmwiki/) để bỏ deps/vendored lạ.

Output: mỗi dòng `<abs-path>\\t<target|watch>`.
  target = repo ta sẽ ghi/đẩy → behind thì CHẶN fan-out.
  watch  = chỉ cảnh báo.

Manifest schema (.harness-workspace.yaml):
  subrepos: ["."­, "sub/a", ...]     # bắt buộc nếu dùng manifest
  targets:  ["."]                    # optional, default = toàn bộ subrepos
  exclude:  ["**/node_modules/**"]   # optional, áp cho fallback find
  maxdepth: 3                        # optional (fallback find)
"""
import fnmatch
import os
import pathlib
import sys

PRUNE = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next"}


def _ok_git(repo: pathlib.Path) -> bool:
    return (repo / ".git").exists()  # dir HOẶC file (worktree/submodule)


def from_manifest(path: pathlib.Path, root: pathlib.Path):
    import yaml
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    subs = data.get("subrepos") or []
    targets = set(data.get("targets") or subs)  # default: tất cả là target
    out = []
    for s in subs:
        ap = (root / s).resolve()
        if _ok_git(ap):
            out.append((str(ap), "target" if s in targets else "watch"))
    return out


def from_find(root: pathlib.Path, maxdepth: int, exclude):
    out, seen = [], set()
    root = root.resolve()
    for dirpath, dirnames, _ in os.walk(root):
        rel = pathlib.Path(dirpath).relative_to(root)
        depth = 0 if str(rel) == "." else len(rel.parts)
        if depth > maxdepth:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in PRUNE]
        repo = pathlib.Path(dirpath)
        if _ok_git(repo) and str(repo) not in seen:
            relstr = str(repo.relative_to(root)) if repo != root else "."
            if any(fnmatch.fnmatch(relstr, g) or fnmatch.fnmatch(str(repo), g) for g in exclude):
                continue
            harnessed = (repo / "harness").is_dir() or (repo / "llmwiki").is_dir()
            out.append((str(repo), "target" if harnessed else "watch"))
            seen.add(str(repo))
    return out


def main():
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else os.getcwd()).resolve()
    manifest = root / ".harness-workspace.yaml"
    try:
        if manifest.is_file():
            rows = from_manifest(manifest, root)
        else:
            import yaml  # noqa: F401 — đảm bảo pyyaml có; nếu thiếu → fail-open rỗng
            rows = from_find(root, maxdepth=3, exclude=[])
    except ImportError:
        sys.stderr.write("list-subrepos: thiếu pyyaml — fail-open (rỗng)\n")
        return
    except Exception as e:  # manifest hỏng → fail-open
        sys.stderr.write(f"list-subrepos: lỗi đọc workspace ({e}) — fail-open\n")
        return
    for path, kind in rows:
        print(f"{path}\t{kind}")


if __name__ == "__main__":
    main()
