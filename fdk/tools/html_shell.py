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


def is_side_nav(html: str) -> bool:
    """Trang KHÔNG phải docs-shell nhưng có sidebar: nav mang `.brand`/`.logo` + ≥ 4 link bất kỳ (trang graph của engine, control-room,
    trang index). User 30/09: "thay thế mặc định thì áp hết" → các trang này cũng đổi sidebar sang rail TOC map, nhưng CHỈ phần điều hướng
    (rail + cụm điều khiển + scroll spy); mind map, skip-link, favicon… vẫn là việc riêng của docs-shell và của R20."""
    m = re.search(r"<nav\b.*?</nav>", html, re.S)
    return bool(m) and bool(re.search(r'class="[^"]*\b(?:logo|brand)\b', m.group(0))) \
        and len(re.findall(r'<a\b(?![^>]*class="[^"]*\b(?:logo|brand)\b)[^>]*\bhref="(?!#")[^"]', m.group(0))) >= 4


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


def _list(q: str) -> str:
    """CSS chế độ DANH SÁCH của rail dày; `q` = điều kiện trên nav (đang bật nhãn, hoặc đang rê chuột). Khung ngoài HOÀN TOÀN trong suốt,
    mỗi dòng là thẻ nhãn riêng + chấm (user 30/09: "bọc kiểu cả sidebar là sai, div ngoài cùng transparent, từng dòng wrap trong container riêng")."""
    n = ":root nav.ovs-side.nw-tocmap" + q
    # mask: danh sách cuộn KHÔNG vẽ xuống vùng cụm điều khiển góc phải dưới (hộp nav vẫn cao trọn màn để vùng rê không hụt)
    return (n + "{width:auto;max-width:calc(100vw - 1rem);overflow-y:auto;overscroll-behavior:contain;scrollbar-width:none;"
            "-webkit-mask-image:linear-gradient(#000 calc(100% - 120px),transparent calc(100% - 104px));mask-image:linear-gradient(#000 calc(100% - 120px),transparent calc(100% - 104px))}"
            + n + ">:not(.ovs-na){display:none}"
            + n + " a.ovs-na{position:static;justify-content:flex-end}"
            + n + " a.ovs-na::before{position:static;opacity:1;visibility:visible;transform:none;pointer-events:auto}")


_LV = ((1, 40, 58), (2, 40, 58), (3, 28, 42), (4, 20, 32), (5, 14, 24), (6, 14, 24))   # chấm nhạt dần theo cấp heading (mẫu: toc-map-item-background-1..6); user 30/09 "dot đậm bất thường" ở 76% → hạ còn 40%
CSS = (
    # ĐIỀU HƯỚNG = TOC MAP (user 30/09/2026, /goal "đổi bộ điều hướng … thành kiểu cuộn này"): rail chấm mục lục mép phải thay sidebar trái.
    # Hai khối .nw-tip + .nw-tocmap chép từ m3e-canvas docs/namuwiki-ui-kit.html dòng 191–215; bỏ dòng chết `.nw-tocmap a::before{position:static}` (thua độ ưu tiên), đổi token --espejo-* → --ovs-* (thẻ nhãn: kính mờ không viền thay thẻ có viền của mẫu — user chọn 30/09), easing →
    # ease-out + bỏ `transition:all` (luật motion-ease-out, transition-all của repo), gói luật :hover vào @media(hover:hover) (màn cảm ứng: hover dính sau khi chạm) và thêm :focus-visible.
    ".nw-tip{position:relative}"
    ".nw-tip[data-tooltip]::before{content:attr(data-tooltip);position:absolute;right:100%;margin:0 .5rem 0 0;padding:.15rem .4rem;white-space:nowrap;pointer-events:none;z-index:509;"
    "font-size:.9rem;line-height:1.5;color:var(--ovs-ink,#111);background-color:var(--ovs-surface2,#fff);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-radius:6px;"
    "box-shadow:0 1px 2px rgba(15,30,60,.08),0 6px 16px -6px rgba(15,30,60,.22);opacity:0;visibility:hidden;transform:translateX(1rem);transition:opacity .1s ease-out,transform .1s ease-out,visibility .1s ease-out}"
    ".nw-tip[data-tooltip]:focus-visible::before,.nw-tip[data-tooltip][data-tooltip-show]::before,[data-tooltip-show-children] .nw-tip[data-tooltip]::before"
    "{opacity:1;visibility:visible;transform:translateX(0);pointer-events:auto}"
    "[data-hover]:not([data-dense]) .nw-tip[data-tooltip]::before{opacity:1;visibility:visible;transform:translateX(0);pointer-events:auto}"
    ".nw-tocmap a{position:absolute;right:0;display:flex;align-items:center;justify-content:center;text-decoration:none}"
    ".nw-tocmap a::before{max-width:calc(100vw - 4rem);overflow:hidden;text-overflow:ellipsis}"                     # màn hẹp: nhãn dài cắt "…" thay vì tràn mép trái
    ".nw-tocmap a:hover::before,.nw-tocmap a.is-hover::before{background-color:color-mix(in srgb,var(--ovs-accent,#0a84ff) 12%,var(--ovs-surface2,#fff));"
    "transition:background-color .05s ease-out}"
    ".nw-tocmap .hit{display:flex;align-items:center;justify-content:flex-end;width:1rem;height:1.75rem;padding:0 .5rem 0 0;box-sizing:content-box}"
    ".nw-tocmap .dot{display:inline-block;width:5px;height:5px;border-radius:100%;background-color:var(--d);transition:background-color .05s ease-out}"
    ".nw-tocmap a:hover .dot,.nw-tocmap a.is-hover .dot{background-color:var(--dh)}"
    + "".join(f".nw-tocmap .l{n}{{--d:color-mix(in srgb,var(--ovs-ink,#111) {d}%,transparent);--dh:color-mix(in srgb,var(--ovs-ink,#111) {h}%,transparent)}}" for n, d, h in _LV) +
    # <nav> của trang (tác giả viết kiểu sidebar: .logo + nhãn nhóm + link) → rail cố định mép phải, dưới toolbar. `:root` + 2 class → thắng CSS nav
    # riêng của trang dù trang đặt sau. Thứ không phải chấm (logo, nhãn nhóm, nút ✕ cũ) ẩn bằng visibility — link lồng trong khối bọc vẫn hiện được.
    ":root nav.ovs-side.nw-tocmap{position:fixed;inset:0 0 0 auto;z-index:40;display:block;box-sizing:border-box;width:1.5rem;height:auto;min-height:0;margin:0;padding:24px 0 112px;overflow:visible;"
    "background:none;backdrop-filter:none;-webkit-backdrop-filter:none;box-shadow:none;border:0;transform:none;transition:none}"
    # VÙNG RÊ (user 30/09, ba lần nhắc: "tính từ cạnh phải cộng thêm xx px", "hover trên khoảng đỏ là tự động hiện ra"): JS nghe mousemove, con trỏ cách mép phải
    # cửa sổ ≤ 176px (hoặc đang nằm trên nhãn) thì gắn data-hover lên nav → bung nhãn. Không dùng hộp bắt chuột vô hình nên không chắn bấm / bôi chữ ở nội dung.
    # Lúc NGHỈ chấm mờ gần như không thấy (user: "dot mờ gần như không thấy khi đang collapsed"), rõ lên khi bung.
    ":root nav.ovs-side.nw-tocmap a.ovs-na .hit{opacity:.22;transition:opacity .12s ease-out}"
    ":root nav.ovs-side.nw-tocmap:is([data-hover],[data-tooltip-show-children]) a.ovs-na .hit,:root nav.ovs-side.nw-tocmap a.ovs-na:focus-visible .hit{opacity:1}"
    ":root nav.ovs-side.nw-tocmap::before,:root nav.ovs-side.nw-tocmap::after{content:none}"
    ":root nav.ovs-side.nw-tocmap :not(.ovs-na,.ovs-na *){position:static;visibility:hidden}"
    ":root nav.ovs-side.nw-tocmap a.ovs-na{visibility:visible;left:auto;width:auto;height:auto;min-height:0;margin:0;padding:0;border:0;border-radius:0;overflow:visible;"
    "background:none;box-shadow:none;font-size:0;line-height:0}"                                 # link không có chữ (nhãn là ::before cỡ rem) — cỡ 0 để cổng title-scale không tính nó là "mục nav"
    # RAIL DÀY (JS gắn data-dense khi số mục × 1.75rem > chiều cao rail, vd design showcase 39 mục): nhãn cao hơn bước chấm nên bung hết sẽ chồng
    # nhau → rê chuột vào rail HOẶC bấm nút mục lục đều mở DANH SÁCH cuộn được: khung ngoài trong suốt, mỗi mục một thẻ nhãn riêng + chấm, bấm được (user 30/09).
    # shortcut: danh sách ẩn mọi con trực tiếp không phải link (logo, nhãn nhóm) — link lồng trong khối bọc sẽ mất ở chế độ này; nâng cấp khi có trang > 28 mục mà nav lồng khối.
    + _list("[data-dense][data-tooltip-show-children]") + _list("[data-dense][data-hover]") +
    # tên class `.dot` / `.hit` của mẫu trùng class riêng của trang (230926-overnight-loop-prd: `.dot{margin-top:8px}` + màu theme tối) → đặt lại trong phạm vi rail
    ":root nav.ovs-side.nw-tocmap a.ovs-na .hit{margin:0;border:0;background:none;box-shadow:none}"
    ":root nav.ovs-side.nw-tocmap a.ovs-na .dot{flex:none;margin:0;border:0;box-shadow:none;background:var(--d)}"
    ":root nav.ovs-side.nw-tocmap a.ovs-na:hover .dot,:root nav.ovs-side.nw-tocmap a.ovs-na.is-hover .dot{background:var(--dh)}"
    ":root nav.ovs-side.nw-tocmap a.ovs-na.active .dot{background:var(--ovs-accent,#0a84ff)}"                 # chấm của mục đang xem (scroll spy)
    # THẺ NHÃN = kính mờ không viền (user chọn trong 4 bản so sánh, 30/09). PHÂN CẤP BẰNG FONT + CỠ CHỮ, một màu chữ (user chọn trong 4 bản so sánh
    # thứ hai, sau khi thử phân bằng màu và chê "màu trông hơi xấu"): JS gắn data-lv = cấp heading của đích —
    # cấp 1 (tên trang / #top) font tiêu đề 18px đậm 700 · cấp 2 font tiêu đề 16px đậm 600 · cấp 3 font nội dung 13.5px · cấp 4 trở xuống 12px.
    # Chưa có JS → mọi nhãn coi như cấp 2. Mục ĐANG XEM: nền thẻ pha màu nhấn + chấm màu nhấn.
    ":root nav.ovs-side.nw-tocmap a.ovs-na::before{font-family:var(--font-display,Georgia,serif);font-size:16px;font-weight:600;line-height:1.35;font-style:normal;"
    "letter-spacing:0;text-transform:none;color:var(--ovs-ink,#111)}"
    ":root nav.ovs-side.nw-tocmap a.ovs-na[data-lv=\"1\"]::before{font-size:18px;font-weight:700}"
    ":root nav.ovs-side.nw-tocmap a.ovs-na[data-lv=\"3\"]::before{font-family:var(--font-text,sans-serif);font-size:13.5px;font-weight:400}"
    ":root nav.ovs-side.nw-tocmap a.ovs-na:is([data-lv=\"4\"],[data-lv=\"5\"],[data-lv=\"6\"])::before{font-family:var(--font-text,sans-serif);font-size:12px;font-weight:400}"
    ":root nav.ovs-side.nw-tocmap a.ovs-na.active::before{background-color:color-mix(in srgb,var(--ovs-accent,#0a84ff) 16%,var(--ovs-surface2,#fff))}"
    ":root nav.ovs-side.nw-tocmap a.ovs-na>:not(.hit){display:none}"                 # mực ripple riêng của trang chèn vào link → không vẽ trên chấm
    ":root body{padding-left:0}"                                    # cột nội dung lấy lại bề ngang sidebar cũ
    ":root .nav-toggle,:root .nav-close{display:none!important}"    # nút ☰/✕ của sidebar cũ
    "@media print{:root nav.ovs-side.nw-tocmap,.ovs-bar{display:none}}"
    # CỤM ĐIỀU KHIỂN NỔI góc phải dưới (user chọn 30/09, thay dải dính trên bị chê "top menu"): thẻ dọc kiểu nhóm nút nổi nw-ctl của mẫu, mỗi ô 2.5rem,
    # ngăn nhau bằng viền: nút sáng/tối + nút bật nhãn mục lục (màn cảm ứng không có hover). Rail chấm dừng phía trên cụm (inset đáy 112px).
    ".ovs-bar{position:fixed;right:12px;bottom:16px;z-index:41;display:flex;flex-direction:column;align-items:stretch;margin:0;padding:0;overflow:hidden;"
    "background:var(--ovs-bg,#fff);border:1px solid var(--ovs-border,rgba(0,0,0,.12));border-radius:6px;box-shadow:0 5px 8px -3px rgba(0,0,0,.165)}"
    ".ovs-bar>*+*{border-top:1px solid var(--ovs-border,rgba(0,0,0,.12))}"
    ":root .ovs-bar .ovs-navbtn,:root .ovs-bar .ovs-theme{position:static;flex:none;width:auto;min-width:2.5rem;height:2.5rem;min-height:0;display:grid;place-items:center;margin:0;padding:0;"
    "border-width:0;border-radius:0;background:none;box-shadow:none;backdrop-filter:none;-webkit-backdrop-filter:none;color:var(--ovs-ink,inherit);cursor:pointer}"
    ":root .ovs-bar>*+.ovs-navbtn,:root .ovs-bar>*+.ovs-theme{border-top-width:1px}"
    ":root .ovs-bar .ovs-theme span{display:none}"                 # ô vuông chỉ có icon; tên trạng thái vẫn ở aria-label / aria-checked
    ".ovs-navbtn[aria-pressed=true]{background:color-mix(in srgb,var(--ovs-accent,#0a84ff) 16%,var(--ovs-bg,#fff))}"
    ".ovs-navbtn svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}"
    ":root .ovs-bar .theme-row{position:static;flex:none;justify-content:center;margin:0;padding:8px;border-width:0;background:none}"   # hàng nút gạt riêng của trang (dark-mode-maker)
    ":root .ovs-bar .theme-row .lbl,:root .ovs-bar .theme-row>span:first-child:not(.theme-switch){display:none}"
    ".ovs-progress{position:fixed;left:0;right:0;top:0;height:3px;z-index:2147483001;pointer-events:none}"
    ".ovs-progress i{display:block;height:100%;width:0;background:var(--ovs-accent,#0a84ff);transition:width .12s ease-out}"
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
# TOC map: cấp chấm theo heading của đích (`#top` → cấp 1; đích không có heading, hoặc link sang trang khác → cấp 3) · `top` theo vị trí đích trong trang, mục sau cách mục trước ≥ một ô 1.75rem (rail đầy thì ô co lại),
# dồn ngược khi tràn đáy · hàng `.theme-row` (nút gạt sáng/tối skill dark-mode-maker chèn vào nav lúc chạy) dời vào cụm điều khiển nổi, không thì nó bị ẩn cùng nav · rail không đủ chỗ thì gắn data-dense (xem CSS) · tính lại khi đổi cỡ / nội dung đổi chiều cao · nút toolbar bật/tắt mọi nhãn (Esc hoặc bấm một mục thì tắt).
JS_TOC = ("(function(){var nav=document.querySelector('nav.nw-tocmap');if(!nav)return;var L=[].slice.call(nav.querySelectorAll('a.nw-tip')),"
          "T=L.map(function(a){var h=a.getAttribute('href')||'';return h.charAt(0)==='#'?document.getElementById(decodeURIComponent(h.slice(1))):null});"
          "L.forEach(function(a,i){var t=T[i],h=t&&(/^H[1-6]$/.test(t.tagName)?t:t.querySelector('h1,h2,h3,h4,h5,h6')),d=a.querySelector('.dot');"
          "var v=h?h.tagName.charAt(1):(/^#(top)?$/.test(a.getAttribute('href')||'')?'1':'3');if(d)d.className='dot l'+v;a.setAttribute('data-lv',v)});"
          "var b=document.querySelector('.ovs-navbtn'),tr=nav.querySelector('.theme-row');if(b&&tr)b.parentNode.insertBefore(tr,b);"
          "function lay(){var cs=getComputedStyle(nav),pt=parseFloat(cs.paddingTop)||0,H=nav.clientHeight-pt-(parseFloat(cs.paddingBottom)||0),D=document.documentElement.scrollHeight,n=L.length;if(H<=0||!n)return;"
          "var c0=1.75*parseFloat(getComputedStyle(document.documentElement).fontSize),cell=Math.min(c0,(H-c0)/Math.max(1,n-1)),y=[],p=-cell;nav.toggleAttribute('data-dense',n*c0>H);"
          "L.forEach(function(a,i){var t=T[i],v=t?(t.getBoundingClientRect().top+window.scrollY)/D*H:p+cell;p=y[i]=Math.max(v,p+cell)});"
          "for(var i=n-1,m=H-c0;i>=0&&y[i]>m;i--,m-=cell)y[i]=m;"
          "L.forEach(function(a,i){a.style.top=Math.round(pt+y[i])+'px'})}"
          "lay();addEventListener('resize',lay);addEventListener('load',lay);if('ResizeObserver' in window)new ResizeObserver(lay).observe(document.body);"
          "function show(on){nav.toggleAttribute('data-tooltip-show-children',on);if(!b)return;"
          "b.setAttribute('aria-pressed',on?'true':'false');b.setAttribute('aria-label',on?'Ẩn nhãn mục lục':'Hiện nhãn mục lục')}"
          "if(b)b.addEventListener('click',function(){show(!nav.hasAttribute('data-tooltip-show-children'))});"
          "if(matchMedia('(hover:hover)').matches){document.addEventListener('mousemove',function(e){nav.toggleAttribute('data-hover',e.clientX>=innerWidth-176||nav.contains(e.target))},{passive:true});"
          "document.documentElement.addEventListener('mouseleave',function(){nav.removeAttribute('data-hover')})}"
          "nav.addEventListener('click',function(e){if(e.target.closest('a'))show(false)});"
          "document.addEventListener('keydown',function(e){if(e.key==='Escape')show(false)})})();")
JS_PROGRESS = ("(function(){var b=document.querySelector('.ovs-progress i');if(!b)return;function u(){var d=document.documentElement,m=d.scrollHeight-d.clientHeight;"
               "b.style.width=(m>0?Math.min(100,d.scrollTop/m*100):0)+'%'}addEventListener('scroll',u,{passive:true});u()})();")
# KHÔNG gợn trên chấm TOC map (`:not(.nw-tip)`): khôi phục style.inset='' sau gợn xoá luôn `top` inline của chấm → chấm rơi khỏi vị trí.
# static→relative phải kèm inset:auto: top/bottom/right sót lại (vd nút theme nổi bottom:16px) sẽ đẩy nút nhảy 16px khi bấm — user 24/09
JS_RIPPLE = ("(function(){document.addEventListener('pointerdown',function(e){var el=e.target.closest&&e.target.closest('nav a:not(.nw-tip),button,.diagram-reset');"
             "if(!el||matchMedia('(prefers-reduced-motion: reduce)').matches)return;var r=el.getBoundingClientRect(),s=Math.max(r.width,r.height),k=document.createElement('span');"
             "var po=el.style.position,ov=el.style.overflow,pi=el.style.inset;if(getComputedStyle(el).position==='static'){el.style.position='relative';el.style.inset='auto'}el.style.overflow='hidden';k.className='ovs-ripple';"
             "k.style.cssText='width:'+s+'px;height:'+s+'px;left:'+(e.clientX-r.left-s/2)+'px;top:'+(e.clientY-r.top-s/2)+'px';el.appendChild(k);"
             "setTimeout(function(){k.remove();el.style.position=po;el.style.inset=pi;el.style.overflow=ov},500)})})();")
FAVICON = ('<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 32 32%22%3E'
           '%3Crect width=%2232%22 height=%2232%22 rx=%228%22 fill=%22%230a84ff%22/%3E%3Cpath d=%22M9 11h14M9 16h14M9 21h9%22 stroke=%22white%22 '
           'stroke-width=%222.4%22 stroke-linecap=%22round%22/%3E%3C/svg%3E">')


def _nav_links(nav: str) -> str:
    """Mỗi <a href="#…"> → một CHẤM trên rail (mẫu nw-tocmap, user 30/09): nhãn nằm trong data-tooltip + aria-label, `top` chia đều làm mặc định
    (JS đặt lại theo vị trí heading thật). Trang đã áp bản sidebar cũ (icon tile `.ic`, nhãn `.ovs-lbl` + số thứ tự trong `title`, brand bọc
    `.ovs-mark`) được chuyển sang; link đã là chấm thì giữ nguyên."""
    nav = re.sub(r'<span class="ic"[^>]*>.*?</span>', "", nav, flags=re.S)
    nav = re.sub(r'<span class="ovs-mark" aria-hidden="true">[^<]*</span><span class="ovs-brand">(.*?)</span>(</(?:a|div)>)', r"\1\2", nav, count=1, flags=re.S)
    A = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.S)

    def item(attrs):
        return "href=" in attrs and not re.search(r'href="#"', attrs) and not re.search(r'class="[^"]*\b(?:logo|brand)\b', attrs)

    total, i = sum(1 for m in A.finditer(nav) if item(m.group(1))), [0]

    def one(m):
        attrs, inner = m.group(1), m.group(2)
        if not item(attrs):
            return m.group(0)
        i[0] += 1
        if re.search(r'class="[^"]*\bnw-tip\b', attrs):
            return m.group(0)
        t = re.search(r'\btitle="([^"]*)"', attrs)
        text = t.group(1) if t and "ovs-lbl" in inner else re.sub(r"<[^>]+>", "", inner)
        lab = _h.escape(" ".join(_h.unescape(text).split()), quote=True)
        attrs = re.sub(r'\s+(?:title|style|data-tooltip|aria-label)="[^"]*"', "", attrs)
        cls = re.search(r'class="([^"]*)"', attrs)
        have = cls.group(1).split() if cls else []
        new = " ".join(have + [c for c in ("ovs-na", "nw-tip") if c not in have])
        attrs = attrs.replace(cls.group(0), f'class="{new}"') if cls else attrs + f' class="{new}"'
        return (f'<a{attrs} data-tooltip="{lab}" aria-label="{lab}" style="top:{(i[0] - .5) / total * 100:.2f}%">'
                '<span class="hit"><span class="dot l2"></span></span></a>')

    return A.sub(one, nav)


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
    full = is_docs_shell(html)                                      # docs-shell → đủ bộ khung; sidebar khác → chỉ đổi điều hướng
    if not (full or is_side_nav(html)) or re.search(r'<meta\s+name="overstack-shell"\s+content="none"', html):
        return html
    v = _vendor()
    # khối CỦA MÌNH bỏ ra TRƯỚC khi tính cờ — không thì lần chạy thứ hai thấy chính spy/ripple mình chèn và
    # tưởng trang tự có (hoặc ngược lại chèn đôi). Review t8: overstack áp lần hai sinh spy + ripple thứ hai.
    html = re.sub(rf'<style id="{STYLE_ID}">.*?</style>', "", html, flags=re.S)
    html = re.sub(rf'<script id="{JS_ID}">.*?</script>', "", html, flags=re.S)
    nav0 = re.search(r"<nav\b.*?</nav>", html, re.S).group(0)
    need = {
        "toc": not re.search(r'class="nav-ic', nav0),                       # nav tự dựng icon riêng (overstack.html) → không đụng
        "skip": "skip-link" not in html,
        "fav": not re.search(r'<link\b[^>]*\brel="(?:shortcut )?icon"', html),
        "spy": "IntersectionObserver" not in html,
        "ripple": "ripple" not in html,
        "mm": not re.search(r'mind-?map|class="mm"', html, re.I),
        "plane": not re.search(r"body::before|orbDrift|ovs-orb", re.sub(rf'<style id="{STYLE_ID}">.*?</style>', "", html, flags=re.S)),
        "drag": "diagram-box" in html and not re.search(r"dataset\.draggable|data-draggable|initDraggableDiagrams", html),
    }
    if not full:
        need.update(skip=False, fav=False, ripple=False, mm=False, plane=False, drag=False)
    # 1) nav → rail TOC map
    if need["toc"]:
        m = re.search(r"<nav\b.*?</nav>", html, re.S)
        nav = _nav_links(m.group(0))
        html = html[:m.start()] + nav + html[m.end():]
    # 1a) thanh tiến độ đọc: con TRỰC TIẾP của <body>, KHÔNG trong <nav> — nav có backdrop-filter nên thành khung chứa của
    # position:fixed → thanh bị nhốt trong sidebar 232px (user 24/09 "phải đặt ở đầu cả trang"). Dời cả bản cũ đã lỡ nằm trong nav.
    html = html.replace('<div class="ovs-progress" aria-hidden="true"><i></i></div>', "")
    html = re.sub(r'<div class="ovs-progress" aria-hidden="true"><i style="[^"]*"></i></div>', "", html)
    if full and (need["toc"] or "ovs-na" in html):
        bar = '<div class="ovs-progress" aria-hidden="true"><i></i></div>'
        # sau skip-link nếu đã có, không thì ngay sau <body>: bước 2 chèn skip-link sau <body> → lần đầu ra [skip][bar], các lần sau vẫn [skip][bar] (idempotent)
        sk = re.search(r'<a class="skip-link"[^>]*>.*?</a>', html, re.S) or re.search(r"<body\b[^>]*>", html)
        html = html[:sk.end()] + bar + html[sk.end():] if sk else html.replace("<nav", bar + "<nav", 1)   # không có <body> → trước <nav>, vẫn là con của body
    # 1b) cụm điều khiển nổi góc phải dưới (user 30/09): nút đổi giao diện của lớp nền + nút bật nhãn mục lục. Gỡ hàng "Giao diện" cũ ở
    # đáy sidebar và dải toolbar dính trên của bản trước; idempotent (cụm dựng lại mỗi lần, nút theme nhấc ra rồi đặt lại vào).
    html = re.sub(r'<div class="ovs-theme-row"><span>Giao diện</span>(<button type="button" class="ovs-theme".*?</button>)</div>', r"\1", html, flags=re.S)
    if "ovs-na" in html:
        tg = re.search(r'<button type="button" class="ovs-theme"[^>]*>.*?</button>', html, re.S)
        btn = tg.group(0) if tg else ""
        if tg:
            html = html[:tg.start()] + html[tg.end():]
        html = re.sub(r'<div class="ovs-bar" role="toolbar".*?<!--/ovs-bar--></div>', "", html, flags=re.S)
        bar = ('<div class="ovs-bar" role="toolbar" aria-label="Điều khiển trang">' + btn
               + '<button type="button" class="ovs-navbtn" aria-controls="ovs-sidebar" aria-pressed="false" aria-label="Hiện nhãn mục lục">'
               '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6h11M9 12h11M9 18h11M4 6h1M4 12h1M4 18h1"/></svg></button><!--/ovs-bar--></div>')
        at = html.find("<nav")                                     # ngay TRƯỚC nav, ngoài <main>: main có backdrop-filter/transform sẽ nhốt position:fixed (luật fixed-trapped)
        html = html[:at] + bar + html[at:]
        def _side(m):                                               # đánh dấu NAV chính (nav đầu) — CSS chỉ áp cho nó, không đụng nav minh hoạ
            t = m.group(0)
            c = re.search(r'class="([^"]*)"', t)
            have = c.group(1).split() if c else []                    # so CLASS, không so chuỗi — id="ovs-sidebar" chứa "ovs-side"
            new = " ".join(have + [k for k in ("ovs-side", "nw-tocmap") if k not in have])
            t = t.replace(c.group(0), f'class="{new}"') if c else t.replace("<nav", f'<nav class="{new}"', 1)
            if "data-tooltip-show-children-hover" not in t:          # rê chuột vào rail → bung mọi nhãn (mẫu)
                t = t[:-1] + " data-tooltip-show-children-hover>"
            return t if re.search(r"\bid=", t) else t.replace("<nav", '<nav id="ovs-sidebar"', 1)
        html = re.sub(r"<nav\b[^>]*>", _side, html, count=1)
        nid = re.search(r'<nav\b[^>]*\bid="([^"]+)"', html)                  # nút thu gọn trỏ ĐÚNG id của sidebar (trang có id riêng, vd sc-side)
        if nid:
            html = html.replace('aria-controls="ovs-sidebar"', f'aria-controls="{nid.group(1)}"', 1)
    # 2) a11y: vùng nội dung chính + skip-link trỏ ĐÚNG id của nó
    target = "main"
    mm = re.search(r"<main\b([^>]*)>", html)
    if mm:
        idm = re.search(r'\bid="([^"]+)"', mm.group(1))
        if idm:
            target = idm.group(1)
        else:
            html = html[:mm.start()] + f'<main id="main"{mm.group(1)}>' + html[mm.end():]
    elif full and not re.search(r'\bid="main"', html) and "</nav>" in html and not wrap_blocked(html):
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
        # không max-width: từ khi bỏ sidebar, khung chứa rộng hơn 1100px làm mind map thành dải lơ lửng lệch mép (cổng band-misaligned, đo 30/09 trang overnight-loop-prd)
        css += ".ovs-mindmap{padding:8px 24px 24px}" + v.MM_CSS; js += v.MM_JS
    if need["drag"] and v:
        css += v.DRAG_CSS; js += v.DRAG_JS
    if need["spy"]:
        js += JS_SPY
    if 'class="ovs-progress"' in html:
        js += JS_PROGRESS
    if "nw-tocmap" in html:
        js += JS_TOC
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
