---
name: orca-graph
description: Phân việc dạng ĐỒ THỊ PHỤ THUỘC trên PLAN.md — trả lời 5 câu hỏi (task này cần việc gì · cái gì chạy song song · phụ thuộc vào gì · tồn tại để làm gì trong graph · liên hệ graph cũ) bằng tool tất định, dispatch theo lớp topo có KHOÁ + lease + generation, state lưu bền append-only (events.jsonl), 2 file python vẽ (1 graph / atlas 2D mọi graph), mọi câu trả lời của model gắn nhãn chắc|gợi-ý|không-biết + nguồn, audit bịa=0. Gọi khi user nói "orca-graph", "graph phân việc", "task nào song song", "phụ thuộc gì", "vẽ graph task", "dispatch theo graph", "/orca-graph".
---

# Skill: orca-graph

Nhánh của `orca-workflow`: cùng propose → gate → plan → dispatch, nhưng **deps là DỮ LIỆU** (graph.json),
không phải suy đoán trong đầu. Runtime: `harness/scripts/orca-graph.py`. Vẽ: `fdk/tools/graph-viz.py`
(1 graph) + `fdk/tools/graph-atlas.py` (atlas 2D). Store mặc định `llmwiki/graph/`.

## When to use
- Có PLAN.md ≥ 3 task và cần biết: cái gì chạy song song, cái gì chờ cái gì, chạy tới đâu rồi.
- Dispatch nhiều agent và cần khoá để 2 agent không giành cùng task / ghi cùng file.
- Việc còn dở nhiều phiên: state phải sống qua crash, không được "nhớ trong đầu".
- KHÔNG dùng cho sự cố (→ `orca-issue`), không dùng khi chưa có PLAN (→ `/propose` rồi `/plan`).

## Steps
0. Pre-work sweep như orca-workflow (`pull-gate-sweep.sh`) nếu có harness.
1. **PLAN có chưa?** Chưa → gọi skill `plan`. Khuôn `/plan` có dòng `**Depends:** Task 1, Task 3` và `**Verify:** <lệnh rc 0>` — điền thật; thiếu Depends thì tool SUY từ Consumes/Produces và gắn nhãn `gợi-ý`.
2. **Dựng graph:** `python3 harness/scripts/orca-graph.py build <PLAN.md>` → in cycle, deps suy luận, và **xung đột ghi cùng file** giữa 2 node song song (⚠ → thêm Depends để ép tuần tự, hoặc chấp nhận có lý do).
3. **Trả lời 5 câu hỏi — bằng tool trước, model sau:**
   - `ask <id> needs` · `ask <id> parallel` · `ask <id> deps <n>` · `ask <id> why <n>` · `ask <id> related`.
   - Phần model bổ sung (ý nghĩa, liên hệ ngữ nghĩa với graph cũ, rủi ro) → **ghi bằng `answer`** kèm nhãn + nguồn:
     `answer <id> <n> --q why --label chắc|gợi-ý|không-biết --score S --evidence file:path:line edge:a->b event:<op_key> absence:<lệnh> --text "..."`.
   - Rubric (user chốt 2026-09-12): đúng **1** · sai **0** · không-biết **0.3** · gợi-ý có nguồn thật **0.5** · **bịa nguồn 0**. Không chắc → nói `gợi-ý`/`không-biết`, đừng gắn `chắc`.
4. **Vẽ + gate:** `python3 fdk/tools/graph-viz.py llmwiki/graph/<id>.graph.json` → gửi HTML cho user duyệt (`gate-create` như orca-workflow).
   - Node trên đồ thị vẽ theo **kind** của task (`**Kind:** build|test|fix|research|docs|design|review|security|infra|data|migrate|deploy|release|cleanup|integration|wiki` trong PLAN.md, mặc định `build`) — icon + shape + màu nền tra ở `skills/orca-graph/assets/kind-glyphs.json` (sổ mặc định, sửa/thêm tại đây là DÙNG CHUNG mọi graph). Viền node vẫn là **state** (không đụng).
   - `kind` lạ chưa có trong sổ → tool tự sinh tạm (monogram + màu/hình theo hash, ghi vào `kind-glyphs.local.json` cùng thư mục) và **in cảnh báo ra stderr**. Thấy cảnh báo này → **hỏi user** có muốn `/raise-issue` để submit glyph mới vào `kind-glyphs.json` không; đừng tự ý thêm vào sổ mặc định mà không hỏi.
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

## Phân cấp graph mẹ → con (PRD Reprise Graph Engine §4)
- `build <PLAN> --parent <gid>/<node>` → graph con gắn vào một node của graph mẹ (containment tree, KHÁC dependency DAG). Node mẹ có `child_graph`, join tự động: chỉ `done_unverified` khi MỌI node con xong (invariant 4); con có node `blocked` → mẹ `blocked`.
- Giới hạn cứng: depth ≤ 6, ≤ 20 node/graph. Vượt → tool từ chối, giảm scope thay vì đào sâu.
- Deps xuyên graph: `**Depends:** other-graph/t3` — thoả khi node đó xong ở graph kia. `check-cycles [dir]` gộp mọi graph, in ĐƯỜNG cycle cụ thể (`a/t2 → b/t3 → a/t2`), rc 2 (PRD §5.3).
- `lint <id>` — leaf đủ hợp đồng chưa (PRD §4.4): title · files · produces · verify · deps rõ. `build --strict` rc 2 nếu thiếu verify/files.

## Replan không phá lịch sử (PRD §10)
- `build` lại trên graph đã có = `plan_version + 1`; node bị bỏ vào `superseded[]` (giữ state cuối), node đổi hợp đồng (`spec_hash` = title/files/deps/verify/produces) mà đã xong → `fresh=stale` (chỉ cảnh báo, không lùi state).
- Kết quả cũ: `set done --plan-version N` với N ≠ hiện tại → STALE, không publish (invariant 2).

## Control (PRD §8.3, invariant 11)
- `control <id> pause|resume|cancel|status`. "Yêu cầu" ≠ "đã dừng": `pause_requested` chỉ thành `paused` khi không còn node `locked|dispatched`; `next`/`lock` không cấp node mới khi không `active`. `cancelled` không resume — build plan version mới.
- `build --max-parallel N` (mặc định 4): `lock` từ chối khi số node đang chạy đã đủ (PRD §12.1).

## Ngoài phạm vi PRD (nói thẳng, không giả vờ có)
PostgreSQL ledger, sandbox/runtime isolation, secret gateway, ngân sách tiền, LangGraph, integration queue/candidate hash, compensation cho effect ngoài. Tool này là file-based cho một máy; cần những thứ trên thì đó là engine khác, không phải nâng cấp orca-graph.

## Máy state mỗi node
`proposed → ready (mọi deps xong) → locked → dispatched → done | done_unverified | failed | unknown`; `blocked` = HITL chờ người.
Ba chiều tách nhau: `state` (vòng đời) · `verified` (verify rc 0?) · `fresh` (upstream làm lại sau khi mình xong → `stale`, chỉ cảnh báo).
Luật vay từ Reprise PRD: op_key idempotent · CAS `--if-rev` · generation chặn kết quả cũ · lease hết → `unknown` không phải `failed` · không verify thì không `done`.

## Rules
- **Lock chỉ kiểm soát DISPATCH**, không kiểm soát side-effect của agent đã chạy. Muốn cách ly thật → worktree riêng mỗi task.
- **Không dispatch node `blocked`** (HITL) cho CLI headless — nó sẽ đoán thay người rồi im lặng (bài học 250626, giao ~1/5).
- **Mọi câu trả lời của model về graph phải qua `answer`** với nhãn + nguồn mở được. Không có nguồn → chọn `không-biết` (0.3) thay vì bịa (0).
- Deps `gợi-ý` (suy luận) phải được user xác nhận hoặc khai `**Depends:**` trước khi dispatch lớp đó.
- Không xoá/sửa tay `events.jsonl`; sai thì append event sửa. `graph.json` chỉ là cache — hỏng thì `build` lại, state fold từ events.
- HTML sinh ra: toggle sáng/tối + full path + thuật ngữ có giải nghĩa (luật fdk) — 2 file vẽ đã lo, đừng viết HTML tay.
- Không làm được (nói thẳng): coupling ngầm không lộ ra file; rollback tự động khi agent chết nửa chừng; sync 2 chiều với sổ Orca; atlas > ~500 node cần graphviz; lock chỉ chặn dispatch, không chặn effect ngoài.

## Recap
`/orca-graph` = PLAN → graph.json có deps → `ask` trả lời 5 câu hỏi tất định → dispatch theo lớp có khoá/lease/gen → state bền append-only → `answer`/`audit` chấm model theo rubric 1/0/0.3/0.5/bịa=0 → HTML 1 graph + atlas 2D.
Use-case bất ngờ: chạy `build` trên PLAN cũ đã làm xong để **kiểm lại** xem hồi đó có 2 task ghi cùng file mà chạy song song không; hoặc `related` để thấy PLAN mới chạm file nào của PLAN cũ trước khi đụng.
