#!/usr/bin/env python3
"""build-control-room — trang ĐẦU TIÊN mở ra của framework, data-first: chỉ đọc dữ liệu đã có,
không sinh dữ liệu mới. Bốn khối: (1) node đang chạy toàn máy (registry orca-graph), (2) tiến độ
từng graph + node kẹt, (3) nợ mở từ problem-tree, (4) chi phí hôm nay + khoảng cách tự chấm/audit.
Daemon `orca-graph.py watch` gọi lại file này mỗi khi có graph đổi; trang tự refresh 15 s.

Usage: build-control-room.py [--dirs d1 d2 ...] [-o llmwiki/html/control-room.html]
"""
import argparse, html, importlib.util, json, os, re, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("graph_viz", Path(__file__).with_name("graph-viz.py"))
viz = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(viz)
_ospec = importlib.util.spec_from_file_location("orca_graph", ROOT / "harness/scripts/orca-graph.py")
og = importlib.util.module_from_spec(_ospec); _ospec.loader.exec_module(og)

STUCK = ("unknown", "failed", "blocked")


def read_jsonl(p: Path) -> list:
    if not p.exists():
        return []
    out = []
    for ln in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            out.append(json.loads(ln))
        except ValueError:
            pass
    return out


def graphs_in(dirs: list) -> list:
    out = []
    for d in dirs:
        d = Path(d)
        for p in sorted(d.glob("*.graph.json")):
            try:
                g = og.Store(d, p.name[:-len(".graph.json")]).load(); g["_dir"] = str(d); out.append(g)
            except SystemExit:
                pass
    return out


def block_running(graphs: list, cap: int) -> str:
    rows = []
    for g in graphs:
        st = og.Store(Path(g["_dir"]), g["id"])
        for n in g["nodes"]:
            if n["state"] in ("locked", "dispatched"):
                left = "—"
                try:
                    left = f"{int(json.loads((st.locks_d / n['id']).read_text())['lease_until'] - time.time())} s"
                except (OSError, ValueError, KeyError):
                    pass
                rows.append(f'<tr><td><code>{html.escape(g["id"])}</code></td><td><code>{n["id"]}</code></td><td>{html.escape(n["title"][:48])}</td>'
                            f'<td><span class="badge" style="border-color:{viz.STATE_COLOR[n["state"]]}">{html.escape(viz.STATE_VI[n["state"]])}</span></td><td>{left}</td><td>{n.get("gen", 0)}</td></tr>')
    warn = f'<div class="sub" style="color:#ef4444">⚠ {len(rows)} node đang chạy vượt trần toàn máy {cap}</div>' if len(rows) > cap else ""
    body = "".join(rows) or '<tr><td colspan="6">Không có node nào đang chạy.</td></tr>'
    return f'<h2 id="chay">Đang chạy toàn máy <span class="badge">{len(rows)}/{cap}</span></h2>{warn}<table><tr><th>Graph</th><th>Node</th><th>Việc</th><th>State</th><th>Lease còn</th><th>Gen</th></tr>{body}</table>'


def block_progress(graphs: list) -> str:
    rows = []
    for g in graphs:
        n = len(g["nodes"]); done = sum(1 for x in g["nodes"] if x["state"] in og.TERMINAL_OK)
        stuck = [f'<code>{x["id"]}</code> {html.escape(viz.STATE_VI[x["state"]])}' for x in g["nodes"] if x["state"] in STUCK]
        pct = int(100 * done / n) if n else 0
        bar = f'<svg width="160" height="10" role="img" aria-label="{pct}%"><rect width="160" height="10" rx="5" fill="var(--glass1)" stroke="var(--border)"/><rect width="{1.6*pct:.0f}" height="10" rx="5" fill="#22c55e"/></svg>'
        page = Path(g["_dir"]).parent / "html" / "orca-graph" / f"{g['id']}.graph.html"
        link = f'<a href="{html.escape(os.path.relpath(page, ROOT / "llmwiki/html"))}">{html.escape(g["id"])}</a>' if page.exists() else html.escape(g["id"])
        rows.append(f'<tr><td>{link}</td><td>{bar} {done}/{n}</td><td>{g.get("control", "active")} · v{g.get("plan_version", 1)} · cấp {g.get("depth", 0)}</td><td>{", ".join(stuck) or "—"}</td></tr>')
    return f'<h2 id="tien-do">Tiến độ từng graph</h2><table><tr><th>Graph</th><th>Xong</th><th>Control · plan · cấp</th><th>Kẹt (cần người / reconcile)</th></tr>{"".join(rows) or "<tr><td colspan=4>Chưa có graph.</td></tr>"}</table>'


def block_debt() -> str:
    p = ROOT / "llmwiki/html/fdk-problem-tree.html"
    if not p.exists():
        return '<h2 id="no">Nợ mở</h2><div class="sub">Không có problem-tree.</div>'
    m = re.search(r'<script type="application/json" id="tree-data">(.*?)</script>', p.read_text(encoding="utf-8"), re.S)
    nodes = json.loads(m.group(1)) if m else []
    open_ = sorted([x for x in nodes if x.get("status") != "solved"], key=lambda x: x.get("date", ""), reverse=True)[:8]
    rows = "".join(f'<tr><td><code>{x["id"]}</code></td><td>{html.escape(x["title"][:90])}</td><td>{x.get("status")}</td><td>{x.get("date", "")}</td></tr>' for x in open_)
    return f'<h2 id="no">Nợ mở từ problem-tree <span class="badge">{sum(1 for x in nodes if x.get("status") != "solved")} / {len(nodes)}</span></h2><table><tr><th>ID</th><th>Vấn đề</th><th>Status</th><th>Ngày</th></tr>{rows or "<tr><td colspan=4>Không còn nợ mở.</td></tr>"}</table>'


def block_cost(dirs: list) -> str:
    today = time.strftime("%Y-%m-%d")
    toks = read_jsonl(ROOT / "harness/metrics/tokens.jsonl")
    # tokens.jsonl (cost-sync) là tổng theo SESSION, không có ts → lấy các session còn được ghi nhận trong ngày qua mtime file cost-by-session
    tt = toks[-8:]
    tin = sum(int(t.get("in", t.get("input", 0)) or 0) for t in tt); tout = sum(int(t.get("out", t.get("output", 0)) or 0) for t in tt)
    usd = sum(float(t.get("usd", 0) or 0) for t in tt)
    gaps = []
    for d in dirs:
        for a in read_jsonl(Path(d) / "audit-log.jsonl"):
            gaps.append((a.get("ts", ""), a.get("graph", ""), a.get("self", 0), a.get("audit", 0)))
    gaps = sorted(gaps, reverse=True)[:6]
    grows = "".join(f'<tr><td>{html.escape(str(ts)[:16])}</td><td><code>{html.escape(g)}</code></td><td>{s:.1f}</td><td>{a:.1f}</td><td>{s - a:.1f}</td></tr>' for ts, g, s, a in gaps)
    return (f'<h2 id="chi-phi">Chi phí — {len(tt)} session gần nhất (tới {today})</h2><div class="chips"><span class="chip"><b>{len(tt)}</b> session gần nhất</span><span class="chip"><b>{tin:,}</b> input</span><span class="chip"><b>{tout:,}</b> output</span><span class="chip"><b>${usd:,.2f}</b> ước tính (cost-sync)</span></div>'
            f'<h3 style="font-size:13px;margin:14px 0 6px">Model tự chấm vs audit (khoảng cách lớn = bịa/tự tin quá)</h3><table><tr><th>Lúc</th><th>Graph</th><th>Tự chấm</th><th>Audit</th><th>Khoảng cách</th></tr>{grows or "<tr><td colspan=5>Chưa có audit.</td></tr>"}</table>')


def build(dirs: list, out: Path) -> None:
    reg = og.registry_load()
    dirs = [str(Path(d).resolve()) for d in dirs] or reg.get("dirs", []) or [str(ROOT / "llmwiki/graph")]
    graphs = graphs_in(dirs)
    nav = ('<div class="brand">control room</div><a href="#chay">Đang chạy</a><a href="#tien-do">Tiến độ</a><a href="#no">Nợ mở</a><a href="#chi-phi">Hôm nay</a>'
           '<div class="grp">Trang khác</div><a href="orca-graph/atlas.html">Atlas graph</a><a href="fdk-problem-tree.html">Problem tree</a><a href="overstack.html">Overstack</a>')
    main = (f'<h1>Control room</h1><div class="sub">Trang data-first: chỉ đọc registry orca-graph, graph.json, problem-tree, tokens.jsonl, audit-log. Tự refresh 15 s. '
            f'Thư mục đang theo dõi: {", ".join(f"<code>{html.escape(d)}</code>" for d in dirs)}. Daemon: {"pid " + str(og.daemon_alive()) if og.daemon_alive() else "không chạy"}.</div>'
            + block_running(graphs, reg.get("max_running", 4)) + block_progress(graphs) + block_debt() + block_cost(dirs))
    old_css = viz.CSS
    viz.CSS = old_css + "\n.badge{font-size:11px}"
    try:
        viz.page("Control room · overstack", nav, main, out, pagekey="control-room", desc="Trang đầu tiên: đang chạy gì, kẹt gì, nợ gì, tốn bao nhiêu")
    finally:
        viz.CSS = old_css
    s = out.read_text(encoding="utf-8").replace('<meta name="viewport"', '<meta http-equiv="refresh" content="15"><meta name="viewport"', 1)
    out.write_text(s, encoding="utf-8")
    print(f"→ {out}  ({len(graphs)} graph, {len(dirs)} dir)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dirs", nargs="*", default=[]); ap.add_argument("-o", "--out", default=str(ROOT / "llmwiki/html/control-room.html"))
    a = ap.parse_args(argv)
    build(a.dirs, Path(a.out))


if __name__ == "__main__":
    main()
