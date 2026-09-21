#!/usr/bin/env python3
"""html_base — LỚP NỀN CHUNG cho mọi HTML do framework sinh ra: font (qua html_font) + token sáng/tối + thang khoảng cách +
thẻ kính không sọc + nút đổi giao diện có nhớ và chống nháy + MỘT quy ước viết hoa.

Vì sao có (20/09/2026): mỗi generator tự viết một bộ CSS nên không trang nào giống trang nào — 6 trang không có chế độ tối, 7 trang
không có nút đổi, sọc viền màu trên ~200 thẻ, viết HOA mỗi chỗ một kiểu; trong khi cổng bắt slop có sẵn lại không soi sản phẩm của
chính framework. Font đã gom về `html_font.py`; file này gom nốt phần còn lại theo đúng cách đó.

    from html_base import apply          # hoặc cứ gọi html_font.apply() như cũ — nó chuyển tiếp sang đây
    html = apply(html)                   # trang độc lập: token + (nếu trang CHƯA có) nút đổi giao diện + chống nháy
    html = apply(child, toggle=False)    # trang CON nhúng trong iframe: theo theme của trang mẹ, không có nút riêng

Hợp đồng với generator: bề mặt và chữ phải đi qua BIẾN (`--t1/--t2/--glass*/--border/--bg` hoặc `--ink/--ink2/--border`, hoặc bộ
`--ovs-*`). Kính viết `rgba(var(--ovs-glass-rgb),.7)` thay cho `rgba(255,255,255,.7)` để sang chế độ tối vẫn còn kính (nền kính đổi
sang xanh than thay vì trắng). Chữ nhấn dùng `var(--ovs-accent)` (đạt 4,5:1 ở cả hai chế độ) — `#0a84ff` chỉ dùng cho MẢNG màu. Màu ghi cứng (`#fff`, `#111`) thì lớp nền không đổi giúp được — cổng html-visual-gate sẽ bắt chữ chìm ở chế độ tối.

Quy ước viết hoa (DUY NHẤT): chỉ `.ovs-eyebrow` (nhãn nhỏ, tiêu đề nhóm, tiêu đề cột) được uppercase + letter-spacing. Tiêu đề, nút,
mục menu, thẻ: viết thường hoa đầu câu. Cấm sọc màu một cạnh; phân loại bằng `.ovs-dot` hoặc nền nhạt toàn thẻ.
"""
import importlib.util, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STYLE_ID, BOOT_ID, KEY = "ovs-base", "ovs-theme-boot", "ovs-theme"

LIGHT = {"bg": "#eaf2fd", "surface": "rgba(255,255,255,.72)", "surface2": "rgba(255,255,255,.9)", "ink": "#0f0f12", "ink2": "#454a57",
         "border": "rgba(30,90,170,.16)", "accent": "#0059b8", "glass-rgb": "255,255,255", "ok": "#0f6a2f", "warn": "#8a3f06", "bad": "#a01414",
         "ok-bg": "#dcfce7", "warn-bg": "#fdf0c4", "bad-bg": "#fee2e2", "accent-bg": "#dbeafe"}
DARK = {"bg": "#0c0f16", "surface": "rgba(24,30,44,.72)", "surface2": "rgba(30,38,56,.9)", "ink": "#e6e9f0", "ink2": "#c8cfdc",
        "border": "rgba(140,170,230,.2)", "accent": "#a9d0ff", "glass-rgb": "26,32,48", "ok": "#6ee7a0", "warn": "#fcd34d", "bad": "#fca5a5",
        "ok-bg": "rgba(74,222,128,.16)", "warn-bg": "rgba(251,191,36,.16)", "bad-bg": "rgba(248,113,113,.18)", "accent-bg": "rgba(125,184,255,.16)"}
# Hai họ biến đang dùng trong các generator (khảo sát 20/09/2026) → chế độ tối cho trang CHƯA có: gán lại đúng tên biến của họ.
_FAMILY_DARK = ("--t1:{ink};--t2:{ink2};--ink:{ink};--ink2:{ink2};--ink-soft:{ink2};--border:{border};--bg:{bg};--accent:{accent};"
                "--glass1:rgba(24,30,44,.55);--glass2:{surface};--glass3:{surface2};--glass-1:rgba(24,30,44,.55);--glass-2:{surface};--glass-3:{surface2};"
                "--edge-hi:rgba(255,255,255,.08);--edge:{accent};"
                # họ thứ ba (problem-tree): thang xanh dùng làm NỀN nhạt và CHỮ nhấn
                "--blue-050:rgba(24,30,44,.72);--blue-100:rgba(40,52,78,.8);--blue-500:{accent};--blue-700:{accent}")


def _vars(d: dict) -> str:
    return "".join(f"--ovs-{k}:{v};" for k, v in d.items())


def base_css(*, family_dark: bool) -> str:
    dark = _vars(DARK) + (_FAMILY_DARK.format(**DARK) if family_dark else "")
    return (
        f":root{{{_vars(LIGHT)}--sp-1:4px;--sp-2:8px;--sp-3:12px;--sp-4:16px;--sp-5:24px;--sp-6:32px;--ovs-r:14px;color-scheme:light}}"
        f"html[data-theme=dark]{{{dark}color-scheme:dark}}"
        + ("html[data-theme=dark] body{background:var(--ovs-bg);color:var(--ovs-ink)}" if family_dark else "")
        + ".ovs-card{background:var(--ovs-surface);border:1px solid var(--ovs-border);border-radius:var(--ovs-r);padding:var(--sp-4);"
          "backdrop-filter:blur(18px) saturate(1.15);-webkit-backdrop-filter:blur(18px) saturate(1.15)}"
          ".ovs-card+.ovs-card{margin-top:var(--sp-4)}"
          # code: tắt ligature (mono ligate `--` thành em-dash → người đọc gõ sai lệnh) — luật cũ của cổng tĩnh, nay có sẵn cho MỌI trang
          "pre,code,kbd,samp{font-variant-ligatures:none;font-feature-settings:\"liga\" 0,\"calt\" 0}"
          ".ovs-eyebrow{font-size:11px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--ovs-ink2)}"
          ".ovs-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--ovs-accent);margin-right:var(--sp-2);vertical-align:1px}"
          ".ovs-dot.ok{background:var(--ovs-ok)}.ovs-dot.warn{background:var(--ovs-warn)}.ovs-dot.bad{background:var(--ovs-bad)}"
          ".ovs-theme{position:fixed;right:16px;bottom:16px;z-index:2147483000;display:inline-flex;align-items:center;gap:8px;padding:8px 12px;"
          "border-radius:999px;border:1px solid var(--ovs-border);background:var(--ovs-surface2);color:var(--ovs-ink);font:inherit;font-size:12px;"
          "cursor:pointer;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px)}"
          ".ovs-theme:focus-visible{outline:2px solid var(--ovs-accent);outline-offset:2px}"
          ".ovs-theme i{width:14px;height:14px;border-radius:50%;box-shadow:inset -4px -3px 0 0 currentColor;display:inline-block}"
          "html[data-theme=dark] .ovs-theme i{box-shadow:none;background:currentColor}"
          "@media print{.ovs-theme{display:none}}")


# Chống nháy: chạy TRƯỚC khi trình duyệt vẽ — đặt data-theme từ lựa chọn đã nhớ, chưa có thì theo hệ điều hành.
BOOT_JS = ("(function(){try{var d=document.documentElement,s=localStorage.getItem('%s');"
           "d.setAttribute('data-theme',s||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'))}catch(e){"
           "document.documentElement.setAttribute('data-theme','light')}})()" % KEY)
TOGGLE_HTML = ('<button type="button" class="ovs-theme" role="switch" aria-label="Đổi giao diện sáng / tối" title="Đổi giao diện sáng / tối">'
               '<i aria-hidden="true"></i><span></span></button>')
TOGGLE_JS = ("(function(){var d=document.documentElement,b=document.querySelector('.ovs-theme');if(!b)return;"
             "function paint(){var k=d.getAttribute('data-theme')==='dark';b.setAttribute('aria-checked',k?'true':'false');"
             "b.lastChild.textContent=k?'Tối':'Sáng';"
             "[].forEach.call(document.querySelectorAll('iframe'),function(f){try{f.contentWindow.postMessage({ovsTheme:k?'dark':'light'},'*')}catch(e){}})}"
             "b.addEventListener('click',function(){var n=d.getAttribute('data-theme')==='dark'?'light':'dark';d.setAttribute('data-theme',n);"
             "try{localStorage.setItem('%s',n)}catch(e){}paint()});paint();window.addEventListener('load',paint)})()" % KEY)
# Trang CON trong iframe: không có nút; lấy theme của trang mẹ lúc mở (cùng origin thì đọc thẳng) và nghe postMessage khi mẹ đổi.
FOLLOW_JS = ("(function(){var d=document.documentElement;function set(t){if(t==='dark'||t==='light')d.setAttribute('data-theme',t)}"
             "try{set(parent.document.documentElement.getAttribute('data-theme'))}catch(e){}"
             "if(!d.getAttribute('data-theme'))set(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');"
             "window.addEventListener('message',function(e){if(e.data&&e.data.ovsTheme)set(e.data.ovsTheme)})})()")


def _font_mod():
    s = importlib.util.spec_from_file_location("ovs_html_font", HERE / "html_font.py"); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def has_own_theme(html: str) -> bool:
    """Trang đã tự có chế độ tối + nút đổi (graph-viz, overstack, control-room) → KHÔNG chèn nút thứ hai, không ghi đè token tối của nó."""
    head = re.split(r"</head\s*>", html, 1, flags=re.I)[0]
    dark_css = bool(re.search(r"\[data-theme\s*=\s*[\"']?dark|prefers-color-scheme\s*:\s*dark", head, re.I))
    toggler = bool(re.search(r"theme-switch|theme-toggle|themeToggle", html)) and "localStorage" in html
    return dark_css and toggler


def apply(html: str, *, toggle: bool = True, fix=None) -> str:
    if f'id="{STYLE_ID}"' in html:
        return html
    # Tự VÁ slop máy-làm-được trước khi gắn lớp nền (mặc định BẬT khi có html-slop-fix.py cạnh file này — repo engine không mang
    # công cụ vá nên ở đó tự tắt): generator nào còn màu ghi cứng/sọc/gradient-text cũng ra trang sạch, không chờ ai nhớ chạy tay.
    fixer = HERE / "html-slop-fix.py"
    if (fix is None and fixer.is_file()) or fix:
        s = importlib.util.spec_from_file_location("ovs_slop_fix", fixer); fm = importlib.util.module_from_spec(s); s.loader.exec_module(fm)
        html = fm.fix_markup(html, [])
    m = re.search(r"</head\s*>", html, re.I)
    if not m:
        # HTML5 cho phép BỎ thẻ <head>: trang agent viết tay hay chỉ có <!doctype> + <title> + <style>.
        # Chèn ngay trước phần tử đầu tiên KHÔNG thuộc head (style/body/nội dung) — chỗ đó đúng là cuối head ngầm.
        m = re.search(r"<style\b|<body\b|<main\b|<h1\b|<div\b", html, re.I)
        if not m:
            return html
        html = html[:m.start()] + "</head>" + html[m.start():]
        m = re.search(r"</head\s*>", html, re.I)
    own = has_own_theme(html)
    head_dark = bool(re.search(r"\[data-theme\s*=\s*[\"']?dark|prefers-color-scheme\s*:\s*dark", html[:m.start()], re.I))
    font = _font_mod()
    html = font.apply(html, _from_base=True)                        # font + trỏ stack hệ thống trong <head> về token
    m = re.search(r"</head\s*>", html, re.I)
    html = html[:m.start()] + f'<style id="{STYLE_ID}">{base_css(family_dark=not head_dark)}</style>' + html[m.start():]
    if own:
        return html
    ho = re.search(r"<head\b[^>]*>", html, re.I)
    boot = FOLLOW_JS if not toggle else BOOT_JS
    # head NGẦM ĐỊNH: không có thẻ mở <head> thì chèn boot NGAY SAU <!doctype>/<html> — phải chạy TRƯỚC style
    # để trang không nháy sai chế độ (chính lý do boot nằm đầu head).
    at = ho.end() if ho else (lambda m: m.end() if m else 0)(
        re.search(r"<html\b[^>]*>|<!doctype[^>]*>", html, re.I))
    html = html[:at] + f'<script id="{BOOT_ID}">{boot}</script>' + html[at:]
    if not toggle:                                                  # trang con: đánh dấu để cổng biết nó theo trang mẹ
        return re.sub(r"<html\b", "<html data-ovs-theme-follow", html, 1, flags=re.I)
    bodies = list(re.finditer(r"</body\s*>", html, re.I))
    if bodies:                                                      # </body> CUỐI CÙNG — cái trước có thể nằm trong srcdoc/JS
        i = bodies[-1].start()
        html = html[:i] + TOGGLE_HTML + f"<script>{TOGGLE_JS}</script>" + html[i:]
    return html


def to_follow(html: str) -> str:
    """Trang ĐỘC LẬP đã gắn lớp nền → bản NHÚNG trong iframe: bỏ nút riêng, đổi script chống nháy thành script theo-trang-mẹ.
    Dùng khi một generator nhúng trang khác qua `srcdoc` (overstack nhúng memory-map, skill-whiteboard): một trang chỉ có MỘT nút đổi giao diện."""
    if "data-ovs-theme-follow" in html:
        return html
    html = html.replace(TOGGLE_HTML + f"<script>{TOGGLE_JS}</script>", "")
    if f'id="{BOOT_ID}"' in html:
        html = re.sub(rf'<script id="{BOOT_ID}">.*?</script>', lambda m: f'<script id="{BOOT_ID}">{FOLLOW_JS}</script>', html, 1, flags=re.S)
    else:
        ho = re.search(r"<head\b[^>]*>", html, re.I)
        if ho:
            html = html[:ho.end()] + f'<script id="{BOOT_ID}">{FOLLOW_JS}</script>' + html[ho.end():]
    return re.sub(r"<html\b", "<html data-ovs-theme-follow", html, 1, flags=re.I)


# Trang MẸ có toggle RIÊNG (overstack, graph-viz): báo theme cho mọi iframe con mỗi khi data-theme đổi và khi iframe vừa tải xong.
# (iframe sandbox không cùng origin nên con KHÔNG đọc được trang mẹ — chỉ còn đường postMessage.)
PARENT_NOTIFY_JS = ("(function(){var d=document.documentElement;function cur(){var t=d.getAttribute('data-theme');"
                    "return t==='dark'||t==='light'?t:(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light')}"
                    "function tell(f){try{f.contentWindow.postMessage({ovsTheme:cur()},'*')}catch(e){}}"
                    "function all(){[].forEach.call(document.querySelectorAll('iframe'),tell)}"
                    "new MutationObserver(all).observe(d,{attributes:true,attributeFilter:['data-theme']});"
                    "[].forEach.call(document.querySelectorAll('iframe'),function(f){f.addEventListener('load',function(){tell(f)})});"
                    "window.addEventListener('load',all);all()})()")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--apply" in a:
        for f in [Path(x) for x in a if not x.startswith("--")]:
            src = f.read_text(encoding="utf-8"); out = apply(src, toggle="--follow" not in a)
            print(f"{'✓' if out != src else '·'} {f}"); f.write_text(out, encoding="utf-8")
    else:
        print(__doc__)
