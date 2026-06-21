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

## 2026-06-21 — orca-workflow + docs-site-macos — design-pattern-infographic
- Fetch 3 YouTube video metadata (Code Lủng · Học Từ Thiền Series: Phần 000/001/002)
- YouTube SPA → transcript không extract được; dùng fallback: metadata + System Design knowledge
- Created 3 MD: wiki/sources/draft/design-pattern-v{1,2,3}.md
- Created 3 HTML infographics: llmwiki/html/design-pattern-v{1,2,3}.html (docs-site-macos light glass)
- Created proposal: wiki/draft/orca/210626-design-pattern-infographic.md
- Created seq diagram: llmwiki/html/210626-design-pattern-infographic-seq.html

## 2026-06-18 — docs-site-macos — orca-framework-overview
- Created llmwiki/html/180626-orca-framework-overview.html (single-file overview, skill grid by color)
- Created draft wiki/sources/draft/180626-orca-framework-overview.md
