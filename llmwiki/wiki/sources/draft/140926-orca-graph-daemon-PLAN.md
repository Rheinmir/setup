---
type: draft
title: "orca-graph daemon — run wrapper heartbeat, watch toàn máy + registry, control-room data-first — PLAN thi hành"
status: proposed
tags: [plan, orca-graph, daemon, heartbeat, control-room]
timestamp: 2026-09-14
---

# orca-graph daemon — PLAN thi hành

**Goal:** phát hiện agent chết trong giây (không đợi lease 90 phút), một daemon cho cả máy không tỉ lệ với số dự án mở, và một trang đầu tiên mở ra trả lời: đang chạy gì, cái gì kẹt, hệ khoẻ không, hôm nay tốn bao nhiêu.

## Origin
User duyệt 2026-09-14 sau thảo luận: bảng sống/chết + daemon gác (PRD Reprise Graph Engine §8.4: lease 60 s, heartbeat 15 s, reaper 15 s); lo ngại resource khi mở n dự án → một daemon toàn máy đọc registry, chi phí tỉ lệ số node đang chạy (đo: 1 lượt fold 3 graph/22 node = 84 ms kể cả khởi động Python); giao diện data-first bậc 1 = trang tĩnh daemon regen.

## Global constraints
- Stdlib only. Không server HTTP (bậc 2, chưa làm). Không sửa format `events.jsonl`.
- Thư mục nhà của daemon: `$ORCA_GRAPH_HOME` (mặc định `~/.orca-graph/`), test đặt biến này vào tmp.
- Node không có `verify` thì `run` từ chối headless (trừ `--allow-unverified`).
- Sau MỖI task: `python3 harness/tests/test_orca_graph.py` xanh.

## File structure
- Sửa `harness/scripts/orca-graph.py` — `run`, `watch`, registry, daemon lock.
- Tạo `fdk/tools/build-control-room.py` — trang `llmwiki/html/control-room.html`.
- Sửa `harness/tests/test_orca_graph.py`, `skills/orca-graph/SKILL.md`.

### Task 1: `run` wrapper — lock ngắn, heartbeat theo pid, tự set done/failed

**Files:**
- Sửa: `harness/scripts/orca-graph.py`
- Test: `harness/tests/test_orca_graph.py`

**Interfaces:**
- Consumes: `cmd_lock`, `emit`, `Store`.
- Produces: `run <id> <node> [--hb 15] [--lease-sec 60] [--allow-unverified] -- <cmd...>`: lock → dispatched → `subprocess.Popen(cmd)` → mỗi `hb` giây ghi `lease_until` mới vào lockfile → exit 0 → `set done --gen` (verify chạy trong emit) · exit ≠ 0 → `failed`; `registry_add(dir)` khi bắt đầu, `registry_prune()` khi graph hết node chạy. Registry: `$ORCA_GRAPH_HOME/registry.json` = `{"dirs": [...]}`.

**Depends:** —

- [ ] **Step 1: test fail**

```python
def test_run_wrapper(tmp_path, monkeypatch=None):
    gid = setup(tmp_path); home = tmp_path / "home"
    env = dict(os.environ, ORCA_GRAPH_HOME=str(home), ORCA_GRAPH_NO_DAEMON="1")
    r = subprocess.run([sys.executable, str(SCRIPT), "--dir", str(tmp_path), "run", gid, "t1", "--hb", "0.2", "--", "sh", "-c", "sleep 0.5"], capture_output=True, text=True, cwd=ROOT, env=env)
    assert r.returncode == 0 and "→ done" in r.stdout, r.stdout + r.stderr          # verify=true
    reg = json.loads((home / "registry.json").read_text()); assert str(tmp_path.resolve()) not in reg["dirs"]   # hết node chạy → prune
    r = subprocess.run([sys.executable, str(SCRIPT), "--dir", str(tmp_path), "run", gid, "t3", "--", "false"], capture_output=True, text=True, cwd=ROOT, env=env)
    assert r.returncode != 0 and "không có verify" in r.stderr                        # t3 không verify → từ chối headless
    r = subprocess.run([sys.executable, str(SCRIPT), "--dir", str(tmp_path), "run", gid, "t3", "--allow-unverified", "--", "false"], capture_output=True, text=True, cwd=ROOT, env=env)
    assert "→ failed" in r.stdout
```

- [ ] **Step 2: fail** — `invalid choice: 'run'`.
- [ ] **Step 3: code** — `home()`, `registry_add/prune`, `cmd_run` (Popen, vòng `while p.poll() is None: heartbeat; sleep hb`), lease mặc định 60 s khi qua `run`.
- [ ] **Step 4: xanh.**

**Verify:** `python3 harness/tests/test_orca_graph.py 2>&1 | grep -q 'ok test_run_wrapper'`

### Task 2: `watch` daemon toàn máy — registry, reaper, reconcile, lock pid, tự thoát khi rảnh

**Files:**
- Sửa: `harness/scripts/orca-graph.py`
- Test: `harness/tests/test_orca_graph.py`

**Interfaces:**
- Consumes: Task 1 registry; `reaper`, `cmd_reconcile`.
- Produces: `watch [--once] [--interval 15] [--idle-sec 600]`: lock `$HOME/daemon.lock` (pid; pid chết → chiếm lại); mỗi lượt: với mỗi dir trong registry → reaper → node `unknown` có verify → reconcile → prune; in bảng `dir · node · state · lease còn`; registry rỗng quá `idle-sec` → thoát; `--once` chạy một lượt rồi thoát (test). `run` tự spawn `watch` nền nếu không có daemon sống (tắt bằng `ORCA_GRAPH_NO_DAEMON=1`).

**Depends:** Task 1

- [ ] **Step 1: test fail**

```python
def test_watch_once(tmp_path):
    gid = setup(tmp_path); home = tmp_path / "home"; home.mkdir()
    (home / "registry.json").write_text(json.dumps({"dirs": [str(tmp_path.resolve())]}))
    env = dict(os.environ, ORCA_GRAPH_HOME=str(home))
    run(tmp_path, "lock", gid, "t1", "--lease-sec", "1"); run(tmp_path, "set", gid, "t1", "dispatched", "--op-key", "k"); time.sleep(1.2)
    r = subprocess.run([sys.executable, str(SCRIPT), "watch", "--once"], capture_output=True, text=True, cwd=ROOT, env=env)
    assert r.returncode == 0 and "t1" in r.stdout and "reconcile" in r.stdout, r.stdout + r.stderr
    g = json.loads((tmp_path / f"{gid}.graph.json").read_text()); assert {n["id"]: n["state"] for n in g["nodes"]}["t1"] == "done"   # lease hết → unknown → verify=true → done
    assert not (home / "daemon.lock").exists()                                     # --once thả lock
```

- [ ] **Step 2: fail** — `invalid choice: 'watch'`.
- [ ] **Step 3: code** — `daemon_lock()`, `cmd_watch`, `spawn_daemon()` gọi từ `cmd_run`.
- [ ] **Step 4: xanh.**

**Verify:** `python3 harness/tests/test_orca_graph.py 2>&1 | grep -q 'ok test_watch_once'`

### Task 3: control-room bậc 1 — trang tĩnh data-first, daemon regen

**Files:**
- Tạo: `fdk/tools/build-control-room.py`
- Sửa: `harness/scripts/orca-graph.py` (watch gọi build khi có thay đổi)
- Sửa: `skills/orca-graph/SKILL.md`
- Test: `harness/tests/test_orca_graph.py`

**Interfaces:**
- Consumes: registry + `*.graph.json` (Task 1–2), `llmwiki/html/fdk-problem-tree.html#tree-data`, `harness/metrics/tokens.jsonl`, `llmwiki/graph/audit-log.jsonl`, theme `graph-viz.page()`.
- Produces: `build-control-room.py [--dirs d1 d2] [-o out.html]` → 4 khối: (1) node đang chạy toàn máy (graph, node, state, lease còn, gen) + trần toàn máy; (2) tiến độ từng graph (thanh SVG done/total, node kẹt `unknown|failed|blocked`); (3) nợ mở từ problem-tree (status ≠ solved, mới nhất trước); (4) chi phí hôm nay từ tokens.jsonl + khoảng cách tự chấm/audit. `<meta http-equiv="refresh" content="15">`, toggle sáng/tối, full path.

**Depends:** Task 2

- [ ] **Step 1: test fail**

```python
def test_control_room(tmp_path):
    gid = setup(tmp_path); run(tmp_path, "lock", gid, "t1"); run(tmp_path, "set", gid, "t1", "dispatched", "--op-key", "k")
    out = tmp_path / "control-room.html"
    r = subprocess.run([sys.executable, str(ROOT / "fdk/tools/build-control-room.py"), "--dirs", str(tmp_path), "-o", str(out)], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr
    h = out.read_text(encoding="utf-8")
    assert "theme-switch" in h and 'class="path"' in h and 'http-equiv="refresh"' in h and ">t1<" in h and "dispatched" in h
```

- [ ] **Step 2: fail** — file không tồn tại.
- [ ] **Step 3: code** — build-control-room.py import graph-viz như atlas; `cmd_watch` gọi build khi bất kỳ graph đổi checksum.
- [ ] **Step 4: xanh** + SKILL.md thêm mục "Daemon & control-room".

**Verify:** `python3 harness/tests/test_orca_graph.py 2>&1 | grep -q 'ok test_control_room'`
