---
type: draft
title: skill-evolve-loop-PLAN
status: proposed
timestamp: 2026-07-24
task: T-260724-01
---

# skill-evolve-loop — PLAN thi hành

**Goal:** đo chất lượng thực thi của TỪNG skill riêng lẻ (không chỉ tần suất), tích luỹ theo thời gian, và khi tỷ lệ lỗi vượt ngưỡng thì tự soạn (không tự ghi) một đề xuất sửa đúng `SKILL.md` đó, dừng ở `/propose`.

**Architecture:** một script glue mới (`harness/scripts/skill-evolve.py`) cắt lát transcript theo TỪNG lần gọi Skill-tool (dùng field mới `line_idx`/`file` thêm vào `fdk/tools/skill-usage.py::collect()`), gọi thẳng `trace-grader.py`'s `runs_from_transcript()`/`grade_run()` (import qua `importlib.util`, không sửa file đó) để lấy verdict tất định cho đúng lần gọi, rồi ghi ledger qua hạ tầng dùng chung `bnal_metrics`/`bnal_config` (KHÔNG hand-roll I/O riêng).

**Tech stack:** Python 3 (stdlib + PyYAML đã có sẵn trong repo qua `bnal_config`), không thêm dependency.

**SPEC nguồn:** `wiki/sources/draft/240726-skill-evolve-loop.md` (duyệt 2026-07-24)

## Origin
- **SPEC:** `wiki/sources/draft/240726-skill-evolve-loop.md`
- **Commit:** _(verify-before-commit điền)_

## Global constraints
(chép nguyên văn từ SPEC)

- **Never auto-promote**: mọi đề xuất sửa SKILL.md PHẢI dừng ở `/propose`, chờ người duyệt. `skill-evolve` không bao giờ tự ghi đè SKILL.md.
- **Build-now-adapt-later**: ngưỡng số (`min_sample`, `fail_rate_threshold`) là giả định best-guess, cô lập trong ĐÚNG MỘT file config `verified: false`.
- **Fail-open tuyệt đối ở phần ghi/scan**: quét/ghi ledger lỗi không được chặn phiên đang chạy.
- **Không sửa `trace-grader.py` hay `failure-flywheel.py`/`flywheel.py`** — chỉ import/gọi làm black-box (trừ MỘT thay đổi additive, backward-compatible vào `skill-usage.py::collect()`).
- Ledger đi theo convention **gitignored local** của `failures.jsonl`/`events.jsonl` — không git-track.
- Trước push: `python3 fdk/tools/medic.py --ci` phải xanh (sàn CI toàn repo, không riêng feature này).

## Ghi chú tinh chỉnh so với SPEC (không phải mâu thuẫn — xem "Cổng ngược" của `/plan`)

Viết PLAN này lộ ra 2 chi tiết SPEC mô tả hơi khác thực tế code — cả hai đều làm mọi FR/SC trong SPEC **dễ đạt hơn**, không phá cái nào:

1. **`failure-flywheel.py` giờ chỉ là shim** (`os.execv` sang `flywheel.py --kind failure`) — engine thật đã refactor thành `flywheel.py` (polarity-selected `--kind failure|success`) dùng chung 2 module `bnal_metrics.py`/`bnal_config.py` (ghi JSONL fail-open + load config `verified:false`, đã kiểm chứng chạy sống qua `flywheel.py --self-test`). SPEC's Non-goal "không sửa failure-flywheel.py" áp dụng y hệt cho `flywheel.py` — nhưng `bnal_metrics`/`bnal_config` là hạ tầng CHUNG, KHÔNG gắn polarity failure/success, nên **tái dùng trực tiếp** (không phải sửa) đúng tinh thần FR-004/FR-009 hơn là hand-roll JSON I/O riêng.
2. **Đường ledger thật là `harness/metrics/<tên>.jsonl`** (qua `bnal_metrics._file()`), không phải `harness/<tên>.jsonl` phẳng như SPEC's Assumptions viết. Dùng đúng `bnal_metrics.append(root, "skill-evolve-ledger.jsonl", ...)` thì file tự nằm ở `harness/metrics/skill-evolve-ledger.jsonl` — cùng chỗ với `failures.jsonl`/`successes.jsonl` đã có, khớp "khuôn failures.jsonl" của FR-004 còn sát nghĩa hơn bản SPEC viết tay.

Không cái nào thuộc 4 điều kiện DỪNG của `/plan` (không mâu thuẫn, không bất khả thi, không phải bịa hàm/API) — cả hai chỉ là path/hạ-tầng chính xác hơn, giữ nguyên toàn bộ FR/SC/Non-goals.

## File structure

- Sửa `fdk/tools/skill-usage.py:86-123` (hàm `collect()`) — thêm 2 field additive `line_idx` (chỉ số dòng trong file) và `file` (đường dẫn file transcript) vào mỗi event. Không đổi field cũ, không đổi `--weekly`/`--json`/`aggregate()`/`build_report()`.
- Tạo `harness/scripts/skill-evolve.py` — toàn bộ logic mới: nạp `skill-usage.py`/`trace-grader.py` qua `importlib`, `bnal_metrics`/`bnal_config` qua import thường (cùng thư mục `harness/scripts/`); CLI `--scan [N]` / `--report` / `--draft <skill_id>` / `--self-test`.
- Tạo `harness/skill-evolve.config.yaml` — adapter `verified: false`, `min_sample`, `fail_rate_threshold` mỗi giá trị chú thích `# ASSUMPTION` (khuôn `harness/failure-flywheel.config.yaml`).

### Task 1: `skill-usage.py::collect()` — thêm `line_idx` + `file` (additive)

**Thoả:** FR-001 (mở rộng: field gốc SPEC chỉ nêu `line_idx`; PLAN thêm `file` vì `collect()` hiện gom sự kiện từ NHIỀU file cùng lúc và không giữ file nguồn — thiếu `file` thì Task 2 không biết mở lại file nào để cắt lát. Superset, không rút bớt gì SPEC yêu cầu.)

**Files:**
- Sửa: `fdk/tools/skill-usage.py:86-123` (hàm `collect`)

**Interfaces:**
- Produces: `collect(transcript_dirs: List[Path]) -> List[dict]`, mỗi dict thêm 2 khoá mới `line_idx: int` (0-based, chỉ số dòng trong file chứa lời gọi Skill-tool) và `file: str` (đường dẫn tuyệt đối tới file transcript chứa event đó) — cạnh 4 khoá cũ `skill`/`ts`/`week`/`session`. Task 2 (`skill-evolve.py::scan`) consume trực tiếp cả 6 khoá.

- [ ] **Step 1: viết assertion fail trước (thêm vào cuối `self_test()`, dòng 360)**

```python
def self_test() -> int:
    """Tất định: fixture 1 dòng transcript Skill-call → collect/aggregate phải đếm đúng."""
    import json as _json
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        td = Path(d)
        line = {"type": "assistant", "timestamp": "2026-07-14T10:00:00.000Z",
                "sessionId": "st-1", "message": {"content": [
                    {"type": "tool_use", "name": "Skill", "input": {"skill": "qc-code"}}]}}
        (td / "s1.jsonl").write_text(_json.dumps(line) + "\n", encoding="utf-8")
        events = collect([td])
        ok = len(events) == 1 and events[0]["skill"] == "qc-code" and iso_week(parse_ts(line["timestamp"])) == "2026-W29"
        ok = ok and events[0].get("line_idx") == 0 and events[0].get("file") == str(td / "s1.jsonl")
    print("skill-usage self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Chạy: `python3 fdk/tools/skill-usage.py --self-test`
Mong đợi: `skill-usage self-test: FAIL` (in ra vì `events[0].get("line_idx")` trả `None`, so `None == 0` → `False` — dùng `.get()` chứ không bracket-index để tránh crash, chỉ so sánh sai và fail sạch).

- [ ] **Step 3: code tối thiểu cho pass — sửa `collect()` (dòng 86-123)**

```python
def collect(transcript_dirs):
    """Trả list event {skill, ts(datetime), week, session, line_idx, file} từ mọi .jsonl trong mọi dir."""
    events = []
    files = sorted(f for d in transcript_dirs for f in glob.glob(str(d / "*.jsonl")))
    for f in files:
        try:
            fh = open(f, encoding="utf-8")
        except OSError:
            continue
        with fh:
            for idx, line in enumerate(fh):
                line = line.strip()
                if not line or '"Skill"' not in line:
                    continue
                try:
                    o = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = o.get("message")
                content = msg.get("content") if isinstance(msg, dict) else None
                if not isinstance(content, list):
                    continue
                ts = parse_ts(o.get("timestamp"))
                if ts is None:
                    continue
                session = o.get("sessionId") or Path(f).stem
                for b in content:
                    if (
                        isinstance(b, dict)
                        and b.get("type") == "tool_use"
                        and b.get("name") == "Skill"
                    ):
                        skill = (b.get("input") or {}).get("skill")
                        if skill:
                            events.append(
                                {"skill": skill, "ts": ts, "week": iso_week(ts),
                                 "session": session, "line_idx": idx, "file": f}
                            )
    return events
```

Diff chính xác: `for line in fh:` → `for idx, line in enumerate(fh):`; thêm `"line_idx": idx, "file": f` vào dict append. Không đổi gì khác trong hàm.

- [ ] **Step 4: chạy lại — PASS**

Chạy: `python3 fdk/tools/skill-usage.py --self-test`
Mong đợi: `skill-usage self-test: PASS`

- [ ] **Step 5: verify không hồi quy `--weekly`/`--json` (đọc field cũ, bỏ qua field mới)**

Chạy: `python3 fdk/tools/skill-usage.py --json --no-html 2>&1 | head -5`
Mong đợi: chạy xong không traceback (hoặc in cảnh báo "Không thấy thư mục transcript" nếu môi trường test trống — cả hai đều KHÔNG phải lỗi do field mới, vì `aggregate()`/`build_report()` chỉ đọc `skill`/`session`/`week`/`ts` theo tên khoá, bỏ qua khoá lạ).

- [ ] **Step 6: commit**

```bash
git add fdk/tools/skill-usage.py
git commit -m "feat(skill-usage): collect() thêm line_idx + file (additive, cho skill-evolve)"
```

### Task 2: `harness/scripts/skill-evolve.py` — `--scan`: cắt lát + chấm + ghi ledger + idempotent

**Thoả:** FR-002, FR-003, FR-004, FR-005

**Files:**
- Tạo: `harness/scripts/skill-evolve.py`

**Interfaces:**
- Consumes: `skill_usage.collect(dirs)` (Task 1, trả `line_idx`/`file`), `skill_usage.discover_transcript_dirs(root)` (đã có sẵn, không đổi); `trace_grader.runs_from_transcript(lines, task_hint=None)`, `trace_grader.grade_run(run, cfg)`, `trace_grader.load_config(path)`, `trace_grader.DEFAULT_CONFIG_PATH` (đã có sẵn, không đổi); `bnal_metrics.append(root, rel, rec, comment="")`, `bnal_metrics.ensure_gitignored(root, rel, comment="")` (đã có sẵn, không đổi).
- Produces: hàm `scan(root, n=1) -> int` (số dòng ledger mới ghi) — Task 5 test trực tiếp hàm này; CLI `skill-evolve.py --scan [N]`.

- [ ] **Step 1: viết test fail trước — file test tạm (chạy trực tiếp bằng `python3 -c`, không cần pytest, khuôn `skill-usage.py::self_test()`)**

```bash
python3 -c "
import sys; sys.path.insert(0, 'harness/scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('skill_evolve', 'harness/scripts/skill-evolve.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print('scan callable:', callable(getattr(mod, 'scan', None)))
"
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Mong đợi: `ModuleNotFoundError` hoặc `FileNotFoundError` (file `harness/scripts/skill-evolve.py` chưa tồn tại).

- [ ] **Step 3: code tối thiểu cho pass — tạo `harness/scripts/skill-evolve.py`**

```python
#!/usr/bin/env python3
"""skill-evolve — per-skill quality ledger + auto-draft revision proposal.

BUILD-NOW / ADAPTER BOUNDARY (see /build-now-adapt-later)
----------------------------------------------------------
Correlator mỏng nối 3 module đã có, KHÔNG viết lại engine chấm điểm nào:
  * fdk/tools/skill-usage.py::collect()   — biết lúc nào gọi skill nào (line_idx/file)
  * harness/scripts/trace-grader.py       — chấm đường đi tất định (runs_from_transcript/grade_run)
  * harness/scripts/bnal_metrics.py + bnal_config.py — ghi ledger JSONL fail-open + load config

Ngưỡng số (min_sample, fail_rate_threshold) sống trong harness/skill-evolve.config.yaml,
verified:false — adapter DUY NHẤT, xem /build-now-adapt-later.

Never auto-promote: --draft chỉ SOẠN đề xuất, dừng ở /propose. Không tự ghi SKILL.md.

Usage
-----
  python3 harness/scripts/skill-evolve.py --scan [N]
  python3 harness/scripts/skill-evolve.py --report
  python3 harness/scripts/skill-evolve.py --draft <skill_id>
  python3 harness/scripts/skill-evolve.py --self-test
"""
import argparse
import datetime as _dt
import glob
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # harness/scripts
HARNESS = HERE.parent                            # harness
ROOT = HARNESS.parent                            # repo root
FDK_TOOLS = ROOT / "fdk" / "tools"

LEDGER = "skill-evolve-ledger.jsonl"
STATE_REL = "skill-evolve.state.json"
CONFIG_NAME = "skill-evolve"
DEFAULT_CFG = {"verified": False, "min_sample": 5, "fail_rate_threshold": 0.4}

sys.path.insert(0, str(HERE))
import bnal_config      # noqa: E402  (cùng thư mục, import thường — không dấu gạch ngang)
import bnal_metrics     # noqa: E402


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # trace-grader.py dùng @dataclass + postponed annotations —
    spec.loader.exec_module(mod)  # cần đăng ký trước exec để dataclasses._is_type resolve được
    return mod


_su = None
def skill_usage():
    global _su
    if _su is None:
        _su = _load_module("skill_usage", FDK_TOOLS / "skill-usage.py")
    return _su


_tg = None
def trace_grader():
    global _tg
    if _tg is None:
        _tg = _load_module("trace_grader", HERE / "trace-grader.py")
    return _tg


def _state_path() -> Path:
    return HARNESS / "metrics" / STATE_REL


def _load_state() -> dict:
    try:
        import json
        return json.loads(_state_path().read_text(encoding="utf-8"))
    except Exception:
        return {"processed": []}


def _save_state(state: dict) -> None:
    try:
        import json
        bnal_metrics.ensure_gitignored(ROOT, STATE_REL, comment="skill-evolve watermark (local)")
        _state_path().parent.mkdir(parents=True, exist_ok=True)
        _state_path().write_text(json.dumps(state), encoding="utf-8")
    except Exception:
        pass


def scan(root=ROOT, n=1) -> int:
    """Cắt lát N session gần nhất theo từng lần gọi Skill-tool, chấm bằng trace-grader,
    ghi verdict vào ledger. Idempotent (watermark theo session::line_idx). Fail-open per lần gọi."""
    su = skill_usage()
    tg = trace_grader()
    dirs = su.discover_transcript_dirs(root)
    all_files = sorted(
        (Path(f) for d in dirs for f in glob.glob(str(Path(d) / "*.jsonl"))),
        key=lambda p: p.stat().st_mtime, reverse=True,
    )
    target = {str(p) for p in all_files[:n]}
    if not target:
        return 0

    events = su.collect(dirs)
    by_file = {}
    for e in events:
        if e["file"] in target:
            by_file.setdefault(e["file"], []).append(e)

    cfg = tg.load_config(str(tg.DEFAULT_CONFIG_PATH))
    state = _load_state()
    processed = set(state.get("processed", []))
    written = 0

    for fpath, evs in by_file.items():
        evs.sort(key=lambda e: e["line_idx"])
        try:
            all_lines = Path(fpath).read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for i, e in enumerate(evs):
            key = f"{e['session']}::{e['line_idx']}"
            if key in processed:
                continue
            start = e["line_idx"]
            end = evs[i + 1]["line_idx"] if i + 1 < len(evs) else len(all_lines)
            slice_lines = all_lines[start:end]
            try:
                runs = tg.runs_from_transcript(slice_lines, task_hint=e["skill"])
                if not runs:
                    processed.add(key)
                    continue
                verdict = tg.grade_run(runs[0], cfg)
            except Exception:
                continue
            rec = {
                "skill": e["skill"], "session": e["session"], "ts": e["ts"].isoformat(),
                "verdict": verdict["verdict"], "flags": verdict["flags"],
            }
            bnal_metrics.append(root, LEDGER, rec, comment="skill-evolve per-skill quality ledger (local)")
            processed.add(key)
            written += 1

    _save_state({"processed": sorted(processed)})
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description="skill-evolve — per-skill quality ledger")
    ap.add_argument("--scan", nargs="?", const=1, type=int, metavar="N",
                    help="quét N session gần nhất (mặc định 1 = session hiện tại)")
    args = ap.parse_args()
    if args.scan is not None:
        n = args.scan
        written = scan(ROOT, n)
        print(f"· scan {n} session → {written} verdict mới ghi vào harness/metrics/{LEDGER}")
        return 0
    ap.error("chưa có subcommand — dùng --scan (thêm --report/--draft ở Task 3/4)")
    return 2


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: chạy lại test — PASS**

Chạy:
```bash
python3 -c "
import sys; sys.path.insert(0, 'harness/scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('skill_evolve', 'harness/scripts/skill-evolve.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print('scan callable:', callable(getattr(mod, 'scan', None)))
"
```
Mong đợi: `scan callable: True`

- [ ] **Step 5: verify idempotency trên fixture thật (2 lần gọi scan liên tiếp không nhân đôi ledger)**

```bash
python3 -c "
import sys, tempfile, json
sys.path.insert(0, 'harness/scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('skill_evolve', 'harness/scripts/skill-evolve.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
import bnal_metrics
with tempfile.TemporaryDirectory() as d:
    from pathlib import Path
    root = Path(d)
    (root / 'harness').mkdir()
    proj = root / 'proj'; proj.mkdir()
    lines = [
        json.dumps({'type':'assistant','timestamp':'2026-07-24T10:00:00.000Z','sessionId':'s1',
                    'message':{'content':[{'type':'tool_use','id':'c1','name':'Skill','input':{'skill':'qc-code'}}]}}),
        json.dumps({'type':'assistant','timestamp':'2026-07-24T10:00:01.000Z','sessionId':'s1',
                    'message':{'content':[{'type':'tool_use','id':'c2','name':'Read','input':{'file_path':'x.py'}}]}}),
        json.dumps({'type':'user','timestamp':'2026-07-24T10:00:02.000Z','sessionId':'s1',
                    'message':{'content':[{'type':'tool_result','tool_use_id':'c2','content':'ok','is_error':False}]}}),
    ]
    (proj / 's1.jsonl').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    su = mod.skill_usage()
    su.discover_transcript_dirs = lambda root: [proj]  # sandbox không có .git — bơm dir thẳng, KHÔNG đổi scan()
    n1 = mod.scan(root, n=1)
    n2 = mod.scan(root, n=1)
    rows = bnal_metrics.read(root, mod.LEDGER)
    print('n1=', n1, 'n2=', n2, 'total_rows=', len(rows))
"
```
Mong đợi: `n1= 1 n2= 0 total_rows= 1` (lần 2 không ghi thêm — idempotent thật).

**Lưu ý fixture (đã xác nhận bằng chạy thật):** `discover_transcript_dirs` cần `git worktree list` chạy được — sandbox test không có `.git` ở `root` giả → hàm fail-open trả `[]`. Test monkeypatch thẳng `su.discover_transcript_dirs` (module đã nạp qua `mod.skill_usage()`) trỏ về dir fixture — KHÔNG đổi hành vi `scan()` cho production, chỉ đổi nguồn `dirs` trong đúng đoạn test này.

- [ ] **Step 6: commit**

```bash
git add harness/scripts/skill-evolve.py
git commit -m "feat(skill-evolve): T2 — scan cắt lát transcript theo skill, chấm bằng trace-grader, ghi ledger idempotent"
```

### Task 3: config adapter + `--report` leaderboard

**Thoả:** FR-006, FR-009

**Files:**
- Tạo: `harness/skill-evolve.config.yaml`
- Sửa: `harness/scripts/skill-evolve.py` (thêm hàm `_leaderboard()`/`report()`, thêm nhánh `--report` vào `main()`)

**Interfaces:**
- Consumes: `bnal_config.load(root, "skill-evolve", DEFAULT_CFG)` (đã có sẵn); `bnal_metrics.read(root, LEDGER)` (đã có sẵn); ledger rows từ Task 2 (`{skill, session, ts, verdict, flags}`).
- Produces: hàm `report(root=ROOT) -> str`; CLI `--report`.

- [ ] **Step 1: viết test fail trước**

```bash
python3 -c "
import sys; sys.path.insert(0, 'harness/scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('skill_evolve', 'harness/scripts/skill-evolve.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
print('report callable:', callable(getattr(mod, 'report', None)))
"
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Mong đợi: `report callable: False` (hàm `report` chưa tồn tại — `getattr(..., None)` trả `None`, `callable(None)` là `False`).

- [ ] **Step 3: tạo `harness/skill-evolve.config.yaml`**

```yaml
# harness/skill-evolve.config.yaml
# Adapter DUY NHẤT của skill-evolve — /build-now-adapt-later. Engine (scan/report/draft)
# built now, không phụ thuộc giá trị nào dưới đây ngoài 2 ngưỡng số này.

verified: false          # ASSUMPTION — chưa hiệu chỉnh trên dữ liệu ledger thật, xem U-06.

min_sample: 5             # ASSUMPTION — số lần gọi tối thiểu trước khi kết luận (tránh
                          #   1 lần lỗi ngẫu nhiên kết luận cả skill tệ).

fail_rate_threshold: 0.4  # ASSUMPTION — mượn nguyên số 40% SkillRL dùng cho RL của họ,
                          #   chưa có cơ sở riêng cho verdict trace-grader (an toàn/quy trình,
                          #   không đo đúng-sai nghiệp vụ — xem Non-goals SPEC).
```

- [ ] **Step 4: code tối thiểu cho pass — thêm vào `harness/scripts/skill-evolve.py` (trước hàm `main()`)**

```python
def _leaderboard(root=ROOT) -> dict:
    """{skill_id: {count, bad}} — bad = số verdict corrupt-success (verdict 'fail' cũng
    tính nếu có, nhưng KHÔNG BAO GIỜ xảy ra với run xuất phát từ transcript — xem
    trace-grader.py docstring runs_from_transcript: Run.ok bị ép True nên grade_run không
    bao giờ trả 'fail' cho nguồn dữ liệu này; giữ cả hai nhánh để không vỡ nếu sau này
    thêm nguồn khác (traces.json/audit) có Run.ok thật)."""
    groups = {}
    for r in bnal_metrics.read(root, LEDGER):
        g = groups.setdefault(r["skill"], {"count": 0, "bad": 0})
        g["count"] += 1
        if r["verdict"] in ("corrupt-success", "fail"):
            g["bad"] += 1
    return groups


def report(root=ROOT) -> str:
    cfg = bnal_config.load(root, CONFIG_NAME, DEFAULT_CFG)
    min_sample = int(cfg.get("min_sample", 5))
    thr = float(cfg.get("fail_rate_threshold", 0.4))
    groups = _leaderboard(root)
    lines = [
        f"skill-evolve — {len(groups)} skill(s) tracked",
        f"min_sample={min_sample}  fail_rate_threshold={thr}  "
        f"(adapter: harness/{CONFIG_NAME}.config.yaml, verified={cfg.get('verified')})",
        "",
    ]
    if not groups:
        lines.append("(chưa có dữ liệu — chạy --scan trước)")
        return "\n".join(lines)
    ordered = sorted(groups.items(), key=lambda kv: (-kv[1]["bad"], kv[0]))
    eligible = []
    for skill, g in ordered:
        rate = g["bad"] / g["count"] if g["count"] else 0.0
        elig = g["count"] >= min_sample and rate >= thr
        if elig:
            eligible.append(skill)
        tag = "DRAFT-ELIGIBLE" if elig else "-"
        lines.append(f"  {g['count']:>4}  fail_rate={rate:.2f}  {tag:<15}  {skill}")
    lines.append("")
    lines.append("Eligible for --draft:" if eligible else "Chưa skill nào đủ mẫu + vượt ngưỡng.")
    lines += [f"  skill-evolve.py --draft {s}" for s in eligible]
    return "\n".join(lines)
```

Sửa `main()` — thêm arg + nhánh (chèn trước dòng `ap.error("chưa có subcommand...")`):

```python
    ap.add_argument("--report", action="store_true", help="leaderboard per-skill")
    ...  # (giữ nguyên --scan đã có)
    if args.report:
        print(report(ROOT))
        return 0
```

- [ ] **Step 5: chạy lại — PASS**

Chạy: `python3 harness/scripts/skill-evolve.py --report`
Mong đợi (ledger rỗng lúc này): `skill-evolve — 0 skill(s) tracked` … `(chưa có dữ liệu — chạy --scan trước)`, exit 0.

- [ ] **Step 6: commit**

```bash
git add harness/skill-evolve.config.yaml harness/scripts/skill-evolve.py
git commit -m "feat(skill-evolve): T3 — config adapter verified:false + --report leaderboard"
```

### Task 4: `--draft <skill_id>` — định vị SKILL.md + nhúng nội dung + bằng chứng

**Thoả:** FR-007, FR-008

**Files:**
- Sửa: `harness/scripts/skill-evolve.py` (thêm `_skill_md_path()`, `draft()`, nhánh `--draft` trong `main()`)

**Interfaces:**
- Consumes: `_leaderboard()`/`bnal_config.load()` (Task 3); `bnal_metrics.read(root, LEDGER)` (đã có sẵn).
- Produces: hàm `draft(root=ROOT, skill_id=None, date_str=None) -> (Path|None, str)`; CLI `--draft <skill_id>`.

**Định vị SKILL.md (FR-008) — xác nhận bằng code thật, không đoán:** `fdk/tools/build-capabilities.py:57-60` (`skills_dir()`) — hàm SINH `fdk/CAPABILITIES.md` — dùng chính xác `root/"skills"` và glob `*/SKILL.md` để liệt kê MỌI skill của repo. Đây là registry canonical, không phải convention tự đoán: `Path(root)/"skills"/skill_id/"SKILL.md"`.

- [ ] **Step 1: viết test fail trước**

```bash
python3 -c "
import sys; sys.path.insert(0, 'harness/scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('skill_evolve', 'harness/scripts/skill-evolve.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
print('draft callable:', callable(getattr(mod, 'draft', None)))
"
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Mong đợi: `draft callable: False`

- [ ] **Step 3: code tối thiểu cho pass — thêm vào `harness/scripts/skill-evolve.py` (trước `main()`)**

```python
def _skill_md_path(root, skill_id):
    """FR-008: định vị qua registry canonical (glob skills/*/SKILL.md dùng bởi
    fdk/tools/build-capabilities.py::skills_dir), KHÔNG đoán bằng convention tên file khác."""
    p = Path(root) / "skills" / skill_id / "SKILL.md"
    return p if p.is_file() else None


def _ddmmyy(date_str: str) -> str:
    y, m, d = date_str.split("-")
    return f"{d}{m}{y[2:]}"


def draft(root=ROOT, skill_id=None, date_str=None):
    cfg = bnal_config.load(root, CONFIG_NAME, DEFAULT_CFG)
    min_sample = int(cfg.get("min_sample", 5))
    thr = float(cfg.get("fail_rate_threshold", 0.4))
    groups = _leaderboard(root)
    g = groups.get(skill_id)
    if not g or not (g["count"] >= min_sample and (g["bad"] / g["count"]) >= thr):
        return None, f"'{skill_id}' chưa đủ mẫu (>= {min_sample}) hoặc chưa vượt ngưỡng ({thr}) — không eligible."

    skill_md = _skill_md_path(root, skill_id)
    if not skill_md:
        return None, f"Không tìm thấy skills/{skill_id}/SKILL.md — không thể soạn draft."

    rows = [r for r in bnal_metrics.read(root, LEDGER)
            if r["skill"] == skill_id and r["verdict"] in ("corrupt-success", "fail")]
    date_str = date_str or _dt.date.today().isoformat()
    ddmmyy = _ddmmyy(date_str)
    out_dir = Path(root) / "llmwiki" / "wiki" / "sources" / "draft"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{ddmmyy}-skill-evolve-{skill_id}.md"

    rate = g["bad"] / g["count"]
    md = [
        "---", "type: draft",
        f'title: "Đề xuất sửa SKILL.md — {skill_id} (skill-evolve)"',
        "status: proposed", f"tags: [skill-evolve, {skill_id}, quality-regression]",
        f"timestamp: {date_str}", "---", "",
        f"# {ddmmyy}-skill-evolve-{skill_id}", "",
        f"Tỷ lệ lỗi (`corrupt-success`/`fail`) của skill `{skill_id}` = "
        f"{g['bad']}/{g['count']} ({rate:.0%}), vượt ngưỡng {thr:.0%} "
        f"(cấu hình `harness/{CONFIG_NAME}.config.yaml`). Nội dung `SKILL.md` hiện tại và "
        f"bằng chứng cụ thể ở dưới — bản này là SEED cho `/propose`, KHÔNG tự ghi đè.", "",
        "## SKILL.md hiện tại (nguyên văn)", "```markdown",
        skill_md.read_text(encoding="utf-8"), "```", "",
        f"## Bằng chứng ({len(rows)} lần gọi lỗi)", "",
        "| Session | Verdict | Flags |", "|---|---|---|",
    ]
    for r in rows[-20:]:
        flags_s = "; ".join(f.get("detail") or f.get("check", "?") for f in r.get("flags", [])) or "-"
        md.append(f"| {r['session']} | {r['verdict']} | {flags_s} |")
    md += [
        "", "## Origin",
        f"- **Source:** `skill-evolve.py --draft {skill_id}` từ `harness/metrics/{LEDGER}` "
        f"({g['count']} lần gọi, {g['bad']} lỗi).",
        f"- **Adapter:** `harness/{CONFIG_NAME}.config.yaml` (verified={cfg.get('verified')}).",
        f"- **Date:** {date_str}", "",
    ]
    out.write_text("\n".join(md), encoding="utf-8")
    return out, f"Đã soạn {out} — STOP, chờ /propose hoàn thiện + người duyệt."
```

Sửa `main()` — thêm arg + nhánh:

```python
    ap.add_argument("--draft", metavar="SKILL_ID", help="soạn đề xuất sửa SKILL.md nếu eligible")
    ...
    if args.draft:
        out, msg = draft(ROOT, args.draft)
        print(msg)
        return 0 if out else 1
```

- [ ] **Step 4: chạy lại — PASS (trên skill chưa đủ mẫu, verify nhánh "chưa eligible")**

Chạy: `python3 harness/scripts/skill-evolve.py --draft qc-code`
Mong đợi: `'qc-code' chưa đủ mẫu (>= 5) hoặc chưa vượt ngưỡng (0.4) — không eligible.` (exit 1) — chứng minh nhánh guard hoạt động trước khi test nhánh thành công ở Task 5.

- [ ] **Step 5: commit**

```bash
git add harness/scripts/skill-evolve.py
git commit -m "feat(skill-evolve): T4 — --draft nhúng SKILL.md hiện tại + bằng chứng, dừng ở /propose"
```

### Task 5: bundled self-test — fixture 2 lần gọi skill (1 clean, 1 corrupt-success)

**Thoả:** FR-002, FR-003, FR-004, FR-005, FR-006, FR-007 (verify tích hợp toàn bộ)

**Files:**
- Sửa: `harness/scripts/skill-evolve.py` (thêm hàm `self_test()`, nhánh `--self-test` trong `main()`)

**Interfaces:**
- Consumes: `scan()` (Task 2), `report()` (Task 3), `draft()` (Task 4) — gọi trực tiếp trong cùng process, không qua subprocess.
- Produces: CLI `--self-test`, exit code 0/1 (khuôn `trace-grader.py --self-test` / `skill-usage.py::self_test()`).

- [ ] **Step 1: viết test fail trước**

```bash
python3 harness/scripts/skill-evolve.py --self-test
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Mong đợi: `argument --self-test/self_test: ...` lỗi argparse ("unrecognized arguments") vì flag chưa tồn tại — exit 2.

- [ ] **Step 3: code tối thiểu cho pass — thêm vào `harness/scripts/skill-evolve.py` (trước `main()`)**

Fixture: 1 session, 2 lần gọi Skill-tool liên tiếp — lần đầu (`demo-clean`) chỉ có 1 `Read` sạch; lần hai (`demo-bad`) gọi tool `force_push` (nằm trong `forbidden_tools` thật của `harness/trace-grader.config.yaml`) → `check_forbidden_tool` bắt được → `corrupt-success`. Chạy `scan` với `min_sample`/`fail_rate_threshold` hạ thấp (ép qua config tạm) để `demo-bad` lên `DRAFT-ELIGIBLE` ngay ở 1 mẫu.

```python
def self_test() -> int:
    import json as _json
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "harness").mkdir()
        (root / "harness" / f"{CONFIG_NAME}.config.yaml").write_text(
            "verified: false\nmin_sample: 1\nfail_rate_threshold: 0.4\n", encoding="utf-8"
        )
        skills_dir = root / "skills" / "demo-bad"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("---\nname: demo-bad\n---\n# demo-bad\n", encoding="utf-8")

        proj = root / "proj"
        proj.mkdir()
        lines = [
            {"type": "assistant", "timestamp": "2026-07-24T10:00:00.000Z", "sessionId": "st-se",
             "message": {"content": [{"type": "tool_use", "id": "c1", "name": "Skill",
                                       "input": {"skill": "demo-clean"}}]}},
            {"type": "assistant", "timestamp": "2026-07-24T10:00:01.000Z", "sessionId": "st-se",
             "message": {"content": [{"type": "tool_use", "id": "c2", "name": "Read",
                                       "input": {"file_path": "x.py"}}]}},
            {"type": "user", "timestamp": "2026-07-24T10:00:02.000Z", "sessionId": "st-se",
             "message": {"content": [{"type": "tool_result", "tool_use_id": "c2",
                                       "content": "ok", "is_error": False}]}},
            {"type": "assistant", "timestamp": "2026-07-24T10:00:03.000Z", "sessionId": "st-se",
             "message": {"content": [{"type": "tool_use", "id": "c3", "name": "Skill",
                                       "input": {"skill": "demo-bad"}}]}},
            {"type": "assistant", "timestamp": "2026-07-24T10:00:04.000Z", "sessionId": "st-se",
             "message": {"content": [{"type": "tool_use", "id": "c4", "name": "force_push",
                                       "input": {}}]}},
            {"type": "user", "timestamp": "2026-07-24T10:00:05.000Z", "sessionId": "st-se",
             "message": {"content": [{"type": "tool_result", "tool_use_id": "c4",
                                       "content": "done", "is_error": False}]}},
        ]
        (proj / "st-se.jsonl").write_text(
            "\n".join(_json.dumps(l) for l in lines) + "\n", encoding="utf-8"
        )

        su = skill_usage()
        events = su.collect([proj])
        by_file = {}
        for e in events:
            by_file.setdefault(e["file"], []).append(e)
        tg = trace_grader()
        cfg = tg.load_config(str(tg.DEFAULT_CONFIG_PATH))
        written = 0
        for fpath, evs in by_file.items():
            evs.sort(key=lambda e: e["line_idx"])
            all_lines = Path(fpath).read_text(encoding="utf-8").splitlines()
            for i, e in enumerate(evs):
                start = e["line_idx"]
                end = evs[i + 1]["line_idx"] if i + 1 < len(evs) else len(all_lines)
                runs = tg.runs_from_transcript(all_lines[start:end], task_hint=e["skill"])
                if not runs:
                    continue
                verdict = tg.grade_run(runs[0], cfg)
                rec = {"skill": e["skill"], "session": e["session"], "ts": e["ts"].isoformat(),
                       "verdict": verdict["verdict"], "flags": verdict["flags"]}
                bnal_metrics.append(root, LEDGER, rec, comment="self-test")
                written += 1

        rep = report(root)
        out, _msg = draft(root, "demo-bad", date_str="2026-07-24")

        ok = (
            written == 2
            and "demo-clean" in rep and "demo-bad" in rep
            and "DRAFT-ELIGIBLE" in rep
            and out is not None and out.exists()
            and "force_push" in out.read_text(encoding="utf-8")
        )

        # idempotency: quét lại CÙNG file (giả lập bằng cách gọi lại append-guard thủ công) —
        # ở đây verify qua scan() thật với watermark, không qua vòng lặp tay ở trên:
        n_again = 0  # scan() thật (không phải vòng lặp tay) mới có watermark — xem Step 4.

    print("skill-evolve self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1
```

Sửa `main()` — thêm nhánh (trước `ap.error(...)`):

```python
    ap.add_argument("--self-test", action="store_true")
    ...
    if args.self_test:
        return self_test()
```

**Lưu ý:** self-test ở trên lặp tay logic của `scan()` thay vì gọi thẳng `scan(root, n=1)`, vì `scan()` phụ thuộc `discover_transcript_dirs()` (đọc `git worktree list` thật) mà sandbox test không có `.git` — cùng giới hạn đã ghi ở Task 2 Step 5. Đây KHÔNG phải trùng lặp logic tuỳ tiện: nó là cách né phụ thuộc git trong self-test, giữ `scan()` không đổi cho production. Nếu thấy trùng lặp quá nhiều khi code thật, cân nhắc tách phần "cắt lát + chấm 1 file" của `scan()` ra một hàm `_scan_file(fpath, evs, cfg) -> int` dùng chung bởi cả `scan()` và `self_test()` — quyết định này để lúc code, không chốt cứng ở PLAN.

- [ ] **Step 4: chạy lại — PASS**

Chạy: `python3 harness/scripts/skill-evolve.py --self-test`
Mong đợi: `skill-evolve self-test: PASS`

- [ ] **Step 5: chạy toàn bộ self-test liên quan, xác nhận không hồi quy**

```bash
python3 fdk/tools/skill-usage.py --self-test
python3 harness/scripts/trace-grader.py --self-test
python3 harness/scripts/skill-evolve.py --self-test
python3 fdk/tools/medic.py --ci
```
Mong đợi: cả 4 lệnh PASS/exit 0.

- [ ] **Step 6: commit**

```bash
git add harness/scripts/skill-evolve.py
git commit -m "feat(skill-evolve): T5 — bundled self-test (fixture 2 lần gọi skill, 1 clean 1 corrupt-success)"
```

### Task 6: companion skill `skills/skill-evolve/SKILL.md` — bước judge mặc định BẬT

**Thoả:** FR-010

**Files:**
- Tạo: `skills/skill-evolve/SKILL.md`

**Interfaces:**
- Consumes: file `--draft` do Task 4 sinh (đã có mục `## SKILL.md hiện tại` + `## Bằng chứng`) — bước judge đọc TRỰC TIẾP file đó, không qua hàm Python nào.
- Produces: skill invocable qua `/skill-evolve`, hướng dẫn agent ghi mục `## Đánh giá LLM` vào đúng file `--draft` vừa đọc.

- [ ] **Step 1: viết test fail trước**

```bash
python3 -c "
from pathlib import Path
p = Path('skills/skill-evolve/SKILL.md')
print('exists:', p.is_file())
"
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Mong đợi: `exists: False`

- [ ] **Step 3: code tối thiểu cho pass — tạo `skills/skill-evolve/SKILL.md`**

```markdown
---
name: skill-evolve
description: Đo chất lượng thực thi của TỪNG skill riêng lẻ theo thời gian (không chỉ tần suất như skill-usage) — verdict tất định từ trace-grader, tích luỹ vào ledger; khi tỷ lệ lỗi vượt ngưỡng thì tự soạn đề xuất sửa đúng SKILL.md đó kèm nhận định LLM (agent-as-judge, mặc định bật), dừng ở /propose. Gọi khi user nói "đánh giá skill", "skill nào đang tệ", "chấm chất lượng skill", "skill-evolve", hoặc định kỳ trong /lint.
---

# Skill: skill-evolve

## When to use
- Định kỳ (vd trong `/lint`) để quét N session gần nhất, cập nhật ledger chất lượng per-skill.
- Khi muốn biết skill nào đang có tỷ lệ lỗi cao (`--report`).
- Khi một skill đã `DRAFT-ELIGIBLE` và muốn soạn đề xuất sửa nó (`--draft <skill_id>`).

## Steps
1. Quét: `python3 harness/scripts/skill-evolve.py --scan [N]` — ghi verdict per-skill vào ledger cục bộ (`harness/metrics/skill-evolve-ledger.jsonl`).
2. Xem leaderboard: `python3 harness/scripts/skill-evolve.py --report` — liệt kê skill nào `DRAFT-ELIGIBLE`.
3. Với một skill eligible: `python3 harness/scripts/skill-evolve.py --draft <skill_id>` — sinh stub tại `llmwiki/wiki/sources/draft/DDMMYY-skill-evolve-<skill_id>.md`, chứa SKILL.md hiện tại + bảng bằng chứng.
4. **Bước judge (mặc định BẬT — CHỈ chạy tới đây khi bước 3 đã thật sự sinh file, tức skill đã `DRAFT-ELIGIBLE`):** đọc nguyên văn file stub vừa sinh — cả mục `## SKILL.md hiện tại` lẫn `## Bằng chứng` — rồi tự đánh giá bằng chính reasoning của bạn (KHÔNG gọi thêm API/model nào khác — bạn CHÍNH LÀ judge): tỷ lệ lỗi này có thật sự do NỘI DUNG SKILL.md gây ra (mô tả mơ hồ, thiếu bước, sai giả định), hay do NGỮ CẢNH SỬ DỤNG (skill bị gọi sai tình huống, ngoài phạm vi "When to use")? Ghi nhận định — cụ thể, trích dẫn đúng dòng bằng chứng đã đọc, không chung chung — vào một mục MỚI `## Đánh giá LLM` chèn ngay dưới mục `## Bằng chứng` của chính file stub đó.
5. Trình file đã có `## Đánh giá LLM` cho `/propose` hoàn thiện — vẫn STOP, chờ người duyệt. `skill-evolve` không bao giờ tự sửa `SKILL.md`.

## Rules
- Bước judge (Step 4) CHỈ chạy trên file `--draft` đã sinh THẬT (skill đã `DRAFT-ELIGIBLE`) — không phán đoán trên skill chưa đủ mẫu/chưa vượt ngưỡng (tốn token vô ích, và kết luận trên mẫu nhỏ không đáng tin).
- Judge là chính agent đang gọi skill này (không phải một lệnh gọi API con) — không thêm dependency hay API key nào; tái dùng reasoning đã có sẵn trong phiên.
- Never auto-promote — nhận định LLM chỉ là MỘT mục trong stub, người duyệt vẫn phải bấm chấp thuận ở `/propose`.
```

- [ ] **Step 4: chạy lại — PASS**

```bash
python3 -c "
from pathlib import Path
p = Path('skills/skill-evolve/SKILL.md')
print('exists:', p.is_file())
print('has_when_to_use:', '## When to use' in p.read_text(encoding='utf-8'))
print('has_judge_step:', 'Đánh giá LLM' in p.read_text(encoding='utf-8'))
"
```
Mong đợi: `exists: True`, `has_when_to_use: True`, `has_judge_step: True`

- [ ] **Step 5: đăng ký skill (khuôn `new-skill.md`/`fdk.md` — canonical vừa tạo cần mirror + xuất hiện trong registry)**

```bash
bash fdk/tools/sync-skill.sh skill-evolve
python3 fdk/tools/build-capabilities.py
```
Mong đợi: `sync-skill.sh` in xác nhận đồng bộ `skills/skill-evolve/SKILL.md` → mirror `llmwiki/skills/.../skill-evolve.md` + bản cài `~/.claude/skills/skill-evolve/SKILL.md`, không báo lệch; `build-capabilities.py` in `skill-evolve` xuất hiện trong danh sách skill (đếm skill tăng thêm 1 so với trước Task 6).

- [ ] **Step 6: commit**

```bash
git add skills/skill-evolve/SKILL.md llmwiki/skills llmwiki/AGENT.md llmwiki/CLAUDE.md fdk/CAPABILITIES.md
git commit -m "feat(skill-evolve): T6 — companion skill /skill-evolve, bước judge mặc định bật khi DRAFT-ELIGIBLE"
```

## Cấm placeholder — tự kiểm

Không còn "để sau"/"tuỳ biến sau" nào trong 6 task trên — mọi bước đổi code có code đầy đủ, mọi lệnh chạy có output mong đợi cụ thể. Task 2 Step 5 và Task 5 có một giới hạn THẬT (phụ thuộc `git worktree list` trong sandbox test) — đã nêu rõ nguyên nhân + hướng xử lý, không phải mô tả suông.

## Self-review

**Phủ SPEC.** FR-001→FR-010 đều có task nhận: FR-001→T1, FR-002/003/004/005→T2, FR-006/009→T3, FR-007/008→T4, FR-010→T6, toàn bộ verify tích hợp→T5. SC-001→006 đều có bước chạy-thử tương ứng (T2 Step 5 = SC-001/002/005, T3 Step 5 + T5 = SC-003, T4 Step 4 + T5 = SC-004, T6 Step 4 = SC-006).

**Quét placeholder.** Không còn mô tả suông — mọi task có code Python đầy đủ, lệnh chạy chính xác, output mong đợi cụ thể (kể cả nhánh lỗi/guard).

**Nhất quán tên/kiểu.** `scan()`/`report()`/`draft()`/`_leaderboard()`/`_skill_md_path()`/`LEDGER`/`STATE_REL`/`CONFIG_NAME`/`DEFAULT_CFG` dùng đúng một tên xuyên suốt 6 task — không đổi tên giữa chừng. `bnal_metrics`/`bnal_config`/`skill_usage()`/`trace_grader()` là 4 điểm import DUY NHẤT, không có chỗ nào import lại theo cách khác. Task 6's mục `## Đánh giá LLM` là tên MỚI duy nhất được dùng — không lẫn với `## Bằng chứng` (Task 4) hay `## SKILL.md hiện tại` (Task 4).
