"""cor — Controlled Output Renderer (shared invariants).

Chưng từ council.py Stage-4 sau khi /council thẩm định (verdict: KHẢ THI nhưng HẸP —
microlib opt-in, KHÔNG god-lib). Đây là các BẤT BIẾN cơ học dùng chung cho mọi
script sinh file HTML/md từ dữ liệu deterministic. Nó KHÔNG chứa layout của bất kỳ
skill nào — mỗi consumer tự viết `render_fn() -> str`; cor lo 5 việc khó-viết-đúng:

  1. escape mọi input (chống vỡ layout & HTML-injection)  -> esc()
  2. versioned no-overwrite (mỗi run 1 bản ghi bất biến)    -> write_versioned()
  3. isolation try/except (lỗi render KHÔNG giết core)       -> write_versioned()
  4. offline self-contained shell (no CDN)                   -> page()
  5. latest pointer tiện dụng (nên gitignore)                -> write_versioned()
Bất biến #6 (deterministic) là trách nhiệm của consumer: đừng nhét Date/random.

THIẾT KẾ CHO FAILURE MODE (Taleb barbell):
  - STATELESS pure functions, không side-effect ẩn, ≤200 dòng → tái bản 30'.
  - backwards-compat: chỉ ADD, không BREAK chữ ký cũ. Consumer PIN version:
        import cor; assert cor.__version__.startswith("0.")
  - escape hatch: nếu file này chết, consumer copy 5 bất biến inline tạm thời.

Zero third-party import (chỉ stdlib) → không kéo theo dependency-tail.
"""
from __future__ import annotations

__version__ = "0.1.0"

import html as _html
import sys as _sys
from pathlib import Path


def esc(x) -> str:
    """html.escape mọi giá trị (kể cả None/số). Bất biến #1."""
    return _html.escape("" if x is None else str(x), quote=True)


def _next_index(out: Path, stem: str) -> int:
    """Số versioned kế tiếp = max(index đang có)+1. Index là cụm chữ-số đầu tiên
    trong tên sau `stem-`. Robust với đuôi tuỳ ý (`-seed42`, `-2026` …)."""
    nxt = 1
    for f in out.glob(f"{stem}-*.html"):
        for part in f.stem[len(stem) + 1:].split("-"):
            if part.isdigit():
                nxt = max(nxt, int(part) + 1)
                break
    return nxt


def write_versioned(render_fn, out_dir, stem: str, tag: str = "", *, latest: bool = True):
    """Gọi `render_fn() -> str` BÊN TRONG try/except rồi ghi ra
    `<out_dir>/<stem>-NNN[-tag].html` (NNN tăng dần, KHÔNG ghi đè) + `latest.html`.

    Bất biến #2/#3/#5. Trả (Path, index) khi ok; (None, 0) khi render lỗi — lỗi chỉ
    WARN, KHÔNG raise, để artifact core của consumer (đã ghi TRƯỚC khi gọi hàm này)
    không bao giờ bị report layer kéo sập. Caller quyết có coi None là fatal không.
    """
    try:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        idx = _next_index(out, stem)
        suffix = f"-{tag}" if tag else ""
        path = out / f"{stem}-{idx:03d}{suffix}.html"
        content = render_fn()
        if not isinstance(content, str):
            raise TypeError(f"render_fn phải trả str, nhận {type(content).__name__}")
        path.write_text(content, encoding="utf-8")
        if latest:
            (out / "latest.html").write_text(content, encoding="utf-8")
        return path, idx
    except Exception as exc:  # noqa: BLE001 - report is derived; never fatal
        print(f"[cor] WARN: render bị bỏ qua ({type(exc).__name__}: {exc}); "
              f"artifact core không bị ảnh hưởng.", file=_sys.stderr)
        return None, 0


# Khung HTML offline tối thiểu (Bất biến #4). Consumer nào muốn tự do layout thì bỏ
# qua hàm này; nó chỉ để các script đơn giản có sẵn 1 shell no-CDN tử tế.
_BASE_CSS = """
:root{--paper:#f4f1ea;--ink:#26221c;--dim:#7a7266;--line:rgba(60,52,40,.13);--accent:#8a6d2f}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font:15px/1.6 "Iowan Old Style",Palatino,Georgia,ui-serif,serif;color:var(--ink);
 background:var(--paper);min-height:100dvh;-webkit-font-smoothing:antialiased}
.cor-wrap{max-width:940px;margin:0 auto;padding:48px 22px 80px}
h1{font-size:clamp(26px,4vw,38px);letter-spacing:-.015em;margin:0 0 6px}
.cor-meta{color:var(--dim);font:500 12.5px/1 ui-monospace,Menlo,monospace;margin-bottom:22px}
a:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
"""


def page(title: str, body_html: str, *, meta: str = "", extra_css: str = "") -> str:
    """Bọc `body_html` (đã escape ở tầng consumer) trong 1 trang self-contained,
    no-CDN, no-JS. Trả chuỗi HTML hoàn chỉnh. `title`/`meta` được escape tại đây."""
    meta_html = ('<div class="cor-meta">' + esc(meta) + '</div>') if meta else ''
    return (
        '<!doctype html><html lang="vi"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>' + esc(title) + '</title><style>' + _BASE_CSS + extra_css + '</style></head>'
        '<body><div class="cor-wrap"><h1>' + esc(title) + '</h1>'
        + meta_html + body_html + '</div></body></html>'
    )


def _selftest() -> int:
    """Conformance cho 5 bất biến cơ học. `python3 cor.py` → exit 0 nếu khoẻ."""
    import tempfile
    assert esc('<a>&"') == '&lt;a&gt;&amp;&quot;', "esc"          # #1
    assert esc(None) == "" and esc(3) == "3", "esc None/num"
    d = Path(tempfile.mkdtemp())
    p1, i1 = write_versioned(lambda: page("T", "<p>x</p>", meta="m"), d, "r", "seed1")
    p2, i2 = write_versioned(lambda: "y", d, "r", "seed1")
    assert (i1, i2) == (1, 2) and p1.name == "r-001-seed1.html", "versioning"  # #2
    assert not p1.read_text().count("<script"), "no inline script leaked"
    assert (d / "latest.html").exists(), "latest pointer"                       # #5
    p3, i3 = write_versioned(lambda: 1 / 0, d, "r")                             # #3
    assert p3 is None and i3 == 0, "isolation must swallow render error"
    p4, i4 = write_versioned(lambda: 42, d, "r")                               # type guard
    assert p4 is None, "non-str render must be rejected safely"
    assert page("A", "<p>b</p>").startswith("<!doctype html") and "http" not in page("A", "").split("cor-wrap")[0].replace("http-equiv", ""), "offline shell"  # #4
    print(f"[cor] selftest OK (v{__version__}) — 5 invariants pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
