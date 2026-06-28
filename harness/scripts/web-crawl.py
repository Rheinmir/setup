#!/usr/bin/env python3
"""web-crawl — fetch a web page and convert it to LLM-ready MARKDOWN (2026 trend: feed models
markdown, not raw HTML — 5-10x fewer tokens). Backs the /web-crawl skill.

  fetch URL [--out FILE]    fetch the URL (builtin urllib) and print/save markdown.
  md FILE                   convert a local HTML file to markdown (no network).
  --self-test               deterministic HTML→markdown on a fixture (fdk-gate BNAL self-test).

The ONE adapter = harness/web-crawl.config.yaml (backend, api_key_env, endpoint — verified:false).
The HTML→markdown converter + urllib fetch are deterministic, built now. A premium backend
(Firecrawl/Crawl4AI/Jina) is the unknown; default 'builtin' works offline with no key. In an
agent session the skill may instead use the in-session WebFetch tool (richer JS rendering).
"""
import html as _html
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

_FALLBACK = {"verified": False, "backend": "builtin", "api_key_env": "FIRECRAWL_API_KEY",
             "max_bytes": 2000000, "default_output_dir": "raw"}


def _config_file(root: Path) -> Path:
    return root / "harness" / "web-crawl.config.yaml"


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


def html_to_markdown(html: str) -> str:
    """Deterministic HTML→markdown: drop script/style, headings, links, lists, code, paragraphs."""
    s = html or ""
    s = re.sub(r"(?is)<(script|style|noscript|template)[^>]*>.*?</\1>", "", s)
    s = re.sub(r"(?is)<!--.*?-->", "", s)
    for i in range(6, 0, -1):                       # h6..h1
        s = re.sub(rf"(?is)<h{i}[^>]*>(.*?)</h{i}>", lambda m, n=i: "\n" + "#" * n + " " + m.group(1).strip() + "\n", s)
    s = re.sub(r"(?is)<a[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", r"[\2](\1)", s)
    s = re.sub(r"(?is)<li[^>]*>(.*?)</li>", r"\n- \1", s)
    s = re.sub(r"(?is)<(strong|b)[^>]*>(.*?)</\1>", r"**\2**", s)
    s = re.sub(r"(?is)<(em|i)[^>]*>(.*?)</\1>", r"*\2*", s)
    s = re.sub(r"(?is)<code[^>]*>(.*?)</code>", r"`\1`", s)
    s = re.sub(r"(?is)<(p|br|div|tr|/h[1-6])[^>]*>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", "", s)               # strip remaining tags
    s = _html.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n[ \t]+", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip() + "\n"


def fetch(url: str, cfg: dict) -> str:
    """builtin backend: urllib fetch → markdown. Premium backends are the (un-wired) adapter."""
    backend = str(cfg.get("backend", "builtin"))
    if backend != "builtin":
        key = os.environ.get(cfg.get("api_key_env", ""))
        if not key:
            print(f"[web-crawl] backend '{backend}' chưa có key ({cfg.get('api_key_env')}) — "
                  f"rơi về builtin. (verified:false: wire backend ở config.)", file=sys.stderr)
    req = Request(url, headers={"User-Agent": "overstack-web-crawl/1.0"})
    with urlopen(req, timeout=20) as r:               # noqa: S310 (explicit http(s) tool)
        raw = r.read(int(cfg.get("max_bytes", 2000000)))
    enc = "utf-8"
    return html_to_markdown(raw.decode(enc, errors="replace"))


def self_test() -> int:
    fixture = ("<html><head><style>x{}</style></head><body>"
               "<h1>Title</h1><p>Hello <strong>world</strong> see "
               "<a href='https://x.tld'>link</a>.</p><ul><li>one</li><li>two</li></ul>"
               "<script>evil()</script></body></html>")
    md = html_to_markdown(fixture)
    ok = ("# Title" in md and "**world**" in md and "[link](https://x.tld)" in md
          and "- one" in md and "evil()" not in md and "<" not in md)
    print("web-crawl self-test:", "PASS" if ok else "FAIL")
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
    if args and args[0] == "md":
        if len(args) < 2:
            print("usage: web-crawl.py md FILE.html", file=sys.stderr); sys.exit(2)
        md = html_to_markdown(Path(args[1]).read_text(encoding="utf-8", errors="replace"))
    elif args and args[0] == "fetch":
        if len(args) < 2:
            print("usage: web-crawl.py fetch URL [--out FILE]", file=sys.stderr); sys.exit(2)
        try:
            md = fetch(args[1], cfg)
        except Exception as exc:
            print(f"[web-crawl] fetch lỗi: {exc}", file=sys.stderr); sys.exit(1)
    else:
        print(__doc__); return
    if out:
        Path(out).write_text(md, encoding="utf-8"); print(f"wrote {out} ({len(md)} chars)")
    else:
        print(md)


if __name__ == "__main__":
    main()
