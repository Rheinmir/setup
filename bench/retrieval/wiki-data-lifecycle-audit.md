# Rà soát mọi thứ SINH nội dung trong `.llmwiki/` và các sổ harness (openship, 13/10/2026)

Nguồn: đọc mã đã cài ở `~/.claude/harness` (hooks, scripts, fdk/tools), `openship/.harness/poc-vendor-neutral/bin`, các skill `~/.claude/skills/*`, đối chiếu file thật trên đĩa openship (mtime, nội dung). Ký hiệu: `H/` = `~/.claude/harness/`, `P/` = `openship/.harness/poc-vendor-neutral/bin/`.

## 0. Thực tế trên đĩa openship

| Cây | Có gì | Mới nhất | Ai sinh |
|---|---|---|---|
| `wiki/concepts` 10 + `wiki/entities` 7 | trang kiến thức, 25/27 có trích dẫn file | 24/09 (chưa sửa lần nào từ đó) | skill `orca-onboard` một lần |
| `wiki/sources/draft` 5 | PLAN, propose, issue upstream | 10/10 | skill propose / plan / surface-coverage (Write) |
| `wiki/draft/{orca,unknown,cave,uiux}` 3 | onboard report, unknown-ledger | 29/09 | skill orca-onboard, unknown-ledger |
| `wiki/sources/provenance` 16 | 1 trang/ngày, 16/16 cùng why từ git | 13/10 | Stop-hook distill |
| `wiki/index.md` | 46 dòng | 13/10 | Stop-hook index_sync --fix + skill |
| `wiki/ledger.jsonl`, `wiki/stale.json` | sự kiện ghi wiki, cờ stale | 10/10 | PostToolUse wiki_ledger |
| `wiki/log.md` | 3 dòng skill + 3 dòng session | 09/10 | SessionEnd + skill |
| `handover/` 7 | bàn giao khi chạm trần token | 13/10 | UserPromptSubmit session-continue |
| `html/` 23 html + 21 json + 28 png | archify, docs-site, wiki-graph, onboarding, problem-tree | 13/10 | skill / Stop (wiki-graph) / SessionEnd (problem-tree) |
| `graph/` | orca-graph 1 graph | 03/10 | skill orca-graph |
| `.harness/metrics/` | memory.jsonl 22, scratch-log 19 dòng, context-receipts | 13/10 | Stop / SessionStart |
| `harness/metrics/` (KHÔNG dấu chấm, cây lạc) | cost-by-session, events, failures, self-report, sync-log, tasks | | writer viết cứng `harness/metrics` |

## 1. Writer TỰ ĐỘNG (hook)

| Writer | Kích hoạt | Đích | Nội dung từ | Ai đọc lại bằng máy |
|---|---|---|---|---|
| hooklib `audit` | mọi hook | `.claude/audit/<ngày>.jsonl` | payload hook | session_end summarize; ledger-snapshot |
| code-logger `render_md` (stop.py:420) | Stop | `llmwiki/wiki/log.md` **đường cứng → không làm gì ở khách** | events.jsonl | — |
| code-logger `run_cost` | Stop | `harness/metrics/cost-by-session.json` (cây lạc) | usage trong transcript | token-budget, session-continue, self-report |
| okf-scan `verify` | Stop | `.harness/metrics/context-receipts.jsonl` | tool_use trong transcript | self-report |
| scratch-log `auto` | Stop khi git bẩn | `.harness/metrics/scratch-log.jsonl` | **git log -1 + status** | distill |
| scratch-log `distill` | Stop khi bẩn | `wiki/sources/provenance/DDMMYY-session-provenance.md` **ghi đè cả file, 1 ngày chỉ còn phiên cuối** | scratch-log + ledger.jsonl | okf-scan bỏ qua; index_sync thêm dòng; wiki-graph vẽ node |
| memory-map | Stop khi bẩn | `llmwiki/html/memory-map.html` **cứng → FileNotFoundError ở khách, không ghi** | | — |
| mem-rank `episode` | Stop khi bẩn, 1/phiên | `.harness/metrics/memory.jsonl` | **did = git log -1, files = status** | session_start recall; okf-scan; self-report |
| build-wiki-graph (stop regen_docs) | Stop, debounce 180s | `.llmwiki/html/wiki-graph.html` | mọi .md + ledger + stale | người; session_start so mtime |
| provenance-log / token-budget / agent-trace | Stop, cùng khối try sau wiki-graph | `.harness/metrics/provenance-log.jsonl`, `harness/metrics/tokens.jsonl` | git status + HEAD | **không thấy file trên đĩa → suy ra bị cắt vì wiki-graph hết ngân sách 20s** |
| index_sync `--fix` | Stop khi status có `wiki/` | `wiki/index.md` khối auto | type + H1 trang | index_sync R3; wiki-health |
| P/harness-events `m_stop` | Stop (đăng ký 2 lần) | `.claude/audit/log.md` | audit.jsonl | người |
| P/harness-events `m_audit` | PostToolUse Write/Edit | `.claude/audit/audit.jsonl` | payload | `_machine_log` |
| wiki_ledger `append_event` | PostToolUse Write/Edit vào wiki | `wiki/ledger.jsonl` | **payload tool_use** (việc thật) | distill; wiki-graph; memory-map |
| wiki_ledger `propagate_stale` | như trên | `wiki/stale.json` | relations trong frontmatter | wiki-graph; wiki-sync; tidy; skill lint |
| code-logger `record` (post_tool_use) | PostToolUse | `harness/metrics/events.jsonl` | payload | render_md, control-room |
| | | prefix kiểm tra `llmwiki/ harness/ skills/ fdk/` **không khớp `.llmwiki/`** → ở khách không ghi sự kiện wiki | | |
| flywheel `record_bite` | PreToolUse khi validator chặn | `harness/metrics/failures.jsonl`, `guardrails/*.md` | stderr validator | self-report; session_start chỉ đọc `.harness/` + cần manifest → **ở khách không ai đọc** |
| user_prompt_submit `save_count` | mỗi prompt | `.claude/audit/.docs-gate.json`, `.self-report.json` | bộ đếm | chính nó |
| session-continue `write_handover` | prompt khi chạm trần token | `handover/DDMMYY-<sid>-continue.md` | tin nhắn cuối + cost + git status | phiên mới (qua prompt) |
| self-report + wiki-sync `flag_stale` | mỗi 50 prompt | `harness/metrics/self-report.jsonl`, `sync-log.jsonl`, `wiki/stale.json` | các sổ; git diff neo..HEAD (openship **chưa có neo**) | raised.json tự đọc; **self-report.jsonl, sync-log không ai đọc** |
| okf-scan `query` (session_start) | SessionStart | `.harness/metrics/context-receipts.jsonl` | wiki frontmatter + memory; **truy vấn = did episode trước (= git subject)** | verify; self-report |
| session_end `main` | SessionEnd | `wiki/log.md` 1 dòng | audit của phiên | người |
| P/harness-events `m_session_end` | SessionEnd | `html/problem-tree.html` thêm node auto | **git diff + untracked** | control-room chỉ đọc `fdk-problem-tree.html` → **không đọc**; người |
| ledger-snapshot `export` | SessionEnd | `~/.claude/overstack-snapshots/…` | glob `harness/metrics/*.jsonl` **không gồm `.harness/`** → memory, receipts, scratch không được backup | import tay |
| handoff-log | SessionEnd | `harness/metrics/handoff-log.jsonl` | orchestration inbox | CLI tay |

## 2. Writer GỌI TAY (CLI / skill)

| Writer | Đích | Nguồn | Đọc lại |
|---|---|---|---|
| scratch-log `note` | scratch-log.jsonl | agent viết why | distill |
| mem-rank add/episode/compact/delete/import; skill record-episode | memory.jsonl | agent | recall, okf-scan |
| mem-rank `export-okf` | mặc định `llmwiki/wiki/sources/memory/` **cứng → đẻ cây lạc ở khách** | memory.jsonl | không ai |
| wiki-sync `--mark-synced` | `wiki/.last-sync.json`, stale.json | git HEAD + hash wiki | session_start wiki_drift |
| okf-check `--migrate` | frontmatter trang wiki | chính trang | validator R9 |
| unknown-ledger | `ROOT = parents[2]` → **ghi vào ~/.claude/harness, không phải wiki khách** | | — |
| tidy | `sources/draft/archive`, `html/archive`, index.md | status frontmatter + `harness/metrics/tasks.json` cứng | index_sync |
| flywheel `--draft` | `llmwiki/wiki/sources/draft` **cứng** | failures.jsonl | người |
| code-logger task | `harness/metrics/events.jsonl`, `tasks.json` | agent | tidy, docs-curate |
| orca-graph engine | `graph/*.graph.json, events, html`, PLAN trong sources/draft, `html/control-room*.html` | PLAN.md + lệnh agent | orca-graph; hooklib.orca_graph_running |
| docs-curate | `ROOT = parents[2]` → **ghi vào ~/.claude/harness** | | — |
| checkpoint | `.checkpoints.jsonl` gốc repo | git | checkpoint CLI |
| Skill propose / plan | sources/draft, html seq, index, log | agent | okf-scan (chữ), orca-graph |
| Skill ingest / wiki-create / join-project / onboard-codebase / orca-onboard | concepts, entities, sources, draft/orca, html onboarding, index, log | agent đọc mã | okf-scan (chữ + cạnh file) |
| Skill query / lint / tidy / docs-curate | sửa concepts, entities, ADR, archive, index, log; wiki-sync --mark-synced | agent | okf-scan |
| Skill orca-handover | `wiki/sources/handover/` (khác `.llmwiki/handover/` máy sinh) | agent | người |
| Skill docs-site-macos, cursor-animated-sites, md-to-html, council, br, archify… | `html/DDMMYY-*.html` | agent | người |
| Skill wikieval / teach-me | `wiki/sources/evals` | agent | wikieval |
| Nhóm skill taste/caveman/imagegen/… | `wiki/draft/{cave,uiux,orca}` | agent | okf-scan (chữ) |
| CI `harness.yml` | chỉ đọc (llmwiki-validate), wikieval bỏ qua vì chưa baseline | | |

## 3. Kết luận rà soát

**(a) Tự động mỗi lượt/phiên:** run_cost, okf verify, scratch auto, distill, episode, index_sync --fix, audit ×2, machine-log; wiki-graph/provenance-log/token-budget có trong mã nhưng thực tế không chạy tới. **Mỗi lần ghi file wiki:** ledger + stale. **Mỗi 50 prompt:** self-report + wiki-sync. **Khi chạm trần:** handover. Mọi thứ còn lại gọi tay.

**(b) Lấy từ git HEAD/status thay vì việc thật:** episode, scratch auto, provenance, provenance-log, problem-tree stub, truy vấn okf-scan đầu phiên, "repository state" trong handover, cờ code-drift. **Lấy từ việc thật:** ledger + stale (payload tool), audit, cost, verify, dòng log.md SessionEnd, tin nhắn cuối trong handover.

**(c) Không máy nào đọc lại:** `wiki/log.md`, `.claude/audit/log.md`, `sources/provenance`, `html/problem-tree.html` ở khách, `self-report.jsonl`, `sync-log.jsonl`, `guardrails/*.md` ở khách, provenance-log/agent-trace/handoff-log/snapshot (chỉ CLI tay), mọi HTML.

**(d) Hỏng ở dự án khách vì đường cứng `llmwiki/` hoặc `harness/metrics` hoặc `parents[2]`:** code-logger render_md, memory-map, export-okf, flywheel --draft, unknown-ledger, docs-curate, post_tool_use prefix, ledger-snapshot glob, và cả cây `harness/metrics/` (7 file) nằm sai chỗ so với `.harness/metrics/` (3 file).

**(e) Phần wiki kiến thức (27 trang) chỉ có MỘT nguồn sinh:** skill orca-onboard chạy một lần 24/09; từ đó không hook nào cập nhật nội dung trang, chỉ có index/ledger/provenance mọc thêm. wiki-sync chưa có neo nên không ai biết code đã trôi bao xa so với wiki.
