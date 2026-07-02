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
| 2026-07-02 13:13:52 | `file.write` | harness/poc-vendor-neutral/bin/harness-events.py · tool=Edit · actor=agent · prev=9a5f42ddb7967dc1d6cc9ff20bf4b132c046d8 |
| 2026-07-02 13:15:14 | `task.set` |  · task=T-260702-01 · state=done · note=49d2361 · actor=agent · prev=d294f254d7095a58c74637081a002c7874b953e41ac62930c39 |
| 2026-07-02 13:30:24 | `file.write` | llmwiki/html/020726-fdk-dev-strategy.html · tool=Write · actor=agent · prev=4ae2d3dd2144be76d8f05cd00c169c797c0b5839a79b |
| 2026-07-02 13:30:33 | `file.write` | llmwiki/html/020726-fdk-dev-strategy.html · tool=Edit · actor=agent · prev=7e92571df727bdfdbcc4e05dc472109035b44625bd59d |
| 2026-07-02 13:30:58 | `file.write` | llmwiki/wiki/sources/draft/020726-docs-site-fdk-strategy.md · tool=Write · actor=agent · prev=1a2633417dc413acb3b777cb8d |
| 2026-07-02 13:31:06 | `file.write` | llmwiki/wiki/sources/draft/020726-docs-site-fdk-strategy.md · tool=Edit · actor=agent · prev=588aac7f2da14ea845e3a304019 |
| 2026-07-02 13:31:13 | `file.write` | llmwiki/wiki/index.md · tool=Edit · actor=agent · prev=213f5f4b9e739d2e9039f629c4a881144795ffe492c46c07bd58fe4ca1858955  |
| 2026-07-02 13:34:24 | `file.write` | llmwiki/wiki/sources/draft/020726-audit-fdk-strategy.md · tool=Write · actor=agent · prev=9780f800dbb5a4e68c3dd568488e3d |
| 2026-07-02 13:34:34 | `file.write` | llmwiki/wiki/index.md · tool=Edit · actor=agent · prev=955148f0f33ab3d0954928a3c01c15dafa439082d9cb745947d7af428607d771  |
| 2026-07-02 13:54:02 | `file.write` | llmwiki/html/020726-audit-fdk-strategy.html · tool=Write · actor=agent · prev=d8187806152f9076d6be1c5fcf6ff808682b9d7511 |
| 2026-07-02 13:54:17 | `file.write` | llmwiki/wiki/sources/draft/020726-audit-fdk-strategy.md · tool=Edit · actor=agent · prev=5383896908096b8ea65d2ecf25b59e1 |
| 2026-07-02 14:08:46 | `file.write` | llmwiki/wiki/sources/draft/020726-wiki-core-relations.md · tool=Write · actor=agent · prev=9c699aedc79cd3e4e9dd10c5a4837 |
| 2026-07-02 14:08:55 | `file.write` | llmwiki/wiki/index.md · tool=Edit · actor=agent · prev=b618051b7a9397ceded38944df4176da8b68c5c00a901894ae8bb4100ef29859  |
| 2026-07-02 14:20:44 | `file.write` | llmwiki/wiki/sources/draft/020726-wiki-core-relations.md · tool=Edit · actor=agent · prev=79cec55afe3297105f6f693d3d5808 |
| 2026-07-02 14:20:50 | `file.write` | llmwiki/wiki/index.md · tool=Edit · actor=agent · prev=79fcd8f033779f91117d617bb7139502a32ea1de6878d1eb23a8fd96bbcae840  |
| 2026-07-02 14:37:41 | `file.write` | llmwiki/.claude/hooks/wiki_ledger.py · tool=Write · actor=agent · prev=46c31fdebe240d05052086626233bb2d37b387842a5e53ba0 |
| 2026-07-02 14:38:12 | `file.write` | llmwiki/.claude/hooks/validators/rel_integrity.py · tool=Write · actor=agent · prev=95b06580f58867e39edec0ec2e91799d321a |
| 2026-07-02 14:38:28 | `file.write` | llmwiki/.claude/hooks/post_tool_use.py · tool=Edit · actor=agent · prev=59b80bdf678d22f17ce6cd37b10fa41022501f7a8d59cfa8 |
| 2026-07-02 14:38:32 | `file.write` | llmwiki/.claude/hooks/post_tool_use.py · tool=Edit · actor=agent · prev=635bbea5f36615f852b083f30731c96007caba1b3ee4c46f |
| 2026-07-02 14:38:55 | `file.write` | fdk/tools/wiki-relations.py · tool=Write · actor=agent · prev=ddf4e677fc29f6f2beace27f9c033d835ef941015f49ba47fc3a7bc5ce |
| 2026-07-02 14:39:18 | `file.write` | llmwiki/.claude/hooks/wiki_ledger.py · tool=Edit · actor=agent · prev=5e602c12b58f08f088a70e0111456046c71eb627da9322bc65 |
| 2026-07-02 14:39:20 | `file.write` | fdk/tools/wiki-relations.py · tool=Edit · actor=agent · prev=c6b9a3e317a6ddac0e85f6deab55d08897d4f31d744ed641badc4e12f73 |
| 2026-07-02 14:40:25 | `file.write` | llmwiki/.claude/hooks/validators/rel_integrity.py · tool=Edit · actor=agent · prev=f56a2d04e9ea6862a23412cb377851bfdd7be |
| 2026-07-02 14:41:00 | `file.write` | llmwiki/wiki/sources/draft/020726-wiki-core-relations.md · tool=Edit · actor=agent · prev=f34a3f00a267a0a971c785164a4ec6 |
| 2026-07-02 14:42:07 | `file.write` | llmwiki/wiki/sources/draft/020726-wiki-core-relations.md · tool=Edit · actor=agent · prev=a452d0087c8841ae02a3d5253d5b26 |

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

## 2026-07-02 — docs-site-macos — docs-site-fdk-strategy
- Render `fdk/wiki/concepts/fdk-dev-strategy.md` → `llmwiki/html/020726-fdk-dev-strategy.html` (mind map + 6 section + 4 diagram kéo-thả); draft `sources/draft/020726-docs-site-fdk-strategy.md`.

## 2026-07-02 — fdk — audit-fdk-strategy
- Audit 3 trụ (harness/skills/llmwiki) theo kim chỉ nam fdk-dev-strategy, 3 agent song song
- Draft report: `wiki/sources/draft/020726-audit-fdk-strategy.md`
- Problem-tree: thêm 4 node p-07..p-10 (policy-not-drive, drift-che-version, mép đăng ký skill, nhịp ship wiki)

## 2026-07-02 — docs-site-macos — audit-fdk-strategy-html
- Render báo cáo audit thành `llmwiki/html/020726-audit-fdk-strategy.html` (liquid-glass, mind map, diagram kéo-thả)
- Bổ sung tình báo multi-session vào draft audit; memory mới `framework-multi-session-dev`

## 2026-07-02 — propose — wiki-core-relations
- Đánh giá hệ thống wiki (6 tiêu chí PROV/KG/context-eng) + proposal wiki-core v2: `sources/draft/020726-wiki-core-relations.md` — chờ duyệt.

## 2026-07-02 — council — wiki-core-relations
- 5 seat (Taleb/Ilya/Munger/Kahneman/Aurelius) phan bien proposal 020726-wiki-core-relations; 3 judge blind-rank, winner Ilya (mean-rank 1.0). Chairman synthesis: thu hep pham vi + 7 guardrail bat buoc (concurrency ledger, depth-cap room, migrate//validator song song...) ghi vao Phan 3 cua draft. Transcript: sources/draft/020726-council-transcript-wiki-core.json; report: html/council/council-report-005-seed42.html.

## 2026-07-02 — fdk — wiki-core v2 buoc 1+2&3
- Ledger JSONL (wiki_ledger.py, flock G1, test 8-process pass) + tombstone; migrate id+relations 82 trang (fdk/tools/wiki-relations.py, idempotent); validator rel_integrity.py warn-only (G4/G7, full-scan 0 canh bao that). Problem-tree +p-11 (partial 2/3). Buoc 4-6 cho on dinh 4-6 tuan.

## 2026-07-02 — verify-before-commit — promoted wiki-core-relations
- Gate: py_compile OK, task_lifecycle OK (backfill T-260702-01), G1 test 400/400 pass, rel-scan 0 canh bao, patterns-guard OK. Commit d4d8b90. Draft -> concepts/wiki-core-relations.md, Origin dien commit.
