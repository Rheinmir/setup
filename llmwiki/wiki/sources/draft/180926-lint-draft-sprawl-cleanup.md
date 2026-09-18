---
type: draft
status: done
tags: [lint, tidy, output-report]
---
# 180926-lint-draft-sprawl-cleanup
**Type:** draft
**Status:** done
**Tags:** lint, output-report
**Proposed:** 2026-09-18

## What
Dọn kho nháp: đối chiếu draft treo với code thật, đóng status cái đã xong, promote bài học lên wiki, archive; gom session-provenance vào thư mục con.

## Output
- `sources/draft/` gốc: 57 → 17 file (còn lại là việc thật chưa làm/làm dở).
- 54 session-provenance → `sources/provenance/`.
- tidy.py: sidecar html đi theo, weekly-Wnn có ngày, gợi ý gitignore đúng thư mục.

## Files
| File | Action |
|------|--------|
| `harness/scripts/tidy.py` | modified |
| `harness/tests/tidy-test.sh` | modified |
| `harness/scripts/scratch-log.py` | modified |
| `harness/tests/dot-layout-runtime-test.sh` | modified |
| `fdk/wiki/concepts/orca-graph.md` | modified |
| `fdk/wiki/concepts/framework-dev-antipatterns.md` | modified |
| `harness/metrics/tasks.json` | modified |

## Notes
- Invoked via: `/lint` skill
- Status `done` ngay để lần tidy sau tự archive, không tự làm phình draft.

## Origin
- **Draft:** `wiki/sources/draft/180926-lint-draft-sprawl-cleanup.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
