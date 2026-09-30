#!/usr/bin/env python3
"""sync-kit — đẩy một ui-kit đã PASS lên kho kit PRIVATE (mặc định Rheinmir/ui-kits), có id chống trùng + v1, v2, v3.

GH#186 + GH#187 (hướng A): kho kit là repo PRIVATE riêng, nên mọi kit đều sync — kể cả kit của repo riêng tư
và kit rút từ site bên thứ ba (RULE-09 vẫn giữ: kit không nhúng ảnh/logo/nội dung có bản quyền).
Script TỪ CHỐI push nếu kho đích không PRIVATE — lộ token/component của dự án riêng là không lấy lại được.

Bố cục kho:
  registry.json               { "<id>": {"source": "...", "latest": N} }
  README.md                   bảng kit (sinh từ registry — kho private nên xem qua GitHub UI)
  <id>/manifest.json          {"id", "versions": [{v, hash, date, source_commit|source_url, skill_version, file}]}
  <id>/vN/index.html          bất biến, không bao giờ ghi đè
  <id>/latest/index.html      bản sao của vN mới nhất

Dùng:
  python3 sync-kit.py <kit.html> --source <thư mục repo | URL>   [--id <id>] [--repo owner/name] [--dry-run]
  UI_KIT_SYNC=0 → bỏ qua toàn bộ. UI_KIT_SYNC_REPO=owner/name → đổi kho đích.
Lỗi mạng/quyền → in "chưa sync, lý do …", rc 0: kit local vẫn là kết quả hợp lệ của skill.
"""
import argparse, datetime, hashlib, json, os, re, subprocess, sys
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_REPO = "Rheinmir/ui-kits"
CACHE = Path(os.environ.get("UI_KIT_SYNC_CACHE", Path.home() / ".cache/overstack/ui-kits"))
META_RE = re.compile(r'\s*<meta name="ui-kit-(?:id|generated)"[^>]*>', re.I)


def sh(*a, cwd=None, check=True):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True, check=check).stdout.strip()


def kit_id(source: str) -> str:
    """URL → host bỏ www, chấm → gạch. Thư mục → <owner>-<repo> từ remote origin, không có remote → <tên>-local."""
    if re.match(r"https?://", source):
        host = urlparse(source).hostname or ""
        return re.sub(r"^www\.", "", host).replace(".", "-").lower()
    try:
        url = sh("git", "remote", "get-url", "origin", cwd=source)
    except (subprocess.CalledProcessError, FileNotFoundError, NotADirectoryError):
        url = ""
    m = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?/?$", url)
    if m:
        return f"{m.group(1)}-{m.group(2)}".lower()
    return re.sub(r"[^a-z0-9]+", "-", Path(source).resolve().name.lower()).strip("-") + "-local"


def kit_hash(html: str) -> str:
    """sha256 sau khi bỏ meta ui-kit-id/generated — gắn id hay dấu thời gian không được sinh phiên bản mới."""
    return hashlib.sha256(META_RE.sub("", html).encode()).hexdigest()


def stamp_id(html: str, kid: str) -> str:
    html = META_RE.sub("", html)
    tag = f'<meta name="ui-kit-id" content="{kid}">'
    return re.sub(r"(<head[^>]*>)", r"\1\n" + tag, html, count=1, flags=re.I) if re.search(r"<head", html, re.I) else tag + "\n" + html


def next_version(manifest: dict, h: str):
    """None = không đổi so với bản mới nhất; ngược lại số phiên bản kế (max(v)+1). Chỉ so với bản MỚI NHẤT:
    quay về nội dung cũ vẫn là một phiên bản mới (lịch sử chỉ tăng)."""
    vs = manifest.get("versions", [])
    if vs and max(vs, key=lambda x: x["v"])["hash"] == h:
        return None
    return max((x["v"] for x in vs), default=0) + 1


def write_version(root: Path, kid: str, html: str, source: str, meta: dict):
    """Ghi vN + latest + manifest + registry + README vào bản clone. Trả (v, None) hoặc (None, v_cũ) khi không đổi."""
    d = root / kid
    mf = d / "manifest.json"
    manifest = json.loads(mf.read_text()) if mf.is_file() else {"id": kid, "versions": []}
    h = kit_hash(html)
    v = next_version(manifest, h)
    if v is None:
        return None, max(x["v"] for x in manifest["versions"])
    body = stamp_id(html, kid)
    for sub in (f"v{v}", "latest"):
        (d / sub).mkdir(parents=True, exist_ok=True)
        (d / sub / "index.html").write_text(body)
    manifest["versions"].append({"v": v, "hash": h, "date": datetime.date.today().isoformat(),
                                 **meta, "file": f"v{v}/index.html"})
    mf.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    rf = root / "registry.json"
    reg = json.loads(rf.read_text()) if rf.is_file() else {}
    reg[kid] = {"source": source, "latest": v}
    rf.write_text(json.dumps(dict(sorted(reg.items())), ensure_ascii=False, indent=2) + "\n")
    rows = "\n".join(f"| `{k}` | {r['source']} | [v{r['latest']}]({k}/latest/index.html) | [manifest]({k}/manifest.json) |"
                     for k, r in sorted(reg.items()))
    (root / "README.md").write_text("# ui-kits\n\nKit sinh bởi `/ui-kit-from-code` (overstack), tự sync bằng "
                                    "`references/sync-kit.py`. Kho PRIVATE — mỗi phiên bản bất biến ở `<id>/vN/`.\n\n"
                                    "| id | nguồn | mới nhất | lịch sử |\n|---|---|---|---|\n" + rows + "\n")
    return v, None


def source_meta(source: str) -> dict:
    if re.match(r"https?://", source):
        return {"source_url": source}
    try:
        return {"source_commit": sh("git", "rev-parse", "HEAD", cwd=source)}
    except Exception:
        return {"source_commit": None}


def skill_version() -> str:
    m = re.search(r'contract-version:\s*"([^"]+)"', (Path(__file__).resolve().parents[1] / "SKILL.md").read_text())
    return m.group(1) if m else "?"


def sync(kit: Path, source: str, repo: str, dry: bool, kid: str = "") -> int:
    vis = sh("gh", "repo", "view", repo, "--json", "visibility", "-q", ".visibility")
    if vis != "PRIVATE":
        print(f"✗ chưa sync: kho {repo} là {vis or '?'}, không phải PRIVATE — từ chối đẩy kit (GH#187)")
        return 0
    clone = CACHE / repo.replace("/", "__")
    if not (clone / ".git").is_dir():
        clone.parent.mkdir(parents=True, exist_ok=True)
        sh("gh", "repo", "clone", repo, str(clone), "--", "-q")
    kid, html = kid or kit_id(source), kit.read_text()
    meta = {**source_meta(source), "skill_version": skill_version()}
    for attempt in range(3):
        if sh("git", "rev-parse", "--verify", "-q", "HEAD", cwd=clone, check=False):
            sh("git", "fetch", "-q", "origin", cwd=clone)
            sh("git", "reset", "-q", "--hard", "@{u}", cwd=clone)   # cache của script, không phải bản làm việc của ai
        v, old = write_version(clone, kid, html, source, meta)
        if v is None:
            print(f"= {kid}: không đổi so với v{old} — không tạo phiên bản mới")
            return 0
        if dry:
            print(f"(dry-run) {kid}: sẽ đẩy v{v} → {repo}")
            sh("git", "checkout", "-q", "--", ".", cwd=clone, check=False)
            sh("git", "clean", "-qfd", cwd=clone, check=False)
            return 0
        sh("git", "add", "-A", cwd=clone)
        sh("git", "commit", "-qm", f"kit({kid}): v{v}", cwd=clone)
        if subprocess.run(["git", "push", "-q", "origin", "HEAD"], cwd=clone, capture_output=True).returncode == 0:
            print(f"✓ {kid}: v{v} → https://github.com/{repo}/tree/HEAD/{kid}/v{v}")
            return 0
        sh("git", "reset", "-q", "--hard", "HEAD~1", cwd=clone)   # máy khác vừa đẩy cùng số → pull lại, tính lại
    print(f"✗ chưa sync: push {repo} bị từ chối 3 lần liên tiếp")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("kit", type=Path)
    ap.add_argument("--source", required=True, help="thư mục repo nguồn hoặc URL site")
    ap.add_argument("--repo", default=os.environ.get("UI_KIT_SYNC_REPO", DEFAULT_REPO))
    ap.add_argument("--id", default="", help="đặt id tay khi nguồn không suy ra được (vd app sau đăng nhập, không rõ host)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if os.environ.get("UI_KIT_SYNC") == "0":
        print("UI_KIT_SYNC=0 — bỏ qua sync")
        return 0
    try:
        return sync(a.kit, a.source, a.repo, a.dry_run, a.id)
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"✗ chưa sync, lý do: {getattr(e, 'stderr', '') or e}".strip())
        return 0


if __name__ == "__main__":
    sys.exit(main())
