#!/usr/bin/env python3
"""html_shell — BỘ KHUNG TRANG TÀI LIỆU tự gắn: phần máy làm được của các luật MUST trong skill docs-site-macos.

Vì sao có (22/09/2026, PLAN 220926-docs-shell-kit): skill khai icon tile trong sidebar, mind map, sơ đồ kéo-thả, scroll
spy, ripple, skip-link, `<main id="main">`, favicon inline… nhưng chỉ bằng văn xuôi — đo được 0/5 trang tài liệu đủ khung,
và user thấy ngay: "mấy nhãn trong sidebar này trông chán thế nhỉ". Nay `html_base.apply()` gọi `apply()` ở đây cho mọi
trang docs-shell (sidebar có `.logo` + ≥ 4 neo `#…`), nên generator, `html_font.py --apply` và trang agent dựng tay đều nhận.

Luật chèn: chỉ THÊM thứ trang còn THIẾU; khối của mình (`ovs-shell`, `ovs-shell-js`) làm mới được, idempotent. Trang có
sidebar riêng (graph của engine, control-room) không phải docs-shell → không đụng. CSS/JS mind map + kéo-thả là bản
NGUYÊN VĂN của skill (trích bằng `--sync` vào `html_shell_vendor.py`, test gác lệch) — không viết lại.

    html_shell.py --sync      trích lại khối CSS/JS từ skills/docs-site-macos/SKILL.md
"""
from __future__ import annotations

import html as _h
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDOR = HERE / "html_shell_vendor.py"
SKILL = HERE.parents[1] / "skills" / "docs-site-macos" / "SKILL.md"
STYLE_ID, JS_ID = "ovs-shell", "ovs-shell-js"

ACCENTS = ("#0a84ff", "#30b0c7", "#5856d6", "#ff9500", "#34c759", "#ff2d55")
# icon line 24×24 kiểu SF Symbols (stroke, không fill) — tra theo TỪ KHOÁ trong tên mục; không khớp → chữ cái đầu
_ICONS = [
    (r"vấn đề|problem|lỗi|bug|sự cố|rủi ro|risk", '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h.01"/>'),
    (r"bản đồ|layout|map|cấu trúc|structure", '<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>'),
    (r"giao hàng|delivery|luồng|flow|đường|pipeline|quy trình", '<path d="M4 12h12"/><path d="m12 6 6 6-6 6"/><path d="M20 5v14"/>'),
    (r"gác|guard|luật|rule|bảo vệ|security|an toàn", '<path d="M12 3 4 6v6c0 4.5 3.4 8.3 8 9 4.6-.7 8-4.5 8-9V6z"/>'),
    (r"kiểm|test|nghiệm thu|verify|check|audit|đo", '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>'),
    (r"bài học|lesson|review|học|learn|ghi chú|note", '<path d="M4 5a2 2 0 0 1 2-2h12v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5"/>'),
    (r"tổng quan|overview|giới thiệu|intro|là gì|about", '<circle cx="12" cy="12" r="9"/><path d="M12 16v-5M12 8h.01"/>'),
    (r"kiến trúc|architecture|layer|tầng|lớp", '<path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5"/>'),
    (r"cài|install|setup|chạy|run|lệnh|command|cli", '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="m7 9 3 3-3 3M13 15h4"/>'),
    (r"module|thành phần|component|pattern|mẫu", '<path d="m12 3 8 4.5v9L12 21l-8-4.5v-9z"/><path d="m4 7.5 8 4.5 8-4.5M12 12v9"/>'),
    (r"cache|dữ liệu|data|lưu|db|storage", '<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/>'),
    (r"tỉ lệ|scale|hiệu năng|performance|ha\b|high", '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>'),
]


def is_docs_shell(html: str) -> bool:
    """Chép từ fdk/tools/docs-shell-survey.py (không import chéo tool — máy khách copy tools/*.py phẳng, thứ tự không bảo đảm)."""
    m = re.search(r"<nav\b.*?</nav>", html, re.S)
    return bool(m) and 'class="logo' in m.group(0) and len(re.findall(r'<a\b(?![^>]*class="[^"]*\blogo)[^>]*href="#[^"]', m.group(0))) >= 4


def nav_icon(label: str) -> str:
    low = label.lower()
    for pat, body in _ICONS:
        if re.search(pat, low):
            return f'<svg viewBox="0 0 24 24" aria-hidden="true">{body}</svg>'
    ch = _h.escape((re.sub(r"^[\W\d_]+", "", label) or "?")[0].upper())
    return f'<b aria-hidden="true">{ch}</b>'


def _vendor():
    if not VENDOR.is_file():
        return None
    s = importlib.util.spec_from_file_location("ovs_html_shell_vendor", VENDOR); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


CSS = (
    # sidebar: icon tile + viên active có chấm (KHÔNG sọc cạnh — luật side-stripe/rounded-edge)
    "nav a.ovs-na{display:flex;align-items:center;gap:10px;padding:6px 10px;font-size:13px;font-weight:500;color:var(--ovs-ink,inherit)}"
    "nav a.ovs-na .ic{flex:none;width:24px;height:24px;border-radius:7px;display:grid;place-items:center;background:var(--ic,#0a84ff);"
    "box-shadow:inset 0 1px 0 rgba(255,255,255,.35)}"
    "nav a.ovs-na .ic svg{width:14px;height:14px;stroke:#fff;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}"
    "nav a.ovs-na .ic b{color:#fff;font-size:12px;font-weight:700;line-height:1}"
    "nav a.ovs-na .ovs-lbl{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    "nav a.ovs-na.active{background:color-mix(in srgb,var(--ovs-accent,#0a84ff) 14%,transparent);color:var(--ovs-ink,inherit);font-weight:600}"
    "nav a.ovs-na.active::after{content:'';flex:none;width:6px;height:6px;border-radius:50%;background:var(--ovs-accent,#0a84ff)}"
    ".ovs-progress{position:fixed;left:0;right:0;top:0;height:3px;z-index:2147483001;pointer-events:none}"
    # nút đổi giao diện VÀO sidebar (hàng cuối, dính đáy) thay vì viên nổi góc phải — user 22/09 "nút chuyển darklight mode đâu ?"
    # margin-top:auto → đáy nav (flex dọc); KHÔNG margin âm + nền riêng: user 24/09 "slop" — dải trắng x=4→227 lệch cả mép nav lẫn cột mục (luật band-misaligned)
    "nav .ovs-theme-row{position:sticky;bottom:0;display:flex;align-items:center;justify-content:space-between;gap:12px;margin:auto 0 0;"
    "padding:12px 10px;border-top:1px solid var(--ovs-border,rgba(0,0,0,.12));background:inherit;font-size:13px;color:var(--ovs-ink,inherit)}"
    "nav .ovs-theme-row .ovs-theme{position:static;backdrop-filter:none;-webkit-backdrop-filter:none}"
    ".ovs-progress i{display:block;height:100%;width:0;background:var(--ovs-accent,#0a84ff);transition:width .12s ease-out}"
    # title-scale: tên trang ≥ 1,2 × mục nav (13px) — logo docs-shell cũ 14–15px ngang hàng mục (quét 22/09/2026)
    ":root nav .logo{font-size:18px;line-height:1.25;letter-spacing:-.015em}:root nav .logo small{font-size:11px;letter-spacing:0}"   # :root → thắng nav .logo của trang dù trang đặt sau
        # a11y
    ".skip-link{position:absolute;left:12px;top:-60px;z-index:2147483001;padding:8px 14px;border-radius:10px;background:var(--ovs-surface2,#fff);"
    "color:var(--ovs-ink,#111);font-size:13px;text-decoration:none;border:1px solid var(--ovs-border,rgba(0,0,0,.12))}"
    ".skip-link:focus{top:12px}"
    ".ovs-ripple{position:absolute;border-radius:50%;pointer-events:none;background:currentColor;opacity:.18;transform:scale(0);"
    "animation:ovs-ripple .45s ease-out forwards}@keyframes ovs-ripple{to{transform:scale(2.4);opacity:0}}"
)

# Mặt phẳng khúc xạ (skill docs-site-macos § Background Plane, BẮT BUỘC): kính cần thứ gì bên dưới để "nghiền" — nền phẳng làm
# kính trông như mảng xanh bệt (user 22/09: "màu xanh mà không có gương gradient nó cứ sao sao ấy"). Chỉ chèn khi trang CHƯA có
# body::before riêng; nền gradient đặt bằng :where(body) (độ ưu tiên 0) nên trang tự đặt nền vẫn thắng.
PLANE_CSS = (
    ":where(body){background:radial-gradient(900px 500px at 12% -10%,rgba(10,132,255,.10),transparent 60%),"
    "radial-gradient(700px 420px at 95% 15%,rgba(90,162,232,.08),transparent 55%),linear-gradient(180deg,#f7fbff 0%,#eaf2fd 100%) fixed}"
    "body::before{content:'';position:fixed;inset:-10%;z-index:-1;pointer-events:none;"
    "background:radial-gradient(640px 440px at 10% 14%,rgba(10,132,255,.22),transparent 65%),"
    "radial-gradient(380px 460px at 4% 52%,rgba(48,176,199,.18),transparent 65%),"
    "radial-gradient(540px 400px at 88% 10%,rgba(88,86,214,.13),transparent 60%),"
    "radial-gradient(720px 500px at 74% 76%,rgba(48,176,199,.13),transparent 65%),"
    "radial-gradient(480px 380px at 16% 86%,rgba(255,149,0,.12),transparent 60%);animation:ovs-orb 46s ease-in-out infinite alternate}"
    "@keyframes ovs-orb{100%{transform:translate(2.2%,1.6%) scale(1.045)}}"
    "body::after{content:'';position:fixed;inset:0;z-index:-1;pointer-events:none;background-image:radial-gradient(rgba(30,90,170,.11) 1px,transparent 1.3px);"
    "background-size:22px 22px;-webkit-mask-image:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,.22));mask-image:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,.22))}"
    "html[data-theme=dark] :where(body){background:radial-gradient(900px 500px at 12% -10%,rgba(10,132,255,.14),transparent 60%),linear-gradient(180deg,#0c0f16 0%,#111827 100%) fixed}"
    "html[data-theme=dark] body::before{opacity:.45}"
    "html[data-theme=dark] body::after{background-image:radial-gradient(rgba(140,170,230,.08) 1px,transparent 1.3px)}"
)

JS_SPY = ("(function(){var L=[].slice.call(document.querySelectorAll('nav a.ovs-na[href^=\"#\"]'));if(!L.length||!('IntersectionObserver' in window))return;"
          "var by={};L.forEach(function(a){var t=document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)));if(t)by[t.id]=a});"
          "var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting&&by[e.target.id]){L.forEach(function(x){x.classList.remove('active')});"
          "by[e.target.id].classList.add('active')}})},{rootMargin:'-35% 0px -60% 0px'});Object.keys(by).forEach(function(id){io.observe(document.getElementById(id))})})();")
JS_PROGRESS = ("(function(){var b=document.querySelector('.ovs-progress i');if(!b)return;function u(){var d=document.documentElement,m=d.scrollHeight-d.clientHeight;"
               "b.style.width=(m>0?Math.min(100,d.scrollTop/m*100):0)+'%'}addEventListener('scroll',u,{passive:true});u()})();")
# static→relative phải kèm inset:auto: top/bottom/right sót lại (vd nút theme nổi bottom:16px) sẽ đẩy nút nhảy 16px khi bấm — user 24/09
JS_RIPPLE = ("(function(){document.addEventListener('pointerdown',function(e){var el=e.target.closest&&e.target.closest('nav a,button,.diagram-reset');"
             "if(!el||matchMedia('(prefers-reduced-motion: reduce)').matches)return;var r=el.getBoundingClientRect(),s=Math.max(r.width,r.height),k=document.createElement('span');"
             "var po=el.style.position,ov=el.style.overflow,pi=el.style.inset;if(getComputedStyle(el).position==='static'){el.style.position='relative';el.style.inset='auto'}el.style.overflow='hidden';k.className='ovs-ripple';"
             "k.style.cssText='width:'+s+'px;height:'+s+'px;left:'+(e.clientX-r.left-s/2)+'px;top:'+(e.clientY-r.top-s/2)+'px';el.appendChild(k);"
             "setTimeout(function(){k.remove();el.style.position=po;el.style.inset=pi;el.style.overflow=ov},500)})})();")
FAVICON = ('<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 32 32%22%3E'
           '%3Crect width=%2232%22 height=%2232%22 rx=%228%22 fill=%22%230a84ff%22/%3E%3Cpath d=%22M9 11h14M9 16h14M9 21h9%22 stroke=%22white%22 '
           'stroke-width=%222.4%22 stroke-linecap=%22round%22/%3E%3C/svg%3E">')


def _nav_links(nav: str) -> str:
    """Mỗi <a href="#…"> chưa có icon → [icon tile][nhãn] (số thứ tự vào title). Nhãn lấy từ TEXT của link (bỏ tag con)."""
    i = [0]

    def one(m):
        attrs, inner = m.group(1), m.group(2)
        if 'href="#' not in attrs or re.search(r'href="#"', attrs) or 'class="ic' in inner or re.search(r'class="[^"]*\blogo', attrs):
            return m.group(0)
        text = re.sub(r"<[^>]+>", "", inner).strip()
        mn = re.match(r"^\s*(\d{1,2})\s*[·.\-:]\s*(.+)$", text, re.S)
        lbl = mn.group(2).strip() if mn else text
        color = ACCENTS[i[0] % len(ACCENTS)]; i[0] += 1
        cls = re.search(r'class="([^"]*)"', attrs)
        attrs = (attrs.replace(cls.group(0), f'class="{cls.group(1)} ovs-na"') if cls else attrs + ' class="ovs-na"')
        # số thứ tự KHÔNG hiện (sidebar 200px: icon + chip + nhãn → nhãn bẻ 2 dòng, luật clickable-wrap; số đã có ở nhãn section) — để trong title
        full = _h.escape(_h.unescape(text))
        if "title=" not in attrs:
            attrs += f' title="{full}"'
        return (f'<a{attrs}><span class="ic" style="--ic:{color}">{nav_icon(lbl)}</span>'
                f'<span class="ovs-lbl">{_h.escape(_h.unescape(lbl))}</span></a>')

    return re.sub(r"<a\b([^>]*)>(.*?)</a>", one, nav, flags=re.S)


def _mind_map(html: str) -> str:
    """Mind map (cấu trúc NGUYÊN VĂN của skill) sinh từ cây h2 → h3 của CHÍNH trang; root = <h1> hoặc .logo."""
    body = html[html.find("</nav>"):] if "</nav>" in html else html
    root = re.search(r"<h1\b[^>]*>(.*?)</h1>", body, re.S) or re.search(r'class="logo"[^>]*>(.*?)<', html, re.S)
    rtxt = re.sub(r"<[^>]+>", "", root.group(1)).strip() if root else "Tài liệu"
    heads = re.findall(r"<h([23])\b[^>]*>(.*?)</h\1>", body, re.S)
    cats, cur = [], None
    for lv, t in heads:
        t = _h.escape(_h.unescape(re.sub(r"<[^>]+>", "", t).strip()))
        if not t:
            continue
        if lv == "2":
            cur = [t, []]; cats.append(cur)
        elif cur is not None:
            cur[1].append(t)
    if len(cats) < 2:
        return ""
    rows = []
    for k, (t, leaves) in enumerate(cats):
        b = f"b-{k % 5}"
        if leaves:
            kids = "".join(f'<div class="row"><div class="node {b} leaf"><span class="nm">{x}</span></div></div>' for x in leaves)
            rows.append(f'<div class="row"><div class="node {b} cat has-children"><span class="nm">{t}</span><span class="ct">{len(leaves)}</span></div>'
                        f'<div class="children">{kids}</div></div>')
        else:
            rows.append(f'<div class="row"><div class="node {b} leaf"><span class="nm">{t}</span></div></div>')
    return (f'<section class="ovs-mindmap" aria-label="Mind map cấu trúc trang"><div class="mm"><div class="mm-canvas"><svg class="mm-links" aria-hidden="true"></svg>'
            f'<div class="tree"><div class="row"><div class="node root has-children"><span class="nm">{_h.escape(_h.unescape(rtxt))}</span>'
            f'<span class="ct">{len(cats)}</span></div><div class="children">{"".join(rows)}</div></div></div></div></div></section>')


def _body_end(html: str) -> int:
    """</body> CUỐI (cái trước có thể nằm trong srcdoc/JS); HTML5 cho bỏ </body> → cuối file (trước </html> nếu có)."""
    b = [x.start() for x in re.finditer(r"</body\s*>", html, re.I)]
    if b:
        return b[-1]
    e = [x.start() for x in re.finditer(r"</html\s*>", html, re.I)]
    return e[-1] if e else len(html)


def wrap_blocked(html: str) -> bool:
    """Bọc <main style=display:contents> sau </nav> sẽ GÃY khi: CSS có `body > …` / `nav ~ …` / `nav + …` (quan hệ anh-em/cha-con
    đổi), hoặc nav nằm trong <header> (main mở trong header, parser đóng ở </header>). Review t8 22/09/2026."""
    css = " ".join(re.findall(r"<style\b[^>]*>(.*?)</style>", html, re.S | re.I))
    if re.search(r"(?<![\w-])body\s*>\s*[\w.#*:\[]|(?<![\w-])nav\s*[~+]", css):
        return True
    n = html.find("<nav"); h = html.rfind("<header", 0, n) if n >= 0 else -1
    return h >= 0 and html.find("</header>", h) > html.find("</nav>")


def has_main_target(html: str) -> bool:
    return bool(re.search(r"<main\b|\bid=\"main\"", html))


def apply(html: str) -> str:
    if not is_docs_shell(html) or re.search(r'<meta\s+name="overstack-shell"\s+content="none"', html):
        return html
    v = _vendor()
    # khối CỦA MÌNH bỏ ra TRƯỚC khi tính cờ — không thì lần chạy thứ hai thấy chính spy/ripple mình chèn và
    # tưởng trang tự có (hoặc ngược lại chèn đôi). Review t8: overstack áp lần hai sinh spy + ripple thứ hai.
    html = re.sub(rf'<style id="{STYLE_ID}">.*?</style>', "", html, flags=re.S)
    html = re.sub(rf'<script id="{JS_ID}">.*?</script>', "", html, flags=re.S)
    nav0 = re.search(r"<nav\b.*?</nav>", html, re.S).group(0)
    need = {
        "icon": not re.search(r'class="ic\b|class="nav-ic', nav0),
        "skip": "skip-link" not in html,
        "fav": not re.search(r'<link\b[^>]*\brel="(?:shortcut )?icon"', html),
        "spy": "IntersectionObserver" not in html,
        "ripple": "ripple" not in html,
        "mm": not re.search(r'mind-?map|class="mm"', html, re.I),
        "plane": not re.search(r"body::before|orbDrift|ovs-orb", re.sub(rf'<style id="{STYLE_ID}">.*?</style>', "", html, flags=re.S)),
        "drag": "diagram-box" in html and not re.search(r"dataset\.draggable|data-draggable|initDraggableDiagrams", html),
    }
    # 1) sidebar
    if need["icon"]:
        m = re.search(r"<nav\b.*?</nav>", html, re.S)
        nav = _nav_links(m.group(0))
        if "ovs-progress" not in nav:
            nav = nav[:nav.rfind("</nav>")] + '<div class="ovs-progress" aria-hidden="true"><i></i></div></nav>'
        html = html[:m.start()] + nav + html[m.end():]
    # 1b) nút đổi giao diện của lớp nền (chèn trước </body>) → hàng cuối sidebar; idempotent (đã ở trong nav thì thôi)
    tg = re.search(r'<button type="button" class="ovs-theme"[^>]*>.*?</button>', html, re.S)
    nav1 = re.search(r"<nav\b.*?</nav>", html, re.S)
    if tg and nav1 and not (nav1.start() < tg.start() < nav1.end()):
        btn = tg.group(0); html = html[:tg.start()] + html[tg.end():]
        nav1 = re.search(r"<nav\b.*?</nav>", html, re.S); nv = nav1.group(0)
        at = nv.find('<div class="ovs-progress"') if '<div class="ovs-progress"' in nv else nv.rfind("</nav>")
        nv = nv[:at] + f'<div class="ovs-theme-row"><span>Giao diện</span>{btn}</div>' + nv[at:]
        html = html[:nav1.start()] + nv + html[nav1.end():]
    # 2) a11y: vùng nội dung chính + skip-link trỏ ĐÚNG id của nó
    target = "main"
    mm = re.search(r"<main\b([^>]*)>", html)
    if mm:
        idm = re.search(r'\bid="([^"]+)"', mm.group(1))
        if idm:
            target = idm.group(1)
        else:
            html = html[:mm.start()] + f'<main id="main"{mm.group(1)}>' + html[mm.end():]
    elif not re.search(r'\bid="main"', html) and "</nav>" in html and not wrap_blocked(html):
        i = html.find("</nav>") + len("</nav>"); j = _body_end(html)
        html = html[:i] + '<main id="main" style="display:contents">' + html[i:j] + "</main>" + html[j:]
    if need["skip"] and has_main_target(html):
        html = re.sub(r"(<body\b[^>]*>)", rf'\1<a class="skip-link" href="#{target}">Bỏ qua tới nội dung</a>', html, count=1, flags=re.I)
    # 3) favicon
    if need["fav"]:
        html = re.sub(r"</head\s*>", FAVICON + "</head>", html, count=1, flags=re.I)
    # 4) mind map sau section ĐẦU (hero/tổng quan)
    css, js = CSS + (PLANE_CSS if need["plane"] else ""), ""
    if need["mm"] and v:
        block = _mind_map(html)
        s0 = re.search(r"<section\b", html[html.find("</nav>"):]) if "</nav>" in html else None
        if block and s0:
            at = html.find("</nav>") + s0.start()
            first = re.match(r"<section\b[^>]*>.*?</section>", html[at:], re.S)
            at = at + first.end() if first else at
            html = html[:at] + block + html[at:]
    if "ovs-mindmap" in html and v:
        css += ".ovs-mindmap{margin:0 auto;max-width:1100px;padding:8px 24px 24px}" + v.MM_CSS; js += v.MM_JS
    if need["drag"] and v:
        css += v.DRAG_CSS; js += v.DRAG_JS
    if need["spy"]:
        js += JS_SPY
    js += JS_PROGRESS
    if need["ripple"]:
        js += JS_RIPPLE
    html = re.sub(r"</head\s*>", f'<style id="{STYLE_ID}">{css}</style></head>', html, count=1, flags=re.I)
    j = _body_end(html)
    return html[:j] + f'<script id="{JS_ID}">{js}</script>' + html[j:]


def skill_blocks(md: str) -> dict:
    """Khối code NGUYÊN VĂN của skill: ```css / ```js ĐẦU TIÊN sau heading Mind Map và Node-Draggable."""
    def after(head, lang):
        i = md.index(head); m = re.search(rf"```{lang}\n(.*?)\n```", md[i:], re.S); return m.group(1)
    return {"MM_CSS": after("### Mind Map", "css"), "MM_JS": after("### Mind Map", "js"),
            "DRAG_CSS": after("#### Node-Draggable Diagrams", "css"), "DRAG_JS": after("#### Node-Draggable Diagrams", "js")}


def sync() -> int:
    b = skill_blocks(SKILL.read_text(encoding="utf-8"))
    VENDOR.write_text('"""SINH TỰ ĐỘNG bởi html_shell.py --sync từ skills/docs-site-macos/SKILL.md — đừng sửa tay (sửa ở skill rồi --sync)."""\n'
                      + "".join(f"{k} = {v!r}\n" for k, v in b.items()), encoding="utf-8")
    print(f"→ {VENDOR}"); return 0


if __name__ == "__main__":
    sys.exit(sync() if "--sync" in sys.argv else (print(__doc__) or 0))
