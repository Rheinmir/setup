#!/usr/bin/env python3
"""graph-atlas — bản đồ 2D KHỔNG LỒ mọi graph phân việc trong một thư mục (<id>.graph.json).
Mỗi graph là một ô kính có sơ đồ mini; trục X = thời gian dựng graph, trục Y = cụm liên hệ
(connected component theo `links` — graph nào chạm cùng file thì cùng hàng). Dây nối giữa các ô =
`links` sang graph cũ. Pan/zoom toàn bản đồ. Theme dùng lại từ graph-viz.py (một nguồn, chống drift).

Usage: graph-atlas.py <dir> [-o out.html]
"""
import argparse, html, importlib.util, json, sys, time
from pathlib import Path

_spec = importlib.util.spec_from_file_location("graph_viz", Path(__file__).with_name("graph-viz.py"))
viz = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(viz)

TILE_W, TILE_H, TGX, TGY = 420, 300, 70, 60
MINI_SCALE = 0.42


def components(graphs: list) -> dict:
    """→ {graph_id: cụm}; union-find trên links."""
    parent = {g["id"]: g["id"] for g in graphs}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for g in graphs:
        for l in g.get("links", []):
            if l["to_graph"] in parent:
                parent[find(g["id"])] = find(l["to_graph"])
    roots = sorted({find(g["id"]) for g in graphs})
    return {g["id"]: roots.index(find(g["id"])) for g in graphs}


def build(d: Path, out: Path) -> None:
    graphs = []
    for p in sorted(d.glob("*.graph.json")):
        try:
            graphs.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"bỏ {p.name}: {e}", file=sys.stderr)
    if not graphs:
        raise SystemExit(f"không có *.graph.json trong {d}")
    graphs.sort(key=lambda g: g.get("built", ""))
    comp = components(graphs)
    depth = {g["id"]: g.get("depth", 0) for g in graphs}          # trục Y = cấp chứa (PRD §4): mẹ hàng 0, con hàng 1…
    col = {}
    for g in graphs:                                              # trong hàng sắp theo thời gian dựng
        col[g["id"]] = sum(1 for o in graphs if depth[o["id"]] == depth[g["id"]] and o.get("built", "") < g.get("built", ""))
    global TILE_H
    TILE_H = min(560, max(TILE_H, max((max(y for _, y in viz.layout(g).values()) + viz.H + 24) * MINI_SCALE + 60 for g in graphs)))
    tile_pos = {g["id"]: (col[g["id"]] * (TILE_W + TGX), depth[g["id"]] * (TILE_H + TGY)) for g in graphs}
    cw = (max(col.values()) + 1) * (TILE_W + TGX); ch = (max(depth.values()) + 1) * (TILE_H + TGY)

    tiles, wires = [], []
    for g in graphs:
        x, y = tile_pos[g["id"]]
        pos = viz.layout(g)
        done = sum(1 for n in g["nodes"] if n.get("state") in ("done", "done_user_reported"))
        tiles.append(f'''<div class="tile card" style="left:{x}px;top:{y}px;width:{TILE_W}px;height:{TILE_H}px" data-g="{html.escape(g["id"])}">
<div class="th"><b>{html.escape(g["id"])}</b><span>cấp {depth[g["id"]]} · {len(g["nodes"])} node · {len(g["layers"])} lớp · {done}/{len(g["nodes"])} xong · cụm {comp[g["id"]]}</span>
<a class="open" href="{html.escape(g["id"])}.graph.html" title="Mở trang graph chi tiết">↗</a></div>
<div class="mini">{viz.svg(g, pos, scale=MINI_SCALE, mini=True)}</div></div>''')
        if g.get("parent") and g["parent"]["graph"] in tile_pos:   # dây CHỨA mẹ→con: liền nét, từ đáy mẹ tới đỉnh con
            px, py = tile_pos[g["parent"]["graph"]]
            ax, ay, bx, by = px + TILE_W / 2, py + TILE_H, x + TILE_W / 2, y
            wires.append(f'<path class="wire contain" d="M{ax} {ay} C{ax} {(ay+by)/2} {bx} {(ay+by)/2} {bx} {by}"><title>{html.escape(g["parent"]["graph"])}/{g["parent"]["node"]} chứa {html.escape(g["id"])}</title></path>')
        for l in g.get("links", []):
            if l["to_graph"] in tile_pos:
                x2, y2 = tile_pos[l["to_graph"]]
                ax, ay, bx, by = x + TILE_W / 2, y + TILE_H / 2, x2 + TILE_W / 2, y2 + TILE_H / 2
                wires.append(f'<path class="wire" d="M{ax} {ay} C{(ax+bx)/2} {ay} {(ax+bx)/2} {by} {bx} {by}"><title>{html.escape(g["id"])} → {html.escape(l["to_graph"])}/{l["to_node"]} qua {", ".join(l["via"])}</title></path>')

    link_rows = "".join(f'<tr><td><code>{html.escape(g["id"])}</code></td><td><code>{html.escape(l["to_graph"])}</code>/<code>{l["to_node"]}</code></td><td>{", ".join(f"<code>{html.escape(v)}</code>" for v in l["via"])}</td><td>{l["kind"]}</td></tr>'
                        for g in graphs for l in g.get("links", [])) or '<tr><td colspan="4">Chưa có liên hệ giữa các graph.</td></tr>'
    nav = '<div class="brand">orca-graph · atlas</div><a href="#ban-do">Bản đồ</a><a href="#lien-he">Liên hệ</a><div class="grp">Graph (theo thời gian)</div>' + \
          "".join(f'<a href="{html.escape(g["id"])}.graph.html">{html.escape(g["id"])}</a>' for g in graphs)
    main = f'''<h1>Atlas phân việc</h1><div class="sub">{len(graphs)} graph · {max(depth.values())+1} cấp chứa · thư mục <code>{html.escape(str(d.resolve()))}</code>. Hàng = cấp chứa (graph mẹ trên, graph con dưới, dây liền nét); trong hàng sắp theo thời gian dựng; dây đứt = chạm cùng file. Lăn chuột zoom, kéo pan, ↗ mở trang chi tiết.</div>
<h2 id="ban-do">Bản đồ 2D</h2>
<div class="diagram-box atlas"><div class="tools"><button data-z="+">+</button><button data-z="-">−</button><button data-z="fit">⤢</button></div>
<div class="pan"><div class="canvas" style="width:{cw}px;height:{ch}px"><svg class="wires" width="{cw}" height="{ch}" xmlns="http://www.w3.org/2000/svg">{"".join(wires)}</svg>{"".join(tiles)}</div></div></div>
{viz.legend_html()}
<h2 id="lien-he">Liên hệ giữa graph (khớp artifact)</h2><table><tr><th>Graph</th><th>Trỏ tới</th><th>Qua file</th><th>Kiểu</th></tr>{link_rows}</table>'''
    extra_css = """
.atlas{height:min(78vh,760px)}.atlas .canvas{position:absolute;left:0;top:0;transform-origin:0 0}
.tile{position:absolute;padding:0;overflow:hidden}.tile .th{display:flex;align-items:center;gap:10px;padding:8px 12px;border-bottom:1px solid var(--border);font-size:12px}
.tile .th span{color:var(--t2);font-size:10.5px;flex:1}.tile .open{color:var(--accent);text-decoration:none;font-size:14px}
.tile .mini{padding:8px;overflow:hidden}.tile .mini svg{position:static;transform:none}
.wires{position:absolute;left:0;top:0;pointer-events:none}.wires .wire{fill:none;stroke:var(--accent);stroke-width:2;stroke-dasharray:8 6;opacity:.7;pointer-events:stroke}
.wires .wire.contain{stroke:var(--t2);stroke-dasharray:none;stroke-width:2.4;opacity:.8}
"""
    # atlas pan/zoom áp lên .canvas thay cho svg → đổi JS chọn phần tử
    js = viz.JS.replace("var svg=box.querySelector('svg');if(!svg)return;", "var svg=box.querySelector('.canvas')||box.querySelector('svg');if(!svg)return;") \
                .replace("w=svg.width.baseVal.value,h=svg.height.baseVal.value", "w=svg.offsetWidth||svg.width.baseVal.value,h=svg.offsetHeight||svg.height.baseVal.value")
    old_css, old_js = viz.CSS, viz.JS
    viz.CSS, viz.JS = old_css + extra_css, js
    try:
        viz.page("Atlas phân việc · orca-graph", nav, main, out, pagekey="orca-graph-atlas", desc=f"Bản đồ 2D {len(graphs)} graph phân việc")
    finally:
        viz.CSS, viz.JS = old_css, old_js
    print(f"→ {out}  ({len(graphs)} graph, {len(wires)} dây)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir"); ap.add_argument("-o", "--out")
    a = ap.parse_args(argv)
    d = Path(a.dir)
    build(d, Path(a.out) if a.out else d / "atlas.html")


if __name__ == "__main__":
    main()
