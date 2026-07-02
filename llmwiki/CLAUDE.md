# Behavioral guidelines — distilled from Karpathy's CLAUDE.md
Giảm lỗi LLM-coding phổ biến. Thiên về cẩn trọng hơn tốc độ; task tầm thường thì dùng phán đoán.

1. **Think before coding.** Đừng đoán, đừng giấu chỗ mơ hồ. Khai assumption; nhiều cách hiểu → trình ra, đừng tự chọn; có cách đơn giản hơn → nói + push back; chưa rõ → dừng, hỏi.
2. **Simplicity first.** Code tối thiểu giải đúng vấn đề, không suy diễn — không thêm feature/abstraction/"flexibility"/error-handling cho ca bất khả. 200 dòng mà 50 đủ → viết lại. "Senior có chê overcomplicated không?" → đơn giản hoá.
3. **Surgical changes.** Chỉ chạm cái buộc phải chạm. Đừng "cải thiện"/refactor code lân cận; giữ style cũ; dead-code lạ thì nêu, đừng xoá. Chỉ dọn orphan do CHÍNH thay đổi của bạn tạo ra. Mỗi dòng đổi phải truy về đúng yêu cầu.
4. **Goal-driven execution.** Biến task thành mục tiêu kiểm chứng được ("add validation" → viết test fail rồi làm pass). Việc nhiều bước → nêu plan ngắn, mỗi bước kèm cách verify. Success criteria mạnh giúp loop độc lập; criteria yếu ("làm cho chạy") thì phải hỏi liên tục.

Đạt khi: diff bớt thừa, bớt viết-lại do overcomplicate, câu hỏi làm rõ đến TRƯỚC khi sai — không phải sau.

(Nguồn: 4 nguyên tắc của Karpathy CLAUDE.md, bản distill của Forrest Chang — `multica-ai/andrej-karpathy-skills`. Bối cảnh framework: rule + skill cụ thể nằm ngay dưới.)
## Rules
- 🧰 **Đồ nghề bạn CÓ — đừng làm lại thứ đã tồn tại:** bản đồ năng lực sinh-bằng-code, luôn-mới (ADR-005): repo framework → `fdk/CAPABILITIES.md` (skill+rule+tool); dự án downstream → `CAPABILITIES.md` ở gốc (build-capabilities deploy cạnh hooks, đọc global skills + rule đã cài). Không chắc có gì cho việc đang làm → ĐỌC nó, hoặc `find-skills "<việc>"`. Sinh lại: `python3 fdk/tools/build-capabilities.py` (downstream tự nhận bối cảnh khi chạy với `--root`).
- **Đang phát triển CHÍNH framework này (skill/rule/validator/script/hook/wiki)? Gọi `/fdk`** — on-demand front-door: pre-flight + không miss rule + không dẫm module cũ. KHÔNG auto-bơm đầu phiên vì phần lớn phiên là dùng framework để dev DỰ ÁN KHÁC (xem `ADR-004`).
- **Design rule (feedback 2026-06-27):** thứ gì auto-fire/tự-bơm context vào MỌI phiên (hook SessionStart/UserPromptSubmit, dòng auto-load) chỉ được phục vụ *dự án hiện tại*; context *nội-bộ-framework* (FDK, inventory, runbook sửa rule) phải **opt-in** qua skill gọi chủ động. Luật này nằm ở đây (theo repo) vì memory cá nhân là máy-local, kéo repo máy khác sẽ mất. Xem `ADR-004`.
- FOLLOW the instructions in README.md in wiki folder
- EVERY wiki file must have an `## Origin` section — source is always traceable
- NEVER write to `raw/`
- ALWAYS update `wiki/index.md` when adding or removing a wiki file
- ALWAYS append to `wiki/log.md` after every operation
- Use `[[wikilinks]]` to cross-reference entries in `wiki/`
- Wiki files live in `concepts/`, `entities/`, `sources/`, `draft/`, `architecture/`, or `tours/` — never in `wiki/` root (enforced by R5 validator)
- Wiki entries are only created AFTER code is committed — never during proposal or planning
- Match a file's verbosity to its reader. Markdown that a machine or agent reads and executes (SKILL.md, policy.yaml, AGENT.md, pure reference tables) may be concise. Documentation a human reads or reviews (review reports, ADRs, README, CONTRIBUTING and runbooks, output-reports, HTML pages) must be full, readable prose with complete sentences — never caveman or over-compressed shorthand there; caveman is only for ephemeral agent-to-agent messages. (Feedback 2026-06-27.)

## Skills

| Skill | Invoke when | File | Loop |
|-------|------------|------|------|
| `ingest` | A new file appears in `raw/` | `skills/wiki-loop/ingest.md` | wiki-loop |
| `query` | User asks a question requiring wiki synthesis | `skills/wiki-loop/query.md` | wiki-loop |
| `lint` | After every 10 ingests, or wiki feels stale | `skills/wiki-loop/lint.md` | wiki-loop |
| `propose` | Any new feature or change is requested | `skills/dev-loop/propose.md` | dev-loop |
| `impact-check` | Before modifying any shared symbol | `skills/dev-loop/impact-check.md` | dev-loop |
| `safe-change` | Editing code called from more than one place | `skills/dev-loop/safe-change.md` | dev-loop |
| `verify-before-commit` | Before every commit | `skills/dev-loop/verify-before-commit.md` | dev-loop |
| `orca-workflow` | Daily propose → gate → dispatch with Orca | `skills/orchestrate/orca-workflow.md` | orchestrate |
| `orca-onboard` | Parallel codebase onboarding with Orca | `skills/orchestrate/orca-onboard.md` | orchestrate |
| `onboard-codebase` | Deep analysis of legacy code to populate Wiki | `skills/dev-loop/onboard-codebase.md` | dev-loop |
| `sync-template` | Upstreaming template improvements to master repo | `skills/utils/sync-template.md` | utils |
| `md-to-html` | User wants to render a professional HTML report | `skills/utils/md-to-html.md` | utils |
| `docs-site-macos` | User wants macOS-style documentation site | `skills/utils/docs-site-macos.md` | utils |
| `web-crawl` | Crawl/scrape a URL or site into LLM-ready markdown | `skills/utils/web-crawl.md` | utils |
| `web-clone` | Clone a page's exact UI as one self-contained offline HTML | `skills/utils/web-clone.md` | utils |
| `fdk` | Đang phát triển CHÍNH framework (skill/rule/validator/hook/wiki) | `skills/utils/fdk.md` | utils |
| `new-skill` | Scaffold một skill mới (canonical+mirror+lệnh register) | `skills/dev-loop/new-skill.md` | dev-loop |
| `loop-runner` | Vòng lặp agent có guardrail (propose→verify→revise, termination) | `skills/dev-loop/loop-runner.md` | dev-loop |
| `failure-flywheel` | Gom lỗi lặp → đề xuất rule/skill mới (error-analysis) | `skills/dev-loop/failure-flywheel.md` | dev-loop |
| `council` | Hội đồng nhiều model đánh giá → câu trả lời tốt nhất (Karpathy) | `skills/orchestrate/council.md` | orchestrate |
| `trace-grader` | Chấm ĐƯỜNG ĐI của agent (tool/thứ tự/pass^k), không chỉ kết quả | `skills/orchestrate/trace-grader.md` | orchestrate |
| `wikieval` | Bộ eval hồi quy từ wiki goldens (cascade assert + baseline, CI gate) | `skills/dev-loop/wikieval.md` | dev-loop |
| `docs-curate` | Sắp xếp gọn kho docs local (html/draft phình to): promote bản chất→wiki, archive render, re-index | `skills/utils/docs-curate.md` | utils |
| `brandkit` | Premium brand-kit image generation skill for creating high-end… | `skills/utils/brandkit.md` | utils |
| `build-now-adapt-later` | When a task is blocked by missing or unverified information (an… | `skills/dev-loop/build-now-adapt-later.md` | dev-loop |
| `cavecrew` | Decision guide for delegating to caveman-style subagents. | `skills/utils/cavecrew.md` | utils |
| `caveman` | Ultra-compressed communication mode. | `skills/utils/caveman.md` | utils |
| `caveman-commit` | Ultra-compressed commit message generator. | `skills/utils/caveman-commit.md` | utils |
| `caveman-compress` | Compress natural language memory files (CLAUDE.md, todos, preferences)… | `skills/utils/caveman-compress.md` | utils |
| `caveman-help` | Quick-reference card for all caveman modes, skills, and commands. | `skills/utils/caveman-help.md` | utils |
| `caveman-review` | Ultra-compressed code review comments. | `skills/utils/caveman-review.md` | utils |
| `caveman-stats` | Show real token usage and estimated savings for the current session. | `skills/utils/caveman-stats.md` | utils |
| `check-approve` | Sinh sẵn 1-liner để trace 1 lệnh approve/return/reject của DMS trên log BE… | `skills/utils/check-approve.md` | utils |
| `computer-use` | Use Orca's computer-use CLI to inspect and operate local desktop app… | `skills/utils/computer-use.md` | utils |
| `cursor-animated-sites` | Build an interactive "cursor-animated walkthrough" page on top of the… | `skills/utils/cursor-animated-sites.md` | utils |
| `design-taste-frontend` | Anti-slop frontend skill for landing pages, portfolios, and redesigns. | `skills/utils/design-taste-frontend.md` | utils |
| `design-taste-frontend-v1` | The original v1 taste-skill, preserved for projects depending on its exact… | `skills/utils/design-taste-frontend-v1.md` | utils |
| `extract-site` | Extract and convert a website or docs site into clean markdown | `skills/utils/extract-site.md` | utils |
| `find-skills` | Helps users discover and install agent skills when they ask questions like… | `skills/utils/find-skills.md` | utils |
| `full-output-enforcement` | Overrides default LLM truncation behavior. | `skills/utils/full-output-enforcement.md` | utils |
| `gpt-taste` | Elite UX/UI & Advanced GSAP Motion Engineer. | `skills/utils/gpt-taste.md` | utils |
| `harness-tour` | Tour — Claude tự diễn cho user xem harness chặn mình theo thời gian thực… | `skills/utils/harness-tour.md` | utils |
| `harness-update` | TỰ BẢO TRÌ framework overstack trên máy user (self-maintain) — migrate… | `skills/utils/harness-update.md` | utils |
| `health-check` | Kiểm tra sức khỏe "pattern chuẩn" của template — pattern đã đủ chưa, có… | `skills/utils/health-check.md` | utils |
| `high-end-visual-design` | Teaches the AI to design like a high-end agency. | `skills/utils/high-end-visual-design.md` | utils |
| `image-to-code` | Elite website image-to-code skill for Codex. | `skills/utils/image-to-code.md` | utils |
| `imagegen-frontend-mobile` | Elite mobile app image-generation skill for creating premium, app-native… | `skills/utils/imagegen-frontend-mobile.md` | utils |
| `imagegen-frontend-web` | Elite frontend image-direction skill for generating premium,… | `skills/utils/imagegen-frontend-web.md` | utils |
| `industrial-brutalist-ui` | Raw mechanical interfaces fusing Swiss typographic print with military… | `skills/utils/industrial-brutalist-ui.md` | utils |
| `jenkins-agent-l3-deploy` | Deploy a docker-compose app via a Jenkins INBOUND AGENT running on the… | `skills/orchestrate/jenkins-agent-l3-deploy.md` | orchestrate |
| `join-project` | Orient nhanh vào dự án đang chạy đã có llmwiki — read-only, không ghi wiki | `skills/utils/join-project.md` | utils |
| `last30days` | Research what people actually say about any topic in the last 30 days. | `skills/utils/last30days.md` | utils |
| `minimalist-ui` | Clean editorial-style interfaces. | `skills/utils/minimalist-ui.md` | utils |
| `new-project-setup` | Deploy llmwiki từ đầu vào project mới — template pull, skill install, RTK,… | `skills/dev-loop/new-project-setup.md` | dev-loop |
| `orca-cli` | Use the public `orca` CLI to operate Orca-managed worktrees/workspaces,… | `skills/orchestrate/orca-cli.md` | orchestrate |
| `orca-dispatch-reference` | Reference for Antigravity/OpenCode dispatch, skill installation,… | `skills/orchestrate/orca-dispatch-reference.md` | orchestrate |
| `orca-eval` | Quét N session Claude Code gần nhất, distill best practices thành report… | `skills/orchestrate/orca-eval.md` | orchestrate |
| `orca-sec-scans` | Quét bảo mật mã nguồn bằng Trivy — tự check/cài Trivy nếu chưa có, quét… | `skills/orchestrate/orca-sec-scans.md` | orchestrate |
| `orchestration` | Use Orca orchestration for structured multi-agent coordination: threaded… | `skills/orchestrate/orchestration.md` | orchestrate |
| `redesign-existing-projects` | Upgrades existing websites and apps to premium quality. | `skills/utils/redesign-existing-projects.md` | utils |
| `snapshot-push` | Push bonbon-ai outer repo as full snapshot, including be/ and fe/ content | `skills/utils/snapshot-push.md` | utils |
| `stitch-design-taste` | Semantic Design System Skill for Google Stitch. | `skills/utils/stitch-design-taste.md` | utils |
| `tour-guide` | Thêm một in-app product tour (spotlight onboarding overlay) tự viết, KHÔNG… | `skills/utils/tour-guide.md` | utils |
| `tour-guide-supademo` | Style thiết kế Supademo cho in-app product tour (dùng kèm skill tour-guide… | `skills/utils/tour-guide-supademo.md` | utils |
| `uat-nonit-testcase` | Tạo bộ test case / checklist UAT cho người dùng nghiệp vụ NON-IT (C&B, kế… | `skills/utils/uat-nonit-testcase.md` | utils |

## Invocation rules
- New file in `raw/` → invoke `ingest` immediately
- New feature request → invoke `propose` first, stop, wait for approval
- Edit to shared code → invoke `impact-check` then `safe-change`
