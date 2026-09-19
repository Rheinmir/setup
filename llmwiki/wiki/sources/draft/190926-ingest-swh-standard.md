---
type: draft
title: "190926-ingest-swh-standard — báo cáo ingest PRD SWH"
status: proposed
tags: [ingest, output-report]
timestamp: 2026-09-19
---

# 190926-ingest-swh-standard
**Type:** draft
**Status:** proposed
**Tags:** ingest, output-report
**Proposed:** 2026-09-19

## What
Ingest PRD Skill Design Standard (SOLID WHAT/HOW) thành concept chính chủ, dựng PLAN 17 node trên orca-graph để chuẩn hoá 80 skill native và tách 23 skill ngoài, đồng thời làm xong ba node không phụ thuộc quyết định nào: ingest, lint cấu trúc SWH và hook từ khoá goal.

## Output
- Concept `solid-what-how` là nguồn chân lý cho khung WHAT/HOW; trang nguồn tóm tắt PRD theo mục.
- Phân loại dựa trên cây file upstream thật (gh api, 19/09/2026): 23 skill ngoài gồm 13 skill từ Leonxlnx/taste-skill, 7 từ JuliusBrussee/caveman, find-skills từ vercel-labs/skills, last30days và agent-reach. hallmark, fable5 và i-have-adhd có gốc upstream nhưng user chốt là native vì đã sửa nhiều ở local, nên có 80 skill native. Provenance hiện ghi sai 21 skill ngoài là `local-authored`.
- Đã xác minh trong mã nguồn `skills` CLI rằng `npx skills add` quét sâu một cấp dưới `skills/`, nên category `skills/external/` vẫn cài được xuống downstream.
- `fdk/tools/swh-lint.py` cùng 8 test: đo baseline 0/103 skill đạt cấu trúc SWH. Công cụ chỉ chứng minh hình dạng; hành vi luôn ghi `review_required`.
- Hook UserPromptSubmit: prompt có từ khoá `goal` thì inject chỉ thị đưa goal vào orca-graph và in link atlas; 4 test, trong đó một test chạy hook thật. Trong lúc làm đã bắt được lỗi annotation `str | None` làm hook crash trên Python 3.9.

## Files
| File | Action |
|------|--------|
| `llmwiki/wiki/concepts/solid-what-how.md` | created |
| `llmwiki/wiki/sources/190926-skill-design-standard-swh-prd.md` | created |
| `llmwiki/wiki/concepts/skill-craft.md` | modified |
| `llmwiki/wiki/sources/draft/190926-swh-skill-standardize-PLAN.md` | created |
| `llmwiki/graph/190926-swh-skill-standardize.graph.json` | created |
| `fdk/tools/swh-lint.py` | created |
| `harness/tests/test_swh_lint.py` | created |
| `llmwiki/.claude/hooks/user_prompt_submit.py` | modified |
| `harness/tests/test_goal_hook.py` | created |

## Notes
- Invoked via: `/ingest` skill
- User đã duyệt 19/09: layout `skills/external/`, 23 skill ngoài, pilot ba skill trước khi fan-out tám lô.

## Origin
- **Draft:** `wiki/sources/draft/190926-ingest-swh-standard.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
