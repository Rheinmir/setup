#!/usr/bin/env python3
"""spacing-survey — khoảng cách và nhịp chữ của trang HTML có theo MỘT thang hay không (0 token, chỉ đọc).

Vì sao có (22/09/2026): user "luật padding cách dòng vẫn slop và không có hệ thống gì cả". Đo lần đầu: 92 giá trị
khoảng cách khác nhau trên 54 trang, 61% ngoài lưới 4px, line-height 14 giá trị. Thang + nguồn chuẩn:
fdk/wiki/sources/220926-spacing-standards.md (IBM Carbon + Tailwind; WCAG 1.4.12/1.4.8; USWDS).

Chỉ đo `px`/`rem` trong padding/margin/gap (+ inset/top/right/bottom/left): `em` phụ thuộc cỡ chữ phần tử nên để cổng
chạy thật đo trên px đã tính. Bỏ khối của lớp nền (`ovs-*`) — đó là token của chính framework.

    spacing-survey.py trang.html [thư-mục …]   rc 2 khi còn giá trị ngoài thang · 0 khi sạch
    spacing-survey.py --all [--json]
"""
from __future__ import annotations

import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCALE = (0, 1, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96)
PROP = re.compile(r"(?<![\w-])(?:padding|margin|gap|row-gap|column-gap)(?:-(?:top|right|bottom|left|inline|block)(?:-(?:start|end))?)?\s*:\s*([^;}]+)", re.I)
LH = re.compile(r"(?<![\w-])line-height\s*:\s*([\d.]+)(px|rem|%)?(?=\s*[;}])")


def page_css(html: str) -> str:
    css = " ".join(re.findall(r"<style\b(?![^>]*\bid=\"ovs-)[^>]*>(.*?)</style>", html, re.S | re.I))
    return re.sub(r"url\(\s*data:[^)]*\)", "", css)


def values(css: str) -> list:
    out = []
    for v in PROP.findall(css):
        if re.search(r"calc\(|clamp\(|min\(|max\(|var\(", v, re.I):     # var(): khớp cổng tĩnh + phép vá (review t8 #4)
            continue
        for n, u in re.findall(r"(-?\d*\.?\d+)(px|rem)\b", v):
            px = abs(float(n)) * (16 if u == "rem" else 1)
            out.append(round(px, 2))
    return out


def on_scale(px: float) -> bool:
    return px < 2 or px in SCALE or (px > 96 and px % 16 == 0)   # < 2px = viền/khe mảnh · bố cục lớn: bội số 16 (Carbon có bậc 160)


def off_scale(css: str) -> list:
    return [v for v in values(css) if not on_scale(v)]


def line_heights(css: str) -> list:
    return [float(n) / (100 if u == "%" else 1) for n, u in LH.findall(css) if u in ("", "%")]


def report(p: Path) -> dict:
    css = page_css(p.read_text(encoding="utf-8", errors="ignore"))
    vs = values(css)
    return {"page": str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p), "values": len(vs), "distinct": len(set(vs)),
            "off_scale": len(off_scale(css)), "off_distinct": sorted(set(off_scale(css)))[:12],
            "lh_distinct": sorted(set(line_heights(css)))}


def main(argv=None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    base = Path.cwd() if (Path.cwd() / ".llmwiki").is_dir() or (Path.cwd() / "llmwiki").is_dir() else ROOT   # máy khách: tool nằm ở ~/.claude/harness (review t8 #8)
    ps = [p for d in ("llmwiki/html", "llmwiki/graph", ".llmwiki/html", ".llmwiki/graph") for p in sorted((base / d).glob("*.html"))] if "--all" in a else []
    for x in [Path(v) for v in a if not v.startswith("--")]:
        ps += sorted(x.glob("*.html")) if x.is_dir() else [x]
    if not ps:
        print(__doc__); return 1
    rows = [report(p) for p in ps]
    if "--json" in a:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for r in rows:
            if r["off_scale"]:
                print(f"✗ {r['page']}: {r['off_scale']}/{r['values']} ngoài thang — vd {', '.join(f'{v:g}px' for v in r['off_distinct'][:6])}")
        tv, to = sum(r["values"] for r in rows), sum(r["off_scale"] for r in rows)
        print(f"spacing-survey: {len(rows)} trang · {tv} giá trị · {to} ngoài thang ({to * 100 // max(tv, 1)}%)")
    return 2 if any(r["off_scale"] for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
