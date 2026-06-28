#!/usr/bin/env python3
"""build-docs-index — sinh MỘT trang glass HTML làm "dashboard chính" cho llmwiki/html/.

README.md trong llmwiki/html/ hứa có `index.html` ("Dashboard chính để duyệt và
tìm kiếm tài liệu") nhưng file đó chưa tồn tại — thư mục có ~25 trang HTML rời rạc,
đặt tên theo tiền tố ngày DDMMYY, mà không có một trang điều hướng nào gom lại.

Tool này quét mọi `llmwiki/html/*.html` (TRỪ chính index.html để chạy lại ổn định),
với mỗi file thì đọc: ngày từ tiền tố DDMMYY, tiêu đề từ `<title>` (hoặc `<h1>` đầu
tiên), kích thước byte, loại (seq/docs/cheatsheet/report suy ra từ tên file), và đánh
dấu "bản cũ" (superseded) cho các phiên bản vN thấp hơn. Sau đó render một LƯỚI THẺ
lọc được: ô tìm kiếm (theo tiêu đề/tên file), sort theo ngày/tên/cỡ, chip lọc theo
loại, và làm mờ các bản cũ.

Trang xuất ra hoàn toàn self-contained (style + script nội tuyến, 0 request ngoài)
theo đúng khuôn liquid-glass của 280626-distill-destinations.html — gồm CẢ hai nút
điều hướng: nút ☰ nổi để mở và nút ✕ trong sidebar để đóng.

Dùng:
    python3 fdk/tools/build-docs-index.py

KHÔNG sửa file dùng-chung: chỉ GHI đúng llmwiki/html/index.html.
"""
import glob
import os
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML_DIR = ROOT / "llmwiki" / "html"
OUT = HTML_DIR / "index.html"
GENERATED = "2026-06-28"  # hardcode theo yêu cầu — KHÔNG gọi datetime.now()

TYPE_ORDER = ["all", "seq", "docs", "cheatsheet", "report"]
TYPE_LABEL = {"all": "Tất cả", "seq": "Sequence", "docs": "Docs",
              "cheatsheet": "Cheatsheet", "report": "Report"}


def esc(s: str) -> str:
    return escape(str(s), quote=True)


def human(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n / 1048576:.1f} MB"
    if n >= 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n} B"


def extract_title(text: str, fallback: str) -> str:
    head = text.split("</head>", 1)[0]
    m = re.search(r"<title>(.*?)</title>", head, re.S | re.I)
    if not m:
        m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S | re.I)
    if not m:
        return fallback
    t = re.sub(r"<[^>]+>", "", m.group(1))
    t = re.sub(r"\s+", " ", t).strip()
    return t or fallback


def parse_date(stem: str):
    """DDMMYY-… → (iso 'YYYY-MM-DD', display 'DD/MM/YYYY'); không có tiền tố → (None, '—')."""
    m = re.match(r"^(\d{2})(\d{2})(\d{2})-", stem)
    if not m:
        return None, "—"
    dd, mm, yy = m.group(1), m.group(2), m.group(3)
    return f"20{yy}-{mm}-{dd}", f"{dd}/{mm}/20{yy}"


def doc_type(name: str) -> str:
    n = name.lower()
    if "cheatsheet" in n:
        return "cheatsheet"
    if "report" in n:
        return "report"
    if "-seq" in n:
        return "seq"
    return "docs"


def parse_version(stem: str):
    """Bỏ tiền tố ngày, rồi tách hậu tố '-vN' ở CUỐI → (base, version|None)."""
    core = re.sub(r"^\d{6}-", "", stem)
    m = re.search(r"-v(\d+)$", core)
    if m:
        return core[:m.start()], int(m.group(1))
    return core, None


def build_card(d: dict) -> str:
    sup = " superseded" if d["superseded"] else ""
    sup_tag = '<span class="sup-tag">bản cũ</span>' if d["superseded"] else ""
    return (
        f'<a class="doc-card type-{d["type"]}{sup}" href="{esc(d["file"])}" '
        f'data-title="{esc(d["title"].lower())}" data-file="{esc(d["file"].lower())}" '
        f'data-type="{d["type"]}" data-date="{d["date_iso"] or ""}" '
        f'data-size="{d["size"]}" data-super="{1 if d["superseded"] else 0}">'
        f'<div class="dc-top"><span class="badge">{d["type"]}</span>{sup_tag}'
        f'<span class="dc-size">{human(d["size"])}</span></div>'
        f'<h3 class="dc-title">{esc(d["title"])}</h3>'
        f'<div class="dc-meta"><span class="dc-file">{esc(d["file"])}</span>'
        f'<span class="dc-date">{esc(d["date_disp"])}</span></div></a>'
    )


def scan() -> list:
    docs = []
    for path in sorted(glob.glob(os.path.join(HTML_DIR, "*.html"))):
        name = os.path.basename(path)
        if name == "index.html":  # tự loại để chạy lại ổn định
            continue
        stem = name[:-5]
        try:
            text = Path(path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        date_iso, date_disp = parse_date(stem)
        base, version = parse_version(stem)
        docs.append({
            "file": name,
            "stem": stem,
            "title": extract_title(text, stem),
            "size": os.path.getsize(path),
            "type": doc_type(name),
            "date_iso": date_iso,
            "date_disp": date_disp,
            "base": base,
            "version": version,
            "superseded": False,
        })

    # superseded: trong cùng base, mọi vN thấp hơn vN cao nhất bị làm mờ
    max_ver: dict = {}
    for d in docs:
        if d["version"] is not None:
            max_ver[d["base"]] = max(max_ver.get(d["base"], 0), d["version"])
    for d in docs:
        if d["version"] is not None and d["version"] < max_ver[d["base"]]:
            d["superseded"] = True

    # thứ tự mặc định = ngày giảm dần (không-ngày xuống cuối), rồi theo tên
    docs.sort(key=lambda d: (d["date_iso"] or "", d["stem"]), reverse=True)
    return docs


STYLE = """:root{
  --font-text:-apple-system,BlinkMacSystemFont,'SF Pro Text','Helvetica Neue','Roboto','Segoe UI',sans-serif;
  --font-display:-apple-system,BlinkMacSystemFont,'SF Pro Display','Helvetica Neue','Roboto','Segoe UI',sans-serif;
  --font-mono:'SF Mono',ui-monospace,'SFMono-Regular',Menlo,'Roboto Mono',Consolas,monospace;
  --glass-2:rgba(255,255,255,.7);--glass-3:rgba(255,255,255,.88);--blur-2:8px;--blur-3:4px;
  --edge-hi:inset 0 1px 0 rgba(255,255,255,.85);--border:rgba(30,90,170,.14);--t1:#0f0f12;--t2:#4a4a55;
}
*{box-sizing:border-box}
html{background:#e9f0fb;scrollbar-width:thin;scrollbar-color:transparent transparent}
html.scrolling{scrollbar-color:rgba(10,132,255,.32) transparent}
body{margin:0;padding-left:210px;font-family:var(--font-text);color:var(--t1);line-height:1.6;
  background:radial-gradient(900px 500px at 12% -10%,rgba(10,132,255,.10),transparent 60%),radial-gradient(700px 420px at 95% 15%,rgba(90,162,232,.08),transparent 55%),linear-gradient(180deg,#f7fbff,#eaf2fd);
  transition:padding-left .28s cubic-bezier(.4,0,.2,1)}
body::before{content:'';position:fixed;inset:-10%;z-index:-1;pointer-events:none;
  background:radial-gradient(640px 440px at 10% 14%,rgba(10,132,255,.22),transparent 65%),radial-gradient(380px 460px at 4% 52%,rgba(48,176,199,.18),transparent 65%),radial-gradient(540px 400px at 88% 10%,rgba(88,86,214,.13),transparent 60%),radial-gradient(720px 500px at 74% 76%,rgba(48,176,199,.13),transparent 65%),radial-gradient(480px 380px at 16% 86%,rgba(255,149,0,.12),transparent 60%);
  animation:orbDrift 46s ease-in-out infinite alternate}
@keyframes orbDrift{100%{transform:translate(2.2%,1.6%) scale(1.045)}}
body::after{content:'';position:fixed;inset:0;z-index:-1;pointer-events:none;background-image:radial-gradient(rgba(30,90,170,.11) 1px,transparent 1.3px);background-size:22px 22px;mask-image:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,.22))}
@media(prefers-reduced-motion:reduce){body::before{animation:none}}
::-webkit-scrollbar{width:11px;height:11px;background:transparent}
::-webkit-scrollbar-track,::-webkit-scrollbar-track-piece,::-webkit-scrollbar-corner,::-webkit-scrollbar-button{background:transparent;border:0;box-shadow:none}
::-webkit-scrollbar-thumb{background:transparent;border-radius:8px;border:3px solid transparent;background-clip:content-box;transition:background-color .25s ease}
html.scrolling::-webkit-scrollbar-thumb,nav.scrolling::-webkit-scrollbar-thumb,::-webkit-scrollbar-thumb:hover{background-color:rgba(10,132,255,.32)}
nav{position:fixed;top:0;left:0;bottom:0;width:210px;z-index:100;overflow-y:auto;display:flex;flex-direction:column;gap:2px;padding:18px 12px;
  background:linear-gradient(165deg,rgba(255,255,255,.46),rgba(255,255,255,.22) 48%,rgba(240,248,255,.34));
  backdrop-filter:blur(24px) saturate(1.7) brightness(1.04);-webkit-backdrop-filter:blur(24px) saturate(1.7) brightness(1.04);
  border-right:1px solid rgba(255,255,255,.55);box-shadow:inset 0 1px 0 rgba(255,255,255,.9),4px 0 24px rgba(30,90,170,.08);transition:transform .28s cubic-bezier(.4,0,.2,1)}
nav::before{content:'';position:absolute;inset:0;pointer-events:none;background:radial-gradient(220px 160px at 18% 4%,rgba(255,255,255,.55),transparent 70%),linear-gradient(115deg,rgba(255,255,255,.28),transparent 28%,transparent 72%,rgba(255,255,255,.14))}
nav>*{position:relative}
nav .logo{margin:0 0 14px;padding:6px 10px;font-family:var(--font-display);font-weight:800;font-size:17px;letter-spacing:-.02em;background:linear-gradient(135deg,#0a84ff,#64b5f7);-webkit-background-clip:text;background-clip:text;color:transparent}
nav .logo small{display:block;font-size:10px;font-weight:600;color:var(--t2);-webkit-text-fill-color:var(--t2)}
nav a{padding:8px 12px;border-radius:10px;font-size:13px;color:var(--t2);text-decoration:none;position:relative;overflow:hidden;transition:background .15s,color .15s;display:flex;align-items:center;justify-content:space-between;gap:8px}
nav a:hover{background:rgba(10,132,255,.06);color:#0a84ff}
nav a.active{color:#0a84ff;background:rgba(10,132,255,.08);font-weight:600}
nav a span{font-size:10px;font-weight:700;color:var(--t2);background:rgba(30,90,170,.08);border-radius:999px;padding:1px 7px;min-width:18px;text-align:center}
nav a.active span{color:#0a84ff;background:rgba(10,132,255,.14)}
.nav-sep{margin:10px 6px 4px;font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--t2);opacity:.7}
.nav-stat{margin-top:auto;padding:12px 10px 4px;font-size:11px;color:var(--t2);line-height:1.55;border-top:1px solid var(--border)}
.nav-stat b{color:#0a84ff}
.nav-stat small{display:block;margin-top:3px;opacity:.8;font-family:var(--font-mono);font-size:10px}
.nav-close{position:absolute;top:10px;right:10px;width:26px;height:26px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:12px;color:var(--t2);cursor:pointer;background:rgba(0,0,0,.04);border:none}
body.nav-collapsed nav{transform:translateX(-100%)}body.nav-collapsed{padding-left:0}
.nav-toggle{position:fixed;top:12px;left:12px;z-index:120;width:32px;height:32px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:14px;color:var(--t2);cursor:pointer;background:linear-gradient(165deg,rgba(255,255,255,.5),rgba(255,255,255,.24));backdrop-filter:blur(24px) saturate(1.7);-webkit-backdrop-filter:blur(24px) saturate(1.7);border:1px solid transparent;box-shadow:inset 0 1px 0 rgba(255,255,255,.75),0 0 0 1px rgba(30,90,170,.08),0 2px 10px rgba(30,90,170,.12);transition:opacity .2s,transform .28s}
.nav-toggle:hover{color:#0a84ff}body:not(.nav-collapsed) .nav-toggle{opacity:0;pointer-events:none}
@media(max-width:640px){body{padding-left:0}}
.hero{max-width:1100px;margin:0 auto;padding:84px 24px 14px}
.hero .eyebrow{display:inline-block;font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:#0a84ff;background:rgba(10,132,255,.10);padding:4px 12px;border-radius:999px;margin-bottom:16px}
.hero h1{font-family:var(--font-display);font-size:clamp(30px,4.6vw,50px);line-height:1.06;letter-spacing:-.02em;margin:0 0 14px;background:linear-gradient(135deg,#0a84ff,#5aa2e8,#cfe3fb);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{font-size:16.5px;color:var(--t2);max-width:760px;margin:0}
/* ─── docs-index additions (cùng token glass) ─── */
.toolbar{position:sticky;top:0;z-index:30;display:flex;flex-wrap:wrap;gap:10px;align-items:center;
  max-width:1100px;margin:18px auto 0;padding:12px 24px;border-radius:16px;
  background:linear-gradient(180deg,rgba(247,251,255,.9),rgba(247,251,255,.66));
  backdrop-filter:blur(16px) saturate(1.5);-webkit-backdrop-filter:blur(16px) saturate(1.5);
  border:1px solid var(--border);box-shadow:var(--edge-hi),0 4px 18px rgba(30,90,170,.08)}
.search{flex:1 1 260px;min-width:180px;font-family:var(--font-text);font-size:14px;color:var(--t1);
  padding:10px 14px;border-radius:12px;border:1px solid var(--border);
  background:var(--glass-3);box-shadow:var(--edge-hi),0 2px 10px rgba(30,90,170,.06);outline:none}
.search:focus{border-color:rgba(10,132,255,.5);box-shadow:var(--edge-hi),0 0 0 3px rgba(10,132,255,.14)}
.search::placeholder{color:var(--t2)}
.toolbar select{font-family:var(--font-text);font-size:13px;color:var(--t1);padding:9px 12px;border-radius:12px;
  border:1px solid var(--border);background:var(--glass-3);box-shadow:var(--edge-hi);cursor:pointer;outline:none}
.hide-super{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;color:var(--t2);cursor:pointer;user-select:none;white-space:nowrap}
.hide-super input{accent-color:#0a84ff;width:15px;height:15px}
.toolbar .count{font-size:12.5px;color:var(--t2);font-weight:600;white-space:nowrap;margin-left:auto}
.toolbar .count b{color:#0a84ff}
.chips{display:flex;flex-wrap:wrap;gap:8px;max-width:1100px;margin:12px auto 0;padding:0 24px}
.chip{font-family:var(--font-text);font-size:12.5px;font-weight:600;color:var(--t2);cursor:pointer;
  padding:6px 13px;border-radius:999px;border:1px solid var(--border);background:var(--glass-2);
  box-shadow:var(--edge-hi);transition:color .15s,background .15s,border-color .15s}
.chip b{opacity:.6;font-weight:700;margin-left:3px}
.chip:hover{color:#0a84ff;border-color:rgba(10,132,255,.4)}
.chip.active{color:#fff;background:linear-gradient(135deg,#0a84ff,#5aa2e8);border-color:transparent}
.chip.active b{opacity:.85}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:16px;
  max-width:1100px;margin:18px auto 0;padding:0 24px}
.doc-card{position:relative;display:flex;flex-direction:column;gap:10px;min-height:140px;text-decoration:none;color:inherit;
  background:var(--glass-2);backdrop-filter:blur(var(--blur-2)) saturate(1.1);-webkit-backdrop-filter:blur(var(--blur-2)) saturate(1.1);
  border:1px solid var(--border);border-radius:16px;box-shadow:var(--edge-hi),0 4px 20px rgba(0,0,0,.06);
  padding:16px 17px 16px 19px;overflow:hidden;transition:transform .18s,box-shadow .18s,opacity .18s}
.doc-card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--accent,#0a84ff)}
.doc-card:hover{transform:translateY(-3px);box-shadow:var(--edge-hi),0 10px 30px rgba(30,90,170,.16)}
.dc-top{display:flex;align-items:center;gap:8px}
.badge{font-size:10.5px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;
  padding:3px 9px;border-radius:999px;color:var(--accent,#0a84ff);background:var(--accent-bg,rgba(10,132,255,.12))}
.sup-tag{font-size:9.5px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:#b96b00;background:rgba(255,149,0,.16);padding:2px 7px;border-radius:999px}
.dc-size{margin-left:auto;font-family:var(--font-mono);font-size:11px;color:var(--t2)}
.dc-title{font-family:var(--font-display);font-size:15px;line-height:1.34;letter-spacing:-.01em;color:var(--t1);margin:0;
  display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.dc-meta{display:flex;align-items:center;gap:8px;margin-top:auto;font-size:11px;color:var(--t2)}
.dc-file{font-family:var(--font-mono);font-size:10.5px;color:#0a5ec7;background:rgba(10,132,255,.07);border-radius:5px;padding:2px 6px;
  max-width:64%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dc-date{margin-left:auto;font-variant-numeric:tabular-nums;white-space:nowrap}
.doc-card.superseded{opacity:.55;filter:saturate(.55)}
.doc-card.superseded:hover{opacity:.9}
.type-seq{--accent:#0a84ff;--accent-bg:rgba(10,132,255,.12)}
.type-docs{--accent:#30b0c7;--accent-bg:rgba(48,176,199,.15)}
.type-cheatsheet{--accent:#f08c00;--accent-bg:rgba(255,149,0,.15)}
.type-report{--accent:#e0264b;--accent-bg:rgba(255,45,85,.12)}
.no-results{display:none;max-width:1100px;margin:34px auto;padding:0 24px;color:var(--t2);font-size:14.5px}
footer{max-width:1100px;margin:30px auto 0;padding:24px 24px 60px;font-size:12.5px;color:var(--t2);border-top:1px solid var(--border)}
footer code{font-family:var(--font-mono);font-size:.85em;background:rgba(10,132,255,.08);padding:1px 5px;border-radius:5px;color:#0a5ec7}"""

SCRIPTS = """<script>
/* nút điều hướng: ☰ nổi để MỞ + ✕ trong sidebar để ĐÓNG (giống khuôn distill) */
(function(){const nav=document.querySelector('nav');if(!nav)return;const b=document.createElement('button');b.className='nav-toggle';b.textContent='\\u2630';document.body.appendChild(b);const c=document.createElement('button');c.className='nav-close';c.textContent='\\u2715';nav.appendChild(c);const ap=v=>{document.body.classList.toggle('nav-collapsed',v);try{localStorage.setItem('nc',v?'1':'0')}catch(e){}};b.onclick=()=>ap(false);c.onclick=()=>ap(true);try{const s=localStorage.getItem('nc');if(s==='1'||(s!=='0'&&matchMedia('(max-width:640px)').matches))ap(true)}catch(e){}})();
/* thanh cuộn tự ẩn */
(function(){const f=el=>{let t;return()=>{el.classList.add('scrolling');clearTimeout(t);t=setTimeout(()=>el.classList.remove('scrolling'),900)}};window.addEventListener('scroll',f(document.documentElement),{passive:true});})();
/* lọc + sort thẻ tài liệu */
(function(){
  const grid=document.getElementById('grid');if(!grid)return;
  const cards=[...grid.querySelectorAll('.doc-card')];
  const q=document.getElementById('q'),sortSel=document.getElementById('sort'),hideSuper=document.getElementById('hideSuper');
  const countEl=document.getElementById('count'),noRes=document.getElementById('noResults');
  const chips=[...document.querySelectorAll('.chip')],navFilters=[...document.querySelectorAll('.nav-filter')];
  let curType='all';
  function apply(){
    const s=q.value.trim().toLowerCase(),hs=hideSuper.checked;let n=0;
    cards.forEach(c=>{
      const okT=curType==='all'||c.dataset.type===curType;
      const okQ=!s||c.dataset.title.indexOf(s)>=0||c.dataset.file.indexOf(s)>=0;
      const okS=!hs||c.dataset.super==='0';
      const show=okT&&okQ&&okS;c.style.display=show?'':'none';if(show)n++;
    });
    countEl.textContent=n;noRes.style.display=n?'none':'block';
  }
  function sortCards(){
    const m=sortSel.value;
    cards.slice().sort((a,b)=>{
      if(m==='title')return a.dataset.title.localeCompare(b.dataset.title);
      if(m==='size-desc')return b.dataset.size-a.dataset.size;
      if(m==='size-asc')return a.dataset.size-b.dataset.size;
      const da=a.dataset.date,db=b.dataset.date;
      if(m==='date-asc'){if(!da)return 1;if(!db)return -1;return da<db?-1:da>db?1:0;}
      if(!da)return 1;if(!db)return -1;return da<db?1:da>db?-1:0;
    }).forEach(c=>grid.appendChild(c));
  }
  function setType(t){curType=t;
    chips.forEach(c=>c.classList.toggle('active',c.dataset.type===t));
    navFilters.forEach(c=>c.classList.toggle('active',c.dataset.type===t));apply();}
  q.addEventListener('input',apply);
  hideSuper.addEventListener('change',apply);
  sortSel.addEventListener('change',()=>{sortCards();apply();});
  chips.forEach(c=>c.addEventListener('click',()=>setType(c.dataset.type)));
  navFilters.forEach(c=>c.addEventListener('click',e=>{e.preventDefault();setType(c.dataset.type);}));
  apply();
})();
</script>"""


def main() -> None:
    docs = scan()
    total = len(docs)
    type_counts: dict = {}
    for d in docs:
        type_counts[d["type"]] = type_counts.get(d["type"], 0) + 1
    total_bytes = sum(d["size"] for d in docs)
    superseded_n = sum(1 for d in docs if d["superseded"])

    cards_html = "\n".join(build_card(d) for d in docs)
    chips_html = "\n".join(
        f'<button class="chip{" active" if t == "all" else ""}" data-type="{t}">'
        f'{TYPE_LABEL[t]} <b>{total if t == "all" else type_counts.get(t, 0)}</b></button>'
        for t in TYPE_ORDER
    )
    nav_filters_html = "\n  ".join(
        f'<a href="#" class="nav-filter{" active" if t == "all" else ""}" data-type="{t}">'
        f'{TYPE_LABEL[t]}<span>{total if t == "all" else type_counts.get(t, 0)}</span></a>'
        for t in TYPE_ORDER
    )

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Docs Index — llmwiki/html</title>
<style>
{STYLE}
</style>
</head>
<body>
<nav>
  <div class="logo">Docs Index<small>llmwiki · html</small></div>
  <div class="nav-sep">Lọc theo loại</div>
  {nav_filters_html}
  <div class="nav-stat"><b>{total}</b> trang · {human(total_bytes)}<br>{superseded_n} bản cũ (superseded)<small>generated {GENERATED}</small></div>
</nav>

<header class="hero">
  <span class="eyebrow">Dashboard chính · llmwiki/html</span>
  <h1>Thư viện tài liệu HTML</h1>
  <p>Một điểm vào duy nhất để duyệt <b>{total}</b> trang tài liệu đã render trong thư mục này.
  Mỗi thẻ hiện loại, ngày (đọc từ tiền tố tên file), kích thước và tiêu đề thật của trang.
  Dùng ô tìm kiếm, sort và các chip loại để lọc; những bản phiên cũ (vN thấp hơn) được làm mờ để bạn ưu tiên bản mới nhất.</p>
</header>

<div class="toolbar">
  <input id="q" class="search" type="search" placeholder="Tìm theo tiêu đề hoặc tên file…" aria-label="Tìm tài liệu">
  <select id="sort" aria-label="Sắp xếp">
    <option value="date-desc">Mới nhất trước</option>
    <option value="date-asc">Cũ nhất trước</option>
    <option value="title">Tên A → Z</option>
    <option value="size-desc">Cỡ lớn nhất</option>
    <option value="size-asc">Cỡ nhỏ nhất</option>
  </select>
  <label class="hide-super"><input id="hideSuper" type="checkbox"> Ẩn bản cũ</label>
  <span class="count">Hiện <b id="count">{total}</b> / {total} trang</span>
</div>

<div class="chips">
{chips_html}
</div>

<main id="grid" class="grid">
{cards_html}
</main>

<p id="noResults" class="no-results">Không có trang nào khớp bộ lọc — thử xoá từ khoá hoặc chọn lại loại.</p>

<footer>Docs Index · sinh tự động bởi <code>fdk/tools/build-docs-index.py</code> ·
self-contained, offline-proof (0 request ngoài) · quét <code>llmwiki/html/*.html</code> (trừ chính nó) · generated {GENERATED}.</footer>

{SCRIPTS}
</body>
</html>
"""
    OUT.write_text(html, encoding="utf-8")
    print(f"✓ index.html: {total} trang ({superseded_n} superseded) · "
          f"by-type {{{', '.join(f'{t}:{type_counts.get(t, 0)}' for t in TYPE_ORDER[1:])}}}")
    print(f"  → {OUT.relative_to(ROOT)} · {len(html) / 1024:.1f} KB · tổng nguồn {human(total_bytes)}")


if __name__ == "__main__":
    main()
