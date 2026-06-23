---
type: draft
title: 210626-design-pattern-infographic
status: done
tags: [orca-workflow, design-pattern, infographic]
timestamp: 2026-06-21
---

# 210626-design-pattern-infographic

**Status:** done
**Sequence diagram (hoạt họa):** [html/210626-design-pattern-infographic-seq.html](../../../html/210626-design-pattern-infographic-seq.html)

## Plan
- [x] Task 1: Fetch transcript video 1 (KIrbA-wEURg), distill nội dung design pattern → `wiki/sources/draft/design-pattern-v1.md`
- [x] Task 2: Fetch transcript video 2 (_U4H5FSIb-c), distill nội dung design pattern → `wiki/sources/draft/design-pattern-v2.md`
- [x] Task 3: Fetch transcript video 3 (LY8_RaLDJT4), distill nội dung design pattern → `wiki/sources/draft/design-pattern-v3.md`
- [x] Task 4: Build 3 HTML infographics từ 3 MD files (docs-site-macos style) → `html/design-pattern-v1.html`, `html/design-pattern-v2.html`, `html/design-pattern-v3.html`

## Agent Task Assignment
| Task | Agent | Model | Status |
|------|-------|-------|--------|
| Fetch transcript + distill video 1 (KIrbA-wEURg) | Claude main | claude-sonnet-4-6 | done |
| Fetch transcript + distill video 2 (_U4H5FSIb-c) | Claude main | claude-sonnet-4-6 | done |
| Fetch transcript + distill video 3 (LY8_RaLDJT4) | Claude main | claude-sonnet-4-6 | done |
| Build 3 HTML infographics từ 3 MD | Claude main | claude-sonnet-4-6 | done |

## Files sẽ tạo/sửa
| File | Action | Lý do |
|------|--------|-------|
| `wiki/sources/draft/design-pattern-v1.md` | create | Distilled content từ video 1 |
| `wiki/sources/draft/design-pattern-v2.md` | create | Distilled content từ video 2 |
| `wiki/sources/draft/design-pattern-v3.md` | create | Distilled content từ video 3 |
| `html/design-pattern-v1.html` | create | Infographic docs-site-macos cho video 1 |
| `html/design-pattern-v2.html` | create | Infographic docs-site-macos cho video 2 |
| `html/design-pattern-v3.html` | create | Infographic docs-site-macos cho video 3 |
| `wiki/index.md` | modify | Append 3 entry mới |
| `wiki/log.md` | modify | Log operation |

## Risks
- YouTube transcript có thể không available (captions off / private) → fallback dùng video description + page metadata
- Transcript raw rất dài → cần distill kỹ, không dump text thô vào MD
- Mỗi video có thể cover nhiều pattern → tổ chức MD theo section rõ ràng

## Origin
- **Draft:** `wiki/draft/orca/210626-design-pattern-infographic.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
