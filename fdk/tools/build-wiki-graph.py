#!/usr/bin/env python3
"""wiki-core v2 Bước 6: sinh trang HTML wiki-graph — đồ thị quan hệ + timeline ledger cho NGƯỜI xem.

Đọc một wiki dir (frontmatter id/relations + ledger.jsonl + stale.json) → 1 file HTML
self-contained (không request ngoài): node = trang wiki (nhóm theo thư mục), cạnh bezier
tô màu theo kiểu quan hệ, cờ stale/tombstone, timeline sự kiện ledger, click node xem chi tiết.

Tiêu chí tốc độ: chỉ đọc 4KB đầu mỗi file (frontmatter), sinh 1 lần, JS đo toạ độ runtime.

Usage: python3 fdk/tools/build-wiki-graph.py <wiki_dir> [-o out.html]
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

CONTENT_DIRS = ("concepts", "entities", "sources", "draft", "architecture", "tours")
FRONTMATTER_RE = re.compile(r"^---[ \t]*\n(.*?)\n---", re.DOTALL)
LINE_RE = {k: re.compile(rf"^{k}[ \t]*:[ \t]*(\S.*?)[ \t]*$", re.MULTILINE) for k in ("id", "type", "title")}
REL_RE = re.compile(r"\{[ \t]*rel[ \t]*:[ \t]*([\w-]+)[ \t]*,[ \t]*(to|path)[ \t]*:[ \t]*([^}\s]+)[ \t]*\}")

REL_COLORS = {
    "derives-from": "#30b0c7", "depends-on": "#5856d6", "implements": "#34c759",
    "supersedes": "#ff9500", "touches": "#8e8e93", "contradicts": "#ff2d55",
}
REL_VI = {
    "derives-from": "chưng cất từ (nguồn gốc)", "depends-on": "phụ thuộc vào",
    "implements": "hiện thực (quyết định/ADR)", "supersedes": "thay thế (bản cũ)",
    "touches": "chạm file code", "contradicts": "mâu thuẫn với",
}


def scan(wiki: Path):
    nodes, edges = [], []
    for d in CONTENT_DIRS:
        base = wiki / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            if p.name in {"README.md", "_template.md"}:
                continue
            try:
                head = p.read_text(encoding="utf-8", errors="ignore")[:4096]
            except OSError:
                continue
            m = FRONTMATTER_RE.match(head)
            fm = m.group(1) if m else ""
            get = lambda k: (LINE_RE[k].search(fm).group(1).strip().strip("'\"") if LINE_RE[k].search(fm) else "")
            pid = get("id") or p.stem
            rel_path = p.relative_to(wiki).as_posix()
            nodes.append({"id": pid, "path": rel_path, "group": d,
                          "type": get("type") or "?", "title": get("title")[:90]})
            for rel, kind, tgt in REL_RE.findall(fm):
                edges.append({"from": pid, "rel": rel, "to": tgt, "kind": kind})
    ledger, stale = [], {}
    lp = wiki / "ledger.jsonl"
    if lp.exists():
        for ln in lp.read_text(encoding="utf-8").splitlines()[-300:]:
            try:
                ledger.append(json.loads(ln))
            except ValueError:
                pass
    sp = wiki / "stale.json"
    if sp.exists():
        try:
            stale = json.loads(sp.read_text(encoding="utf-8"))
        except ValueError:
            pass
    return nodes, edges, ledger, stale


def build_html(wiki_name: str, out_abs: str, nodes, edges, ledger, stale) -> str:
    data = json.dumps({"nodes": nodes, "edges": edges, "ledger": ledger[::-1], "stale": stale,
                       "relColors": REL_COLORS, "relVi": REL_VI}, ensure_ascii=False)
    n_stale = len(stale)
    legend = " · ".join(f'<span style="color:{c}">■</span> {r} — {REL_VI[r]}' for r, c in REL_COLORS.items())
    return f"""<!DOCTYPE html>
<html lang="vi"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>wiki-graph — {wiki_name}</title>
<meta name="description" content="Đồ thị quan hệ + timeline ledger của wiki {wiki_name} (wiki-core v2).">
<meta name="theme-color" content="#eaf2fd">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%230a84ff'/%3E%3C/svg%3E">
<style>
:root{{--ink:#0f0f12;--ink2:#4a4a55;--border:rgba(30,90,170,.14);--g2:rgba(255,255,255,.7)}}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{background:#e9f0fb}}
body{{font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Helvetica Neue','Roboto','Segoe UI',sans-serif;
color:var(--ink);line-height:1.55;padding:28px 24px 60px;
background:radial-gradient(900px 500px at 12% -10%,rgba(10,132,255,.10),transparent 60%),
radial-gradient(700px 420px at 95% 15%,rgba(90,162,232,.08),transparent 55%),
linear-gradient(180deg,#f7fbff 0%,#eaf2fd 100%)}}
h1{{font-size:clamp(22px,3.4vw,32px);letter-spacing:-.02em;
background:linear-gradient(135deg,#0a84ff,#5aa2e8,#cfe3fb);-webkit-background-clip:text;background-clip:text;color:transparent}}
.sub{{color:var(--ink2);font-size:13px;margin:6px 0 18px}}
.wrap{{max-width:1200px;margin:0 auto}}
.panel{{background:var(--g2);backdrop-filter:blur(8px) saturate(1.1);border:1px solid var(--border);
border-radius:16px;box-shadow:inset 0 1px 0 rgba(255,255,255,.85),0 4px 20px rgba(20,40,90,.08);
padding:18px;margin-bottom:18px}}
.panel h2{{font-size:15px;color:#1d1d1f;margin-bottom:10px}}
.legend{{font-size:11.5px;color:var(--ink2);margin-bottom:10px}}
#graph{{position:relative;overflow-x:auto;min-height:200px}}
#gcanvas{{position:relative;width:max-content;min-width:100%}}
#glinks{{position:absolute;inset:0;pointer-events:none;overflow:visible;z-index:0}}
#glinks path{{fill:none;stroke-width:1.8;opacity:.55;stroke-linecap:round}}
.cols{{display:flex;gap:56px;position:relative;z-index:1}}
.col{{display:flex;flex-direction:column;gap:7px;min-width:210px}}
.col h3{{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink2);margin-bottom:3px}}
.node{{position:relative;padding:6px 11px;border-radius:11px;background:rgba(255,255,255,.78);
border:1px solid var(--border);box-shadow:inset 0 1px 0 rgba(255,255,255,.85),0 2px 10px rgba(20,40,90,.06);
font-size:12px;cursor:pointer;white-space:nowrap;max-width:280px;overflow:hidden;text-overflow:ellipsis}}
.node:hover{{border-color:#0a84ff}}
.node.sel{{border-color:#0a84ff;background:rgba(10,132,255,.08)}}
.node .flag{{font-size:9.5px;font-weight:700;border-radius:999px;padding:0 6px;margin-left:5px}}
.node .stale{{background:rgba(255,149,0,.15);color:#f08c00}}
.node .tomb{{background:rgba(0,0,0,.08);color:#4a4a55}}
#detail{{font-size:12.5px;color:var(--ink2);min-height:40px}}
#detail b{{color:var(--ink)}}
table{{width:100%;border-collapse:collapse;font-size:12px;font-variant-numeric:tabular-nums}}
th,td{{text-align:left;padding:6px 10px;border-bottom:1px solid rgba(30,90,170,.09)}}
th{{font-size:10.5px;text-transform:uppercase;letter-spacing:.05em;color:var(--ink2)}}
.act-add{{color:#28a745}}.act-modify{{color:#0a84ff}}.act-delete{{color:#e0264b}}
footer{{text-align:center;font-size:11.5px;color:var(--ink2);margin-top:24px}}
code{{font-family:'SF Mono',ui-monospace,Menlo,monospace;font-size:.92em;background:rgba(10,132,255,.07);
border:1px solid rgba(10,132,255,.10);border-radius:5px;padding:1px 5px}}
:focus-visible{{outline:2px solid #0a84ff;outline-offset:2px}}
@media(prefers-reduced-motion:reduce){{*{{transition:none!important;animation:none!important}}}}
</style></head><body><div class="wrap">
<h1>wiki-graph — {wiki_name}</h1>
<p class="sub">{len(nodes)} trang · {len(edges)} quan hệ có kiểu · {n_stale} trang stale (lỗi thời — trang nó phụ thuộc vừa bị sửa/xóa) · {len(ledger)} sự kiện ledger (sổ cái — nhật ký máy ghi mỗi lần wiki thay đổi)</p>
<div class="panel"><h2>Đồ thị quan hệ (click node xem chi tiết)</h2>
<div class="legend">{legend} · <span style="color:#f08c00">■</span> badge S = stale · badge T = tombstone (bia mộ — trang bị "xóa" nhưng giữ lại làm dấu vết)</div>
<div id="graph"><div id="gcanvas"><svg id="glinks"></svg><div class="cols" id="cols"></div></div></div>
<div id="detail">Chọn một node để xem quan hệ vào/ra + sự kiện ledger của trang đó.</div></div>
<div class="panel"><h2>Timeline ledger (mới nhất trước)</h2>
<table><thead><tr><th>Thời điểm</th><th>Phiên</th><th>Hành động</th><th>Trang</th></tr></thead><tbody id="tl"></tbody></table></div>
<footer>wiki-core v2 · sinh bởi <code>fdk/tools/build-wiki-graph.py</code><br>
<code>{out_abs}</code></footer></div>
<script type="application/json" id="data">{data}</script>
<script>
(function(){{
var D=JSON.parse(document.getElementById('data').textContent);
var byId={{}}; D.nodes.forEach(function(n){{byId[n.id]=n}});
var stalePaths=D.stale||{{}};
// cột theo group
var groups={{}};
D.nodes.forEach(function(n){{(groups[n.group]=groups[n.group]||[]).push(n)}});
var cols=document.getElementById('cols');
Object.keys(groups).forEach(function(g){{
  var c=document.createElement('div');c.className='col';
  c.innerHTML='<h3>'+g+' ('+groups[g].length+')</h3>';
  groups[g].forEach(function(n){{
    var el=document.createElement('div');el.className='node';el.tabIndex=0;el.dataset.id=n.id;
    var flags='';
    if(stalePaths[n.path])flags+='<span class="flag stale" title="stale — trang nó phụ thuộc vừa đổi">S</span>';
    if(n.type==='tombstone')flags+='<span class="flag tomb" title="tombstone — đã khai tử, giữ dấu vết">T</span>';
    el.innerHTML=n.id+flags; el.title=(n.title||n.path)+' — '+n.path;
    el.addEventListener('click',function(){{select(n)}});
    c.appendChild(el); n._el=el;
  }});
  cols.appendChild(c);
}});
var svg=document.getElementById('glinks'),canvas=document.getElementById('gcanvas');
function draw(hl){{
  var w=canvas.scrollWidth,h=canvas.scrollHeight,cR=canvas.getBoundingClientRect();
  svg.setAttribute('width',w);svg.setAttribute('height',h);svg.setAttribute('viewBox','0 0 '+w+' '+h);
  while(svg.firstChild)svg.removeChild(svg.firstChild);
  D.edges.forEach(function(e){{
    var a=byId[e.from],b=byId[e.to];
    if(!a||!b||!a._el||!b._el)return; // cạnh touches (path code) không vẽ — không phải node wiki
    if(hl&&e.from!==hl&&e.to!==hl)return;
    var ra=a._el.getBoundingClientRect(),rb=b._el.getBoundingClientRect();
    var x1=ra.right-cR.left,y1=ra.top+ra.height/2-cR.top,x2=rb.left-cR.left,y2=rb.top+rb.height/2-cR.top;
    if(x2<x1){{x1=ra.left-cR.left;x2=rb.right-cR.left}}
    var dx=Math.max(24,Math.abs(x2-x1)*0.4);
    var p=document.createElementNS('http://www.w3.org/2000/svg','path');
    p.setAttribute('d','M'+x1+' '+y1+' C'+(x1+dx)+' '+y1+' '+(x2-dx)+' '+y2+' '+x2+' '+y2);
    p.setAttribute('stroke',D.relColors[e.rel]||'#9aa4b2');
    if(hl)p.setAttribute('stroke-width','2.6');
    svg.appendChild(p);
  }});
}}
var selEl=null;
function select(n){{
  if(selEl)selEl.classList.remove('sel'); selEl=n._el; selEl.classList.add('sel');
  var out=D.edges.filter(function(e){{return e.from===n.id}});
  var inn=D.edges.filter(function(e){{return e.to===n.id}});
  var ev=D.ledger.filter(function(l){{return l.target===n.path}}).slice(0,5);
  var st=stalePaths[n.path];
  var html='<b>'+n.id+'</b> <code>'+n.path+'</code> — type: '+n.type;
  if(st)html+=' · <b style="color:#f08c00">STALE</b> (do <code>'+st.by+'</code> '+st.action+' lúc '+st.ts+')';
  html+='<br>→ trỏ đi: '+(out.map(function(e){{return e.rel+' <code>'+e.to+'</code>'}}).join(' · ')||'(không)');
  html+='<br>← được trỏ tới: '+(inn.map(function(e){{return '<code>'+e.from+'</code> '+e.rel}}).join(' · ')||'(không)');
  html+='<br>Sự kiện ledger: '+(ev.map(function(l){{return l.ts+' '+l.action}}).join(' · ')||'(chưa có)');
  document.getElementById('detail').innerHTML=html;
  draw(n.id);
}}
var tl=document.getElementById('tl');
D.ledger.slice(0,120).forEach(function(l){{
  var tr=document.createElement('tr');
  tr.innerHTML='<td>'+(l.ts||'')+'</td><td>'+(l.session||'')+'</td><td class="act-'+l.action+'">'+l.action+'</td><td><code>'+(l.target||'')+'</code></td>';
  tl.appendChild(tr);
}});
draw(null);
addEventListener('resize',function(){{clearTimeout(window.__t);window.__t=setTimeout(function(){{draw(null)}},120)}});
}})();
</script></body></html>"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("wiki_dir")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    t0 = time.perf_counter()
    wiki = Path(a.wiki_dir).resolve()
    if not wiki.is_dir():
        sys.exit(f"khong thay wiki dir: {wiki}")
    name = wiki.parent.name if wiki.name == "wiki" else wiki.name
    out = Path(a.out).resolve() if a.out else Path("llmwiki/html").resolve() / f"wiki-graph-{name}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    nodes, edges, ledger, stale = scan(wiki)
    out.write_text(build_html(name, str(out), nodes, edges, ledger, stale), encoding="utf-8")
    dt = (time.perf_counter() - t0) * 1000
    print(f"✓ {out} — {len(nodes)} node, {len(edges)} canh, {len(ledger)} su kien, {len(stale)} stale ({dt:.0f} ms)")


if __name__ == "__main__":
    main()
