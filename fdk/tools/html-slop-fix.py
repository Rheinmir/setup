#!/usr/bin/env python3
"""html-slop-fix — vá MÁY-LÀM-ĐƯỢC cho một trang HTML đã có sẵn (trang agent dựng tay, trang cũ không còn khuôn để sinh lại).

Chỉ đụng CSS trong các khối <style> của <head> (không đụng JS, không đụng srcdoc, không đụng văn xuôi). Các phép vá, đúng thứ tự:
  1. gradient-text      `background-clip:text` + nền gradient + chữ trong suốt → chữ màu đặc `var(--ovs-accent)`
  2. sọc một cạnh       `border-left/right: ≥3px solid <màu>` → bỏ khai báo · luật `::before/::after` rộng ≤6px cao 100% → bỏ luật
  3. kính               `rgba(R,G,B,A)` với R,G,B ≥ 230 (trắng và trắng-pha-xanh) → `rgba(var(--ovs-glass-rgb,255,255,255),A)` (tối vẫn còn kính)
  4. chữ nhấn           `color:#0a84ff | #0a5ec7 | #5856d6` → `var(--ovs-accent)` (đạt 4,5:1 ở cả hai chế độ; #0a84ff chỉ để tô MẢNG)
  5. chữ nhỏ hạ opacity `small{…opacity:.N}` → bỏ opacity (chữ phụ đã nhạt sẵn, hạ nữa là chìm)
     màu HEX ghi cứng  nền gần-trắng → `var(--ovs-surface2,…)` · chữ đen/xám → `var(--ovs-ink/--ovs-ink2,…)`; màu bão hoà giữ nguyên
  7. khoảng cách        padding/margin/gap `px`/`rem` ngoài thang (2·4·8·12·16·20·24·32·40·48·64·80·96) → bậc GẦN NHẤT (hoà → bậc
                        lớn hơn: chật là triệu chứng slop); line-height < 1,5 trên luật chữ NỘI DUNG (p, li, dd, td, body, .desc…) →
                        `var(--lh-body,1.6)`. Nguồn chuẩn: fdk/wiki/sources/220926-spacing-standards.md (Carbon, Tailwind, WCAG, USWDS).
  8. chữ hoa đầu câu    tiêu đề h1–h6, nút, summary, th, label, tab, tên trang (.brand/.logo), mục <a> trong <nav> bắt đầu bằng chữ
                        thường → viết hoa chữ đầu. Tha định danh (có số hoặc - _ . / : @), tên riêng (overstack, npm, git…), chữ trong
                        code/pre/script. Cùng quy tắc với luật `sentence-case` của cổng chạy thật (user 22/09/2026).
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


SCALE_PX = (2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96)
_SPACE = re.compile(r"((?<![\w-])(?:padding|margin|gap|row-gap|column-gap)(?:-(?:top|right|bottom|left|inline|block)(?:-(?:start|end))?)?\s*:\s*)([^;}]+)", re.I)
_BODY_SEL = re.compile(r"(?:^|[\s>+~,(])(?:p|li|dd|td|body|blockquote)(?![\w-])|\.(?:desc|description|lead|body|prose)(?![\w-])", re.I)   # theo TỪ (review t8: .text-muted/.lead-in/.summary bị nâng nhầm)
_NOT_BODY = re.compile(r"\bh[1-6]\b|btn|button|badge|chip|tag|pill|nav|sidebar|menu|toolbar|label|logo|brand|kbd|code|icon|num|count|::?(?:before|after)", re.I)


def snap(px: float) -> float:
    """Bậc gần nhất của thang; giữ giá trị < 2px (viền/khe mảnh); > 96 → bội số 16 gần nhất. Hoà → bậc lớn hơn."""
    a = abs(px)
    if a < 2:                                  # viền/khe mảnh (0,5–1,9px, hay sinh từ rem) — không phải khoảng cách, giữ nguyên
        return px
    if a > 96:
        v = round(a / 16) * 16
    else:
        v = min(SCALE_PX, key=lambda s: (abs(s - a), -s if px >= 0 else s))   # hoà: dương → lớn hơn (thoáng), âm → gần 0 (review t8)
    return v if px >= 0 else -v


def _snap_value(val: str) -> tuple:
    if re.search(r"calc\(|clamp\(|min\(|max\(|var\(", val):
        return val, 0
    n = 0
    def one(m):
        nonlocal n
        num, unit = float(m.group(1)), m.group(2)
        px = num * (16 if unit == "rem" else 1)
        sp = snap(px)
        if abs(sp - px) < 0.01:
            return m.group(0)
        n += 1
        return f"{sp / 16:g}rem" if unit == "rem" else f"{sp:g}px"
    return re.sub(r"(-?\d*\.?\d+)(px|rem)\b", one, val), n


def fix_spacing(css: str) -> tuple:
    """Phép vá 7 — trả (css, số giá trị bẻ về thang, số line-height nâng)."""
    ns = nl = 0
    def sp(m):
        nonlocal ns
        v, k = _snap_value(m.group(2)); ns += k
        return m.group(1) + v
    out = []
    for chunk in re.split(r"(\})", css):
        if "{" not in chunk:
            out.append(chunk); continue
        pre, decl = chunk.rsplit("{", 1)
        sel = pre.rsplit("{", 1)[-1].rsplit(";", 1)[-1]
        decl = _SPACE.sub(sp, decl)
        if _BODY_SEL.search(sel) and not _NOT_BODY.search(sel):
            def lh(m):
                nonlocal nl
                if float(m.group(1)) < 1.5:
                    nl += 1; return m.group(0)[: m.start(1) - m.start(0)] + "var(--lh-body,1.6)"
                return m.group(0)
            decl = re.sub(r"(?<![\w-])line-height\s*:\s*(\d*\.?\d+)(?=\s*(?:;|$|!))", lh, decl)
        out.append(pre + "{" + decl)
    return "".join(out), ns, nl


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
        # cùng khối khai báo có NỀN màu cố định (viên trạng thái: ink_on() đã chọn chữ đạt tương phản với nền đó) → giữ nguyên:
        # token --ovs-ink đổi theo theme sẽ ra chữ sáng trên nền cam ở chế độ tối (control-room 22/09: 2,26:1).
        a = max(css.rfind(c, 0, m.start()) for c in '{"\'')
        z = min([i for i in (css.find(c, m.end()) for c in '}"\'') if i >= 0] or [len(css)])
        fb = re.search(r"background(?:-color)?\s*:\s*(#[0-9a-fA-F]{3,8})\b", css[a:z])
        if fb and _hex(fb.group(1))[0] <= 0.70:
            return m.group(0)
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
    css, ns, nl = fix_spacing(css)
    note(ns, "khoảng cách ngoài thang → bậc gần nhất"); note(nl, "line-height chữ nội dung < 1,5 → --lh-body")
    for k, v in data.items():
        css = css.replace(k, v)
    return css


_PROTECT = re.compile(r"<script\b.*?</script\s*>|<pre\b.*?</pre\s*>|<code\b.*?</code\s*>|<textarea\b.*?</textarea\s*>"
                      r"|\ssrcdoc\s*=\s*(?:\"[^\"]*\"|'[^']*')", re.I | re.S)
_INLINE = re.compile(r"(<[a-zA-Z][\w-]*\b[^<>]*?\sstyle\s*=\s*\")([^\"]*)(\")")   # CHỈ thuộc tính style trong THẺ MỞ (không data-style, không văn xuôi)


_IDENT = re.compile(r"[\d\-_./:@]")
_BRANDS = {"overstack", "orca", "llmwiki", "npm", "npx", "git", "gh", "curl", "claude", "iphone", "macos", "ios"}
_CASE_TAG = re.compile(r"(<label\b[^>]*>\s*<input\b[^>]*>\s*|<(?:h[1-6]|button|summary|th|legend|label)\b[^>]*>|<(?:div|span|a)\b[^>]*class=\"[^\"]*\b(?:brand|logo)\b[^\"]*\"[^>]*>"
                       r"|<[a-z]+\b[^>]*role=\"tab\"[^>]*>)([^<]*)", re.I)


def _cap(text: str) -> str:
    m = re.match(r"^([^\w]*)(\w)", text, re.U)                  # bỏ qua ký hiệu/emoji/khoảng trắng đầu (⤢, ←, ✓…)
    if not m or not m.group(2).isalpha() or not m.group(2).islower():
        return text
    tok = text[m.start(2):].split()[0] if text[m.start(2):].split() else ""
    if _IDENT.search(tok) or re.sub(r"[^\w]", "", tok.lower()) in _BRANDS:
        return text
    return text[:m.start(2)] + m.group(2).upper() + text[m.end(2):]


def fix_case(html: str) -> tuple:
    """Phép vá 8 — chạy trên HTML ĐÃ chừa script/pre/code/srcdoc. Trả (html, số chỗ sửa)."""
    n = 0
    def one(m):
        nonlocal n
        if 'data-case="keep"' in m.group(1):                      # lối thoát: tên riêng muốn giữ chữ thường
            return m.group(0)
        t = _cap(m.group(2)); n += t != m.group(2)
        return m.group(1) + t
    html = _CASE_TAG.sub(one, html)
    def nav(m):                                                    # <a> chỉ khi nằm trong <nav>
        return re.sub(r"(<a\b[^>]*>)([^<]*)", lambda a: a.group(0) if 'data-case="keep"' in a.group(1) else a.group(1) + _cap(a.group(2)), m.group(0))
    before = html
    html = re.sub(r"<nav\b.*?</nav>", nav, html, flags=re.S | re.I)
    n += sum(1 for x, y in zip(re.findall(r"<nav\b.*?</nav>", before, re.S | re.I), re.findall(r"<nav\b.*?</nav>", html, re.S | re.I)) if x != y)
    return html, n


def fix_markup(html: str, log: list) -> str:
    """Chỉ VÁ (CSS trong <style> + style="" trong thẻ mở), KHÔNG gắn lớp nền — html_base.apply gọi hàm này trước khi chèn token.
    Chừa nguyên script · pre · code · textarea · srcdoc (review t8 22/09/2026: bản trước vá cả `<style>` nằm trong chuỗi JS, ví dụ
    code đã escape và srcdoc nháy đơn — nay html_base gọi hàm này MỖI lần làm mới trang nên phải tuyệt đối không chạm chúng)."""
    keep = []
    html = _PROTECT.sub(lambda m: keep.append(m.group(0)) or f"\x00P{len(keep) - 1}\x00", html)
    html = re.sub(r"(<style\b(?![^>]*\bid=\"ovs-)[^>]*>)(.*?)(</style\s*>)",
                  lambda x: x.group(1) + fix_css(x.group(2), log) + x.group(3), html, flags=re.I | re.S)
    html = _INLINE.sub(lambda a: a.group(1) + fix_css("x{" + a.group(2) + "}", [])[2:-1] + a.group(3), html)
    html, nc = fix_case(html)
    if nc:
        log.append(f"{nc}× chữ thường đầu nhãn/tiêu đề → viết hoa")
    return re.sub(r"\x00P(\d+)\x00", lambda m: keep[int(m.group(1))], html)


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
