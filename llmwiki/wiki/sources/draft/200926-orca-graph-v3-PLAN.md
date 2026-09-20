---
type: draft
title: "PLAN — orca-graph v3: áp Reprise PRD v1.1 (edge có lý do, resource claims, lý do chờ, add-node, identity/dry-streak/cost), bộ eval VT, tách repo riêng Rheinmir/orca-graph và option cài mặc định tick sẵn"
status: proposed
tags: [plan, orca-graph, reprise, topology, repo-split, install, eval]
timestamp: 2026-09-20
---

# PLAN 200926 — orca-graph v3

Bối cảnh: PRD Reprise Graph Engine lên v1.1 (nguồn [[200926-reprise-graph-engine-prd-v11]]). §30.3 của PRD khuyên thứ tự áp dụng đầu tiên: audit cạnh, item manifest, identity reducer, trên fixture tất định. PLAN này nhận đúng phần nằm trong tầm một tool file-based một máy ([[ADR-018-orca-graph-file-based-graph-engine]]) và chạy bằng chính orca-graph (dogfood như bản v2).

User chốt ngày 20/09/2026: (1) không cần ép nhỏ gọn, chỉ cần chạy đúng kế hoạch; (2) module graph tách HẲN sang repo riêng để theo dõi và eval được; (3) thêm được node vào graph khi user yêu cầu; (4) install hiện option đã tick sẵn, Enter là kéo đủ.

Ngoài phạm vi (nói thẳng): item pipeline bền có outbox và backpressure (§24.3), layered fan-in theo token (§24.6), anchor registry (§25.3), routing model theo eval floor (§27.1), scale proposal (§27.4). Những thứ này cần ledger giao dịch, là engine khác.

## Global constraints
- `events.jsonl` vẫn là nguồn chân lý append-only; `graph.json` chỉ là cache. Tính năng mới không được phá graph cũ (schema_version giữ 1, field mới đều tuỳ chọn).
- `reason_class` và `resources` KHÔNG nằm trong `spec_hash` — gắn lý do cho cạnh cũ không được làm node đã xong thành stale.
- `audit-edges` chỉ đọc: không sửa PLAN, không sửa graph (PRD §23.3 bước 2: không âm thầm xoá).
- Mỗi tính năng có test pytest tất định, tên test chứa mã VT tương ứng khi có.
- Đường dẫn máy khách giữ nguyên (`~/.claude/harness/harness/scripts/orca-graph.py`, `~/.claude/harness/fdk/tools/graph-viz.py`) để skill và hook cũ không gãy.
- Không AI-attribution trong commit (R15); không commit `llmwiki/raw/` ngoài file PRD mới.

### Task 1: edge reason_class + lệnh audit-edges
**Kind:** build
**Thoả:** GX-R01, GX-R02 (PRD v1.1 §23.2–23.3) · VT-01, VT-02
**Depends:** —
**Files:**
- Sửa: `harness/scripts/orca-graph.py`
- Sửa: `harness/tests/test_orca_graph.py`
**Interfaces:**
- Consumes: —
- Produces: node có `dep_reasons: {dep_id: reason_class}`; cú pháp PLAN `**Depends:** Task 1 (data), Task 2 (preference)`; lệnh `audit-edges <id> [--json]` in `EDGE_UNJUSTIFIED`, cạnh preference đề xuất bỏ, critical path đơn vị trước/sau (dùng bởi Task 3, Task 6, Task 7)
**Resources:** engine-source(exclusive)
```python
HARD_REASONS = ("data", "contract", "acceptance", "effect_order", "control")   # cạnh cứng: không bỏ dù không truyền artifact
REASONS = HARD_REASONS + ("preference",)                                        # preference: chỉ do thứ tự viết
def audit_edges(g: dict) -> dict:   # CHỈ ĐỌC → {findings[{edge, code, action, why}], diff{remove_preference_edges}, critical_path{unit,before,after}, layers, frontier}
    ...
```
```bash
python3 harness/scripts/orca-graph.py audit-edges <id> [--json] [--strict]   # --strict rc 2 khi còn EDGE_UNJUSTIFIED
```
**Verify:** `python3 -m pytest -q harness/tests/test_orca_graph.py -k "edge or VT01 or VT02"`

### Task 2: resource claims — admission lúc lock
**Kind:** build
**Thoả:** GX-R03 (§23.4) · VT-03, VT-04
**Depends:** Task 1 (data)
**Files:**
- Sửa: `harness/scripts/orca-graph.py`
- Sửa: `harness/tests/test_orca_graph.py`
**Interfaces:**
- Consumes: parser của Task 1
- Produces: node có `resources: [{key, mode}]` từ `**Resources:** db-migration(exclusive), api-x(shared)`; `lock` từ chối khi claim xung đột đang được node locked/dispatched giữ (kể cả graph khác cùng store); hàm `resource_blockers(g, node, d)` (dùng bởi Task 3, Task 6)
**Resources:** engine-source(exclusive)
```python
def parse_claims(raw: str, where: str = "") -> list:            # "db(exclusive), api(capacity:2)" → [{key, mode, units?}], key chuẩn hoá lowercase + normpath
def resource_blockers(g: dict, n: dict, d: Path) -> list:       # [{key, mode, held_by[gid/nid], why}] — soi mọi graph trong store
def admission_mutex(d: Path, wait: float = 15.0):               # contextmanager; cmd_lock = with admission_mutex(dir): _lock(a)
```
**Verify:** `python3 -m pytest -q harness/tests/test_orca_graph.py -k "resource or VT03 or VT04"`

### Task 3: ask waiting — phân loại lý do chờ
**Kind:** build
**Thoả:** GX-R15 phần lý do chờ (§28.4, §8.4 ready ≠ admitted)
**Depends:** Task 2 (data)
**Files:**
- Sửa: `harness/scripts/orca-graph.py`
- Sửa: `harness/tests/test_orca_graph.py`
**Interfaces:**
- Consumes: `resource_blockers` của Task 2
- Produces: `ask <id> waiting` và `next` in mỗi node chưa chạy kèm lý do `data | gate | resource | queue | control | retry` (PRD §28.4)
**Resources:** engine-source(exclusive)
```python
def wait_reasons(g: dict, d: Path) -> dict:    # {node: {"reason": data|gate|resource|queue|control|retry|none, "detail": str}}
```
```bash
python3 harness/scripts/orca-graph.py ask <id> waiting
```
**Verify:** `python3 -m pytest -q harness/tests/test_orca_graph.py -k "waiting"`

### Task 4: add-node — thêm node vào graph theo yêu cầu user
**Kind:** build
**Thoả:** yêu cầu user 20/09 (3): thêm được node vào graph khi user yêu cầu · PRD §10 replan giữ lịch sử
**Depends:** Task 3 (preference)
**Files:**
- Sửa: `harness/scripts/orca-graph.py`
- Sửa: `harness/tests/test_orca_graph.py`
**Interfaces:**
- Consumes: `cmd_build` (replan giữ lịch sử)
- Produces: `add-node <id> --title T [--depends t1:data,t2] [--files a,b] [--verify CMD] [--kind K] [--resources k(mode)] [--mode hitl]` → append khối `### Task N:` vào PLAN.md gốc rồi build lại (plan_version + 1), in id node mới; từ chối khi sinh cycle hoặc vượt 20 node, PLAN giữ nguyên khi từ chối
**Resources:** engine-source(exclusive)
```bash
python3 harness/scripts/orca-graph.py add-node <id> --title "Viết changelog" --depends t1:data,t2 \
    --blocks t5 --files CHANGELOG.md --verify "test -s CHANGELOG.md" --kind docs --resources "repo-head(exclusive)"
# → "+ t13 «Viết changelog» → <PLAN.md> · chèn trước ['t5']" rồi REPLAN plan_version N → N+1, vẽ lại HTML
```
**Verify:** `python3 -m pytest -q harness/tests/test_orca_graph.py -k "add_node"`

### Task 5: identity reconcile + dry streak + cost envelope
**Kind:** build
**Thoả:** GX-R04, GX-R06 phần identity (§24.1, §25.5) · GX-R10 phần dry streak (§26.4) · GX-R12 phần đếm call (§27.2) · VT-09, VT-10, VT-17, VT-19, VT-23, VT-28
**Depends:** Task 4 (preference)
**Files:**
- Sửa: `harness/scripts/orca-graph.py`
- Sửa: `harness/tests/test_orca_graph.py`
**Interfaces:**
- Consumes: —
- Produces: hàm `reconcile_verdicts`, `next_dry_streak` nguyên văn PRD §25.5/§26.4; lệnh `reconcile-items --expected A,B,C --verdicts file.jsonl` (rc 2 khi thiếu/lỗi giao thức), `dry-streak --prev N --complete 0|1 --new N`, `cost-envelope <id> [--reviewers N] [--max-attempts N]` (20 node có QC → 42; 3 reviewer → 82)
**Resources:** engine-source(exclusive)
```python
def reconcile_verdicts(expected_ids, verdict_rows): ...                 # nguyên văn PRD §25.5 — ghép theo item_id, không theo vị trí
def next_dry_streak(previous, *, round_complete, new_count): ...        # nguyên văn PRD §26.4
def cost_envelope(g, reviewers=1, max_attempts=3) -> dict:              # min_calls = 1 + afk + reviewers×qc + 1
```
```bash
python3 harness/scripts/orca-graph.py reconcile-items --expected A,B,C --verdicts rows.jsonl --universe 100
python3 harness/scripts/orca-graph.py dry-streak --prev 1 --complete 1 --new 0
python3 harness/scripts/orca-graph.py cost-envelope <id> --reviewers 3
```
**Verify:** `python3 -m pytest -q harness/tests/test_orca_graph.py -k "VT09 or VT10 or VT17 or VT19 or VT23"`

### Task 6: graph-viz vẽ lý do cạnh + resource
**Kind:** design
**Thoả:** GX-R15 phần hiển thị (§28.4): nhìn ra cạnh nào là preference, cổng nào là gate, node giữ tài nguyên gì
**Depends:** Task 2 (data)
**Files:**
- Sửa: `fdk/tools/graph-viz.py`
**Interfaces:**
- Consumes: `dep_reasons`, `resources` của Task 1, Task 2
- Produces: cạnh preference vẽ nét đứt, tooltip/nhãn cạnh ghi reason_class, panel node hiện resources; graph cũ không có field mới vẫn vẽ như trước
```python
reason = (n.get("dep_reasons") or {}).get(d, "")
cls = "edge" + (" pref" if reason == "preference" else " gate" if reason in ("control", "acceptance") else "")
if reason == "preference":
    dash = ' stroke-dasharray="2 6"'
```
**Verify:** `python3 fdk/tools/graph-viz.py llmwiki/graph/200926-orca-graph-v3.graph.json && grep -q "preference" llmwiki/graph/200926-orca-graph-v3.graph.html`

### Task 7: bộ eval VT — ma trận + scoreboard
**Kind:** test
**Thoả:** yêu cầu user 20/09 (2): theo dõi + eval được · PRD §30.1 ma trận VT-01…28, §30.2 release gates
**Depends:** Task 5 (data)
**Files:**
- Tạo: `harness/tests/orca-graph-evals/vt-matrix.json`
- Tạo: `harness/tests/orca-graph-evals/run.py`
**Interfaces:**
- Consumes: test có mã VT của Task 1–5
- Produces: `vt-matrix.json` = 28 dòng `{id, behavior, status: covered|out_of_scope, test?, reason?}`; `run.py` chạy pytest theo từng VT covered, ghi `scoreboard.json` `{ts, engine_sha, covered, passed, out_of_scope, rows[]}`, rc 1 khi có VT covered mà đỏ
```json
{"id": "VT-09", "behavior": "Duplicate item giữ count bằng expected → so định danh phát hiện thiếu ID", "status": "covered"}
```
```bash
python3 evals/run.py --check     # ghép VT-09 ↔ mọi testcase có "VT09" trong tên; rc 1 khi VT trong phạm vi đỏ / thiếu test
```
**Verify:** `python3 harness/tests/orca-graph-evals/run.py --check`

### Task 8: tách repo Rheinmir/orca-graph + shim ở setup
**Kind:** migrate
**Thoả:** yêu cầu user 20/09 (2): tách HẲN module graph sang repo riêng
**Depends:** Task 6 (effect_order), Task 7 (effect_order)
**Files:**
- Tạo: `harness/scripts/orca-graph.py` (shim thay engine)
- Tạo: `fdk/tools/graph-viz.py` (shim)
- Tạo: `fdk/tools/graph-atlas.py` (shim)
- Xoá: `harness/tests/test_orca_graph.py`
- Xoá: `harness/tests/orca-graph-ui-smoke.mjs`
**Interfaces:**
- Consumes: engine + test + eval của Task 1–7
- Produces: repo `Rheinmir/orca-graph` (`engine/`, `skills/orca-graph/`, `tests/`, `evals/`, `install.sh`, CI, README, VERSION); shim ở setup tìm engine theo `$ORCA_GRAPH_ENGINE_DIR` rồi `~/.orca-graph/repo/engine/`, thiếu thì in đúng một lệnh cài và rc 3; `__file__` giữ là đường shim để `overstack_paths` và control-room vẫn giải đúng
```python
# shim (giống nhau cho 3 file): tìm engine thật rồi chạy TRONG globals của shim → __file__ vẫn là đường shim
_real = next((d / _NAME for d in _dirs if (d / _NAME).is_file()), None)
if _real is None:
    raise SystemExit(3)          # sau khi in lệnh cài
__engine_dir__ = str(_real.parent)
exec(compile(_real.read_text(encoding="utf-8"), str(_real), "exec"), globals())
```
**Verify:** `python3 harness/scripts/orca-graph.py --dir llmwiki/graph show 200926-orca-graph-v3 >/dev/null && cd "$HOME/.orca-graph/repo" && python3 -m pytest -q tests && python3 evals/run.py --check`

### Task 9: install — option orca-graph tick sẵn, Enter là kéo đủ
**Kind:** infra
**Thoả:** yêu cầu user 20/09 (4): install hiện option đã tick sẵn, Enter là kéo đủ; chỉ kéo khi cần
**Depends:** Task 8 (contract)
**Files:**
- Sửa: `harness/poc-vendor-neutral/install.sh`
- Sửa: `harness/poc-vendor-neutral/bootstrap.sh`
- Sửa: `harness/poc-vendor-neutral/install.ps1`
- Sửa: `README.md`
- Tạo: `harness/tests/install-graph-option-test.sh`
**Interfaces:**
- Consumes: `install.sh` của repo orca-graph (Task 8)
- Produces: khi có TTY, install in checklist `[x] orca-graph` và chờ Enter (gõ `n` để bỏ); không TTY (curl | bash do agent chạy) thì mặc định kéo; cờ `--no-graph` và biến `ORCA_GRAPH_REF`; bảng trạng thái cuối có dòng orca-graph
```bash
MODS=("graph|orca-graph — engine đồ thị phân việc …")     # checklist: mọi mục mặc định 1 (tick)
# hỏi CHỈ KHI: [ -t 1 ] && ( : </dev/tty ) && không CI/OVERSTACK_NONINTERACTIVE ; read -r -t 60 ans </dev/tty
#   ""  → cài mục đang tick · số → tick/bỏ · n → bỏ hết
[ "$WITH_GRAPH" = 1 ] && bash <install.sh của Rheinmir/orca-graph> [--no-skill]   # fail-open
```
**Verify:** `bash harness/tests/install-graph-option-test.sh`

### Task 10: SKILL + mirror + provenance + wiki
**Kind:** docs
**Thoả:** luật KÉO NGOÀI của framework (mirror SKILL + provenance pin) · AGENT.md: wiki chỉ cập nhật sau khi code xong
**Depends:** Task 8 (data)
**Files:**
- Sửa: `skills/orca-graph/SKILL.md`
- Sửa: `llmwiki/skills/orchestrate/orca-graph.md`
- Sửa: `fdk/skills.provenance.json`
- Sửa: `fdk/wiki/concepts/orca-graph.md`
**Interfaces:**
- Consumes: lệnh mới của Task 1–5, repo của Task 8
- Produces: SKILL mô tả `audit-edges`, `**Resources:**`, `ask waiting`, `add-node`, `reconcile-items`, `cost-envelope`; provenance `adapt_mode: external-pull` trỏ repo mới; concept orca-graph cập nhật v3
```json
{"orca-graph": {"adapt_mode": "external-pull", "source": "https://github.com/Rheinmir/orca-graph", "commit": "<sha>", "version": "3.0.1"}}
```
```bash
python3 harness/scripts/sync-skills.py && python3 fdk/tools/skill-provenance.py record orca-graph --source https://github.com/Rheinmir/orca-graph
```
**Verify:** `grep -q "add-node" skills/orca-graph/SKILL.md && grep -q "audit-edges" llmwiki/skills/orchestrate/orca-graph.md && python3 -c "import json;assert json.load(open('fdk/skills.provenance.json'))['skills']['orca-graph']['adapt_mode']=='external-pull'"`

### Task 11: review kỹ + sửa finding
**Kind:** review
**Thoả:** yêu cầu user: review kỹ càng trước khi đóng gói · PRD §25 reviewer context riêng, chỉ nhận finding tái hiện được
**Depends:** Task 9 (acceptance), Task 10 (acceptance)
**Files:**
- Tạo: `llmwiki/wiki/sources/draft/200926-orca-graph-v3-review.md`
**Interfaces:**
- Consumes: toàn bộ diff của Task 1–10 ở cả hai repo
- Produces: báo cáo review (finding, mức, đã sửa hay hoãn có lý do); test và eval vẫn xanh sau khi sửa
```bash
# hai reviewer context riêng (engine · install/shim), chỉ báo lỗi ĐÃ tái hiện trong mktemp + HOME cô lập
python3 -m pytest -q tests -k review && python3 evals/run.py --check && bash tests/install-test.sh     # repo engine
python3 fdk/tools/medic.py --ci && python3 fdk/tools/ci-local.py                                      # repo framework
```
**Verify:** `test -s llmwiki/wiki/sources/draft/200926-orca-graph-v3-review.md && cd "$HOME/.orca-graph/repo" && python3 -m pytest -q tests`

### Task 12: ship — push repo mới + /ship setup
**Kind:** release
**Thoả:** yêu cầu user: đóng gói và /ship lên remote · ship RULE-04: chứng minh đường remote bằng smoke người-mới, không chỉ medic
**Depends:** Task 11 (acceptance)
**Files:**
- Sửa: `llmwiki/wiki/log.md`
**Interfaces:**
- Consumes: hai repo đã review
- Produces: `Rheinmir/orca-graph` public có tag `v3.0.0`; nhánh `orca` của setup đã push; cài thử từ remote thật kéo được engine
```bash
gh repo create Rheinmir/orca-graph --public --source . --remote origin --push && git tag -a v3.0.x && gh release create v3.0.x
curl -fsSL https://raw.githubusercontent.com/Rheinmir/orca-graph/main/install.sh | bash          # cài thật từ remote
git push origin orca                                                                               # framework
```
**Verify:** `gh repo view Rheinmir/orca-graph --json name -q .name && test -z "$(git log origin/orca..HEAD --oneline)"`

## Origin

- Nguồn: `llmwiki/raw/Reprise-Graph-Engine-Full-Cycle-PRD (1).md` §22–30, tóm ở [[200926-reprise-graph-engine-prd-v11]].
- Yêu cầu user ngày 20/09/2026 (goal của phiên + tin nhắn bổ sung: ưu tiên repo riêng theo dõi/eval được, vẽ thêm node theo yêu cầu).
- PLAN bản trước cùng dòng: `sources/draft/archive/proposals/120926-orca-graph-v2-PLAN.md`.
