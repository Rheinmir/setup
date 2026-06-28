<!-- SINH BẰNG CODE: build-capabilities.py — ĐỪNG sửa tay; chạy lại để cập nhật. -->
# CAPABILITIES — toàn bộ đồ nghề (luôn-mới, đếm từ đĩa)

**63 skill · 13 rule · 9 fdk-tool · 30 harness-script.** Agent: đây là danh sách ĐẦY ĐỦ những gì bạn có để dùng. Tìm nhanh: `python3 fdk/tools/build-skill-search.py` rồi `find-skill "<việc cần làm>"`. Phát triển framework: gọi `/fdk`.

## Skills (gọi bằng `/<tên>`)

### wiki-loop (3)
- **`/ingest`** — Process new file in llmwiki/raw/ and distill into wiki pages
- **`/lint`** — Periodic wiki health check
- **`/query`** — Synthesize answer from wiki; persist new insights as wiki entries

### dev-loop (12)
- **`/build-now-adapt-later`** — When a task is blocked by missing or unverified information (an undocumented protocol, an …
- **`/failure-flywheel`** — Capture each agent failure, bucket and count it deterministically, and when a failure clas…
- **`/impact-check`** — Map all callers and dependents of a symbol before modifying shared code
- **`/loop-runner`** — Deterministic guardrailed agent-loop driver
- **`/new-project-setup`** — Deploy llmwiki từ đầu vào project mới
- **`/new-skill`** — Scaffold a new skill into both publish trees at once
- **`/onboard-codebase`** — Deep codebase analysis
- **`/propose`** — Plan a feature before coding
- **`/safe-change`** — Modify shared code without breaking existing callers
- **`/tour-guide`** — Thêm một in-app product tour (spotlight onboarding overlay) tự viết, KHÔNG cần thư viện (k…
- **`/verify-before-commit`** — Gate every commit
- **`/wikieval`** — Turn wiki golden pages into a CI-blocking eval suite with a cheap→expensive assertion casc…

### orchestrate (10)
- **`/council`** — Run a Karpathy-style LLM council (3-stage multi-agent evaluation) on top of the existing o…
- **`/jenkins-agent-l3-deploy`** — Deploy a docker-compose app via a Jenkins INBOUND AGENT running on the target server (no S…
- **`/orca-cli`** — Use the public `orca` CLI to operate Orca-managed worktrees/workspaces, terminals, repos, …
- **`/orca-dispatch-reference`** — Reference for Antigravity/OpenCode dispatch, skill installation, AgentMemory, RTK token pr…
- **`/orca-eval`** — Quét N session Claude Code gần nhất, distill best practices thành report md + đề xuất acti…
- **`/orca-onboard`** — Parallel codebase onboarding
- **`/orca-sec-scans`** — Quét bảo mật mã nguồn bằng Trivy
- **`/orca-workflow`** — Daily propose → gate → dispatch workflow with Orca
- **`/orchestration`** — Use Orca orchestration for structured multi-agent coordination: threaded messages, blockin…
- **`/trace-grader`** — Score the PATH an agent took (tool choice, ordering, retries, repeatability)

### utils (38)
- **`/brandkit`** — Premium brand-kit image generation skill for creating high-end brand-guidelines boards, lo…
- **`/cavecrew`** — Decision guide for delegating to caveman-style subagents
- **`/caveman`** — Ultra-compressed communication mode
- **`/caveman-commit`** — Ultra-compressed commit message generator
- **`/caveman-compress`** — Compress natural language memory files (CLAUDE.md, todos, preferences) into caveman format…
- **`/caveman-help`** — Quick-reference card for all caveman modes, skills, and commands
- **`/caveman-review`** — Ultra-compressed code review comments
- **`/caveman-stats`** — Show real token usage and estimated savings for the current session
- **`/check-approve`** — Sinh sẵn 1-liner để trace 1 lệnh approve/return/reject của DMS trên log BE (docker) + FE p…
- **`/computer-use`** — Use Orca's computer-use CLI to inspect and operate local desktop app windows through acces…
- **`/cursor-animated-sites`** — Build an interactive "cursor-animated walkthrough" page on top of the /docs-site-macos gla…
- **`/design-taste-frontend`** — Anti-slop frontend skill for landing pages, portfolios, and redesigns
- **`/design-taste-frontend-v1`** — The original v1 taste-skill, preserved for projects depending on its exact behavior
- **`/docs-curate`** — Sắp xếp gọn kho tài liệu LOCAL (llmwiki/html/ + wiki/sources/draft/) khi phình to
- **`/docs-site-macos`** — Build a beautiful macOS-inspired documentation site (single HTML file) with a liquid-glass…
- **`/extract-site`** — Extract and convert a website or docs site into clean markdown
- **`/fdk`** — Front-door on-demand cho phát triển framework HOẶC distill/author một skill
- **`/find-skills`** — Helps users discover and install agent skills when they ask questions like "how do I do X"…
- **`/full-output-enforcement`** — Overrides default LLM truncation behavior
- **`/gpt-taste`** — Elite UX/UI & Advanced GSAP Motion Engineer
- **`/harness-tour`** — Tour
- **`/harness-update`** — TỰ BẢO TRÌ framework overstack trên máy user (self-maintain)
- **`/health-check`** — Kiểm tra sức khỏe "pattern chuẩn" của template
- **`/high-end-visual-design`** — Teaches the AI to design like a high-end agency
- **`/image-to-code`** — Elite website image-to-code skill for Codex
- **`/imagegen-frontend-mobile`** — Elite mobile app image-generation skill for creating premium, app-native screen concepts a…
- **`/imagegen-frontend-web`** — Elite frontend image-direction skill for generating premium, conversion-aware website desi…
- **`/industrial-brutalist-ui`** — Raw mechanical interfaces fusing Swiss typographic print with military terminal aesthetics
- **`/join-project`** — Orient nhanh vào dự án đang chạy đã có llmwiki
- **`/last30days`** — Research what people actually say about any topic in the last 30 days
- **`/md-to-html`** — Render Markdown thành standalone HTML
- **`/minimalist-ui`** — Clean editorial-style interfaces
- **`/redesign-existing-projects`** — Upgrades existing websites and apps to premium quality
- **`/snapshot-push`** — Push bonbon-ai outer repo as full snapshot, including be/ and fe/ content
- **`/stitch-design-taste`** — Semantic Design System Skill for Google Stitch
- **`/sync-template`** — Sync structural improvements between project and master template repo
- **`/tour-guide-supademo`** — Style thiết kế Supademo cho in-app product tour (dùng kèm skill tour-guide
- **`/uat-nonit-testcase`** — Tạo bộ test case / checklist UAT cho người dùng nghiệp vụ NON-IT (C&B, kế toán, vận hành)

## Harness rules (gác tự động — vi phạm bị chặn)
- **R1** — no-write-raw
- **R2** — origin-required
- **R3** — index-sync
- **R4** — audit-log
- **R5** — folder-structure
- **R6** — verify-before-commit
- **R7** — proposal-complete
- **R8** — session-health
- **R9** — okf-frontmatter
- **R10** — docs-gate
- **R11** — seq-html-glass-style
- **R12** — pull-before-change
- **R13** — decision-to-adr

## FDK tools (`python3 fdk/tools/<x>`)
- `artifacts.py`
- `build-capabilities.py`
- `build-cheatsheet.py`
- `build-docs-index.py`
- `build-health-dashboard.py`
- `build-overstack-docs.py`
- `build-skill-search.py`
- `docs-curate.py`
- `new-skill.py`

## Harness scripts (`python3 harness/scripts/<x>`)
- `adapt-registry.py`
- `arch-scan.py`
- `audit.py`
- `claim-receipts.py`
- `code-logger.py`
- `council.py`
- `dispatch-verify.py`
- `egress-guard.py`
- `failure-flywheel.py`
- `fdk-gate.py`
- `harness-doctor.py`
- `harness-lint.py`
- `health-check.py`
- `inject-scan.py`
- `loop-runner.py`
- `mem-rank.py`
- `okf-check.py`
- `prospect-critic.py`
- `scoped-hooks.py`
- `skill-registry.py`
- `spec-gate.py`
- `success-flywheel.py`
- `sync-skills.py`
- `sync-template.py`
- `token-budget.py`
- `trace-grader.py`
- `trace-otel.py`
- `wiki-graph.py`
- `wiki-health.py`
- `wikieval.py`

## Origin
- Sinh bằng `fdk/tools/build-capabilities.py` từ đĩa (skills/, policy.yaml, fdk/tools/, harness/scripts/, sync-skills LOOP_MAP). KHÔNG hardcode.
