---
type: draft
title: orca-graph-write-sandbox-qc-gate-PLAN
status: done
tags: [orca-graph, sandbox, qc, write-paths]
timestamp: 2026-09-17
task: T-260917-01
---

# 170926-orca-graph-write-sandbox-qc-gate

Kéo GH#162 + GH#163 vào orca-graph, cài đặt thật. Cả 2 task cùng chạm `harness/scripts/orca-graph.py`
nên Task 2 phụ thuộc Task 1 (tuần tự, tránh xung đột ghi song song).

## Global constraints
- Không xoá/sửa tay `events.jsonl` — sai thì append event sửa (luật SKILL.md orca-graph).
- Không hardcode CLI/hạ tầng ngoài phạm vi PRD Reprise — chỉ vay LUẬT state, không vay hạ tầng (ADR-018).
- Mọi gate mới phải là CHECKPOINT trong `emit()` (chokepoint chung mọi caller: `cmd_run`, `cmd_reconcile`, `watch_once`, `cmd_set`) — root cause một chỗ, không vá riêng từng caller (CLAUDE.md ponytail: "Bug = root cause, không vá triệu chứng... sửa 1 lần ở hàm chung").
- File `git status --porcelain` KHÔNG có trong tmp_path test hiện có (không phải git repo) — mọi enforcement phải no-op an toàn khi `_git_root()` trả `None`, không được raise.
- Giữ tương thích ngược: node PLAN.md cũ không khai `**QC:**` hoặc không track git vẫn chạy y hệt trước đây.

### Task 1: Allow-listed write paths trong `cmd_run` (GH#162)
**Files:**
- Sửa: `harness/scripts/orca-graph.py`
**Interfaces:**
- Consumes: —
- Produces (dùng bởi Task 3): `_git_root()`, `_changed_files()`, `enforce_allowed_paths()`, cờ `--strict` trên `run`
**Verify:** `cd /Users/giatran/orca/setup/setup && rtk proxy python3 -m pytest harness/tests/test_orca_graph.py -k "allowed_paths" -q`

```python
def _git_root(cwd: Path):
    """Repo git gốc của cwd, None nếu không trong git repo (vd tmp_path test) — bỏ qua enforcement khi None."""
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, text=True)
        return Path(r.stdout.strip()) if r.returncode == 0 else None
    except OSError:
        return None


def _changed_files(root: Path) -> dict:
    """{path: "M"|"??"} — tracked đã sửa vs untracked mới, đường dẫn tương đối gốc git (khớp quy ước `files` PLAN.md)."""
    r = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True)
    out = {}
    for ln in r.stdout.splitlines():
        if len(ln) < 4:
            continue
        code, path = ln[:2], ln[3:].split(" -> ")[-1].strip()
        if path:
            out[path] = "??" if code.strip() == "??" else "M"
    return out


def enforce_allowed_paths(root: Path, before: dict, allowed: list, strict: bool) -> list:
    """GH#162: chunk ghi NGOÀI `files` khai trong node — cảnh báo (mặc định) hoặc phục hồi cứng (--strict).
    Chỉ xét file MỚI đổi trong lần chạy này (after − before), không đụng đổi có từ trước khi spawn."""
    after = _changed_files(root)
    touched = {p: c for p, c in after.items() if p not in before}
    out_of_scope = [p for p in touched if p not in set(allowed)]
    if out_of_scope and strict:
        for p in out_of_scope:
            if touched[p] == "??":
                try:
                    (root / p).unlink()
                except OSError:
                    pass
            else:
                subprocess.call(["git", "checkout", "--", p], cwd=root)
    return out_of_scope
```

Trong `cmd_run`, quanh chỗ spawn subprocess:
```python
    root = _git_root(Path.cwd())
    before = _changed_files(root) if root else {}
    p = subprocess.Popen(a.cmd)
    while p.poll() is None:
        time.sleep(a.hb)
        if lp.exists():
            lk = json.loads(lp.read_text()); lk["lease_until"] = time.time() + a.lease_sec; lk["pid"] = p.pid; atomic_write(lp, json.dumps(lk))
    g = st.load()
    to = "done" if p.returncode == 0 else "failed"
    note = f"rc={p.returncode}"
    if to == "done" and root is not None and n.get("files"):
        oos = enforce_allowed_paths(root, before, n["files"], a.strict)
        if oos:
            tag = "strict: revert" if a.strict else "⚠ ngoài phạm vi (files)"
            note += f" | {tag} {len(oos)}: {','.join(oos[:5])}"
    emit(st, g, a.node, to, by=a.by, note=note, op_key=f"run-end:{a.node}:{gen}", gen=gen)
```
Argparse: thêm `p.add_argument("--strict", action="store_true")` vào parser `run`.

### Task 2: Tách vai QC khỏi Verify — trường `**QC:**` + gate trong `emit()`/`cmd_reconcile` (GH#163)
**Files:**
- Sửa: `harness/scripts/orca-graph.py`
**Interfaces:**
- Consumes: —
- Produces (dùng bởi Task 3): trường node `qc`, gate trong `emit()` + `cmd_reconcile`
**Depends:** Task 1
**Verify:** `cd /Users/giatran/orca/setup/setup && rtk proxy python3 -m pytest harness/tests/test_orca_graph.py -k "qc_gate" -q`

`parse_plan`: thêm `"qc": ""` vào dict khởi tạo node, thêm `("Qc", "qc")` vào tuple key-loop `**Key:**`.
`spec_hash`: thêm `"qc"` vào tuple các trường được hash (đổi lệnh QC cũng làm node done cũ thành `stale`, giống đổi `verify`).

Trong `emit()`, NGAY SAU khối re-verify hiện có (giữ nguyên khối đó, thêm tiếp theo):
```python
    if to == "done" and n.get("qc") and by != "reconcile":
        rc = subprocess.call(n["qc"], shell=True)
        if rc != 0:
            to = "done_unverified"; note = (note + f" qc rc={rc}").strip()
```

`cmd_reconcile` viết lại:
```python
def cmd_reconcile(a):
    st = Store(Path(a.dir), a.id); g = st.load()
    n = {x["id"]: x for x in g["nodes"]}[a.node]
    if not n.get("verify"):
        print(f"{a.node} không có verify → không tự kết luận được; cần người: set done_user_reported hoặc ready"); return
    rc = subprocess.call(n["verify"], shell=True)
    to = "done" if rc == 0 else "ready"
    note = f"verify rc={rc}"
    qrc = None
    if to == "done" and n.get("qc"):
        qrc = subprocess.call(n["qc"], shell=True)
        if qrc != 0:
            to = "ready"; note += f" | qc rc={qrc} FAIL"
    op_key = f"reconcile:{a.node}:{n['gen']}:{rc}" + (f":{qrc}" if qrc is not None else "")
    emit(st, g, a.node, to, by="reconcile", note=note, op_key=op_key)
    if to != "done":
        cmd_unlock(a)
```

### Task 3: Cập nhật tài liệu — SKILL.md máy state + Rules
**Files:**
- Sửa: `skills/orca-graph/SKILL.md`
**Interfaces:**
- Consumes: Task 1 Produces (`--strict`), Task 2 Produces (`**QC:**`)
- Produces: —
**Depends:** Task 1, Task 2
**Verify:** `grep -q "QC:" skills/orca-graph/SKILL.md && grep -q "allow" skills/orca-graph/SKILL.md`

Cập nhật § "Máy state mỗi node" (thêm mô tả `qc`) và § "Rules"/"Ngoài phạm vi PRD" (bỏ dòng cũ nói "không kiểm soát side-effect" nếu nay đã có allow-path mềm; ghi rõ mức độ: mặc định cảnh báo, `--strict` mới phục hồi cứng). Diff văn xuôi minh hoạ (không phải code, nhưng đây là nội dung ĐÚNG cần thay):

```markdown
- **Lock chỉ kiểm soát DISPATCH**, không kiểm soát side-effect của agent đã chạy. Muốn cách ly thật → worktree riêng mỗi task.
+ **Lock chỉ kiểm soát DISPATCH**; side-effect có allow-list MỀM (GH#162) — `run` diff `files` khai vs file thật đổi, mặc định CẢNH BÁO (note trong event), `--strict` mới phục hồi cứng (untracked xoá, tracked `git checkout`). Muốn cách ly thật (process-level) → worktree riêng mỗi task, allow-list không thay thế.
```
```markdown
+ - `qc` (GH#163, tuỳ chọn): lệnh review ĐỘC LẬP chạy SAU `verify` rc=0 — fail thì `done`→`done_unverified` (qua `emit()`) hoặc `ready` (qua `reconcile`), không tự động `done` dù verify xanh.
```

## Origin
Thi hành trực tiếp cho [[170926-orca-graph-no-write-sandbox]] (GH#162) và [[170926-orca-graph-no-separate-qc-role]] (GH#163) — 2 issue raised phiên 2026-09-17 khi so sánh `/orca-graph` với kiến trúc "Atlas dispatch pipeline" (ảnh user cung cấp). Goal `/goal` cùng phiên: "kéo 2 issue về, vẽ kiến trúc archify, thực hiện, test kỹ, commit push".
