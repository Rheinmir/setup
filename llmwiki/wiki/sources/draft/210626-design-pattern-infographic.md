# 210626-design-pattern-infographic
**Type:** draft
**Status:** proposed
**Tags:** orca-workflow, docs-site-macos, output-report
**Proposed:** 2026-06-21

## What
Fetch metadata từ 3 YouTube video (Code Lủng · Học Từ Thiền series), distill thành 3 MD files và render 3 HTML infographic docs-site-macos style.

## Output
- 3 MD files — nội dung System Design theo metadata + fallback knowledge (transcript YouTube không extract được qua WebFetch)
- 3 HTML infographic — light glass docs-site-macos, sidebar cố định, animated SVG diagrams, draggable nodes, code copy buttons
- 1 proposal + 1 seq diagram

## Files
| File | Action |
|------|--------|
| `wiki/sources/draft/design-pattern-v1.md` | created |
| `wiki/sources/draft/design-pattern-v2.md` | created |
| `wiki/sources/draft/design-pattern-v3.md` | created |
| `llmwiki/html/design-pattern-v1.html` | created |
| `llmwiki/html/design-pattern-v2.html` | created |
| `llmwiki/html/design-pattern-v3.html` | created |
| `llmwiki/wiki/draft/orca/210626-design-pattern-infographic.md` | created |
| `llmwiki/html/210626-design-pattern-infographic-seq.html` | created |
| `wiki/index.md` | modified |
| `wiki/log.md` | modified |

## Notes
- YouTube transcript không accessible qua WebFetch (SPA + timedtext API trống)
- Fallback: dùng oEmbed metadata + System Design knowledge
- Series: Code Lủng · Học Từ Thiền — Phần 000 (Phan Văn Ngọc Thắng), 001 (Trần Hồng Gấm), 002 (Bạch Hồng Vinh)
- Preview server đã chạy trên port 8765
- Invoked via: `/orca-workflow` → `/docs-site-macos`

## Origin
- **Draft:** `wiki/sources/draft/210626-design-pattern-infographic.md`
- **Commit:** `73ad42f` — feat(wiki): add Học Từ Thiền System Design series
- **Date promoted:** 2026-06-21
