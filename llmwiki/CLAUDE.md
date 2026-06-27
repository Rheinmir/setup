# Behavioral guidelines — distilled from Karpathy's CLAUDE.md
Giảm lỗi LLM-coding phổ biến. Thiên về cẩn trọng hơn tốc độ; task tầm thường thì dùng phán đoán.

1. **Think before coding.** Đừng đoán, đừng giấu chỗ mơ hồ. Khai assumption; nhiều cách hiểu → trình ra, đừng tự chọn; có cách đơn giản hơn → nói + push back; chưa rõ → dừng, hỏi.
2. **Simplicity first.** Code tối thiểu giải đúng vấn đề, không suy diễn — không thêm feature/abstraction/"flexibility"/error-handling cho ca bất khả. 200 dòng mà 50 đủ → viết lại. "Senior có chê overcomplicated không?" → đơn giản hoá.
3. **Surgical changes.** Chỉ chạm cái buộc phải chạm. Đừng "cải thiện"/refactor code lân cận; giữ style cũ; dead-code lạ thì nêu, đừng xoá. Chỉ dọn orphan do CHÍNH thay đổi của bạn tạo ra. Mỗi dòng đổi phải truy về đúng yêu cầu.
4. **Goal-driven execution.** Biến task thành mục tiêu kiểm chứng được ("add validation" → viết test fail rồi làm pass). Việc nhiều bước → nêu plan ngắn, mỗi bước kèm cách verify. Success criteria mạnh giúp loop độc lập; criteria yếu ("làm cho chạy") thì phải hỏi liên tục.

Đạt khi: diff bớt thừa, bớt viết-lại do overcomplicate, câu hỏi làm rõ đến TRƯỚC khi sai — không phải sau.

(Nguồn: 4 nguyên tắc của Karpathy CLAUDE.md, bản distill của Forrest Chang — `multica-ai/andrej-karpathy-skills`. Bối cảnh framework: rule + skill cụ thể nằm ngay dưới.)
## Rules
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
| `docs-site-macos` | User wants macOS-style documentation site | `skills/utils/docs-site-macos-skill.md` | utils |
| `fdk` | Đang phát triển CHÍNH framework (skill/rule/validator/hook/wiki) | `skills/utils/fdk.md` | utils |

## Invocation rules
- New file in `raw/` → invoke `ingest` immediately
- New feature request → invoke `propose` first, stop, wait for approval
- Edit to shared code → invoke `impact-check` then `safe-change`