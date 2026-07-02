---
type: concept
title: Feature Catalog — mọi năng lực framework & VÌ SAO cần nó
status: active
tags: [fdk, features, catalog, why, eval, council, loop, harness]
timestamp: 2026-06-28
id: feature-catalog
---

# Feature Catalog — và VÌ SAO mỗi cái phải có

Danh sách năng lực của framework kèm **lý do tồn tại** (không phải "có thì tốt" mà "thiếu thì hỏng gì"). Bản máy-đọc luôn-mới của danh sách là `fdk/CAPABILITIES.md` (sinh bằng code); trang này giải thích *tại sao*. Mọi feature đều **deterministic, 0-token runtime, fail-open**, và nếu có phần cần model thì phần đó bị nhốt sau một adapter `verified:false` (theo [[fdk]] Phần 4 + skill `/build-now-adapt-later`).

## Nhóm 1 — Hạ tầng đảm bảo (không phụ thuộc agent nhớ)

- **code-logger** (`harness/scripts/code-logger.py`) — *Vì sao:* AGENT.md bảo "luôn append log.md sau mỗi thao tác", nhưng đó là kỷ luật agent — agent QUÊN là thường. code-logger để **hook (PostToolUse) ghi log bằng CODE** vào `events.jsonl` và **Stop hook render block tự-động trong log.md**, nên log phản ánh thực tế thay vì trông chờ agent.
- **cost-attribution** (`code-logger.py --run-cost` ← Stop hook; `--cost-summary`) — *Vì sao:* Trụ 1 Outer Harness — "API bill $X, tiền đi đâu?" không trả lời được vì cost rải trên laptop. Stop hook đọc **transcript của run** (nguồn token thật), cộng theo model, quy ra cost rồi **upsert 1 bản ghi / run** vào `harness/metrics/cost-by-session.json` (idempotent, không nhờ agent nhớ). Đơn giá là ẩn số → nhốt trong adapter `harness/cost-rates.json` (`verified:false`, build-now-adapt-later); summary cảnh báo ⚠️ khi rates chưa verify. Xem [[outer-harness-evaluation]].
- **build-capabilities** (`fdk/tools/build-capabilities.py` → `fdk/CAPABILITIES.md`) — *Vì sao:* framework đã quá lớn (58 skill + rule + tool) → agent không chắc biết hết cái gì có → nhiều thứ không bao giờ được dùng. Bản đồ năng lực **sinh từ đĩa bằng code** (không hardcode, có `--check` gate chống drift) + pointer trong AGENT/CLAUDE → agent LUÔN biết đúng đồ nghề.
- **fdk-gate** (`harness/scripts/fdk-gate.py`) — *Vì sao:* "xong" một feature là mơ hồ. fdk-gate là **định-nghĩa-hoàn-thành máy-đọc**: 13 step (mọi validator + freshness gate), board ✓/✗, wired **pre-push** → chức năng mới phải pass đủ step mới cho push.

## Nhóm 2 — Harness tự gác chính nó (drift mà harness cũ không bắt)

- **harness-lint** + `wikidirs.py` — *Vì sao:* hằng số content-dir từng là 6 ở 3 file nhưng 4 ở 2 file khác → broken wikilink ở `architecture/`·`tours/` lọt gate. Lint bắt hằng-số-lệch + wiring policy→settings lệch — harness canh chính nó.
- **harness-doctor** — *Vì sao:* harness fail-open khắp nơi (để bền) → một validator hỏng âm thầm vẫn pass mọi thứ, không ai báo "rail đã tối". Doctor chạy fixture sai/đúng qua từng validator, **chứng minh mỗi rail còn cắn**. (Đã bắt ngay một drift validator deployed bị stale.)
- **adapt-registry** — *Vì sao:* marker `verified:false`/`ASSUMPTION`/`⚠️` của BNAL chỉ là prose; agent quay lại không biết "còn gì chưa kiểm chứng". Registry liệt kê + **gate chống guess rò qua adapter** (Step-7).
- **agent_claude_parity / duplicate_basename / skill-registry** — *Vì sao:* AGENT.md(14)≠CLAUDE.md(9); dup design-pattern; marketplace tụt 30 skill — toàn bộ là drift cross-file mà không validator nào soi. Ba cổng này đóng.

## Nhóm 3 — Tri thức & khám phá (scale lên không lạc)

- **wiki-graph** — *Vì sao:* wiki-health đếm cạnh rồi **vứt chiều inbound** → không hỏi được "ai trỏ tới X" trước khi đổi/xoá. Query đồ thị tất định 0-token (backlinks/orphans/broken/export) cho impact-check.
- **build-docs-index** (→ `llmwiki/html/index.html`) — *Vì sao:* README hứa `index.html` "Dashboard chính" nhưng nó không tồn tại; 26 trang docs không hub. Generator quét live → dashboard glass lọc/sort được.
- **build-skill-search** (BM25 `find-skill`) — *Vì sao:* 58 skill khó tìm; `find-skills` tốn một lượt LLM mỗi câu. Chỉ mục BM25 offline xếp hạng tức thì + nhúng vào cheatsheet.

## Nhóm 4 — Vòng đời & tự-tiến-hoá

- **artifacts** + **index_sync --fix** — *Vì sao:* 54 artifact local chất đống không lifecycle; index hand-maintained đã drift. Manifest + dedup gate + **self-healing index** (auto-thêm file mới vào index).
- **new-skill** scaffolder — *Vì sao:* thêm skill = 4 chỗ tay → drift bảo đảm. Sinh 2 file máy giống-hệt + in lệnh register.
- **dispatch-verify** — *Vì sao:* R7 gác *lời hứa* proposal trước fan-out, nhưng sau dispatch không gì xác nhận *đáp đất*. Đối chiếu task khai-done với file thật (bắt "khai done nhưng vắng").
- **failure-flywheel** — *Vì sao:* bài học đắt nhất là lỗi lặp lại, nhưng "nhớ để rút rule" là kỷ luật người-hay-quên. Gom lỗi→đếm→**tự gieo stub đề xuất rule/skill** vào luồng /propose (dừng chờ duyệt).

## Nhóm 5 — Eval & đánh giá đa-agent (trend 2026)

- **wikieval** — *Vì sao:* framework *sinh* được nhưng không *chứng minh thay đổi có giúp gì*. Wiki goldens → cascade assert tất định + baseline hồi quy chặn merge (exit 2) — eval rẻ, lặp-được, không như eval-dựa-LLM đắt và bất định. Judge LLM nhốt sau adapter.
- **council** (Karpathy 3-stage) — *Vì sao:* một model trả lời câu khó dễ tự tin sai/thiên vị. Hội đồng nhiều model: trả lời độc lập → chấm chéo **ẩn danh** → chairman tổng hợp. Phần TOÁN (ẩn danh, mean-rank, chống thiên-vị-vị-trí) tất định byte-identical; "model nào ngồi ghế nào" nhốt 1 file config.
- **loop-runner** — *Vì sao:* vòng lặp agent dễ chạy hoang/tự-tuyên-bố-xong. Driver có **chốt dừng bắt buộc** (max-iter/budget/no-progress state-hash/escalate) và "pass" quyết bằng **exit-code lệnh thật** (agent không cãi được). Critique LLM = adapter.
- **trace-grader** — *Vì sao:* đáp án đúng có thể đi đường tệ ("corrupt success": force-push, retry-storm, sửa file chưa đọc) hoặc chỉ ăn may. Chấm **đường đi** (tool/thứ tự/pass^k) bằng luật tất định; agent-as-judge = adapter.
- **health-dashboard** — *Vì sao:* tín hiệu sức khỏe rải 8+ validator. Một lệnh → trang glass traffic-light + bảng drift.

## Cách thêm một feature mới cho HỢP LỆ
Xem checklist trong [[fdk]] Phần 4 (bản máy-đọc = `harness/scripts/fdk-gate.py`): code+test → (rule→policy / skill→mirror+LOOP_MAP+AGENT&CLAUDE+CAPABILITIES / gate→pre-commit+CI+fdk-gate) → ẩn số→adapter → wiki "vì sao" → docs → `fdk-gate` GREEN → push.

## Origin
- **Source:** phiên autonomous 2026-06-28 — `/goal` "triển khai full 14 feature + logger-by-code + agent-awareness + master-wiki + fdk-gate + 5 feature mới (eval/council/loop) + adapt-audit". Why-paragraphs chưng cất từ các build-agent. Commit `6e71974`.
- **Liên quan:** [[fdk]], [[rule-registry]], `fdk/CAPABILITIES.md`.
