#!/usr/bin/env python3
"""build-design-showcase — trang MẪU CHUẨN cho mọi thiết kế mặc định (PLAN 220926-design-showcase t2).

Mỗi khối = một mẫu chạy thật của một phần thiết kế có luật (lưới 1–4 cột, sidebar, kanban, list, motion, hướng dẫn,
chart, graph…) kèm code đúng như bản chạy. Harness và agent audit theo trang này: thiếu mẫu thì lấy khối theo id,
nghi ngờ một UI thì so với khối cùng id.

Khối sống ở các file phẳng `showcase_<nhóm>.py` cạnh file này (installer chỉ copy `fdk/tools/*.py` phẳng xuống
`~/.claude/harness/fdk/tools/`). Mỗi file có `GROUP = "<tên nhóm>"` và `BLOCKS = [dict(...)]`:
    id     neo `#b-<id>`, ổn định (là index — đừng đổi tên)
    title  tiêu đề khối (viết hoa chữ đầu)
    rules  list id luật khối này minh hoạ (xem showcase_rules.py)
    html   markup khối; phần tử gốc mang class `sc-<id>`
    css    CSS khối, mọi selector bắt đầu bằng `.sc-<id>` (không đè khối khác)
    js     JS khối (tuỳ chọn); biến `root` = phần tử `.sc-<id>`
    note   một câu: khối này chuẩn ở chỗ nào

    python3 fdk/tools/build-design-showcase.py                 # ghi skills/hallmark/references/design-showcase.html
    python3 fdk/tools/build-design-showcase.py --out x.html
    python3 fdk/tools/build-design-showcase.py --list          # index: id · nhóm · tiêu đề · luật
    python3 fdk/tools/build-design-showcase.py --get kanban    # code một khối (dán thẳng vào trang)
    # máy khách: python3 ~/.claude/harness/fdk/tools/build-design-showcase.py --get kanban
"""
from __future__ import annotations

import html as H
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE.parents[1] / "skills" / "hallmark" / "references" / "design-showcase.html"
GROUP_ORDER = ["showcase_layout", "showcase_components", "showcase_motion", "showcase_dataviz"]


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def groups() -> list:
    """[(tên nhóm, slug, [block…])] theo GROUP_ORDER, rồi các file showcase_*.py khác (nếu có) theo tên."""
    files = sorted(HERE.glob("showcase_*.py"), key=lambda p: (GROUP_ORDER.index(p.stem) if p.stem in GROUP_ORDER else 99, p.stem))
    out = []
    for f in files:
        mod = _load(f)
        if hasattr(mod, "BLOCKS"):
            out.append((mod.GROUP, f.stem.replace("showcase_", ""), mod.BLOCKS))
    return out


def all_blocks() -> list:
    return [dict(b, group=g) for g, _, bs in groups() for b in bs]


def snippet(b: dict) -> str:
    """Code một khối, dán thẳng vào trang được (HTML + <style> + <script>)."""
    parts = [b["html"].strip()]
    if b.get("css"):
        parts.append("<style>\n" + b["css"].strip() + "\n</style>")
    if b.get("js"):
        parts.append("<script>\n(() => {\n  const root = document.querySelector('.sc-" + b["id"] + "');\n"
                     + b["js"].strip() + "\n})();\n</script>")
    return "\n".join(parts)


PAGE_CSS = """
body{margin:0;color:var(--ovs-ink)}
nav.sc-side{position:fixed;inset:0 auto 0 0;z-index:40;width:248px;overflow-y:auto;padding:24px 16px 0;box-sizing:border-box;transition:transform .2s ease-out;
  border-right:1px solid var(--ovs-border);background:rgba(var(--ovs-glass-rgb),.55);backdrop-filter:blur(24px) saturate(1.2);-webkit-backdrop-filter:blur(24px) saturate(1.2)}
nav.sc-side .logo{display:block;font-family:var(--font-display);font-size:18px;font-weight:var(--fw-heading,600);letter-spacing:var(--ls-heading,-.02em);padding:0 8px 16px;color:var(--ovs-ink);text-decoration:none}
nav.sc-side .grp{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ovs-ink);margin:24px 8px 8px}
nav.sc-side a:not(.logo){display:flex;align-items:center;min-height:32px;padding:4px 8px;border-radius:8px;font-size:13px;color:var(--ovs-ink);text-decoration:none}
nav.sc-side a:not(.logo):hover{background:var(--ovs-accent-bg)}
main.sc-main{margin-left:248px;padding:72px 40px 96px;max-width:1040px;box-sizing:border-box}
.sc-navbtn{position:fixed;top:16px;left:264px;z-index:45;width:36px;height:36px;display:grid;place-items:center;border:1px solid var(--ovs-border);border-radius:10px;background:rgba(var(--ovs-glass-rgb),.7);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);color:var(--ovs-ink);cursor:pointer;transition:left .2s ease-out}
.sc-navbtn svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8}
.sc-scrim{display:none}
html.sc-nav-off nav.sc-side{transform:translateX(-100%)}html.sc-nav-off main.sc-main{margin-left:0}html.sc-nav-off .sc-navbtn{left:16px}
.sc-hero{margin:0 0 48px}.sc-hero h1{font-size:40px;line-height:1.25;margin:0 0 16px}.sc-hero p{max-width:var(--measure);margin:0 0 16px;color:var(--ovs-ink2)}
.sc-group{margin:0 0 64px}.sc-group>h2{font-size:28px;line-height:1.42;margin:40px 0 24px;padding-top:16px}
.sc-block{margin:0 0 48px}.sc-block>h3{font-size:22px;line-height:1.55;margin:32px 0 16px}
.sc-block>.sc-note{margin:0 0 24px;max-width:var(--measure);color:var(--ovs-ink2)}
.sc-demo{border:1px solid var(--ovs-border);border-radius:14px;padding:24px;background:rgba(var(--ovs-glass-rgb),.7);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);box-shadow:inset 0 1px 0 rgba(255,255,255,.6),0 8px 24px rgba(30,90,170,.06)}
.sc-meta{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:24px 0 0;font-size:13px;color:var(--ovs-ink2)}
.sc-meta code{font-family:inherit;font-size:12px;font-weight:500;padding:2px 8px;border-radius:999px;background:var(--ovs-accent-bg);color:var(--ovs-ink)}
details.sc-code{margin:12px 0 0}
details.sc-code>summary{cursor:pointer;display:inline-flex;align-items:center;min-height:32px;padding:4px 12px;border:1px solid var(--ovs-border);border-radius:999px;font-size:13px}
.sc-codebox{position:relative;margin:12px 0 0}
.sc-codebox pre{margin:0;padding:16px;max-height:420px;overflow:auto;border-radius:12px;background:var(--ovs-surface2);border:1px solid var(--ovs-border);font-size:12px;line-height:1.6}
.sc-copy{position:absolute;top:8px;right:8px;min-height:32px;padding:4px 12px;border:1px solid var(--ovs-border);border-radius:999px;background:var(--ovs-surface);color:var(--ovs-ink);font:inherit;font-size:12px;cursor:pointer}
@media (max-width:900px){nav.sc-side{width:min(300px,85vw);transform:translateX(-100%)}html.sc-nav-open nav.sc-side{transform:none}
  main.sc-main,html.sc-nav-off main.sc-main{margin-left:0;padding:72px 16px 64px}.sc-navbtn,html.sc-nav-off .sc-navbtn{left:16px}
  html.sc-nav-open .sc-navbtn{left:calc(min(300px,85vw) + 8px)}
  html.sc-nav-open .sc-scrim{display:block;position:fixed;inset:0;z-index:35;background:rgba(0,0,0,.35)}}
"""
PAGE_JS = """(()=>{const h=document.documentElement,b=document.querySelector('.sc-navbtn'),mob=matchMedia('(max-width:900px)');if(!b)return;
const on=()=>mob.matches?h.classList.contains('sc-nav-open'):!h.classList.contains('sc-nav-off');
const paint=()=>{b.setAttribute('aria-expanded',on());b.setAttribute('aria-label',on()?'Đóng sidebar':'Mở sidebar')};
try{if(localStorage.getItem('ovs-nav')==='off')h.classList.add('sc-nav-off')}catch(e){}paint();
b.addEventListener('click',()=>{if(mob.matches)h.classList.toggle('sc-nav-open');else{const off=h.classList.toggle('sc-nav-off');try{localStorage.setItem('ovs-nav',off?'off':'on')}catch(e){}}paint()});
const close=()=>{h.classList.remove('sc-nav-open');paint()};document.querySelector('.sc-scrim').addEventListener('click',close);
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&h.classList.contains('sc-nav-open'))close()});
document.querySelectorAll('nav.sc-side a[href^="#b-"]').forEach(a=>a.addEventListener('click',()=>{if(mob.matches)close()}));mob.addEventListener('change',paint)})();
document.addEventListener('click',e=>{const b=e.target.closest('.sc-copy');if(!b)return;
const t=b.parentElement.querySelector('code').textContent;const done=()=>{b.textContent='Đã chép';setTimeout(()=>b.textContent='Sao chép',1200)};
if(navigator.clipboard)navigator.clipboard.writeText(t).then(done,done);else done()});"""


def render_block(b: dict) -> str:
    rules = "".join(f"<code>{H.escape(r)}</code>" for r in b.get("rules", []))
    return (f'<article class="sc-block" id="b-{b["id"]}" data-block="{b["id"]}" data-rules="{",".join(b.get("rules", []))}">'
            f'<h3>{H.escape(b["title"])}</h3><p class="sc-note">{H.escape(b.get("note", ""))}</p>'
            f'<div class="sc-demo">{b["html"]}</div>'
            f'<div class="sc-meta">Luật: {rules}</div>'
            f'<details class="sc-code"><summary>Xem code</summary><div class="sc-codebox">'
            f'<button class="sc-copy" type="button">Sao chép</button>'
            f'<pre><code class="language-html">{H.escape(snippet(b))}</code></pre></div></details></article>')


def build() -> str:
    gs = groups()
    n_blocks = sum(len(bs) for _, _, bs in gs)
    rules = _load(HERE / "showcase_rules.py").RULES
    nav = ['<nav class="sc-side" id="sc-side" aria-label="Index khối"><a class="logo" href="#top">Design showcase</a>']
    body = []
    for name, slug, bs in gs:
        nav.append(f'<div class="grp">{H.escape(name)}</div>')
        nav += [f'<a href="#b-{b["id"]}">{H.escape(b["title"])}</a>' for b in bs]
        body.append(f'<section class="sc-group" id="g-{slug}"><h2>{H.escape(name)}</h2>{"".join(render_block(b) for b in bs)}</section>')
    nav.append("</nav>")
    css = PAGE_CSS + "\n".join(b.get("css", "") for _, _, bs in gs for b in bs)
    js = PAGE_JS + "\n".join(f"(()=>{{const root=document.querySelector('#b-{b['id']} .sc-{b['id']}');if(!root)return;{b['js']}}})();"
                             for _, _, bs in gs for b in bs if b.get("js"))
    page = ('<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Design showcase</title>'
            '<meta name="description" content="Mẫu chuẩn mọi phần thiết kế mặc định của overstack — mỗi khối có index, bản chạy thật và code; harness và agent audit theo trang này.">'
            '<meta name="generator" content="fdk/tools/build-design-showcase.py — ĐỪNG sửa tay, sửa showcase_*.py rồi build lại">'
            f'<style>{css}</style></head><body id="top">{"".join(nav)}'
            '<button class="sc-navbtn" type="button" aria-controls="sc-side" aria-expanded="true" aria-label="Đóng sidebar">'
            '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="3"/><path d="M9 4v16"/></svg></button><div class="sc-scrim"></div>'
            '<main class="sc-main" id="main"><header class="sc-hero"><h1>Design showcase</h1>'
            f'<p>Mẫu chuẩn cho mọi thiết kế mặc định của framework: {n_blocks} khối, phủ {len(rules)} luật. '
            'User không nói khác thì làm đúng như khối cùng loại ở đây.</p>'
            '<p>Mỗi khối có bản chạy thật, danh sách luật nó minh hoạ, và code gập lại. Agent lấy code bằng lệnh '
            '<code>build-design-showcase.py --get &lt;id&gt;</code>.</p></header>'
            f'{"".join(body)}</main><script>{js}</script></body></html>')
    base = _load(HERE / "html_base.py")
    return base.apply(page)


def main(argv: list) -> int:
    if "--list" in argv:
        for b in all_blocks():
            print(f'{b["id"]:<18} {b["group"]:<22} {b["title"]:<40} {",".join(b.get("rules", []))}')
        return 0
    if "--get" in argv:
        want = argv[argv.index("--get") + 1] if len(argv) > argv.index("--get") + 1 else ""
        hit = [b for b in all_blocks() if b["id"] == want]
        if not hit:
            print(f"không có khối '{want}' — xem --list", file=sys.stderr); return 1
        print(snippet(hit[0])); return 0
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else DEFAULT_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(), encoding="utf-8")
    print(f"→ {out}  ({len(all_blocks())} khối)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
