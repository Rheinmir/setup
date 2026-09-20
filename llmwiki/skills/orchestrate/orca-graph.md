---
name: orca-graph
description: Phân việc dạng ĐỒ THỊ PHỤ THUỘC trên PLAN.md — trả lời 5 câu hỏi (task này cần việc gì · cái gì chạy song song · phụ thuộc vào gì · tồn tại để làm gì trong graph · liên hệ graph cũ) bằng tool tất định, dispatch theo lớp topo có KHOÁ + lease + generation, state lưu bền append-only (events.jsonl), 2 file python vẽ (1 graph / atlas 2D mọi graph), mọi câu trả lời của model gắn nhãn chắc|gợi-ý|không-biết + nguồn, audit bịa=0. Gọi khi user nói "orca-graph", "graph phân việc", "task nào song song", "phụ thuộc gì", "vẽ graph task", "dispatch theo graph", "/orca-graph".
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.1.0"
---

# Skill: orca-graph

Nhánh của `orca-workflow`: cùng propose → gate → plan → dispatch, nhưng **deps là DỮ LIỆU** (graph.json),
không phải suy đoán trong đầu. Runtime: `harness/scripts/orca-graph.py`. Vẽ: `fdk/tools/graph-viz.py`
(1 graph) + `fdk/tools/graph-atlas.py` (atlas 2D). Store mặc định `llmwiki/graph/`.

**Engine sống ở repo riêng** `https://github.com/Rheinmir/orca-graph` (test + bộ eval VT + lịch sử riêng), cài vào
`~/.orca-graph/repo/`. Ba đường dẫn ở trên trong overstack là **shim** trỏ sang engine đó — lệnh gõ y như cũ. Shim báo
"chưa cài engine" (rc 3) → chạy đúng lệnh nó in ra: `curl -fsSL https://raw.githubusercontent.com/Rheinmir/orca-graph/main/install.sh | bash`.
Không có overstack: gọi thẳng `~/.orca-graph/bin/orca-graph`.

## WHAT

### Purpose và context
- **Purpose:** phân việc của một PLAN.md thành ĐỒ THỊ PHỤ THUỘC (deps là DỮ LIỆU trong graph.json), trả lời 5 câu hỏi bằng tool tất định, dispatch theo lớp topo có khoá + lease + generation, state bền append-only, và chấm mọi câu trả lời của model theo rubric có nguồn.
- **Trigger (when to use):**
  - Có PLAN.md ≥ 3 task và cần biết: cái gì chạy song song, cái gì chờ cái gì, chạy tới đâu rồi.
  - Dispatch nhiều agent và cần khoá để 2 agent không giành cùng task / ghi cùng file.
  - Việc còn dở nhiều phiên: state phải sống qua crash, không được "nhớ trong đầu".
- **Non-goals:** KHÔNG dùng cho sự cố (→ `orca-issue`), không dùng khi chưa có PLAN (→ `/propose` rồi `/plan`).
  Ngoài phạm vi PRD v1.1 (nói thẳng): item pipeline bền có outbox/backpressure, layered fan-in theo token, anchor registry, routing model theo eval floor, scale proposal, seen ledger cho discovery — xem `evals/vt-matrix.json` của repo engine: 13/28 kịch bản VT ghi `out_of_scope` kèm lý do.
  Ngoài phạm vi PRD (nói thẳng, không giả vờ có): PostgreSQL ledger, secret gateway, ngân sách tiền, LangGraph, integration queue/candidate hash, compensation cho effect ngoài, sandbox process-level (chạy lệnh agent trong container/VM riêng). Tool này là file-based cho một máy; cần những thứ trên thì đó là engine khác, không phải nâng cấp orca-graph. (Allow-list GHI file — khác sandbox process — đã có, xem `run --strict` ở mục Reference — Daemon & control-room bên dưới và GH#162.)

### Mental model
`PLAN.md → build → graph.json (cache) + events.jsonl (nguồn chân lý, append-only) → ask (5 câu hỏi) → next/lock/set/run theo lớp topo → verify (+ qc) → audit → graph-viz / graph-atlas / control-room`.

Máy state mỗi node:
`proposed → ready (mọi deps xong) → locked → dispatched → done | done_unverified | failed | unknown`; `blocked` = HITL chờ người.
Ba chiều tách nhau: `state` (vòng đời) · `verified` (verify rc 0?) · `fresh` (upstream làm lại sau khi mình xong → `stale`, chỉ cảnh báo).
Luật vay từ Reprise PRD: op_key idempotent · CAS `--if-rev` · generation chặn kết quả cũ · lease hết → `unknown` không phải `failed` · không verify thì không `done`.
- `qc` (GH#163, tuỳ chọn — trường `**QC:**` trong PLAN.md, nằm trong `spec_hash` như `verify`): lệnh review ĐỘC LẬP chạy SAU `verify` rc=0, KHÔNG chạy bởi cùng lời gọi đã tự verify (`by != "reconcile"` ở `emit()`) — tách vai reviewer khỏi vai người/agent vừa tự verify. Fail thì: qua `run`/`set done` trực tiếp → `emit()` demote `done`→`done_unverified` (giống verify fail); qua `reconcile` → kết luận `ready` (reconcile tự quyết dứt khoát, không để lửng done_unverified). Không khai `**QC:**` → hành vi y hệt trước đây (tương thích ngược).

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | `PLAN.md` | có | ≥ 3 task; dòng `**Depends:**`, `**Verify:**`, tuỳ chọn `**Kind:**`, `**QC:**`, `**Resources:**`; chưa có → gọi skill `plan` |
| In | lý do cạnh | nên có | `**Depends:** Task 1 (data), Task 2 (preference)` — reason ∈ data · contract · acceptance · effect_order · control (cạnh CỨNG) · preference (chỉ do thứ tự viết) |
| In | claim tài nguyên | khi dùng chung | `**Resources:** db-migration(exclusive), api-x(shared), llm(capacity:2)` — thiếu mode = exclusive |
| In | store | không | mặc định `llmwiki/graph/` |
| In | `--parent <gid>/<node>` | không | gắn graph con vào node graph mẹ |
| In | agent + lệnh agent | khi dispatch | tên agent cho `lock --by`; lệnh cho `run … --` |
| Out | `<id>.graph.json` + `<id>.events.jsonl` + `.locks/` | có | graph + state bền |
| Out | output `build` | có | cycle, deps suy luận (`gợi-ý`), xung đột ghi cùng file giữa 2 node song song |
| Out | answer có nhãn + nguồn | khi model trả lời | chấm theo rubric 1 / 0 / 0.3 / 0.5 / bịa 0 |
| Out | HTML graph + atlas 2D + `control-room.html` | có | 2 file python vẽ + generator control-room |
| Out | `audit-log.jsonl` | khi kết | kết quả mở lại từng nguồn, bịa = 0 |

### Rules và capabilities
- RULE-01 (MUST): **Lock kiểm soát DISPATCH; side-effect ghi file có allow-list MỀM** (GH#162) — xem `run --strict` ở trên. Allow-list KHÔNG thay thế cách ly process thật → worktree riêng mỗi task vẫn là lựa chọn khi cần cô lập hoàn toàn (chạy lệnh, biến môi trường, side-effect ngoài filesystem).
- RULE-02 (MUST): **Không dispatch node `blocked`** (HITL) cho CLI headless — nó sẽ đoán thay người rồi im lặng (bài học 250626, giao ~1/5).
- RULE-03 (MUST): **Mọi câu trả lời của model về graph phải qua `answer`** với nhãn + nguồn mở được. Không có nguồn → chọn `không-biết` (0.3) thay vì bịa (0).
- RULE-04 (MUST): Deps `gợi-ý` (suy luận) phải được user xác nhận hoặc khai `**Depends:**` trước khi dispatch lớp đó.
- RULE-05 (MUST): Không xoá/sửa tay `events.jsonl`; sai thì append event sửa. `graph.json` chỉ là cache — hỏng thì `build` lại, state fold từ events.
- RULE-06 (MUST): HTML sinh ra: toggle sáng/tối + full path + thuật ngữ có giải nghĩa (luật fdk) — 2 file vẽ đã lo, đừng viết HTML tay.
- RULE-08 (MUST): **Tranh chấp tài nguyên KHÔNG phải cạnh DAG** (PRD v1.1 §23.2). Hai task độc lập dùng chung nhánh tích hợp / schema DB / cổng test / quota API → khai `**Resources:**`, để `lock` tuần tự hoá lúc chạy; ĐỪNG thêm `**Depends:**` giả. Worktree riêng không miễn claim.
- RULE-09 (MUST): `audit-edges` chỉ ĐỌC và chỉ ĐỀ XUẤT. Cạnh thiếu lý do (`EDGE_UNJUSTIFIED`) thì GIỮ và hỏi user; "không thấy dependency" không bằng "đã chứng minh độc lập". Bỏ cạnh = user đồng ý → sửa PLAN → build lại.
- RULE-10 (MUST): User yêu cầu THÊM việc vào graph đang chạy → `add-node` (nó sửa PLAN gốc rồi build lại, `plan_version + 1`, lịch sử giữ nguyên). Cấm vá tay `graph.json`; cấm tạo graph mới cho cùng một goal.
- RULE-07 (MUST): Không làm được (nói thẳng): coupling ngầm không lộ ra file; rollback tự động khi agent chết nửa chừng; sync 2 chiều với sổ Orca; atlas > ~500 node cần graphviz; allow-list chỉ soát filesystem, không soát network/process/secret access.
- Capabilities: đọc PLAN và file dự án; ghi store graph append-only + khoá file; spawn và theo dõi process agent (heartbeat theo pid); chạy lệnh verify/qc; đọc diff git để soát allow-list; sinh HTML tĩnh. Mirror một chiều sang sổ điều phối ngoài là tuỳ chọn.

### Failure boundaries
- Chưa có PLAN → **blocked**, gọi `plan` (hoặc `/propose` rồi `/plan`); là sự cố → chuyển `orca-issue`.
- Cycle (`check-cycles` rc 2) hoặc vượt depth ≤ 6 / ≤ 20 node → tool từ chối, **blocked** tới khi giảm scope.
- Deps `gợi-ý` chưa xác nhận → **clarify** với user trước khi dispatch lớp đó.
- Node `blocked` (HITL) → chờ người, KHÔNG dispatch headless.
- Agent im lặng quá lease → `unknown` (không phải `failed`) → `reconcile`; quá 3 attempt → **failed**.
- Kết quả gen cũ hoặc plan_version khác → STALE, không publish.
- Không có nguồn cho câu trả lời → nhãn `không-biết`, không bịa.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | deterministic | repo có harness | Bước 0: pre-work sweep `pull-gate-sweep.sh` | sweep xong | không harness → bỏ |
| W02 | judgment | PLAN | Bước 1: PLAN có chưa; chưa → skill `plan`; điền Depends + Verify thật | PLAN.md | thiếu Depends → tool suy, nhãn gợi-ý |
| W03 | deterministic | PLAN.md | Bước 2: `python3 harness/scripts/orca-graph.py build <PLAN.md>` | graph.json + cảnh báo cycle, xung đột file | xung đột → thêm Depends hoặc chấp nhận có lý do |
| W03b | deterministic | graph.json | Bước 2b: `audit-edges <id>` — cạnh thiếu lý do, cạnh preference bỏ được, critical path trước/sau | bảng finding (chỉ đọc) | `EDGE_UNJUSTIFIED` → hỏi user lý do, điền vào Depends |
| W04 | judgment | graph | Bước 3: 5 câu hỏi bằng `ask` trước, model sau qua `answer` kèm nhãn + nguồn | answer có nhãn | không nguồn → không-biết |
| W05 | effect | graph.json | Bước 4: vẽ `graph-viz.py` → gửi HTML cho user duyệt (`gate-create`) | HTML + gate | kind lạ → B06 |
| W06 | effect | graph đã duyệt | Bước 5: vòng `next` → `lock` → `set dispatched` → dispatch → `set done` tới khi `next` báo hoàn tất | node done | lease hết → B05 |
| W07 | deterministic | graph xong | Bước 6: `audit <id>` → `graph-atlas.py llmwiki/graph/` → problem-tree nếu lộ vấn đề | audit-log + atlas | bịa > 0 → báo |

Chi tiết từng bước (nguồn chân lý cho W01–W07; bước 0–6 ứng với W01–W07):

0. Pre-work sweep như orca-workflow (`pull-gate-sweep.sh`) nếu có harness.
1. **PLAN có chưa?** Chưa → gọi skill `plan`. Khuôn `/plan` có dòng `**Depends:** Task 1, Task 3` và `**Verify:** <lệnh rc 0>` — điền thật; thiếu Depends thì tool SUY từ Consumes/Produces và gắn nhãn `gợi-ý`.
2. **Dựng graph:** `python3 harness/scripts/orca-graph.py build <PLAN.md>` → in cycle, deps suy luận, và **xung đột ghi cùng file** giữa 2 node song song (⚠ → thêm Depends để ép tuần tự, hoặc chấp nhận có lý do).
3. **Trả lời 5 câu hỏi — bằng tool trước, model sau:**
   - `ask <id> needs` · `ask <id> parallel` · `ask <id> deps <n>` · `ask <id> why <n>` · `ask <id> related`.
   - Phần model bổ sung (ý nghĩa, liên hệ ngữ nghĩa với graph cũ, rủi ro) → **ghi bằng `answer`** kèm nhãn + nguồn:
     `answer <id> <n> --q why --label chắc|gợi-ý|không-biết --score S --evidence file:path:line edge:a->b event:<op_key> absence:<lệnh> --text "..."`.
   - Rubric (user chốt 2026-09-12): đúng **1** · sai **0** · không-biết **0.3** · gợi-ý có nguồn thật **0.5** · **bịa nguồn 0**. Không chắc → nói `gợi-ý`/`không-biết`, đừng gắn `chắc`.
4. **Vẽ + gate:** `python3 fdk/tools/graph-viz.py llmwiki/graph/<id>.graph.json` → gửi HTML cho user duyệt (`gate-create` như orca-workflow).
   - Node trên đồ thị vẽ theo **kind** của task (`**Kind:** build|test|fix|research|docs|design|review|security|infra|data|migrate|deploy|release|cleanup|integration|wiki` trong PLAN.md, mặc định `build`) — icon + shape + màu nền tra ở `engine/kind-glyphs.json` của repo engine (`~/.orca-graph/repo/engine/`; sổ mặc định DÙNG CHUNG mọi graph — sửa/thêm qua PR vào repo đó). Viền node vẫn là **state** (không đụng).
   - `kind` lạ chưa có trong sổ → tool tự sinh tạm (monogram + màu/hình theo hash, ghi vào `~/.orca-graph/kind-glyphs.local.json` — máy-local, không bẩn git clone của engine) và **in cảnh báo ra stderr**. Thấy cảnh báo này → **hỏi user** có muốn `/raise-issue` để submit glyph mới vào `kind-glyphs.json` không; đừng tự ý thêm vào sổ mặc định mà không hỏi.
5. **Vòng chạy** (lặp tới khi `next` báo hoàn tất):
   ```
   next <id>                                  # node ready = chạy song song NGAY; blocked = HITL, KHÔNG dispatch headless
   lock <id> <n> --by <agent>                 # O_EXCL + lease (mặc định 90 phút); heartbeat <id> <n> khi chờ lâu
   set <id> <n> dispatched --op-key <uuid>    # rồi orca orchestration dispatch --task … --inject (brief NGUYÊN VĂN từ PLAN)
   set <id> <n> done --gen <gen> --op-key <uuid>   # gen lấy từ output lệnh dispatched; gen cũ → STALE, không publish
   ```
   Agent im lặng quá lease → `next` tự đẩy node về `unknown` → `reconcile <id> <n>` (chạy verify) trước khi lock lại. Tối đa 3 attempt.
   Muốn mirror sang sổ Orca: `sync-orca <id> --run` (một chiều; sổ Orca runtime-global, đóng dấu dự án).
6. **Kết:** `audit <id>` (mở lại từng nguồn; bịa = 0; ghi `audit-log.jsonl`) → `graph-atlas.py llmwiki/graph/` regen atlas → cập nhật problem-tree nếu lộ vấn đề quy trình.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | user_optional | việc cần tách graph con dưới một node | `build <PLAN> --parent <gid>/<node>`; node mẹ join khi MỌI node con xong | vượt depth 6 hoặc 20 node → tool từ chối | W03 |
| B02 | conditional_required | `build` lại trên graph đã có | `plan_version + 1`, node bỏ vào `superseded[]`, node đổi `spec_hash` đã xong → `fresh=stale` | kết quả plan_version cũ → STALE | W06 |
| B03 | user_optional | user muốn dừng / tiếp / huỷ | `control <id>` pause, resume, cancel, status | `cancelled` không resume → build plan mới | W06 |
| B04 | capability_optional | muốn một lệnh thay 4 lệnh gõ tay | `run <id> <node> -- <lệnh agent>` + daemon `watch` + control-room | node thiếu verify → từ chối headless | W06 |
| B05 | recovery | agent im lặng quá lease | `next` đẩy node về `unknown` → `reconcile <id> <n>` chạy verify rồi mới lock lại | tối đa 3 attempt rồi failed | W06 |
| B06 | conditional_required | `kind` lạ chưa có trong `kind-glyphs.json` | tool sinh glyph tạm vào `kind-glyphs.local.json` + cảnh báo stderr → hỏi user có `/raise-issue` glyph mới không | không tự thêm vào sổ mặc định | W05 |
| B07 | user_optional | muốn mirror sang sổ Orca | `sync-orca <id> --run` (một chiều) | — | W06 |
| B09 | user_optional | user yêu cầu thêm việc / "vẽ thêm node" khi graph đã có | `add-node <id> --title … [--depends t1:data] [--blocks t5] [--files …] [--verify …] [--kind …] [--resources …]` → in `+ tN`, build lại, vẽ lại HTML, đưa link cho user | sinh cycle / > 20 node / dep lạ → tool từ chối, PLAN nguyên vẹn | W05 |
| B10 | recovery | `lock` báo `chờ RESOURCE` | node khác đang giữ claim xung đột → làm node ready khác trước, `ask <id> waiting` xem ai giữ; lock lại khi node kia xong | không tự `unlock` node của agent khác | W06 |
| B08 | conditional_required | node khai `**QC:**` | chạy QC độc lập sau verify rc 0; fail → `done_unverified` (run/set) hoặc `ready` (reconcile) | không khai → hành vi cũ | W06 |

### Validation và stopping
Tất định: `done` chỉ khi `verify` rc 0 (và QC nếu khai); lease/generation/op_key/CAS do tool quyết; `check-cycles` và `lint`/`build --strict` rc 2 khi hỏng; `audit` mở lại từng nguồn, bịa = 0. Cần người: duyệt HTML graph ở gate, xác nhận deps `gợi-ý`, xử lý node `blocked`. Vòng chạy dừng khi `next` báo hoàn tất; mỗi node tối đa 3 attempt.

### Examples
- **Positive:** PLAN 5 task, t2 và t3 cùng Depends t1 → `build` báo không cycle, không xung đột file → `ask t2 parallel` trả t3 → `next` cấp t1, xong thì cấp t2 + t3 song song mỗi cái một `lock --by`, `set done --gen` → `audit` bịa = 0 → atlas regen.
- **Boundary/failure:** t2 và t3 song song cùng ghi `src/api.ts` → `build` in ⚠ xung đột ghi cùng file → thêm `**Depends:** Task 2` vào t3 để ép tuần tự rồi build lại; agent t3 im quá lease → `unknown` → `reconcile` chạy verify trước khi lock lại.
- **Boundary:** model muốn nói "t4 tồn tại để mở khoá release" nhưng không có nguồn mở được → `answer … --label không-biết` (0.3), không gắn `chắc`.

### Reference — Phân cấp graph mẹ → con (PRD Reprise Graph Engine §4)
- `build <PLAN> --parent <gid>/<node>` → graph con gắn vào một node của graph mẹ (containment tree, KHÁC dependency DAG). Node mẹ có `child_graph`, join tự động: chỉ `done_unverified` khi MỌI node con xong (invariant 4); con có node `blocked` → mẹ `blocked`.
- Giới hạn cứng: depth ≤ 6, ≤ 20 node/graph. Vượt → tool từ chối, giảm scope thay vì đào sâu.
- Deps xuyên graph: `**Depends:** other-graph/t3` — thoả khi node đó xong ở graph kia. `check-cycles [dir]` gộp mọi graph, in ĐƯỜNG cycle cụ thể (`a/t2 → b/t3 → a/t2`), rc 2 (PRD §5.3).
- `lint <id>` — leaf đủ hợp đồng chưa (PRD §4.4): title · files · produces · verify · deps rõ. `build --strict` rc 2 nếu thiếu verify/files.

### Reference — Topology có lý do & tài nguyên có chủ (PRD v1.1 §23)
- **Depends parse NGHIÊM:** token không resolve được (ghi chú chen vào sau dấu `—`, `Task 1 và Task 2`, task không tồn tại, dep xuyên graph sai dạng `<gid>/<tid>`) là LỖI `build`, không bị nuốt — cạnh biến mất im lặng thì node ready sớm mà không ai thấy. Ngăn bằng `,` hoặc `;`; ghi chú để ở dòng khác.
- **Lý do cạnh:** `**Depends:** Task 1 (data), other-graph/t3 (control)`. Năm lớp cứng (data · contract · acceptance · effect_order · control) không bỏ được dù không truyền artifact — cổng duyệt không mang payload vẫn là cạnh thật. `preference` = chỉ do thứ tự viết. Reason KHÔNG nằm trong `spec_hash`: gắn lý do cho graph đang chạy không làm node đã xong thành stale.
- `audit-edges <id> [--json] [--strict]` — dry-run. Mã finding: `EDGE_UNJUSTIFIED` (khai Depends mà thiếu lý do → giữ) · `EDGE_INFERRED` (deps suy luận) · `PREFERENCE_REMOVABLE` (đề xuất bỏ) · `PREFERENCE_HAS_HIDDEN_CONSTRAINT` (ghi preference nhưng Consumes/Verify/QC của downstream nhắc tới Task, file hoặc output của upstream, hoặc hai node cùng ghi một file → giữ; so CHUỖI nên coupling không lộ ra chữ thì không bắt được). In critical path **đếm theo node** (unit-weight, KHÔNG phải thời lượng), số lớp và tập chạy-ngay trước/sau. `--strict` rc 2 khi còn `EDGE_UNJUSTIFIED`.
- **Resource claims:** key do tool chuẩn hoá (lowercase + normpath) nên alias khác chữ vẫn là một tài nguyên. `lock` lấy HẾT claim hoặc không lấy gì (không giữ A chờ B), soi mọi graph trong cùng store, chạy dưới một mutex admission. `exclusive` chặn mọi claim cùng key; `capacity:N` = KÍCH THƯỚC POOL của key — mỗi node đang giữ key (kể cả `shared`) chiếm 1 slot, các node khai N khác nhau thì lấy N nhỏ nhất (không phụ thuộc thứ tự lock, `shared` không lách được quota); `shared` thuần chỉ bị exclusive hoặc pool đầy chặn. Lease hết ở graph KHÁC cũng được reaper quét khi `lock`/`next` (claim không kẹt xuyên graph); `unlock` tay một node đang chạy đưa nó về `unknown` — reconcile trước khi lock lại. `build` in `ℹ … cùng claim` cho cặp song song — thông tin, không phải lỗi.
- `ask <id> waiting` — mỗi node chưa chạy kèm MỘT lý do: `data` (chờ upstream) · `gate` (HITL, cổng control/acceptance, verify chưa xanh, unknown chờ reconcile) · `resource` (claim bị giữ, nêu ai giữ) · `queue` (max_parallel đầy) · `control` (pause/cancel) · `retry` (hết 3 attempt) · `none`. `next` in thêm dòng cho node **ready nhưng chưa lock được** — ready ≠ admitted.
- Lớp topo (`ask parallel`) là **hình chiếu để giải thích**, không phải rào: node đủ deps là ready ngay dù node khác cùng lớp với upstream của nó chưa xong.

### Reference — Định danh, vòng khô, ngân sách lần gọi (PRD v1.1 §24–27)
- `reconcile-items --expected A,B,C --verdicts rows.jsonl [--universe N]` — ghép verdict (`supported|refuted|inconclusive`) theo `item_id`, không theo vị trí. `{A,A,B}` đủ 3 dòng vẫn THIẾU C → rc 2. Dòng `verdict: null` hoặc `status` ≠ ok = outcome thiếu CÓ ID (`errored_ids`), không bị lọc mất, không tính refuted; cùng item vừa có verdict vừa có dòng lỗi → `CONFLICTING_OUTCOME`; manifest rỗng cần `--allow-empty`; thiếu file verdict là lỗi, không phải "0 dòng". `coverage` tách hai mẫu số: xong/đã-chọn và đã-chọn/toàn-tập (`unknown` khi không biết — không báo 100%). Dùng khi fan-out một lô item (vd `/tc-run`) rồi gom kết quả.
- `dry-streak --prev N --complete 0|1 --new N` — vòng discovery khô chỉ tính khi vòng HOÀN TẤT và không có ứng viên mới; vòng lỗi reset về 0. Khô = heuristic dừng, không chứng minh đã rà hết.
- `cost-envelope <id> [--reviewers N] [--max-attempts N]` — đếm LẦN GỌI model trước dispatch: planner 1 + worker/node afk + reviewer × node có QC + synthesis 1; `max_calls` nhân trần retry; `expected` ghi unknown khi chưa có số đo. Verify shell = 0 token nhưng vẫn tốn CPU, báo riêng. Đừng nói "N agent" thay tổng call.

### Reference — Replan không phá lịch sử (PRD §10)
- `build` lại trên graph đã có = `plan_version + 1`; node bị bỏ vào `superseded[]` (giữ state cuối), node đổi hợp đồng (`spec_hash` = title/files/deps/verify/produces) mà đã xong → `fresh=stale` (chỉ cảnh báo, không lùi state).
- Kết quả cũ: `set done --plan-version N` với N ≠ hiện tại → STALE, không publish (invariant 2).
- `run` nhớ `plan_version` lúc dispatch: replan xảy ra GIỮA lúc agent chạy → kết quả là STALE, node về `ready` để làm lại theo spec mới (rc ≠ 0).
- `add-node` là replan một-node: chạy dưới mutex admission (hai lệnh song song không đè nhau), nhìn PLAN đúng như parser (bỏ qua code fence), mọi field phải MỘT dòng, `--blocks` từ chối node đang `locked|dispatched`, PLAN phải khớp graph (sửa tay thì `build` trước); id mới không tái dùng id node đã bị bỏ; `--blocks t5` chèn node mới TRƯỚC t5 (nối vào dòng Depends của t5, chưa có thì thêm). Build lại graph CON mà quên `--parent` vẫn giữ liên kết mẹ cũ.

### Reference — Control (PRD §8.3, invariant 11)
- `control <id> pause|resume|cancel|status`. "Yêu cầu" ≠ "đã dừng": `pause_requested` chỉ thành `paused` khi không còn node `locked|dispatched`; `next`/`lock` không cấp node mới khi không `active`. `cancelled` không resume — build plan version mới.
- `build --max-parallel N` (mặc định 4): `lock` từ chối khi số node đang chạy đã đủ (PRD §12.1).

### Reference — Daemon & control-room (PRD §8.4: lease 60 s · heartbeat 15 s · reaper 15 s)
- `run <id> <node> [--hb 15] [--lease-sec 60] [--strict] -- <lệnh agent>` — thay 4 lệnh gõ tay: lock ngắn → dispatched → spawn lệnh → heartbeat theo pid → exit 0 thành `done` (verify tự chạy), khác 0 thành `failed`. Node không có `verify` bị từ chối headless (`--allow-unverified` để ép). Tự ghi thư mục vào registry `~/.orca-graph/registry.json` và tự spawn daemon nếu chưa có (`ORCA_GRAPH_NO_DAEMON=1` để tắt, `ORCA_GRAPH_HOME` đổi thư mục nhà).
- **Allow-list ghi (GH#162):** khi trong git repo, `run` diff file THẬT bị đổi (tracked sửa + untracked mới, so với NGAY TRƯỚC lúc spawn) với `files` khai của node. Ngoài phạm vi → mặc định chỉ CẢNH BÁO (ghi vào `note` của event `done`); `--strict` mới phục hồi cứng (untracked mới bị xoá, tracked sửa bị `git checkout` về HEAD). Không phải git repo (vd store nằm ngoài repo) → tự bỏ qua, không lỗi. Bookkeeping của CHÍNH orca-graph (`.graph.json`/`.events.jsonl`/`.locks/`) luôn bị loại khỏi diff, không tính là "agent ghi".
- `watch [--once] [--interval 5] [--idle-sec 600]` — **một daemon cho cả máy**, lock `daemon.lock` theo pid. Mỗi lượt chỉ đọc các dir trong registry còn node chạy (chi phí theo số node chạy, không theo số dự án mở; đo 84 ms/lượt kể cả khởi động Python): reaper lease hết → `unknown` → có verify thì reconcile ngay; in bảng sống/chết; registry rỗng quá idle-sec thì tự thoát; graph đổi thì regen control-room.
- `fdk/tools/build-control-room.py` → `llmwiki/html/control-room.html` — trang đầu tiên mở ra, data-first (chỉ đọc registry, graph.json, problem-tree, tokens.jsonl, audit-log): đang chạy gì toàn máy + trần, tiến độ từng graph + node kẹt, nợ mở, chi phí hôm nay + khoảng cách tự chấm/audit. Tự refresh 5 s; daemon regen mỗi lượt và mỗi lần `run` bắt đầu/kết thúc nên trang LIVE không cần server. Bậc 2 (server + bấm pause/cancel) và bậc 3 (nhúng Orca) chưa làm, chỉ làm khi bậc 1 dùng hằng ngày thấy thiếu.
- Sống/chết ≠ đúng/sai: daemon chỉ biết process còn hay mất; `done` hay làm lại vẫn do `verify` quyết. Process sống mà treo thì heartbeat vẫn xanh — đặt `**Verify:**` idempotent và trần thời gian theo node.

### Reference — Recap
`/orca-graph` = PLAN → graph.json có deps → `ask` trả lời 5 câu hỏi tất định → dispatch theo lớp có khoá/lease/gen → state bền append-only → `answer`/`audit` chấm model theo rubric 1/0/0.3/0.5/bịa=0 → HTML 1 graph + atlas 2D.
Use-case bất ngờ: chạy `build` trên PLAN cũ đã làm xong để **kiểm lại** xem hồi đó có 2 task ghi cùng file mà chạy song song không; hoặc `related` để thấy PLAN mới chạm file nào của PLAN cũ trước khi đụng.
