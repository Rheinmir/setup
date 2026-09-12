"""test_orca_graph — cycle · ready-set · lease→unknown · op_key idempotent · gen stale bị chặn ·
kill -9 giữa lúc ghi không hỏng sổ (Reprise PRD bất biến 6) · audit bịa=0 · render graph-viz.py + graph-atlas.py."""
import importlib.util, json, os, signal, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "harness/scripts/orca-graph.py"
_spec = importlib.util.spec_from_file_location("og", SCRIPT)
og = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(og)

PLAN = """# X
### Task 1: A
**Files:**
- Tạo: `a.py`
**Interfaces:**
- Consumes: —
- Produces (dùng bởi Task 2): `fa()`
**Verify:** `true`
### Task 2: B
**Files:**
- Sửa: `b.py`
**Interfaces:**
- Consumes: `fa()` (Task 1 Produces)
- Produces: `fb()`
**Depends:** Task 1
**Verify:** `false`
### Task 3: C
**Files:**
- Sửa: `a.py`
**Interfaces:**
- Consumes: —
- Produces: —
"""


def run(d, *args):
    return subprocess.run([sys.executable, str(SCRIPT), "--dir", str(d), *args], capture_output=True, text=True, cwd=ROOT)


def setup(tmp_path):
    p = tmp_path / "x-PLAN.md"; p.write_text(PLAN, encoding="utf-8")
    r = run(tmp_path, "build", str(p)); assert r.returncode == 0, r.stderr
    return "x"


def test_build_layers_and_conflict(tmp_path):
    gid = setup(tmp_path)
    g = json.loads((tmp_path / f"{gid}.graph.json").read_text())
    assert g["layers"] == [["t1", "t3"], ["t2"]]
    assert g["conflicts"] == [{"a": "t1", "b": "t3", "files": ["a.py"]}]
    assert {n["id"]: n["state"] for n in g["nodes"]} == {"t1": "ready", "t2": "proposed", "t3": "ready"}
    assert {n["id"]: n["deps_conf"] for n in g["nodes"]}["t2"] == "chắc"


def test_cycle_detected():
    nodes = {"a": {"deps": ["b"]}, "b": {"deps": ["a"]}}
    try:
        og.toposort(nodes); assert False
    except SystemExit as e:
        assert "CYCLE" in str(e)


def test_opkey_idempotent_and_gen_stale(tmp_path):
    gid = setup(tmp_path)
    assert run(tmp_path, "lock", gid, "t1", "--by", "x").returncode == 0
    assert run(tmp_path, "set", gid, "t1", "dispatched", "--op-key", "k1").returncode == 0
    r = run(tmp_path, "set", gid, "t1", "dispatched", "--op-key", "k1"); assert "no-op" in r.stdout
    r = run(tmp_path, "set", gid, "t1", "done", "--gen", "0"); assert "STALE" in r.stdout
    r = run(tmp_path, "set", gid, "t1", "done", "--gen", "1"); assert "→ done" in r.stdout
    g = json.loads((tmp_path / f"{gid}.graph.json").read_text())
    n = {x["id"]: x for x in g["nodes"]}
    assert n["t1"]["state"] == "done" and n["t1"]["attempts"] == 1 and n["t1"]["gen"] == 1
    assert n["t2"]["state"] == "ready"           # deps xong → mở khoá
    # verify fail → done_unverified, không phải done
    run(tmp_path, "lock", gid, "t2"); run(tmp_path, "set", gid, "t2", "dispatched", "--op-key", "k2")
    r = run(tmp_path, "set", gid, "t2", "done", "--gen", "1"); assert "done_unverified" in r.stdout


def test_cas_if_rev(tmp_path):
    gid = setup(tmp_path)
    r = run(tmp_path, "set", gid, "t3", "failed", "--if-rev", "9"); assert r.returncode != 0 and "CAS" in r.stderr


def test_lease_expired_to_unknown(tmp_path):
    gid = setup(tmp_path)
    run(tmp_path, "lock", gid, "t1", "--lease-sec", "1"); run(tmp_path, "set", gid, "t1", "dispatched", "--op-key", "k")
    time.sleep(1.2)
    r = run(tmp_path, "next", gid); assert "unknown" in r.stdout
    r = run(tmp_path, "reconcile", gid, "t1"); assert "→ done" in r.stdout   # verify=true


def test_kill9_mid_write_keeps_ledger(tmp_path):
    gid = setup(tmp_path)
    ev = tmp_path / f"{gid}.events.jsonl"
    child = subprocess.Popen([sys.executable, "-c", f"""
import json,time
f=open({str(ev)!r},'a')
for i in range(100000):
    f.write(json.dumps({{'ts':'t','node':'t3','from':'ready','to':'failed','op_key':'w%d'%i,'gen':0,'rev':i+1}})+'\\n'); f.flush()
"""])
    time.sleep(0.3); os.kill(child.pid, signal.SIGKILL); child.wait()
    r = run(tmp_path, "show", gid); assert r.returncode == 0, r.stderr   # dòng cuối cụt được bỏ, sổ vẫn đọc được
    assert "t3   failed" in r.stdout


def test_audit_fabricated_is_zero(tmp_path):
    gid = setup(tmp_path)
    run(tmp_path, "answer", gid, "t2", "--q", "deps", "--label", "chắc", "--evidence", "edge:t1->t2", "--text", "ok")
    run(tmp_path, "answer", gid, "t2", "--q", "why", "--label", "gợi-ý", "--evidence", "file:khong/co.py", "--text", "bịa")
    run(tmp_path, "answer", gid, "-", "--q", "related", "--label", "không-biết", "--text", "?")
    r = run(tmp_path, "answer", gid, "t2", "--q", "why", "--label", "chắc", "--text", "không nguồn"); assert r.returncode != 0
    r = run(tmp_path, "audit", gid)
    assert "BỊA" in r.stdout and "sau audit 1.3" in r.stdout


def test_render_viz_and_atlas(tmp_path):
    gid = setup(tmp_path)
    viz = ROOT / "fdk/tools/graph-viz.py"; atlas = ROOT / "fdk/tools/graph-atlas.py"
    r = subprocess.run([sys.executable, str(viz), str(tmp_path / f"{gid}.graph.json")], capture_output=True, text=True, cwd=ROOT); assert r.returncode == 0, r.stderr
    h = (tmp_path / f"{gid}.graph.html").read_text(encoding="utf-8")
    assert "theme-switch" in h and 'class="path"' in h and h.count('class="node"') == 3
    r = subprocess.run([sys.executable, str(atlas), str(tmp_path)], capture_output=True, text=True, cwd=ROOT); assert r.returncode == 0, r.stderr
    assert "Atlas" in (tmp_path / "atlas.html").read_text(encoding="utf-8")
    child = tmp_path / "c-PLAN.md"; child.write_text(PLAN, encoding="utf-8"); run(tmp_path, "build", str(child), "--parent", f"{gid}/t3")
    r = subprocess.run([sys.executable, str(atlas), str(tmp_path)], capture_output=True, text=True, cwd=ROOT); assert r.returncode == 0, r.stderr
    h = (tmp_path / "atlas.html").read_text(encoding="utf-8"); assert 'class="wire contain"' in h and "cấp 1" in h


def test_hierarchy_join(tmp_path):
    gid = setup(tmp_path)                                   # graph mẹ x: t1,t2,t3
    child = tmp_path / "c-PLAN.md"; child.write_text(PLAN.replace("Task 3", "Task 9"), encoding="utf-8")
    r = run(tmp_path, "build", str(child), "--parent", f"{gid}/t3"); assert r.returncode == 0, r.stderr
    g = json.loads((tmp_path / "c.graph.json").read_text()); assert g["parent"] == {"graph": gid, "node": "t3"} and g["depth"] == 1
    r = run(tmp_path, "show", gid); assert "child=c" in r.stdout
    for n in ("t1", "t2", "t9"):                            # xong hết con → mẹ t3 join
        run(tmp_path, "lock", "c", n); run(tmp_path, "set", "c", n, "dispatched", "--op-key", "k"+n); run(tmp_path, "set", "c", n, "done_user_reported", "--op-key", "d"+n)
    r = run(tmp_path, "show", gid); assert "t3   done_unverified" in r.stdout, r.stdout


def test_cross_graph_cycle_path(tmp_path):
    a = tmp_path / "a-PLAN.md"; a.write_text(PLAN.replace("**Depends:** Task 1", "**Depends:** Task 1, b/t3"), encoding="utf-8")
    b = tmp_path / "b-PLAN.md"; b.write_text(PLAN.replace("- Produces: —\n", "- Produces: —\n**Depends:** a/t2\n"), encoding="utf-8")
    assert run(tmp_path, "build", str(a)).returncode == 0 and run(tmp_path, "build", str(b)).returncode == 0
    r = run(tmp_path, "check-cycles"); assert r.returncode == 2 and "a/t2 → b/t3 → a/t2" in r.stdout, r.stdout   # ĐƯỜNG cycle cụ thể
    b.write_text(PLAN, encoding="utf-8"); run(tmp_path, "build", str(b))
    assert run(tmp_path, "check-cycles").returncode == 0
    g = json.loads((tmp_path / "a.graph.json").read_text()); assert {n["id"]: n["state"] for n in g["nodes"]}["t2"] == "proposed"  # chờ b/t3
    for n in ("t1", "t3"): run(tmp_path, "lock", "b", n); run(tmp_path, "set", "b", n, "done_user_reported", "--op-key", "b"+n)
    run(tmp_path, "lock", "a", "t1"); run(tmp_path, "set", "a", "t1", "done_user_reported", "--op-key", "a1")
    r = run(tmp_path, "show", "a"); assert "t2   ready" in r.stdout, r.stdout                 # dep ngoài đã thoả


def test_lint_leaf_contract(tmp_path):
    gid = setup(tmp_path)
    r = run(tmp_path, "lint", gid); assert r.returncode == 0
    assert "t3" in r.stdout and "verify" in r.stdout and "produces" in r.stdout   # t3 thiếu verify + produces
    assert "2/3 leaf đủ hợp đồng" in r.stdout, r.stdout
    r = run(tmp_path, "build", str(tmp_path / "x-PLAN.md"), "--strict"); assert r.returncode == 2


def test_plan_version_supersede(tmp_path):
    gid = setup(tmp_path); p = tmp_path / "x-PLAN.md"
    run(tmp_path, "lock", gid, "t1"); run(tmp_path, "set", gid, "t1", "dispatched", "--op-key", "k1"); run(tmp_path, "set", gid, "t1", "done", "--gen", "1", "--op-key", "d1")
    p.write_text(PLAN.replace("Task 1: A", "Task 1: A đổi tên").split("### Task 3")[0], encoding="utf-8")
    r = run(tmp_path, "build", str(p)); assert "plan_version 1 → 2" in r.stdout, r.stdout
    g = json.loads((tmp_path / f"{gid}.graph.json").read_text())
    assert g["plan_version"] == 2 and [n["id"] for n in g["superseded"]] == ["t3"]
    n = {x["id"]: x for x in g["nodes"]}; assert n["t1"]["state"] == "done" and n["t1"]["fresh"] == "stale", n["t1"]
    r = run(tmp_path, "set", gid, "t2", "done", "--plan-version", "1"); assert "STALE" in r.stdout


def test_control_and_max_parallel(tmp_path):
    gid = setup(tmp_path)
    run(tmp_path, "build", str(tmp_path / "x-PLAN.md"), "--max-parallel", "1")
    assert run(tmp_path, "lock", gid, "t1").returncode == 0
    r = run(tmp_path, "lock", gid, "t3"); assert r.returncode != 0 and "max_parallel" in r.stderr
    r = run(tmp_path, "control", gid, "pause"); assert "pause_requested" in r.stdout      # còn t1 locked → chưa paused
    r = run(tmp_path, "next", gid); assert "không cấp node mới" in r.stdout
    run(tmp_path, "set", gid, "t1", "failed", "--op-key", "f1")
    r = run(tmp_path, "control", gid, "status"); assert "control=paused" in r.stdout, r.stdout   # hết node đang chạy → paused
    run(tmp_path, "control", gid, "resume"); r = run(tmp_path, "next", gid); assert "t3" in r.stdout


if __name__ == "__main__":
    import tempfile
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            with tempfile.TemporaryDirectory() as d:
                fn(Path(d)) if fn.__code__.co_argcount else fn()
            print("ok", name)
