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

(c) PLAN 220926 — trang docs-shell (sidebar có `.logo` + ≥4 neo `#…`) phải đủ bộ khung MUST của docs-site-macos:
    icon tile trong sidebar, skip-link, <main id="main">, favicon inline, scroll spy, ripple, mind map, sơ đồ kéo-thả.
    Trước đây chỉ là văn xuôi trong skill → 0/5 trang đủ. Lớp nền (`html_font.py --apply`) tự chèn hết → chặn kèm đúng
    lệnh đó. CHECKS chép từ fdk/tools/docs-shell-survey.py (máy khách: validators và tools ở hai thư mục khác nhau);
    test_html_docs_shell.py gác hai bản không lệch.

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


def _nav(text: str) -> str:
    m = re.search(r"<nav\b.*?</nav>", text, re.S)
    return m.group(0) if m else ""


def is_docs_shell(text: str) -> bool:
    n = _nav(text)
    return 'class="logo' in n and len(re.findall(r'<a\b(?![^>]*class="[^"]*\blogo)[^>]*href="#[^"]', n)) >= 4


SHELL_CHECKS = {
    "icon-tile":  lambda h: bool(re.search(r'class="ic\b|class="nav-ic|<span[^>]*class="[^"]*\bico', _nav(h))),
    "skip-link":  lambda h: "skip-link" in h,
    "main-id":    lambda h: bool(re.search(r'<main\b|\bid="main"', h)),          # <main> id bất kỳ (skip-link trỏ đúng id đó)
    "favicon":    lambda h: bool(re.search(r'<link\b[^>]*\brel="(?:shortcut )?icon"', h)),   # thứ tự thuộc tính / file favicon đều nhận
    "nav-toggle": lambda h: "nav-toggle" in h,
    "scroll-spy": lambda h: "IntersectionObserver" in h,
    "ripple":     lambda h: "ripple" in h,
    "mind-map":   lambda h: bool(re.search(r'mind-?map|class="mm"', h, re.I)),
    "draggable":  lambda h: "diagram-box" not in h or bool(re.search(r"dataset\.draggable|data-draggable|initDraggableDiagrams", h)),
}


MANUAL = {"nav-toggle"}   # lớp nền (fdk/tools/html_shell.py) KHÔNG tự chèn — thông báo không được hứa "--apply là xong"


def wrap_blocked(html: str) -> bool:
    """Chép từ fdk/tools/html_shell.py — khi True lớp nền KHÔNG bọc <main> (sẽ gãy CSS/parser) → main-id, skip-link phải dựng tay."""
    css = " ".join(re.findall(r"<style\b[^>]*>(.*?)</style>", html, re.S | re.I))
    if re.search(r"(?<![\w-])body\s*>\s*[\w.#*:\[]|(?<![\w-])nav\s*[~+]", css):
        return True
    n = html.find("<nav"); h = html.rfind("<header", 0, n) if n >= 0 else -1
    return h >= 0 and html.find("</header>", h) > html.find("</nav>")


def shell_problem(path: str, text: str):
    if not is_docs_shell(text) or re.search(r'<meta\s+name="overstack-shell"\s+content="none"', text):
        return None
    gaps = [k for k, ok in SHELL_CHECKS.items() if not ok(text)]
    if not gaps:
        return None
    manual = set(MANUAL) | ({"main-id", "skip-link"} if "main-id" in gaps and wrap_blocked(text) else set())
    auto = [g for g in gaps if g not in manual]
    msg = f"trang tài liệu thiếu bộ khung MUST của docs-site-macos: {', '.join(gaps)}."
    if auto:
        msg += (f" Lớp nền tự chèn {', '.join(auto)} — chạy: python3 ~/.claude/harness/fdk/tools/html_font.py --apply {path}"
                "  (repo framework: python3 fdk/tools/html_font.py --apply …).")
    if "nav-toggle" in gaps:
        msg += " nav-toggle phải dựng tay theo §Navigation của /docs-site-macos (.nav-toggle + .nav-close) — lớp nền không chèn vì đụng bố cục riêng."
    if "main-id" in gaps and "main-id" in manual:
        msg += (" main-id + skip-link phải dựng tay: bọc nội dung trong <main id=\"main\"> sẽ gãy trang này (CSS `body >`/`nav ~`/`nav +`"
                " hoặc nav nằm trong <header>).")
    msg += " Trang cố ý không theo khung → <meta name=\"overstack-shell\" content=\"none\"> kèm lý do."
    return msg


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
    errs = [e for e in (nav_problem(text), preset_problem(path, text), shell_problem(path, text)) if e]
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
    shell = ('<nav><div class="logo">T</div>' + "".join(f'<a href="#s{i}">S{i}</a>' for i in range(5)) + "</nav>")
    assert blocked(shell + secs), "docs-shell thiếu bộ khung phải bị chặn (c)"
    full = ('<link rel="icon" href="data:x"><a class="skip-link"></a>' + shell.replace('<a href', '<a class="ic" href')
            + '<main id="main"></main>nav-toggle IntersectionObserver ripple <div class="mm"></div>' + secs)
    assert not blocked(full), "docs-shell đủ khung phải qua (c)"
    sub = d / "council"
    sub.mkdir()
    (sub / "x.html").write_text(secs, encoding="utf-8")
    check(str(sub / "x.html"))  # ngoài */html/*.html → bỏ qua, không exit
    print("html_docs_shell --self-test: 11/11 ok")


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
