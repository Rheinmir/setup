#!/usr/bin/env python3
"""build-control-room — trang ĐẦU TIÊN mở ra của framework, data-first: chỉ đọc dữ liệu đã có,
không sinh dữ liệu mới. Bốn khối cockpit: (1) node đang chạy toàn máy (registry orca-graph), (2) tiến độ
từng graph + node kẹt, (3) nợ mở từ problem-tree, (4) chi phí hôm nay + khoảng cách tự chấm/audit.
Cộng trang riêng control-room-kanban.html: bảng dispatch kiểu kanban (cần làm/đang làm/chưa verify/
chặn/xong) + hàng thẻ worker — cột và người giữ suy TỪ claim lock + events.jsonl thật, không bịa roster.
Daemon `orca-graph.py watch` gọi lại file này mỗi khi có graph đổi; trang tự refresh 15 s.

Usage: build-control-room.py [--dirs d1 d2 ...] [-o <overstack>/html/control-room.html]
"""
import argparse, html, importlib.util, json, os, re, subprocess, time
from pathlib import Path



def _ovs_font(html: str) -> str:
    """Font mặc định của mọi HTML framework sinh ra = Lexend Deca Light, NHÚNG (nguồn duy nhất: fdk/tools/html_font.py)."""
    import importlib.util
    here = Path(__file__).resolve()
    for c in (here.with_name("html_font.py"), here.parents[2] / "fdk" / "tools" / "html_font.py", Path.home() / ".claude/harness/fdk/tools/html_font.py"):
        if c.is_file():
            s = importlib.util.spec_from_file_location("html_font", c); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
            return m.apply(html)
    return html

def detect_root() -> Path:
    """Dự án đang GỌI (git-root của CWD, hoặc CWD) luôn thắng trước — script này chạy dưới subprocess
    kế thừa cwd của orca-graph.py, cwd đó chính là dự án downstream cần regen.
    KHÔNG được suy ROOT theo hình dạng thư mục quanh __file__: bản global-install có ĐÚNG hình dạng
    thư mục con của repo framework (được installer copy nguyên cây sang) nên heuristic đoán-theo-hình-dạng
    luôn khớp nhầm, trỏ path về thư mục CÀI ĐẶT thay vì dự án đang chạy — bug đo thật 2026-09-17,
    path in ra trỏ vào thư mục cài global thay vì `<dự án>/.llmwiki/html/...`.
    __file__.parents[2] chỉ dùng khi CWD không có git (hiếm: chạy ad-hoc ngoài mọi repo)."""
    try:
        r = subprocess.run(["git", "-C", str(Path.cwd()), "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, timeout=3)
        if r.returncode == 0 and r.stdout.strip():
            return Path(r.stdout.strip())
    except Exception:
        pass
    repo = Path(__file__).resolve().parents[2]
    if (repo / "fdk" / "tools").is_dir() and (repo / "harness" / "scripts").is_dir():
        return repo
    return Path.cwd()


ROOT = detect_root()


def _load(name: str, cands: list):
    for c in cands:
        if c.is_file():
            spec = importlib.util.spec_from_file_location(name, c); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
    raise SystemExit(f"không tìm thấy {name}: {cands}")


viz = _load("graph_viz", [Path(__file__).with_name("graph-viz.py")])
# Layout máy khách KHÁC repo framework: harness/ → .harness/ hoặc ~/.claude/harness — đi qua overstack_paths, không ghi cứng
_op = _load("overstack_paths", [ROOT / "harness" / "scripts" / "overstack_paths.py", Path.home() / ".claude/harness/harness/scripts/overstack_paths.py"])
HARNESS = Path(_op.harness_dir(ROOT))
OVERSTACK = Path(_op.overstack_dir(ROOT) or (ROOT / "llmwiki"))   # bare-path: ok fallback repo framework khi helper trả None
og = _load("orca_graph", [HARNESS / "scripts" / "orca-graph.py", Path.home() / ".claude/harness/harness/scripts/orca-graph.py"])

STUCK = ("unknown", "failed", "blocked")


def proj_name(d) -> str:
    """Tên dự án từ thư mục store: <proj>/llmwiki/graph → proj; <proj>/.llmwiki/graph → proj; <x>/p1 → p1."""
    parts = [x for x in Path(d).resolve().parts if x not in ("graph", "llmwiki", ".llmwiki")]
    return parts[-1] if parts else str(d)


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
                rows.append(f'<tr><td><code>{html.escape(proj_name(g["_dir"]))}/{html.escape(g["id"])}</code></td><td><code>{n["id"]}</code></td><td>{html.escape(n["title"][:48])}</td>'
                            f'<td><span class="badge" style="border-color:{viz.STATE_COLOR[n["state"]]}">{html.escape(viz.STATE_VI[n["state"]])}</span></td><td>{left}</td><td>{n.get("gen", 0)}</td></tr>')
    warn = f'<div class="sub" style="color:#ef4444">⚠ {len(rows)} node đang chạy vượt trần toàn máy {cap}</div>' if len(rows) > cap else ""
    body = "".join(rows) or '<tr><td colspan="6">Không có node nào đang chạy.</td></tr>'
    return f'<h2 id="chay">Đang chạy toàn máy <span class="badge">{len(rows)}/{cap}</span></h2>{warn}<table><tr><th>Graph</th><th>Node</th><th>Việc</th><th>State</th><th>Lease còn</th><th>Gen</th></tr>{body}</table>'


def block_progress(graphs: list, out: Path) -> str:
    rows = []
    for g in graphs:
        n = len(g["nodes"]); done = sum(1 for x in g["nodes"] if x["state"] in og.TERMINAL_OK)
        stuck = [f'<code>{x["id"]}</code> {html.escape(viz.STATE_VI[x["state"]])}' for x in g["nodes"] if x["state"] in STUCK]
        pct = int(100 * done / n) if n else 0
        bar = f'<svg width="160" height="10" role="img" aria-label="{pct}%"><rect width="160" height="10" rx="5" fill="var(--glass1)" stroke="var(--border)"/><rect width="{1.6*pct:.0f}" height="10" rx="5" fill="#22c55e"/></svg>'
        cands = [Path(g["_dir"]).parent / "html" / "orca-graph" / f"{g['id']}.graph.html",   # <proj>/llmwiki/graph → <proj>/llmwiki/html/orca-graph
                 Path(g["_dir"]) / "html" / "orca-graph" / f"{g['id']}.graph.html"]           # store đặt thẳng trong thư mục dự án
        page = next((c for c in cands if c.exists()), cands[0])
        link = f'<a href="{html.escape(os.path.relpath(page, out.resolve().parent))}">{html.escape(g["id"])}</a>' if page.exists() else html.escape(g["id"])
        rows.append(f'<tr><td><span class="sub">{html.escape(proj_name(g["_dir"]))}/</span>{link}</td><td>{bar} {done}/{n}</td><td>{g.get("control", "active")} · v{g.get("plan_version", 1)} · cấp {g.get("depth", 0)}</td><td>{", ".join(stuck) or "—"}</td></tr>')
    return f'<h2 id="tien-do">Tiến độ từng graph</h2><table><tr><th>Graph</th><th>Xong</th><th>Control · plan · cấp</th><th>Kẹt (cần người / reconcile)</th></tr>{"".join(rows) or "<tr><td colspan=4>Chưa có graph.</td></tr>"}</table>'


def block_debt() -> str:
    p = OVERSTACK / "html" / "fdk-problem-tree.html"
    if not p.exists():
        return '<h2 id="no">Nợ mở</h2><div class="sub">Không có problem-tree.</div>'
    m = re.search(r'<script type="application/json" id="tree-data">(.*?)</script>', p.read_text(encoding="utf-8"), re.S)
    nodes = json.loads(m.group(1)) if m else []
    open_ = sorted([x for x in nodes if x.get("status") != "solved"], key=lambda x: x.get("date", ""), reverse=True)[:8]
    rows = "".join(f'<tr><td><code>{x["id"]}</code></td><td>{html.escape(x["title"][:90])}</td><td>{x.get("status")}</td><td>{x.get("date", "")}</td></tr>' for x in open_)
    return f'<h2 id="no">Nợ mở từ problem-tree <span class="badge">{sum(1 for x in nodes if x.get("status") != "solved")} / {len(nodes)}</span></h2><table><tr><th>ID</th><th>Vấn đề</th><th>Status</th><th>Ngày</th></tr>{rows or "<tr><td colspan=4>Không còn nợ mở.</td></tr>"}</table>'


def block_cost(dirs: list) -> str:
    today = time.strftime("%Y-%m-%d")
    toks = read_jsonl(HARNESS / "metrics" / "tokens.jsonl")
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


def _collect(dirs: list):
    reg = og.registry_load()
    dirs = [str(Path(d).resolve()) for d in dirs] or reg.get("dirs", []) or [str(OVERSTACK / "graph")]
    return reg, dirs, graphs_in(dirs)


def build_detail(dirs: list, out: Path) -> None:
    """Trang CHI TIẾT (dài, cuộn) — mở từ cockpit khi một ô không đủ chỗ."""
    reg, dirs, graphs = _collect(dirs)
    nav = ('<div class="brand">control room · chi tiết</div><a href="control-room.html">← Cockpit</a><a href="#chay">Đang chạy</a><a href="#tien-do">Tiến độ</a><a href="#no">Nợ mở</a><a href="#chi-phi">Hôm nay</a>'
           '<div class="grp">Trang khác</div><a href="control-room-kanban.html">Bảng dispatch (kanban)</a><a href="orca-graph/atlas.html">Atlas graph</a><a href="fdk-problem-tree.html">Problem tree</a><a href="overstack.html">Overstack</a>')
    main = (f'<h1>Control room — chi tiết</h1><div class="sub">Trang data-first: chỉ đọc registry orca-graph, graph.json, problem-tree, tokens.jsonl, audit-log. Tự refresh 15 s. '
            f'Thư mục đang theo dõi: {", ".join(f"<code>{html.escape(d)}</code>" for d in dirs)}. Daemon: {"pid " + str(og.daemon_alive()) if og.daemon_alive() else "không chạy"}.</div>'
            + block_running(graphs, reg.get("max_running", 4)) + block_progress(graphs, out) + block_debt() + block_cost(dirs))
    old_css = viz.CSS; viz.CSS = old_css + "\n.badge{font-size:11px}"
    try:
        viz.page("Control room · chi tiết", nav, main, out, pagekey="control-room", desc="Bản đầy đủ của cockpit")
    finally:
        viz.CSS = old_css
    _refresh(out, graphs); print(f"→ {out}  (chi tiết · {len(graphs)} graph)")


def _refresh(out: Path, graphs: list = ()) -> None:
    """Live bằng JS reload (meta refresh trên file:// không đáng tin trong Chrome — bài học 150926: tab hiện bản hôm qua
    11 giờ) + nhãn trạng thái góc phải. Trang là ẢNH CHỤP: chỉ được vẽ lại khi state đổi hoặc daemon `watch` còn sống.
    Feedback 200926 "control room chết trong âm thầm": bản cũ cứ quá 20 s là đỏ "daemon không ghi?" — kể cả khi KHÔNG có gì
    chạy (daemon cố ý tự thoát sau 10 phút rảnh) → đỏ vĩnh viễn, vô nghĩa, không nói phải làm gì. Nay tách 3 tình huống:
      rảnh   (0 node chạy)                 → xám: "ảnh chụp lúc HH:MM — không có node chạy, state không đổi từ đó" (KHÔNG phải lỗi)
      sống   (có node chạy, trang mới <20s) → xanh
      CHẾT   (có node chạy, trang cũ ≥20s)  → đỏ + đúng một lệnh để bật lại daemon"""
    gen_ms = int(time.time() * 1000)
    running = sum(1 for g in graphs for n in g["nodes"] if n["state"] in ("locked", "dispatched"))
    pid = og.daemon_alive()
    at = time.strftime("%H:%M:%S")
    WATCH = str(og.__file__).replace("\\", "/").replace("'", "")     # đường THẬT của engine trên máy này (repo framework ≠ máy khách ≠ global)
    js = f"""<script>(function(){{var G={gen_ms},RUN={running},PID={pid or 0};var el=document.createElement('div');el.id='live';el.setAttribute('role','status');
document.body.appendChild(el);function tick(){{var a=Math.round((Date.now()-G)/1000);
if(RUN===0){{el.textContent='○ ảnh chụp lúc {at} — không có node chạy, state không đổi từ đó'+(PID?'':' · daemon nghỉ (tự bật khi có node chạy)');el.className='idle';return}}
if(a<20){{el.textContent='● '+RUN+' node đang chạy · cập nhật '+a+' s trước'+(PID?' · daemon pid '+PID:'');el.className='ok';return}}
el.textContent='⚠ '+RUN+' node đang chạy nhưng trang đứng '+a+' s — daemon đã chết. Bật lại: python3 {WATCH} watch';el.className='stale'}}
tick();setInterval(tick,1000);
setInterval(function(){{if(document.visibilityState==='visible')location.reload()}},5000);}})();</script>
<style>#live{{position:fixed;right:14px;bottom:12px;z-index:9;font-size:11px;padding:4px 10px;border-radius:999px;border:1px solid var(--border);background:var(--glass1);backdrop-filter:blur(12px);color:var(--t2);max-width:min(92vw,720px)}}
#live.ok{{color:#22c55e}}#live.idle{{color:var(--t2)}}#live.stale{{color:#fff;background:#ef4444;border-color:#ef4444}}</style>"""
    s = out.read_text(encoding="utf-8").replace('<meta name="viewport"', '<meta http-equiv="refresh" content="5"><meta name="viewport"', 1).replace("</body>", js + "</body>", 1)
    out.write_text(_ovs_font(s), encoding="utf-8")


# ---------- COCKPIT: board-first, mọi thứ trong MỘT màn hình; ô nào tràn thì cắt + "→ chi tiết" ----------
COCKPIT_CSS = """
main a{color:var(--accent);text-decoration:none}main a:hover{text-decoration:underline}
nav{position:sticky;inset:auto;top:0;width:auto;height:auto;flex-direction:row;align-items:center;gap:6px;padding:8px 14px;border-right:0;border-bottom:1px solid var(--border);overflow:visible;z-index:5}
nav::before{display:none}body{padding-left:0!important}nav .brand{padding:0 10px 0 0;font-size:12px}
nav a{padding:5px 9px;border-left:0;border-radius:8px;font-size:11.5px}nav .grp{display:none}nav .nav-close,.nav-toggle{display:none}
nav .kpi{display:flex;gap:6px;flex-wrap:wrap;margin-left:6px}nav .kpi .chip{padding:3px 9px;font-size:11px}
body.nav-collapsed nav{transform:none}  /* cockpit không có sidebar để đóng — localStorage navCollapsed từ trang khác không được kéo thanh trên ra ngoài */
nav .theme-row{position:static;margin-left:auto;padding:0 0 0 12px;border:0;background:transparent;backdrop-filter:none}
main{max-width:none;padding:10px 14px 8px;height:calc(100vh - 50px);display:grid;grid-template-columns:repeat(12,1fr);grid-template-rows:minmax(0,1.15fr) minmax(0,1fr);gap:10px}
.panel{display:flex;flex-direction:column;min-height:0;padding:10px 12px}.panel h2{margin:0 0 6px;font-size:12.5px;display:flex;align-items:center;gap:8px}
.panel h2 .badge{margin-left:auto;font-size:10.5px}.panel .body{overflow:auto;min-height:0;flex:1}.panel table{font-size:11.5px;border-radius:10px}.panel th,.panel td{padding:5px 8px}
.panel .more{font-size:11px;color:var(--accent);text-decoration:none;margin-top:6px;align-self:flex-end}
.p-run{grid-column:span 7}.p-stuck{grid-column:span 5}.p-prog{grid-column:span 4}.p-debt{grid-column:span 5}.p-cost{grid-column:span 3}
.stuck-row{display:flex;gap:8px;align-items:center;padding:6px 4px;border-bottom:1px solid var(--border);font-size:11.5px}.stuck-row:last-child{border:0}
.stuck-row .st{padding:1px 7px;border-radius:999px;color:#fff;font-size:10px;white-space:nowrap}.stuck-row .who{color:var(--t2);white-space:nowrap}
.kv{display:grid;grid-template-columns:auto 1fr;gap:3px 10px;font-size:11.5px}.kv b{font-size:15px}.kv .lb{color:var(--t2)}
footer{grid-column:1/-1;margin:0;font-size:10.5px;align-self:end}footer .path{font-size:10.5px}
@media (max-width:900px){main{height:auto;display:block}.panel{margin-bottom:10px}}
"""

KANBAN_CSS = """
.kboard-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap;margin:16px 0}
.kboard-head .kpi-big{display:flex;gap:22px;align-items:baseline}
.kboard-head .kpi-big b{font-size:26px}.kboard-head .kpi-big span{font-size:10.5px;color:var(--t2);text-transform:uppercase;letter-spacing:.05em;display:block;text-align:center}
.agents{display:flex;gap:10px;flex-wrap:wrap}
.agent-card{flex:1 1 160px;min-width:150px;padding:10px 12px}
.agent-card .id{font-weight:600;font-size:12.5px}
.agent-card .st{font-size:11px;color:var(--t2);margin-top:3px}
.agent-card.busy{border-color:var(--accent);box-shadow:inset 0 1px 0 rgba(255,255,255,.55),0 0 0 1px var(--accent)}
.klanes{display:grid;grid-template-columns:repeat(5,minmax(210px,1fr));gap:12px;overflow-x:auto;padding-bottom:6px}
.klane{background:var(--glass1);border:1px solid var(--border);border-radius:var(--r);padding:10px;min-height:120px}
.klane h3{margin:0 0 2px;font-size:11.5px;text-transform:uppercase;letter-spacing:.04em;display:flex;justify-content:space-between;align-items:center}
.klane .hint{font-size:10.5px;color:var(--t2);margin:0 0 10px}
.kcard{background:var(--glass3);border:1px solid var(--border);border-left:3px solid var(--edge);border-radius:10px;padding:8px 10px;margin-bottom:8px;font-size:12px}
.kcard .kid{font-weight:600;font-size:11.5px}.kcard .ktier{font-size:9.5px;margin-left:5px;padding:0 5px}
.kcard .ktitle{margin:3px 0 4px}
.kcard .kdeps{font-size:10.5px;color:var(--t2)}
.kcard .kowner{display:flex;align-items:center;gap:5px;margin-top:5px;font-size:10.5px;color:var(--t2)}
.kcard .kowner .dot{width:6px;height:6px;border-radius:50%;flex:none}
@media (max-width:900px){.klanes{grid-template-columns:1fr}}
"""


def _trim(rows: list, n: int, anchor: str, detail: str) -> tuple:
    """Cắt danh sách theo ô; phần dư thành link "→ chi tiết" (quy tắc: không đủ vùng hiển thị mới đổi trang)."""
    more = f'<a class="more" href="{detail}#{anchor}">+{len(rows) - n} nữa → chi tiết</a>' if len(rows) > n else ""
    return rows[:n], more


def build_cockpit(dirs: list, out: Path, detail_name: str = "control-room-detail.html") -> None:
    reg, dirs, graphs = _collect(dirs)
    cap = reg.get("max_running", 4); pid = og.daemon_alive()
    # --- ô 1: đang chạy toàn máy ---
    run_rows = []
    for g in graphs:
        st = og.Store(Path(g["_dir"]), g["id"])
        for n in g["nodes"]:
            if n["state"] in ("locked", "dispatched"):
                left = "—"
                try:
                    left = f"{int(json.loads((st.locks_d / n['id']).read_text())['lease_until'] - time.time())} s"
                except (OSError, ValueError, KeyError):
                    pass
                run_rows.append(f'<tr><td><code>{html.escape(proj_name(g["_dir"]))}/{html.escape(g["id"])}</code></td><td><code>{n["id"]}</code></td><td>{html.escape(n["title"][:40])}</td>'
                                f'<td><span class="badge" style="border-color:{viz.STATE_COLOR[n["state"]]}">{html.escape(viz.STATE_VI[n["state"]])}</span></td><td>{left}</td><td>{n.get("gen", 0)}</td></tr>')
    n_run = len(run_rows); run_rows, run_more = _trim(run_rows, 8, "chay", detail_name)
    warn = f'<span class="badge" style="border-color:#ef4444;color:#ef4444">vượt trần</span>' if n_run > cap else ""
    p_run = (f'<section class="card panel p-run"><h2 id="chay">Đang chạy toàn máy {warn}<span class="badge">{n_run}/{cap}</span></h2><div class="body"><table><tr><th>Graph</th><th>Node</th><th>Việc</th><th>State</th><th>Lease</th><th>Gen</th></tr>'
             f'{"".join(run_rows) or "<tr><td colspan=6>Không có node nào đang chạy.</td></tr>"}</table></div>{run_more}</section>')
    # --- ô 2: kẹt / cần người ---
    stuck = []
    for g in graphs:
        for n in g["nodes"]:
            if n["state"] in STUCK:
                stuck.append(f'<div class="stuck-row"><span class="st" style="background:{viz.STATE_COLOR[n["state"]]}">{html.escape(viz.STATE_VI[n["state"]].split(" (")[0])}</span>'
                             f'<code>{html.escape(proj_name(g["_dir"]))}/{html.escape(g["id"])}/{n["id"]}</code><span>{html.escape(n["title"][:34])}</span>'
                             f'<span class="who">{"reconcile" if n["state"] == "unknown" and n.get("verify") else "cần người"}</span></div>')
    n_stuck = len(stuck); stuck, stuck_more = _trim(stuck, 7, "tien-do", detail_name)
    p_stuck = f'<section class="card panel p-stuck"><h2>Kẹt — cần người hoặc reconcile<span class="badge">{n_stuck}</span></h2><div class="body">{"".join(stuck) or "<div class=sub>Không có node kẹt.</div>"}</div>{stuck_more}</section>'
    # --- ô 3: tiến độ ---
    prog = []
    for g in sorted(graphs, key=lambda x: x.get("built", ""), reverse=True):
        n = len(g["nodes"]); done = sum(1 for x in g["nodes"] if x["state"] in og.TERMINAL_OK); pct = int(100 * done / n) if n else 0
        cands = [Path(g["_dir"]).parent / "html" / "orca-graph" / f"{g['id']}.graph.html", Path(g["_dir"]) / "html" / "orca-graph" / f"{g['id']}.graph.html"]
        page = next((c for c in cands if c.exists()), None)
        name = f'<a href="{html.escape(os.path.relpath(page, out.resolve().parent))}">{html.escape(g["id"])}</a>' if page else html.escape(g["id"])
        bar = f'<svg width="90" height="8"><rect width="90" height="8" rx="4" fill="var(--glass1)" stroke="var(--border)"/><rect width="{0.9*pct:.0f}" height="8" rx="4" fill="#22c55e"/></svg>'
        prog.append(f'<tr><td><span class="sub">{html.escape(proj_name(g["_dir"]))}/</span>{name}</td><td>{bar} {done}/{n}</td><td class="sub">{g.get("control", "active")} · v{g.get("plan_version", 1)}</td></tr>')
    n_prog = len(prog); prog, prog_more = _trim(prog, 7, "tien-do", detail_name)
    p_prog = f'<section class="card panel p-prog"><h2 id="tien-do">Tiến độ<span class="badge">{n_prog} graph</span></h2><div class="body"><table><tr><th>Graph</th><th>Xong</th><th></th></tr>{"".join(prog) or "<tr><td colspan=3>Chưa có graph.</td></tr>"}</table></div>{prog_more}</section>'
    # --- ô 4: nợ mở ---
    debt_rows, n_open, n_all = [], 0, 0
    pt = OVERSTACK / "html" / "fdk-problem-tree.html"
    if pt.exists():
        m = re.search(r'<script type="application/json" id="tree-data">(.*?)</script>', pt.read_text(encoding="utf-8"), re.S)
        nodes = json.loads(m.group(1)) if m else []; n_all = len(nodes)
        open_ = sorted([x for x in nodes if x.get("status") != "solved"], key=lambda x: x.get("date", ""), reverse=True); n_open = len(open_)
        debt_rows = [f'<tr><td><code>{x["id"]}</code></td><td>{html.escape(x["title"][:70])}</td><td class="sub">{x.get("status")}</td></tr>' for x in open_]
    debt_rows, debt_more = _trim(debt_rows, 7, "no", detail_name)
    p_debt = f'<section class="card panel p-debt"><h2 id="no">Nợ mở (problem-tree)<span class="badge">{n_open}/{n_all}</span></h2><div class="body"><table>{"".join(debt_rows) or "<tr><td>Không còn nợ mở.</td></tr>"}</table></div>{debt_more}</section>'
    # --- ô 5: chi phí + audit ---
    toks = read_jsonl(HARNESS / "metrics" / "tokens.jsonl")[-8:]
    usd = sum(float(t.get("usd", 0) or 0) for t in toks); tout = sum(int(t.get("out", 0) or 0) for t in toks)
    gaps = sorted([(a.get("ts", ""), a.get("graph", ""), a.get("self", 0), a.get("audit", 0)) for d in dirs for a in read_jsonl(Path(d) / "audit-log.jsonl")], reverse=True)[:3]
    gap_html = "".join(f'<div class="stuck-row"><code>{html.escape(g)[:26]}</code><span class="who">tự {s:.1f} · audit {a:.1f} · lệch {s - a:.1f}</span></div>' for _, g, s, a in gaps) or '<div class="sub">Chưa có audit.</div>'
    p_cost = (f'<section class="card panel p-cost"><h2 id="chi-phi">Chi phí & audit</h2><div class="body"><div class="kv"><span class="lb">{len(toks)} session gần nhất</span><b>${usd:,.2f}</b><span class="lb">output tokens</span><b>{tout:,}</b></div>'
              f'<div class="sub" style="margin:8px 0 4px">Model tự chấm vs audit</div>{gap_html}</div><a class="more" href="{detail_name}#chi-phi">→ chi tiết</a></section>')
    kanban_name = detail_name.replace("-detail.html", "-kanban.html")
    nav = (f'<div class="brand">cockpit</div><div class="kpi"><span class="chip">daemon <b>{"pid " + str(pid) if pid else "tắt"}</b></span><span class="chip">chạy <b>{n_run}/{cap}</b></span>'
           f'<span class="chip">kẹt <b>{n_stuck}</b></span><span class="chip">graph <b>{len(graphs)}</b></span><span class="chip">nợ <b>{n_open}</b></span></div>'
           f'<a href="#chay">Đang chạy</a><a href="#tien-do">Tiến độ</a><a href="#no">Nợ mở</a><a href="#chi-phi">Hôm nay</a><a href="{detail_name}">Chi tiết ↗</a><a href="{kanban_name}">Bảng dispatch (kanban) ↗</a><a href="orca-graph/atlas.html">Atlas</a><a href="fdk-problem-tree.html">Problem tree</a>')
    old_css = viz.CSS; viz.CSS = old_css + COCKPIT_CSS
    try:
        viz.page("Cockpit · overstack", nav, p_run + p_stuck + p_prog + p_debt + p_cost, out, pagekey="control-room", desc="Board-first: đang chạy · kẹt · tiến độ · nợ · chi phí trong một màn hình")
    finally:
        viz.CSS = old_css
    _refresh(out, graphs); print(f"→ {out}  (cockpit · {len(graphs)} graph, {n_run} chạy, {n_stuck} kẹt)")


# ---------- KANBAN: bảng dispatch (cần làm/đang làm/chưa verify/chặn/xong) + hàng thẻ worker ----------
# Cột suy từ MÁY STATE THẬT của orca-graph.py (proposed→ready→locked→dispatched→done|done_unverified|
# failed|unknown; blocked=HITL) — không có khái niệm "testing"/"verifying" riêng trong hệ này nên gộp
# theo ngữ nghĩa gần nhất thay vì bịa cột giả: done_unverified+unknown = "chưa verify" (chờ reconcile),
# blocked+failed = "chặn" (cần người quyết).
LANES = [
    ("todo", "Cần làm", "claimable", {"proposed", "ready"}, "#0a84ff"),
    ("doing", "Đang làm", "worker đang giữ packet", {"locked", "dispatched"}, "#f59e0b"),
    ("unverified", "Chưa verify", "chờ reconcile/verify", {"done_unverified", "unknown"}, "#84cc16"),
    ("blocked", "Chặn", "cần người / retry", {"blocked", "failed"}, "#ef4444"),
    ("done", "Xong", "đã commit", {"done", "done_user_reported"}, "#22c55e"),
]


def _rel_time(ts: str) -> str:
    try:
        t = time.mktime(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S"))
    except ValueError:
        return ts
    d = max(0, int(time.time() - t))
    if d < 60:
        return f"{d}s trước"
    if d < 3600:
        return f"{d // 60} phút trước"
    if d < 86400:
        return f"{d // 3600} giờ trước"
    return f"{d // 86400} ngày trước"


def _agents(graphs: list) -> list:
    """Suy worker/agent TỪ events.jsonl thật (trường `by`) + lock hiện có — KHÔNG bịa roster tĩnh
    (không có khái niệm 'tier'/'GPU' trong orca-graph, nên không hiển thị — khác gì không có thì nói thẳng)."""
    last_seen: dict = {}   # by -> (ts, to, "proj/graph/node")
    busy: dict = {}        # by -> ("proj/graph/node", lease_left_s)
    for g in graphs:
        gid = f'{proj_name(g["_dir"])}/{g["id"]}'
        st = og.Store(Path(g["_dir"]), g["id"])
        for e in read_jsonl(st.events_p):
            by = e.get("by")
            if not by or by == "reconcile":
                continue
            key = f'{gid}/{e.get("node", "-")}'
            if by not in last_seen or e.get("ts", "") > last_seen[by][0]:
                last_seen[by] = (e.get("ts", ""), e.get("to", ""), key)
        for n in g["nodes"]:
            if n["state"] not in ("locked", "dispatched"):
                continue
            try:
                lk = json.loads((st.locks_d / n["id"]).read_text())
                by, left = lk.get("by"), int(lk.get("lease_until", 0) - time.time())
                if by and left > 0:
                    busy[by] = (f'{gid}/{n["id"]}', left)
            except (OSError, ValueError, KeyError):
                pass
    out = []
    for w in sorted(set(last_seen) | set(busy)):
        if w in busy:
            node, left = busy[w]
            out.append({"id": w, "busy": True, "detail": f'đang giữ <code>{html.escape(node)}</code> · lease còn {left}s'})
        else:
            ts, to, node = last_seen.get(w, ("", "", ""))
            out.append({"id": w, "busy": False, "detail": f'idle · lần cuối <b>{html.escape(to)}</b> <code>{html.escape(node)}</code> · {_rel_time(ts)}' if ts else "idle"})
    return out


def _node_owner(st, node_id: str):
    """Chủ thẻ = lock hiện tại (nếu có); không có lock → người CHẠM gần nhất trong events cho node đó."""
    try:
        lk = json.loads((st.locks_d / node_id).read_text())
        return lk.get("by"), "từ claim lock"
    except (OSError, ValueError, KeyError):
        pass
    last_by, last_to = None, None
    for e in read_jsonl(st.events_p):
        if e.get("node") == node_id and e.get("by"):
            last_by, last_to = e["by"], e.get("to")
    src = {"dispatched": "từ dispatch record", "locked": "từ claim lock"}.get(last_to, f"từ event {last_to}" if last_to else None)
    return last_by, src


def build_kanban(dirs: list, out: Path, detail_name: str = "control-room-detail.html") -> None:
    reg, dirs, graphs = _collect(dirs)
    agents = _agents(graphs)
    lanes_nodes = {key: [] for key, *_ in LANES}
    for g in graphs:
        gid = f'{proj_name(g["_dir"])}/{g["id"]}'
        st = og.Store(Path(g["_dir"]), g["id"])
        for n in g["nodes"]:
            lane = next((key for key, _, _, states, _ in LANES if n["state"] in states), None)
            if not lane:
                continue
            owner_by, owner_src = _node_owner(st, n["id"])
            owner_html = (f'<div class="kowner"><span class="dot" style="background:{viz.STATE_COLOR[n["state"]]}"></span>'
                          f'<b>{html.escape(owner_by)}</b> {html.escape(owner_src or "")}</div>') if owner_by else '<div class="kowner">— chưa ai chạm</div>'
            deps = ", ".join(n.get("deps") or []) or "—"
            lanes_nodes[lane].append(
                f'<div class="kcard" style="border-left-color:{viz.STATE_COLOR[n["state"]]}">'
                f'<div><span class="kid">{html.escape(gid)}/{html.escape(n["id"])}</span><span class="ktier badge">{html.escape(n.get("kind") or "build")}</span></div>'
                f'<div class="ktitle">{html.escape(n["title"][:70])}</div>'
                f'<div class="kdeps">← {html.escape(deps)}</div>{owner_html}</div>')
    n_done, n_doing, n_total = len(lanes_nodes["done"]), len(lanes_nodes["doing"]), sum(len(v) for v in lanes_nodes.values())
    lanes_html = "".join(
        f'<div class="klane" style="border-top:3px solid {color}"><h3>{html.escape(label)}<span class="badge">{len(lanes_nodes[key])}</span></h3>'
        f'<div class="hint">{html.escape(hint)}</div>{"".join(lanes_nodes[key]) or "<div class=sub>Trống.</div>"}</div>'
        for key, label, hint, _, color in LANES)
    agents_html = "".join(
        f'<div class="card agent-card{" busy" if a["busy"] else ""}"><div class="id">{html.escape(a["id"])}</div><div class="st">{a["detail"]}</div></div>'
        for a in agents) or '<div class="sub">Chưa thấy worker nào trong events.</div>'
    main = (f'<h1>Bảng dispatch</h1><div class="sub">Một phép chiếu của repository, không phải danh sách ai đó giữ bằng tay. '
            f'Cột và người giữ mỗi thẻ đến từ chính claim lock, bản ghi dispatch, verdict verify và lịch sử events.</div>'
            f'<div class="kboard-head"><div class="agents">{agents_html}</div>'
            f'<div class="kpi-big"><div><b>{n_done}</b><span>xong</span></div><div><b>{n_doing}</b><span>đang chạy</span></div>'
            f'<div><b>{n_total}</b><span>tổng node</span></div></div></div>'
            f'<div class="klanes">{lanes_html}</div>')
    nav = ('<div class="brand">bảng dispatch · kanban</div><a href="control-room.html">← Cockpit</a><a href="' + detail_name + '">Chi tiết</a>'
           '<div class="grp">Trang khác</div><a href="orca-graph/atlas.html">Atlas graph</a><a href="fdk-problem-tree.html">Problem tree</a><a href="overstack.html">Overstack</a>')
    old_css = viz.CSS; viz.CSS = old_css + KANBAN_CSS
    try:
        viz.page("Bảng dispatch · kanban", nav, main, out, pagekey="control-room", desc="Kanban node theo state thật (claim lock/dispatch/QC) + worker đang bận hay idle")
    finally:
        viz.CSS = old_css
    _refresh(out, graphs); print(f"→ {out}  (kanban · {len(graphs)} graph, {n_total} node, {len(agents)} worker)")


def build(dirs: list, out: Path) -> None:
    out = Path(out)
    build_cockpit(dirs, out)
    build_detail(dirs, out.with_name(out.stem + "-detail.html"))
    build_kanban(dirs, out.with_name(out.stem + "-kanban.html"), detail_name=out.with_name(out.stem + "-detail.html").name)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dirs", nargs="*", default=[]); ap.add_argument("-o", "--out", default=str(OVERSTACK / "html" / "control-room.html"))
    a = ap.parse_args(argv)
    build(a.dirs, Path(a.out))


if __name__ == "__main__":
    main()
