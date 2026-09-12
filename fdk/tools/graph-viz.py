#!/usr/bin/env python3
"""graph-viz — vẽ MỘT graph phân việc (<id>.graph.json của orca-graph.py) thành trang HTML
self-contained theme docs-site-macos (liquid-glass, toggle sáng/tối, full path), layout phân lớp
theo thế hệ topo (Sugiyama-lite, KHÔNG cần graphviz). Tuỳ chọn --png xuất ảnh qua matplotlib.

Usage:
  graph-viz.py <path/to/x.graph.json> [-o out.html] [--png out.png]
Module: graph-atlas.py import lại `layout()`, `svg()`, `page()` từ đây (một nguồn theme, chống drift).
"""
import argparse, html, json, os, sys, time, zlib
from pathlib import Path

# Node = khối {shape+icon theo KIND, viền màu theo STATE, caption id}. IR = nửa cạnh/bán kính
# icon; W,H = hộp bao NGUYÊN NODE (icon + khoảng cách + caption) dùng cho layout cột/hàng;
# ICON_CY = tâm dọc của icon tính từ đỉnh hộp — cạnh/mũi tên nối vào ICON_CY, không phải H/2,
# để dây nối chạm đúng hình chứ không đâm vào khoảng trống có caption.
IR, ICON_CY = 15, 18
W, H, GX, GY = 46, 54, 86, 24
STATE_COLOR = {"proposed": "#94a3b8", "ready": "#0a84ff", "locked": "#a855f7", "dispatched": "#f59e0b",
               "done": "#22c55e", "done_user_reported": "#16a34a", "done_unverified": "#84cc16",
               "failed": "#ef4444", "unknown": "#f97316", "blocked": "#64748b"}
STATE_VI = {"proposed": "đề xuất (chờ deps)", "ready": "sẵn sàng (chạy được ngay)", "locked": "đã khoá (đang giành)",
            "dispatched": "đã giao (agent đang chạy)", "done": "xong — đã verify", "done_user_reported": "xong — người báo tay",
            "done_unverified": "xong — chưa verify", "failed": "hỏng (retry được)", "unknown": "không rõ (hết lease, cần reconcile)",
            "blocked": "chặn — cần người (HITL)"}

# ---------- kind → {icon, shape, color} — bộ mặc định SỐNG trong skill, tái dùng mọi graph ----------
_SKILL_ASSETS = Path(__file__).resolve().parents[2] / "skills" / "orca-graph" / "assets"
KIND_REGISTRY_PATH = _SKILL_ASSETS / "kind-glyphs.json"      # nguồn vĩnh viễn — sửa tay hoặc /raise-issue
KIND_LOCAL_PATH = _SKILL_ASSETS / "kind-glyphs.local.json"   # nơi tạm giữ kind MỚI agent tự sinh
_FALLBACK_REGISTRY = {"build": {"icon": "🔧", "shape": "circle", "color": "#3b82f6"}}  # phòng khi thiếu file


def load_kind_registry() -> dict:
    """Nguồn vĩnh viễn (skills/orca-graph/assets/kind-glyphs.json) + kind mới đã tự sinh trước đó
    (kind-glyphs.local.json) — cùng một `kind` thì file local đè để không sinh lại mỗi lần chạy."""
    reg = dict(_FALLBACK_REGISTRY)
    for p in (KIND_REGISTRY_PATH, KIND_LOCAL_PATH):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            reg.update({k: v for k, v in data.items() if not k.startswith("_")})
        except (OSError, ValueError):
            pass
    return reg


def glyph_for(kind: str, registry: dict, new_kinds: dict) -> dict:
    """Tra {icon,shape,color} cho một kind. Không có trong registry → TỰ SINH tất định (cùng
    kind luôn ra cùng glyph giữa các lần chạy, không cần lưu trạng thái ngẫu nhiên) và ghi vào
    `new_kinds` để render_graph() lưu + báo cho người/agent gọi tool biết mà cân nhắc raise-issue.
    Icon tự sinh là CHỮ CÁI ĐẦU (monogram) — trung thực hơn gán bừa một emoji không liên quan."""
    kind = (kind or "build").strip() or "build"
    if kind in registry:
        return registry[kind]
    h = zlib.crc32(kind.encode("utf-8"))
    g = {"icon": kind[:2].upper(), "shape": "square" if h % 2 else "circle", "color": f"hsl({h % 360} 55% 50%)"}
    new_kinds[kind] = g
    return g


# ---------- layout ----------
def layout(g: dict) -> dict:
    """→ {node_id: (x, y)}; cột = lớp topo, thứ tự trong cột theo trọng tâm deps (giảm cắt dây)."""
    nodes = {n["id"]: n for n in g["nodes"]}
    pos, prev_y = {}, {}
    for li, layer in enumerate(g["layers"]):
        def key(i):
            ys = [prev_y[d] for d in nodes[i]["deps"] if d in prev_y]
            return (sum(ys) / len(ys) if ys else 1e9, i)
        order = sorted(layer, key=key)
        for r, i in enumerate(order):
            pos[i] = (li * (W + GX), r * (H + GY))
            prev_y[i] = r
    return pos


def svg(g: dict, pos: dict, scale: float = 1.0, mini: bool = False, registry: dict = None, new_kinds: dict = None) -> str:
    nodes = {n["id"]: n for n in g["nodes"]}
    registry = load_kind_registry() if registry is None else registry
    new_kinds = {} if new_kinds is None else new_kinds
    maxx = max((x for x, _ in pos.values()), default=0) + W
    maxy = max((y for _, y in pos.values()), default=0) + H
    padl = 12 + (IR + W * 1.6 + 8 if g.get("conflicts") else 0)   # chừa chỗ cho cung xung đột vồng ra trái
    out = [f'<svg class="graph" viewBox="-{padl:.0f} -12 {maxx+padl+12:.0f} {maxy+24}" width="{(maxx+padl+12)*scale:.0f}" height="{(maxy+24)*scale:.0f}" '
           f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Đồ thị phụ thuộc {html.escape(g["id"])}">',
           '<defs><marker id="arw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           '<path d="M0 0L10 5L0 10z" fill="var(--edge)"/></marker></defs>']
    for i, n in nodes.items():
        x1, y1 = pos[i]
        for d in n["deps"]:
            if d not in pos:
                continue
            x0, y0 = pos[d]
            # Nối vào tâm ICON (ICON_CY), không phải tâm nguyên hộp node — hộp giờ CAO hơn icon
            # vì có thêm dòng caption id bên dưới; nối theo H/2 cũ sẽ đâm vào khoảng trống đó.
            ax, ay, bx, by = x0 + W, y0 + ICON_CY, x1, y1 + ICON_CY
            cx = (ax + bx) / 2
            dash = ' stroke-dasharray="6 5"' if n.get("deps_conf") == "gợi-ý" else ""
            out.append(f'<path class="edge" d="M{ax} {ay} C{cx} {ay} {cx} {by} {bx} {by}"{dash} marker-end="url(#arw)" data-e="{d}->{i}"><title>{d} → {i} (phụ thuộc{" — suy luận" if dash else ""})</title></path>')
    for c in g.get("conflicts", []):
        (xa, ya), (xb, yb) = pos[c["a"]], pos[c["b"]]
        # Cung VÒNG RA BÊN TRÁI cột (không đâm xuyên các node nằm giữa a và b); độ vồng theo khoảng cách
        x, y0, y1 = xa + W / 2, ya + ICON_CY, yb + ICON_CY
        bow = min(W * 1.6, 28 + abs(y1 - y0) * 0.22)
        out.append(f'<path class="conflict" d="M{x-IR} {y0} Q{x-IR-bow} {(y0+y1)/2} {x-IR} {y1}"><title>{c["a"]} ∥ {c["b"]} cùng ghi {", ".join(c["files"])}</title></path>')
    for i, n in nodes.items():
        x, y = pos[i]
        cx, cy = x + W / 2, y + ICON_CY
        col = STATE_COLOR.get(n.get("state", "proposed"), "#94a3b8")
        title = html.escape(n["title"])
        gl = glyph_for(n.get("kind", "build"), registry, new_kinds)
        shape = (f'<rect x="{-IR}" y="{-IR}" width="{IR*2}" height="{IR*2}" rx="6" fill="{gl["color"]}" fill-opacity=".28" stroke="{col}" stroke-width="3"/>'
                 if gl.get("shape") == "square" else
                 f'<circle r="{IR}" fill="{gl["color"]}" fill-opacity=".28" stroke="{col}" stroke-width="3"/>')
        # Node = shape+icon theo KIND (việc task LÀM) + viền màu theo STATE + caption id dưới
        # hình. Nội dung đầy đủ (title/state/deps/…) hiện trong thẻ khi bấm — xem NODE_HTML
        # trong render_graph() — không nhồi chữ dài lên đồ thị.
        out.append(f'<g class="node" data-id="{i}" transform="translate({cx},{cy})" tabindex="0">{shape}'
                   f'<text text-anchor="middle" dy="0.34em" class="nicon">{html.escape(gl["icon"])}</text>'
                   f'<text text-anchor="middle" y="{IR+13}" class="nid">{html.escape(i)}</text>'
                   f'<title>{i}: {title} · kind={html.escape(n.get("kind") or "build")}</title></g>')
    out.append("</svg>")
    return "\n".join(out)


# ---------- theme (docs-site-macos) — MỘT danh sách rule dark, emit 2 khối ----------
_DARK_RULES = [
    ("html{PFX}", "--bg:#0c0f16;--glass1:rgba(22,28,40,.55);--glass2:rgba(24,30,44,.72);--glass3:rgba(20,26,38,.9);"
                  "--t1:#e6e9f0;--t2:#a2a9b8;--border:rgba(120,160,230,.16);--edge:#8fb3ff;--accent:#5ea2ff;--orb1:#1a3a6a;--orb2:#2a1a5a"),
    ("html{PFX} body", "background:radial-gradient(1200px 700px at 8% -10%,var(--orb1),transparent 60%),radial-gradient(900px 600px at 100% 100%,var(--orb2),transparent 60%),var(--bg)"),
]


def _dark_css() -> str:
    a = "\n".join(f"{sel.replace('{PFX}', ':not([data-theme=light])')}{{{body}}}" for sel, body in _DARK_RULES)
    b = "\n".join(f"{sel.replace('{PFX}', '[data-theme=dark]')}{{{body}}}" for sel, body in _DARK_RULES)
    return f"@media (prefers-color-scheme: dark){{\n{a}\n}}\n{b}"


CSS = """
:root{--bg:#eaf2fd;--glass1:rgba(255,255,255,.55);--glass2:rgba(255,255,255,.7);--glass3:rgba(255,255,255,.88);
 --t1:#0f0f12;--t2:#4a4a55;--border:rgba(30,90,170,.14);--edge:#3b6fb6;--accent:#0a84ff;--orb1:#bcd6ff;--orb2:#dcc9ff;
 --nav-w:260px;--nav-pad-y:18px;--r:16px}
*{box-sizing:border-box}html{color-scheme:light dark}[hidden]{display:none!important}
body{margin:0;font:13.5px/1.55 -apple-system,BlinkMacSystemFont,"SF Pro Text",Inter,system-ui,sans-serif;color:var(--t1);
 background:radial-gradient(1200px 700px at 8% -10%,var(--orb1),transparent 60%),radial-gradient(900px 600px at 100% 100%,var(--orb2),transparent 60%),var(--bg);
 min-height:100vh;padding-left:var(--nav-w);transition:padding-left .25s}
body.nav-collapsed{padding-left:0}
nav{position:fixed;inset:0 auto 0 0;width:var(--nav-w);display:flex;flex-direction:column;padding:var(--nav-pad-y) 0 var(--nav-pad-y);
 background:linear-gradient(180deg,rgba(255,255,255,.62),rgba(255,255,255,.38) 55%,rgba(255,255,255,.5));backdrop-filter:blur(24px) saturate(1.3);
 border-right:1px solid var(--border);transition:transform .25s;z-index:5;overflow:auto}
nav::before{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(420px 220px at 20% 0%,rgba(255,255,255,.55),transparent 70%),linear-gradient(115deg,transparent 40%,rgba(255,255,255,.18) 50%,transparent 60%)}
html:not([data-theme=light]) nav,html[data-theme=dark] nav{background:linear-gradient(180deg,rgba(30,38,56,.7),rgba(24,30,44,.5) 55%,rgba(30,38,56,.62))}
@media (prefers-color-scheme: light){html:not([data-theme=dark]) nav{background:linear-gradient(180deg,rgba(255,255,255,.62),rgba(255,255,255,.38) 55%,rgba(255,255,255,.5))}}
body.nav-collapsed nav{transform:translateX(-100%)}
nav .brand{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--t2);padding:0 18px 10px}
nav a{display:block;padding:7px 18px;font-size:12px;color:var(--t1);text-decoration:none;border-left:2px solid transparent}
nav a:hover{background:var(--glass1);border-left-color:var(--accent)}
nav .grp{font-size:10.5px;color:var(--t2);padding:12px 18px 4px;text-transform:uppercase;letter-spacing:.06em}
.nav-close{position:absolute;top:10px;right:10px;width:26px;height:26px;border:0;border-radius:8px;background:var(--glass1);color:var(--t2);cursor:pointer}
.nav-toggle{position:fixed;top:12px;left:12px;width:32px;height:32px;border:1px solid var(--border);border-radius:10px;background:var(--glass1);backdrop-filter:blur(14px);cursor:pointer;z-index:6;transition:opacity .2s}
body:not(.nav-collapsed) .nav-toggle{opacity:0;pointer-events:none}
.theme-row{position:sticky;bottom:calc(-1 * var(--nav-pad-y));margin-top:auto;display:flex;align-items:center;justify-content:space-between;padding:11px 16px;
 border-top:1px solid var(--border);background:var(--glass1);backdrop-filter:blur(14px);font-size:12px;color:var(--t2)}
.theme-switch{cursor:pointer}.theme-switch .track{display:inline-block;position:relative;width:50px;height:26px;border-radius:999px;background:#cfe0fa;border:1px solid var(--border);font-size:11px;line-height:26px}
.theme-switch .track::before{content:'☀️';position:absolute;left:6px}.theme-switch .track::after{content:'🌙';position:absolute;right:6px}
.theme-switch .knob{position:absolute;top:2px;left:2px;width:20px;height:20px;border-radius:50%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.25);transition:left .18s;z-index:1}
.theme-switch.on .knob{left:26px}.theme-switch.on .track{background:#2b3a5c}
main{max-width:1180px;margin:0 auto;padding:28px 28px 60px}
h1{font-size:22px;margin:6px 0 4px;letter-spacing:-.01em}h2{font-size:15px;margin:30px 0 10px}.sub{color:var(--t2);font-size:12.5px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}.chip{padding:4px 10px;border-radius:999px;font-size:11px;background:var(--glass2);border:1px solid var(--border)}
.chip b{color:var(--accent)}
.card,.diagram-box{background:var(--glass2);backdrop-filter:blur(18px) saturate(1.1);border:1px solid var(--border);border-radius:var(--r);
 box-shadow:inset 0 1px 0 rgba(255,255,255,.55),0 8px 30px rgba(20,60,120,.08);padding:14px 16px}
.diagram-box{padding:0;overflow:hidden;position:relative;height:min(62vh,560px)}
.diagram-box .pan{position:absolute;inset:0;cursor:grab}.diagram-box .pan:active{cursor:grabbing}
.diagram-box svg{position:absolute;left:0;top:0;transform-origin:0 0;will-change:transform}
.diagram-box .tools{position:absolute;right:10px;top:10px;display:flex;gap:6px;z-index:2}
.diagram-box .tools button{width:28px;height:28px;border:1px solid var(--border);border-radius:8px;background:var(--glass1);backdrop-filter:blur(12px);color:var(--t1);cursor:pointer;font-size:13px}
svg .edge{fill:none;stroke:var(--edge);stroke-width:1.6;opacity:.85}svg .conflict{fill:none;stroke:#ef4444;stroke-width:1.6;stroke-dasharray:4 4;opacity:.85}
svg .node:focus{outline:none}svg .node:focus-visible circle,svg .node:focus-visible rect{stroke-width:4}
svg .node{cursor:pointer}svg .node :first-child{transition:filter .15s}svg .node:hover :first-child,svg .node:focus :first-child{filter:brightness(1.15);stroke-width:4}
svg .node.dim{opacity:.22}svg .edge.dim{opacity:.1}svg .edge.hot{stroke-width:2.6;opacity:1}
svg text{fill:var(--t1);font-family:inherit;pointer-events:none}svg .nid{font-size:10px;font-weight:600}svg .nicon{font-size:15px}
svg .st{font-weight:400;fill:var(--t2);font-size:10.5px}svg .ttl{font-size:11.5px}svg .meta{font-size:10px;fill:var(--t2)}
#node-inspector{margin-top:12px;min-height:44px}#node-inspector .placeholder{margin:0;font-style:italic}
.legend{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:11px;color:var(--t2);margin:10px 2px}.legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:-1px}
table{width:100%;border-collapse:collapse;font-size:12.5px;background:var(--glass3);backdrop-filter:blur(20px);border:1px solid var(--border);border-radius:var(--r);overflow:hidden}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--border);vertical-align:top}th{font-size:10.5px;text-transform:uppercase;letter-spacing:.05em;color:var(--t2)}
tr:last-child td{border-bottom:0}code,.path{font:11.5px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--glass1);padding:1px 5px;border-radius:5px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}.node-card{scroll-margin-top:20px}.node-card h3{margin:0 0 4px;font-size:13px}
.node-card .st{font-size:10.5px;padding:2px 8px;border-radius:999px;color:#fff;margin-left:6px;vertical-align:1px}
.node-card ul{margin:6px 0 0;padding-left:16px;font-size:12px;color:var(--t2)}.node-card li b{color:var(--t1)}
.gloss dt{font-weight:600;font-size:12.5px;margin-top:8px}.gloss dd{margin:2px 0 0;font-size:12px;color:var(--t2)}
footer{margin-top:40px;color:var(--t2);font-size:11px}footer .path{display:inline-block;margin-top:6px;user-select:all}
.badge{display:inline-block;padding:1px 7px;border-radius:999px;font-size:10.5px;border:1px solid var(--border);background:var(--glass1)}
@media (max-width:640px){body{padding-left:0}main{padding:18px 14px}}
""" + _dark_css()

JS = r"""
(function(){var b=document.body;var nav=document.querySelector('nav');if(!nav)return;
var x=document.createElement('button');x.className='nav-close';x.textContent='✕';x.title='Đóng thanh bên';nav.appendChild(x);
var t=document.createElement('button');t.className='nav-toggle';t.textContent='☰';t.title='Mở thanh bên';b.appendChild(t);
function set(c){b.classList.toggle('nav-collapsed',c);try{localStorage.setItem('navCollapsed',c?'1':'0')}catch(e){}}
x.onclick=function(){set(true)};t.onclick=function(){set(false)};
try{var s=localStorage.getItem('navCollapsed');set(s===null?matchMedia('(max-width:640px)').matches:s==='1')}catch(e){}})();
(function(){var K='PAGEKEY-theme',d=document.documentElement,nav=document.querySelector('nav');if(!nav)return;
function isDark(){var t=d.getAttribute('data-theme');return t?t==='dark':matchMedia('(prefers-color-scheme: dark)').matches}
var sw=document.createElement('div');sw.className='theme-switch';sw.setAttribute('role','switch');sw.setAttribute('tabindex','0');
sw.innerHTML='<span class="track"><span class="knob"></span></span>';
var row=document.createElement('div');row.className='theme-row';var lb=document.createElement('span');lb.textContent='Giao diện';row.appendChild(lb);row.appendChild(sw);nav.appendChild(row);
function paint(){var dk=isDark();sw.classList.toggle('on',dk);sw.setAttribute('aria-checked',dk?'true':'false');sw.setAttribute('aria-label',dk?'Đang tối — gạt sang sáng':'Đang sáng — gạt sang tối')}
function flip(){var n=isDark()?'light':'dark';d.setAttribute('data-theme',n);try{localStorage.setItem(K,n)}catch(e){}paint()}
sw.addEventListener('click',flip);sw.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();flip()}});paint()})();
/* pan/zoom + highlight chuỗi phụ thuộc khi hover/click node */
document.querySelectorAll('.diagram-box').forEach(function(box){var svg=box.querySelector('svg');if(!svg)return;var pan=box.querySelector('.pan')||box;
var s=1,tx=16,ty=16,drag=null;function ap(){svg.style.transform='translate('+tx+'px,'+ty+'px) scale('+s+')'}
function fit(){var r=box.getBoundingClientRect(),w=svg.width.baseVal.value,h=svg.height.baseVal.value;s=Math.min((r.width-32)/w,(r.height-32)/h,1.4);tx=(r.width-w*s)/2;ty=(r.height-h*s)/2;ap()}
pan.addEventListener('wheel',function(e){e.preventDefault();var k=e.deltaY<0?1.1:0.9;var r=box.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top;tx=mx-(mx-tx)*k;ty=my-(my-ty)*k;s*=k;ap()},{passive:false});
pan.addEventListener('mousedown',function(e){drag={x:e.clientX-tx,y:e.clientY-ty}});window.addEventListener('mousemove',function(e){if(drag){tx=e.clientX-drag.x;ty=e.clientY-drag.y;ap()}});window.addEventListener('mouseup',function(){drag=null});
box.querySelectorAll('.tools [data-z]').forEach(function(bt){bt.onclick=function(){var z=bt.dataset.z;if(z==='fit')return fit();var k=z==='+'?1.2:0.83;var r=box.getBoundingClientRect();tx=r.width/2-(r.width/2-tx)*k;ty=r.height/2-(r.height/2-ty)*k;s*=k;ap()}});
var edges=[].slice.call(svg.querySelectorAll('.edge')),nodes=[].slice.call(svg.querySelectorAll('.node'));
function chain(id,dir,acc){edges.forEach(function(e){var p=e.dataset.e.split('->');if(dir==='up'&&p[1]===id&&acc.indexOf(p[0])<0){acc.push(p[0]);chain(p[0],'up',acc)}if(dir==='down'&&p[0]===id&&acc.indexOf(p[1])<0){acc.push(p[1]);chain(p[1],'down',acc)}});return acc}
function hl(id){if(!id){nodes.forEach(function(n){n.classList.remove('dim')});edges.forEach(function(e){e.classList.remove('dim','hot')});return}
var keep=chain(id,'up',[id]);keep=chain(id,'down',keep);nodes.forEach(function(n){n.classList.toggle('dim',keep.indexOf(n.dataset.id)<0)});
edges.forEach(function(e){var p=e.dataset.e.split('->');var on=keep.indexOf(p[0])>=0&&keep.indexOf(p[1])>=0;e.classList.toggle('dim',!on);e.classList.toggle('hot',on)})}
var pinned=null,insp=document.getElementById('node-inspector'),dataEl=document.getElementById('node-html-data');
var NODE_HTML=dataEl?JSON.parse(dataEl.textContent):{};
function showCard(id){if(!insp)return;insp.innerHTML=NODE_HTML[id]||'';insp.classList.toggle('empty',!id)}
var pph=insp&&insp.querySelector('.placeholder')?insp.innerHTML:'';
nodes.forEach(function(n){n.addEventListener('mouseenter',function(){if(!pinned)hl(n.dataset.id)});n.addEventListener('mouseleave',function(){if(!pinned)hl(null)});
n.addEventListener('click',function(){var id=n.dataset.id;pinned=pinned===id?null:id;hl(pinned);showCard(pinned||'')})});
if(insp&&!pinned)insp.innerHTML=pph;
fit();window.addEventListener('resize',fit)});
/* Lưới đầy đủ — ẨN mặc định, chỉ bung khi bấm nút hoặc bấm link node ở thanh bên. */
(function(){var btn=document.getElementById('toggle-grid-btn'),grid=document.getElementById('node-grid');if(!btn||!grid)return;
function label(){btn.textContent=grid.hidden?'Xem dạng lưới đầy đủ ▾':'Ẩn dạng lưới đầy đủ ▴'}
btn.onclick=function(){grid.hidden=!grid.hidden;label()};label();
document.querySelectorAll('nav a[href^="#n-"]').forEach(function(a){a.addEventListener('click',function(){grid.hidden=false;label()})})})();
"""


def page(title: str, nav_html: str, main_html: str, out: Path, pagekey: str, desc: str = "") -> None:
    doc = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc or title)}"><meta name="theme-color" content="#eaf2fd">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%230a84ff'/%3E%3C/svg%3E">
<script>(function(){{try{{var t=localStorage.getItem("{pagekey}-theme");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}}})();</script>
<style>{CSS}</style></head><body>
<nav>{nav_html}</nav>
<main>{main_html}
<footer>Sinh bởi <code>fdk/tools/{Path(__file__).name}</code> · {time.strftime("%Y-%m-%d %H:%M")} · file này nằm tại:<br><code class="path">{html.escape(str(out.resolve()))}</code></footer>
</main><script>{JS.replace("PAGEKEY", pagekey)}</script></body></html>"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")


# ---------- trang 1 graph ----------
def legend_html() -> str:
    return '<div class="legend">' + "".join(f'<span><i style="background:{c}"></i>{html.escape(STATE_VI[s])}</span>' for s, c in STATE_COLOR.items()) + \
           '<span><i style="background:transparent;border-top:2px dashed var(--edge);height:0"></i>dây đứt = phụ thuộc SUY LUẬN (chưa khai Depends)</span>' \
           '<span><i style="background:transparent;border-top:2px dashed #ef4444;height:0"></i>đỏ = 2 node song song ghi cùng file</span></div>'


def kind_legend_html(nodes: dict, registry: dict, new_kinds: dict) -> str:
    """Chú giải icon/shape — chỉ liệt các kind THẬT SỰ có trong graph này, không lặp 16 mục mặc định."""
    seen = sorted({n.get("kind") or "build" for n in nodes.values()})
    items = []
    for k in seen:
        gl = registry.get(k) or new_kinds.get(k) or {"icon": "?", "shape": "circle", "color": "#94a3b8"}
        mark = " (mới — chưa có trong sổ mặc định)" if k in new_kinds else ""
        items.append(f'<span><i style="background:{gl["color"]};border-radius:{"3px" if gl.get("shape")=="square" else "50%"}"></i>{gl["icon"]} {html.escape(k)}{mark}</span>')
    return '<div class="legend">' + "".join(items) + '</div>'


def render_graph(gp: Path, out: Path, answers: list, png: str = "") -> None:
    g = json.loads(gp.read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in g["nodes"]}
    pos = layout(g)
    registry = load_kind_registry()
    new_kinds: dict = {}
    st_count = {}
    for n in g["nodes"]:
        st_count[n.get("state", "proposed")] = st_count.get(n.get("state", "proposed"), 0) + 1
    down = {i: [j for j, m in nodes.items() if i in m["deps"]] for i in nodes}

    nav = f'<div class="brand">orca-graph</div><a href="#top">{html.escape(g["id"])}</a><div class="grp">Mục</div>' \
          '<a href="#do-thi">Đồ thị</a><a href="#lop">Lớp song song</a><a href="#node">Từng node</a><a href="#lien-he">Liên hệ graph cũ</a>' \
          '<a href="#tra-loi">Câu trả lời & audit</a><a href="#thuat-ngu">Thuật ngữ</a><div class="grp">Node</div>' + \
          "".join(f'<a href="#n-{i}">{i} · {html.escape(n["title"][:24])}</a>' for i, n in nodes.items())

    chips = "".join(f'<span class="chip"><b>{v}</b> {html.escape(STATE_VI[k])}</span>' for k, v in st_count.items())
    layers_rows = "".join(
        f'<tr><td><b>L{li}</b></td><td>{" ∥ ".join(f"<code>{i}</code>" for i in layer)}</td>'
        f'<td>{"⚠ " + ", ".join(f"{c[chr(97)]}∥{c[chr(98)]}" for c in g.get("conflicts", []) if {c["a"], c["b"]} <= set(layer)) or "—"}</td></tr>'
        for li, layer in enumerate(g["layers"]))
    # Nội dung MỘT node — dùng chung cho (a) thẻ hiện khi bấm vào hình tròn trên đồ thị và
    # (b) ô trong lưới đầy đủ (ẩn mặc định, bật bằng nút) — một nguồn, không lặp lại HTML.
    card_body = {}
    for i, n in nodes.items():
        col = STATE_COLOR.get(n.get("state", "proposed"))
        card_body[i] = f'''<h3>{i} — {html.escape(n["title"])}<span class="st" style="background:{col}">{html.escape(STATE_VI.get(n.get("state",""), ""))}</span></h3>
<ul><li><b>Cần xong trước</b> (deps): {", ".join(f"<code>{d}</code>" for d in n["deps"]) or "— (gốc)"} <span class="badge">{n.get("deps_conf","")}</span></li>
<li><b>Mở khoá cho</b>: {", ".join(f"<code>{d}</code>" for d in down[i]) or "— (lá)"}</li>
<li><b>Kiểu / chế độ</b>: {n.get("kind","")} / {"cần người (HITL)" if n.get("mode")=="hitl" else "agent tự chạy (AFK)"}</li>
<li><b>File chạm</b>: {", ".join(f"<code>{html.escape(f)}</code>" for f in n.get("files", [])) or "—"}</li>
<li><b>Làm ra</b>: {html.escape("; ".join(n.get("produces", []))[:220]) or "—"}</li>
<li><b>Verify</b>: {f"<code>{html.escape(n['verify'])}</code>" if n.get("verify") else "— (không có → tối đa done_unverified)"}</li>
<li><b>Runtime</b>: gen {n.get("gen",0)} · rev {n.get("rev",0)} · attempt {n.get("attempts",0)} · {"còn tươi" if n.get("fresh")=="current" else "STALE — upstream đã làm lại"}</li></ul>'''
    cards = "".join(f'<div class="card node-card" id="n-{i}">{body}</div>' for i, body in card_body.items())
    node_html_json = json.dumps(card_body, ensure_ascii=False).replace("</", "<\\/")
    links = g.get("links", [])
    links_rows = "".join(f'<tr><td><code>{html.escape(l["to_graph"])}</code></td><td><code>{l["to_node"]}</code></td><td>{", ".join(f"<code>{html.escape(v)}</code>" for v in l["via"])}</td><td>{l["kind"]}</td></tr>' for l in links) \
        or '<tr><td colspan="4">Không khớp artifact với graph cũ nào. Liên hệ ngữ nghĩa (nếu có) do model trả lời và phải gắn nhãn + nguồn — xem mục Câu trả lời.</td></tr>'
    ans_rows = "".join(
        f'<tr><td>{html.escape(a["q"])}</td><td>{a.get("node") or "-"}</td><td><span class="badge">{html.escape(a["label"])}</span></td><td>{a["self_score"]}</td>'
        f'<td>{"<br>".join(f"<code>{html.escape(e)}</code>" for e in a["evidence"]) or "—"}</td><td>{html.escape(a["text"][:160])}</td></tr>' for a in answers) \
        or '<tr><td colspan="6">Chưa có câu trả lời nào được ghi (<code>orca-graph.py answer …</code>).</td></tr>'

    main = f'''<a id="top"></a><h1>{html.escape(g["id"])}</h1><div class="sub">PLAN nguồn: <code>{html.escape(g.get("plan",""))}</code> · dựng lúc {html.escape(g.get("built",""))} · {len(nodes)} node · {len(g["layers"])} lớp</div>
<div class="chips">{chips}<span class="chip"><b>{len(g.get("conflicts",[]))}</b> xung đột ghi cùng file</span><span class="chip"><b>{len(links)}</b> liên hệ graph cũ</span></div>
<h2 id="do-thi">Đồ thị phụ thuộc</h2><div class="sub">Trái → phải là thứ tự bắt buộc; các vòng tròn cùng một cột chạy song song được. Mỗi vòng tròn là một node — bấm vào để xem nội dung ở thẻ bên dưới. Hover để sáng chuỗi phụ thuộc. Lăn chuột để zoom, kéo để pan.</div>
<div class="diagram-box"><div class="tools"><button data-z="+" title="Phóng to">+</button><button data-z="-" title="Thu nhỏ">−</button><button data-z="fit" title="Vừa khung">⤢</button></div><div class="pan">{svg(g, pos, registry=registry, new_kinds=new_kinds)}</div></div>
<div class="card node-card" id="node-inspector"><p class="sub placeholder">Bấm vào một vòng tròn trong đồ thị để xem nội dung node ở đây.</p></div>
<div class="sub">Icon/hình = <b>kind</b> (việc task làm) · viền màu = <b>state</b> (đang ở đâu trong vòng đời).</div>
{kind_legend_html(nodes, registry, new_kinds)}
{legend_html()}
<h2 id="lop">Lớp song song (topo layers)</h2><table><tr><th>Lớp</th><th>Node chạy song song</th><th>Xung đột</th></tr>{layers_rows}</table>
<h2 id="node">Từng node — cần gì, mở khoá gì, xong thì ra sao</h2>
<button type="button" id="toggle-grid-btn" class="chip" style="cursor:pointer">Xem dạng lưới đầy đủ ▾</button>
<div class="grid" id="node-grid" hidden>{cards}</div>
<script id="node-html-data" type="application/json">{node_html_json}</script>
<h2 id="lien-he">Liên hệ với graph cũ (khớp artifact, tất định)</h2><table><tr><th>Graph</th><th>Node</th><th>Qua file</th><th>Kiểu</th></tr>{links_rows}</table>
<h2 id="tra-loi">Câu trả lời của model & tự chấm</h2><div class="sub">Rubric: đúng 1 · sai 0 · không-biết 0.3 · gợi-ý có nguồn thật 0.5 · <b>bịa nguồn 0</b>. Điểm sau audit xem <code>orca-graph.py audit</code>.</div>
<table><tr><th>Câu hỏi</th><th>Node</th><th>Nhãn</th><th>Tự chấm</th><th>Nguồn</th><th>Trả lời</th></tr>{ans_rows}</table>
<h2 id="thuat-ngu">Thuật ngữ</h2><dl class="gloss card">
<dt>deps (phụ thuộc)</dt><dd>Node phải XONG trước thì node này mới được chạy. Dây đứt = tool suy ra từ Consumes/Produces, chưa ai khai tường minh.</dd>
<dt>lớp topo (topological layer)</dt><dd>Nhóm node không phụ thuộc nhau → chạy song song được. Lớp sau chỉ mở khi lớp trước xong.</dd>
<dt>lease (thuê khoá)</dt><dd>Khoá có hạn giờ. Hết hạn mà chưa báo xong → node về <i>unknown</i> (không rõ), không tự kết luận hỏng.</dd>
<dt>generation (thế hệ giao việc)</dt><dd>Mỗi lần giao lại tăng 1. Kết quả mang gen cũ bị bỏ, tránh agent chết-sống-lại ghi đè lần giao mới.</dd>
<dt>verify</dt><dd>Lệnh shell trả 0 = task xong thật. Không có verify thì tối đa chỉ đạt <i>done_unverified</i> (xong nhưng chưa ai kiểm).</dd>
<dt>stale (cũ)</dt><dd>Node đã xong nhưng node nó phụ thuộc bị làm lại → kết quả có thể lệch; chỉ cảnh báo, không tự lùi trạng thái.</dd>
<dt>HITL / AFK</dt><dd>HITL = cần người sống quyết định, không giao cho agent headless. AFK = agent tự chạy được.</dd></dl>'''
    page(f"Graph phân việc · {g['id']}", nav, main, out, pagekey=f"orca-graph-{g['id']}", desc=f"Đồ thị phụ thuộc {len(nodes)} node của PLAN {g.get('plan','')}")
    print(f"→ {out}")
    if new_kinds:
        # kind lạ → đã tự sinh icon/shape/color TẠM (xem glyph_for), lưu vào file LOCAL để lần
        # sau chạy lại cùng graph không sinh khác đi. Đây là chỗ "bơm ngữ cảnh": in rõ để AGENT
        # đang gọi tool này đọc được và hỏi user có muốn /raise-issue nộp glyph lên sổ mặc định
        # (kind-glyphs.json) hay không — script không tự quyết, chỉ nêu sự kiện.
        local = {}
        try:
            local = json.loads(KIND_LOCAL_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
        local.update(new_kinds)
        KIND_LOCAL_PATH.parent.mkdir(parents=True, exist_ok=True)
        KIND_LOCAL_PATH.write_text(json.dumps(local, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"⚠ {len(new_kinds)} kind CHƯA có trong sổ mặc định ({KIND_REGISTRY_PATH}) — đã tự sinh tạm, lưu ở {KIND_LOCAL_PATH}:", file=sys.stderr)
        for k, gl in new_kinds.items():
            print(f"    kind={k!r} → icon={gl['icon']!r} shape={gl['shape']} color={gl['color']}", file=sys.stderr)
        print("  Muốn glyph này dùng chung mọi graph/mọi project? Hỏi user có raise-issue để submit vào "
              f"{KIND_REGISTRY_PATH.relative_to(KIND_REGISTRY_PATH.parents[3])} không (dùng skill /raise-issue).", file=sys.stderr)
    if png:
        render_png(g, pos, Path(png))


def render_png(g: dict, pos: dict, out: Path) -> None:
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    except ImportError:
        print("matplotlib không có → bỏ qua --png", file=sys.stderr); return
    nodes = {n["id"]: n for n in g["nodes"]}
    fig, ax = plt.subplots(figsize=(max(6, (max(x for x, _ in pos.values()) + W) / 90), max(3, (max(y for _, y in pos.values()) + H) / 90)))
    for i, n in nodes.items():
        x, y = pos[i]
        for d in n["deps"]:
            x0, y0 = pos[d]
            ax.add_patch(FancyArrowPatch((x0 + W, -(y0 + H / 2)), (x, -(y + H / 2)), arrowstyle="->", mutation_scale=10, color="#3b6fb6",
                                         connectionstyle="arc3,rad=0.15", ls="--" if n.get("deps_conf") == "gợi-ý" else "-"))
    for i, n in nodes.items():
        x, y = pos[i]
        ax.add_patch(FancyBboxPatch((x, -(y + H)), W, H, boxstyle="round,pad=2,rounding_size=10", fc="white", ec=STATE_COLOR.get(n.get("state"), "#999"), lw=2))
        ax.text(x + 10, -(y + 22), f"{i} · {n.get('state')}", fontsize=8, weight="bold")
        ax.text(x + 10, -(y + 44), n["title"][:34], fontsize=7)
    ax.set_xlim(-10, max(x for x, _ in pos.values()) + W + 10); ax.set_ylim(-(max(y for _, y in pos.values()) + H + 10), 10); ax.axis("off")
    fig.tight_layout(); fig.savefig(out, dpi=160); print(f"→ {out}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("graph"); ap.add_argument("-o", "--out"); ap.add_argument("--png", default="")
    a = ap.parse_args(argv)
    gp = Path(a.graph)
    gid = gp.name.replace(".graph.json", "")
    ans_p = gp.with_name(f"{gid}.answers.jsonl")
    answers = [json.loads(l) for l in ans_p.read_text(encoding="utf-8").splitlines() if l.strip()] if ans_p.exists() else []
    out = Path(a.out) if a.out else gp.with_name(f"{gid}.graph.html")
    render_graph(gp, out, answers, a.png)


if __name__ == "__main__":
    main()
