---
type: draft
title: "orca-graph v2 — áp Reprise Graph Engine PRD (phân cấp, cycle xuyên graph, leaf contract, plan version, control) — PLAN thi hành"
status: proposed
tags: [plan, orca-graph, graph-engine]
timestamp: 2026-09-12
---

# orca-graph v2 — PLAN thi hành

**Goal:** đưa các cơ chế của `llmwiki/raw/Reprise-Graph-Engine-Full-Cycle-PRD.md` áp dụng được cho một tool file-based vào `harness/scripts/orca-graph.py` + 2 file vẽ, rồi dùng chính orca-graph để chạy PLAN này (dogfood).

## Origin
Yêu cầu user 2026-09-12: "triển khai xong PRD thì dùng". PRD §3 (3 cấu trúc tách nhau), §4 (graph mẹ → cấp n), §5.2–5.3 (giới hạn + cycle xuyên module), §4.4 (leaf đủ tốt), §7.3/§8.1 (membership freeze, stale result), §8.3 (control state), §10 (replan không phá run), §12.1 (budget/concurrency), §16.1 (12 invariants).

## Global constraints
- Ngoài phạm vi: PostgreSQL, sandbox, secret gateway, tiền, LangGraph, integration queue, compensation (PRD §9.3, §11.4, §12.3, §13). Nói rõ trong SKILL.md.
- Không phá store cũ: graph.json schema_version tăng 1→2, tool đọc v1 và nâng cấp tại chỗ (thêm field mặc định); events.jsonl không đổi format.
- Không LLM trong kiểm quyền/DAG/lifecycle (invariant 12) — mọi thứ trong tool là tất định.
- Test: `python3 harness/tests/test_orca_graph.py` phải xanh sau MỖI task.

## File structure
- Sửa `harness/scripts/orca-graph.py` — parent/child, cross-graph deps + cycle path, lint, plan_version, control, max-parallel.
- Sửa `fdk/tools/graph-atlas.py` — trục Y = cấp chứa (depth), dây containment.
- Sửa `harness/tests/test_orca_graph.py` — test cho từng cơ chế.
- Sửa `skills/orca-graph/SKILL.md` — bước dùng + phạm vi.

### Task 1: Phân cấp graph mẹ → con (containment tree) + join

**Files:**
- Sửa: `harness/scripts/orca-graph.py`
- Test: `harness/tests/test_orca_graph.py`

**Interfaces:**
- Consumes: `Store`, `fold()`, `cmd_build()`.
- Produces: `build <PLAN> --parent <gid>/<node>` ghi `graph.parent={graph,node}` và bên graph mẹ node đó có `child_graph=<gid>`; `fold()` join: node có `child_graph` thì state = `done_unverified` khi MỌI node con ∈ TERMINAL_OK (invariant 4: thiếu 1 required → không completed), `blocked` nếu con có node `blocked`; `depth` = cấp; từ chối depth > 6 và > 20 node/graph (PRD §5.2).

**Depends:** —
- [ ] **Step 1: viết test fail** (thêm vào `harness/tests/test_orca_graph.py`)

```python
def test_hierarchy_join(tmp_path):
    gid = setup(tmp_path)                                   # graph mẹ x: t1,t2,t3
    child = tmp_path / "c-PLAN.md"; child.write_text(PLAN.replace("Task 3", "Task 9"), encoding="utf-8")
    r = run(tmp_path, "build", str(child), "--parent", f"{gid}/t3"); assert r.returncode == 0, r.stderr
    g = json.loads((tmp_path / "c.graph.json").read_text()); assert g["parent"] == {"graph": gid, "node": "t3"} and g["depth"] == 1
    r = run(tmp_path, "show", gid); assert "child=c" in r.stdout
    for n in ("t1", "t2", "t9"):                            # xong hết con → mẹ t3 join
        run(tmp_path, "lock", "c", n); run(tmp_path, "set", "c", n, "dispatched", "--op-key", "k"+n); run(tmp_path, "set", "c", n, "done_user_reported", "--op-key", "d"+n)
    r = run(tmp_path, "show", gid); assert "t3   done_unverified" in r.stdout
```

- [ ] **Step 2: chạy cho THẤY fail** — `python3 harness/tests/test_orca_graph.py` → `unrecognized arguments: --parent`.
- [ ] **Step 3: code** — `cmd_build --parent`: ghi `parent`, `depth = parent.depth+1` (>6 → SystemExit), >20 node → SystemExit; graph mẹ: node `child_graph`. `fold()`: node có `child_graph` → đọc store con, mọi node ∈ TERMINAL_OK → `done_unverified`; có `blocked` → `blocked`. `cmd_show` in `child=<gid>`.
- [ ] **Step 4: chạy test xanh.**

**Verify:** `python3 harness/tests/test_orca_graph.py 2>&1 | grep -q 'ok test_hierarchy_join'`

### Task 2: Deps xuyên graph + báo ĐƯỜNG cycle

**Files:**
- Sửa: `harness/scripts/orca-graph.py`
- Test: `harness/tests/test_orca_graph.py`

**Interfaces:**
- Consumes: Task 1 (`graph.parent`, `child_graph`).
- Produces: `**Depends:**` chấp nhận `other-graph/t3`; `toposort` coi dep ngoài là đã thoả khi node đó ∈ TERMINAL_OK ở graph kia (đọc store); `check-cycles <dir>` duyệt toàn bộ graph trong dir, in đường cycle cụ thể `a/t1 → b/t2 → a/t1` (PRD §5.3), rc 2 khi có cycle.

**Depends:** Task 1
- [ ] **Step 1: viết test fail**

```python
def test_cross_graph_cycle_path(tmp_path):
    a = tmp_path / "a-PLAN.md"; a.write_text(PLAN.replace("**Depends:** Task 1", "**Depends:** Task 1, b/t3"), encoding="utf-8")
    b = tmp_path / "b-PLAN.md"; b.write_text(PLAN.replace("- Produces: —\n", "- Produces: —\n**Depends:** a/t2\n"), encoding="utf-8")
    assert run(tmp_path, "build", str(a)).returncode == 0 and run(tmp_path, "build", str(b)).returncode == 0
    r = run(tmp_path, "check-cycles"); assert r.returncode == 2 and "a/t2 → b/t3 → a/t2" in r.stdout   # in ĐƯỜNG cycle cụ thể
    b.write_text(PLAN, encoding="utf-8"); run(tmp_path, "build", str(b))
    assert run(tmp_path, "check-cycles").returncode == 0
```

- [ ] **Step 2: fail** — `invalid choice: 'check-cycles'`.
- [ ] **Step 3: code** — `parse_plan`: dep dạng `<gid>/<tid>` giữ nguyên; `toposort` bỏ dep ngoài khỏi indeg; `fold`: dep ngoài thoả khi node đó ∈ TERMINAL_OK ở store kia (không có store → chưa thoả); `cmd_check_cycles(dir)`: gộp mọi graph thành một DAG khoá `gid/tid`, DFS in đường cycle, rc 2.
- [ ] **Step 4: xanh.**

**Verify:** `python3 harness/tests/test_orca_graph.py 2>&1 | grep -q 'ok test_cross_graph_cycle_path'`

### Task 3: Leaf contract lint (§4.4)

**Files:**
- Sửa: `harness/scripts/orca-graph.py`
- Test: `harness/tests/test_orca_graph.py`

**Interfaces:**
- Consumes: `parse_plan()`.
- Produces: `lint <id>` liệt kê từng node thiếu: outcome(title) · files(write scope) · produces(output) · verify(phép kiểm) · deps rõ (không `gợi-ý`); in `N/M leaf đủ hợp đồng`; `build --strict` rc 2 nếu có node thiếu verify hoặc files.

**Depends:** Task 2
- [ ] **Step 1: viết test fail**

```python
def test_lint_leaf_contract(tmp_path):
    gid = setup(tmp_path)
    r = run(tmp_path, "lint", gid); assert r.returncode == 0
    assert "t3" in r.stdout and "verify" in r.stdout and "produces" in r.stdout   # t3 thiếu verify + produces
    assert "leaf đủ hợp đồng" in r.stdout
    r = run(tmp_path, "build", str(tmp_path / "x-PLAN.md"), "--strict"); assert r.returncode == 2
```

- [ ] **Step 2: fail** — `invalid choice: 'lint'`.
- [ ] **Step 3: code** — `leaf_gaps(node) -> list[str]` kiểm title/files/produces/verify/deps_conf; `cmd_lint`; `build --strict` rc 2 nếu thiếu files hoặc verify.
- [ ] **Step 4: xanh.**

**Verify:** `python3 harness/tests/test_orca_graph.py 2>&1 | grep -q 'ok test_lint_leaf_contract'`

### Task 4: plan_version + spec_hash + supersede khi rebuild (§10.1, §7.3)

**Files:**
- Sửa: `harness/scripts/orca-graph.py`
- Test: `harness/tests/test_orca_graph.py`

**Interfaces:**
- Consumes: `cmd_build()`, `fold()`.
- Produces: mỗi node có `spec_hash` (sha256 của title+files+deps+verify+produces); `build` lại trên graph đã có → `plan_version += 1`, ghi event graph-level `plan.rebuilt {from,to,changed[],removed[]}`; node đã terminal mà spec_hash đổi → `fresh=stale` + note; node bị bỏ khỏi PLAN → giữ trong `superseded[]` (không xoá lịch sử, invariant 10); `set done --plan-version N` với N ≠ hiện tại → STALE không publish (invariant 2).

**Depends:** Task 3
- [ ] **Step 1: viết test fail**

```python
def test_plan_version_supersede(tmp_path):
    gid = setup(tmp_path); p = tmp_path / "x-PLAN.md"
    run(tmp_path, "lock", gid, "t1"); run(tmp_path, "set", gid, "t1", "dispatched", "--op-key", "k1"); run(tmp_path, "set", gid, "t1", "done", "--gen", "1", "--op-key", "d1")
    p.write_text(PLAN.replace("Task 1: A", "Task 1: A đổi tên").split("### Task 3")[0], encoding="utf-8")
    r = run(tmp_path, "build", str(p)); assert "plan_version 1 → 2" in r.stdout
    g = json.loads((tmp_path / f"{gid}.graph.json").read_text())
    assert g["plan_version"] == 2 and [n["id"] for n in g["superseded"]] == ["t3"]
    n = {x["id"]: x for x in g["nodes"]}; assert n["t1"]["state"] == "done" and n["t1"]["fresh"] == "stale"
    r = run(tmp_path, "set", gid, "t2", "done", "--plan-version", "1"); assert "STALE" in r.stdout
```

- [ ] **Step 2: fail** — `KeyError: 'plan_version'`.
- [ ] **Step 3: code** — `spec_hash(node)`; `cmd_build`: graph cũ tồn tại → so nodes, `plan_version+1`, `superseded += removed (kèm state cuối)`, event graph-level `plan.rebuilt`; `fold`: node terminal mà `spec_hash` ≠ `done_spec_hash` (lưu trong event done) → `fresh=stale`; `set --plan-version N` ≠ hiện tại → STALE.
- [ ] **Step 4: xanh.**

**Verify:** `python3 harness/tests/test_orca_graph.py 2>&1 | grep -q 'ok test_plan_version_supersede'`

### Task 5: Control state (pause/resume/cancel) + max-parallel (§8.3, §12.1)

**Files:**
- Sửa: `harness/scripts/orca-graph.py`
- Test: `harness/tests/test_orca_graph.py`

**Interfaces:**
- Consumes: `cmd_next()`, `cmd_lock()`.
- Produces: `control <id> pause|resume|cancel` → graph.control ∈ {active, pause_requested, paused, cancel_requested, cancelled}; `next` khi không active in "control=… — không cấp node mới" và rỗng; `paused/cancelled` chỉ khi không còn node `locked|dispatched` (invariant 11: yêu cầu ≠ đã dừng); `lock` từ chối khi số node `locked+dispatched` ≥ `max_parallel` (mặc định 4, `build --max-parallel N`).

**Depends:** Task 4
- [ ] **Step 1: viết test fail**

```python
def test_control_and_max_parallel(tmp_path):
    gid = setup(tmp_path)
    run(tmp_path, "build", str(tmp_path / "x-PLAN.md"), "--max-parallel", "1")
    assert run(tmp_path, "lock", gid, "t1").returncode == 0
    r = run(tmp_path, "lock", gid, "t3"); assert r.returncode != 0 and "max_parallel" in r.stderr
    r = run(tmp_path, "control", gid, "pause"); assert "pause_requested" in r.stdout      # còn t1 locked → chưa paused
    r = run(tmp_path, "next", gid); assert "không cấp node mới" in r.stdout
    run(tmp_path, "set", gid, "t1", "failed", "--op-key", "f1")
    r = run(tmp_path, "control", gid, "status"); assert "paused" in r.stdout              # hết node đang chạy → paused
    run(tmp_path, "control", gid, "resume"); r = run(tmp_path, "next", gid); assert "t3" in r.stdout
```

- [ ] **Step 2: fail** — `invalid choice: 'control'`.
- [ ] **Step 3: code** — graph.control (+ event node "-"); `cmd_control`; `cmd_next` kiểm control (pause_requested → paused khi không còn locked/dispatched; cancel_requested → cancelled tương tự); `cmd_lock` đếm locked+dispatched ≥ max_parallel → SystemExit.
- [ ] **Step 4: xanh.**

**Verify:** `python3 harness/tests/test_orca_graph.py 2>&1 | grep -q 'ok test_control_and_max_parallel'`

### Task 6: Atlas theo cấp chứa

**Files:**
- Sửa: `fdk/tools/graph-atlas.py`

**Interfaces:**
- Consumes: `graph.parent` (Task 1).
- Produces: trục Y = depth (graph mẹ hàng 0, con hàng 1…), trong hàng sắp theo thời gian; dây containment liền nét (mẹ→con) khác dây liên hệ file (đứt); tile ghi `cấp N`.

**Depends:** Task 1
- [ ] **Step 1: mở rộng test render** (đã có `test_render_viz_and_atlas`)

```python
    # thêm vào cuối test_render_viz_and_atlas:
    child = tmp_path / "c-PLAN.md"; child.write_text(PLAN, encoding="utf-8"); run(tmp_path, "build", str(child), "--parent", f"{gid}/t3")
    r = subprocess.run([sys.executable, str(atlas), str(tmp_path)], capture_output=True, text=True, cwd=ROOT); assert r.returncode == 0, r.stderr
    h = (tmp_path / "atlas.html").read_text(encoding="utf-8"); assert 'class="wire contain"' in h and "cấp 1" in h
```

- [ ] **Step 2: fail** — `AssertionError` (chưa có `wire contain`).
- [ ] **Step 3: code** — `graph-atlas.py`: `depth = g.get("depth", 0)`; y = depth; dây `contain` liền nét mẹ→con; tile ghi `cấp N`.
- [ ] **Step 4: xanh.**

**Verify:** `python3 harness/tests/test_orca_graph.py 2>&1 | grep -q 'ok test_render_viz_and_atlas'`

### Task 7: SKILL.md + docs

**Files:**
- Sửa: `skills/orca-graph/SKILL.md`

**Interfaces:**
- Consumes: mọi lệnh mới của Task 1–6.
- Produces: mục "Phân cấp", "Replan", "Control", "Ngoài phạm vi PRD" trong SKILL.md; mirror sync.

**Depends:** Task 5, Task 6
- [ ] **Step 1: sửa SKILL.md** — thêm các mục (khối dưới là nội dung phải xuất hiện):

```markdown
## Phân cấp (PRD §4): `build <PLAN> --parent <gid>/<node>` · depth ≤ 6 · ≤ 20 node/graph · node mẹ join khi MỌI node con xong
## Replan (PRD §10): `build` lại = plan_version+1, node bỏ đi vào `superseded`, node đổi spec → stale; `set done --plan-version`
## Control (PRD §8.3): `control <id> pause|resume|cancel|status` — yêu cầu ≠ đã dừng; `build --max-parallel N`
## Cycle xuyên graph (PRD §5.3): `check-cycles <dir>` in đường cycle cụ thể
## Ngoài phạm vi PRD: DB, sandbox, secret gateway, tiền, LangGraph, integration queue, compensation
```

- [ ] **Step 2: sync** — `bash fdk/tools/sync-skill.sh orca-graph`.

**Verify:** `bash fdk/tools/sync-skill.sh orca-graph >/dev/null && grep -q 'check-cycles' skills/orca-graph/SKILL.md`
