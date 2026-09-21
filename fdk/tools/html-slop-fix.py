#!/usr/bin/env python3
"""html-slop-fix — vá MÁY-LÀM-ĐƯỢC cho một trang HTML đã có sẵn (trang agent dựng tay, trang cũ không còn khuôn để sinh lại).

Chỉ đụng CSS trong các khối <style> của <head> (không đụng JS, không đụng srcdoc, không đụng văn xuôi). Các phép vá, đúng thứ tự:
  1. gradient-text      `background-clip:text` + nền gradient + chữ trong suốt → chữ màu đặc `var(--ovs-accent)`
  2. sọc một cạnh       `border-left/right: ≥3px solid <màu>` → bỏ khai báo · luật `::before/::after` rộng ≤6px cao 100% → bỏ luật
  3. kính               `rgba(R,G,B,A)` với R,G,B ≥ 230 (trắng và trắng-pha-xanh) → `rgba(var(--ovs-glass-rgb,255,255,255),A)` (tối vẫn còn kính)
  4. chữ nhấn           `color:#0a84ff | #0a5ec7 | #5856d6` → `var(--ovs-accent)` (đạt 4,5:1 ở cả hai chế độ; #0a84ff chỉ để tô MẢNG)
  5. chữ nhỏ hạ opacity `small{…opacity:.N}` → bỏ opacity (chữ phụ đã nhạt sẵn, hạ nữa là chìm)
     màu HEX ghi cứng  nền gần-trắng → `var(--ovs-surface2,…)` · chữ đen/xám → `var(--ovs-ink/--ovs-ink2,…)`; màu bão hoà giữ nguyên
  6. lớp nền            html_base.apply(): token sáng/tối, nút đổi giao diện nếu trang chưa có, chống nháy, font, tắt ligature trong code
Xong thì chạy lại cổng tĩnh và IN những gì còn lại cần NGƯỜI sửa — không giả vờ sạch.

    html-slop-fix.py trang.html [trang2.html …] [--dry-run] [--follow]      # --follow: trang CON nhúng iframe (theo theme trang mẹ)
Exit: 0 mọi trang sạch cổng tĩnh sau vá · 2 còn finding cần người · 1 lỗi đọc/ghi.  Idempotent.
"""
import importlib.util, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name, fname):
    s = importlib.util.spec_from_file_location(name, HERE / fname); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def fix_css(css: str, log: list) -> str:
    def note(n, what):
        if n:
            log.append(f"{n}× {what}")
    fap = _load("fap_fix", "frontend-antipattern.py")
    out = []
    data = {}                                                     # giữ nguyên data-URI (font nhúng) — không cho regex nào chạm vào
    css = re.sub(r"url\(\s*data:[^)]*\)", lambda m: data.setdefault(f"url(__D{len(data)}__)", m.group(0)) and f"url(__D{len(data) - 1}__)", css)
    n_grad = n_stripe = n_rule = 0
    for chunk in re.split(r"(\})", css):
        if "{" not in chunk:
            out.append(chunk); continue
        pre, decl = chunk.rsplit("{", 1)
        sel = pre.rsplit("{", 1)[-1].rsplit(";", 1)[-1]
        if re.search(r"background-clip\s*:\s*text", decl, re.I):
            decl = re.sub(r"(?:-webkit-)?background-clip\s*:\s*text\s*;?", "", decl, flags=re.I)
            decl = re.sub(r"-webkit-text-fill-color\s*:\s*transparent\s*;?", "", decl, flags=re.I)
            decl = re.sub(r"(?<![-\w])color\s*:\s*transparent\s*;?", "", decl, flags=re.I)
            decl = re.sub(r"background(?:-image)?\s*:\s*(?:linear|radial|conic)-gradient\((?:[^()]|\([^()]*\))*\)\s*;?", "", decl, flags=re.I)
            decl = decl.rstrip("; \n") + ";color:var(--ovs-accent,#0059b8)"; n_grad += 1
        if re.search(r"::?(?:before|after)\b", sel) and re.search(r"(?<![\w-])width\s*:\s*[1-6]px", decl) and \
                (re.search(r"height\s*:\s*100%", decl) or (re.search(r"(?<![\w-])top\s*:\s*0", decl) and re.search(r"bottom\s*:\s*0", decl))):
            bg = re.search(r"background(?:-color)?\s*:\s*([^;}]+)", decl)
            if bg and not fap._is_neutral_color(bg.group(1)):
                n_rule += 1; out.append(pre.rsplit(sel, 1)[0] if pre.endswith(sel) else pre[: len(pre) - len(sel)]); out.append("__DROP__"); continue
        if not re.search(r"blockquote|\bhr\b|\btable\b|\bt[dh]\b", sel, re.I):
            def drop(m):
                nonlocal n_stripe
                if float(m.group(1)) >= 3 and not fap._is_neutral_color(m.group(2)):
                    n_stripe += 1; return ""
                return m.group(0)
            decl = re.sub(r"border-(?:left|right|inline-start)\s*:\s*(\d+(?:\.\d+)?)px\s+solid\s*([^;}]*);?", drop, decl, flags=re.I)
        out.append(pre + "{" + decl)
    css = "".join(out)
    css = re.sub(r"__DROP__\}", "", css)                           # luật sọc ::before đã bỏ: nuốt luôn dấu } của nó
    note(n_grad, "gradient-text → màu đặc"); note(n_stripe, "border sọc một cạnh"); note(n_rule, "luật ::before/::after vẽ sọc")
    css, n = re.subn(r"rgba\(\s*2[3-5]\d\s*,\s*2[3-5]\d\s*,\s*2[3-5]\d\s*,", "rgba(var(--ovs-glass-rgb,255,255,255),", css); note(n, "kính trắng → token kính")
    css, n = re.subn(r"(?<![-\w])color\s*:\s*#(?:0a84ff|0a5ec7|5856d6)\b", "color:var(--ovs-accent,#0059b8)", css, flags=re.I); note(n, "chữ nhấn → --ovs-accent")
    css, n = re.subn(r"(small\s*\{[^}]*?)opacity\s*:\s*\.\d+\s*;?", r"\1", css); note(n, "chữ nhỏ bỏ opacity")
    # màu HEX ghi cứng: nền gần-trắng → token bề mặt; chữ đen/xám (ít bão hoà) → token mực. Màu bão hoà (trạng thái, thương hiệu) GIỮ NGUYÊN.
    def _hex(h):
        h = h.lstrip("#"); h = "".join(c * 2 for c in h[:3]) if len(h) in (3, 4) else h[:6]
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        lin = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
        mx, mn = max(r, g, b), min(r, g, b)
        return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b), (0 if mx == 0 else (mx - mn) / mx)
    import colorsys
    cnt = {"bg": 0, "ink": 0, "sem": 0}
    def sem(hexs):                      # sắc độ → vai ngữ nghĩa (token có giá trị riêng cho sáng/tối nên đạt tương phản ở cả hai)
        h = hexs.lstrip("#"); h = "".join(c * 2 for c in h[:3]) if len(h) in (3, 4) else h[:6]
        hue = colorsys.rgb_to_hsv(*(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))[0] * 360
        return "bad" if (hue >= 345 or hue < 18) else "warn" if hue < 65 else "ok" if hue < 170 else "accent"
    def bg(m):
        L, S = _hex(m.group(2))
        if L > 0.70 and S < 0.10:                       # xám rất nhạt (#e2e8f0) cũng là BỀ MẶT, không phải màu nhấn
            cnt["bg"] += 1; return f"{m.group(1)}var(--ovs-surface2,{m.group(2)})"
        if L > 0.72 and S >= 0.10:
            cnt["sem"] += 1; return f"{m.group(1)}var(--ovs-{sem(m.group(2))}-bg,{m.group(2)})"
        return m.group(0)
    css = re.sub(r"(background(?:-color)?\s*:\s*)(?:var\(--ovs-surface2,\s*)?(#[0-9a-fA-F]{3,8})\)?(?=\s*[;}!])", bg, css)
    css, n = re.subn(r"(background(?:-color)?\s*:\s*)white(?=\s*[;}!])", r"\1var(--ovs-surface2,#fff)", css); cnt["bg"] += n
    def tint(m):                        # rgba pha màu rất nhạt (kênh ≥ 200 nhưng không phải trắng) → nền ngữ nghĩa
        r, g, bb = (int(x) for x in m.group(2, 3, 4)); hx = "#%02x%02x%02x" % (r, g, bb); L, S = _hex(hx)
        if min(r, g, bb) >= 200 and S >= 0.06 and not (min(r, g, bb) >= 230):
            cnt["sem"] += 1; return f"{m.group(1)}var(--ovs-{sem(hx)}-bg,{m.group(0)[len(m.group(1)):]})"
        return m.group(0)
    css = re.sub(r"(background(?:-color)?\s*:\s*)rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*[\d.]+\s*)?\)(?=\s*[;}!])", tint, css)
    def ink(m):
        L, S = _hex(m.group(2))
        if S < 0.72 and L < 0.10:
            cnt["ink"] += 1; return f"{m.group(1)}var(--ovs-ink,{m.group(2)})"
        if S < 0.55 and L < 0.50:
            cnt["ink"] += 1; return f"{m.group(1)}var(--ovs-ink2,{m.group(2)})"
        if S >= 0.55:                   # màu NHẤN dùng làm chữ: trộn với màu mực → GIỮ sắc độ của mục, tự đậm lên ở sáng / nhạt đi ở tối
            cnt["sem"] += 1; return f"{m.group(1)}color-mix(in oklab,{m.group(2)} 52%,var(--ovs-ink,#0f0f12))"
        return m.group(0)
    css = re.sub(r"((?<![-\w])color\s*:\s*)(#[0-9a-fA-F]{3,8})(?=\s*[;}!\"'])", ink, css)
    note(cnt["bg"], "nền hex gần-trắng → --ovs-surface2"); note(cnt["ink"], "chữ hex đen/xám → --ovs-ink/--ovs-ink2"); note(cnt["sem"], "màu nhấn/trạng thái → trộn mực (chữ) · nền pha → token ngữ nghĩa")
    for k, v in data.items():
        css = css.replace(k, v)
    return css


def fix_markup(html: str, log: list) -> str:
    """Chỉ VÁ (CSS trong <head> + style="" trong body), KHÔNG gắn lớp nền — html_base.apply gọi hàm này trước khi chèn token."""
    m = re.search(r"</head\s*>", html, re.I)
    if not m:
        # head NGẦM ĐỊNH (HTML5 cho phép bỏ thẻ): coi mọi thứ trước phần tử nội dung đầu tiên là head.
        m = re.search(r"<style\b|<body\b|<main\b|<h1\b|<div\b", html, re.I)
        if not m:
            log.append("không có </head> — bỏ qua"); return html
    head, rest = html[:m.start()], html[m.start():]
    # Khối <style> có thể nằm NGOÀI head (trang head ngầm định, hoặc style đặt cuối body). Vá cả hai phần.
    # An toàn với iframe srcdoc: nội dung srcdoc là HTML đã escape (&lt;style&gt;) nên regex này không chạm tới.
    sty = lambda s: re.sub(r"(<style\b(?![^>]*\bid=\"ovs-)[^>]*>)(.*?)(</style\s*>)",
                           lambda x: x.group(1) + fix_css(x.group(2), log) + x.group(3), s, flags=re.I | re.S)
    head = sty(head)
    rest = sty(rest)
    def inline(seg):
        return re.sub(r'(style\s*=\s*")([^"]*)(")', lambda a: a.group(1) + fix_css("x{" + a.group(2) + "}", [])[2:-1] + a.group(3), seg)
    parts = re.split(r"(<script\b.*?</script\s*>)", rest, flags=re.I | re.S)
    rest = "".join(p if p.lower().startswith("<script") else inline(p) for p in parts)
    return head + rest


def fix_page(html: str, *, follow: bool, log: list) -> str:
    return _load("hb_fix", "html_base.py").apply(fix_markup(html, log), toggle=not follow, fix=False)


def main(argv=None) -> int:
    a = list(sys.argv[1:] if argv is None else argv)
    dry, follow = "--dry-run" in a, "--follow" in a
    files = [Path(x) for x in a if not x.startswith("--")]
    if not files:
        print(__doc__); return 1
    fap = _load("fap_main", "frontend-antipattern.py"); left = 0
    for f in files:
        try:
            src = f.read_text(encoding="utf-8")
        except OSError as e:
            print(f"✗ {f}: {e}"); return 1
        log = []; out = fix_page(src, follow=follow, log=log)
        if out != src and not dry:
            f.write_text(out, encoding="utf-8")
        rest = [x for x in fap._scan_text(out) if x["level"] == "FAIL"]
        left += len(rest)
        print(f"{'✓' if out != src else '·'} {f.name}: " + ("; ".join(log) or "không có gì để vá") + (f" · CÒN {len(rest)} FAIL cần người" if rest else " · sạch cổng tĩnh"))
        for x in rest[:4]:
            print(f"      ↳ {x.get('rule') or ''} {x['msg'][:110]}")
    return 2 if left else 0


if __name__ == "__main__":
    sys.exit(main())
