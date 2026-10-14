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

Quy ước viết hoa (DUY NHẤT): chỉ `.ovs-eyebrow` (nhãn nhỏ, tiêu đề nhóm, tiêu đề cột) được uppercase, giãn chữ tối đa .02em (luật wide-tracking 30/09/2026 — giãn rộng làm mắt phải nhảy từng chữ). Tiêu đề, nút,
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
    F = "input:is(:not([type]),[type=text],[type=search],[type=email],[type=url],[type=tel],[type=password],[type=number]),textarea"
    H = "input:is(:not([type]),[type=text],[type=search],[type=email],[type=url],[type=tel],[type=password],[type=number]):hover,textarea:hover"
    Fo = "input:is(:not([type]),[type=text],[type=search],[type=email],[type=url],[type=tel],[type=password],[type=number]):focus,textarea:focus"
    I = "input:is(:not([type]),[type=text],[type=search],[type=email],[type=url],[type=tel],[type=password],[type=number])[aria-invalid=true],textarea[aria-invalid=true]"
    IF = "input:is(:not([type]),[type=text],[type=search],[type=email],[type=url],[type=tel],[type=password],[type=number])[aria-invalid=true]:focus,textarea[aria-invalid=true]:focus"
    dark = _vars(DARK) + (_FAMILY_DARK.format(**DARK) if family_dark else "")
    return (
        f":root{{{_vars(LIGHT)}--sp-1:4px;--sp-2:8px;--sp-3:12px;--sp-4:16px;--sp-5:24px;--sp-6:32px;--sp-7:40px;--sp-8:48px;--sp-9:64px;--sp-10:80px;--sp-11:96px;"
        f"--lh-body:1.75;--lh-heading:1.25;--measure:35em;--ovs-r:14px;color-scheme:light}}"
        # nhịp chữ mặc định (PLAN 220926-spacing-system, chuẩn WCAG 1.4.12/USWDS): :where = độ ưu tiên 0 → trang tự đặt vẫn thắng
        ":where(p,li,dd,blockquote){line-height:var(--lh-body)}:where(h1,h2,h3){line-height:var(--lh-heading)}"
        # sentence-case cho MỌI tiêu đề, kể cả tiêu đề JS sinh lúc chạy (phép vá HTML không với tới) — :where = trang tự đặt vẫn thắng
        ":where(h1,h2,h3,h4,h5,h6,summary,legend)::first-letter{text-transform:uppercase}"
        f"html[data-theme=dark]{{{dark}color-scheme:dark}}"
        + ("html[data-theme=dark] body{background:var(--ovs-bg);color:var(--ovs-ink)}" if family_dark else "")
        + ".ovs-card{background:var(--ovs-surface);border:1px solid var(--ovs-border);border-radius:var(--ovs-r);padding:var(--sp-4);"
          "backdrop-filter:blur(18px) saturate(1.15);-webkit-backdrop-filter:blur(18px) saturate(1.15)}"
          ".ovs-card+.ovs-card{margin-top:var(--sp-4)}"
          # chữ dài chia hai cột (user 01/10/2026): html-slop-fix bọc chuỗi đoạn dài vào .ovs-cols; khung hẹp hơn hai cột 24em tự về một cột
          # user 01/10/2026 lần 2: chữ vẫn to → chia 2-3-4 khối theo bề rộng (cột tối thiểu 18em, tối đa 4 cột)
          ".ovs-cols{columns:4 18em;column-gap:var(--sp-6);margin:0 0 var(--sp-4)}.ovs-cols>p{max-width:var(--measure);orphans:3;widows:3}"
          ".ovs-cols>p:first-child{margin-top:0}"
          # footer cuối trang = dòng nguồn/tham chiếu, đọc lướt → mờ, nhỏ, có vạch ngăn (user 01/10/2026: "đặt nó làm footer mờ").
          # "Mờ" = màu ink2, KHÔNG thêm opacity: opacity .8 kéo contrast xuống 3.33:1 < 4.5 (cổng chạy-thật đỏ 06/10/2026)
          ":is(main,body)>footer{color:var(--ovs-ink2);font-size:.75rem;line-height:1.6;margin-top:var(--sp-8);padding-top:var(--sp-4);"
          "border-top:1px solid var(--ovs-border)}:is(main,body)>footer p{margin:0;max-width:none;font-size:inherit;line-height:inherit;color:inherit}"
          ":is(main,body)>footer :is(code,b,strong){background:none;padding:0;font-weight:inherit;color:inherit;font-size:inherit}"
          # hàng meta dưới tiêu đề (loại · nguồn · trạng thái · phút đọc) — kiểu dòng thông tin báo giấy, không phải văn xuôi
          ".ovs-meta{display:flex;flex-wrap:wrap;align-items:center;gap:var(--sp-1) 0;font-size:.8125rem;line-height:1.6;color:var(--ovs-ink2);max-width:none}"
          ".ovs-meta-i{display:inline-flex;align-items:center;gap:var(--sp-1)}.ovs-meta-i+.ovs-meta-i::before{content:\"·\";margin:0 var(--sp-2);opacity:.6}"
          ".ovs-meta-v{padding:0 var(--sp-2);border-radius:999px;background:var(--ovs-surface2);border:1px solid var(--ovs-border);color:var(--ovs-ink);font-weight:var(--fw-strong,600)}"
          # dáng báo giấy (user 01/10/2026): vạch kẻ giữa cột · khối ngắn 2 cột · sapo · trích dẫn nổi bật
          ".ovs-cols{column-rule:1px solid var(--ovs-border)}.ovs-cols.ovs-cols-2{columns:2 18em}"
          ".ovs-sapo{font-size:1.125rem;line-height:1.65;font-weight:500;color:var(--ovs-ink);max-width:var(--measure);margin:0 0 var(--sp-5)}"
          ".ovs-pull{margin:var(--sp-6) 0;padding:var(--sp-5) var(--sp-4);border-top:2px solid var(--ovs-ink);border-bottom:1px solid var(--ovs-border);"
          "font-family:var(--font-display);font-size:1.5rem;line-height:1.5;font-weight:600;color:var(--ovs-ink);max-width:none;text-wrap:balance}"
          ".ovs-readtime{color:var(--ovs-ink2);font-size:.875em;white-space:nowrap}"
          ".ovs-ord{font-weight:var(--fw-strong,600);color:var(--ovs-accent)}"
          # code: tắt ligature (mono ligate `--` thành em-dash → người đọc gõ sai lệnh) — luật cũ của cổng tĩnh, nay có sẵn cho MỌI trang
          "pre,code,kbd,samp{font-variant-ligatures:none;font-feature-settings:\"liga\" 0,\"calt\" 0}"
          ".ovs-eyebrow{font-size:11px;font-weight:600;letter-spacing:.02em;text-transform:uppercase;color:var(--ovs-ink2)}"
          ".ovs-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--ovs-accent);margin-right:var(--sp-2);vertical-align:1px}"
          ".ovs-dot.ok{background:var(--ovs-ok)}.ovs-dot.warn{background:var(--ovs-warn)}.ovs-dot.bad{background:var(--ovs-bad)}"
          ".ovs-theme{position:fixed;right:16px;bottom:16px;z-index:2147483000;display:inline-flex;align-items:center;gap:8px;padding:8px 12px;"
          "border-radius:999px;border:1px solid var(--ovs-border);background:var(--ovs-surface2);color:var(--ovs-ink);font:inherit;font-size:12px;"
          "cursor:pointer;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px)}"
          ".ovs-theme:focus-visible{outline:2px solid var(--ovs-accent);outline-offset:2px}"
          ".ovs-theme i{width:14px;height:14px;border-radius:50%;box-shadow:inset -4px -3px 0 0 currentColor;display:inline-block}"
          "html[data-theme=dark] .ovs-theme i{box-shadow:none;background:currentColor}"
          "@media print{.ovs-theme{display:none}}"
          # hàng một dòng (user 24/09 "tràn thì không xuống dòng, chỉ mờ đi; hover thấy đủ" — luật row-wrap): mờ mép phải CHỈ khi tràn thật
          # (cờ data-clip do LINE_JS đặt); hover/focus bung ra đủ nội dung. Dùng cho hàng chip/chỉ số/meta/breadcrumb — không cho đoạn văn.
          # ô nhập (user 24/09 "viền khoanh tròn là slop" — luật field-ring): không viền, không vòng; nền pha từ màu chữ của chính ô
          # (currentColor → đúng cả trang sáng/tối/tự quản theme), hover đậm hơn, focus đậm nữa. !important: quy tắc NHÀ, trang không ghi đè.
          f"{F}{{border-color:transparent!important;box-shadow:none!important;background:color-mix(in srgb,currentColor 6%,transparent)!important;transition:background-color .12s ease-out}}"
          f"{H}{{background:color-mix(in srgb,currentColor 9%,transparent)!important}}"
          f"{Fo}{{outline:none!important;box-shadow:none!important;background:color-mix(in srgb,currentColor 13%,transparent)!important}}"
          f"{I}{{background:color-mix(in srgb,var(--ovs-bad,#c0392b) 12%,transparent)!important}}{IF}{{background:color-mix(in srgb,var(--ovs-bad,#c0392b) 20%,transparent)!important}}"
          # !important: ovs-line là HỢP ĐỒNG hành vi — CSS riêng của trang (.kpi{flex-wrap:wrap} đặt sau lớp nền) không được phá nó
          ".ovs-line{display:flex;flex-wrap:nowrap!important;white-space:nowrap!important;overflow:hidden!important;min-width:0}.ovs-line>*{flex:none!important}"
          ".ovs-line[data-clip]{-webkit-mask-image:linear-gradient(90deg,#000 calc(100% - 56px),transparent);mask-image:linear-gradient(90deg,#000 calc(100% - 56px),transparent)}"
          ".ovs-line[data-clip]:hover,.ovs-line[data-clip]:focus-within{flex-wrap:wrap!important;white-space:normal!important;overflow:visible!important;-webkit-mask-image:none;mask-image:none}"
          # người dùng bật "giảm chuyển động" ở hệ điều hành → tắt mọi hiệu ứng trên MỌI trang sinh ra (luật reduced-motion-missing, 21/09/2026)
          "@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;"
          "transition-duration:.01ms!important;scroll-behavior:auto!important}}")


# Chống nháy: chạy TRƯỚC khi trình duyệt vẽ — đặt data-theme từ lựa chọn đã nhớ, chưa có thì SÁNG (mặc định framework,
# user chốt 22/09/2026: "kêu mặc định lightmode cơ mà" — không theo prefers-color-scheme của hệ điều hành).
BOOT_JS = ("(function(){try{var d=document.documentElement,s=localStorage.getItem('%s');"
           "d.setAttribute('data-theme',s==='dark'?'dark':'light')}catch(e){"
           "document.documentElement.setAttribute('data-theme','light')}})()" % KEY)
# cờ data-clip cho .ovs-line: tràn thật mới mờ mép. Bỏ qua phần tử đang hover/focus — không thì bung ra → hết tràn → gỡ cờ → co lại → nhấp nháy.
# Theo dõi DOM đổi (trang dựng bằng JS như nightshift) + resize, gộp một lần mỗi khung hình.
LINE_JS = ("(function(){var q=0,t=0;"
           # hàng flex ngang ≥ 2 mục nhỏ (≤ 64px) rơi xuống ≥ 2 dòng → gắn ovs-line (cùng tiêu chí luật row-wrap của html-visual-gate)
           "function auto(){t=Date.now();var A=document.querySelectorAll('body *');for(var i=0;i<A.length;i++){var e=A[i];if(e.classList.contains('ovs-line')||/^H[1-6]$/.test(e.tagName))continue;"
           "var c=getComputedStyle(e);if(c.display.indexOf('flex')<0||c.flexDirection.indexOf('row')!==0||c.flexWrap==='nowrap')continue;var K=[],hs=0,mn=1e9;"
           "for(var k=e.firstElementChild;k;k=k.nextElementSibling){var kc=getComputedStyle(k),r=k.getBoundingClientRect();if(r.width<=1||r.height<=1||kc.position==='absolute'||kc.position==='fixed')continue;"
           "if(kc.flexBasis==='100%'){K=[];break}K.push(r);hs=Math.max(hs,r.height);mn=Math.min(mn,r.height)}if(K.length<2||hs>64)continue;"
           "for(var n=1;n<K.length;n++)if(Math.abs(K[n].top-K[0].top)>=mn/2){e.classList.add('ovs-line');break}}}"
           "function m(){q=0;if(Date.now()-t>500)auto();var L=document.querySelectorAll('.ovs-line');for(var i=0;i<L.length;i++){var e=L[i];"
           "if(e.matches(':hover,:focus-within'))continue;var c=e.scrollWidth>e.clientWidth+1;if(c!==e.hasAttribute('data-clip'))e.toggleAttribute('data-clip',c)}}"
           "function s(){if(!q)q=requestAnimationFrame(m)}function r(){t=0;s()}new MutationObserver(s).observe(document.documentElement,{childList:true,subtree:true,characterData:true});"
           "addEventListener('resize',r);addEventListener('load',r);document.addEventListener('mouseout',s)})();")
LINE_TAG = f'<script id="ovs-line">{LINE_JS}</script>'
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
             "if(!d.getAttribute('data-theme'))set('light');"
             "window.addEventListener('message',function(e){if(e.data&&e.data.ovsTheme)set(e.data.ovsTheme)})})()")


def _font_mod():
    s = importlib.util.spec_from_file_location("ovs_html_font", HERE / "html_font.py"); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def has_own_theme(html: str) -> bool:
    """Trang đã tự có chế độ tối + nút đổi (graph-viz, overstack, control-room) → KHÔNG chèn nút thứ hai, không ghi đè token tối của nó."""
    head = re.split(r"</head\s*>", html, 1, flags=re.I)[0]
    dark_css = bool(re.search(r"\[data-theme\s*=\s*[\"']?dark|prefers-color-scheme\s*:\s*dark", head, re.I))
    toggler = bool(re.search(r"theme-switch|theme-toggle|themeToggle", html)) and "localStorage" in html
    return dark_css and toggler


def _shell(html: str) -> str:
    """Bộ khung trang tài liệu (html_shell.py, PLAN 220926) — chỉ khi file có mặt; engine không mang file này nên trang graph không đổi."""
    f = HERE / "html_shell.py"
    if not f.is_file():
        return html
    try:                                   # lỗi ở bộ khung trên trang lạ KHÔNG được làm sập mọi generator (review t8 #10)
        s = importlib.util.spec_from_file_location("ovs_html_shell", f); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
        return m.apply(html)
    except Exception as e:                 # noqa: BLE001 — fail-open có tên
        sys.stderr.write(f"[html_base] bỏ qua bộ khung trang tài liệu: {type(e).__name__}: {e}\n")
        return html


def _apply(html: str, *, toggle: bool = True, fix=None) -> str:
    if f'id="{STYLE_ID}"' in html:                                  # lớp nền đã có (template/trang cũ): LÀM MỚI khối nền + khối font về bản hiện tại
        def _fresh(m):                                              # giữ lựa chọn family_dark của lần chèn đầu (khối cũ có luật body tối hay không)
            return f'<style id="{STYLE_ID}">{base_css(family_dark="html[data-theme=dark] body{" in m.group(0))}</style>'
        html = re.sub(rf'<style id="{STYLE_ID}">.*?</style\s*>', _fresh, html, count=1, flags=re.S)
        html = re.sub(r'<script id="ovs-line">.*?</script\s*>', "", html, flags=re.S)                        # hàng một dòng (24/09): làm mới / chèn
        html = re.sub(rf'(<style id="{STYLE_ID}">.*?</style\s*>)', lambda _m: _m.group(1) + LINE_TAG, html, count=1, flags=re.S)
        fixer = HERE / "html-slop-fix.py"              # vá lại cả trang ĐÃ có lớp nền — trước 22/09 nhánh này bỏ qua vá, nên phép vá
        if (fix is None and fixer.is_file()) or fix:  # mới (khoảng cách về thang) không bao giờ tới trang cũ. Mọi phép vá idempotent.
            s_ = importlib.util.spec_from_file_location("ovs_slop_fix", fixer); fm = importlib.util.module_from_spec(s_); s_.loader.exec_module(fm)
            html = fm.fix_markup(html, [])
        return _shell(_font_mod().apply(html, _from_base=True))
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
    html = html[:m.start()] + f'<style id="{STYLE_ID}">{base_css(family_dark=not head_dark)}</style>' + LINE_TAG + html[m.start():]
    if own:                                                         # trang tự có theme: không chèn nút thứ hai — nhưng VẪN gắn bộ khung/điều hướng. Trước 30/09 nhánh
        return _shell(html)                                         # này trả thẳng nên lần áp ĐẦU không có rail, lần hai mới có (overstack.html: generator ra sidebar, --apply ra rail)
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
    return _shell(html)


# Ribbon "Overstack" (user 02/10/2026, phương án B): thanh nhỏ chữ Gothic góc trái trên, DÍNH ở đỉnh khi cuộn — mọi trang framework sinh ra,
# TRỪ tài liệu chính thức (overstack.html đánh dấu data-ovs-no-mast) và trang con trong iframe (theo trang mẹ). Font Chomsky (OFL,
# Chomsky-NOTICE.txt) cắt chỉ còn glyph "Overstack" (~3KB) — đổi chữ thì cắt lại: pyftsubset <Chomsky.woff2> --text=... --flavor=woff2.
MAST_ID, MAST_TEXT = "ovs-mast", "Overstack"


def _mast_css() -> str:
    import base64
    f = HERE / "assets" / "fonts" / "Chomsky-mast.woff2"
    face = (f'@font-face{{font-family:"Chomsky";src:url(data:font/woff2;base64,{base64.b64encode(f.read_bytes()).decode()}) format("woff2");font-display:block}}'
            if f.is_file() else "")
    return (face + ".ovs-mast{position:sticky;top:0;z-index:2147482000;display:flex;align-items:center;padding:var(--sp-2,8px) var(--sp-4,16px);"
            "background:color-mix(in srgb,var(--ovs-bg) 88%,transparent);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);"
            "border-bottom:1px solid var(--ovs-border);margin:0 0 var(--sp-5,24px)}"
            ".ovs-mast-name{font-family:\"Chomsky\",Georgia,serif;font-size:26px;line-height:1;color:var(--ovs-ink);text-decoration:none;letter-spacing:0}"
            "@media print{.ovs-mast{position:static}}")


def _is_follow(html: str) -> bool:
    """Trang NHÚNG (đã qua to_follow) — chỉ xét thẻ <html> mở đầu: trang mẹ nhúng trang con qua srcdoc cũng chứa chuỗi này
    trong thân, xét cả văn bản thì trang mẹ mất ribbon + favicon (overstack.html 06/10/2026 giữ favicon xanh cũ)."""
    m = re.search(r"<html\b[^>]*>", html, re.I)
    return bool(m and "data-ovs-theme-follow" in m.group(0))


def mast(html: str) -> str:
    """Gắn/LÀM MỚI ribbon. Idempotent: gỡ bản cũ rồi chèn lại, nên áp lại trang cũ là CSS ribbon lên bản hiện tại."""
    if "data-ovs-no-mast" in html or _is_follow(html):
        return html
    html = re.sub(rf'<style id="{MAST_ID}-css">.*?</style>|<div id="{MAST_ID}"[^>]*>.*?</div>', "", html, flags=re.S)
    h, b = re.search(r"</head\s*>", html, re.I), re.search(r"<body\b[^>]*>", html, re.I)   # cái ĐẦU: thẻ của trang chính, srcdoc/JS nằm sau
    if not (h and b) or b.start() < h.start():
        return html
    bar = f'<div id="{MAST_ID}" class="ovs-mast" role="banner"><span class="ovs-mast-name">{MAST_TEXT}</span></div>'
    html = html[:b.end()] + bar + html[b.end():]
    at = html.find(f'<style id="{STYLE_ID}">')           # TRƯỚC khối nền (đứng yên), không trước </head>: html_shell gỡ-rồi-chèn khối của nó ở đó → đảo thứ tự
    at = at if 0 <= at < h.start() else h.start()
    return html[:at] + f'<style id="{MAST_ID}-css">{_mast_css()}</style>' + html[at:]


# Favicon = chữ "O" của ribbon phủ kín ô (user 02/10/2026) — MỌI trang độc lập, kể cả overstack.html; THAY favicon cũ của generator.
# Nét chữ rút sẵn từ Chomsky-mast.woff2 (fontTools SVGPathPen) để lúc chạy không cần fontTools; tự đổi màu theo chế độ sáng/tối của trình duyệt.
FAVICON_SVG = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='-18 -786 815 815'><style>path{fill:#111}@media (prefers-color-scheme:dark){path{fill:#f2f2f2}}</style><path transform='scale(1,-1)' d='M199.31210327148438 603.3731842041016 260.95220947265625 628.9676971435547C260.95220947265625 521.2086181640625 260.9541015625 413.4495391845703 260.9541015625 305.69044494628906L191.6516571044922 276.154541015625C174.88037109375 323.5634002685547 165.92764282226562 376.11016845703125 165.92764282226562 429.61871337890625C165.92764282226562 493.5791931152344 178.068359375 552.0941772460938 199.31211853027344 603.3731842041016ZM217.31954956054688 641.2168426513672C245.6704559326172 693.5884704589844 284.15870666503906 736.5945434570312 328.7041015625 767.8300933837891L314.201171875 786.3330230712891C163.14163208007812 725.0359954833984 42.342010498046875 572.3384246826172 42.342010498046875 366.32122802734375C42.342010498046875 140.77476501464844 182.31382751464844 -28.564682006835938 350.0135955810547 -28.564682006835938C525.0232086181641 -28.564682006835938 735.9516143798828 190.85427856445312 735.9516143798828 419.0563049316406C735.9516143798828 589.1531829833984 628.3419952392578 711.2011108398438 505.201171875 765.0000152587891ZM201.3350067138672 251.3717803955078 389.9521484375 330.75392150878906 390.0164031982422 682.5583801269531 392.2841796875 683.5000152587891C407.72547912597656 676.7563018798828 422.4015197753906 669.4654998779297 436.3193054199219 661.6544036865234C436.3193054199219 468.28440856933594 436.31842041015625 274.91441345214844 436.31842041015625 81.54443359375C432.765869140625 81.34140014648438 429.2063751220703 81.23924255371094 425.64381408691406 81.23924255371094C322.53656005859375 81.23924255371094 243.85682678222656 152.3477325439453 201.3350067138672 251.3717803955078ZM464.98326110839844 85.39506530761719C464.9832458496094 148.83770751953125 464.982666015625 212.2803497314453 464.982666015625 275.7229919433594L631.7685241699219 359.9234161376953C633.0531921386719 345.6885070800781 633.6924133300781 331.1865692138672 633.6924133300781 316.4414367675781C633.6924133300781 188.89947509765625 555.1638641357422 104.55381774902344 464.9832305908203 85.39506530761719ZM464.9815216064453 644.1320648193359C529.1327514648438 601.4556884765625 574.4758453369141 546.26611328125 601.8828735351562 481.90708923339844L464.9822235107422 412.7901916503906C464.9822235107422 489.90415954589844 464.98150634765625 567.0181274414062 464.98150634765625 644.132080078125ZM464.98231506347656 380.68263244628906 612.1320343017578 454.96990966796875C619.1414947509766 434.1694030761719 624.4237823486328 412.52435302734375 628.0052337646484 390.1357116699219L464.9825439453125 307.8305969238281C464.98255920410156 332.11460876464844 464.9823303222656 356.39862060546875 464.9823303222656 380.68263244628906Z'/></svg>")


def favicon(html: str) -> str:
    from urllib.parse import quote
    h = re.search(r"</head\s*>", html, re.I)
    if not h or _is_follow(html):
        return html
    head = re.sub(r"<link\b[^>]*\brel=[\"']?(?:shortcut )?icon\b[^>]*>", "", html[:h.start()], flags=re.I)
    at = min([i for i in (head.find(f'<style id="{MAST_ID}-css">'), head.find(f'<style id="{STYLE_ID}">')) if i >= 0] or [len(head)])   # cùng lý do với mast(): né chỗ html_shell gỡ-chèn
    return head[:at] + f'<link rel="icon" href="data:image/svg+xml,{quote(FAVICON_SVG, safe=" =:/;,")}">' + head[at:] + html[h.start():]


def apply(html: str, *, toggle: bool = True, fix=None) -> str:
    out = _apply(html, toggle=toggle, fix=fix)
    return favicon(mast(out)) if toggle else out


def to_follow(html: str) -> str:
    """Trang ĐỘC LẬP đã gắn lớp nền → bản NHÚNG trong iframe: bỏ nút riêng, đổi script chống nháy thành script theo-trang-mẹ.
    Dùng khi một generator nhúng trang khác qua `srcdoc` (overstack nhúng memory-map, skill-whiteboard): một trang chỉ có MỘT nút đổi giao diện."""
    if _is_follow(html):
        return html
    html = re.sub(rf'<style id="{MAST_ID}-css">.*?</style>|<div id="{MAST_ID}"[^>]*>.*?</div>', "", html, flags=re.S)   # trang con: ribbon chỉ ở trang mẹ
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
                    "return t==='dark'?'dark':'light'}"
                    "function tell(f){try{f.contentWindow.postMessage({ovsTheme:cur()},'*')}catch(e){}}"
                    "function all(){[].forEach.call(document.querySelectorAll('iframe'),tell)}"
                    "new MutationObserver(all).observe(d,{attributes:true,attributeFilter:['data-theme']});"
                    "[].forEach.call(document.querySelectorAll('iframe'),function(f){f.addEventListener('load',function(){tell(f)})});"
                    "window.addEventListener('load',all);all()})()")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--apply" in a:
        for f in [Path(x) for x in a if not x.startswith("--")]:
            src = f.read_text(encoding="utf-8")
            # --favicon-only: trang tự lo theme/font (ui-kit-from-code) — chỉ gắn favicon "O", không đụng lớp nền
            out = favicon(src) if "--favicon-only" in a else apply(src, toggle="--follow" not in a)
            print(f"{'✓' if out != src else '·'} {f}"); f.write_text(out, encoding="utf-8")
    else:
        print(__doc__)
