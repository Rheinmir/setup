---
type: index
title: "Issues — ledger local"
status: living
tags: [issue, ledger, raise-issue, handoff]
timestamp: 2026-07-03
id: issues-ledger
---

# Issues — ledger local

> Ledger issue travel-được (đi theo repo, là NGUỒN CHÂN LÝ). Mỗi dòng = một issue.
> Raise bằng skill `/raise-issue`. Nếu repo có tracker remote (GitHub/GitLab/Gitea) thì mirror lên đó — cột `tracker`.
> Người nhận mở bằng `entry` (thường `/fdk`). Chi tiết ở file draft tương ứng.

| id | kind | tiêu đề | status | assignee | entry | tracker |
|----|------|---------|--------|----------|-------|---------|
| [030726-foundation-section](draft/030726-foundation-section.md) | foundation | Mọi wiki thiếu mục Foundation (bài toán · vì sao tồn tại · vì sao chọn công nghệ) | open | @Rheinmir | /fdk | [GH#6](https://github.com/Rheinmir/setup/issues/6) |
| [030726-orca-independence-planb](draft/030726-orca-independence-planb.md) | architecture | Orca-independence: tự-build orchestration optional làm Plan B | open | @Rheinmir | /fdk | [GH#7](https://github.com/Rheinmir/setup/issues/7) |
| [030726-skill-usage-dashboard](draft/030726-skill-usage-dashboard.md) | feature-gap | Thống kê skill-usage thực tế → dashboard HTML báo cáo hàng tuần | open | @Rheinmir | /fdk | [GH#8](https://github.com/Rheinmir/setup/issues/8) |
| [030726-memory-episodic-vector](draft/030726-memory-episodic-vector.md) | feature-gap | Memory: episodic + vector + temporal cho llmwiki (4/4 tầng) — frontier THUA #1 | open | @Rheinmir | /fdk | [GH#9](https://github.com/Rheinmir/setup/issues/9) |
| [030726-self-evolving-skills](draft/030726-self-evolving-skills.md) | feature-gap | Self-evolving skills: vòng CoEvoSkills nội bộ (sinh→eval→merge) — frontier THUA #2 | open | @Rheinmir | /fdk | [GH#10](https://github.com/Rheinmir/setup/issues/10) |
| [030726-observability-runtime](draft/030726-observability-runtime.md) | feature-gap | Observability runtime: tracing + eval-per-skill + simulation cho orca — frontier THUA #3 | open | @Rheinmir | /fdk | [GH#11](https://github.com/Rheinmir/setup/issues/11) |
| [030726-orchestration-scale](draft/030726-orchestration-scale.md) | architecture | Orchestration scale: DAG + file-bus, orca hàng-trăm-subagent có verify — frontier CHỚM #1 | open | @Rheinmir | /fdk | [GH#12](https://github.com/Rheinmir/setup/issues/12) |
| [030726-skill-resolve-supplychain](draft/030726-skill-resolve-supplychain.md) | tech-debt | Skill-resolve ambiguity + supply-chain audit — frontier CHỚM #2 | open | @Rheinmir | /fdk | [GH#13](https://github.com/Rheinmir/setup/issues/13) |

## Origin
Tạo bởi skill `/raise-issue` (phiên 2026-07-03) như ledger tập trung cho issue local travel-được. Bắt nguồn từ phiên hỏi về vai trò YAML/Python → council-026 phát hiện gap nền tảng (thiếu Foundation) + đề xuất Orca-independence Plan B. Nguồn bằng chứng: `llmwiki/html/030726-yaml-vs-python.html`, `llmwiki/html/council/council-report-026-seed42.html`.

| [030726-multi-session-add-guard](draft/030726-multi-session-add-guard.md) | process | Đa-session chung working tree: git add -A trộn việc — cần guard quy-session | open | @Rheinmir | /fdk | _(ledger-only)_ |
| [030726-overstack-html-audit](draft/030726-overstack-html-audit.md) | tech-debt | overstack.html audit đa-góc-nhìn: mâu thuẫn nội tại + lỗi thời 3 commit + UX (dark/search/a11y) | open | @Rheinmir | /fdk | [GH#14](https://github.com/Rheinmir/setup/issues/14) |
| [030726-ralph-br-frame-production-line](draft/030726-ralph-br-frame-production-line.md) | architecture | Dây chuyền Ralph: BR-kỹ → frames gắn-chặt-code → mỗi frame là loop có harness + monitor | open | @Rheinmir | /fdk | [GH#15](https://github.com/Rheinmir/setup/issues/15) |
| [030726-retrieval-eval-baseline-rot](draft/030726-retrieval-eval-baseline-rot.md) | tech-debt | retrieval-eval giòn (TOKEN_EPS=0 spam) + pull-gate hit@1→0 | done | @Rheinmir | /fdk | [GH#16](https://github.com/Rheinmir/setup/issues/16) |
| [040726-precommit-slow-fragile-on-commit](draft/040726-precommit-slow-fragile-on-commit.md) | tech-debt | pre-commit 17-rule fire-drill >2ph khi commit — timeout + ngắt-giữa-chừng hỏng index | open | @Rheinmir | /fdk | [GH#18](https://github.com/Rheinmir/setup/issues/18) |
| [040726-selftest-nested-commit-unguarded](draft/040726-selftest-nested-commit-unguarded.md) | tech-debt | Self-test harness chạy git commit LỒNG không tắt hook → nguy cơ tự-kích đệ quy | open | @Rheinmir | /fdk | [GH#30](https://github.com/Rheinmir/setup/issues/30) |
| [050726-ship-selfindex-engine-downstream](draft/050726-ship-selfindex-engine-downstream.md) | foundation | Ship self-index engine (wiki-graph + retrieval) xuống downstream — hết credibility gap 'query được' | open | @Rheinmir | /fdk | [GH#41](https://github.com/Rheinmir/setup/issues/41) |
| [050726-wikigraph-package-import-resolver](draft/050726-wikigraph-package-import-resolver.md) | tech-debt | Engine wiki-graph: resolver Python chỉ khớp basename 1-segment → import qualified theo package không nối cạnh | open | @Rheinmir | /fdk | [GH#43](https://github.com/Rheinmir/setup/issues/43) |
| [050726-wikigraph-dangling-wikilink](draft/050726-wikigraph-dangling-wikilink.md) | tech-debt | wiki-graph: broken wikilink [[X]] đẻ cạnh dangling trỏ node không tồn tại | open | @Rheinmir | /fdk | [GH#47](https://github.com/Rheinmir/setup/issues/47) |
| [050726-explicit-index-scope-yaml](draft/050726-explicit-index-scope-yaml.md) | foundation | Harness/wiki-graph: khai báo scope index tường minh qua .overstack.yaml | in-progress | @Rheinmir | /fdk | [GH#49](https://github.com/Rheinmir/setup/issues/49) |
| [050726-unify-install-manifest](draft/050726-unify-install-manifest.md) | foundation | Thống nhất install: bootstrap kéo file-list từ manifest → ship engine + wire llmwiki hooks | in-progress | @Rheinmir | /fdk | [GH#51](https://github.com/Rheinmir/setup/issues/51) |
| [050726-reachability-sweep-skill-tools](draft/050726-reachability-sweep-skill-tools.md) | foundation | Reachability sweep: skill-shipped trỏ tool .py không ship (GH#54) | in-progress | @Rheinmir | /fdk | [GH#54](https://github.com/Rheinmir/setup/issues/54) |
