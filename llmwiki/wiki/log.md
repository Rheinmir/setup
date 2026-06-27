# Operation Log

## 2026-04-28 — init — Knowledge Base initialized
- Created folder structure: concepts/, entities/, sources/, sources/draft/
- Created wiki/index.md, wiki/log.md
- Created AGENT.md

## 2026-06-15 — health-check — pattern-sync version + skill + SessionStart hook
- Thêm harness/scripts/health-check.py + harness/version.json (fingerprint 49 pattern)
- Thêm skill /health-check + hook session_start.py (báo cáo không chặn)
- Wire R8 policy, install-harness.sh, sync-template Step 0/6b; +health-check.md vào manifest
- Draft: wiki/sources/draft/150626-health-check-pattern-sync.md

## 2026-06-22 — orca-workflow — design-pattern-html-refactor
- Refactor 3 HTML infographics: v1 (4→5 sections), v2 (4→7 sections), v3 (4→10 sections)
- v1 thêm: Rate Limiting section, CDN card, prose WHY/WHEN cho 5 building blocks, 6-row tradeoff table
- v2 thêm: Rate Limiting, Consensus Algorithms (Raft/Paxos/PBFT), Monitoring & Observability (Three Pillars, SLI/SLO/SLA)
- v3 thêm: Communication Patterns (Saga/Event Sourcing), Service Discovery, Retry+Jitter, Stateless Design, EDA, CQRS
- agy terminals blocked (codex-trust-workspace) → Claude main thực hiện trực tiếp
- Proposal: wiki/draft/orca/220626-design-pattern-html-refactor.md

## 2026-06-21 — orca-workflow + docs-site-macos — design-pattern-infographic
- Fetch 3 YouTube video metadata (Code Lủng · Học Từ Thiền Series: Phần 000/001/002)
- YouTube SPA → transcript không extract được; dùng fallback: metadata + System Design knowledge
- Created 3 MD: wiki/sources/draft/design-pattern-v{1,2,3}.md
- Created 3 HTML infographics: llmwiki/html/design-pattern-v{1,2,3}.html (docs-site-macos light glass)
- Created proposal: wiki/draft/orca/210626-design-pattern-infographic.md
- Created seq diagram: llmwiki/html/210626-design-pattern-infographic-seq.html

## 2026-06-18 — docs-site-macos — orca-framework-overview
- Created llmwiki/html/180626-orca-framework-overview.html (single-file overview, skill grid by color)
- Created draft wiki/sources/draft/180626-orca-framework-overview.md

## 2026-06-22 — install-harness — mode=migrate
- Cài harness L0–L4 (validators, hooks, pre-commit, wiki-health, health-check, evals)
- Backfill nợ: YAML frontmatter R9 (9 legacy files), ## Origin (design-pattern.md), index sync (5 rows)
- Fix pre-commit Windows: python3 bash-wrapper → python (real MZ exe); fix arch-scan UnicodeEncodeError

## 2026-06-22 — docs-site-macos — chown
- Created llmwiki/html/220626-chown.html (single-file docs về lệnh chown)
- Created draft wiki/sources/draft/220626-chown.md
- 2026-06-23 00:17 — session `07d80623` — 8 tool calls — files: 230626-docs-gate-register-seq.html, 230626-docs-gate-register.md, index.md, install-harness.sh, settings.json

## 2026-06-23 — docs-site-macos — harness-docs-gate-orca-guard
- 2026-06-23 01:07 — session `07d80623` — 22 tool calls — files: 230626-docs-gate-register-seq.html, 230626-docs-gate-register.md, 230626-harness-docs-gate-orca-guard-report.md, 230626-harness-docs-gate-orca-guard.html, 230626-orca-guard-hook-seq.html, 230626-orca-guard-hook.md, index.md, install-harness.sh …

## 2026-06-23 — orca-workflow: /harness-update < 30s
- Proposal 230626-harness-update-sub30s (gate duyệt) → impl T1-T4.
- T1 install-harness.sh `--self-heal`: tự backfill Origin+index+OKF in-process, re-audit 1 lần (gộp vòng lặp 3-reinstall agent → 1 lệnh).
- T2 harness/scripts/audit.py: gộp 3 audit về 1 process; Origin backfill 1 lượt git log.
- T3 `--no-clone` fast-fail (0.02s, không treo mạng) + skip pre-commit install nếu đã cài.
- T4 viết lại skill 1-phát-gọi + bench harness/metrics/harness-update-bench.json.
- Bench: migrate-có-nợ 0.56s, re-run sạch 0.31s, smoke ⛔×3. Dispatch opencode T3 treo → kill, claude-cli tiếp quản.

## 2026-06-23 — orca-workflow: skill tạo docs đạt chuẩn OKF v0.1
- Proposal 230626-docs-skill-okf (gate duyệt) → impl T1-T3.
- T1 orca-onboard: heredoc + example block `**Type:**` bold → YAML frontmatter `type: draft` (hết tạo nợ R9).
- T2 onboard-codebase + new-project-setup: thêm dòng Rule nhắc OKF (copy _template.md).
- T3 harness/tests/docs-skill-okf-test.sh: 10/10 PASS (skill .md áp OKF, skill HTML N/A, wiki repo OKF 7/8 chỉ còn legacy 220626-chown).
- Dispatch opencode T2 no-op (0 output) → claude-cli tiếp quản (lần 2 liên tiếp opencode hỏng).
- 2026-06-23 01:44 — session `31d9431b` — 27 tool calls — files: 230626-docs-skill-okf-seq.html, 230626-docs-skill-okf.md, 230626-harness-update-sub30s-seq.html, 230626-harness-update-sub30s.md, audit.py, docs-skill-okf-test.sh, harness-update-test.sh, harness-update.md …

## 2026-06-23 — orca-workflow: /sync-template < 30s (cờ --full)
- Proposal 230626-sync-template-sub30s (gate gate_70ba7f4b3b1d duyệt) → impl T1-T4.
- Phát hiện: script đã <1s; nút thắt >30s là 5-6 round-trip agent quanh Step 6a/6b/8 + log.md.
- T1-T3 sync-template.py: cờ `--full` gộp OKF backfill (import okf-check in-process) + fingerprint-sau-OKF + self-verify 3 vị trí + append log vào 1 process. Không cờ = hành vi cũ.
- T4: viết lại FAST PATH skill về 1 phát `--full`; bench harness/metrics/sync-template-bench.json — steady 0.27s, pull+install+verify 0.76s (cả hai <30s & <5s); phân loại + exit code giữ nguyên, CONFLICT vẫn exit 3.
- T3 dự kiến opencode → claude làm inline (coupled cùng file T1/T2, opencode dispatch bất ổn).

## 2026-06-23 — orca-workflow: hook fail-open + kênh giao hook (fix client cozyroom)
- Proposal 230626-orca-guard-failopen (gate gate_357120266bc7 duyệt) → impl T1-T3.
- Sự cố: client cozyroom mọi Bash bị chặn vì hook orca_guard.py thiếu file + lệnh hook trần không fail-open.
- T1: guard `if [ -f "<p>" ]; then python3 "<p>"; fi` ở install-harness.sh (GLOBAL cmd + ROOT h) + llmwiki/.claude/settings.json (7 command); re-merge dedup theo basename → nâng cấp lệnh trần cũ, không trùng, giữ user hook.
- T2: thêm 8 llmwiki/.claude/hooks/*.py + settings.json vào manifest (57 pattern); /sync-template --full giao được orca_guard.py.
- T3: installer WARN khi hook thiếu file (không fatal) + golden test harness/tests/orca-guard-failopen-test.sh 6/6 PASS; 3 python block embed compile OK.
- Gỡ ngay client: `git show origin/orca:llmwiki/.claude/hooks/orca_guard.py > llmwiki/.claude/hooks/orca_guard.py`.

## 2026-06-23 — orca-workflow: rà 26 npx skill vs bản cũ → vá 2 regression
- Audit 4 agent song song (old npx cdd3e08~1 vs canonical): 23 OK, 3 flag.
- orca-workflow: khôi phục section "An toàn container/DB" (Cozyroom DB path + bài học 05-29 recreate→mất DB) bị refactor b0f30e0 làm rớt → canonical + npx.
- tour-guide: canonical vốn bonbon-specific (fe/components/dms/...) → thay bằng bản generic self-contained (khớp published description) + có frontmatter (vá luôn gap thiếu frontmatter); npx regenerate.
- onboard-codebase: GIỮ NGUYÊN — canonical cố tình caveman-compress (commit 52827b7), npx mirror đúng harness.
- Kết quả: npx body == canonical cho toàn bộ skill (chuẩn so với harness).
## 2026-06-25 — orca-onboard — onboard-setup
## 2026-06-25 — orca-onboard — onboard-setup complete (4 phases, static-parse route, ~$0.04 actual)
## 2026-06-25 — docs-site-macos — harness-mcp-scenarios
## 2026-06-25 — docs-site-macos — harness-arch-vs-current
## 2026-06-25 — harness — poc-vendor-neutral (13/13 PASS)
## 2026-06-25 — concept — cursor-explain-site (distill cloner-template → extract-site Mode 3)
## 2026-06-25 — orca-eval — eval-report + promote skill cursor-animated-sites
## 2026-06-25 — cursor-animated-sites — cicd-lifecycle (kiểm chứng skill)
## 2026-06-25 — cursor-animated-sites — index gộp harness + CI/CD
## 2026-06-25 — cursor-animated-sites — gộp 3 trang (index+harness+cicd) thành 1 file walkthroughs
## 2026-06-27 — orca-workflow — framework-gap-backfill: proposal + R11 seq-glass-style + R12 pull-before-change (gate1 PreToolUse + gate2 pre-push)
## 2026-06-27 — orca-workflow — R12 rút gọn về (B) orchestrator pre-work sweep + (C) pre-push; BỎ (A) per-edit PreToolUse (cost cao, lệch đa-vendor)
## 2026-06-27 — orca-workflow — propose R12 v3 workspace-aware (pull-gate-sweep + --all-subrepos), gate chờ duyệt
## 2026-06-27 — orca-workflow — R12 v3 DUYỆT + impl T1-T5 (list-subrepos.py, pull-gate-sweep.sh, install --all-subrepos, Step 0 sweep ×2, test 4/4 PASS); Kiro thiếu → Claude inline
## 2026-06-27 — backfill — rule-registry (R1..R12 + flag drift R3/R8) + ADR-001/002 + lấp decisions.md
## 2026-06-27 — T1 reconcile — thêm R3/R4/R8/R10 (hook_event) vào policy.yaml (11 rule); điều tra: R3/R8 KHÔNG drift, gỡ flag; registry cập nhật
## 2026-06-27 — T5 drift-test — policy-converters-drift-test.sh (28/28 + negative bắt drift); wire .pre-commit
## 2026-06-27 — T4 — CONTRIBUTING-harness.md (runbook thêm rule); gap-backfill CLOSED (T1-T5 done)
## 2026-06-27 — policy-drives-wiring — gen-converters SINH hook claude từ hook_event rules (output identical, drift-test 36/0 + negative)
## 2026-06-27 — R11 [repo] — migrate 8 seq html flat → glass (override docs-site-macos); bật enforce_at [session,repo] + pre-commit seq-html-glass
## 2026-06-27 — R6 + two-policy — R6=verify-before-commit (KHÔNG reserved); reconcile harness/policy.yaml↔poc (cả hai R1-R12); drift-test check parity
## 2026-06-27 — fix broken wikilink — stub concepts extract-site + docs-site-macos-skill (wiki-health 0 broken)
## 2026-06-27 — fix — poc R7 thêm exclude_basenames (_template miễn, khớp production); full test sweep 10/10
## 2026-06-27 — review — session-review output report (13 commit, full sweep 10/10) + re-sync ~/.claude skill
## 2026-06-27 — commit — 5 wiki untracked có-sẵn được index trỏ (architecture, cursor-explain-site, onboarding-tour, project-structure, 250626-onboard-setup)
## 2026-06-27 — docs-site-macos — session-review-html (trang glass 6 section, self-contained, :8765)
## 2026-06-27 — feedback — siết luật: tắt caveman khi viết tài liệu (orca-workflow x2 + CLAUDE.md); lưu memory docs-no-caveman
## 2026-06-27 — feedback — tinh chỉnh luật caveman: máy đọc thì gọn được, người đọc thì đầy đủ (orca-workflow x2 + CLAUDE.md)
## 2026-06-27 — docs-site-macos — viết lại 270626-session-review.html bằng văn xuôi đầy đủ (theo feedback caveman), giữ design system glass
## 2026-06-27 — docs-site-macos — tinh gọn session-review.html (cô đọng vừa đủ, không sơ sài) theo feedback

## 2026-06-27 — propose — wiki-sync-structure
Draft proposal `270626-wiki-sync-structure.md` + seq HTML `270626-wiki-sync-structure-seq.html`. Skill tái gọi `/wiki-sync-structure` để phát hiện & sửa drift tài liệu cấu trúc (số liệu 32→56 / 25→44, gap file 03, bảng skill AGENT.md≠CLAUDE.md, dedupe design-pattern + infographic). 4 task, all claude. STOP chờ duyệt.

## 2026-06-27 — propose — propose-single-source
Draft `270626-propose-single-source.md` + seq HTML (glass-style). Refactor DRY: /propose hấp thụ gap glass-style → thành single source of truth; orca-workflow bước 2 đổi sang GỌI /propose (như bước 1 đã gọi query); giữ R12/query/gate/dispatch. 3 task, all claude. STOP chờ duyệt.

## 2026-06-27 — edit(skill) — propose step-7 rich-prose + glass
Sửa thẳng bước 7 của /propose (cả 3 bản: dev-loop canonical + mirror skills/ + global ~/.claude, diff=SAME): companion HTML phải có CẢ (A) animated diagram VÀ (B) prose chi tiết câu hoàn chỉnh cho mỗi task — chỉ-diagram = chưa đạt; + bắt buộc style docs-site-macos glass. Theo rule CLAUDE.md 2026-06-27 (HTML là tài liệu người-đọc). Gộp luôn gap glass-style của proposal #2-T1.

## 2026-06-27 — implement — propose-single-source (proposal #2)
Đã làm T1–T3: (T1) bước 7 /propose nuốt glass-style + prose (B); (T2) orca-workflow bước 2 → GỌI /propose + mô hình Claude-nghĩ/CLI-rẻ-render (OpenCode→agy→kiro, Full tier, watchdog+R7 gate+fallback); (T3) ADR-003 + decisions.md. Bonus: vá drift skill↔validator R7-(d) — /propose spec + 2 seq html đổi .msg opacity≥.82 (bài 130626). 5 file skill (3 propose + 2 orca-workflow) giữ diff=SAME. Chưa commit.

## 2026-06-27 — concept — fdk (Framework Development Kit)
Dựng bộ xương phát triển framework: front-door `concepts/fdk.md` (pre-flight gate + Phần 2 không-miss-rule + Phần 3 không-dẫm-module với lệnh inventory live, không hardcode số). Wire vào AGENT.md + CLAUDE.md (rule đầu), cross-link rule-registry + CONTRIBUTING-harness. index/decisions cập nhật.

## 2026-06-27 — hook — fdk context-pump (SessionStart)
session_start.py thêm fdk_context(): mỗi phiên tự bơm 1 block "framework có gì" (skills/validators/scripts/hooks/rules đếm live) + cửa vào fdk.md. Fail-open, test in đúng + exit 0. fdk.md ghi nhận cửa chủ động.

## 2026-06-27 — docs-site-macos — fdk-docs
Render fdk.md thành trang docs glass đọc được: llmwiki/html/270626-fdk-docs.html (sidebar + 6 section accent + draggable SVG pre-flight + checklist + copy/ripple/scroll-spy, self-contained). Cross-link fdk.md ↔ html.

## 2026-06-27 — fix+skill — fdk opt-in (/fdk) + audit
Sửa lỗi tư duy "mặc định phiên = dev framework": gỡ fdk_context() khỏi session_start.py (giữ pattern-health); tạo skill /fdk (canonical utils + mirror, diff=SAME) gọi chủ động; slim pointer AGENT/CLAUDE → /fdk điều kiện + đăng ký skill table; ADR-004 + audit 5 điểm auto-fire (2 phạm: fdk_context + pointer; 3 không). fdk.md + docs HTML section 4 cập nhật.

## 2026-06-27 — durability — ghim luật opt-in vào repo
Memory cá nhân là máy-local (không theo git) → ghim luật "auto-fire chỉ phục vụ dự án hiện tại; context nội-bộ-framework phải opt-in" vào AGENT.md + CLAUDE.md (## Rules, feedback 2026-06-27) + guard actionable trong fdk.md pre-flight + trang docs. Travel với repo, mọi máy/agent đều thấy.
