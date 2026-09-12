#!/usr/bin/env python3
"""orca-graph — phân việc dạng ĐỒ THỊ PHỤ THUỘC trên PLAN.md, có khoá + lease + generation,
state bền append-only (events.jsonl), và sổ câu trả lời của model có audit nguồn.

Store (mặc định `llmwiki/graph/`, override bằng --dir):
  <id>.graph.json      cache fold từ events (ghi temp → fsync → rename)
  <id>.events.jsonl    append-only {ts,node,from,to,by,op_key,gen,rev,note}
  <id>.answers.jsonl   câu trả lời của MODEL: {q,node,label,score,evidence[],text,ts}
  <id>.locks/<node>    lockfile O_EXCL {gen,lease_until,by}

Lệnh:
  build <PLAN.md> [--id X]          PLAN → graph (deps từ `**Depends:**`, thiếu → suy từ Consumes/Produces "Task N")
  ask <id> needs|parallel|deps <n>|why <n>|related
  next <id>                         node ready (đã reaper lease hết → unknown)
  lock|unlock|heartbeat <id> <n> [--by X] [--lease-sec N]
  set <id> <n> <state> [--op-key K] [--gen G] [--if-rev R] [--note ..] [--by X]
  reconcile <id> <n>                chạy `verify` cho node unknown/done_unverified
  sync-orca <id> [--run]            in (hoặc chạy) `orca orchestration task-create --deps` theo topo
  answer <id> <n|-> --q Q --label chắc|gợi-ý|không-biết --score S --evidence E.. --text T
  audit <id>                        mở lại từng nguồn; không mở được = bịa = 0
  show <id>                         tóm tắt state
Luật một dòng của rubric: đúng 1 · sai 0 · không-biết 0.3 · gợi-ý có nguồn thật 0.5 · bịa nguồn 0.
"""
import argparse, hashlib, json, os, re, subprocess, sys, time
from pathlib import Path

SCHEMA = 1
STATES = ["proposed", "ready", "locked", "dispatched", "done", "done_unverified",
          "done_user_reported", "failed", "unknown", "blocked"]
TERMINAL_OK = {"done", "done_user_reported"}
LABELS = {"chắc": 1.0, "gợi-ý": 0.5, "không-biết": 0.3}
DEFAULT_DIR = Path("llmwiki/graph")


# ---------- store ----------
def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def atomic_write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, p)


def append_jsonl(p: Path, obj: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n"); f.flush(); os.fsync(f.fileno())


def read_jsonl(p: Path) -> list:
    if not p.exists():
        return []
    out = []
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    for i, ln in enumerate(lines):
        if not ln.strip():
            continue
        try:
            out.append(json.loads(ln))
        except json.JSONDecodeError:
            if i == len(lines) - 1:   # dòng cuối cụt do kill giữa chừng → bỏ, không hỏng sổ
                continue
            raise SystemExit(f"events hỏng ở dòng {i+1}: {p}")
    return out


class Store:
    def __init__(self, d: Path, gid: str):
        self.d, self.gid = d, gid
        self.graph_p = d / f"{gid}.graph.json"
        self.events_p = d / f"{gid}.events.jsonl"
        self.answers_p = d / f"{gid}.answers.jsonl"
        self.locks_d = d / f"{gid}.locks"

    def load(self) -> dict:
        if not self.graph_p.exists():
            raise SystemExit(f"không có graph: {self.graph_p}")
        g = json.loads(self.graph_p.read_text(encoding="utf-8"))
        if g.get("schema_version") != SCHEMA:
            raise SystemExit(f"schema_version {g.get('schema_version')} ≠ {SCHEMA} — dừng, không đoán")
        body = {k: v for k, v in g.items() if k != "checksum"}
        if g.get("checksum") and checksum(body) != g["checksum"]:
            print("⚠ checksum lệch — fold lại từ events", file=sys.stderr)
        return fold(g, read_jsonl(self.events_p), self.d)

    def save(self, g: dict) -> None:
        g["schema_version"] = SCHEMA
        g.pop("checksum", None)
        g["checksum"] = checksum(g)
        atomic_write(self.graph_p, json.dumps(g, ensure_ascii=False, indent=1))


def checksum(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def fold(g: dict, events: list, d: Path = None) -> dict:
    """graph.json là cache; events là sự thật. Fold idempotent theo op_key."""
    nodes = {n["id"]: n for n in g["nodes"]}
    seen = set()
    for n in nodes.values():   # fold LUÔN từ gốc — events là sự thật duy nhất, gọi lặp không cộng dồn
        n.update(state="proposed", gen=0, rev=0, attempts=0, fresh="current", verified="unverified")
    g["control"] = "active"
    for e in events:
        k = e.get("op_key")
        if k and k in seen:
            continue
        if k:
            seen.add(k)
        if e.get("kind") == "control":
            g["control"] = e["to"]; continue
        n = nodes.get(e.get("node"))
        if not n:
            continue
        if e.get("kind") == "stale_result":
            continue
        if e.get("to") in STATES:
            n["state"] = e["to"]; n["rev"] = max(n["rev"], e.get("rev", n["rev"]))
            if e.get("gen") is not None:
                n["gen"] = max(n["gen"], e["gen"])
            if e["to"] == "dispatched":
                n["attempts"] = n.get("attempts", 0) + 1
            if e["to"] == "done":
                n["verified"] = "verified"
            if e["to"] in TERMINAL_OK or e["to"] == "done_unverified":
                n["done_spec_hash"] = e.get("spec_hash")
            if e["to"] in ("ready", "proposed"):
                n["verified"] = "unverified"
    # control (PRD §8.3, invariant 11): "đã yêu cầu" chỉ thành "đã dừng" khi không còn node đang chạy
    running = any(n["state"] in ("locked", "dispatched") for n in nodes.values())
    if g["control"] == "pause_requested" and not running:
        g["control"] = "paused"
    if g["control"] == "cancel_requested" and not running:
        g["control"] = "cancelled"
    # join (PRD §4/§8.5, invariant 4): node có child_graph chỉ xong khi MỌI node con xong; con blocked → mẹ blocked
    for n in nodes.values():
        cg = n.get("child_graph")
        if cg and d is not None and n["state"] not in TERMINAL_OK:
            try:
                kids = Store(d, cg).load()["nodes"]
            except SystemExit:
                continue
            if kids and all(k["state"] in TERMINAL_OK for k in kids):
                n["state"] = "done_unverified"; n["verified"] = "unverified"
            elif any(k["state"] == "blocked" for k in kids):
                n["state"] = "blocked"
    # freshness: upstream redo sau khi mình done → stale (cảnh báo, không lùi state)
    for n in nodes.values():
        if n["state"] in TERMINAL_OK:
            up_redo = any(nodes[d]["state"] not in TERMINAL_OK for d in n["deps"] if d in nodes)
            spec_changed = bool(n.get("done_spec_hash")) and n.get("spec_hash") and n["done_spec_hash"] != n["spec_hash"]
            n["fresh"] = "stale" if (up_redo or spec_changed) else "current"
    # ready: proposed mà mọi deps done (dep ngoài `gid/tid` đọc store graph kia; không có store → chưa thoả)
    ext_cache = {}
    def dep_ok(dep):
        if dep in nodes:
            return nodes[dep]["state"] in TERMINAL_OK
        if "/" in dep and d is not None:
            og_, tn = dep.split("/", 1)
            if og_ not in ext_cache:
                try:
                    ext_cache[og_] = {x["id"]: x for x in Store(d, og_).load()["nodes"]}
                except SystemExit:
                    ext_cache[og_] = {}
            return ext_cache[og_].get(tn, {}).get("state") in TERMINAL_OK
        return False
    for n in nodes.values():
        if n["state"] == "proposed" and all(dep_ok(x) for x in n["deps"]):
            n["state"] = "blocked" if n.get("mode") == "hitl" else "ready"
    return g


# ---------- PLAN parser ----------
TASK_RE = re.compile(r"^### Task ([A-Za-z0-9]+)[:\s]+(.*)$")
TASK_REF = re.compile(r"Task ([A-Za-z0-9]+)")


def tid(tok: str) -> str:
    return f"t{tok}" if tok.isdigit() else tok.lower()


def parse_plan(text: str) -> list:
    tasks, cur, fence = [], None, False
    for ln in text.splitlines():
        if ln.strip().startswith("```"):
            fence = not fence; continue
        if fence:                      # nội dung trong khối code không phải cấu trúc PLAN
            continue
        m = TASK_RE.match(ln.strip())
        if m:
            cur = {"id": tid(m.group(1)), "num": tid(m.group(1)), "title": m.group(2).strip(), "files": [],
                   "consumes": [], "produces": [], "deps": [], "deps_conf": "chắc", "kind": "build",
                   "mode": "afk", "verify": "", "produces_for": []}
            tasks.append(cur); continue
        if cur is None or ln.startswith("## "):
            if ln.startswith("## "):
                cur = None
            continue
        s = ln.strip()
        fm = re.match(r"^- (Tạo|Sửa|Test|Xoá|Create|Modify):\s*`([^`]+)`", s)
        if fm:
            cur["files"].append(fm.group(2).split(":")[0]); continue
        for key, field in (("Depends", "deps_raw"), ("Kind", "kind"), ("Mode", "mode"), ("Verify", "verify")):
            km = re.match(rf"^\*\*{key}:\*\*\s*(.*)$", s)
            if km:
                cur[field] = km.group(1).strip().strip("`")
        if s.startswith("- Consumes:"):
            cur["consumes"].append(s[len("- Consumes:"):].strip())
        if s.startswith("- Produces"):
            cur["produces"].append((s.split(":", 1)[1].strip() if ":" in s else "") or s.lstrip("- "))
            cur["produces_for"] += [tid(x) for x in TASK_REF.findall(s)]
    ids = {t["num"] for t in tasks}
    for t in tasks:
        raw = t.pop("deps_raw", "")
        if raw:
            deps = []
            for tok in [x.strip() for x in raw.split(",") if x.strip() and x.strip() != "—"]:
                if "/" in tok:                       # dep XUYÊN graph: <gid>/<tid> (PRD §3.2 milestone có địa chỉ đầy đủ)
                    deps.append(tok)
                else:
                    x = tid(re.sub(r"^Task\s*", "", tok))
                    if x in ids and x != t["num"]:
                        deps.append(x)
            t["deps"] = deps
        else:  # suy từ Consumes "Task N" + Produces "dùng bởi Task N" của task khác
            dep = {tid(x) for c in t["consumes"] for x in TASK_REF.findall(c)}
            dep |= {o["num"] for o in tasks if t["num"] in o["produces_for"]}
            t["deps"] = [x for x in sorted(dep) if x in ids and x != t["num"]]
            t["deps_conf"] = "gợi-ý" if t["deps"] else "chắc"
        t["mode"] = "hitl" if t["mode"].lower().startswith("hitl") else "afk"
    for t in tasks:
        for k in ("num", "produces_for"):
            t.pop(k, None)
    return tasks


def spec_hash(n: dict) -> str:
    """Băm HỢP ĐỒNG của node (title/files/deps/verify/produces) — đổi là node đã-xong thành stale (PRD §7.3, §10.1)."""
    return hashlib.sha256(json.dumps({k: n.get(k) for k in ("title", "files", "deps", "verify", "produces")}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def toposort(nodes: dict) -> list:
    """Trả về các LỚP (mỗi lớp = chạy song song được). Raise nếu có cycle."""
    indeg = {i: len([d for d in n["deps"] if d in nodes]) for i, n in nodes.items()}
    layers, done = [], set()
    while len(done) < len(nodes):
        layer = sorted(i for i, d in indeg.items() if d == 0 and i not in done)
        if not layer:
            raise SystemExit("CYCLE: " + ", ".join(i for i in nodes if i not in done))
        layers.append(layer); done |= set(layer)
        for i in layer:
            for j, n in nodes.items():
                if i in n["deps"]:
                    indeg[j] -= 1
    return layers


def write_conflicts(nodes: dict, layers: list) -> list:
    out = []
    for layer in layers:
        for a in layer:
            for b in layer:
                if a < b:
                    shared = sorted(set(nodes[a]["files"]) & set(nodes[b]["files"]))
                    if shared:
                        out.append({"a": a, "b": b, "files": shared})
    return out


def cmd_build(a):
    plan = Path(a.plan)
    text = plan.read_text(encoding="utf-8")
    gid = a.id or plan.stem.replace("-PLAN", "").replace("_PLAN", "")
    tasks = parse_plan(text)
    if not tasks:
        raise SystemExit("PLAN không có `### Task N:` nào")
    if len(tasks) > 20:
        raise SystemExit(f"{len(tasks)} node > 20/graph (PRD §5.2) — gom theo trách nhiệm hoặc tách graph con")
    parent, depth = None, 0
    if a.parent:
        pg, pn = a.parent.split("/", 1)
        pst = Store(Path(a.dir), pg); pgraph = pst.load()
        pnode = {n["id"]: n for n in pgraph["nodes"]}.get(pn)
        if not pnode:
            raise SystemExit(f"graph mẹ {pg} không có node {pn}")
        depth = pgraph.get("depth", 0) + 1
        if depth > 6:
            raise SystemExit(f"depth {depth} > 6 (PRD §5.2) — giảm scope thay vì đào sâu")
        parent = {"graph": pg, "node": pn}
        pnode["child_graph"] = gid; pst.save(pgraph)
    nodes = {t["id"]: t for t in tasks}
    layers = toposort(nodes)
    conflicts = write_conflicts(nodes, layers)
    st = Store(Path(a.dir), gid)
    for t in tasks:
        t["spec_hash"] = spec_hash(t)
    plan_version, superseded = 1, []
    if st.graph_p.exists():                      # REPLAN (PRD §10.1): version mới, không xoá lịch sử (invariant 10)
        old = json.loads(st.graph_p.read_text(encoding="utf-8"))
        old = fold(old, read_jsonl(st.events_p), Path(a.dir))
        plan_version = old.get("plan_version", 1) + 1
        old_nodes = {n["id"]: n for n in old["nodes"]}
        removed = [i for i in old_nodes if i not in nodes]
        changed = [i for i in nodes if i in old_nodes and old_nodes[i].get("spec_hash") != nodes[i]["spec_hash"]]
        superseded = old.get("superseded", []) + [{"id": i, "title": old_nodes[i]["title"], "state": old_nodes[i]["state"], "plan_version": old.get("plan_version", 1)} for i in removed]
        append_jsonl(st.events_p, {"ts": now(), "kind": "plan.rebuilt", "node": "-", "from": old.get("plan_version", 1), "to": plan_version,
                                   "changed": changed, "removed": removed, "op_key": f"rebuild:{plan_version}"})
        print(f"REPLAN: plan_version {old.get('plan_version', 1)} → {plan_version} · đổi spec {changed or '—'} · bỏ {removed or '—'}")
    g = {"id": gid, "plan": str(plan), "built": now(), "nodes": tasks, "layers": layers, "parent": parent, "depth": depth,
         "plan_version": plan_version, "superseded": superseded, "max_parallel": a.max_parallel, "conflicts": conflicts, "links": find_links(Path(a.dir), gid, tasks)}
    g = fold(g, read_jsonl(st.events_p), Path(a.dir))
    st.save(g)
    print(f"graph {gid}: {len(tasks)} node · {len(layers)} lớp · cấp {depth} · {len(conflicts)} xung đột ghi cùng file · {len(g['links'])} liên hệ graph cũ")
    for c in conflicts:
        print(f"  ⚠ {c['a']} ∥ {c['b']} cùng ghi {c['files']} → nên ép tuần tự (thêm **Depends:**)")
    sug = [t["id"] for t in tasks if t["deps_conf"] == "gợi-ý"]
    if sug:
        print(f"  ℹ deps SUY LUẬN (gợi-ý, chưa khai **Depends:**): {', '.join(sug)}")
    print(f"  → {st.graph_p}")
    if a.strict:
        bad = [t["id"] for t in tasks if not t.get("verify") or not t.get("files")]
        if bad:
            print(f"STRICT: {bad} thiếu verify/files — không dispatch được (PRD §4.4)"); sys.exit(2)


def find_links(d: Path, gid: str, tasks: list) -> list:
    """Liên hệ graph cũ = khớp ARTIFACT (file) — tất định. Ngữ nghĩa để model trả lời + gắn nhãn."""
    mine = {f for t in tasks for f in t["files"]}
    links = []
    for p in sorted(d.glob("*.graph.json")):
        if p.stem == f"{gid}.graph":
            continue
        try:
            og = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        for on in og.get("nodes", []):
            shared = sorted(mine & set(on.get("files", [])))
            if shared:
                links.append({"to_graph": og["id"], "to_node": on["id"], "via": shared, "kind": "touches-same-file"})
    return links


def cmd_check_cycles(a):
    """Gộp MỌI graph trong dir thành một DAG khoá gid/tid; in ĐƯỜNG cycle cụ thể (PRD §5.3), rc 2."""
    d = Path(a.dir); edges = {}
    for p in sorted(d.glob("*.graph.json")):
        g = json.loads(p.read_text(encoding="utf-8"))
        for n in g["nodes"]:
            edges[f"{g['id']}/{n['id']}"] = [x if "/" in x else f"{g['id']}/{x}" for x in n["deps"]]
    color, path, found = {}, [], []
    def dfs(u):
        color[u] = 1; path.append(u)
        for v in edges.get(u, []):
            if v not in edges:
                continue
            if color.get(v) == 1:
                found.append(path[path.index(v):] + [v]); return True
            if color.get(v, 0) == 0 and dfs(v):
                return True
        path.pop(); color[u] = 2; return False
    for u in list(edges):
        if color.get(u, 0) == 0 and dfs(u):
            break
    if found:
        print("CYCLE: " + " → ".join(found[0])); sys.exit(2)
    print(f"OK: {len(edges)} node trong {len(list(d.glob('*.graph.json')))} graph, không cycle")


# ---------- leaf contract (PRD §4.4) ----------
def leaf_gaps(n: dict) -> list:
    """Leaf chỉ hợp lệ khi đủ: outcome · phạm vi ghi · output · phép kiểm quan sát được · deps rõ."""
    gaps = []
    if not n.get("title"):
        gaps.append("title (outcome)")
    if not n.get("files"):
        gaps.append("files (phạm vi ghi)")
    if not any(x.strip("—- ") for x in n.get("produces", [])):
        gaps.append("produces (output)")
    if not n.get("verify"):
        gaps.append("verify (phép kiểm)")
    if n.get("deps_conf") == "gợi-ý":
        gaps.append("deps suy luận (chưa khai Depends)")
    return gaps


def cmd_lint(a):
    g = Store(Path(a.dir), a.id).load()
    ok = 0
    for n in g["nodes"]:
        gaps = leaf_gaps(n)
        ok += not gaps
        print(f"  {'✓' if not gaps else '✗'} {n['id']:<4} {n['title'][:48]:<50} {'; '.join(gaps)}")
    print(f"{ok}/{len(g['nodes'])} leaf đủ hợp đồng (PRD §4.4)")


# ---------- ask ----------
def upstream(nodes, nid, acc=None):
    acc = acc if acc is not None else []
    for d in nodes[nid]["deps"]:
        if d in nodes and d not in acc:
            acc.append(d); upstream(nodes, d, acc)
    return acc


def downstream(nodes, nid):
    return [i for i, n in nodes.items() if nid in upstream(nodes, i)]


def cmd_ask(a):
    g = Store(Path(a.dir), a.id).load()
    nodes = {n["id"]: n for n in g["nodes"]}
    q = a.query[0]
    if q == "needs":
        for l, layer in enumerate(g["layers"]):
            for i in layer:
                n = nodes[i]
                print(f"[L{l}] {i} {n['title']}  ({n['kind']}/{n['mode']}, {n['state']})  files={len(n['files'])}")
    elif q == "parallel":
        for l, layer in enumerate(g["layers"]):
            tag = " ⚠xung đột" if any({c['a'], c['b']} <= set(layer) for c in g["conflicts"]) else ""
            print(f"L{l}: {' ∥ '.join(layer)}{tag}")
        rn = [i for i, n in nodes.items() if n["state"] == "ready"]
        print(f"chạy NGAY được: {' ∥ '.join(rn) or '(không có)'}")
    elif q in ("deps", "why"):
        nid = a.query[1]
        n = nodes[nid]
        if q == "deps":
            print(f"{nid} phụ thuộc TRỰC TIẾP: {n['deps'] or '—'} [{n['deps_conf']}]")
            print(f"gián tiếp: {upstream(nodes, nid) or '—'}")
            print(f"mở khoá cho: {downstream(nodes, nid) or '—'}")
        else:
            print(f"{nid} — {n['title']}")
            print(f"  làm ra: {n['produces'] or '—'}")
            print(f"  mở khoá: {downstream(nodes, nid) or '— (lá; giá trị nằm ở chính output)'}")
            print(f"  chạm file: {n['files']}")
            ls = [l for l in g["links"] if any(f in l["via"] for f in n["files"])]
            print(f"  liên hệ graph cũ (khớp file): {[(l['to_graph'], l['to_node']) for l in ls] or '—'}")
    elif q == "related":
        for l in g["links"]:
            print(f"{g['id']} → {l['to_graph']}/{l['to_node']} via {l['via']} [{l['kind']}]")
        if not g["links"]:
            print("không khớp artifact với graph cũ nào (liên hệ ngữ nghĩa → model trả lời, nhãn gợi-ý)")
    else:
        raise SystemExit("ask: needs|parallel|deps <n>|why <n>|related")


# ---------- runtime ----------
def reaper(st: Store, g: dict, by="reaper") -> int:
    nodes = {n["id"]: n for n in g["nodes"]}
    n_exp = 0
    if st.locks_d.exists():
        for lp in st.locks_d.iterdir():
            try:
                lk = json.loads(lp.read_text())
            except Exception:
                continue
            if time.time() > lk["lease_until"] and nodes.get(lp.name, {}).get("state") in ("locked", "dispatched"):
                emit(st, g, lp.name, "unknown", by=by, note="lease hết — không tự kết luận", op_key=f"reap:{lp.name}:{lk['gen']}")
                lp.unlink(); n_exp += 1
    return n_exp


def emit(st: Store, g: dict, nid: str, to: str, by="", note="", op_key="", gen=None, if_rev=None, plan_version=None) -> bool:
    nodes = {n["id"]: n for n in g["nodes"]}
    n = nodes[nid]
    if to not in STATES:
        raise SystemExit(f"state lạ: {to} (hợp lệ: {STATES})")
    op_key = op_key or f"{nid}:{to}:{int(time.time()*1000)}"
    if any(e.get("op_key") == op_key for e in read_jsonl(st.events_p)):
        print(f"no-op: op_key {op_key} đã có"); return False
    if if_rev is not None and n["rev"] != if_rev:
        raise SystemExit(f"CAS: rev hiện tại {n['rev']} ≠ --if-rev {if_rev}")
    if to in TERMINAL_OK or to == "done_unverified":
        if plan_version is not None and plan_version != g.get("plan_version", 1):
            append_jsonl(st.events_p, {"ts": now(), "kind": "stale_result", "node": nid, "plan_version": plan_version, "cur_plan_version": g.get("plan_version", 1), "by": by})
            print(f"STALE: kết quả plan_version {plan_version} ≠ hiện tại {g.get('plan_version', 1)} — không publish (invariant 2)"); return False
        if gen is not None and gen != n["gen"]:
            append_jsonl(st.events_p, {"ts": now(), "kind": "stale_result", "node": nid, "gen": gen, "cur_gen": n["gen"], "by": by})
            print(f"STALE: kết quả gen {gen} ≠ gen hiện tại {n['gen']} — không publish"); return False
        if to == "done" and n.get("verify") and by != "reconcile":
            rc = subprocess.call(n["verify"], shell=True)
            if rc != 0:
                to = "done_unverified"; note = (note + f" verify rc={rc}").strip()
        if to == "done" and not n.get("verify"):
            to = "done_unverified"; note = (note + " (không có verify)").strip()
    new_gen = n["gen"] + 1 if to == "dispatched" else n["gen"]
    frm, rev0 = n["state"], n["rev"]
    ev = {"ts": now(), "node": nid, "from": frm, "to": to, "by": by, "op_key": op_key, "gen": new_gen, "rev": n["rev"] + 1, "note": note,
          "spec_hash": n.get("spec_hash"), "plan_version": g.get("plan_version", 1)}
    append_jsonl(st.events_p, ev)
    st.save(fold(g, read_jsonl(st.events_p), st.d))
    print(f"{nid}: {frm} → {to} (gen {new_gen}, rev {rev0+1})")
    return True


def cmd_next(a):
    st = Store(Path(a.dir), a.id); g = st.load()
    k = reaper(st, g)
    if k:
        g = st.load(); print(f"reaper: {k} node hết lease → unknown")
    if g.get("control", "active") != "active":
        print(f"control={g['control']} — không cấp node mới" + (" (còn node đang chạy, chờ chúng kết thúc)" if g["control"].endswith("_requested") else "")); return
    rn = [n for n in g["nodes"] if n["state"] == "ready"]
    hitl = [n["id"] for n in g["nodes"] if n["state"] == "blocked"]
    print("ready (chạy song song ngay): " + (" ∥ ".join(n["id"] for n in rn) or "(không có)"))
    if hitl:
        print(f"blocked (HITL — cần người, KHÔNG dispatch headless): {hitl}")
    left = [n["id"] for n in g["nodes"] if n["state"] not in TERMINAL_OK]
    if not left:
        print("✅ graph hoàn tất")


def cmd_lock(a):
    st = Store(Path(a.dir), a.id); g = st.load()
    nodes = {n["id"]: n for n in g["nodes"]}
    n = nodes[a.node]
    if n["state"] not in ("ready", "unknown", "failed"):
        raise SystemExit(f"{a.node} đang {n['state']} — chỉ lock node ready/unknown/failed")
    if g.get("control", "active") != "active":
        raise SystemExit(f"control={g['control']} — không lock (resume trước)")
    running = sum(1 for x in g["nodes"] if x["state"] in ("locked", "dispatched"))
    if running >= g.get("max_parallel", 4):
        raise SystemExit(f"max_parallel={g.get('max_parallel', 4)} đã đầy ({running} node đang chạy) — chờ node xong (PRD §12.1)")
    if n["attempts"] >= a.max_attempts and n["state"] != "ready":
        raise SystemExit(f"{a.node} đã {n['attempts']} attempt ≥ {a.max_attempts} — dừng retry")
    st.locks_d.mkdir(parents=True, exist_ok=True)
    lp = st.locks_d / a.node
    try:
        fd = os.open(lp, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise SystemExit(f"{a.node} đã bị khoá: {lp.read_text()}")
    with os.fdopen(fd, "w") as f:
        json.dump({"gen": n["gen"] + 1, "lease_until": time.time() + a.lease_sec, "by": a.by}, f); f.flush(); os.fsync(f.fileno())
    emit(st, g, a.node, "locked", by=a.by, note=f"lease {a.lease_sec}s", op_key=a.op_key)


def cmd_unlock(a):
    st = Store(Path(a.dir), a.id)
    lp = st.locks_d / a.node
    if lp.exists():
        lp.unlink(); print(f"unlock {a.node}")
    else:
        print("không có lock")


def cmd_heartbeat(a):
    st = Store(Path(a.dir), a.id)
    lp = st.locks_d / a.node
    if not lp.exists():
        raise SystemExit("không có lock để gia hạn")
    lk = json.loads(lp.read_text()); lk["lease_until"] = time.time() + a.lease_sec
    atomic_write(lp, json.dumps(lk)); print(f"heartbeat {a.node} → +{a.lease_sec}s")


def cmd_set(a):
    st = Store(Path(a.dir), a.id); g = st.load()
    ok = emit(st, g, a.node, a.state, by=a.by, note=a.note, op_key=a.op_key, gen=a.gen, if_rev=a.if_rev, plan_version=a.plan_version)
    if ok and a.state in TERMINAL_OK | {"failed", "done_unverified"}:
        cmd_unlock(a)


def cmd_reconcile(a):
    st = Store(Path(a.dir), a.id); g = st.load()
    n = {x["id"]: x for x in g["nodes"]}[a.node]
    if not n.get("verify"):
        print(f"{a.node} không có verify → không tự kết luận được; cần người: set done_user_reported hoặc ready"); return
    rc = subprocess.call(n["verify"], shell=True)
    to = "done" if rc == 0 else "ready"
    emit(st, g, a.node, to, by="reconcile", note=f"verify rc={rc}", op_key=f"reconcile:{a.node}:{n['gen']}:{rc}")
    if to != "done":
        cmd_unlock(a)


def cmd_sync_orca(a):
    g = Store(Path(a.dir), a.id).load()
    idmap, cmds = {}, []
    for layer in g["layers"]:
        for i in layer:
            n = {x["id"]: x for x in g["nodes"]}[i]
            deps = json.dumps([idmap.get(d, f"<{d}>") for d in n["deps"]])
            spec = f"[graph {g['id']}/{i}] {n['title']}"
            cmd = ["orca", "orchestration", "task-create", "--spec", spec, "--task-title", n["title"][:60], "--deps", deps, "--json"]
            if a.run:
                out = subprocess.run(cmd, capture_output=True, text=True)
                try:
                    idmap[i] = json.loads(out.stdout)["result"]["task"]["id"]   # result.task.id, KHÔNG envelope id
                except Exception:
                    raise SystemExit(f"task-create lỗi cho {i}: {out.stdout[:200]} {out.stderr[:200]}")
                print(f"{i} → {idmap[i]}")
            else:
                cmds.append(" ".join(json.dumps(c) if " " in c else c for c in cmd))
    if not a.run:
        print("# dry-run (thêm --run để tạo thật; sổ Orca là runtime-global — đóng dấu dự án qua orca-reconcile.py --stamp nếu có):")
        print("\n".join(cmds))


# ---------- answers + audit ----------
EV_RE = re.compile(r"^(file|event|edge|absence|cmd):(.+)$")


def cmd_answer(a):
    st = Store(Path(a.dir), a.id); st.load()
    if a.label not in LABELS:
        raise SystemExit(f"label phải là {list(LABELS)}")
    if a.label != "không-biết" and not a.evidence:
        raise SystemExit("chắc/gợi-ý BẮT BUỘC có --evidence (file:path:line | event:<op_key> | edge:<a>-><b> | absence:<lệnh>)")
    for e in a.evidence:
        if not EV_RE.match(e):
            raise SystemExit(f"evidence sai dạng: {e}")
    score = min(float(a.score), LABELS[a.label])
    append_jsonl(st.answers_p, {"ts": now(), "q": a.q, "node": a.node, "label": a.label, "self_score": score,
                                "evidence": a.evidence, "text": a.text, "by": a.by})
    print(f"ghi câu trả lời [{a.label}] tự chấm {score} · {len(a.evidence)} nguồn")


def check_evidence(e: str, st: Store, g: dict) -> bool:
    kind, body = EV_RE.match(e).groups()
    if kind == "file":
        m = re.match(r"^(.*?)(?::(\d+))?$", body)
        p = Path(m.group(1))
        if not p.exists():
            return False
        if m.group(2):
            return int(m.group(2)) <= len(p.read_text(encoding="utf-8", errors="ignore").splitlines())
        return True
    if kind == "event":
        return any(ev.get("op_key") == body or ev.get("ts") == body for ev in read_jsonl(st.events_p))
    if kind == "edge":
        m = re.match(r"^(?:([^/]+)/)?(\w+)->(\w+)$", body)
        if not m:
            return False
        gg = g if not m.group(1) or m.group(1) == g["id"] else Store(st.d, m.group(1)).load()
        nodes = {n["id"]: n for n in gg["nodes"]}
        return m.group(3) in nodes and m.group(2) in nodes[m.group(3)]["deps"]
    if kind in ("absence", "cmd"):   # lệnh đã chạy — chạy lại phải KHÔNG lỗi cú pháp (rc≠127); absence: output rỗng
        r = subprocess.run(body, shell=True, capture_output=True, text=True)
        return r.returncode != 127 and (kind == "cmd" or not r.stdout.strip())
    return False


def cmd_audit(a):
    st = Store(Path(a.dir), a.id); g = st.load()
    answers = read_jsonl(st.answers_p)
    if not answers:
        print("chưa có câu trả lời"); return
    tot_self = tot_audit = 0.0
    rows = []
    for ans in answers:
        bad = [e for e in ans["evidence"] if not check_evidence(e, st, g)]
        if ans["label"] == "không-biết":
            sc = 0.3
        elif bad:
            sc = 0.0   # bịa = 0, bất kể nhãn
        else:
            sc = ans["self_score"]
        tot_self += ans["self_score"]; tot_audit += sc
        rows.append((ans["q"], ans.get("node") or "-", ans["label"], ans["self_score"], sc, bad))
        print(f"{'BỊA ' if bad else 'OK  '} {ans['q']:<9} {ans.get('node') or '-':<5} [{ans['label']}] tự={ans['self_score']} audit={sc}" + (f"  nguồn hỏng: {bad}" if bad else ""))
    n = len(answers)
    print(f"— {n} câu · tự chấm {tot_self:.1f} · sau audit {tot_audit:.1f} · khoảng cách {tot_self - tot_audit:.1f} (lớn = bịa/tự tin quá)")
    append_jsonl(st.d / "audit-log.jsonl", {"ts": now(), "graph": g["id"], "n": n, "self": tot_self, "audit": tot_audit})


def cmd_control(a):
    st = Store(Path(a.dir), a.id); g = st.load()
    cur = g.get("control", "active")
    if a.action == "status":
        print(f"control={cur}"); return
    to = {"pause": "pause_requested", "cancel": "cancel_requested", "resume": "active"}[a.action]
    if a.action == "resume" and cur == "cancelled":
        raise SystemExit("đã cancelled — không resume; build lại plan version mới nếu muốn tiếp")
    append_jsonl(st.events_p, {"ts": now(), "kind": "control", "node": "-", "from": cur, "to": to, "by": a.by, "op_key": f"control:{to}:{int(time.time()*1000)}"})
    g = st.load(); st.save(g)
    print(f"control: {cur} → {g['control']}" + (" (yêu cầu đã nhận; workload chưa dừng)" if g["control"].endswith("_requested") else ""))


def cmd_show(a):
    g = Store(Path(a.dir), a.id).load()
    print(f"{g['id']}  plan={g['plan']}  v{g.get('plan_version',1)}  control={g.get('control','active')}  max_parallel={g.get('max_parallel',4)}  nodes={len(g['nodes'])}  layers={len(g['layers'])}  cấp={g.get('depth',0)}  superseded={[x['id'] for x in g.get('superseded',[])]}" + (f"  mẹ={g['parent']['graph']}/{g['parent']['node']}" if g.get('parent') else ""))
    for n in g["nodes"]:
        print(f"  {n['id']:<4} {n['state']:<18} gen={n['gen']} rev={n['rev']} att={n['attempts']} {n['fresh']:<7} deps={n['deps']}{' child=' + n['child_graph'] if n.get('child_graph') else ''}  {n['title'][:50]}")


# ---------- cli ----------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=str(DEFAULT_DIR))
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("build"); p.add_argument("plan"); p.add_argument("--id"); p.add_argument("--parent", help="<gid>/<node> graph mẹ"); p.add_argument("--strict", action="store_true"); p.add_argument("--max-parallel", type=int, default=4); p.set_defaults(f=cmd_build)
    p = sp.add_parser("ask"); p.add_argument("id"); p.add_argument("query", nargs="+"); p.set_defaults(f=cmd_ask)
    p = sp.add_parser("next"); p.add_argument("id"); p.set_defaults(f=cmd_next)
    for name, fn in (("lock", cmd_lock), ("unlock", cmd_unlock), ("heartbeat", cmd_heartbeat), ("reconcile", cmd_reconcile)):
        p = sp.add_parser(name); p.add_argument("id"); p.add_argument("node"); p.add_argument("--by", default=os.environ.get("USER", "agent"))
        p.add_argument("--lease-sec", type=int, default=5400); p.add_argument("--max-attempts", type=int, default=3); p.add_argument("--op-key", default="")
        p.set_defaults(f=fn)
    p = sp.add_parser("set"); p.add_argument("id"); p.add_argument("node"); p.add_argument("state")
    p.add_argument("--op-key", default=""); p.add_argument("--gen", type=int); p.add_argument("--if-rev", type=int); p.add_argument("--plan-version", type=int)
    p.add_argument("--note", default=""); p.add_argument("--by", default=os.environ.get("USER", "agent")); p.set_defaults(f=cmd_set)
    p = sp.add_parser("sync-orca"); p.add_argument("id"); p.add_argument("--run", action="store_true"); p.set_defaults(f=cmd_sync_orca)
    p = sp.add_parser("answer"); p.add_argument("id"); p.add_argument("node"); p.add_argument("--q", required=True, choices=["needs", "parallel", "deps", "why", "related"])
    p.add_argument("--label", required=True); p.add_argument("--score", default="1"); p.add_argument("--evidence", nargs="*", default=[])
    p.add_argument("--text", required=True); p.add_argument("--by", default="model"); p.set_defaults(f=cmd_answer)
    p = sp.add_parser("audit"); p.add_argument("id"); p.set_defaults(f=cmd_audit)
    p = sp.add_parser("check-cycles"); p.add_argument("cdir", nargs="?"); p.set_defaults(f=lambda a: (setattr(a, "dir", a.cdir or a.dir), cmd_check_cycles(a)))
    p = sp.add_parser("show"); p.add_argument("id"); p.set_defaults(f=cmd_show)
    p = sp.add_parser("lint"); p.add_argument("id"); p.set_defaults(f=cmd_lint)
    p = sp.add_parser("control"); p.add_argument("id"); p.add_argument("action", choices=["pause", "resume", "cancel", "status"]); p.add_argument("--by", default=os.environ.get("USER", "agent")); p.set_defaults(f=cmd_control)
    a = ap.parse_args(argv)
    if getattr(a, "node", None) == "-":
        a.node = None
    a.f(a)


if __name__ == "__main__":
    main()
