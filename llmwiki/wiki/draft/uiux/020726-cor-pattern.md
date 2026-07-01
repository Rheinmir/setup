---
title: cor-controlled-output-renderer
type: draft
status: proposed
tags: [build-now-adapt-later, fdk, council, output-report, cor]
proposed: 2026-07-02
---

# 020726-cor-pattern
**Type:** draft
**Status:** proposed
**Tags:** cor, council, build-now-adapt-later, fdk

## What
Chưng "Controlled Output Renderer" (COR) từ `council.py` Stage-4 thành microlib dùng
chung `harness/scripts/lib/cor.py`, sau khi khảo sát 65 skill + `/council` thẩm định.

## Council verdict (5 ghế, blind peer-rank, seed 42)
KHẢ THI **nhưng HẸP**. Consensus: Munger (scope 3-4 skill, opt-in) > Taleb (barbell:
stateless ≤200 dòng, pin version, add-only) > Linus (extract chỉ helper I/O, prove
trên 1 consumer) > Meadows (gate-first, reuse docs-site-macos) > Rams (doc+gate, no lib).
→ KHÔNG god-lib cho 13 skill; microlib opt-in + contract, dogfood council trước.
Report: `llmwiki/html/council/council-report-004-seed42.html`.

## Output (build-now-adapt-later)
- **Built now:** `harness/scripts/lib/cor.py` (124 dòng, stateless, zero third-party):
  `esc` · `write_versioned` (versioning+isolation+latest) · `page` (offline shell) +
  `_selftest` (5 bất biến, `python3 cor.py` exit 0).
- **Dogfood:** `council.py._write_report` giờ gọi `cor.write_versioned` (đã bỏ code trùng);
  selftest council 12/12 vẫn xanh, report versioned #004 sinh qua cor.
- **Quarantine (adapt-later):** roster adopter + `verified` flag trong `harness/docs/cor-guide.md`
  (council=verified; wikieval/trace-grader/failure-flywheel/retrieval-eval/propose=false).
  Wire thêm = 1 dòng `cor.write_versioned` rồi flip verified — không đụng cor.py.
- **Contract/guide:** `harness/docs/cor-guide.md` (6 bất biến + API + ranh giới không chồng
  vai docs-site-macos/md-to-html; loại skill creative khỏi scope).

## Files
| File | Action |
|------|--------|
| `harness/scripts/lib/cor.py` | created |
| `harness/scripts/lib/__init__.py` | created |
| `harness/docs/cor-guide.md` | created |
| `harness/scripts/council.py` | modified (import cor + _write_report dùng cor) |
| `llmwiki/html/council/council-report-004-seed42.html` | generated (council COR verdict) |

## Notes
- Invoked via: goal overnight → survey (3 agent) → `/council` (5 ghế) → `/build-now-adapt-later` + `/fdk`.
- Chưa ép GATE/enforce (council: đợi observe). Adopter mở rộng là bước con opt-in.

## Origin
- **Draft:** `wiki/draft/uiux/020726-cor-pattern.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
