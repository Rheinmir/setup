# Operation Log

## 2026-04-28 — init — Knowledge Base initialized
- Created folder structure: concepts/, entities/, sources/, sources/draft/
- Created wiki/index.md, wiki/log.md
- Created AGENT.md

## 2026-06-15 — health-check — pattern-sync version + skill + SessionStart hook
- Thêm harness/scripts/health-check.py + harness/version.json (fingerprint 49 pattern)
- Thêm skill /health-check + hook session_start.py (báo cáo không chặn)
- Wire R8 policy, install-harness.sh, sync-template Step 0/6b; +health-check.md vào manifest
- Draft: wiki/sources/draft/150626-health-check-pattern-sync.md

## 2026-06-18 — docs-site-macos — orca-framework-overview
- Created llmwiki/html/180626-orca-framework-overview.html (single-file overview, skill grid by color)
- Created draft wiki/sources/draft/180626-orca-framework-overview.md

## 2026-06-22 — docs-site-macos — chown
- Created llmwiki/html/220626-chown.html (single-file docs về lệnh chown)
- Created draft wiki/sources/draft/220626-chown.md
- 2026-06-23 00:17 — session `07d80623` — 8 tool calls — files: 230626-docs-gate-register-seq.html, 230626-docs-gate-register.md, index.md, install-harness.sh, settings.json

## 2026-06-23 — docs-site-macos — harness-docs-gate-orca-guard
- 2026-06-23 01:07 — session `07d80623` — 22 tool calls — files: 230626-docs-gate-register-seq.html, 230626-docs-gate-register.md, 230626-harness-docs-gate-orca-guard-report.md, 230626-harness-docs-gate-orca-guard.html, 230626-orca-guard-hook-seq.html, 230626-orca-guard-hook.md, index.md, install-harness.sh …

## 2026-06-23 — orca-workflow: /harness-update < 30s
- Proposal 230626-harness-update-sub30s (gate duyệt) → impl T1-T4.
- T1 install-harness.sh `--self-heal`: tự backfill Origin+index+OKF in-process, re-audit 1 lần (gộp vòng lặp 3-reinstall agent → 1 lệnh).
- T2 harness/scripts/audit.py: gộp 3 audit về 1 process; Origin backfill 1 lượt git log.
- T3 `--no-clone` fast-fail (0.02s, không treo mạng) + skip pre-commit install nếu đã cài.
- T4 viết lại skill 1-phát-gọi + bench harness/metrics/harness-update-bench.json.
- Bench: migrate-có-nợ 0.56s, re-run sạch 0.31s, smoke ⛔×3. Dispatch opencode T3 treo → kill, claude-cli tiếp quản.

## 2026-06-23 — orca-workflow: skill tạo docs đạt chuẩn OKF v0.1
- Proposal 230626-docs-skill-okf (gate duyệt) → impl T1-T3.
- T1 orca-onboard: heredoc + example block `**Type:**` bold → YAML frontmatter `type: draft` (hết tạo nợ R9).
- T2 onboard-codebase + new-project-setup: thêm dòng Rule nhắc OKF (copy _template.md).
- T3 harness/tests/docs-skill-okf-test.sh: 10/10 PASS (skill .md áp OKF, skill HTML N/A, wiki repo OKF 7/8 chỉ còn legacy 220626-chown).
- Dispatch opencode T2 no-op (0 output) → claude-cli tiếp quản (lần 2 liên tiếp opencode hỏng).
