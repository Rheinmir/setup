#!/usr/bin/env python3
"""html_font — MỘT nguồn token font cho mọi HTML do framework sinh ra (việc user giao 20/09/2026, đổi font 21/09/2026).

Nội dung dùng **Be Vietnam Pro** (theme đọc kiểu Vietcetera, user chốt 21/09/2026): body 400, chữ đậm 600, tiêu đề 800 siết
letter-spacing âm. Be Vietnam Pro KHÔNG có bản variable → nhúng BA file tĩnh 400/600/800 (≈95 KB; đủ 5 weight là 160 KB — quá trần
150 KB của PLAN 210926). Trang xin 500 thì trình duyệt lấy 400, xin 700 lấy 800 (luật khớp font CSS) — nét THẬT, không giả đậm.
`--font-mono` cho code GIỮ font hệ thống. Font được NHÚNG base64 vào từng trang (user chốt "nhúng hết"): trang mở bằng file://,
không mạng vẫn đúng font, không gọi ra fonts.googleapis.com. Luôn có fallback hệ thống phía sau.

    from html_font import head_css, FONT_TEXT       # generator: chèn head_css() vào <style> ĐẦU TIÊN của trang
    html_font.py --apply trang.html [trang2.html…]  # trang do SKILL/agent dựng tay: nhúng font tại chỗ (idempotent) — gọi SAU khi ghi trang
    html_font.py --check                            # data module khớp các file woff2?  (rc 1 khi lệch)
    html_font.py --rebuild <dir chứa BeVietnamPro-{Regular,SemiBold,ExtraBold}.ttf>   # cắt lại subset + sinh lại data module (cần fontTools + brotli)

Dữ liệu base64 nằm ở `html_font_data.py` (file .py để đi cùng đợt copy `fdk/tools/*.py` xuống ~/.claude/harness — asset nhị phân
không được installer copy). Giấy phép SIL OFL 1.1: `assets/fonts/BeVietnamPro-NOTICE.txt`.
"""
import base64, hashlib, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONTS = HERE / "assets" / "fonts"
WEIGHTS = (400, 600, 800)
_SRC = {400: "Regular", 600: "SemiBold", 800: "ExtraBold"}
DATA = HERE / "html_font_data.py"

FAMILY = "Be Vietnam Pro"
FALLBACK = "-apple-system,BlinkMacSystemFont,'Segoe UI','Roboto','Helvetica Neue',sans-serif"
FONT_TEXT = f"'{FAMILY}',{FALLBACK}"
FONT_DISPLAY = FONT_TEXT
FONT_MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,monospace"
WEIGHT_TEXT = 400          # nội dung — như theme mẫu
WEIGHT_STRONG = 600        # <strong>/<b>/th
WEIGHT_HEADING = 800       # tiêu đề: nét đậm nhất đã nhúng
TRACK_HEADING = "-.03em"   # CHỈ h1/h2: theme siết -.035 → -.055em ở tiêu đề lớn; h3/h4 (~16px) siết vào là dính chữ (soát ảnh 21/09)


def woff2(w: int) -> Path:
    return FONTS / f"BeVietnamPro-{w}-vi.woff2"


def _load_data():
    import importlib.util
    spec = importlib.util.spec_from_file_location("html_font_data", DATA); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _load_b64() -> dict:
    """{weight: base64 woff2}"""
    return _load_data().WOFF2_B64


def font_face() -> str:
    return "".join(f"@font-face{{font-family:'{FAMILY}';font-style:normal;font-weight:{w};font-display:swap;"
                   f"src:url(data:font/woff2;base64,{b}) format('woff2')}}" for w, b in sorted(_load_b64().items()))


def head_css() -> str:
    """Khối CSS đặt ĐẦU <style> của trang: @font-face nhúng + token + mặc định cho nội dung. Trang có khai `--font-text`/
    `--font-display` riêng ở SAU thì phải bỏ đi (hoặc trỏ về var này) — html-font-lint gác."""
    return (font_face() +
            f":root{{--font-text:{FONT_TEXT};--font-display:{FONT_DISPLAY};--font-mono:{FONT_MONO};--fw-text:{WEIGHT_TEXT};--fw-strong:{WEIGHT_STRONG};--fw-heading:{WEIGHT_HEADING};--ls-heading:{TRACK_HEADING}}}"
            f"html,body{{font-family:var(--font-text);font-weight:var(--fw-text)}}"
            f"strong,b,th{{font-weight:var(--fw-strong)}}h1,h2,h3,h4{{font-family:var(--font-display);font-weight:var(--fw-heading)}}h1,h2{{letter-spacing:var(--ls-heading)}}"
            f"code,pre,kbd,samp{{font-family:var(--font-mono)}}")


STYLE_ID = "ovs-font"


def apply(html: str, *, _from_base: bool = False) -> str:
    """Gắn font mặc định vào MỘT trang HTML hoàn chỉnh — generator gọi đúng một dòng ngay trước khi ghi file.
    Chèn <style id="ovs-font"> ở CUỐI <head> để thắng cascade: token `--font-text/--font-display` trang tự khai ở trên bị đè,
    `body` nhận Be Vietnam Pro 400; chỗ nào trang đã đặt font-weight riêng giữ nguyên (trình duyệt khớp về 400/600/800 đã nhúng).
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
    if f'id="{STYLE_ID}"' in html:             # đã có khối font → LÀM MỚI nếu nó là bản cũ (đổi font 21/09/2026: skeleton/template
        cur = f'<style id="{STYLE_ID}">{head_css()}</style>'   # nhúng sẵn Lexend không được "bỏ qua vì idempotent" mãi mãi)
        return re.sub(rf'<style id="{STYLE_ID}">.*?</style\s*>', lambda _: cur, html, count=1, flags=re.S)
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


def _write_data(raw: dict) -> None:
    body = ['"""SINH TỰ ĐỘNG bởi html_font.py --rebuild/--sync — đừng sửa tay. Be Vietnam Pro subset (latin + tiếng Việt, weight 400/600/800), SIL OFL 1.1."""\n',
            "WOFF2_SHA256 = {\n" + "".join(f'    {w}: "{hashlib.sha256(r).hexdigest()}",\n' for w, r in sorted(raw.items())) + "}\n", "WOFF2_B64 = {\n"]
    for w, r in sorted(raw.items()):
        b64 = base64.b64encode(r).decode()
        body.append(f"    {w}: (\n" + "".join(f'        "{b64[i:i+120]}"\n' for i in range(0, len(b64), 120)) + "    ),\n")
    DATA.write_text("".join(body) + "}\n", encoding="utf-8")


def check() -> int:
    m = _load_data(); ok = set(m.WOFF2_B64) == set(WEIGHTS)
    for w in WEIGHTS if ok else ():
        raw = base64.b64decode(m.WOFF2_B64[w])
        ok = ok and raw[:4] == b"wOF2" and hashlib.sha256(raw).hexdigest() == m.WOFF2_SHA256[w]
        if woff2(w).exists():              # máy khách chỉ có .py → chỉ kiểm tự-nhất-quán; repo framework kiểm thêm khớp file gốc
            ok = ok and hashlib.sha256(woff2(w).read_bytes()).hexdigest() == m.WOFF2_SHA256[w]
    print("html_font: OK" if ok else "html_font: LỆCH — chạy html_font.py --sync (hoặc --rebuild)"); return 0 if ok else 1


def rebuild(src_dir: str) -> int:
    from fontTools.ttLib import TTFont
    from fontTools import subset
    uni = (list(range(0x20, 0x7F)) + list(range(0xA0, 0x180)) + [0x1A0, 0x1A1, 0x1AF, 0x1B0] + list(range(0x300, 0x30A)) + [0x323]
           + list(range(0x1EA0, 0x1EFA)) + list(range(0x2010, 0x2028))
           + [0x2030, 0x2032, 0x2033, 0x2039, 0x203A, 0x20AB, 0x20AC, 0x2122, 0x2212, 0x2248, 0x2260, 0x2264, 0x2265, 0x2026, 0x00D7, 0x2022])
    for w in WEIGHTS:
        f = TTFont(Path(src_dir) / f"BeVietnamPro-{_SRC[w]}.ttf")
        opt = subset.Options(); opt.layout_features = ["kern", "liga", "mark", "mkmk", "ccmp", "locl"]; opt.name_IDs = [1, 2, 3, 4, 6, 13, 14]
        opt.notdef_outline = True; opt.flavor = "woff2"
        s = subset.Subsetter(opt); s.populate(unicodes=uni); s.subset(f); subset.save_font(f, str(woff2(w)), opt)
        print(f"→ {woff2(w)} ({woff2(w).stat().st_size/1024:.1f} KB)")
    _write_data({w: woff2(w).read_bytes() for w in WEIGHTS}); print(f"→ {DATA}"); return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--rebuild" in a:
        rest = [x for x in a if not x.startswith("--")]
        sys.exit(rebuild(rest[0] if rest else str(Path.home() / "Library/Fonts")))
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
                f.write_text(out, encoding="utf-8"); print(f"✓ {f}: nhúng {FAMILY} (+{(len(out) - len(src)) / 1024:.0f} KB)")
        sys.exit(rc)
    if "--sync" in a:
        _write_data({w: woff2(w).read_bytes() for w in WEIGHTS}); print(f"→ {DATA}"); sys.exit(0)
    sys.exit(check())
