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
| 2026-07-02 17:07:58 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=a02f0efac6f99d3d8249428af287f8cd10dce1f74b83ca9fb26b2e19b |
| 2026-07-02 17:08:08 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=a3d45d1f7cd8f6b9f5ea2f8bb8ea4225d05cdf5a1e4d819a0d3882f14 |
| 2026-07-02 17:08:18 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=32a2f656e4f08a57eff6071915ef991c5ef0723a661c5fb72fad428a4 |
| 2026-07-02 17:08:34 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=9afcc0733703a8cb762c04c1293086e522994d62b8b715bdd1fba84ba |
| 2026-07-02 17:29:33 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Write · actor=agent · prev=10acf1ca774e3b4d98c032df7e1ef9be88da19c5d15dfae7e0b74920 |
| 2026-07-02 17:32:07 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=86237fe0d5e1ffe8cd90577db9ecee01bf613b1af6e744f89f6cdb747 |
| 2026-07-02 17:32:16 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=b7493230ab89870e19ccf456deb1cefa0caba1063f1a3d4765c07d270 |
| 2026-07-02 17:32:49 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=aab55bb1d3c976ce0d75221dd34f34ac8e2fb914a59561bacd6d26861 |
| 2026-07-02 17:34:19 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=e2d94704de420fc5a11e7ee0c24b936ed54d584028a9cacf9bcd4964b |
| 2026-07-02 17:34:30 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=f9a7930d2bf741ceb4ccd8a48f32eb0ca9526ce4bdf585934dfd17e7d |
| 2026-07-02 17:34:37 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=6627569fd7c97400616897d1836b200244abca36fdd5f9e8c07d051f8 |
| 2026-07-02 17:34:44 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=6700c11311fcd975fe9006f65a05553ed9661573c7fcae2af5fc87c49 |
| 2026-07-02 17:34:55 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=9291895738b288c5001209cf88ceb9f27a22e5e737787237e61d4bdfb |
| 2026-07-02 17:37:02 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=4583f0190f4fff1f5eec8f6614da258002f0f3bf52d95307af9f41c30 |
| 2026-07-02 17:37:20 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=f0114d1a0d8fffc5ec373aba72787650ca483a7a59de1c8b206d96a21 |
| 2026-07-02 17:37:31 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=bce5911aa0bcf0336bddcd14fd2e8ee88e186fe7ba56fa6f8f61538d9 |
| 2026-07-02 17:38:04 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=312fa9ad4f6612c749a1f2ed254d9e97df711da46bc63a144d5ff453d |
| 2026-07-02 17:38:14 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=9e23e5876bd116980258a390ad87970d85a10b9fdd1832554d9c6bc29 |
| 2026-07-02 17:41:38 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=0b6b4cab08b5df84e25d5c5c16104de2123d17f44e02f3ac46e814957 |
| 2026-07-02 17:41:46 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=9a7d8dccd71e13631d1119fda182dddaf0d24be53c4775287bcfec7c8 |
| 2026-07-02 17:41:53 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=560aaf2b155cb4d7f6ce53c519e177e445d1db2a13f7f8e73ba3c01ab |
| 2026-07-02 17:42:01 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=e9dd6bf5562d16bddcbc51778a60c500d3cb058f9f122dbed65a970e8 |
| 2026-07-02 17:42:13 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=93d82377683589fb73d5a8a604770667ee6996c746e549ca420d7c91c |
| 2026-07-02 17:42:36 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=a46e843c94e512804314f04bf66af519255664ff8dbb9dc175dc4bae2 |
| 2026-07-02 17:44:51 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=eaf3b983f6a6a9bca3a90cf04639c169ee01b71197024b8994792c352 |
| 2026-07-02 17:48:01 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=55943227977e7dbc0a77a88767596c7e09142cc8a009cf30724bddcc1 |
| 2026-07-02 17:48:10 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=e898552d9d3189d583134a6faf28630efee29923085b584ac895ecd57 |
| 2026-07-02 17:48:19 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=dce446c3eba956d23e19a62eb33e64a34a3bc004a7ebf8a729c130eb5 |
| 2026-07-02 17:48:36 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=37721d293d52d2d2e589e54a5368bd59c956fb6b1a56936efe8586399 |
| 2026-07-02 17:48:46 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=1eddebed3fe4e3a0e15e74132d881d82c9b239dd218dc83d5ef88341d |
| 2026-07-02 17:49:02 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=ebb22bf5e4ba58ddfdcfa4a209c41329066978661fb76fa3b0b46b5b0 |
| 2026-07-02 17:49:12 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=a35f67a6d4996f88dc34482cc2ece75625d8b6e9a0f1c85daa0f97bc6 |
| 2026-07-02 17:53:14 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=6a58439487f92284363337555c5dc621be89eed3a7c921d8fb58bb3b3 |
| 2026-07-02 17:53:21 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=f72f562315f752ecdae68a495ae3f3861c56943382e28c3b5c442c16a |
| 2026-07-02 17:53:31 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=13572310291e1b12ef710faf0c085d800b29f618e933e026a6706cdb5 |
| 2026-07-02 18:08:10 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=2d1c39e1baa7f27ab56848761eda52b69b9ee421baf692c1f917547d3 |
| 2026-07-02 18:11:37 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=d30ad8dde8008887b8e02490288ce778c0cf9e7fe3c1f3fd4cdba408d |
| 2026-07-02 18:13:33 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=7069753a922ddc14b81c81cfd764f0eef214c825ffd6a52fbae37faef |
| 2026-07-02 18:13:41 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=e4e1b9b76e14d2986c52a7ac4c8bcc2a05a37ab2feb0ad1d852ca5933 |
| 2026-07-02 18:13:52 | `file.write` | fdk/tools/build-wiki-graph.py · tool=Edit · actor=agent · prev=c558957e2eaeca6a53d6e4b452df3f37e1d9768012924f6bbb8629f11 |

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

## 2026-07-02 — fdk — wiki-core v2 buoc 4-6 (day som theo quyet dinh user)
- Stale-propagation cap=1 buoc (G2, test A-B-C + chu trinh + tuoi-lai; 9.8ms/lan ghi tren 63 trang). Skill /wiki-room (G3: depth cap=1, budget, circuit breaker) — register du marketplace/LOOP_MAP/AGENT/CLAUDE, skill-registry all agree. Wiki-graph HTML: build-wiki-graph.py (13ms) -> html/wiki-graph-fdk.html + wiki-graph-llmwiki.html. Problem-tree p-11 -> solved 3/3.

## 2026-07-02 — fdk — wiki-graph het flat
- build-wiki-graph.py ve them [[wikilink]] than bai = canh mem net dut (khong gia ngu nghia); them 12 relations co kieu that cho 6 trang loi (validator bat 1 cross-wiki dangling -> go). Demo stale: sua rule-registry -> fdk-dev-strategy stale (badge S trong graph). fdk 121 canh / llmwiki 18 canh, build 5ms/3ms.
