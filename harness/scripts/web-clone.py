#!/usr/bin/env python3
"""web-clone — save a page as ONE self-contained HTML (UI + resources), the SingleFile idea
(2026). Backs the /web-clone skill.

  inline HTML_FILE [--out FILE]   inline a LOCAL page's local CSS/JS/images into one file.
  url URL [--out FILE]            capture a live URL via the configured engine (single-file CLI
                                  / monolith) — falls back with guidance if none installed.
  --self-test                     deterministic local-resource inlining on a fixture (fdk-gate).

The ONE adapter = harness/web-clone.config.yaml (engine, *_cmd, preserve_interactions; flagged
verified=false). The local-resource inliner is deterministic, built now. A faithful live-URL
engine and JS-INTERACTION preservation are the unknowns; default 'builtin' inlines local pages.
"""
import base64
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_FALLBACK = {"verified": False, "engine": "builtin", "singlefile_cmd": "single-file",
             "monolith_cmd": "monolith", "embed_images": True, "preserve_interactions": "best-effort"}


def _config_file(root: Path) -> Path:
    return root / "harness" / "web-clone.config.yaml"


def load_config(root: Path) -> dict:
    cfg = dict(_FALLBACK)
    try:
        import yaml
        data = yaml.safe_load(_config_file(root).read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for k, v in data.items():
                if v is not None:
                    cfg[k] = v
    except Exception:
        pass
    return cfg


def _read_local(base: Path, ref: str):
    """Read a local resource referenced by the page (skip http/data URIs). None if not local."""
    if re.match(r"(?i)^(https?:|data:|//)", ref):
        return None
    p = (base / ref).resolve()
    try:
        if p.is_file():
            return p
    except Exception:
        pass
    return None


def inline(html_path: Path, cfg: dict) -> str:
    """Deterministic: inline local <link> CSS, <script src> JS, and (optionally) <img> as data URI."""
    base = html_path.resolve().parent
    s = html_path.read_text(encoding="utf-8", errors="replace")

    def css_repl(m):
        p = _read_local(base, m.group(1))
        if not p:
            return m.group(0)
        return "<style>\n" + p.read_text(encoding="utf-8", errors="replace") + "\n</style>"
    s = re.sub(r"(?is)<link[^>]*rel=[\"']stylesheet[\"'][^>]*href=[\"']([^\"']+)[\"'][^>]*>", css_repl, s)
    s = re.sub(r"(?is)<link[^>]*href=[\"']([^\"']+)[\"'][^>]*rel=[\"']stylesheet[\"'][^>]*>", css_repl, s)

    def js_repl(m):
        p = _read_local(base, m.group(1))
        if not p:
            return m.group(0)
        return "<script>\n" + p.read_text(encoding="utf-8", errors="replace") + "\n</script>"
    s = re.sub(r"(?is)<script[^>]*src=[\"']([^\"']+)[\"'][^>]*>\s*</script>", js_repl, s)

    if cfg.get("embed_images", True):
        def img_repl(m):
            p = _read_local(base, m.group(1))
            if not p:
                return m.group(0)
            mime = mimetypes.guess_type(str(p))[0] or "image/png"
            b64 = base64.b64encode(p.read_bytes()).decode("ascii")
            return m.group(0).replace(m.group(1), f"data:{mime};base64,{b64}")
        s = re.sub(r"(?is)<img[^>]*src=[\"']([^\"']+)[\"'][^>]*>", img_repl, s)
    return s


def capture_url(url: str, out: Path, cfg: dict) -> int:
    """Premium engine adapter: shell out to single-file CLI / monolith if available."""
    engine = str(cfg.get("engine", "builtin"))
    cmd = None
    if engine == "singlefile-cli" and shutil.which(cfg.get("singlefile_cmd", "single-file")):
        cmd = [cfg["singlefile_cmd"], url, str(out)]
    elif engine == "monolith" and shutil.which(cfg.get("monolith_cmd", "monolith")):
        cmd = [cfg["monolith_cmd"], url, "-o", str(out)]
    if not cmd:
        print(f"[web-clone] engine '{engine}' chưa cài (verified:false). Cài single-file CLI "
              f"(`npm i -g single-file-cli`) hoặc monolith (`cargo install monolith`), hoặc tải "
              f"trang về rồi `web-clone.py inline`.", file=sys.stderr)
        return 1
    try:
        subprocess.run(cmd, check=True, timeout=120)
        print(f"captured {url} → {out}"); return 0
    except Exception as exc:
        print(f"[web-clone] engine lỗi: {exc}", file=sys.stderr); return 1


def self_test() -> int:
    with tempfile.TemporaryDirectory() as d:
        base = Path(d)
        (base / "style.css").write_text("body{color:red}", encoding="utf-8")
        (base / "app.js").write_text("console.log(1)", encoding="utf-8")
        (base / "index.html").write_text(
            "<html><head><link rel='stylesheet' href='style.css'></head>"
            "<body>hi<script src='app.js'></script></body></html>", encoding="utf-8")
        out = inline(base / "index.html", _FALLBACK)
        ok = ("<style>" in out and "color:red" in out and "console.log(1)" in out
              and "href='style.css'" not in out and "src='app.js'" not in out)
    print("web-clone self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> None:
    args = sys.argv[1:]
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    out = None
    if "--out" in args:
        i = args.index("--out"); out = args[i + 1] if len(args) > i + 1 else None; del args[i:i + 2]
    if "--root" in args:
        i = args.index("--root"); root = Path(args[i + 1]); del args[i:i + 2]
    if "--self-test" in args:
        sys.exit(self_test())
    cfg = load_config(root)
    if args and args[0] == "inline":
        if len(args) < 2:
            print("usage: web-clone.py inline HTML_FILE [--out FILE]", file=sys.stderr); sys.exit(2)
        html = inline(Path(args[1]), cfg)
        if out:
            Path(out).write_text(html, encoding="utf-8"); print(f"wrote {out} ({len(html)} chars)")
        else:
            print(html)
        return
    if args and args[0] == "url":
        if len(args) < 2:
            print("usage: web-clone.py url URL [--out FILE]", file=sys.stderr); sys.exit(2)
        sys.exit(capture_url(args[1], Path(out or "clone.html"), cfg))
    print(__doc__)


if __name__ == "__main__":
    main()
