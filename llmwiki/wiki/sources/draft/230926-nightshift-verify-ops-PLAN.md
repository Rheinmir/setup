---
type: draft
title: "PLAN — Nightshift phần 2: kiểm, tích hợp, phục hồi, vận hành (N14…N24)"
status: proposed
tags: [plan, nightshift, overnight-loop, orca-graph]
timestamp: 2026-09-23
---

# PLAN 230926 — Nightshift phần 2: kiểm, tích hợp, phục hồi, vận hành (N14…N24)

Nguồn: [[230926-overnight-loop-PRD]] §09 (ticket N01–N24), contract §06, invariant §07, AT §10, crash matrix §11. Phần 2 của `230926-nightshift-core`; deps xuyên graph dạng `230926-nightshift-core/tN`. N14/N23/N24 là HITL (cần provider/host VM).

## Global constraints
- Repo đích: `/Users/giatran/orca/nightshift` (repo MỚI, độc lập — D01: core KHÔNG import Overstack/Orca/llmwiki/`~/.claude`). Đường dẫn **Files:** tính từ gốc repo; code nằm dưới `src/nightshift/`.
- Python ≥ 3.11 (máy dev: gọi `python3.11`, `python3` mặc định là 3.9), CHỈ stdlib trong core (§05 Dependency rule); provider/importer/reporter UI ngoài core, CLI tiêm adapter.
- Test chạy bằng `python3 -m unittest` (không pytest), không network, không model thật; mock provider cho mọi AT.
- Tiền = integer micro-USD, thời gian UTC ISO-8601, deadline epoch trong DB; UUID cho ID (§06).
- Invariant §07 là luật cứng: 1 active attempt/revision, reserve+dispatch cùng transaction, `spent+reserved+requested<=cap`, deadline không reset, succeeded luôn có receipt, worker không ghi ledger/oracle, không sửa checkout gốc, ready rỗng ≠ completed.
- Mỗi task: test kiểm BẤT BIẾN + ca mất/sai dữ liệu theo AT của ticket, không mirror từng dòng code.
- Không AI-attribution trong commit.

### Task 1: N14 — Một adapter model thật
**Kind:** integration
**Thoả:** PRD §09 N14 · M07 · 2 ngày + senior review
**Depends:** 230926-nightshift-core/t7 (data), 230926-nightshift-core/t10 (data), 230926-nightshift-core/t13 (data)
**Mode:** HITL
**Files:**
- Tạo: `src/nightshift/providers/chosen_provider.py`
- Tạo: `tests/test_real_provider_contract.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N14 + test xanh
**Chờ người:** cần provider thật + credential (operator chọn provider, senior review SDK) — user cung cấp host sau; KHÔNG dispatch headless.
**Làm:** operator chọn provider/phiên bản CLI/API; preflight capabilities; credential gateway; limit token/calls; cancel; usage reconciliation.
**Mẫu:** Protocol mục 06; không có câu lệnh provider giả đoán flag.
**AC:** chạy contract suite mock và live trên một fixture trong daytime budget; AT13/24/27.
**Bẫy:** adapter import SDK vào core; hứa dollar cap khi provider không chặn max usage.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_real_provider_contract -v`
**Code:** chưa có — adapter thật chờ user chốt provider (PRD cấm đoán flag CLI/API); sẽ kế thừa bộ contract có sẵn:
```python
# tests/contracts/test_provider_suite.py (đã có) — adapter mới chỉ cần:
class RealProviderContract(ProviderContractSuite, unittest.TestCase):
    def make(self, tmp, behaviour):
        return ChosenProvider(...)  # N14: cấu hình do operator cung cấp
```

### Task 2: N15 — Verifier độc lập và frozen oracle
**Kind:** test
**Thoả:** PRD §09 N15 · M08 · 2 ngày
**Depends:** 230926-nightshift-core/t10 (data), 230926-nightshift-core/t12 (data), 230926-nightshift-core/t13 (data)
**Files:**
- Tạo: `src/nightshift/verification/runner.py`
- Tạo: `src/nightshift/verification/receipt.py`
- Tạo: `tests/test_verification.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N15 + test xanh
**Làm:** snapshot oracle trước run; candidate chạy môi trường riêng; hash input/environment/oracle; required checks; log artifact; pass lặp hai lần với test nền có rủi ro flaky.
**Mẫu:** `verifier.py`.
**AC:** AT20/25/27; model nói pass nhưng test fail → fail; verifier crash → inconclusive; xanh lần đầu đỏ lần sau không done.
**Bẫy:** chạy test bên trong checkout worker đã sửa mà không so oracle.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_verification -v`
**Code:** `tests/test_verification.py` (trích 18 dòng đầu, bản thật)
```python
"""N15 · AT20/AT25/AT27/AT28: fresh-tree verify, frozen oracle, flaky=inconclusive."""
import copy
import os
import time
import unittest
from pathlib import Path

from nightshift.verification.runner import verify
from nightshift.workspace.create import create
from nightshift.workspace.git_candidate import collect
from tests.helpers import approved_run, task

FIX = 'def parse_pair(text):\n    key, value = text.split("=", 1)\n    return key.strip(), value.strip()\n'


class VerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp, self.m, self.db = approved_run(self, [task("T1")])
```

### Task 3: N16 — Integration coordinator
**Kind:** integration
**Thoả:** PRD §09 N16 · M06/M08 · 2 ngày + senior review
**Depends:** 230926-nightshift-core/t4 (data), 230926-nightshift-core/t12 (data), Task 2 (data)
**Files:**
- Tạo: `src/nightshift/integration/coordinator.py`
- Tạo: `tests/test_integration.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N16 + test xanh
**Làm:** exclusive review branch lock; intent durable; apply candidate trên head hiện tại; combined tests; Git ref CAS; receipt; không auto-push.
**Mẫu:** `integration_recipe.py` trong phần code bổ sung.
**AC:** AT31/32; task riêng xanh nhưng kết hợp đỏ → không publish; head đổi thì rebuild/reverify.
**Bẫy:** merge conflict tự giải bằng model rồi dùng receipt cũ; DB done trước ref update.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_integration -v`
**Code:** `tests/test_integration.py` (trích 18 dòng đầu, bản thật)
```python
"""N16 · AT31/AT32: combined regression refuses publish; moved head -> rebuild + reverify."""
import time
import unittest

from nightshift.integration.coordinator import head, integrate, review_ref
from nightshift.store.claims import advance, claim
from nightshift.store.db import tasks, transaction
from nightshift.verification.runner import default_runner
from nightshift.workspace.create import create, git
from nightshift.workspace.git_candidate import collect
from tests.helpers import approved_run, task

EST = {"calls": 1, "tokens": 0, "micro": 0}
FIX = 'def parse_pair(text):\n    key, value = text.split("=", 1)\n    return key.strip(), value.strip()\n'


class IntegrationTests(unittest.TestCase):
    def setUp(self):
```

### Task 4: N17 — Retry và no-progress classifier
**Kind:** build
**Thoả:** PRD §09 N17 · M09 · 1 ngày
**Depends:** 230926-nightshift-core/t7 (data), 230926-nightshift-core/t13 (data), Task 2 (data)
**Files:**
- Tạo: `src/nightshift/recovery/retry.py`
- Tạo: `tests/test_retry.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N17 + test xanh
**Làm:** transient retry hữu hạn; backoff seed; auth/policy nonretryable; repeated failure fingerprint; budget giữ cùng run.
**Mẫu:** retry bounded ở `engine.py`, classifier mục 07.
**AC:** AT08/14/27; transient có retry, AUTH không; không ngủ qua deadline rồi spawn.
**Bẫy:** hash thay do timestamp/log bị xem là tiến triển.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_retry -v`
**Code:** `tests/test_retry.py` (trích 18 dòng đầu, bản thật)
```python
"""N17 · AT08/AT14/AT27: bounded retry, AUTH not retried, backoff within deadline."""
import unittest

from nightshift.recovery.retry import backoff, decide, fingerprint


def d(**kw):
    base = dict(code="TRANSIENT", attempts=1, max_attempts=3, fp="a", last_fp=None, now=0,
                deadline=10_000, min_attempt_s=60, seed="s")
    base.update(kw)
    return decide(**base)


class RetryTests(unittest.TestCase):
    def test_transient_retries_with_growing_backoff(self):
        r1, r2 = d(attempts=1), d(attempts=2, fp="b", last_fp="a")
        self.assertEqual((r1["action"], r2["action"]), ("retry", "retry"))
        self.assertGreaterEqual(r1["retry_at"], 10)
```

### Task 5: N18 — Crash recovery và reconciliation
**Kind:** fix
**Thoả:** PRD §09 N18 · M09 · 2 ngày + senior review
**Depends:** 230926-nightshift-core/t4 (data), 230926-nightshift-core/t6 (data), Task 3 (data), Task 4 (data)
**Files:**
- Tạo: `src/nightshift/recovery/reconcile.py`
- Tạo: `tests/test_crash_matrix.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N18 + test xanh
**Làm:** fence, inspect cgroup/PID identity/artifact/outbox/ref; unknown không retry mù; accept durable result bằng verify lại; operator resolution có event.
**Mẫu:** `engine.py` chỉ chuyển unknown; nâng cấp theo bảng mục 11.
**AC:** AT06/10/11/22/33; kill ở từng boundary không duplicate publish hoặc mất task.
**Bẫy:** thấy process chết là coi không có effect.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_crash_matrix -v`
**Code:** `tests/test_crash_matrix.py` (trích 18 dòng đầu, bản thật)
```python
"""N18 · AT06/AT10/AT11/AT22/AT33: every crash boundary -> no duplicate publish, no lost task."""
import json
import subprocess
import sys
import time
import unittest

from nightshift.execution.supervisor import process_identity
from nightshift.integration import coordinator as integ
from nightshift.policy.budget import snapshot
from nightshift.recovery.reconcile import apply, plan, resolve
from nightshift.errors import NightshiftError
from nightshift.store.claims import advance, claim
from nightshift.store.db import tasks, transaction
from nightshift.verification import receipt as rc
from nightshift.workspace.create import create
from tests.helpers import approved_run, git, task

```

### Task 6: N19 — Report sáng hôm sau
**Kind:** docs
**Thoả:** PRD §09 N19 · M10 · 1 ngày
**Depends:** 230926-nightshift-core/t3 (data), Task 2 (data)
**Files:**
- Tạo: `src/nightshift/reporting/report.py`
- Tạo: `src/nightshift/reporting/report.html`
- Tạo: `tests/test_report.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N19 + test xanh
**Làm:** read snapshot DB; generated HTML+JSON; evidence relative links; redact secrets; highlight quyết định cần người.
**Mẫu:** `report.py`.
**AC:** AT34; tổng task đúng số manifest, unknown không nằm trong completed; thiếu receipt báo broken evidence.
**Bẫy:** text model tự kể số task hoặc thiếu phần budget held.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_report -v`
**Code:** `tests/test_report.py` (trích 18 dòng đầu, bản thật)
```python
"""N19 · AT29/AT34: derived counts, verified != integrated, unknown not completed, redaction."""
import json
import unittest

from nightshift.reporting.report import build, write
from nightshift.store.claims import claim, fence, finish
from nightshift.store.db import transaction
from nightshift.verification import receipt as rc
from tests.helpers import approved_run, task

EST = {"calls": 1, "tokens": 10, "micro": 0}


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp, self.m, self.db = approved_run(
            self, [task(f"T{i}") for i in range(1, 7)],
            budget={"max_calls": 20, "max_tokens": 1000, "max_cost_microusd": 100})
```

### Task 7: N20 — CLI/control và run locking
**Kind:** build
**Thoả:** PRD §09 N20 · M11 · 1 ngày
**Depends:** 230926-nightshift-core/t8 (data), 230926-nightshift-core/t9 (data), Task 6 (data)
**Files:**
- Tạo: `src/nightshift/cli.py`
- Tạo: `tests/test_cli.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N20 + test xanh
**Làm:** validate/preflight/start/status/pause/resume/cancel/reconcile/report; JSON output; exit codes C07; lock scope run; lệnh nhiều lần idempotent.
**Mẫu:** `cli.py`, `engine.py` fcntl.
**AC:** AT09/15/16/35; hai start cùng run chỉ một coordinator; stale lock sau crash không chặn vĩnh viễn; đọc status không tạo run trống.
**Bẫy:** delete file lock bằng tay khi process cũ còn chạy.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_cli -v`
**Code:** `tests/test_cli.py` (trích 18 dòng đầu, bản thật)
```python
"""N20 · AT09/AT15/AT16/AT35 + US01/US03: CLI end to end on the fixture with the mock."""
import json
import threading
import time
import unittest
from pathlib import Path

from nightshift import cli
from nightshift.engine import Engine, coordinator_lock
from nightshift.errors import NightshiftError
from nightshift.util import tree_hash
from tests.helpers import TempDir, dump, git, manifest, task

import os
os.environ.setdefault("NIGHTSHIFT_BACKOFF_SCALE", "0.01")

FIX = 'def parse_pair(text):\n    key, value = text.split("=", 1)\n    return key.strip(), value.strip()\n'
WRONG = FIX.replace("value.strip()", "value.strip().lower()")
```

### Task 8: N21 — Import/export adapter Overstack tùy chọn
**Kind:** integration
**Thoả:** PRD §09 N21 · M11 · 1 ngày
**Depends:** 230926-nightshift-core/t2 (data), Task 7 (data)
**Files:**
- Tạo: `src/nightshift/adapters/overstack_import.py`
- Tạo: `tests/test_optional_import.py`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N21 + test xanh
**Làm:** map FR/SC, verify, scope, deps; reject dữ liệu thiếu; không tự cấp quyền từ skill text.
**Mẫu:** `contracts.py` là validation cuối.
**AC:** AT36; bỏ toàn bộ adapter package thì core test vẫn xanh.
**Bẫy:** import event cũ rồi nhận luôn completed dù hash input/receipt không khớp.
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.test_optional_import -v`
**Code:** `src/nightshift/adapters/overstack_import.py` (trích 18 dòng đầu, bản thật)
```python
"""Optional adapter (ticket N21): Overstack PLAN.md -> C01 DRAFT, run state -> JSON export.

The core never imports this module. A draft is NOT approved: the operator still runs
`nightshift validate` and `start --approved-by`. Nothing in the PLAN text can grant
policy, budget or network: those come only from operator arguments.
"""
import json
import re
from pathlib import Path

from .. import MANIFEST_SCHEMA
from ..errors import ManifestError
from ..util import tree_hash

TASK_RE = re.compile(r"^### Task (\d+):\s*(.+?)\s*$", re.M)
FIELD_RE = re.compile(r"^\*\*(Depends|Verify|Làm|Mode):\*\*\s*(.+?)\s*$", re.M)
FILE_RE = re.compile(r"^- (?:Tạo|Sửa|Create|Modify|Test):\s*`([^`]+)`", re.M)
DEP_RE = re.compile(r"Task (\d+)")
```

### Task 9: N22 — Chaos và contract test suite
**Kind:** test
**Thoả:** PRD §09 N22 · M12 · 2 ngày
**Depends:** Task 5 (data), Task 7 (data)
**Files:**
- Tạo: `tests/chaos/`
- Tạo: `tests/contracts/`
- Tạo: `scripts/run-chaos.sh`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N22 + test xanh
**Làm:** fault injection tại commit/spawn/rename/verify/ref CAS/report; recorded seed; mock clock; không chỉ test happy path.
**Mẫu:** `test_core.py` (10 tests đã chạy); mở rộng lên AT01–36.
**AC:** tất cả P0 pass; mỗi invariant có negative case chứng minh gate cắn.
**Bẫy:** assert implementation tự trả “true”; mock hết Git/process/SQLite rồi nhận recovery production pass.
**Verify:** `cd /Users/giatran/orca/nightshift && bash scripts/run-chaos.sh`
**Code:** `tests/chaos/test_chaos.py` (trích 18 dòng đầu, bản thật)
```python
"""N22 · chaos: SIGKILL-equivalent at every crash boundary, then resume to the end.

Each seed picks a fault point and a visit count, kills the real coordinator process
there (os._exit(137): no finally, no cleanup), restarts it until the run stops, and
checks the safety invariants of PRD §07 on the final ledger + Git state.
Seeds: NIGHTSHIFT_CHAOS_SEEDS (default 8; gate G1 asks for 20).
"""
import json
import os
import random
import subprocess
import sys
import unittest
from pathlib import Path

from nightshift.store.db import connect
from nightshift.util import tree_hash
from tests.helpers import TempDir, dump, git, manifest, task
```

### Task 10: N23 — Packaging, service và canary
**Kind:** deploy
**Thoả:** PRD §09 N23 · M12 · 1,5 ngày
**Depends:** 230926-nightshift-core/t10 (data), Task 1 (data), Task 9 (data)
**Mode:** HITL
**Files:**
- Tạo: `deploy/nightshift.service`
- Tạo: `deploy/README.md`
- Tạo: `scripts/canary.sh`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N23 + test xanh
**Chờ người:** cần host Linux/VM riêng (systemd, cgroup, image digest) — user cung cấp host sau; KHÔNG dispatch headless.
**Làm:** pinned package/image digests; dedicated user; service restart có backoff; host cgroup cleanup; no unlimited restart; startup reconcile trước admission.
**Mẫu:** rollout checklist mục 12; adapter phải preflight thật.
**AC:** G0→G5, AT17/18/33; reboot không tự spawn trước reconcile; service stop không orphan.
**Bẫy:** dùng cron mỗi phút để đẻ coordinator mới; auto restart reset deadline.
**Verify:** `cd /Users/giatran/orca/nightshift && bash scripts/canary.sh --check`
**Code:** `scripts/canary.sh` (trích 18 dòng đầu, bản thật)
```bash
#!/usr/bin/env bash
# N23/N24 canary. Two modes:
#   --check   static readiness (runs anywhere): unit file sane, profile pinned, suite green.
#   --run     on the dedicated Linux host only: one fixture night with the mock provider in
#             the real sandbox + service, then writes a canary receipt (gate G2/G4 evidence).
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3.11}"
mode="${1:---check}"
fail() { echo "CANARY FAIL: $*" >&2; exit 1; }

check() {
  unit=deploy/nightshift.service
  grep -q '^StartLimitBurst=' "$unit" || fail "unit has no restart cap"
  grep -q '^KillMode=control-group' "$unit" || fail "unit would leave orphan workers"
  grep -q '^RestartPreventExitStatus=0 2 3 4 5' "$unit" || fail "unit restarts on non-crash exits"
  grep -q 'nightshift resume' "$unit" || fail "unit must resume (reconcile first), not start"
  "$PY" - <<'PY' || fail "worker profile"
```

### Task 11: N24 — UAT và bàn giao vận hành
**Kind:** release
**Thoả:** PRD §09 N24 · M12 · 1 ngày + canary nights
**Depends:** Task 6 (data), Task 8 (data), Task 10 (data)
**Mode:** HITL
**Files:**
- Tạo: `docs/operator-runbook.md`
- Tạo: `docs/uat.md`
- Tạo: `release-receipt.json`
**Interfaces:**
- Consumes: output của các task ở dòng Depends (contract §06 tương ứng)
- Produces: module theo ticket N24 + test xanh
**Chờ người:** cần host VM chạy 3 đêm canary + operator ký nhận — user cung cấp host sau; KHÔNG dispatch headless.
**Làm:** operator chạy 3 tình huống success/partial/recovery, kiểm report, restore snapshot; ghi owner xử lý mỗi reason.
**Mẫu:** mục 10–13.
**AC:** có đủ evidence 3 đêm canary, ký nhận scope, kill SLO và rollback rehearsal.
**Bẫy:** coi 8 giờ process không chết là tiêu chí duy nhất.
**Verify:** `cd /Users/giatran/orca/nightshift && bash scripts/canary.sh --check`
**Code:** `scripts/canary.sh` (trích 18 dòng đầu, bản thật)
```bash
#!/usr/bin/env bash
# N23/N24 canary. Two modes:
#   --check   static readiness (runs anywhere): unit file sane, profile pinned, suite green.
#   --run     on the dedicated Linux host only: one fixture night with the mock provider in
#             the real sandbox + service, then writes a canary receipt (gate G2/G4 evidence).
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3.11}"
mode="${1:---check}"
fail() { echo "CANARY FAIL: $*" >&2; exit 1; }

check() {
  unit=deploy/nightshift.service
  grep -q '^StartLimitBurst=' "$unit" || fail "unit has no restart cap"
  grep -q '^KillMode=control-group' "$unit" || fail "unit would leave orphan workers"
  grep -q '^RestartPreventExitStatus=0 2 3 4 5' "$unit" || fail "unit restarts on non-crash exits"
  grep -q 'nightshift resume' "$unit" || fail "unit must resume (reconcile first), not start"
  "$PY" - <<'PY' || fail "worker profile"
```

## Origin

- Sinh bằng `scratchpad/gen_nightshift_plans.py` từ [[230926-overnight-loop-PRD]] §09 (ticket N01–N24); khối **Code** là phần đầu file test THẬT trong repo `/Users/giatran/orca/nightshift` (commit 044a974 · 20e9aaa · 19161be), không phải code minh hoạ.
