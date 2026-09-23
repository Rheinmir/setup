#!/usr/bin/env python3
"""docs-shell-survey — trang tài liệu theo khuôn docs-site-macos THIẾU quy định MUST nào (0 token, chỉ đọc).

Vì sao có (22/09/2026): skill docs-site-macos khai 13 luật MUST + nhiều thành phần REQUIRED nhưng chỉ bằng văn xuôi —
agent dựng trang bỏ qua thì không gì bắt (user: "mấy nhãn trong sidebar này trông chán thế nhỉ"). Bộ đo này là nguồn
CHECKS dùng chung cho lớp nền (html_base chèn phần máy làm được) và luật R20 (gác phần còn lại).

Trang docs-shell = có <nav> chứa `.logo` và ≥ 4 link neo `#…`. Sidebar RIÊNG (trang graph của engine, control-room)
không theo khuôn này nên không bị hỏi.

    docs-shell-survey.py trang.html [thư-mục …]   rc 2 khi có trang thiếu · 0 khi đủ
    docs-shell-survey.py --all [--json]          mọi trang trong llmwiki/html + llmwiki/graph
"""
from __future__ import annotations

import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def is_docs_shell(html: str) -> bool:
    m = re.search(r"<nav\b.*?</nav>", html, re.S)
    return bool(m) and 'class="logo' in m.group(0) and len(re.findall(r'<a\b(?![^>]*class="[^"]*\blogo)[^>]*href="#[^"]', m.group(0))) >= 4


def _nav(html: str) -> str:
    m = re.search(r"<nav\b.*?</nav>", html, re.S)
    return m.group(0) if m else ""


# Mỗi check: True = ĐỦ. Thành phần có điều kiện (sơ đồ) chỉ hỏi khi trang có đối tượng đó.
CHECKS = {
    "icon-tile":  lambda h: bool(re.search(r'class="ic\b|class="nav-ic|<span[^>]*class="[^"]*\bico', _nav(h))),
    "skip-link":  lambda h: "skip-link" in h,
    "main-id":    lambda h: bool(re.search(r'<main\b|\bid="main"', h)),          # <main> id bất kỳ (skip-link trỏ đúng id đó)
    "favicon":    lambda h: bool(re.search(r'<link\b[^>]*\brel="(?:shortcut )?icon"', h)),   # thứ tự thuộc tính / file favicon đều nhận
    "nav-toggle": lambda h: "nav-toggle" in h,
    "scroll-spy": lambda h: "IntersectionObserver" in h,
    "ripple":     lambda h: "ripple" in h,
    "mind-map":   lambda h: bool(re.search(r'mind-?map|class="mm"', h, re.I)),   # khuôn skill dùng class "mm"
    "draggable":  lambda h: "diagram-box" not in h or bool(re.search(r"dataset\.draggable|data-draggable|initDraggableDiagrams", h)),
}


def exempt(html: str) -> bool:
    return bool(re.search(r'<meta\s+name="overstack-shell"\s+content="none"', html))   # trang cố ý không theo khung


def gaps(html: str) -> list:
    return [k for k, ok in CHECKS.items() if not ok(html)] if is_docs_shell(html) and not exempt(html) else []


def pages_all() -> list:
    return [p for d in ("llmwiki/html", "llmwiki/graph") for p in sorted((ROOT / d).glob("*.html"))]


def main(argv=None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    ps = pages_all() if "--all" in a else []
    for x in [Path(v) for v in a if not v.startswith("--")]:
        ps += sorted(x.glob("*.html")) if x.is_dir() else [x]
    if not ps:
        print(__doc__); return 1
    rows = []
    for p in ps:
        h = p.read_text(encoding="utf-8", errors="ignore")
        if is_docs_shell(h) and not exempt(h):
            rows.append({"page": str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p), "gaps": gaps(h)})
    if "--json" in a:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for r in rows:
            print(f"{'✓' if not r['gaps'] else '✗'} {r['page']}" + (f": thiếu {', '.join(r['gaps'])}" if r["gaps"] else ""))
        bad = sum(1 for r in rows if r["gaps"])
        print(f"docs-shell-survey: {len(rows) - bad}/{len(rows)} trang docs-shell đủ khung")
    return 2 if any(r["gaps"] for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
