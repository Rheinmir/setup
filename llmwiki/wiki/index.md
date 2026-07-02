# Wiki Index

> Khuôn wiki per-project (demo). Wiki RIÊNG của framework nằm ở `fdk/wiki/` (the kit — ADR-008).

| File | Type | Summary |
|------|------|---------|
| [example-concept](concepts/example-concept.md) | concept | Ví dụ một trang concept hợp lệ (Origin + OKF) cho project dùng llmwiki |
| [300626-audit-fix-docs-site-macos](draft/uiux/300626-audit-fix-docs-site-macos.md) | draft | Audit + 8 fix (a11y/head/glass) cho skill docs-site-macos, đồng bộ cả 2 bản mirror |
| [010726-onboard-html-tabs-redesign](draft/orca/010726-onboard-html-tabs-redesign.md) | draft | 2026-07-01 |
| [010726-trupillar4-council-persona](draft/orca/010726-trupillar4-council-persona.md) | draft | Chốt cứng Trụ 4 (cổng CI code-health) + persona-lens 18 vĩ nhân cho council (BNAL) |
| [010726-dev-harness-kit](draft/orca/010726-dev-harness-kit.md) | draft | Thiết kế 'dev tự build harness' (BNAL) + council 18 ông chọn checksum-seal; report HTML |
| [020726-docs-site-fdk-strategy](sources/draft/020726-docs-site-fdk-strategy.md) | draft | Render concept fdk-dev-strategy (Mongol pattern) thành docs site HTML liquid-glass |
| [020726-wiki-core-relations](sources/draft/020726-wiki-core-relations.md) | draft | Đánh giá wiki theo 6 tiêu chí + thiết kế wiki-core v2, đã qua council 5-phản-biện (roadmap sửa: guardrail concurrency/depth-cap trước khi build) |
| [architecture](sources/evals/retrieval/architecture.md) | eval | Golden truy-hồi: Kiến trúc repo setup gồm những gì? |
| [blocking-layer](sources/evals/retrieval/blocking-layer.md) | eval | Golden truy-hồi: Lớp CHẶN nằm ở hook/CI hay ở MCP? |
| [bnal-adapter](sources/evals/retrieval/bnal-adapter.md) | eval | Golden truy-hồi: build-now-adapt-later: core-now + adapter verified:false nghĩa là gì? |
| [boris-roles](sources/evals/retrieval/boris-roles.md) | eval | Golden truy-hồi: 5 vai vòng đời agent của Boris Cherny là gì? |
| [boris-template](sources/evals/retrieval/boris-template.md) | eval | Golden truy-hồi: Áp 5 archetype Boris Cherny vào template: sweep-gate + persona dispatc |
| [decision-adr-gate](sources/evals/retrieval/decision-adr-gate.md) | eval | Golden truy-hồi: Gate ép quyết định kiến trúc thành ADR (R13) hoạt động ra sao? |
| [docs-macos](sources/evals/retrieval/docs-macos.md) | eval | Golden truy-hồi: Skill docs-site-macos dùng để làm gì? |
| [enforcement-floor](sources/evals/retrieval/enforcement-floor.md) | eval | Golden truy-hồi: Vì sao CI mới là sàn enforcement thật, ba lớp chặn ra sao? |
| [explain-clone-site](sources/evals/retrieval/explain-clone-site.md) | eval | Golden truy-hồi: Làm sao explain và clone một website? |
| [extract-site](sources/evals/retrieval/extract-site.md) | eval | Golden truy-hồi: Skill extract-site dùng để làm gì? |
| [fdk-optin](sources/evals/retrieval/fdk-optin.md) | eval | Golden truy-hồi: Vì sao framework-dev context là opt-in, không auto-bơm đầu phiên? |
| [fdk-what](sources/evals/retrieval/fdk-what.md) | eval | Golden truy-hồi: FDK — Framework Development Kit là gì, gọi khi nào? |
| [feature-catalog](sources/evals/retrieval/feature-catalog.md) | eval | Golden truy-hồi: Bản đồ mọi năng lực framework và vì sao cần nằm ở đâu? |
| [harness-local](sources/evals/retrieval/harness-local.md) | eval | Golden truy-hồi: Làm sao dự án tự build harness riêng mà KHÔNG chạm module gốc? |
| [logger-downstream](sources/evals/retrieval/logger-downstream.md) | eval | Golden truy-hồi: code-logger và bản đồ năng lực đi xuống dự án downstream thế nào? |
| [onboarding-tour](sources/evals/retrieval/onboarding-tour.md) | eval | Golden truy-hồi: Onboarding tour trong framework là gì? |
| [orient-forcequery](sources/evals/retrieval/orient-forcequery.md) | eval | Golden truy-hồi: Session orientation + auto-index + force-query quyết định thế nào? |
| [outer-eval](sources/evals/retrieval/outer-eval.md) | eval | Golden truy-hồi: Outer harness được đánh giá (evaluation) ra sao? |
| [policy-sot](sources/evals/retrieval/policy-sot.md) | eval | Golden truy-hồi: Policy là nguồn chân lý — quyết định enforcement nằm ở đâu? |
| [project-local-rule](sources/evals/retrieval/project-local-rule.md) | eval | Golden truy-hồi: Dự án tự phát triển rule riêng P-namespace sandbox-safe thế nào? |
| [protected-lib](sources/evals/retrieval/protected-lib.md) | eval | Golden truy-hồi: Cơ chế bảo vệ pattern library khỏi sửa nhầm là gì? |
| [pull-gate](sources/evals/retrieval/pull-gate.md) | eval | Golden truy-hồi: Pull-before-change gate hoạt động thế nào? |
| [query-eval](sources/evals/retrieval/query-eval.md) | eval | Golden truy-hồi: Cách đo truy hồi (recall + token) của skill query? |
| [r10](sources/evals/retrieval/r10.md) | eval | Golden truy-hồi: R10 policy — docs-gate hook nhắc bổ sung docs là gì? |
| [rule-registry](sources/evals/retrieval/rule-registry.md) | eval | Golden truy-hồi: Danh sách rule R1..R12 canonical nằm ở đâu? |
| [scanner-gitignore](sources/evals/retrieval/scanner-gitignore.md) | eval | Golden truy-hồi: wiki-tree scanner lọc file gitignored tại đâu? |
| [skill-sot](sources/evals/retrieval/skill-sot.md) | eval | Golden truy-hồi: Vì sao skill là single source of truth, sửa hành vi ở đâu? |
| [trend-bnal-1](sources/evals/retrieval/trend-bnal-1.md) | eval | Golden truy-hồi: 5 trend 2026 đầu áp qua build-now-adapt-later là gì? |
| [trend-bnal-2](sources/evals/retrieval/trend-bnal-2.md) | eval | Golden truy-hồi: 5 trend 2026 tiếp (memory, cost, injection, hallucination) áp ntn? |
| [wiki-in-kit](sources/evals/retrieval/wiki-in-kit.md) | eval | Golden truy-hồi: Vì sao wiki của framework sống trong kit (fdk)? |
| [010726-query-retrieval-eval](draft/orca/010726-query-retrieval-eval.md) | draft | Query L0→L1: eval truy-hồi + telemetry + query 3-tầng |
| [010726-21-quy-tac-docs](sources/draft/010726-21-quy-tac-docs.md) | draft | Docs site bóc tách "21 Quy Tắc Không Thể Phá Vỡ" |
| [010726-council-report-redesign](draft/uiux/010726-council-report-redesign.md) | draft | 2026-07-01 |
| [020726-cor-pattern](draft/uiux/020726-cor-pattern.md) | draft | 2026-07-02 |
| [020726-openai-compat-endpoint-pools](sources/draft/020726-openai-compat-endpoint-pools.md) | draft | 2026-07-02 |
| [020726-adr-015-status](sources/draft/020726-adr-015-status.md) | draft | 2026-07-02 |
| [020726-eval-report](sources/draft/020726-eval-report.md) | draft | 2026-07-02 |
| [020726-orca-issue-ledger-travel](sources/020726-orca-issue-ledger-travel.md) | draft | 2026-07-02 |
| [problem-tree](concepts/problem-tree.md) | concept | 2026-07-02 |
| [020726-overstack-docs-redesign](draft/uiux/020726-overstack-docs-redesign.md) | draft | 2026-07-02 |
| [020726-ingest-fdk-strategy](sources/draft/020726-ingest-fdk-strategy.md) | draft | Ingest fdk-stragegy.md → pattern 8 nguyên tắc "Mongol" cho dev fdk (ghi vào fdk/wiki) |
| [020726-audit-fdk-strategy](sources/draft/020726-audit-fdk-strategy.md) | draft | Audit 3 trụ theo 8 nguyên tắc Mongol pattern — nợ lớn nhất ở #3 (policy chưa drive, drift che) |
