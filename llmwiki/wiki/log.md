## 2026-09-19 — fdk-uat — ship SWH v1.1 Reuse Layer (66cd426)
- PHA 1 canary (3 biến override): 3 trụ ✓ · test-broad 80/80 · npx ghi mới 103 skill · `new-skill` bản mới có `reuse_decision` · `skill-reuse.py` ở engine global · catalog KHÔNG ship (framework-only, đúng thiết kế; `new-skill.py` không có ở engine global nên không ghi rác) · orchestration skills reachable · worktree Orca `uat-260919-1422` assert thấy.
- PHA 2 main-URL (không override, ref `rheinmir/setup#orca`): sentinel khớp lượt 1 · test-broad 80/80 · `reuse_decision` có trong skill cài · `skill-reuse.py` global.
- Canary đã xoá.

## 2026-09-20 — ingest — Reprise-Graph-Engine-Full-Cycle-PRD (1).md

- tạo `sources/200926-reprise-graph-engine-prd-v11.md` — phần chênh v1.1 (§22–30) và bảng áp vào orca-graph v3
- sửa `sources/120926-reprise-graph-engine-prd.md` — thêm mục "Bản kế tiếp" trỏ sang v1.1
- sửa `index.md` — thêm dòng source v1.1

## 2026-09-20 — orca-graph — v3 + tách repo + review

- tạo `sources/draft/200926-orca-graph-v3-PLAN.md` — PLAN 12 task, chạy bằng graph `200926-orca-graph-v3`
- tạo `sources/draft/200926-orca-graph-v3-review.md` — báo cáo review độc lập, 16 lỗi CAO/VỪA đã sửa kèm test
- sửa `index.md` — thêm hai dòng draft trên

## 2026-09-20 — orca-graph — repo_role + font Lexend Deca Light + luồng cài

- tạo `sources/draft/200926-repo-role-ship-flows-PLAN.md` — PLAN 13 task, graph `200926-repo-role-ship-flows`
- sửa `index.md` — thêm dòng draft trên
- tạo `sources/draft/200926-repo-role-ship-flows-review.md` — báo cáo review độc lập trước khi push

## 2026-09-22 — ingest + orca-graph — Reprise-CoCanvas-Product-Grade-PRD.md

- tạo `sources/220926-reprise-cocanvas-prd.md` — tóm tắt PRD (ba lớp, ADR-001/002/003, ChangeSet, commit Git/DB, phạm vi C0/C1/C2) và cách bẻ backlog
- tạo `sources/draft/220926-cocanvas-m1-foundation-PLAN.md`, `…-m2-agent-design-PLAN.md`, `…-m3-chain-release-PLAN.md` — 28 ticket CC thành 10/10/8 task, cạnh xuyên graph có lý do
- build 3 graph trong `llmwiki/graph/` + HTML + atlas; check-cycles OK, audit-edges --strict rc 0, lint đủ hợp đồng
- sửa `index.md` — thêm dòng source CoCanvas

## 2026-09-22 — tách dự án — Reprise CoCanvas ra repo riêng

- xoá `sources/220926-reprise-cocanvas-prd.md` và 3 PLAN `sources/draft/220926-cocanvas-*-PLAN.md`, bỏ 4 dòng tương ứng trong `index.md`, xoá 3 graph `llmwiki/graph/220926-cocanvas-*`
- lý do: user muốn CoCanvas là dự án riêng; toàn bộ đã chuyển sang `/Users/giatran/orca/reprise-cocanvas` (commit 01d59b1: docs/prd, docs/prd-summary.md, docs/research, plan/ + store orca-graph `plan/graph/`)
- giữ nguyên `llmwiki/raw/prd/Reprise-CoCanvas-Product-Grade-PRD.md` (luật: không ghi vào raw/)

## 2026-09-23 — orca-graph + build — PRD Overnight loop (Nightshift) vào graph và code

- PLAN sinh thẳng từ PRD §09 bằng `scratchpad/gen_nightshift_plans.py`. PRD có 24 ticket, vượt trần 20 node/graph, nên tách HAI graph: `230926-nightshift-core` (N01–N13, 13 node) và `230926-nightshift-verify-ops` (N14–N24, 11 node, deps xuyên graph). `check-cycles`: không cycle.
- Code nằm ở repo MỚI, độc lập `/Users/giatran/orca/nightshift` (D01: core chỉ dùng stdlib, không import Overstack), 3 commit local: 044a974, 20e9aaa, 19161be. Suite: 120 test xanh, 1 test skip; chaos 16 seed xanh (SIGKILL ở 8 ranh giới); cổng AT01–AT36 đều có test.
- Graph 1: 13/13 done. Graph 2: 8/11 done; mỗi node qua `set done` chạy lại lệnh Verify thật.
- Còn HITL: t1 = N14 (adapter provider thật: cần user chọn provider/credential, và senior review SDK); t10 = N23 và t11 = N24 (cần host Linux/VM để chạy systemd, rootless sandbox, 3 đêm canary). Code của N23/N24 (`deploy/nightshift.service`, `scripts/canary.sh`, runbook, UAT) đã viết sẵn; `canary.sh --check` PASS; phần `--run` chờ VM.
- Sandbox live (AT19) đã PASS trên Docker Desktop khi bật cờ `NIGHTSHIFT_SANDBOX_LIVE=1 NIGHTSHIFT_SANDBOX_ROOTLESS=0`; rootless thật vẫn phải chứng minh trên VM (G2).

## 2026-09-24 — propose — 240926-intent-manifest-ui-nightshift
- SPEC + trang companion `llmwiki/html/240926-intent-manifest-ui-seq.html` (8 sơ đồ archify, R7 PASS, cổng tĩnh + cổng chạy thật PASS). Quyết định user: mở từ điện thoại; UI tự chạy start sau màn tóm tắt hiệu ứng. Chờ duyệt → /plan.

- 2026-09-24 cập nhật SPEC 240926-intent-manifest-ui-nightshift: thêm giao thức intake/1 + binding MCP/CLI/file (T6–T8), luồng chính từ agent terminal, agent soạn–người duyệt qua link; 11 task, R7 + hai cổng HTML PASS.

- 2026-09-24 SPEC 240926-intent-manifest-ui-nightshift bản 3: luồng một phiên + closebox giấy phép + đêm tự quyết có decisions log + báo cáo tiếng người (phản hồi "bắt con người làm quá nhiều"); 12 task, R7 + hai cổng HTML PASS. Hướng dẫn/test nhánh intake-guide còn theo bản 2, viết lại sau khi duyệt.

- 2026-09-24 plan — 240926-intent-manifest-ui-nightshift-PLAN: 12 task, 3 mốc; SPEC bản 3 đã duyệt; hướng dẫn + test bản 3 commit 62c5a36 (nightshift, nhánh intake-guide).
- 2026-09-24 thi hành PLAN 240926-intent-manifest-ui-nightshift: 12/12 task commit trên nightshift nhánh intake-guide (40d8fb2..fca0922), test chế độ bắt buộc xanh, báo cáo thật qua hai cổng HTML; 3 chỗ khác kế hoạch ghi trong PLAN.

## 2026-09-28 — propose — 280926-overstack-strands-wrapper

- SPEC chờ duyệt: Strands harness thành vendor thứ 7 (repo private Rheinmir/overstack-strands, policy ghim từ setup) + hệ đánh giá bọc ngoài E0–E3 trên OpenRouter (model Trung Quốc). 5 task, 5 sơ đồ archify, 4 unknown U-01..U-04. Task T-260928-01.

## 2026-09-28 — plan — 280926-overstack-strands-wrapper-PLAN

- SPEC bản 2 (5 chỗ sửa do /plan phát hiện: skill-ab-eval.py chưa commit, snippet hook bị gitignore, exit 2 → Guide, E3 đọc lịch sử hội thoại, model mới hơn) được duyệt lại. PLAN 7 task nhúng nguyên văn prototype đã chạy trên bản PyPI đã pin: 22 test xanh, E0 11/11. U-01 đã trả; U-02..U-04 còn mở.

## 2026-09-29 — plan — 290926-uiux-semantic-search-PLAN

- PLAN 6 task semantic search cho uiux-asset (Upstash Search free); graph orca-graph dựng + 6/6 node verify thật → done. Đo: tìm theo nhóm 12/12, tìm gộp 8–9/12. Code ở repo Rheinmir/uiux-asset commit 6f07191.

## 2026-09-29 — fix — 290926-uiux-followups-PLAN

- html-visual-gate: eye-rest bỏ qua nội dung `<details>` đang đóng (Chromium vẫn trả getClientRects) — fixture eye-rest-details đỏ 800px → xanh; test cổng 66/66. CI harness đỏ html-slop: tái hiện trong container Linux 26/26 xanh, upstream đã sửa ở 77f7810. uiux-asset: `npm run deploy` tự nạp chỉ mục khi đổi + xoá mục đã gỡ.

## 2026-10-01 — issues — /goal "kéo toàn bộ issue về và xử lý"

- GitHub còn 1 issue mở (#191). Ledger `ISSUES.md` lệch: 33 dòng GitHub đã đóng vẫn ghi open/in-progress → đồng bộ (COMPLETED→done, NOT_PLANNED→wontfix, cả frontmatter draft); 38 link chết do draft đã dời vào archive/ → sửa; thêm `wiki-health.py --fail-on ledger` + bước CI để link chết không tái phát.
- GH#191: skill `surface-coverage` (SWH) + `fdk/tools/surface-coverage.py` (scan bề mặt từ code @commit, check sổ phủ + file:line) + `harness/tests/test_surface_coverage.py`; cắm Phase 2 `orca-onboard` (RULE-12, báo `N/M mục`) và `teach-me` (RULE-10).
- 030726-multi-session-add-guard (ledger-only): luật pathspec tường minh trong /fdk + CLAUDE/AGENT; rule dự án P1 `no-bulk-stage` (harness-local) + test 2 phiên + firedrill → done.
- 150726-legacy-html-slop-debt (ledger-only, draft mất 2 lần): đếm lại bằng frontend-antipattern 0/18 file → tạo lại draft, done.
- Kèm draft chờ duyệt `011026-theme-toggle-neumorphism` (chuẩn nút sáng/tối mới) để không mất như draft chưa commit trước đây.

<!-- log:auto:start -->

### 🤖 Log tự-động (code-logger, không do agent ghi)

| Thời điểm | Event | Chi tiết |
|---|---|---|
| 2026-09-28 23:42:35 | `commit.reconcile` |  · actor=system · agent_n=0 · human_n=2 · human=['llmwiki/graph/280926-issues-sweep.graph.json', 'llmwiki/wiki/sources/d |
| 2026-09-28 23:42:41 | `commit.reconcile` |  · actor=system · agent_n=0 · human_n=2 · human=['llmwiki/graph/280926-issues-sweep.graph.json', 'llmwiki/wiki/sources/d |
| 2026-09-28 23:42:58 | `commit.reconcile` |  · actor=system · agent_n=0 · human_n=2 · human=['llmwiki/graph/280926-issues-sweep.graph.json', 'llmwiki/wiki/index.md' |
| 2026-09-28 23:42:58 | `commit.reconcile` |  · actor=system · agent_n=0 · human_n=1 · human=['llmwiki/wiki/sources/draft/280926-issues-sweep-PLAN.md'] · prev=4cc879 |
| 2026-09-28 23:43:08 | `commit.reconcile` |  · actor=system · agent_n=0 · human_n=1 · human=['llmwiki/wiki/sources/draft/280926-issues-sweep-PLAN.md'] · prev=b245ac |
| 2026-09-28 23:43:47 | `commit.reconcile` |  · actor=system · agent_n=0 · human_n=3 · human=['fdk/skill-catalog/recipes/ui-snapshot.recipe.json', 'skills/ui-snapsho |
| 2026-09-28 23:43:47 | `commit.reconcile` |  · actor=system · agent_n=0 · human_n=3 · human=['llmwiki/AGENT.md', 'fdk/tools/build-overstack-docs.py', 'llmwiki/skill |
| 2026-09-28 23:43:47 | `commit.reconcile` |  · actor=system · agent_n=0 · human_n=4 · human=['fdk/CAPABILITIES.md', 'llmwiki/CLAUDE.md', 'fdk/skills.provenance.json |

<!-- log:auto:end -->
