---
type: draft
title: Refactor llmwiki sang chuẩn Open Knowledge Format (OKF) v0.1
status: proposed
tags: [okf, refactor, harness, frontmatter, knowledge-format]
timestamp: 2026-06-19
---

# 190626-okf-refactor-llmwiki

**Status:** proposed

## What
Refactor toàn bộ knowledge base `llmwiki/wiki/` để tuân thủ **Open Knowledge Format (OKF) v0.1** (Google Cloud, 12/06/2026): mỗi concept là một file Markdown có **YAML frontmatter parse được**, bắt buộc đúng một trường `type` không rỗng; nhờ đó bất kỳ AI agent nào cũng đọc trực tiếp được bộ wiki mà không cần chuyển đổi.

## Tại sao
- Wiki hiện dùng pseudo-frontmatter dạng bold trong body — `**Type:** concept` / `**Tags:** …` — **không phải** YAML frontmatter, nên không qua được tiêu chí hợp lệ OKF.
- OKF biến mẫu hình "LLM wiki" thành chuẩn khả chuyển: viết một lần, mọi agent (Claude/opencode/antigravity/Gemini ADK) dùng được. Đúng định hướng đa-engine của skill `orca-workflow`.
- Harness vừa cài (branch `orca`) **chưa có** validator frontmatter — đây là lúc đóng đinh OKF thành hàng rào trước khi wiki phình to.

## Spec đích (OKF v0.1)
- **Bắt buộc:** một trường `type` (chuỗi ngắn — vd `concept`, `entity`, `Playbook`, `API Endpoint`).
- **Tùy chọn (nên có):** `title`, `description`, `resource` (URI ổn định), `tags`, `timestamp`.
- **Tương thích về sau:** bên đọc PHẢI bỏ qua được khóa lạ → validator không được fail vì khóa ngoài spec.
- **Tiêu chí hợp lệ:** (1) mọi file .md không-dành-riêng có frontmatter parse được; (2) mọi frontmatter có `type` không rỗng; (3) file dành riêng theo cấu trúc spec.

## Affected
| File / Symbol | How it changes |
|---------------|----------------|
| `llmwiki/wiki/concepts/*.md`, `entities/*.md`, `sources/**/*.md` (trừ reserved) | Thêm YAML frontmatter; bỏ dòng bold `**Type:**/**Tags:**/**Status:**` |
| `llmwiki/wiki/sources/draft/150626-okf-docs-site.md` | Chuyển sang frontmatter (file nội dung đầu tiên migrate) |
| `llmwiki/wiki/{concepts,entities,sources,sources/draft}/_template.md` | Header bold → khối YAML frontmatter mẫu |
| `llmwiki/skills/wiki-loop/ingest.md`, `dev-loop/propose.md`, `wiki-loop/query.md` | Hướng dẫn output frontmatter thay vì bold |
| `harness/validators/okf_frontmatter.py` (mới) | R9: kiểm frontmatter parse được + `type` không rỗng |
| `harness/policy.yaml`, `.pre-commit-config.yaml`, `llmwiki/.claude/hooks/post_tool_use.py` | Wire R9 vào post-tool + pre-commit (R8 đã dùng cho pattern-sync) |
| `harness/version.json` | Upstream-only bump (pattern mới R9) khi đẩy lên repo `setup` |

## Reserved files (miễn frontmatter — theo R5 `ALLOWED_ROOT_FILES`)
`index.md`, `log.md`, `README.md`, `decisions.md`, `active-context.md`, `_template.md` — là file cấu trúc/chỉ mục, không phải concept; khai báo là "reserved filename" đúng quy tắc (3) của OKF.

## Risks
- **R2 origin-required**: OKF giữ body Markdown tự do → section `## Origin` ở body vẫn còn → R2 không gãy. Phải GIỮ nguyên `## Origin` khi migrate.
- **R3 index-sync**: refactor không đổi tập file → index.md vẫn khớp. Không thêm/xóa file trong bước migrate.
- **Khóa lạ**: validator R9 phải tolerate khóa ngoài spec (vd `status`) — nếu fail sẽ vi phạm tinh thần OKF.
- **YAML hỏng**: tab/ký tự đặc biệt trong title tiếng Việt → bọc string khi cần; chạy file-by-file + diff.

## Plan
- [ ] **T1** — Convert mọi file nội dung (concepts/entities/sources, trừ reserved) từ bold `**Type:**` sang YAML frontmatter (`type` bắt buộc + title/tags/timestamp), giữ nguyên H1, body và `## Origin`.
- [ ] **T2** — Update 4 `_template.md` để sinh frontmatter YAML → file mới born-OKF.
- [ ] **T3** — Update skill `ingest`/`propose`/`query` để output frontmatter thay vì bold, giữ ràng buộc Origin + index + log.
- [ ] **T4** — Thêm validator harness **R9 `okf_frontmatter.py`** (parse + `type` không rỗng, tolerate khóa lạ, bỏ reserved); wire vào policy/hooks/pre-commit; bump `version.json`.
- [ ] **T5** — Chốt reserved-filename map + tạo concept `okf-conformance` mô tả ánh xạ llmwiki↔OKF, chạy 3 tiêu chí hợp lệ OKF v0.1 trên cây wiki.

**Sequence diagram**: [190626-okf-refactor-seq.html](../../../html/190626-okf-refactor-seq.html)

## Agent Task Assignment
| Task | Agent | Engine | Lý do |
|------|-------|--------|-------|
| T1 convert files | opencode | deepseek | sửa hàng loạt cơ học, rẻ token |
| T2 templates | opencode | deepseek | thay header theo mẫu cố định |
| T3 skills | claude | opus | cần hiểu ngữ nghĩa skill, không phá loop |
| T4 validator R9 | claude | opus | logic validator + wire hooks, đụng harness |
| T5 conformance | claude | opus | phán định reserved + viết tài liệu chuẩn |

> Theo skill `orca-workflow`: Claude phân tích/đụng harness, opencode lo phần cơ học. Kill opencode khỏi pool nếu idle quá lâu.

## Success criteria
- Chạy tiêu chí OKF v0.1 trên cây wiki → **3/3 pass** (frontmatter parse được · `type` không rỗng · reserved đúng cấu trúc).
- `harness/validators/okf_frontmatter.py` tồn tại; thử ghi file wiki thiếu `type` → **BỊ CHẶN ✓** (như R1/R2/R5).
- Validator KHÔNG fail khi frontmatter có khóa lạ (vd `status`).
- `pre-commit run --all-files` xanh; R2/R3 vẫn pass sau migrate.
- File mới tạo từ `_template.md` đã có frontmatter hợp lệ ngay.

## Notes
- Nguồn chuẩn: [[150626-okf-docs-site]] (research OKF v0.1) + `llmwiki/html/150626-open-knowledge-format-vi.html`.
- OKF stack cùng llms.txt (signpost) + MCP (tool sống) — không cạnh tranh; refactor này chỉ chuẩn hóa lớp lưu trữ tri thức.

## Origin
- **Draft:** `wiki/sources/draft/190626-okf-refactor-llmwiki.md`
- **Source:** `/sync-template` → `/harness-update` (migrate harness) + `/orca-workflow` chạy ra kế hoạch theo OKF spec
- **Commit:** _(filled by `verify-before-commit`)_
- **Date promoted:** _(filled by `verify-before-commit`)_
