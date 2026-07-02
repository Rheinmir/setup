# Operation Log

## 2026-06-28 — migrate — framework wiki → fdk/wiki
`llmwiki/wiki` giờ là khuôn per-project (chỉ giữ 1 file demo). Wiki riêng của framework
(64 file: ADR-001..008, concepts harness/fdk) chuyển sang `fdk/wiki/` — "the kit". Xem ADR-008.

## 2026-06-30 — redesign-existing-projects — audit-fix-docs-site-macos
Audit skill `docs-site-macos` theo checklist redesign; vá 8 defect (focus-ring, viewport/meta+favicon, collapse-clip, prototype self-contained, Output-Report lặp, shadow tint, smooth-scroll, reduced-motion) + a11y (skip-link/`<main>`/SVG-aria/tabular-nums/text-wrap). Áp cho CẢ 2 bản mirror (`skills/docs-site-macos/SKILL.md` ↔ `llmwiki/skills/utils/docs-site-macos.md`), verify content identical (939 dòng, diff=0). Mở rộng audit sang 3 skill sinh-HTML họ hàng (cursor-animated-sites, md-to-html, uat-nonit-testcase). Quyết định chiến thuật parity: GIỮ committed-mirror + gate (bác generate-at-install vì gây cross-project drift); vá `stop.py` để tự chạy `sync-skills.py` cuối mỗi lượt đụng skill. Toàn bộ 65 cặp canonical↔mirror verify identical.

## 2026-07-01 — build-now-adapt-later — trupillar4-council-persona
Chốt cứng Trụ 4 bằng cổng CI tất định không-LLM (`code_health.py`: mọi .py compile sạch, wire fdk-gate+CI; lint sâu advisory — BNAL). Triển khai persona-lens council: 18 vĩ nhân + 13 cặp đối-trọng + lệnh `council.py roster --case` (thuần lookup, ép ≥1 cặp). Commit 490df16 + 04b3fcd, fdk-gate 20/20.

## 2026-07-01 — fdk+bnal+council — dev-harness-kit
Thiết kế cơ chế 'dev tự build harness riêng' (skeleton + không-chạm-core + protected/seal) theo BNAL: nền đã có harness-local(ADR-011)+R14; chốt 3 mảnh CHẮC (scaffolder/seal-command/R14-ext) + cô lập 2 ẩn số. Council 18 persona (council.py mean-rank, thoát loop) chọn checksum-seal #1 (1.39) > R14-ext (1.72) > chmod (3.0) > zip (3.89). Report: llmwiki/html/010726-dev-harness-kit-council.html.

<!-- log:auto:start -->

### 🤖 Log tự-động (code-logger, không do agent ghi)

| Thời điểm | Event | Chi tiết |
|---|---|---|
| 2026-07-02 11:29:23 | `file.write` | llmwiki/html/fdk-problem-tree.html · tool=Edit · actor=agent · prev=54b2142ad17e39220dbd97c24d45de663887ae9898b7bc87a7a2 |
| 2026-07-02 11:29:34 | `file.write` | llmwiki/html/fdk-problem-tree.html · tool=Edit · actor=agent · prev=c5b464ee96deef570497f11df30ca183c95432eafa874423aa1e |
| 2026-07-02 11:29:40 | `file.write` | llmwiki/html/fdk-problem-tree.html · tool=Edit · actor=agent · prev=dfe606961f1bc43e286baa88eff5b4e7cdd7abad6b6e68d43d5e |
| 2026-07-02 11:29:41 | `file.write` | llmwiki/html/fdk-problem-tree.html · tool=Edit · actor=agent · prev=aedfb9a5c74a40b598054e312bfcb32843c4264d9902b67d5f3c |
| 2026-07-02 11:31:47 | `file.write` | llmwiki/html/fdk-problem-tree.html · tool=Edit · actor=agent · prev=78998fff037735a08d9094ce4ea3f49cd832d2430182afa348d8 |
| 2026-07-02 12:20:57 | `file.write` | llmwiki/html/fdk-problem-tree.html · tool=Edit · actor=agent · prev=11be0ea1d274165734c150c354dda5a04898bf28553d1c620405 |
| 2026-07-02 12:20:58 | `file.write` | llmwiki/html/fdk-problem-tree.html · tool=Edit · actor=agent · prev=e37e37ceb5e9f881064dc984c0f22b38a3d94853a2429d5d03cc |
| 2026-07-02 12:21:00 | `file.write` | llmwiki/html/fdk-problem-tree.html · tool=Edit · actor=agent · prev=775c24408ac1ba8324168977b4057644cbbbbf224dde894c9f8a |
| 2026-07-02 12:28:08 | `file.write` | skills/fdk/SKILL.md · tool=Edit · actor=agent · prev=0535039f1504c8361f14f7ab78f529e2a353ad63b5e67b47234fc58850283a08 ·  |
| 2026-07-02 12:28:24 | `file.write` | llmwiki/html/fdk-problem-tree.html · tool=Edit · actor=agent · prev=e14ba6d45be7b8cf5266c2aafe2d79e81c76e105840fe3d7aa5a |
| 2026-07-02 12:28:35 | `file.write` | llmwiki/html/fdk-problem-tree.html · tool=Edit · actor=agent · prev=da6d609bab34188489a569c564b2158667b14e0ecf258f199bd0 |
| 2026-07-02 12:31:56 | `file.write` | skills/fdk/SKILL.md · tool=Edit · actor=agent · prev=cd2de553e39ea06455c166dfbadb94c11518681cb5385aa0bb56b6e5bfd982db ·  |
| 2026-07-02 12:32:44 | `file.write` | llmwiki/html/fdk-problem-tree.html · tool=Edit · actor=agent · prev=3f7ebd1728a7d2f7f684a848237ed863d5cd3f707198a05e6d32 |
| 2026-07-02 12:32:52 | `file.write` | llmwiki/html/fdk-problem-tree.html · tool=Edit · actor=agent · prev=17b4e2bef90d59d3dee1f0c83d3bcaef6c1d72aeccd1ea932d73 |
| 2026-07-02 12:33:11 | `file.write` | llmwiki/html/fdk-problem-tree.html · tool=Edit · actor=agent · prev=5cc575cdb03713d0916280a6bda8b5fb6a728b6fc85192775f59 |
| 2026-07-02 12:33:26 | `file.write` | llmwiki/html/fdk-problem-tree.html · tool=Edit · actor=agent · prev=5cdd2622037eba60ce59c2eb8ea716e96219b80ec1ce7fc197f5 |
| 2026-07-02 12:38:42 | `file.write` | skills/fdk/SKILL.md · tool=Edit · actor=agent · prev=00f03c8259bc083f97aa9139196957d6667c82f212edfc162b99aa924bed24cc ·  |
| 2026-07-02 12:41:57 | `file.write` | llmwiki/wiki/sources/draft/020726-eval-report.md · tool=Write · actor=agent · prev=d02f0f8be1a6f04e765b0c9e120a62528b764 |
| 2026-07-02 12:42:08 | `file.write` | llmwiki/wiki/sources/draft/020726-eval-report.md · tool=Edit · actor=agent · prev=023f472e9427e93895264e589a7a44df440253 |
| 2026-07-02 12:45:36 | `file.write` | fdk/tools/sync-skill.sh · tool=Write · actor=agent · prev=9610569284b5c81703a5f5f69cd3f15947a57de3ec8bb652964095e7dc64f3 |
| 2026-07-02 12:45:54 | `file.write` | skills/fdk/SKILL.md · tool=Edit · actor=agent · prev=c6570d74a2affb1877c7f90935080683c6193196dfed96374971bbf6574753fb ·  |
| 2026-07-02 12:47:08 | `file.write` | harness/validators/report_show_path.py · tool=Write · actor=agent · prev=49e613de5b6d5c53f671b17154541b767298be35fe17059 |
| 2026-07-02 12:47:20 | `file.write` | llmwiki/.claude/hooks/post_tool_use.py · tool=Edit · actor=agent · prev=38680a45436f5d289fe31eb6d2cde267ef2596947cadb075 |
| 2026-07-02 12:47:41 | `file.write` | llmwiki/.claude/hooks/session_end.py · tool=Edit · actor=agent · prev=7f177268894fdf793918ca7950e0cf84c21df0755e384e6638 |
| 2026-07-02 12:47:50 | `file.write` | llmwiki/.claude/hooks/session_end.py · tool=Edit · actor=agent · prev=5cdc2aaa13b69722754680e6c765b92a4a1f53550832db66df |
| 2026-07-02 12:52:49 | `task.new` |  · task=T-260702-01 · title=orca-issue + ledger travel (p-02, p-04) · state=proposed · actor=agent · prev=4bcac2f15648c6 |
| 2026-07-02 12:54:09 | `file.write` | llmwiki/wiki/sources/draft/020726-orca-issue-ledger-travel.md · tool=Write · actor=agent · prev=9ea9e5aa58d3004a97723c8d |
| 2026-07-02 12:55:58 | `file.write` | llmwiki/html/020726-orca-issue-ledger-travel-seq.html · tool=Write · actor=agent · prev=75147860a8ddef8bcf2b278e0ba270d9 |
| 2026-07-02 13:00:05 | `file.write` | skills/orca-issue/SKILL.md · tool=Write · actor=agent · prev=574cf76fb1ec9fa6470a099f01331c2df640824b0e08372c6e2f825fa53 |
| 2026-07-02 13:01:33 | `file.write` | skills/orca-workflow/SKILL.md · tool=Edit · actor=agent · prev=ed8a065a33fa318d277391471a0ecc4550a1cff7e24484f512996c90a |
| 2026-07-02 13:02:23 | `file.write` | harness/poc-vendor-neutral/install.sh · tool=Edit · actor=agent · prev=804c4c309725acd2f4d5b08bfad9e28f98abaf5e7702f7fbd |
| 2026-07-02 13:02:57 | `file.write` | llmwiki/.claude/hooks/session_end.py · tool=Edit · actor=agent · prev=8e1a1cec86179e0a9ad94b7325d7b91cf8ace44126efae76e4 |
| 2026-07-02 13:03:05 | `file.write` | llmwiki/.claude/hooks/session_end.py · tool=Edit · actor=agent · prev=0fa2cd32cdb9a166b951eb749bb6f844d93fedff4b1c35b3e5 |
| 2026-07-02 13:04:20 | `file.write` | llmwiki/wiki/concepts/problem-tree.md · tool=Write · actor=agent · prev=450e568a2caaa2b2fbd497ab07f13229cec02024715da5a7 |
| 2026-07-02 13:11:09 | `file.write` | fdk/wiki/concepts/fdk-dev-strategy.md · tool=Write · actor=agent · prev=6ec512883c8c4e1d2c504a82c2774a815a888bc34760996f |
| 2026-07-02 13:11:20 | `file.write` | fdk/wiki/sources/mongol-ai-strategy.md · tool=Write · actor=agent · prev=0fbd49403e30e443bb7227bd6064d26ebca7ed95df3155e |
| 2026-07-02 13:11:59 | `file.write` | fdk/wiki/index.md · tool=Edit · actor=agent · prev=93b1923f21936f521d776d938a662f088d49d4ba5df8014cb27de8d9395c5633 · h= |
| 2026-07-02 13:12:14 | `file.write` | llmwiki/wiki/sources/draft/020726-ingest-fdk-strategy.md · tool=Write · actor=agent · prev=db449df58b1d38de5b5dc3699d3a6 |
| 2026-07-02 13:12:21 | `file.write` | llmwiki/wiki/sources/draft/020726-ingest-fdk-strategy.md · tool=Edit · actor=agent · prev=9f395eae32637ad4301a5d875cbd5b |
| 2026-07-02 13:12:29 | `file.write` | llmwiki/wiki/index.md · tool=Edit · actor=agent · prev=99d4dbb5c2defae7345e974963839bd369f9e2dc4fc0175a837f39a6480b8025  |

<!-- log:auto:end -->
## 2026-07-01 — orca-onboard — html-tabs-redesign (propose)
## 2026-07-01 — docs-site-macos — 21-quy-tac-docs

## 2026-07-01 — redesign-existing-projects — council-report-redesign

## 2026-07-02 — build-now-adapt-later+fdk — cor-controlled-output-renderer (council verdict: khả thi/hẹp)
## 2026-07-02 — docs-site-macos — openai-compat-endpoint-pools

## 2026-07-02 — docs-site-macos — adr-015-status

## 2026-07-02 — redesign-existing-projects — overstack-docs-redesign

## 2026-07-02 — orca-eval — eval-report session hiện tại (lens Meadows)

## 2026-07-02 — propose — orca-issue-ledger-travel (T-260702-01, p-02+p-04)

## 2026-07-02 — orca-issue+ledger-travel — T1-T5 implemented (skill orca-issue, orca-workflow rẽ nhánh, seed template, R17 fallback, concept problem-tree)

## 2026-07-02 — ingest — fdk-stragegy
- Distill `raw/fdk-stragegy.md` → `fdk/wiki/concepts/fdk-dev-strategy.md` + `fdk/wiki/sources/mongol-ai-strategy.md` (wiki framework, ADR-008)
- Draft report: `wiki/sources/draft/020726-ingest-fdk-strategy.md`

## 2026-07-02 — verify-before-commit — promoted 020726-orca-issue-ledger-travel (commit 49d2361, task T-260702-01 done, 20/20 test + drift 52/0)
