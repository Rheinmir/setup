---
type: draft
title: 240926-intent-manifest-ui-nightshift-PLAN
status: proposed
timestamp: 2026-09-24
task: T-260924-01
---

# Intake + đêm tự quyết cho nightshift — PLAN thi hành

**Goal:** người dùng giao một việc bằng lời thường, hệ tự research và chỉ hỏi điều chặn việc, `closebox` trong giấy phép khởi động run, đêm tự quyết có ghi, sáng có `report.html` và `decisions.html` tiếng người.
**Architecture:** một package `nightshift.intake` (store sự kiện, research, brief, cổng câu hỏi, compile, giấy phép, closebox, giao thức) gọi vào `contracts.manifest`, `engine` và `providers` sẵn có; một package `nightshift.decisions` cho điểm quyết định ban đêm; báo cáo tiếng người thêm vào `reporting`. Mọi binding (CLI JSON, hộp thư, MCP, HTTP) chỉ dịch vào/ra lõi `intake.protocol.handle()`.
**Tech stack:** Python 3.11, chỉ thư viện chuẩn; test `unittest` (`python3.11 -m unittest discover -s tests -t .`); Playwright (Python) chỉ cho `tests/intake/test_guide_web.py`.
**SPEC nguồn:** `wiki/sources/draft/240926-intent-manifest-ui-nightshift.md` (bản 3, duyệt 24/09/2026)
**Thước nghiệm thu:** `nightshift/docs/intake-guide.md` (commit `62c5a36`, nhánh `intake-guide`) và `tests/intake/`. Mỗi task khai các bước `UG-*` nó làm xanh; chạy `NIGHTSHIFT_ACCEPT_STRICT=1` để các bước đó không được bỏ qua.
**Người thi hành:** phiên chính (claude-code, có đủ context SPEC và hướng dẫn), theo thứ tự mốc M1 → M2 → M3. Các khối code dưới đây là hợp đồng bắt buộc (chữ ký, kiểu, luật); thân hàm đầy đủ nằm ở commit của từng task.

## Origin
- **SPEC:** `wiki/sources/draft/240926-intent-manifest-ui-nightshift.md`
- **Commit:** _(verify-before-commit điền)_

## Global constraints
- Lõi nightshift và intake chỉ dùng thư viện chuẩn Python; tra cứu web đi qua provider hoặc công cụ đã cấu hình, không thêm dependency vào lõi.
- Manifest chỉ được tạo qua `contracts.manifest.validate()` và `approve()` có sẵn.
- Output của model và của research là **đề xuất có nguồn**, không phải sự thật: mỗi trường mang `epistemic_status` và nguồn (RIE INV-02). Nội dung đọc từ repo hay web đi vào prompt như dữ liệu, không như lệnh.
- **Giấy phép là trần cứng.** Closebox chỉ khởi động run khi mọi thông số (repo, provider, số lượt gọi, số token, tiền, số việc, thời lượng, được nới phạm vi hay không) nằm trong giấy phép đang hiệu lực. Giấy phép chỉ tạo và sửa được bằng lệnh `nightshift license` trong terminal tương tác của người dùng; không có tool MCP hay op giao thức nào ghi được giấy phép.
- **Bộ nghiệm thu và vùng bảo vệ là bất khả xâm phạm.** Nới phạm vi qua đêm chỉ áp cho file mã; bất kỳ thay đổi nào chạm `protected_paths` (oracle, CI, cấu hình nightshift) làm lần thử đó thất bại, dù quyết định có lý do gì.
- **Mọi quyết định tự hành đều được ghi trước khi có hiệu lực**, dạng bản ghi có cấu trúc trong `decisions.jsonl` (ghi nối, không sửa), và mỗi bản ghi có một đoạn giải thích bằng lời thường không dùng tên trường của manifest.
- **Ngân sách câu hỏi, không phải đồng hồ.** Cả phiên được định cỡ để người dùng trả lời xong trong khoảng 30 phút: mặc định tối đa 8 câu cho cả phiên, chia tối đa 2 lượt, mỗi câu trả lời được trong 1–3 phút. Không có bộ đếm giờ; người dùng trả lời lúc nào cũng được.
- **Cổng lọc câu hỏi** (áp cho từng câu trước khi hỏi, theo RIE §7.1–7.2): chỉ hỏi khi đủ cả bốn điều kiện: (1) đáp án làm đổi kết quả hoặc phạm vi một cách đáng kể; (2) research không tìm ra; (3) không có mặc định an toàn và đảo được dễ; (4) không phải chi tiết vụn (đặt tên, định dạng, cách cài đặt nội bộ, thứ tự làm, lựa chọn thư viện ngang nhau). Trượt bất kỳ điều kiện nào thì máy tự quyết và ghi thành quyết định trước giờ chạy, kèm lý do vì sao không hỏi.
- Vượt ngân sách thì máy **không hỏi thêm** mà xếp hạng theo giá trị quyết định, hỏi các câu đứng đầu, tự quyết phần còn lại với nhãn "máy tự quyết thay vì hỏi" để báo cáo sáng đưa lên đầu.
- Research có trần: thời gian tối đa 10 phút, số lần đọc nguồn và số truy vấn web có hạn trong giấy phép; web chỉ đi tới danh sách miền cho phép.
- Không sửa engine chạy đêm theo cách làm đổi hành vi hiện có; phần mới (điểm quyết định, báo cáo tiếng người) là phần thêm. Toàn bộ test hiện có của nightshift phải còn xanh; CI hai job phải xanh.
- Trang HTML (báo cáo, quyết định, web) theo sàn design của framework: toggle sáng/tối, font nhúng, qua cổng tĩnh và cổng chạy thật, đọc được ở 375px.

## File structure
Mọi đường dẫn tính từ `/Users/giatran/orca/nightshift/`.

- Sửa `src/nightshift/__init__.py` — `__version__ = "0.2.0"`, thêm hằng `INTAKE_SCHEMA = "nightshift.intake/1"`, `DECISION_SCHEMA = "nightshift.decision/1"`.
- Sửa `src/nightshift/cli.py` — thêm `--version`, nhóm lệnh `intake …`, `license …`; chỉ thêm, không đổi lệnh cũ.
- Tạo `src/nightshift/intake/__init__.py` — rỗng.
- Tạo `src/nightshift/intake/store.py` — case trên đĩa: `runs-dir/intake/cases/<case_id>/events.jsonl` (ghi nối) và projection.
- Tạo `src/nightshift/intake/research.py` — graph research: các nút đọc repo/git/docs/tests/đêm trước/web, trả atom có nguồn.
- Tạo `src/nightshift/intake/brain.py` — nơi dựng brief: `MockBrain` (đọc kịch bản demo), `CliBrain` (`claude -p`/`codex exec` chỉ trả văn bản), và nhận đề xuất của agent.
- Tạo `src/nightshift/intake/gate.py` — cổng lọc bốn điều kiện + ngân sách; sinh câu hỏi và quyết định trước giờ chạy.
- Tạo `src/nightshift/intake/compile.py` — brief đã chốt → manifest (`validate`), snapshot oracle, preflight mở rộng.
- Tạo `src/nightshift/intake/license.py` — đọc/ghi/kiểm giấy phép `~/.nightshift/license.json`.
- Tạo `src/nightshift/intake/demo.py` — dựng repo mẫu `ns-demo` + kịch bản provider giả.
- Tạo `src/nightshift/intake/protocol.py` — `handle(request) -> response`, bảng op, idempotency, trạng thái.
- Tạo `src/nightshift/intake/bindings/cli_json.py` — `nightshift intake …` → protocol.
- Tạo `src/nightshift/intake/bindings/mailbox.py` — `inbox/` → protocol → `outbox/`.
- Tạo `src/nightshift/intake/bindings/mcp_stdio.py` — MCP JSON-RPC 2.0 qua stdio.
- Tạo `src/nightshift/intake/bindings/http.py` + `src/nightshift/intake/ui/app.html` — web đọc báo cáo, trả lời, closebox; ghép thiết bị.
- Tạo `src/nightshift/decisions/__init__.py`, `src/nightshift/decisions/log.py` — `DecisionRecord`, kiểm, ghi nối `decisions.jsonl`.
- Sửa `src/nightshift/providers/base.py` — `parse_result` chấp nhận khoá tuỳ chọn `decisions`.
- Sửa `src/nightshift/providers/mock_worker.py` — bước kịch bản có `decisions` thì ghi vào result.
- Sửa `src/nightshift/workspace/git_candidate.py` — `collect(..., widened=())` coi file trong `widened` là hợp lệ (không bao giờ với `protected`).
- Sửa `src/nightshift/engine.py:130-205` (`run_attempt`) — ghi quyết định trước khi `collect`, truyền `widened` khi giấy phép cho phép.
- Tạo `src/nightshift/reporting/human.py` + `src/nightshift/reporting/human.html` — `report.html` và `decisions.html` tiếng người.
- Sửa `pyproject.toml` — package-data thêm `intake/ui/*.html`, `reporting/*.html` đã có.
- Tạo `deploy/intake-tunnel.yml.example` — named tunnel riêng cho web intake.
- Test: `tests/intake/test_store.py`, `test_research.py`, `test_gate.py`, `test_compile.py`, `test_license.py`, `test_protocol.py`, `test_decisions.py`, `test_human_report.py`, `test_mcp.py`, `test_mailbox.py`; cùng bộ `tests/intake/test_guide_*.py` đã có.

## Mốc
- **M1 (Task 1–6):** làm xanh `UG-SETUP-01…06`, `UG-CLI-01…06`.
- **M2 (Task 7–8):** làm xanh `UG-CLI-07`, `UG-RPT-01…04`.
- **M3 (Task 9–12):** làm xanh `UG-MBX-*`, `UG-MCP-10…14`, `UG-WEB-*`; UAT tay `UG-MCP-01/02`, `UG-WEB-04`.

### Task 1: Case store, giao thức tối thiểu, `nightshift intake new/status`

**Thoả:** FR-001, FR-013

**Files:**
- Sửa: `src/nightshift/__init__.py`
- Tạo: `src/nightshift/intake/__init__.py`, `src/nightshift/intake/store.py`, `src/nightshift/intake/protocol.py`, `src/nightshift/intake/bindings/__init__.py`, `src/nightshift/intake/bindings/cli_json.py`
- Sửa: `src/nightshift/cli.py:190-245` (parser, `main`)
- Test: `tests/intake/test_store.py`, `tests/intake/test_protocol.py`

**Interfaces:**
- Consumes: `nightshift.util.atomic_write(path, raw)`, `canonical_json`, `now`, `iso`; `nightshift.errors.NightshiftError(code, detail, retryable, exit_code=...)`.
- Produces:
  - `store.runs_dir() -> Path` (env `NIGHTSHIFT_RUNS_DIR`, mặc định `~/.nightshift/runs`)
  - `store.Case` với `id: str`, `dir: Path`, `append(kind: str, **payload) -> int` (trả revision mới), `events() -> list[dict]`, `project() -> dict`
  - `store.create_case(repo: str, text: str, client_key: str) -> tuple[Case, bool]` (bool = mới tạo); `case_id` dạng `c-` + 12 hex
  - `store.load_case(case_id: str) -> Case` (thiếu → `NightshiftError("CASE_NOT_FOUND", exit_code=3)`)
  - `protocol.handle(req: dict) -> dict` với response đúng mục 9.3 của hướng dẫn; `protocol.exit_code(resp: dict) -> int` theo mục 9.5
  - `cli_json.main(argv: list[str]) -> int`

**Depends:** —
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.intake.test_store tests.intake.test_protocol -q`

- [ ] **Step 1: viết test fail**

```python
# tests/intake/test_store.py
import os, unittest
from unittest import mock
from tests.helpers import TempDir, make_repo
from nightshift.intake import store


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TempDir(self).path
        self.repo, _ = make_repo(self.tmp)
        p = mock.patch.dict(os.environ, {"NIGHTSHIFT_RUNS_DIR": str(self.tmp / "runs")})
        p.start(); self.addCleanup(p.stop)

    def test_create_is_idempotent_by_client_key(self):
        a, new_a = store.create_case(str(self.repo), "sửa parse_pair", "key-00000001")
        b, new_b = store.create_case(str(self.repo), "sửa parse_pair", "key-00000001")
        self.assertEqual((a.id, new_a, new_b), (b.id, True, False))
        self.assertRegex(a.id, r"^c-[0-9a-f]{12}$")

    def test_events_are_append_only_and_projected(self):
        c, _ = store.create_case(str(self.repo), "sửa parse_pair", "key-00000002")
        rev = c.append("note", text="x")
        self.assertEqual(rev, 2)
        self.assertEqual([e["kind"] for e in c.events()], ["case.created", "note"])
        self.assertEqual(c.project()["text"], "sửa parse_pair")

    def test_missing_case(self):
        with self.assertRaises(Exception) as cm:
            store.load_case("c-000000000000")
        self.assertEqual(cm.exception.code, "CASE_NOT_FOUND")
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Chạy: `python3.11 -m unittest tests.intake.test_store -q`
Mong đợi: FAIL — `ModuleNotFoundError: No module named 'nightshift.intake'`

- [ ] **Step 3: code tối thiểu cho pass**

```python
# src/nightshift/intake/store.py (hợp đồng)
CASE_RE = re.compile(r"^c-[0-9a-f]{12}$")
KEY_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")

def runs_dir() -> Path:
    return Path(os.environ.get("NIGHTSHIFT_RUNS_DIR") or Path.home() / ".nightshift" / "runs")

def create_case(repo, text, client_key):
    if not KEY_RE.match(client_key or ""):
        raise NightshiftError("INVALID_REQUEST", "client_key phải 8–64 ký tự chữ, số, - hoặc _", exit_code=3)
    idx = runs_dir() / "intake" / "keys" / f"{client_key}.case"
    if idx.exists():                       # idempotent: cùng key → cùng case
        return load_case(idx.read_text().strip()), False
    case_id = "c-" + hashlib.sha256(f"{client_key}|{now()}".encode()).hexdigest()[:12]
    c = Case(case_id); c.dir.mkdir(parents=True)
    c.append("case.created", repo=str(Path(repo).expanduser().resolve()), text=text, client_key=client_key)
    atomic_write(idx, case_id.encode())
    return c, True
```

Protocol: `handle()` bắt `NightshiftError` và trả `{"error": e.as_dict() không kèm evidence_ref, ...}`; `exit_code`: có `error` → `error.exit_code` gắn khi raise (`INVALID_REQUEST`/`CASE_NOT_FOUND`/`REPO_NOT_FOUND`/`LICENSE_NEEDS_HUMAN` → 3, `REVISION_CONFLICT` → 4, `NOT_READY` → 2, `LICENSE_EXCEEDED`/`PREFLIGHT_FAILED`/`PROVIDER_UNAVAILABLE` → 5), không lỗi và `state == "asking"` → 2, còn lại 0. `cli_json` hỗ trợ `--print a.b` (in giá trị theo đường dẫn chấm; chuỗi in trơn, còn lại in JSON).

- [ ] **Step 4: chạy lại — PASS**

Chạy: `python3.11 -m unittest tests.intake.test_store tests.intake.test_protocol -q`
Mong đợi: `OK`

- [ ] **Step 5: commit**

```bash
git add src/nightshift/__init__.py src/nightshift/intake src/nightshift/cli.py tests/intake/test_store.py tests/intake/test_protocol.py
git commit -m "feat(intake): case store sự kiện + giao thức intake/1 + nightshift intake new/status"
```

### Task 2: Repo mẫu, giấy phép, `--version`

**Thoả:** FR-006, FR-007

**Files:**
- Tạo: `src/nightshift/intake/demo.py`, `src/nightshift/intake/license.py`
- Sửa: `src/nightshift/cli.py` (lệnh `--version`, `intake demo`, `license set|show`)
- Test: `tests/intake/test_license.py`

**Interfaces:**
- Consumes: `store.runs_dir()` (Task 1); `tests.helpers.git`.
- Produces:
  - `demo.build(dest: Path) -> dict` trả `{"repo", "baseline_sha", "mock_script"}`; repo có `src/parser.py` (viết hoa giá trị), `src/format.py` (gọi `parse_pair` rồi `.upper()`), `tests/test_basic.py` (xanh), `acceptance/test_parser.py` (đỏ), `README.md` có câu "Values are upper-cased for legacy clients.", và `.nightshift/mock-script.json` gồm khoá `intake` (brief kịch bản) và `run` (kịch bản mock provider).
  - `license.path() -> Path` (`~/.nightshift/license.json`, env `NIGHTSHIFT_LICENSE` ghi đè)
  - `license.load() -> dict | None`
  - `license.save_interactive(lic: dict, *, stdin, stdout) -> dict` — không phải TTY → `NightshiftError("LICENSE_NEEDS_HUMAN", exit_code=3)`; in giấy phép, hỏi `Lưu giấy phép này? Gõ yes để xác nhận: `, chỉ lưu khi đọc được `yes`
  - `license.check(lic: dict, plan: dict) -> list[str]` — mỗi phần tử là một câu tiếng người nói vượt ở đâu; rỗng = trong giấy phép. `plan` có `repo`, `provider`, `tasks`, `max_calls`, `hours`, `widen_scope`.

**Depends:** Task 1
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.intake.test_license -q`

- [ ] **Step 1: viết test fail**

```python
# tests/intake/test_license.py
import io, unittest
from nightshift.intake import license as lic

BASE = {"repos": ["/r/ns-demo"], "providers": ["mock"], "max_calls": 40, "max_tasks": 6,
        "max_hours": 8, "widen_scope": True, "max_questions": 8, "web_domains": []}


class LicenseTests(unittest.TestCase):
    def test_within(self):
        self.assertEqual(lic.check(BASE, {"repo": "/r/ns-demo", "provider": "mock", "tasks": 1,
                                          "max_calls": 20, "hours": 8, "widen_scope": True}), [])

    def test_each_excess_is_explained(self):
        why = lic.check(BASE, {"repo": "/r/other", "provider": "cli:codex", "tasks": 9,
                               "max_calls": 99, "hours": 9, "widen_scope": True})
        self.assertEqual(len(why), 5)
        self.assertTrue(any("cli:codex" in w for w in why))

    def test_non_tty_cannot_save(self):
        with self.assertRaises(Exception) as cm:
            lic.save_interactive(BASE, stdin=io.StringIO("yes\n"), stdout=io.StringIO())
        self.assertEqual(cm.exception.code, "LICENSE_NEEDS_HUMAN")
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Chạy: `python3.11 -m unittest tests.intake.test_license -q`
Mong đợi: FAIL — `ImportError: cannot import name 'license'`

- [ ] **Step 3: code tối thiểu cho pass**

```python
# src/nightshift/intake/license.py (hợp đồng)
def check(lic, plan):
    why = []
    if plan["repo"] not in lic["repos"]:
        why.append(f"Giấy phép không có repo {plan['repo']}.")
    if plan["provider"] not in lic["providers"]:
        why.append(f"Giấy phép chỉ cho provider {', '.join(lic['providers'])}; yêu cầu dùng {plan['provider']}.")
    if plan["tasks"] > lic["max_tasks"]:
        why.append(f"Có {plan['tasks']} việc, giấy phép cho tối đa {lic['max_tasks']}.")
    if plan["max_calls"] > lic["max_calls"]:
        why.append(f"Cần tới {plan['max_calls']} lượt gọi model, giấy phép cho tối đa {lic['max_calls']}.")
    if plan["hours"] > lic["max_hours"]:
        why.append(f"Chạy {plan['hours']} giờ, giấy phép cho tối đa {lic['max_hours']} giờ.")
    if plan["widen_scope"] and not lic["widen_scope"]:
        why.append("Việc cần nới phạm vi file nhưng giấy phép không cho.")
    return why

def save_interactive(new, *, stdin=sys.stdin, stdout=sys.stdout):
    if not (hasattr(stdin, "isatty") and stdin.isatty()):
        raise NightshiftError("LICENSE_NEEDS_HUMAN", "Giấy phép chỉ đổi được từ terminal có người.", exit_code=3)
    stdout.write(json.dumps(new, ensure_ascii=False, indent=2) + "\nLưu giấy phép này? Gõ yes để xác nhận: ")
    stdout.flush()
    if stdin.readline().strip() != "yes":
        raise NightshiftError("LICENSE_NEEDS_HUMAN", "Không xác nhận, giấy phép giữ nguyên.", exit_code=3)
    atomic_write(path(), canonical_json(new).encode()); os.chmod(path(), 0o600)
    return new
```

- [ ] **Step 4: chạy lại — PASS**

Chạy: `python3.11 -m unittest tests.intake.test_license -q`
Mong đợi: `OK`; thêm `NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest tests.intake.test_guide_cli` phải qua `UG-SETUP-01…06`.

- [ ] **Step 5: commit**

```bash
git add src/nightshift/intake/demo.py src/nightshift/intake/license.py src/nightshift/cli.py tests/intake/test_license.py
git commit -m "feat(intake): repo mẫu, giấy phép chỉ-người-sửa, nightshift --version"
```

### Task 3: Graph research

**Thoả:** FR-002

**Files:**
- Tạo: `src/nightshift/intake/research.py`
- Sửa: `src/nightshift/intake/protocol.py` (op `case.create` chạy research khi `wait > 0`)
- Test: `tests/intake/test_research.py`

**Interfaces:**
- Consumes: `store.Case.append`; `license.load()` (lấy `web_domains`, trần đọc).
- Produces:
  - `research.Atom = dict` với khoá `id`, `kind`, `value`, `epistemic_status` (`observed`), `source` (`"path:line"`, `"git:<sha>"`, hoặc URL)
  - `research.run(repo: Path, text: str, *, web_domains: list[str], max_reads: int = 40, deadline_s: float = 600, fetch=urllib_fetch) -> list[Atom]`
  - Nút (mỗi nút lỗi thì ghi atom `kind="research_error"` và các nút khác vẫn chạy): `repo_map`, `git_head` (`baseline_sha`, cây sạch), `test_commands` (dò `tests/`, `acceptance/`, `pyproject.toml`, `package.json`, `Makefile`, `go.mod`), `tests_for_symbols` (file test nhắc tới định danh có trong lời giao việc), `docs_claims` (câu trong README/docs nhắc cùng định danh), `past_nights` (quyết định/báo cáo cũ của cùng repo trong `runs_dir()`), `web_docs` (chỉ khi `web_domains` khác rỗng; URL ngoài danh sách bị từ chối).

**Depends:** Task 1, Task 2
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.intake.test_research -q`

- [ ] **Step 1: viết test fail**

```python
# tests/intake/test_research.py
import unittest
from pathlib import Path
from tests.helpers import TempDir
from nightshift.intake import demo, research


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.repo = Path(demo.build(TempDir(self).path / "ns-demo")["repo"])

    def test_demo_research_finds_what_the_gate_needs(self):
        atoms = research.run(self.repo, "sửa hàm parse_pair giữ chữ hoa", web_domains=[])
        kinds = {a["kind"] for a in atoms}
        self.assertTrue({"baseline_sha", "test_command", "tests_for_symbol", "doc_claim"} <= kinds)
        t = [a for a in atoms if a["kind"] == "tests_for_symbol"]
        self.assertTrue(any("acceptance/test_parser.py" in a["source"] for a in t))
        self.assertTrue(all(a["epistemic_status"] == "observed" and a["source"] for a in atoms))

    def test_web_outside_allowlist_is_refused_without_breaking_the_graph(self):
        calls = []
        atoms = research.run(self.repo, "parse_pair", web_domains=["docs.python.org"],
                             fetch=lambda url: calls.append(url) or "<p>x</p>")
        self.assertTrue(all(u.startswith("https://docs.python.org/") for u in calls))
        self.assertIn("baseline_sha", {a["kind"] for a in atoms})
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Chạy: `python3.11 -m unittest tests.intake.test_research -q`
Mong đợi: FAIL — `ImportError: cannot import name 'research'`

- [ ] **Step 3: code tối thiểu cho pass**

```python
# src/nightshift/intake/research.py (hợp đồng)
IDENT = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]{2,}\b")
NODES = ("repo_map", "git_head", "test_commands", "tests_for_symbols", "docs_claims", "past_nights", "web_docs")

def run(repo, text, *, web_domains, max_reads=40, deadline_s=600, fetch=urllib_fetch):
    ctx = {"repo": Path(repo), "symbols": _symbols(text), "reads": 0, "max_reads": max_reads,
           "t_end": now() + deadline_s, "web_domains": web_domains, "fetch": fetch}
    atoms = []
    for name in NODES:                       # lớp tuần tự; mỗi nút độc lập, lỗi không lan
        if now() > ctx["t_end"]:
            atoms.append(_atom("research_error", f"hết thời gian trước nút {name}", "research")); break
        try:
            atoms += globals()["_" + name](ctx)
        except Exception as e:  # noqa: BLE001 — một nút hỏng không được làm hỏng cả graph
            atoms.append(_atom("research_error", f"{name}: {type(e).__name__}", "research"))
    return atoms

def _allowed(url, domains):
    host = urllib.parse.urlparse(url).hostname or ""
    return url.startswith("https://") and any(host == d or host.endswith("." + d) for d in domains)
```

- [ ] **Step 4: chạy lại — PASS**

Chạy: `python3.11 -m unittest tests.intake.test_research -q`
Mong đợi: `OK`

- [ ] **Step 5: commit**

```bash
git add src/nightshift/intake/research.py src/nightshift/intake/protocol.py tests/intake/test_research.py
git commit -m "feat(intake): graph research local + web theo danh sách miền, atom có nguồn"
```

### Task 4: Brief và cổng câu hỏi

**Thoả:** FR-003, FR-003b, FR-004

**Files:**
- Tạo: `src/nightshift/intake/brain.py`, `src/nightshift/intake/gate.py`
- Sửa: `src/nightshift/intake/protocol.py` (op `case.propose`, `case.answer`; `case.create` gọi brain rồi gate)
- Test: `tests/intake/test_gate.py`

**Interfaces:**
- Consumes: `research.run` (Task 3); `store.Case`; `license.load()["max_questions"]`.
- Produces:
  - Brief (dict): `{"tasks": [{"id", "goal", "goal_quote", "allowed_paths", "acceptance_dir"}], "candidates": [Candidate]}`
  - Candidate (dict): `{"id", "topic", "text", "options": [{"n", "value", "recommended"}], "changes_outcome": bool, "answer_atom_kinds": [str], "safe_default": {"value", "reversible": bool} | None, "micro": bool, "value_rank": int}`
  - `brain.for_env() -> Brain`; `Brain.brief(text: str, atoms: list[Atom]) -> Brief`. `MockBrain` đọc khoá `intake` của `NIGHTSHIFT_MOCK_SCRIPT`; `CliBrain` chạy `claude -p --output-format json` (hoặc `codex exec`) với prompt chỉ-trả-JSON, kiểm schema, tối đa 1 lần sửa.
  - `gate.apply(brief: Brief, atoms: list[Atom], *, budget: int = 8, rounds_used: int = 0) -> tuple[list[Question], list[PreRunDecision]]`
    - Câu bị loại khi: `not changes_outcome`, hoặc có atom thuộc `answer_atom_kinds`, hoặc `safe_default` có và `reversible`, hoặc `micro`. Mỗi câu bị loại sinh `PreRunDecision {"topic", "chosen", "explanation", "asked": False, "why_not_asked"}`.
    - Còn lại xếp `value_rank` giảm dần, lấy tối đa `budget`; phần dư thành `PreRunDecision` với `why_not_asked = "máy tự quyết thay vì hỏi: vượt ngân sách câu hỏi"`.
    - `rounds_used >= 2` → không hỏi thêm câu nào.
  - Trường `fields` của response: mỗi trường brief kèm `epistemic_status`: `goal` là `user_asserted` khi `goal_quote` nằm nguyên văn trong lời giao việc, ngược lại `inferred`.

**Depends:** Task 3
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.intake.test_gate -q && NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest tests.intake.test_guide_cli`

- [ ] **Step 1: viết test fail**

```python
# tests/intake/test_gate.py
import unittest
from nightshift.intake import gate

def cand(i, **kw):
    c = {"id": i, "topic": i, "text": i + "?", "options": [{"n": 1, "value": "a", "recommended": True}],
         "changes_outcome": True, "answer_atom_kinds": [], "safe_default": None, "micro": False, "value_rank": 5}
    c.update(kw); return c

BRIEF = {"tasks": [{"id": "T1", "goal": "g", "goal_quote": "", "allowed_paths": ["src/a.py"], "acceptance_dir": "acceptance"}]}


class GateTests(unittest.TestCase):
    def test_four_conditions(self):
        b = dict(BRIEF, candidates=[
            cand("real"),
            cand("noimpact", changes_outcome=False),
            cand("found", answer_atom_kinds=["tests_for_symbol"]),
            cand("reversible", safe_default={"value": "x", "reversible": True}),
            cand("micro", micro=True)])
        qs, pre = gate.apply(b, [{"kind": "tests_for_symbol"}])
        self.assertEqual([q["id"] for q in qs], ["real"])
        self.assertEqual(sorted(d["topic"] for d in pre), ["found", "micro", "noimpact", "reversible"])
        self.assertTrue(all(d["asked"] is False and d["why_not_asked"] for d in pre))

    def test_budget_keeps_highest_value_and_labels_the_rest(self):
        b = dict(BRIEF, candidates=[cand(f"q{i}", value_rank=i) for i in range(10)])
        qs, pre = gate.apply(b, [], budget=8)
        self.assertEqual([q["id"] for q in qs][:2], ["q9", "q8"])
        self.assertEqual(len(qs), 8)
        self.assertTrue(all("vượt ngân sách" in d["why_not_asked"] for d in pre))

    def test_no_third_round(self):
        qs, _ = gate.apply(dict(BRIEF, candidates=[cand("late")]), [], rounds_used=2)
        self.assertEqual(qs, [])
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Chạy: `python3.11 -m unittest tests.intake.test_gate -q`
Mong đợi: FAIL — `ImportError: cannot import name 'gate'`

- [ ] **Step 3: code tối thiểu cho pass**

```python
# src/nightshift/intake/gate.py (hợp đồng)
def _why_not(c, kinds):
    if not c["changes_outcome"]:
        return "đáp án không làm đổi kết quả đáng kể"
    if set(c["answer_atom_kinds"]) & kinds:
        return "research đã tìm ra câu trả lời trong repo hoặc tài liệu"
    if c["safe_default"] and c["safe_default"]["reversible"]:
        return "có mặc định an toàn, đảo ngược được dễ"
    if c["micro"]:
        return "chi tiết vụn, máy tự quyết"
    return None

def apply(brief, atoms, *, budget=8, rounds_used=0):
    kinds = {a["kind"] for a in atoms}
    ask, pre = [], []
    for c in brief["candidates"]:
        why = _why_not(c, kinds)
        (pre.append(_decide(c, why)) if why else ask.append(c))
    ask.sort(key=lambda c: -c["value_rank"])
    limit = 0 if rounds_used >= 2 else budget
    for c in ask[limit:]:
        pre.append(_decide(c, "máy tự quyết thay vì hỏi: vượt ngân sách câu hỏi"))
    return [_question(c) for c in ask[:limit]], pre
```

`MockBrain` của repo mẫu trả đúng ba ứng viên: `q-legacy-upper` (đổi kết quả, không atom trả lời, không mặc định an toàn, không vụn, `value_rank` 9), `tiêu chí xong` (`answer_atom_kinds=["tests_for_symbol"]`), `tên nhánh review` (`micro=True`) — nên `UG-CLI-01` có đúng một câu và hai quyết định trước giờ chạy (cộng quyết định deadline mặc định là ba).

- [ ] **Step 4: chạy lại — PASS**

Chạy: `python3.11 -m unittest tests.intake.test_gate -q`
Mong đợi: `OK`; `NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest tests.intake.test_guide_cli` qua tới `UG-CLI-04`.

- [ ] **Step 5: commit**

```bash
git add src/nightshift/intake/brain.py src/nightshift/intake/gate.py src/nightshift/intake/protocol.py tests/intake/test_gate.py
git commit -m "feat(intake): brief + cổng lọc câu hỏi bốn điều kiện, ngân sách 8 câu, quyết định trước giờ chạy"
```

### Task 5: Compile manifest và preflight mở rộng

**Thoả:** FR-008

**Files:**
- Tạo: `src/nightshift/intake/compile.py`
- Test: `tests/intake/test_compile.py`

**Interfaces:**
- Consumes: `contracts.manifest.validate(data, check_repo=True)`, `engine.preflight(manifest, work_dir, runner)`, `util.tree_hash(path)`, `util.iso(ts)`; brief đã chốt (Task 4).
- Produces:
  - `compile.build(case: Case, brief: Brief, answers: dict, *, deadline_local: str = "06:00", provider: str) -> dict` — manifest `nightshift.manifest/1` hợp lệ: `baseline_sha` từ atom `baseline_sha`; oracle = bản chụp `acceptance_dir` vào `case.dir/oracle/<task_id>`; `verify_profiles[<task_id>] = {"baseline": [lệnh test hiện có], "acceptance": [lệnh chạy oracle], "acceptance_ids": [...], "oracle_dir": ..., "timeout_s": 900}`; `protected_paths` luôn gồm `acceptance/**`, `tests/**`, `.github/**`, `.nightshift/**`; `deadline_utc` = giờ địa phương Asia/Ho_Chi_Minh gần nhất tính từ bây giờ.
  - `compile.preflight_ext(manifest: dict, work_dir: Path, runner) -> None` — gọi `engine.preflight` (baseline phải xanh), rồi chạy lệnh acceptance trên baseline: không chạy được (lỗi import/không tìm thấy test) → `NightshiftError("PREFLIGHT_FAILED", "Test nghiệm thu không chạy được: …", exit_code=5)`; chạy mà xanh → `PREFLIGHT_FAILED` "Test nghiệm thu đã xanh trước khi sửa, không đo được việc".

**Depends:** Task 4
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.intake.test_compile -q`

- [ ] **Step 1: viết test fail**

```python
# tests/intake/test_compile.py
import os, tempfile, unittest
from pathlib import Path
from unittest import mock
from tests.helpers import TempDir
from nightshift.contracts.manifest import validate
from nightshift.intake import compile as cp, demo, store


class CompileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TempDir(self).path
        self.d = demo.build(self.tmp / "ns-demo")
        p = mock.patch.dict(os.environ, {"NIGHTSHIFT_RUNS_DIR": str(self.tmp / "runs")}); p.start(); self.addCleanup(p.stop)
        self.case, _ = store.create_case(self.d["repo"], "sửa parse_pair", "cmp-000001")
        self.brief = {"tasks": [{"id": "T1", "goal": "giữ chữ hoa chữ thường", "goal_quote": "",
                                 "allowed_paths": ["src/parser.py"], "acceptance_dir": "acceptance"}], "candidates": []}

    def test_manifest_is_valid_and_protects_the_oracle(self):
        m = cp.build(self.case, self.brief, {}, provider="mock")
        validate(m)
        self.assertIn("acceptance/**", m["tasks"][0]["protected_paths"])
        self.assertEqual(m["baseline_sha"], self.d["baseline_sha"])

    def test_preflight_requires_green_baseline_and_red_acceptance(self):
        m = cp.build(self.case, self.brief, {}, provider="mock")
        with tempfile.TemporaryDirectory() as w:
            cp.preflight_ext(m, Path(w), None)          # repo mẫu: tests xanh, acceptance đỏ → qua
        fixed = Path(self.d["repo"]) / "src" / "parser.py"
        fixed.write_text(fixed.read_text().replace(".upper()", ""))
        os.system(f"git -C {self.d['repo']} commit -qam fix")
        self.case2, _ = store.create_case(self.d["repo"], "x", "cmp-000002")
        m2 = cp.build(self.case2, self.brief, {}, provider="mock")
        with tempfile.TemporaryDirectory() as w, self.assertRaises(Exception) as cm:
            cp.preflight_ext(m2, Path(w), None)
        self.assertEqual(cm.exception.code, "PREFLIGHT_FAILED")
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Chạy: `python3.11 -m unittest tests.intake.test_compile -q`
Mong đợi: FAIL — `ImportError: cannot import name 'compile'`

- [ ] **Step 3: code tối thiểu cho pass**

```python
# src/nightshift/intake/compile.py (hợp đồng)
PROTECTED = ["acceptance/**", "tests/**", ".github/**", ".nightshift/**"]

def next_local(hhmm, tz_offset_h=7):
    h, m = map(int, hhmm.split(":"))
    local = datetime.now(timezone(timedelta(hours=tz_offset_h)))
    t = local.replace(hour=h, minute=m, second=0, microsecond=0)
    if t <= local:
        t += timedelta(days=1)
    return t

def preflight_ext(manifest, work_dir, runner):
    runner = runner or default_runner
    preflight(manifest, work_dir, runner)                     # baseline phải xanh
    for name, prof in manifest["verify_profiles"].items():
        tree = build_tree(Path(work_dir) / f"acc-{name}", manifest["repo_path"], manifest["baseline_sha"], b"")
        overlay_oracle(tree, prof["oracle_dir"])
        checks = run_checks(tree, {"acceptance": prof["acceptance"], "acceptance_ids": prof["acceptance_ids"],
                                   "timeout_s": prof["timeout_s"]}, Path(work_dir) / f"acc-logs-{name}", now() + 300, runner)
        if any(c["exit_code"] in (None, 5) or c["timed_out"] for c in checks):
            raise NightshiftError("PREFLIGHT_FAILED", f"Test nghiệm thu của việc {name} không chạy được.", exit_code=5)
        if all(c["exit_code"] == 0 for c in checks):
            raise NightshiftError("PREFLIGHT_FAILED", f"Test nghiệm thu của việc {name} đã xanh trước khi sửa, không đo được việc.", exit_code=5)
```

(`build_tree`, `overlay_oracle`, `run_checks` là các hàm có sẵn trong `src/nightshift/verification/runner.py`; `unittest` trả mã 5 khi không tìm thấy test nào.)

- [ ] **Step 4: chạy lại — PASS**

Chạy: `python3.11 -m unittest tests.intake.test_compile -q`
Mong đợi: `OK`

- [ ] **Step 5: commit**

```bash
git add src/nightshift/intake/compile.py tests/intake/test_compile.py
git commit -m "feat(intake): dựng manifest tất định + preflight kiểm test nghiệm thu chạy được và đang đỏ"
```

### Task 6: Closebox trong giấy phép

**Thoả:** FR-005, FR-006

**Files:**
- Sửa: `src/nightshift/intake/protocol.py` (op `case.closebox`), `src/nightshift/intake/bindings/cli_json.py` (`intake closebox --provider --wait`)
- Test: bổ sung `tests/intake/test_protocol.py`

**Interfaces:**
- Consumes: `compile.build`, `compile.preflight_ext` (Task 5); `license.check` (Task 2); `contracts.manifest.approve(data, snapshot_dir, approved_by)`; `store.db.connect`, `initialize`; `engine.Engine(run_dir, provider, verify_runner=...)`; `providers.registry.make(spec, run_dir, mock_script=...)`.
- Produces: `case.closebox` với params `{"case_id", "provider"?, "wait"?}`:
  - còn câu chưa trả lời → `NOT_READY` (exit 2)
  - `license.check` khác rỗng → `LICENSE_EXCEEDED`, `detail` = các câu nối bằng khoảng trắng, `state` giữ `ready` (exit 5)
  - trong giấy phép → `approve(manifest, run_dir/"snapshot", approved_by=<tên user hệ điều hành đã chuẩn hoá theo `ID_RE`>)`, `initialize`, khởi động engine trong **tiến trình tách riêng** (`subprocess.Popen([... "nightshift", "resume", run_dir, "--provider", p], start_new_session=True)`), ghi sự kiện `run.started`; `wait > 0` thì đọc ledger tới khi run dừng hoặc hết `wait`, trả `state` `running`/`done` và `run {"run_id", "status"}`.

**Depends:** Task 5
**Verify:** `cd /Users/giatran/orca/nightshift && NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest tests.intake.test_guide_cli`

- [ ] **Step 1: viết test fail**

```python
# bổ sung tests/intake/test_protocol.py
    def test_closebox_refuses_outside_license(self):
        resp = protocol.handle({"schema_version": "nightshift.intake/1", "op": "case.closebox",
                                "client_key": "close-000001", "params": {"case_id": self.case_id, "provider": "cli:codex"}})
        self.assertEqual(resp["error"]["code"], "LICENSE_EXCEEDED")
        self.assertIn("cli:codex", resp["error"]["detail"])
        self.assertEqual(protocol.exit_code(resp), 5)
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Chạy: `python3.11 -m unittest tests.intake.test_protocol -q`
Mong đợi: FAIL — `KeyError: 'error'` hoặc `INVALID_REQUEST: unknown op case.closebox`

- [ ] **Step 3: code tối thiểu cho pass**

```python
# src/nightshift/intake/protocol.py — op case.closebox (hợp đồng)
def _closebox(p):
    case = store.load_case(p["case_id"]); st = case.project()
    if st["questions"]:
        raise NightshiftError("NOT_READY", "Còn câu hỏi chưa trả lời.", exit_code=2)
    provider = p.get("provider") or os.environ.get("NIGHTSHIFT_PROVIDER", "mock")
    manifest = compile.build(case, st["brief"], st["answers"], provider=provider)
    lic = license.load()
    why = ["Chưa có giấy phép; chạy nightshift license set trong terminal của bạn."] if lic is None else \
        license.check(lic, {"repo": manifest["repo_path"], "provider": provider, "tasks": len(manifest["tasks"]),
                            "max_calls": manifest["budget"]["max_calls"], "hours": _hours(manifest),
                            "widen_scope": st.get("widen_scope", lic["widen_scope"])})
    if why:
        raise NightshiftError("LICENSE_EXCEEDED", " ".join(why), exit_code=5)
    compile.preflight_ext(manifest, case.dir / "preflight", verify_runner_for_env())
    run_dir = start_detached(case, manifest, provider)       # approve + initialize + Popen(resume)
    case.append("run.started", run_dir=str(run_dir))
    return _wait_run(case, run_dir, p.get("wait", 0))
```

- [ ] **Step 4: chạy lại — PASS**

Chạy: `NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest tests.intake.test_guide_cli`
Mong đợi: các subTest `UG-SETUP-01…06`, `UG-CLI-01…06` qua; `UG-CLI-07` và `UG-RPT-*` còn đỏ (thuộc M2).

- [ ] **Step 5: commit**

```bash
git add src/nightshift/intake/protocol.py src/nightshift/intake/bindings/cli_json.py tests/intake/test_protocol.py
git commit -m "feat(intake): closebox trong giấy phép, chạy tách tiến trình, --wait đọc ledger"
```

### Task 7: Điểm quyết định ban đêm và nới phạm vi có ghi

**Thoả:** FR-009, FR-010

**Files:**
- Tạo: `src/nightshift/decisions/__init__.py`, `src/nightshift/decisions/log.py`
- Sửa: `src/nightshift/providers/base.py` (`RESULT_KEYS` thêm tuỳ chọn `decisions`), `src/nightshift/providers/mock_worker.py`, `src/nightshift/workspace/git_candidate.py:37-60` (`collect(..., widened=())`), `src/nightshift/engine.py:163-190` (`run_attempt`)
- Test: `tests/intake/test_decisions.py`

**Interfaces:**
- Consumes: `store.db.emit`; kịch bản mock của repo mẫu (Task 2) có ở bước `run` một quyết định nới phạm vi sang `src/format.py`.
- Produces:
  - `log.validate(rec: dict) -> dict` — bắt buộc khoá `id`, `when` (`pre_run|night`), `topic`, `situation`, `options` (≥2), `chosen` (∈ options), `explanation` (không chứa tên trường nào trong `log.JARGON`), `impact` (dict, có thể có `files_outside_scope: list[str]`), `reversible` (bool), `evidence` (list), `asked` (bool), `why_not_asked` (khi `asked` là False)
  - `log.JARGON = ("allowed_paths", "protected_paths", "verify_profile", "oracle_hash", "baseline_sha", "max_attempts", "epistemic_status", "manifest_hash", "attempt_id")`
  - `log.append(path: Path, rec: dict) -> None` — ghi nối một dòng, `fsync`
  - `git_candidate.collect(checkout, baseline, allowed, protected, widened=())` — file trong `widened` không còn là `OUT_OF_SCOPE`; file khớp `protected` vẫn là `PROTECTED_PATH` dù có trong `widened`
  - Engine: trước `collect`, đọc `result["decisions"]` (nếu có), `log.validate` từng bản ghi, `log.append` vào `<run_dir>/decisions.jsonl`, gom `files_outside_scope` thành `widened` khi `manifest["policy"]["widen_scope"]` là True; bản ghi hỏng → lần thử thất bại với `POLICY`.

**Depends:** Task 6
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.intake.test_decisions -q && python3.11 -m unittest discover -s tests -t . -q`

- [ ] **Step 1: viết test fail**

```python
# tests/intake/test_decisions.py
import unittest
from nightshift.decisions import log
from nightshift.workspace.git_candidate import collect
from nightshift.workspace.create import create
from tests.helpers import TempDir, make_repo

REC = {"id": "d-1", "when": "night", "topic": "sửa thêm file", "situation": "màn hình vẫn viết hoa",
       "options": ["chỉ sửa parser", "sửa thêm format.py"], "chosen": "sửa thêm format.py",
       "explanation": "Hàm định dạng gọi lại parse_pair rồi viết hoa.", "impact": {"files_outside_scope": ["src/format.py"]},
       "reversible": True, "evidence": ["diff"], "asked": False, "why_not_asked": "trong đêm"}


class DecisionTests(unittest.TestCase):
    def test_record_rules(self):
        log.validate(REC)
        for bad in ({**REC, "chosen": "khác"}, {**REC, "explanation": "đổi allowed_paths"}, {**REC, "options": ["a"]}):
            with self.assertRaises(Exception):
                log.validate(bad)

    def test_widened_never_covers_protected(self):
        tmp = TempDir(self).path
        repo, sha = make_repo(tmp)
        d = create(tmp / "run", repo, sha, "a-1")
        (d / "checkout/src/extra.py").write_text("x = 1\n")
        (d / "checkout/tests/test_basic.py").write_text("# broken\n")
        c = collect(d / "checkout", sha, ["src/parser.py"], ["tests/**"], widened=["src/extra.py", "tests/test_basic.py"])
        codes = {(v["path"], v["code"]) for v in c["violations"]}
        self.assertNotIn(("src/extra.py", "OUT_OF_SCOPE"), codes)
        self.assertIn(("tests/test_basic.py", "PROTECTED_PATH"), codes)
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Chạy: `python3.11 -m unittest tests.intake.test_decisions -q`
Mong đợi: FAIL — `ModuleNotFoundError: No module named 'nightshift.decisions'`

- [ ] **Step 3: code tối thiểu cho pass**

```python
# src/nightshift/workspace/git_candidate.py — thay vòng kiểm trong collect()
def collect(checkout, baseline, allowed, protected, widened=()):
    changes = _raw_changes(checkout, baseline)
    violations = []
    for c in changes:
        for p in sorted({c["path"], c["old_path"]}):
            if path_matches(p, protected):
                violations.append({"path": p, "code": "PROTECTED_PATH"})      # widened không bao giờ tha
            elif not path_matches(p, allowed) and p not in widened:
                violations.append({"path": p, "code": "OUT_OF_SCOPE"})
        # SYMLINK / SUBMODULE giữ nguyên như cũ
```

```python
# src/nightshift/decisions/log.py (hợp đồng)
REQUIRED = {"id", "when", "topic", "situation", "options", "chosen", "explanation", "impact",
            "reversible", "evidence", "asked"}

def validate(rec):
    if not isinstance(rec, dict) or not REQUIRED <= set(rec):
        raise NightshiftError("POLICY", "bản ghi quyết định thiếu trường", exit_code=5)
    if rec["when"] not in ("pre_run", "night") or len(rec["options"]) < 2 or rec["chosen"] not in rec["options"]:
        raise NightshiftError("POLICY", "bản ghi quyết định sai dạng", exit_code=5)
    if any(w in rec["explanation"] for w in JARGON):
        raise NightshiftError("POLICY", "lời giải thích phải là lời thường, không dùng tên trường của máy", exit_code=5)
    if rec["asked"] is False and not rec.get("why_not_asked"):
        raise NightshiftError("POLICY", "quyết định tự hành phải nói vì sao không hỏi", exit_code=5)
    return rec
```

- [ ] **Step 4: chạy lại — PASS**

Chạy: `python3.11 -m unittest tests.intake.test_decisions -q && python3.11 -m unittest discover -s tests -t . -q`
Mong đợi: `OK` (143 test cũ vẫn xanh)

- [ ] **Step 5: commit**

```bash
git add src/nightshift/decisions src/nightshift/providers src/nightshift/workspace/git_candidate.py src/nightshift/engine.py tests/intake/test_decisions.py
git commit -m "feat(decisions): điểm quyết định đêm ghi trước khi làm, nới phạm vi có ghi, không bao giờ tha vùng bảo vệ"
```

### Task 8: Báo cáo tiếng người

**Thoả:** FR-011, FR-012

**Files:**
- Tạo: `src/nightshift/reporting/human.py`, `src/nightshift/reporting/human.html`
- Sửa: `src/nightshift/engine.py` (`finalize` gọi `human.write(run_dir, case_dir)` khi run do intake tạo), `src/nightshift/intake/protocol.py` (op `run.report`)
- Test: `tests/intake/test_human_report.py`

**Interfaces:**
- Consumes: `reporting.report.build(db, run_dir)` (dict báo cáo máy); `decisions.jsonl` (Task 7); quyết định trước giờ chạy trong sổ sự kiện case (Task 4).
- Produces:
  - `human.write(run_dir: Path, case_dir: Path) -> dict` trả `{"report_html", "decisions_html", "summary": {"done", "not_done", "smells"}}`
  - `report.html`: `<h2>` theo đúng thứ tự "Kết quả đêm qua", "Nên xem trước", "Từng việc", "Chi phí", "Chi tiết kỹ thuật"; mục kỹ thuật là `<details id="chi-tiet-ky-thuat">` và là nơi duy nhất được chứa từ trong `log.JARGON`; mỗi mùi là `<a href="decisions.html#<id>">` với chữ "Sửa thêm file ngoài phạm vi: <file>" hoặc "Máy tự quyết thay vì hỏi: <chủ đề>" hoặc "Không đảo ngược được: <chủ đề>"
  - `decisions.html`: mỗi quyết định là `<section id="<id>">` với bảng các dòng "Tình huống", "Đã chọn", "Vì sao", "Phương án không chọn", "Ảnh hưởng", "Đảo ngược được không", "Bằng chứng", và link "Xem diff" tới bản patch trong kho artifact
  - Hai trang theo sàn design (toggle sáng/tối, font nhúng qua `html_font.py --apply` của framework khi có, không bắt buộc lúc chạy)

**Depends:** Task 7
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.intake.test_human_report -q && NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest tests.intake.test_guide_cli`

- [ ] **Step 1: viết test fail**

```python
# tests/intake/test_human_report.py
import json, unittest
from pathlib import Path
from tests.helpers import TempDir
from nightshift.reporting import human
from nightshift.decisions.log import JARGON


class HumanReportTests(unittest.TestCase):
    def test_sections_order_and_no_jargon_in_main(self):
        tmp = TempDir(self).path
        run_dir, case_dir = tmp / "run", tmp / "case"
        run_dir.mkdir(); case_dir.mkdir()
        (run_dir / "decisions.jsonl").write_text(json.dumps({
            "id": "d-1", "when": "night", "topic": "sửa thêm file", "situation": "s", "options": ["a", "b"],
            "chosen": "b", "explanation": "vì màn hình vẫn viết hoa", "impact": {"files_outside_scope": ["src/format.py"]},
            "reversible": True, "evidence": ["diff"], "asked": False, "why_not_asked": "trong đêm"}, ensure_ascii=False) + "\n")
        out = human.write(run_dir, case_dir, machine_report={"status": "COMPLETED", "tasks": [], "budget": {}})
        html = Path(out["report_html"]).read_text()
        heads = [h for h in ["Kết quả đêm qua", "Nên xem trước", "Từng việc", "Chi phí", "Chi tiết kỹ thuật"] if h in html]
        self.assertEqual(heads, ["Kết quả đêm qua", "Nên xem trước", "Từng việc", "Chi phí", "Chi tiết kỹ thuật"])
        main = html.split('id="chi-tiet-ky-thuat"')[0]
        self.assertFalse([w for w in JARGON if w in main])
        self.assertIn('href="decisions.html#d-1"', html)
        self.assertEqual(out["summary"]["smells"], 1)
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Chạy: `python3.11 -m unittest tests.intake.test_human_report -q`
Mong đợi: FAIL — `ImportError: cannot import name 'human'`

- [ ] **Step 3: code tối thiểu cho pass**

```python
# src/nightshift/reporting/human.py (hợp đồng)
SMELL_TEXT = {"outside": "Sửa thêm file ngoài phạm vi: {}", "unasked": "Máy tự quyết thay vì hỏi: {}",
              "irreversible": "Không đảo ngược được: {}"}

def smells(decisions):
    out = []
    for d in decisions:
        for f in d["impact"].get("files_outside_scope", []):
            out.append((d["id"], SMELL_TEXT["outside"].format(f)))
        if d["when"] == "pre_run" and "vượt ngân sách" in d.get("why_not_asked", ""):
            out.append((d["id"], SMELL_TEXT["unasked"].format(d["topic"])))
        if not d["reversible"]:
            out.append((d["id"], SMELL_TEXT["irreversible"].format(d["topic"])))
    return out
```

- [ ] **Step 4: chạy lại — PASS**

Chạy: `python3.11 -m unittest tests.intake.test_human_report -q && NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest tests.intake.test_guide_cli`
Mong đợi: `OK`; mọi subTest của `test_guide_cli` qua, gồm `UG-CLI-07`, `UG-RPT-01/02/04`.

- [ ] **Step 5: commit**

```bash
git add src/nightshift/reporting/human.py src/nightshift/reporting/human.html src/nightshift/engine.py src/nightshift/intake/protocol.py tests/intake/test_human_report.py
git commit -m "feat(reporting): report.html và decisions.html tiếng người, mùi dẫn tới quyết định"
```

### Task 9: Hộp thư file

**Thoả:** FR-013

**Files:**
- Tạo: `src/nightshift/intake/bindings/mailbox.py`
- Sửa: `src/nightshift/intake/bindings/cli_json.py` (`intake process`, `intake serve --mailbox`)
- Test: `tests/intake/test_mailbox.py`

**Interfaces:**
- Consumes: `protocol.handle` (Task 1–8).
- Produces: `mailbox.process_once(root: Path) -> int` — với mỗi `inbox/*.json`: tên không khớp `store.KEY_RE` → chuyển sang `inbox/rejected/`; JSON hỏng → `outbox/<key>.json` là response lỗi `INVALID_REQUEST`; có `outbox/<key>.json` rồi thì không xử lý lại (idempotent); ghi response bằng `atomic_write`; chuyển yêu cầu vào `inbox/done/`. `mailbox.serve(root, interval_s=1.0)` lặp `process_once`.

**Depends:** Task 1
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.intake.test_mailbox -q && NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest tests.intake.test_guide_mailbox`

- [ ] **Step 1: viết test fail**

```python
# tests/intake/test_mailbox.py
import json, unittest
from tests.helpers import TempDir
from nightshift.intake.bindings import mailbox


class MailboxTests(unittest.TestCase):
    def test_bad_name_and_bad_json(self):
        root = TempDir(self).path
        (root / "inbox").mkdir()
        (root / "inbox" / "bad name!.json").write_text("{}")
        (root / "inbox" / "demo-mbx-9999.json").write_text("{not json")
        mailbox.process_once(root)
        self.assertTrue((root / "inbox" / "rejected" / "bad name!.json").exists())
        out = json.loads((root / "outbox" / "demo-mbx-9999.json").read_text())
        self.assertEqual(out["error"]["code"], "INVALID_REQUEST")
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Chạy: `python3.11 -m unittest tests.intake.test_mailbox -q`
Mong đợi: FAIL — `ImportError: cannot import name 'mailbox'`

- [ ] **Step 3: code tối thiểu cho pass**

```python
# src/nightshift/intake/bindings/mailbox.py (hợp đồng)
def process_once(root):
    inbox, outbox = root / "inbox", root / "outbox"
    for d in (inbox / "done", inbox / "rejected", outbox):
        d.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in sorted(inbox.glob("*.json")):
        key = f.stem
        if not KEY_RE.match(key):
            f.rename(inbox / "rejected" / f.name); continue
        target = outbox / f.name
        if not target.exists():
            try:
                req = json.loads(f.read_text(encoding="utf-8"))
                resp = protocol.handle(req)
            except ValueError as e:
                resp = protocol.error_response("INVALID_REQUEST", f"File không phải JSON hợp lệ: {e}")
            atomic_write(target, json.dumps(resp, ensure_ascii=False).encode())
        f.replace(inbox / "done" / f.name); n += 1
    return n
```

- [ ] **Step 4: chạy lại — PASS**

Chạy: `NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest tests.intake.test_guide_mailbox`
Mong đợi: `OK` (`UG-MBX-01…04`)

- [ ] **Step 5: commit**

```bash
git add src/nightshift/intake/bindings/mailbox.py src/nightshift/intake/bindings/cli_json.py tests/intake/test_mailbox.py
git commit -m "feat(intake): hộp thư file inbox/outbox, idempotent, ghi nguyên tử"
```

### Task 10: MCP stdio

**Thoả:** FR-007, FR-013

**Files:**
- Tạo: `src/nightshift/intake/bindings/mcp_stdio.py`
- Sửa: `src/nightshift/intake/bindings/cli_json.py` (`intake mcp`)
- Test: `tests/intake/test_mcp.py`

**Interfaces:**
- Consumes: `protocol.handle`.
- Produces: `mcp_stdio.serve(stdin, stdout)` — JSON-RPC 2.0, mỗi dòng một thông điệp; `initialize` trả `{"protocolVersion", "serverInfo": {"name": "nightshift-intake", "version"}, "capabilities": {"tools": {}}}`; `tools/list` trả đúng `TOOLS = [intake_create, intake_status, intake_answer, intake_propose, intake_closebox, intake_report]` kèm `inputSchema`; `tools/call` với tên lạ → lỗi `-32602`; tên hợp lệ → gọi `protocol.handle` với op tương ứng, trả `{"content": [{"type": "text", "text": <json>}], "structuredContent": <response>, "isError": <có error>}`; `notifications/*` không trả lời.

**Depends:** Task 1, Task 9
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.intake.test_mcp -q && NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest tests.intake.test_guide_mcp`

- [ ] **Step 1: viết test fail**

```python
# tests/intake/test_mcp.py
import io, json, unittest
from nightshift.intake.bindings import mcp_stdio


class McpTests(unittest.TestCase):
    def rpc(self, *msgs):
        out = io.StringIO()
        mcp_stdio.serve(io.StringIO("".join(json.dumps(m) + "\n" for m in msgs)), out)
        return [json.loads(l) for l in out.getvalue().splitlines()]

    def test_tools_and_unknown_tool(self):
        r = self.rpc({"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                     {"jsonrpc": "2.0", "method": "notifications/initialized"},
                     {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "intake_license_set", "arguments": {}}})
        self.assertEqual(len(r), 2)
        self.assertEqual([t["name"] for t in r[0]["result"]["tools"]],
                         ["intake_create", "intake_status", "intake_answer", "intake_propose", "intake_closebox", "intake_report"])
        self.assertEqual(r[1]["error"]["code"], -32602)
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Chạy: `python3.11 -m unittest tests.intake.test_mcp -q`
Mong đợi: FAIL — `ImportError: cannot import name 'mcp_stdio'`

- [ ] **Step 3: code tối thiểu cho pass**

```python
# src/nightshift/intake/bindings/mcp_stdio.py (hợp đồng)
OPS = {"intake_create": "case.create", "intake_status": "case.status", "intake_answer": "case.answer",
       "intake_propose": "case.propose", "intake_closebox": "case.closebox", "intake_report": "run.report"}

def serve(stdin=sys.stdin, stdout=sys.stdout):
    for line in stdin:
        if not line.strip():
            continue
        msg = json.loads(line)
        if "id" not in msg:
            continue                                            # notification
        m, mid = msg.get("method"), msg["id"]
        if m == "initialize":
            res = {"protocolVersion": msg["params"].get("protocolVersion", "2025-06-18"),
                   "serverInfo": {"name": "nightshift-intake", "version": __version__}, "capabilities": {"tools": {}}}
        elif m == "tools/list":
            res = {"tools": [{"name": n, "description": DESC[n], "inputSchema": SCHEMA[n]} for n in OPS]}
        elif m == "tools/call" and msg["params"]["name"] in OPS:
            a = dict(msg["params"].get("arguments") or {})
            key = a.pop("client_key", None) or f"mcp-{uuid.uuid4().hex[:16]}"
            resp = protocol.handle({"schema_version": INTAKE_SCHEMA, "op": OPS[msg["params"]["name"]], "client_key": key, "params": a})
            res = {"content": [{"type": "text", "text": json.dumps(resp, ensure_ascii=False)}],
                   "structuredContent": resp, "isError": bool(resp.get("error"))}
        else:
            _send(stdout, {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602 if m == "tools/call" else -32601, "message": "unknown"}})
            continue
        _send(stdout, {"jsonrpc": "2.0", "id": mid, "result": res})
```

- [ ] **Step 4: chạy lại — PASS**

Chạy: `NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest tests.intake.test_guide_mcp`
Mong đợi: `OK` (`UG-MCP-10…14`)

- [ ] **Step 5: commit**

```bash
git add src/nightshift/intake/bindings/mcp_stdio.py src/nightshift/intake/bindings/cli_json.py tests/intake/test_mcp.py
git commit -m "feat(intake): MCP stdio sáu công cụ, không có công cụ ghi giấy phép"
```

### Task 11: Web đọc báo cáo, trả lời từ xa

**Thoả:** FR-004, FR-005, FR-013

**Files:**
- Tạo: `src/nightshift/intake/bindings/http.py`, `src/nightshift/intake/ui/app.html`, `deploy/intake-tunnel.yml.example`
- Sửa: `src/nightshift/intake/bindings/cli_json.py` (`intake serve --http HOST:PORT --print-pairing`, `intake pair`), `pyproject.toml` (package-data `intake/ui/*.html`)
- Test: `tests/intake/test_guide_web.py` (đã có)

**Interfaces:**
- Consumes: `protocol.handle`; `human.write` output (Task 8).
- Produces: `http.serve(host: str, port: int, *, print_pairing: bool)` dùng `http.server.ThreadingHTTPServer`; chỉ nhận host `127.0.0.1`/`localhost`; in một dòng JSON `{"url", "pairing_code", "expires_in_s": 600}`; `POST /pair {code}` → cookie `ns_session` (`HttpOnly; Secure khi qua HTTPS; SameSite=Strict`), sai 5 lần khoá 15 phút; mọi `GET/POST /api/v1/intent/*` không có phiên → 401; lệnh ghi cần header `X-Nightshift-CSRF` khớp phiên; `GET /` trả `app.html` (các nhãn: "Ghép thiết bị", "Mã ghép", "Việc của bạn", "Cần bạn trả lời", "Mình đang hiểu", "Cần bạn quyết định", "Khuyến nghị", "Trả lời bằng lời", "Gửi trả lời", "Sẵn sàng", "Closebox", "Đang chạy"); `GET /cases/<id>/report.html` và `/decisions.html` phục vụ file báo cáo.

**Depends:** Task 8
**Verify:** `cd /Users/giatran/orca/nightshift && NIGHTSHIFT_ACCEPT_STRICT=1 /tmp/ns-pw/bin/python -m unittest tests.intake.test_guide_web`

- [ ] **Step 1: viết test fail**

Test đã có: `tests/intake/test_guide_web.py` (đọc nhãn in đậm từ `docs/intake-guide.md` mục 6 và 7.3).

- [ ] **Step 2: chạy cho THẤY nó fail**

Chạy: `NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest tests.intake.test_guide_web`
Mong đợi: FAIL ở `UG-WEB-01` — `json.decoder.JSONDecodeError` (lệnh `intake serve` chưa tồn tại)

- [ ] **Step 3: code tối thiểu cho pass**

```python
# src/nightshift/intake/bindings/http.py (hợp đồng phần phiên)
class Sessions:
    def __init__(self):
        self.code, self.code_exp = f"{secrets.randbelow(10**6):06d}", now() + 600
        self.fails, self.locked_until, self.tokens = 0, 0.0, {}

    def pair(self, code):
        if now() < self.locked_until:
            return None
        if code != self.code or now() > self.code_exp:
            self.fails += 1
            if self.fails >= 5:
                self.locked_until, self.fails = now() + 900, 0
            return None
        self.code_exp = 0                                  # dùng một lần
        tok, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(16)
        self.tokens[tok] = csrf
        return tok, csrf
```

- [ ] **Step 4: chạy lại — PASS**

Chạy: `NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest tests.intake.test_guide_web`
Mong đợi: `OK` (`UG-WEB-01…03`, `UG-RPT-03`)

- [ ] **Step 5: commit**

```bash
git add src/nightshift/intake/bindings/http.py src/nightshift/intake/ui/app.html deploy/intake-tunnel.yml.example src/nightshift/intake/bindings/cli_json.py pyproject.toml
git commit -m "feat(intake): web đọc báo cáo và trả lời từ xa, ghép thiết bị một lần, CSRF"
```

### Task 12: E2E, UAT và CI

**Thoả:** FR-014

**Files:**
- Sửa: `.github/workflows/ci.yml` (job `unit` đặt `NIGHTSHIFT_ACCEPT_STRICT=1`; job mới `web` cài Playwright chạy `tests.intake.test_guide_web`)
- Sửa: `docs/uat.md` (bảng UAT cho `UG-MCP-01`, `UG-MCP-02`, `UG-WEB-04`)
- Sửa: `README.md` (mục Intake trỏ `docs/intake-guide.md`)

**Interfaces:**
- Consumes: mọi task trước.
- Produces: CI xanh ở chế độ bắt buộc; bản ghi UAT tay.

**Depends:** Task 9, Task 10, Task 11
**Verify:** `cd /Users/giatran/orca/nightshift && NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest discover -s tests -t .`

- [ ] **Step 1: viết test fail**

```yaml
# .github/workflows/ci.yml — job unit
      - run: python -m unittest discover -s tests -t . -v
        env:
          NIGHTSHIFT_ACCEPT_STRICT: "1"
```

- [ ] **Step 2: chạy cho THẤY nó fail**

Chạy: `NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest discover -s tests -t .` trước khi Task 9–11 xong
Mong đợi: FAIL ở các bước `UG-MBX-*`, `UG-MCP-*`, `UG-WEB-*`

- [ ] **Step 3: code tối thiểu cho pass**

```markdown
<!-- docs/uat.md — thêm bảng -->
| ID | Người thử | Ngày | Kết quả | Bằng chứng |
| --- | --- | --- | --- | --- |
| UG-MCP-01 | | | | ảnh `claude mcp list` / `codex mcp list` |
| UG-MCP-02 | | | | bản ghi phiên agent + report.html sáng hôm sau |
| UG-WEB-04 | | | | ảnh điện thoại ở màn Việc của bạn |
```

- [ ] **Step 4: chạy lại — PASS**

Chạy: `NIGHTSHIFT_ACCEPT_STRICT=1 python3.11 -m unittest discover -s tests -t .`
Mong đợi: `OK`, không còn bước nào bị bỏ qua vì "intake chưa triển khai"

- [ ] **Step 5: commit**

```bash
git add .github/workflows/ci.yml docs/uat.md README.md
git commit -m "ci+docs(intake): nghiệm thu bắt buộc theo hướng dẫn, job web, bảng UAT"
```

### Task 13: Site HTML duy nhất: giao việc, trả lời, closebox, báo cáo và cấu hình trên web
**Kind:** build
**Depends:** Task 11 (contract)
**Files:**
- Sửa: `src/nightshift/intake/bindings/http.py`
- Sửa: `src/nightshift/intake/ui/app.html`
- Sửa: `src/nightshift/intake/protocol.py`
- Sửa: `src/nightshift/intake/brain.py`
- Sửa: `tests/intake/test_guide_web.py`
- Sửa: `docs/intake-guide.md`
**Interfaces:**
- Consumes: —
- Produces: —
**Verify:** `cd /Users/giatran/orca/nightshift && python3.11 -m unittest tests.intake.test_guide_contract tests.intake.test_protocol -q && NIGHTSHIFT_ACCEPT_STRICT=1 /tmp/ns-pw/bin/python -m unittest tests.intake.test_guide_web`

- [x] **Step 1: hợp đồng (đã làm, commit `011ee76`)**

```python
# src/nightshift/intake/brain.py
def for_env(provider=None): ...          # provider=None → NIGHTSHIFT_PROVIDER như cũ

# src/nightshift/intake/protocol.py — op_create
b = brain.for_env(p.get("analyze_with"))  # web không có agent đề xuất nên hệ tự phân tích

# src/nightshift/intake/bindings/http.py
# POST /api/v1/intent/cases  {repo, text, client_key} → case.create(wait=120,
#      analyze_with=NIGHTSHIFT_PROVIDER or provider đầu tiên khác "mock" trong giấy phép)
# GET  /api/v1/profile       → {"license": license.load(), "source": "default"|"file", "path": ...}  (chỉ đọc)
```

- [x] **Step 2: giao diện** — `app.html`: khung **Giao việc mới** (ô **Repo**, ô **Việc cần làm**, nút **Giao việc**) và khung **Cấu hình** chỉ xem; hướng dẫn mục 7 thêm `UG-WEB-03`, `UG-WEB-06`.

## Ghi chú thi hành (24/09/2026)

Cả 12 task đã commit trên nhánh `intake-guide` của `Rheinmir/nightshift` (từ `40d8fb2` tới `fca0922`). Toàn bộ test chạy xanh ở chế độ `NIGHTSHIFT_ACCEPT_STRICT=1` với trình duyệt thật; chỉ test sandbox Podman live bị bỏ qua trên máy này (chạy trên CI). Ba chỗ làm khác kế hoạch, có lý do:

- **Task 7:** cờ "được nới phạm vi" không nằm trong `manifest["policy"]` vì `validate()` chỉ nhận đúng `POLICY_V1`; closebox ghi nó vào `<run_dir>/intake.json` và engine đọc từ đó. Hợp đồng manifest giữ nguyên.
- **Task 8:** báo cáo tiếng người do `nightshift.intake.runner` sinh sau khi engine dừng, không đặt trong `Engine.finalize`, để engine không phụ thuộc intake; template HTML viết thẳng trong `reporting/human.py` thay vì file `human.html` riêng. Có thêm `diff.html` để link "Xem diff" trỏ đúng file.
- **Task 6:** khi người dùng không nêu giờ, hạn chót mặc định được rút về trong trần giờ của giấy phép và ghi thành quyết định trước giờ chạy; hạn chót tự nêu mà vượt trần vẫn bị từ chối. Phát hiện khi closebox giữa trưa: "6 giờ sáng mai" cách 18 tiếng, vượt trần 8 tiếng.

- **Sau nghiệm thu (commit `c67e35b`):** theo quyết định của người dùng, cài xong có sẵn **profile mặc định** (mọi repo, `cli:claude` hoặc `mock`, mọi trần không giới hạn từ commit `0faa1b0`) nên dùng được ngay với một câu; `license set` chỉ đổi thông số được nêu, xoá file là về mặc định. Hướng dẫn tổ chức lại quanh việc sửa thông số (mục 3, `UG-PROF-*`) và cả bốn cách đều có đủ bốn bước giao việc, trả lời, closebox, lấy báo cáo.

- **Task 13 (commit `011ee76`):** trang web thành site HTML duy nhất cho người: giao việc, trả lời, closebox, báo cáo và khung cấu hình chỉ xem. Khi cập nhật graph lộ ra `tests/intake/test_protocol.py` chưa từng được tạo dù Task 1/6 khai; đã viết bù (commit `f4d0aee`).

Kiểm thêm ngoài test: `report.html`, `decisions.html`, `diff.html` sinh từ lượt chạy thật và `intake/ui/app.html` qua cổng tĩnh `frontend-antipattern.py`; ba trang báo cáo qua cổng chạy thật `html-visual-gate.mjs`.

## Self-review

1. **Phủ SPEC:** FR-001 → Task 1; FR-002 → Task 3; FR-003, FR-003b, FR-004 → Task 4 (FR-004 cả Task 11); FR-005, FR-006 → Task 6 (FR-006 cả Task 2); FR-007 → Task 2, Task 10; FR-008 → Task 5; FR-009, FR-010 → Task 7; FR-011, FR-012 → Task 8; FR-013 → Task 1, 9, 10, 11; FR-014 → Task 12. SPEC T1–T12 ↔ Task 1–12 theo thứ tự mốc (SPEC T9 giao thức ⊂ Task 1 + Task 9; SPEC T12 = Task 12).
2. **Placeholder:** không còn; mọi bước có lệnh chạy và output mong đợi.
3. **Nhất quán tên:** `store.create_case/load_case/Case.append`, `research.run`, `brain.for_env`, `gate.apply`, `compile.build/preflight_ext`, `license.check/save_interactive/load`, `log.validate/append/JARGON`, `collect(..., widened=())`, `human.write`, `mailbox.process_once`, `mcp_stdio.serve`, `http.serve` dùng thống nhất giữa các task; op và tên tool khớp mục 9.2 của hướng dẫn.
