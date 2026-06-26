---
type: draft
title: 250626-cicd-lifecycle
status: proposed
tags: [cursor-animated-sites, output-report]
timestamp: 2026-06-25
---

# 250626-cicd-lifecycle

**Status:** proposed

## What
Trang walkthrough tương tác cho luồng CI/CD (push → pipeline → deploy → rollback), tạo bằng skill `/cursor-animated-sites` để kiểm chứng skill chạy đúng.

## Output
- HTML self-contained 12 bước: BAN ĐẦU → PUSH → CHECKOUT → INSTALL → LINT → TEST → BUILD → SCAN → DEPLOY staging → SMOKE → PROMOTE production → (NẾU LỖI) ROLLBACK.
- Áp đủ recipe skill: con trỏ mũi tên gutter (mượt, left+top cùng easing), số thứ tự, artifact hiện dần đúng job tạo (node_modules→install, dist/image→build, scan→scan, staging→deploy, smoke→smoke, prod→promote), màu theo vai trò (đọc/ghi), caption lời thường (rule #12), 2 mode tự bước/tự chạy, mặc định tĩnh frame đầy đủ.

## Files
| File | Action |
|------|--------|
| `llmwiki/html/250626-cicd-lifecycle.html` | created |

## Notes
- Invoked via: `/cursor-animated-sites` skill (kiểm chứng skill).
- Preview: http://localhost:8765/llmwiki/html/250626-cicd-lifecycle.html
- Skill chạy tốt: không phải sửa lỗi caveman/cursor/màu — các rule 1–12 áp được ngay từ đầu.

## Origin
- **Draft:** `wiki/sources/draft/250626-cicd-lifecycle.md`
- **Skill:** `~/.claude/skills/cursor-animated-sites/SKILL.md`
- **Commit:** _(filled by verify-before-commit)_
