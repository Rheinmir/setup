#!/usr/bin/env python3
"""html_font — MỘT nguồn token font cho mọi HTML do framework sinh ra (việc user giao 20/09/2026, đổi font 21/09/2026).

TIÊU ĐỀ dùng **Newsreader 600** (serif kiểu báo; user chốt 22/09/2026 sau khi so sáu font trên cùng một mẫu tiếng Việt) — nhúng MỘT
file tĩnh cắt tại wght 600 / opsz 24. Nội dung dùng **Be Vietnam Pro** (theme đọc kiểu Vietcetera, user chốt 21/09/2026): body 400, chữ đậm 600, tiêu đề 800 siết
letter-spacing âm. Be Vietnam Pro KHÔNG có bản variable → nhúng BA file tĩnh 400/600/800 (≈95 KB; đủ 5 weight là 160 KB — quá trần
150 KB của PLAN 210926). Trang xin 500 thì trình duyệt lấy 400, xin 700 lấy 800 (luật khớp font CSS) — nét THẬT, không giả đậm.
Chữ trong SƠ ĐỒ/GRAPH (svg · .diagram-box · .mm · .graph) dùng **Lexend Deca**: mặc định Light 300, đậm = Regular 400 (user chốt
22/09/2026). Hai bản TĨNH cùng tên họ — mọi độ đậm < 500 ra Light, ≥ 500 ra Regular, `font-synthesis:none` cấm đậm giả — nên
"đậm = Lexend thường" là luật cứng (bản variable sẽ vẽ đúng 700 khi trang xin 700). `--font-mono` cho code GIỮ font hệ thống. Font được NHÚNG base64 vào từng trang (user chốt "nhúng hết"): trang mở bằng file://,
không mạng vẫn đúng font, không gọi ra fonts.googleapis.com. Luôn có fallback hệ thống phía sau.

    from html_font import head_css, FONT_TEXT       # generator: chèn head_css() vào <style> ĐẦU TIÊN của trang
    html_font.py --apply trang.html [trang2.html…]  # trang do SKILL/agent dựng tay: nhúng font tại chỗ (idempotent) — gọi SAU khi ghi trang
    html_font.py --check                            # data module khớp các file woff2?  (rc 1 khi lệch)
    html_font.py --rebuild <dir BeVietnamPro-*.ttf> [LexendDeca-VariableFont_wght.ttf]   # cắt lại subset + sinh lại data module (cần fontTools + brotli)

Dữ liệu base64 nằm ở `html_font_data.py` (file .py để đi cùng đợt copy `fdk/tools/*.py` xuống ~/.claude/harness — asset nhị phân
không được installer copy). Giấy phép SIL OFL 1.1: `assets/fonts/BeVietnamPro-NOTICE.txt`.
"""
from __future__ import annotations

import base64, hashlib, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONTS = HERE / "assets" / "fonts"
WEIGHTS = (400, 600, 800)
_SRC = {400: "Regular", 600: "SemiBold", 800: "ExtraBold"}
DATA = HERE / "html_font_data.py"
CHART_FAMILY = "Lexend Deca"
CHART_WEIGHTS = (300, 400)            # Light cho mặc định · Regular cho đậm
CHART_SCOPE = ":is(svg,.diagram-box,.mm,.graph)"

DISPLAY_FAMILY = "Newsreader"          # TIÊU ĐỀ (user chốt 22/09/2026 sau khi so 6 font: "E · Newsreader 600")
DISPLAY_WEIGHTS = (600,)
DISPLAY_OPSZ = 24                      # trục optical size cố định cho cỡ tiêu đề 20–32px
DISPLAY_FALLBACK = "Georgia,'Times New Roman',serif"

FAMILY = "Be Vietnam Pro"
FALLBACK = "-apple-system,BlinkMacSystemFont,'Segoe UI','Roboto','Helvetica Neue',sans-serif"
FONT_TEXT = f"'{FAMILY}',{FALLBACK}"
FONT_DISPLAY = f"'{DISPLAY_FAMILY}',{DISPLAY_FALLBACK}"
FONT_MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,monospace"
WEIGHT_TEXT = 400          # nội dung — như theme mẫu
WEIGHT_STRONG = 600        # <strong>/<b>/th
WEIGHT_HEADING = 600       # tiêu đề: Newsreader SemiBold (serif — 800 của sans cũ đọc nặng, user 22/09 "font này cũng lởm luôn")
TRACK_HEADING = "-.01em"   # CHỈ h1/h2: theme siết -.035 → -.055em ở tiêu đề lớn; h3/h4 (~16px) siết vào là dính chữ (soát ảnh 21/09)


def woff2(w: int) -> Path:
    return FONTS / f"BeVietnamPro-{w}-vi.woff2"


def display_woff2(w: int) -> Path:
    return FONTS / f"Newsreader-{w}-vi.woff2"


def chart_woff2(w: int) -> Path:
    return FONTS / f"LexendDeca-{w}-vi.woff2"


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


def display_face() -> str:
    b = _load_data().DISPLAY_B64
    return "".join(f"@font-face{{font-family:'{DISPLAY_FAMILY}';font-style:normal;font-weight:{w};font-display:swap;"
                   f"src:url(data:font/woff2;base64,{b[w]}) format('woff2')}}" for w in DISPLAY_WEIGHTS)


def chart_face() -> str:
    """Hai @font-face 'Lexend Deca' TĨNH: dải 1–499 → Light, 500–1000 → Regular (xin 600/700/bold vẫn ra Regular)."""
    b = _load_data().CHART_B64
    rng = {300: "1 499", 400: "500 1000"}
    return "".join(f"@font-face{{font-family:'{CHART_FAMILY}';font-style:normal;font-weight:{rng[w]};font-display:swap;"
                   f"src:url(data:font/woff2;base64,{b[w]}) format('woff2')}}" for w in CHART_WEIGHTS)


def chart_css() -> str:
    """Chữ trong sơ đồ/graph → họ 'Lexend Deca' (hai bản tĩnh). KHÔNG ép font-weight: độ đậm trang tự đặt được giữ nguyên, và
    chính dải của hai @font-face quyết nét — chữ thường (≤499) ra Light, chữ đậm (≥500) ra Regular. Bản đầu ép 300 rồi đẩy thẻ đậm
    lên 500 → rule chèn SAU thắng rule đậm cùng độ ưu tiên của trang, nhãn node graph mất đậm (soát ảnh 22/09/2026).
    Chữ code bên trong giữ mono. `font-synthesis:none` — không cho trình duyệt tô đậm giả trên bản Regular."""
    sc = CHART_SCOPE
    return f"{sc},{sc} :not(code,pre,kbd,samp,code *){{font-family:var(--font-chart);font-synthesis:none}}"


def head_css() -> str:
    """Khối CSS đặt ĐẦU <style> của trang: @font-face nhúng + token + mặc định cho nội dung. Trang có khai `--font-text`/
    `--font-display` riêng ở SAU thì phải bỏ đi (hoặc trỏ về var này) — html-font-lint gác."""
    return (font_face() + display_face() + chart_face() +
            f":root{{--font-chart:'{CHART_FAMILY}',{FALLBACK};--font-text:{FONT_TEXT};--font-display:{FONT_DISPLAY};--font-mono:{FONT_MONO};--fw-text:{WEIGHT_TEXT};--fw-strong:{WEIGHT_STRONG};--fw-heading:{WEIGHT_HEADING};--ls-heading:{TRACK_HEADING}}}"
            f"html,body{{font-family:var(--font-text);font-weight:var(--fw-text)}}"
            f"strong,b,th{{font-weight:var(--fw-strong)}}h1,h2,h3,h4{{font-family:var(--font-display);font-weight:var(--fw-heading)}}h1,h2{{letter-spacing:var(--ls-heading)}}"
            f"code,pre,kbd,samp{{font-family:var(--font-mono)}}"
            # thang tiêu đề MẶC ĐỊNH to → nhỏ (user 22/09/2026 "các cấp header phải thêm chuẩn từ to tới nhỏ"); :where = độ ưu tiên 0
            # → trang tự đặt vẫn thắng, và luật heading-scale của cổng chạy thật bắt khi thứ tự sai
            f":where(h1){{font-size:2.5rem;line-height:1.25}}:where(h2){{font-size:1.75rem;line-height:1.42;margin:40px 0 24px}}"
            f":where(h3){{font-size:1.375rem;line-height:1.55;margin:32px 0 16px}}:where(h4){{font-size:1.125rem;line-height:1.5;margin:24px 0 12px}}"
            f":where(p,ul,ol,blockquote){{margin:0 0 24px}}"
            + chart_css())


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
    body.append("}\n")
    cr = {w: chart_woff2(w).read_bytes() for w in CHART_WEIGHTS}
    body.append("CHART_SHA256 = {\n" + "".join(f'    {w}: "{hashlib.sha256(r).hexdigest()}",\n' for w, r in sorted(cr.items())) + "}\nCHART_B64 = {\n")
    for w, r in sorted(cr.items()):
        b64 = base64.b64encode(r).decode()
        body.append(f"    {w}: (\n" + "".join(f'        "{b64[i:i+120]}"\n' for i in range(0, len(b64), 120)) + "    ),\n")
    dr = {w: display_woff2(w).read_bytes() for w in DISPLAY_WEIGHTS}
    body.append("}\nDISPLAY_SHA256 = {\n" + "".join(f'    {w}: "{hashlib.sha256(r).hexdigest()}",\n' for w, r in sorted(dr.items())) + "}\nDISPLAY_B64 = {\n")
    for w, r in sorted(dr.items()):
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
    ok = ok and set(getattr(m, "DISPLAY_B64", {})) == set(DISPLAY_WEIGHTS)
    for w in DISPLAY_WEIGHTS if ok else ():
        raw = base64.b64decode(m.DISPLAY_B64[w])
        ok = ok and raw[:4] == b"wOF2" and hashlib.sha256(raw).hexdigest() == m.DISPLAY_SHA256[w]
        if display_woff2(w).exists():
            ok = ok and hashlib.sha256(display_woff2(w).read_bytes()).hexdigest() == m.DISPLAY_SHA256[w]
    ok = ok and set(getattr(m, "CHART_B64", {})) == set(CHART_WEIGHTS)
    for w in CHART_WEIGHTS if ok else ():
        raw = base64.b64decode(m.CHART_B64[w])
        ok = ok and raw[:4] == b"wOF2" and hashlib.sha256(raw).hexdigest() == m.CHART_SHA256[w]
        if chart_woff2(w).exists():
            ok = ok and hashlib.sha256(chart_woff2(w).read_bytes()).hexdigest() == m.CHART_SHA256[w]
    print("html_font: OK" if ok else "html_font: LỆCH — chạy html_font.py --sync (hoặc --rebuild)"); return 0 if ok else 1


def rebuild(src_dir: str, chart_src: str | None = None, display_src: str | None = None) -> int:
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
    lx = Path(chart_src or Path.home() / "Library/Fonts/LexendDeca-VariableFont_wght.ttf")
    from fontTools.varLib import instancer
    for w in CHART_WEIGHTS:                # chart: Lexend Deca TĨNH tại 300 / 400 (cắt glyph trước, cố định trục sau)
        f = TTFont(lx)
        opt = subset.Options(); opt.layout_features = ["kern", "liga", "mark", "mkmk", "ccmp", "locl"]; opt.name_IDs = [1, 2, 3, 4, 6, 13, 14]
        opt.notdef_outline = True
        s = subset.Subsetter(opt); s.populate(unicodes=uni); s.subset(f)
        tmp = chart_woff2(w).with_suffix(".tmp.ttf"); f.save(tmp)
        v = instancer.instantiateVariableFont(TTFont(tmp), {"wght": w}); v.flavor = "woff2"; v.save(chart_woff2(w)); tmp.unlink()
        print(f"→ {chart_woff2(w)} ({chart_woff2(w).stat().st_size/1024:.1f} KB)")
    nr = Path(display_src or Path.home() / "Library/Fonts/Newsreader.ttf")
    if nr.is_file():                       # TIÊU ĐỀ: Newsreader tĩnh tại wght 600 / opsz 24 (cắt glyph trước, cố định trục sau)
        for w in DISPLAY_WEIGHTS:
            f = TTFont(nr)
            opt = subset.Options(); opt.layout_features = ["kern", "liga", "mark", "mkmk", "ccmp", "locl"]; opt.name_IDs = [1, 2, 3, 4, 6, 13, 14]
            opt.notdef_outline = True
            sb = subset.Subsetter(opt); sb.populate(unicodes=uni); sb.subset(f)
            tmp = display_woff2(w).with_suffix(".tmp.ttf"); f.save(tmp)
            v = instancer.instantiateVariableFont(TTFont(tmp), {"wght": w, "opsz": DISPLAY_OPSZ}); v.flavor = "woff2"; v.save(display_woff2(w)); tmp.unlink()
            print(f"→ {display_woff2(w)} ({display_woff2(w).stat().st_size/1024:.1f} KB)")
    _write_data({w: woff2(w).read_bytes() for w in WEIGHTS}); print(f"→ {DATA}"); return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--rebuild" in a:
        rest = [x for x in a if not x.startswith("--")]
        sys.exit(rebuild(rest[0] if rest else str(Path.home() / "Library/Fonts"), rest[1] if len(rest) > 1 else None, rest[2] if len(rest) > 2 else None))
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
