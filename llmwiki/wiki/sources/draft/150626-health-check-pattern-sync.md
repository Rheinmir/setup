# 150626-health-check-pattern-sync
**Type:** draft
**Status:** implemented
**Tags:** health-check, harness, sync-template, pattern-version, output-report
**Proposed:** 2026-06-15

## What
Thêm skill `/health-check` + cơ chế version cho bộ "pattern chuẩn" của template: 1 file cấu hình `harness/version.json` (version + hash từng pattern), L4 eval `health-check.py`, và hook SessionStart báo cáo không chặn.

## Output
- **Chẩn đoán 3 mốc:** disk ↔ `version.json` (DRIFT), local ↔ remote `version.json` (BEHIND), manifest ↔ disk (MISSING).
- **Báo cáo không chặn** đầu phiên (SessionStart hook) — lệch thì nhắc `/sync-template`, không gate.
- **Fingerprint** = hash 49 pattern ổn định (loại `version.json` + 4 file sống theo project: index/log/active-context/decisions).
- **Tích hợp luồng:** R8 trong `policy.yaml`; `install-harness.sh` copy+đăng ký SessionStart (ROOT + GLOBAL) + auto-sinh version.json; `sync-template` thêm Step 0 (health-check trước) + Step 6b (refresh version.json sau sync).
- **Fail-open** tuyệt đối: mất mạng / thiếu file → báo cáo phần local, không gãy phiên.

## Files
| File | Action |
|------|--------|
| `harness/scripts/health-check.py` | created |
| `harness/version.json` | created (generated) |
| `llmwiki/.claude/hooks/session_start.py` | created |
| `llmwiki/skills/utils/health-check.md` | created |
| `harness/policy.yaml` | modified (R8) |
| `harness/scripts/install-harness.sh` | modified (copy + SessionStart wiring) |
| `llmwiki/.claude/settings.json` | modified (SessionStart hook) |
| `llmwiki/skills/utils/sync-template.md` | modified (Step 0 + 6b) |
| `.template-manifest.json` | modified (+health-check.md) |

## Notes
- Invoked via: thiết kế theo yêu cầu user; build trên nhánh `orca` (nơi harness sống) để sync xuống.
- Quyết định thiết kế (qua hỏi-đáp): file mới + hash từng pattern · SessionStart báo cáo không chặn · build trên orca.
- Đã test: offline / remote-404 fail-open / drift / missing / `--fail-on` exit codes · `install-harness.sh` end-to-end trên project mới (SessionStart đăng ký đủ 5 event).
- Liên quan: [[sync-template]] (thực thi sync), `wiki-health.py` (L4 anh em — soi nội dung wiki).

## Origin
- **Draft:** `wiki/sources/draft/150626-health-check-pattern-sync.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
