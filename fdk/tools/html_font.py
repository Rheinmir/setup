#!/usr/bin/env python3
"""html_font — MỘT nguồn token font cho mọi HTML do framework sinh ra (việc user giao 20/09/2026).

Nội dung dùng **Lexend Deca, weight 300 (Light)**; chữ đậm/tiêu đề lấy nét thật từ cùng font (trục wght 300–700, không giả đậm);
`--font-mono` cho code GIỮ font hệ thống. Font được NHÚNG base64 vào từng trang (user chốt "nhúng hết"): trang mở bằng file://,
không mạng vẫn đúng font, không gọi ra fonts.googleapis.com. Luôn có fallback hệ thống phía sau.

    from html_font import head_css, FONT_TEXT       # generator: chèn head_css() vào <style> ĐẦU TIÊN của trang
    html_font.py --apply trang.html [trang2.html…]  # trang do SKILL/agent dựng tay: nhúng font tại chỗ (idempotent) — gọi SAU khi ghi trang
    html_font.py --check                            # data module khớp file woff2?  (rc 1 khi lệch)
    html_font.py --rebuild [path/to/LexendDeca-VariableFont_wght.ttf]   # cắt lại subset + sinh lại data module (cần fontTools + brotli)

Dữ liệu base64 nằm ở `html_font_data.py` (file .py để đi cùng đợt copy `fdk/tools/*.py` xuống ~/.claude/harness — asset nhị phân
không được installer copy). Giấy phép SIL OFL 1.1: `assets/fonts/LexendDeca-NOTICE.txt`.
"""
import base64, hashlib, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WOFF2 = HERE / "assets" / "fonts" / "LexendDeca-300-700-vi.woff2"
DATA = HERE / "html_font_data.py"

FAMILY = "Lexend Deca"
FALLBACK = "-apple-system,BlinkMacSystemFont,'Segoe UI','Roboto','Helvetica Neue',sans-serif"
FONT_TEXT = f"'{FAMILY}',{FALLBACK}"
FONT_DISPLAY = FONT_TEXT
FONT_MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,monospace"
WEIGHT_TEXT = 300          # Light — mặc định cho NỘI DUNG
WEIGHT_STRONG = 500        # <strong>/<b>/th: đủ tương phản với 300 mà không nặng nề
WEIGHT_HEADING = 500


def _load_b64() -> str:
    import importlib.util
    spec = importlib.util.spec_from_file_location("html_font_data", DATA); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.WOFF2_B64


def font_face() -> str:
    return (f"@font-face{{font-family:'{FAMILY}';font-style:normal;font-weight:300 700;font-display:swap;"
            f"src:url(data:font/woff2;base64,{_load_b64()}) format('woff2')}}")


def head_css() -> str:
    """Khối CSS đặt ĐẦU <style> của trang: @font-face nhúng + token + mặc định cho nội dung. Trang có khai `--font-text`/
    `--font-display` riêng ở SAU thì phải bỏ đi (hoặc trỏ về var này) — html-font-lint gác."""
    return (font_face() +
            f":root{{--font-text:{FONT_TEXT};--font-display:{FONT_DISPLAY};--font-mono:{FONT_MONO};--fw-text:{WEIGHT_TEXT};--fw-strong:{WEIGHT_STRONG}}}"
            f"html,body{{font-family:var(--font-text);font-weight:var(--fw-text)}}"
            f"strong,b,th{{font-weight:var(--fw-strong)}}h1,h2,h3,h4{{font-family:var(--font-display);font-weight:{WEIGHT_HEADING}}}"
            f"code,pre,kbd,samp{{font-family:var(--font-mono)}}")


STYLE_ID = "ovs-font"


def apply(html: str, *, _from_base: bool = False) -> str:
    """Gắn font mặc định vào MỘT trang HTML hoàn chỉnh — generator gọi đúng một dòng ngay trước khi ghi file.
    Chèn <style id="ovs-font"> ở CUỐI <head> để thắng cascade: token `--font-text/--font-display` trang tự khai ở trên bị đè,
    `body` nhận Lexend Deca weight 300; chỗ nào trang đã đặt font-weight riêng giữ nguyên và lấy nét THẬT từ trục wght.
    Stack hệ thống chép tay (`-apple-system,…`) CHỈ được trỏ về token khi nằm trong khối <style> của <head> — bản đầu quét regex
    trên TOÀN trang và (review 20/09/2026) đã: làm hỏng 2 iframe srcdoc trong overstack.html (tài liệu con không có `--font-text`),
    cắt đôi stack có `"Segoe UI"`, và ăn mất nháy đóng của chuỗi JS. Stack kết thúc bằng `monospace` không bị đụng. Idempotent."""
    import re
    if not _from_base:                         # generator vẫn gọi html_font.apply() như cũ → chuyển tiếp sang LỚP NỀN (font + token + toggle).
        base = HERE / "html_base.py"           # không có html_base (bản sao cũ ở repo engine) → chỉ gắn font như trước
        if base.is_file():
            import importlib.util
            s = importlib.util.spec_from_file_location("ovs_html_base", base); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
            return m.apply(html)
    if f'id="{STYLE_ID}"' in html:
        return html
    m = re.search(r"</head\s*>", html, re.I)
    if not m:
        return html
    head, rest = html[:m.start()], html[m.start():]
    def fix_css(sm):
        css = re.sub(r"font-family:\s*-apple-system[^;{}]*",
                     lambda f: f.group(0) if "monospace" in f.group(0) else "font-family:var(--font-text)", sm.group(2))
        return sm.group(1) + css + sm.group(3)
    head = re.sub(r"(<style\b[^>]*>)(.*?)(</style\s*>)", fix_css, head, flags=re.I | re.S)
    return head + f'<style id="{STYLE_ID}">{head_css()}</style>' + rest


MARK = f"font-family:'{FAMILY}'"           # chuỗi html-font-lint tìm trong trang đã sinh


def _write_data(raw: bytes) -> None:
    b64 = base64.b64encode(raw).decode()
    DATA.write_text('"""SINH TỰ ĐỘNG bởi html_font.py --rebuild/--sync — đừng sửa tay. Lexend Deca subset (latin + tiếng Việt, wght 300–700), SIL OFL 1.1."""\n'
                    f'WOFF2_SHA256 = "{hashlib.sha256(raw).hexdigest()}"\nWOFF2_B64 = (\n'
                    + "".join(f'    "{b64[i:i+120]}"\n' for i in range(0, len(b64), 120)) + ")\n", encoding="utf-8")


def check() -> int:
    import importlib.util
    spec = importlib.util.spec_from_file_location("html_font_data", DATA); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    ok = base64.b64decode(m.WOFF2_B64)[:4] == b"wOF2" and hashlib.sha256(base64.b64decode(m.WOFF2_B64)).hexdigest() == m.WOFF2_SHA256
    if WOFF2.exists():                     # máy khách chỉ có .py → chỉ kiểm tự-nhất-quán; repo framework kiểm thêm khớp file gốc
        ok = ok and hashlib.sha256(WOFF2.read_bytes()).hexdigest() == m.WOFF2_SHA256
    print("html_font: OK" if ok else "html_font: LỆCH — chạy html_font.py --sync (hoặc --rebuild)"); return 0 if ok else 1


def rebuild(src: str) -> int:
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    from fontTools import subset
    uni = (list(range(0x20, 0x7F)) + list(range(0xA0, 0x180)) + [0x1A0, 0x1A1, 0x1AF, 0x1B0] + list(range(0x300, 0x30A)) + [0x323]
           + list(range(0x1EA0, 0x1EFA)) + list(range(0x2010, 0x2028))
           + [0x2030, 0x2032, 0x2033, 0x2039, 0x203A, 0x20AB, 0x20AC, 0x2122, 0x2212, 0x2248, 0x2260, 0x2264, 0x2265, 0x2026, 0x00D7, 0x2022])
    f = TTFont(src)
    opt = subset.Options(); opt.layout_features = ["kern", "liga", "mark", "mkmk", "ccmp", "locl"]; opt.name_IDs = [1, 2, 3, 4, 6, 13, 14]; opt.notdef_outline = True
    s = subset.Subsetter(opt); s.populate(unicodes=uni); s.subset(f)      # cắt glyph TRƯỚC, giới hạn trục SAU (ngược lại fontTools lỗi KeyError gvar)
    tmp = WOFF2.with_suffix(".tmp.ttf"); f.save(tmp); f = TTFont(tmp)
    v = instancer.instantiateVariableFont(f, {"wght": (300, 700)}, inplace=False); v.flavor = "woff2"; v.save(WOFF2); tmp.unlink()
    _write_data(WOFF2.read_bytes()); print(f"→ {WOFF2} ({WOFF2.stat().st_size/1024:.1f} KB) · → {DATA}"); return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--rebuild" in a:
        rest = [x for x in a if not x.startswith("--")]
        sys.exit(rebuild(rest[0] if rest else str(Path.home() / "Library/Fonts/LexendDeca-VariableFont_wght.ttf")))
    if "--apply" in a:
        rc = 0
        for f in [Path(x) for x in a if not x.startswith("--")]:
            if not f.is_file():
                print(f"✗ không thấy {f}"); rc = 1; continue
            src = f.read_text(encoding="utf-8"); out = apply(src)
            if not __import__("re").search(r"</head\s*>", src, __import__("re").I):
                print(f"✗ {f}: không có </head> — không phải trang HTML hoàn chỉnh"); rc = 1
            elif out == src:
                print(f"· {f}: đã có font (bỏ qua)")
            else:
                f.write_text(out, encoding="utf-8"); print(f"✓ {f}: nhúng {FAMILY} Light (+{(len(out) - len(src)) / 1024:.0f} KB)")
        sys.exit(rc)
    if "--sync" in a:
        _write_data(WOFF2.read_bytes()); print(f"→ {DATA}"); sys.exit(0)
    sys.exit(check())
