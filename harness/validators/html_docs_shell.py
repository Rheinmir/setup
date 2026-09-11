#!/usr/bin/env python3
"""R20 html-docs-shell: vỏ trang HTML tài liệu phải nhất quán, bất kể skill nào sinh ra nó.

(a) GH#155 — trang có >3 mục phải có menu điều hướng. Yêu cầu "sidebar" từng chỉ sống trong
    skill /docs-site-macos → chỉ đúng khi agent tự nạp skill; /propose sinh một *-seq.html 11 mục
    không menu mà không cổng nào chặn. "Mục" đếm tất định = max(<section id=…>, <h2>); >3 mục mà
    không <nav> nào chứa ≥3 href="#…" → chặn.
    Thoát: <meta name="overstack-nav" content="none"> (trang cố ý một cột).
(b) GH#154 — sơ đồ archify nhúng qua <iframe> phải cùng theme trang chứa (preset `macos`, mặc định
    của bản cài). Agent hay chép `visual_preset: signal-flow` từ archify/examples → font mono lệch
    trang. Thoát: <meta name="overstack-preset" content="<preset>"> khi user YÊU CẦU preset đó.

Phạm vi: file .html nằm TRỰC TIẾP trong một thư mục `html/` (`*/html/*.html`). Miễn: chính artifact
archify (viewer tự chứa — cùng cách miễn R16/R7).

Contract: stdin JSON {"action":"write","file_path":...} hoặc argv files. Exit 0/2.
"""
import json
import re
import sys
from pathlib import Path

MAX_SECTIONS_NO_NAV = 3
ARCHIFY_RE = re.compile(r"\barchify \d+\.\d+")
NAV_RE = re.compile(r"<nav\b[^>]*>(.*?)</nav>", re.S | re.I)
ANCHOR_RE = re.compile(r"""href\s*=\s*["']#[^"']""", re.I)
NAV_OFF_RE = re.compile(r"""<meta\s+name=["']overstack-nav["']\s+content=["']none["']""", re.I)
IFRAME_RE = re.compile(r"""<iframe\b[^>]*?\bsrc\s*=\s*["']([^"'#?]+\.html)""", re.I)
PRESET_RE = re.compile(r"""\sdata-preset=["']([a-z0-9-]+)["']""")   # thuộc tính phần tử, không phải selector CSS
PRESET_OK_RE = re.compile(r"""<meta\s+name=["']overstack-preset["']\s+content=["']([a-z0-9-]+)["']""", re.I)


def is_archify(text: str) -> bool:
    return bool(ARCHIFY_RE.search(text)) and "<svg" in text


def in_scope(path: str) -> bool:
    p = Path(path or "")
    return p.suffix == ".html" and p.parent.name == "html"


def nav_problem(text: str):
    if NAV_OFF_RE.search(text):
        return None
    sec = len(re.findall(r"<section\b[^>]*\bid\s*=", text, re.I))
    h2 = len(re.findall(r"<h2\b", text, re.I))
    n = max(sec, h2)
    if n <= MAX_SECTIONS_NO_NAV:
        return None
    anchors = max([len(ANCHOR_RE.findall(m)) for m in NAV_RE.findall(text)] or [0])
    if anchors >= 3:
        return None
    return (f"{n} mục (<section id>={sec}, <h2>={h2}) nhưng không có <nav> chứa ≥3 liên kết #anchor "
            f"(đếm được {anchors}) — trang dài không có menu điều hướng. Sửa: nạp /docs-site-macos (Skill tool) "
            f"và dựng sidebar theo §Navigation (nav + .nav-toggle/.nav-close + scroll-spy). Cố ý một cột → "
            f'thêm <meta name="overstack-nav" content="none"> kèm lý do.')


def preset_problem(path: str, text: str):
    allowed = {"macos", *PRESET_OK_RE.findall(text)}
    bad = []
    for src in dict.fromkeys(IFRAME_RE.findall(text)):
        try:
            art = (Path(path).parent / src).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = PRESET_RE.search(art) if is_archify(art) else None
        if m and m.group(1) not in allowed:
            bad.append(f"{src} ({m.group(1)})")
    if not bad:
        return None
    return (f"sơ đồ archify nhúng lệch theme trang chứa: {', '.join(bad)} — để trống meta.visual_preset "
            f"(mặc định macos) rồi render lại; đừng chép preset từ archify/examples. User yêu cầu preset đó → "
            f'thêm <meta name="overstack-preset" content="<preset>"> vào trang chứa.')


def check(path: str) -> None:
    if not in_scope(path):
        return
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    if is_archify(text):
        return
    errs = [e for e in (nav_problem(text), preset_problem(path, text)) if e]
    if errs:
        for e in errs:
            print(f"[R20 html-docs-shell] {path}: {e}", file=sys.stderr)
        sys.exit(2)


def self_test():
    import tempfile
    d = Path(tempfile.mkdtemp()) / "llmwiki" / "html"
    d.mkdir(parents=True)
    f = d / "p.html"

    def blocked(content):
        f.write_text(content, encoding="utf-8")
        try:
            check(str(f))
            return False
        except SystemExit as e:
            return e.code == 2

    secs = "".join(f'<section id="s{i}"><h2>S{i}</h2></section>' for i in range(5))
    nav = "<nav>" + "".join(f'<a href="#s{i}">S{i}</a>' for i in range(5)) + "</nav>"
    assert blocked(secs), "5 mục không nav phải bị chặn"
    assert not blocked(nav + secs), "có nav ≥3 anchor phải qua"
    assert not blocked("<h2>a</h2><h2>b</h2><h2>c</h2>"), "≤3 mục phải qua"
    assert not blocked('<meta name="overstack-nav" content="none">' + secs), "meta thoát phải qua"
    assert not blocked("<html>archify 2.17.0 <svg></svg>" + secs), "artifact archify được miễn"
    (d / "t1.html").write_text('<html>archify 2.17.0 <body data-preset="signal-flow"><svg/>', encoding="utf-8")
    (d / "t2.html").write_text('<html>archify 2.17.0 <body data-preset="macos"><svg/>', encoding="utf-8")
    assert blocked(nav + secs + '<iframe src="t1.html"></iframe>'), "preset signal-flow phải bị chặn"
    assert not blocked(nav + secs + '<iframe src="t2.html"></iframe>'), "preset macos phải qua"
    assert not blocked('<meta name="overstack-preset" content="signal-flow">' + nav + secs
                       + '<iframe src="t1.html"></iframe>'), "preset user yêu cầu (meta) phải qua"
    sub = d / "council"
    sub.mkdir()
    (sub / "x.html").write_text(secs, encoding="utf-8")
    check(str(sub / "x.html"))  # ngoài */html/*.html → bỏ qua, không exit
    print("html_docs_shell --self-test: 9/9 ok")


def main() -> None:
    if sys.argv[1:] == ["--self-test"]:
        self_test()
        return
    args = sys.argv[1:]
    if args:
        for p in args:
            check(p)
        sys.exit(0)
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if ev.get("action") == "write":
        check(ev.get("file_path", ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
