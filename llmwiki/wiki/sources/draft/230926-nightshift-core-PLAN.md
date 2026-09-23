---
type: draft
title: "PLAN — Nightshift phần 1: nền dữ liệu, điều phối, thực thi cô lập (N01…N13)"
status: proposed
tags: [plan, nightshift, overnight-loop, orca-graph]
timestamp: 2026-09-23
---

# PLAN 230926 — Nightshift phần 1: nền dữ liệu, điều phối, thực thi cô lập (N01…N13)

Nguồn: [[230926-overnight-loop-PRD]] §09 (ticket N01–N24), contract §06, invariant §07, AT §10, crash matrix §11. 24 ticket vượt trần 20 node/graph nên tách HAI graph: `230926-nightshift-core` (section A–C, N01…N13) và `230926-nightshift-verify-ops` (N14…N24).

## Global constraints
- Repo đích: `/Users/giatran/orca/nightshift` (repo MỚI, độc lập — D01: core KHÔNG import Overstack/Orca/llmwiki/`~/.claude`). Đường dẫn **Files:** tính từ gốc repo; code nằm dưới `src/nightshift/`.
- Python ≥ 3.11 (máy dev: gọi `python3.11`, `python3` mặc định là 3.9), CHỈ stdlib trong core (§05 Dependency rule); provider/importer/reporter UI ngoài core, CLI tiêm adapter.
- Test chạy bằng `python3 -m unittest` (không pytest), không network, không model thật; mock provider cho mọi AT.
- Tiền = integer micro-USD, thời gian UTC ISO-8601, deadline epoch trong DB; UUID cho ID (§06).
- Invariant §07 là luật cứng: 1 active attempt/revision, reserve+dispatch cùng transaction, `spent+reserved+requested<=cap`, deadline không reset, succeeded luôn có receipt, worker không ghi ledger/oracle, không sửa checkout gốc, ready rỗng ≠ completed.
- Mỗi task: test kiểm BẤT BIẾN + ca mất/sai dữ liệu theo AT của ticket, không mirror từng dòng code.
- Không AI-attribution trong commit.

### Task 1: N01 — Khởi tạo package và mock fixture
**Kind:** build
**Thoả:** PRD §09 N01 · M01 · 0,5 ngày
**Files:**
- Tạo: `pyproject.toml`
- Tạo: `src/nightshift/src/nightshift/__init__.py`
- Tạo: `tests/fixtures/repo/`
- Tạo: `README.md`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N01 + test xanh
**Làm:** tạo CLI entrypoint, fixture repo có lỗi một dòng và acceptance test cố định; đặt version schema.
**Mẫu:** `cli.py`, `manifest.json`.
**AC:** máy không có Orca/Overstack vẫn chạy `python3 -m unittest discover -v`; chưa cấu hình provider vẫn chạy mock.
**Bẫy:** import từ `~/.claude` hoặc dùng cwd ngầm.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest discover -s tests -t . -v`
**Code:** `tests/helpers.py` (trích 18 dòng đầu, bản thật)
```python
"""Shared fixtures: a throwaway git repo + frozen oracle + valid manifest."""
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from nightshift import MANIFEST_SCHEMA
from nightshift.util import iso, tree_hash

FIX = Path(__file__).resolve().parent / "fixtures"
ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@t", "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"}


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
```

### Task 2: N02 — Validate và đóng băng manifest
**Kind:** build
**Thoả:** PRD §09 N02 · M01 · 1 ngày
**Depends:** Task 1 (data)
**Files:**
- Tạo: `src/nightshift/contracts/manifest.py`
- Tạo: `src/nightshift/contracts/manifest.schema.json`
- Tạo: `tests/test_manifest.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N02 + test xanh
**Làm:** validate field/type, deps, cycle, paths, baseline, verify profile, cap; approve tạo snapshot ngoài writable mount.
**Mẫu:** `contracts.py`.
**AC:** AT01–03, AT28; cùng JSON khác whitespace có cùng hash; đổi acceptance làm khác hash.
**Bẫy:** hash bao gồm chính field hash; nhận NaN; boolean bị xem là integer; path symlink thoát root.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_manifest -v`
**Code:** `tests/test_manifest.py` (trích 18 dòng đầu, bản thật)
```python
"""N02 · AT01–03, AT28: manifest validation + canonical hash + frozen snapshot."""
import copy
import json
import os
import unittest
from pathlib import Path

from nightshift.contracts.manifest import approve, load_json, manifest_hash, validate
from nightshift.errors import ManifestError
from tests.helpers import TempDir, manifest, task


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TempDir(self).path
        self.m = manifest(self.tmp, [task("T1"), task("T2", ["T1"])])

    def code(self, data, **kw):
```

### Task 3: N03 — SQLite schema và transaction helper
**Kind:** data
**Thoả:** PRD §09 N03 · M02 · 1,5 ngày
**Depends:** Task 2 (data)
**Files:**
- Tạo: `src/nightshift/store/schema.sql`
- Tạo: `src/nightshift/store/db.py`
- Tạo: `tests/test_store.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N03 + test xanh
**Làm:** tables runs/tasks/task_deps/attempts/events/reservations/outbox/artifacts; PK/FK/unique/check state; WAL+FULL; transaction helper rollback cả exception/cancel.
**Mẫu:** `store.py`.
**AC:** AT04/05; injected error giữa claim và reserve không để row nửa chừng; duplicate event không tăng counter.
**Bẫy:** ghi event ngoài transaction, dùng JSONL như DB đồng thời nhiều writer.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_store -v`
**Code:** `tests/test_store.py` (trích 18 dòng đầu, bản thật)
```python
"""N03 · AT04/AT05: atomic transactions, idempotent events, one active attempt."""
import sqlite3
import unittest

from nightshift.errors import NightshiftError
from nightshift.store.db import emit, initialize, run_row, tasks, transaction
from nightshift.util import now
from tests.helpers import approved_run, task


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp, self.m, self.db = approved_run(self, [task("T1"), task("T2", ["T1"])])
        self.rid = self.m["run_id"]

    def test_initialize_idempotent_and_changed_manifest_rejected(self):
        self.assertFalse(initialize(self.db, self.m))
        other = dict(self.m, approved_manifest_hash="f" * 64)
```

### Task 4: N04 — Migration, backup và outbox
**Kind:** migrate
**Thoả:** PRD §09 N04 · M02 · 1,5 ngày
**Depends:** Task 3 (data)
**Files:**
- Tạo: `src/nightshift/store/migrate.py`
- Tạo: `src/nightshift/store/outbox.py`
- Tạo: `tests/test_backup.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N04 + test xanh
**Làm:** `PRAGMA user_version`, backup API nhất quán, migration additive; unique op_key; consumer idempotent.
**Mẫu:** transaction/emit ở `store.py`; mở rộng bảng outbox theo C05.
**AC:** AT06/26; crash sau commit trước deliver vẫn drain đúng một logical effect; restore mở được run/report.
**Bẫy:** copy chỉ state.db khi WAL còn live; xóa outbox trước ack.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_backup -v`
**Code:** `tests/test_backup.py` (trích 18 dòng đầu, bản thật)
```python
"""N04 · AT06/AT26: outbox drains exactly one logical effect; WAL-safe backup/restore."""
import sqlite3
import unittest

from nightshift.errors import NightshiftError
from nightshift.store.db import connect, emit, tasks, transaction
from nightshift.store.migrate import LATEST, backup, migrate, restore, version
from nightshift.store.outbox import drain, enqueue, pending
from tests.helpers import approved_run, task


class OutboxBackupTests(unittest.TestCase):
    def setUp(self):
        self.tmp, self.m, self.db = approved_run(self, [task("T1")])

    def test_migrate_idempotent_and_too_new(self):
        self.assertEqual(version(self.db), LATEST)
        self.assertEqual(migrate(self.db), LATEST)
```

### Task 5: N05 — Scheduler thuần và propagation
**Kind:** build
**Thoả:** PRD §09 N05 · M03 · 1 ngày
**Depends:** Task 2 (data), Task 3 (data)
**Files:**
- Tạo: `src/nightshift/scheduler/ready.py`
- Tạo: `tests/test_scheduler.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N05 + test xanh
**Làm:** topo reject cycle; scheduler không sửa graph; stable priority + age; downstream fail chặn, task độc lập vẫn tiếp tục.
**Mẫu:** `admission.select_ready`.
**AC:** AT07/08/29; input order thay đổi không phá deps; missing dep không được bỏ qua.
**Bẫy:** ready rỗng thì kết luận hoàn thành.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_scheduler -v`
**Code:** `tests/test_scheduler.py` (trích 18 dòng đầu, bản thật)
```python
"""N05 · AT07/AT08/AT29: dependency gating, propagation, empty ready != completed."""
import random
import unittest

from nightshift.scheduler.ready import classify, propagate
from nightshift.store.db import deps, tasks, transaction
from tests.helpers import approved_run, task


def rows_(states, prio=None):
    return {t: {"state": s, "ord": i, "priority": (prio or {}).get(t, 0), "blocked_by": None,
                "next_eligible_at": None} for i, (t, s) in enumerate(states.items())}


class SchedulerTests(unittest.TestCase):
    D = {"T2": ["T1"], "T4": ["T2"]}

    def test_at07_dependent_waits_independent_runs(self):
```

### Task 6: N06 — Claim, lease, fencing, resource lock
**Kind:** build
**Thoả:** PRD §09 N06 · M03 · 2 ngày
**Depends:** Task 3 (data), Task 5 (data)
**Files:**
- Tạo: `src/nightshift/scheduler/admission.py`
- Tạo: `src/nightshift/store/claims.py`
- Tạo: `tests/test_claims.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N06 + test xanh
**Làm:** lấy đủ resources hoặc không lấy gì trong transaction; generation tăng; heartbeat có CAS; unique active attempt.
**Mẫu:** `admission.claim/finish`; production thêm lease và resource rows.
**AC:** AT09/10/11; hai coordinator tranh cùng task chỉ một winner; late completion không thay head/state.
**Bẫy:** kiểm quota rồi update ở hai transaction; PID reuse bị hiểu là worker cũ còn sống.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_claims -v`
**Code:** `tests/test_claims.py` (trích 18 dòng đầu, bản thật)
```python
"""N06 · AT09/AT10/AT11: one winner, generation fencing, lease heartbeat."""
import threading
import unittest

from nightshift.scheduler.admission import admit
from nightshift.store.claims import (StaleResult, advance, claim, expire_leases, fence, finish,
                                     heartbeat)
from nightshift.store.db import connect, tasks, transaction
from nightshift.util import now
from tests.helpers import approved_run, task

EST = {"calls": 1, "tokens": 1000, "micro": 0}


class ClaimTests(unittest.TestCase):
    def setUp(self):
        self.tmp, self.m, self.db = approved_run(
            self, [task("T1", resources=[{"name": "integration", "mode": "exclusive"}]),
```

### Task 7: N07 — Budget ledger và reservation
**Kind:** build
**Thoả:** PRD §09 N07 · M04 · 2 ngày
**Depends:** Task 3 (data)
**Files:**
- Tạo: `src/nightshift/policy/budget.py`
- Tạo: `tests/test_budget.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N07 + test xanh
**Làm:** reserve trước spawn, cap cho calls/tokens/cost; settle idempotent; unknown usage giữ held; global cap qua nhiều session; backoff vẫn tính wall time.
**Mẫu:** `admission.py` cho call cap + SQL mục 07 cho tiền.
**AC:** AT12/13/14; đồng thời request cuối budget chỉ một được nhận; restart không reset ledger.
**Bẫy:** refund khi model timeout nhưng provider có thể đã tính tiền; float gây sai số.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_budget -v`
**Code:** `tests/test_budget.py` (trích 18 dòng đầu, bản thật)
```python
"""N07 · AT04/AT12/AT13/AT14: reservation cap, unknown usage held, no reset on reopen."""
import threading
import unittest

from nightshift.policy.budget import reserve, resolve_unknown, settle, snapshot
from nightshift.store.claims import claim
from nightshift.store.db import connect, run_row, transaction
from tests.helpers import approved_run, task


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.tmp, self.m, self.db = approved_run(
            self, [task("T1"), task("T2")],
            budget={"max_calls": 3, "max_tokens": 1000, "max_cost_microusd": 500})
        self.rid = self.m["run_id"]

    def res(self, db=None, **est):
```

### Task 8: N08 — Policy gate và control intent
**Kind:** security
**Thoả:** PRD §09 N08 · M04/M11 · 1 ngày
**Depends:** Task 2 (data), Task 6 (data), Task 7 (data)
**Files:**
- Tạo: `src/nightshift/policy/authorize.py`
- Tạo: `src/nightshift/control.py`
- Tạo: `tests/test_control.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N08 + test xanh
**Làm:** pause ngừng admission, drain; cancel stop worker; effect v1 local-only; deny tăng quyền từ provider result.
**Mẫu:** `cli.py` control + `claim` check.
**AC:** AT15/16/30; cancelled không resume; pause lúc admission tranh chấp có ordering rõ theo transaction.
**Bẫy:** “cancel requested” hiển thị như “cancelled” trước khi có receipt kill.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_control -v`
**Code:** `tests/test_control.py` (trích 18 dòng đầu, bản thật)
```python
"""N08 · AT15/AT16/AT30: pause drains, cancel terminal, model cannot widen policy."""
import copy
import unittest

from nightshift import control
from nightshift.errors import NightshiftError
from nightshift.policy.authorize import PolicyDenied, authorize, breaker_open, screen_requests
from nightshift.contracts.manifest import manifest_hash
from nightshift.store.claims import claim, finish
from nightshift.store.db import transaction
from tests.helpers import approved_run, task

EST = {"calls": 1, "tokens": 0, "micro": 0}


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.tmp, self.m, self.db = approved_run(self, [task("T1"), task("T2")])
```

### Task 9: N09 — Process supervisor và watchdog
**Kind:** infra
**Thoả:** PRD §09 N09 · M05 · 2 ngày
**Depends:** Task 6 (data), Task 8 (data)
**Files:**
- Tạo: `src/nightshift/execution/supervisor.py`
- Tạo: `tests/test_process_tree.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N09 + test xanh
**Làm:** argv không shell interpolation; process group/cgroup; timeout setup/model/verify; TERM grace rồi KILL; reap; cap logs.
**Mẫu:** `process.py`.
**AC:** AT17/18; lệnh ngủ, spawn grandchild, không stdout, log flood đều dừng trong giới hạn.
**Bẫy:** `subprocess.run(timeout=...)` chỉ xử lý leader, bỏ con; chỉ kiểm deadline ở đầu vòng.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_process_tree -v`
**Code:** `tests/test_process_tree.py` (trích 18 dòng đầu, bản thật)
```python
"""N09 · AT17/AT18: deadline kills leader+grandchild, log flood capped, stop honoured."""
import os
import sys
import time
import unittest

from nightshift.execution.supervisor import process_identity, run, same_process, scrubbed_env
from tests.helpers import TempDir

PY = sys.executable


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
```

### Task 10: N10 — Container sandbox và secret boundary
**Kind:** security
**Thoả:** PRD §09 N10 · M05 · 2 ngày + senior review
**Depends:** Task 9 (data)
**Files:**
- Tạo: `src/nightshift/execution/sandbox.py`
- Tạo: `deploy/worker-profile.json`
- Tạo: `tests/test_sandbox.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N10 + test xanh
**Làm:** rootless, read-only root, no network, caps/PID limits; credentials chỉ gateway; verifier mount oracle readonly.
**Mẫu:** supervisor là nền quản process, **chưa là sandbox**. Lệnh contract: `sandbox.spawn(argv, mounts, limits, network='deny')`.
**AC:** AT19/20; worker thử đọc home/token/store và ghi outside đều bị OS từ chối.
**Bẫy:** worktree hoặc allowlist prompt bị nhận là sandbox; mount socket điều khiển host.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_sandbox -v`
**Code:** `tests/test_sandbox.py` (trích 18 dòng đầu, bản thật)
```python
"""N10 · AT19/AT20 (policy half): mount/secret/network rules; live OS check is gated.

The live test proves OS denial and needs a rootless container host (G2, VM). Enable it
with NIGHTSHIFT_SANDBOX_LIVE=1 (and NIGHTSHIFT_SANDBOX_ROOTLESS=0 on Docker Desktop).
"""
import os
import sys
import time
import unittest
from pathlib import Path

from nightshift.execution.sandbox import (Mount, SandboxError, build_argv, load_profile, probe,
                                          spawn, validate_mounts)
from tests.helpers import TempDir


class SandboxPolicyTests(unittest.TestCase):
    def setUp(self):
```

### Task 11: N11 — Workspace và artifact store
**Kind:** build
**Thoả:** PRD §09 N11 · M06 · 1,5 ngày
**Depends:** Task 2 (data), Task 9 (data)
**Files:**
- Tạo: `src/nightshift/workspace/create.py`
- Tạo: `src/nightshift/artifacts/store.py`
- Tạo: `tests/test_artifacts.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N11 + test xanh
**Làm:** tên attempt unique, exclusive create; path resolve/symlink validation; write temp/fsync/rename + fsync directory; immutable hash check.
**Mẫu:** `workspace.py`, `worker.py` atomic output.
**AC:** AT21/22; rerun không xóa attempt cũ; crash trước rename không publish partial.
**Bẫy:** basename dùng task_id lặp rồi force remove worktree cũ.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_artifacts -v`
**Code:** `tests/test_artifacts.py` (trích 18 dòng đầu, bản thật)
```python
"""N11 · AT21/AT22: independent checkout at SHA, user tree untouched, atomic artifacts."""
import os
import unittest
from pathlib import Path

from nightshift.artifacts.store import ArtifactStore
from nightshift.errors import NightshiftError
from nightshift.util import tree_hash
from nightshift.workspace.create import create
from tests.helpers import TempDir, git, make_repo


class WorkspaceArtifactTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TempDir(self).path
        self.repo, self.sha = make_repo(self.tmp)

    def test_at21_dirty_user_checkout_untouched(self):
```

### Task 12: N12 — Git candidate và scope guard
**Kind:** security
**Thoả:** PRD §09 N12 · M06 · 1,5 ngày
**Depends:** Task 10 (data), Task 11 (data)
**Files:**
- Tạo: `src/nightshift/workspace/git_candidate.py`
- Tạo: `tests/test_scope.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N12 + test xanh
**Làm:** so toàn bộ tree so baseline; xử lý tracked/untracked/delete/rename/symlink/submodule/mode; reject protected files; không tự sửa test.
**Mẫu:** nguyên tắc prepare attempt ở `workspace.py`; dùng Git NUL-delimited paths, parse rename hai đường.
**AC:** AT20/23; sửa/xóa/rename oracle đều fail; checkout người dùng dirty không đổi byte.
**Bẫy:** chỉ kiểm file mới xuất hiện trong `git status`, bỏ file đã dirty từ trước.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_scope -v`
**Code:** `tests/test_scope.py` (trích 18 dòng đầu, bản thật)
```python
"""N12 · AT20/AT23: oracle edits rejected; odd names/rename/symlink/submodule/mode caught."""
import os
import unittest

from nightshift.workspace.create import create
from nightshift.workspace.git_candidate import collect
from tests.helpers import TempDir, git, make_repo

ALLOWED = ["src/parser.py", "src/new file.py"]
PROTECTED = ["acceptance/**", "tests/**", ".github/**"]


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TempDir(self).path
        self.repo, self.sha = make_repo(self.tmp)
        self.ck = create(self.tmp / "run", self.repo, self.sha, "a1b2c3d4-0001") / "checkout"

```

### Task 13: N13 — Provider protocol + mock
**Kind:** integration
**Thoả:** PRD §09 N13 · M07 · 1 ngày
**Depends:** Task 2 (data), Task 9 (data)
**Files:**
- Tạo: `src/nightshift/providers/base.py`
- Tạo: `src/nightshift/providers/mock.py`
- Tạo: `tests/test_provider_contract.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N13 + test xanh
**Làm:** strict parser, output cap, ID/generation check, mock ok/fail_first/timeout/crash/malformed/late.
**Mẫu:** `worker.py`, `verifier.py` schema validation.
**AC:** AT24; mock không network; null JSON/missing usage không chuyển task xanh.
**Bẫy:** lấy dòng “SUCCESS” cuối stdout làm outcome; gửi full transcript vào verifier.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_provider_contract -v`
**Code:** `tests/test_provider_contract.py` (trích 18 dòng đầu, bản thật)
```python
"""N13 · AT24: strict result parsing; mock modes; model prose never becomes success."""
import json
import time
import unittest

from nightshift.providers.base import (ProtocolError, build_request, parse_result, synthetic)
from nightshift.providers.mock import MockProvider
from nightshift.workspace.create import create
from tests.helpers import TempDir, make_repo, task

TICKET = {"attempt_id": "a1b2c3d4-0001", "task_id": "T1", "generation": 1,
          "deadline_utc": "2030-01-01T00:00:00Z"}


def run_mock(case, mode, timeout=10, extra=None, should_stop=None):
    tmp = TempDir(case).path
    repo, sha = make_repo(tmp)
    d = create(tmp / "run", repo, sha, TICKET["attempt_id"])
```

## Origin

- Sinh bằng `scratchpad/gen_nightshift_plans.py` từ [[230926-overnight-loop-PRD]] §09 (ticket N01–N24); khối **Code** là phần đầu file test THẬT trong repo `/Users/giatran/orca/nightshift` (commit 044a974 · 20e9aaa · 19161be), không phải code minh hoạ.
