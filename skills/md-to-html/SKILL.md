---
name: md-to-html
description: >-
  Render markdown to professional standalone HTML
---

# Skill: md-to-html

## Purpose
Biến file Markdown thành trang HTML đẹp, tự-chứa, kèm biểu đồ (Mermaid), chart (Chart.js), bảng styled, code highlight, hình ảnh tự sinh, và TOC nổi — giúp đọc tài liệu kỹ thuật trực quan hơn nhiều so với xem `.md` thô.

## When to use
- Cần render / xuất / chia sẻ một file `.md` thành HTML
- Tài liệu có nhiều bước, so sánh, số liệu cần visualize
- Muốn file tài liệu trông professional, có thể mở thẳng trong browser

## Trigger phrases
`/md-to-html`, `md2html`, `biến md thành html`, `render md`, `xuất html từ md`, `visualize doc`

## Đầu ra
Tất cả file `.html` được xuất ra PHẢI lưu vào thư mục `html/` của project (ví dụ: `/Users/giatran/infras/html/tên-file.html`), KHÔNG lưu cùng thư mục với file `.md` nguồn.

## Xem full instructions tại
`~/.gemini/antigravity/skills/md-to-html/SKILL.md`


---

## Output Report

After all main skill tasks complete, write a propose draft to the wiki.

### Steps

**1. Build the filename:**
- Format: `DDMMYY-<ten>.md`
- `DDMMYY` = today (e.g., `020626` for 2 June 2026)
- `<ten>` = 2–4 kebab-case words summarising what was done (e.g., `landing-page-coteccons`, `brand-kit-fintech`, `ingest-auth-spec`)

**2. Write** `llmwiki/wiki/sources/draft/DDMMYY-<ten>.md`:

```
# DDMMYY-<ten>
**Type:** draft
**Status:** proposed
**Tags:** <skill-name>, output-report
**Proposed:** YYYY-MM-DD

## What
<One sentence — what this skill invocation produced or decided>

## Output
<Key artefacts, files created/modified, or decisions made>

## Files
| File | Action |
|------|--------|
| `path/to/file` | created / modified |

## Notes
- Invoked via: `/<skill-name>` skill

## Origin
- **Draft:** `wiki/sources/draft/DDMMYY-<ten>.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
```

**3. Update wiki index & log:**
- `llmwiki/wiki/index.md` — append one row: `| [DDMMYY-<ten>](sources/draft/DDMMYY-<ten>.md) | draft | YYYY-MM-DD |`
- `llmwiki/wiki/log.md` — append: `## YYYY-MM-DD — <skill-name> — <ten>`

> Skip only when the skill produces zero artefacts and zero decisions (e.g., a pure display mode like `/caveman-stats`).