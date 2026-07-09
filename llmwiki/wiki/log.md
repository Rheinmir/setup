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
| 2026-07-07 10:39:51 | `file.write` | llmwiki/html/070726-huong-dan-repo-files.html · tool=Edit · session=d99d8818 · actor=agent · prev=058afd7b60038ab706b04f |
| 2026-07-07 10:40:41 | `file.write` | llmwiki/html/070726-huong-dan-repo-files.html · tool=Edit · session=d99d8818 · actor=agent · prev=d0fb7e144de2983ca0512b |
| 2026-07-07 10:42:15 | `file.write` | llmwiki/html/070726-huong-dan-repo-files.html · tool=Edit · session=d99d8818 · actor=agent · prev=e319bb72ac07a07ad59ce7 |
| 2026-07-07 10:42:57 | `file.write` | llmwiki/html/070726-huong-dan-repo-files.html · tool=Edit · session=d99d8818 · actor=agent · prev=dd7388aed847c9f95432ee |
| 2026-07-07 10:43:47 | `file.write` | llmwiki/html/070726-huong-dan-repo-files.html · tool=Edit · session=d99d8818 · actor=agent · prev=f480eda22037fff64d66e8 |
| 2026-07-07 10:44:36 | `file.write` | llmwiki/html/070726-huong-dan-repo-files.html · tool=Edit · session=d99d8818 · actor=agent · prev=e1810bd062fe4c87ba5958 |
| 2026-07-07 10:45:24 | `file.write` | llmwiki/wiki/sources/draft/070726-huong-dan-repo-files.md · tool=Edit · session=d99d8818 · actor=agent · prev=47844ee314 |
| 2026-07-07 13:26:38 | `file.write` | skills/br/assets/frame-template.md · tool=Write · session=c610b991 · actor=agent · prev=61f8ec0a89dfedc22320d54f3f85f975 |
| 2026-07-07 13:26:59 | `file.write` | fdk/tools/frame-lint.py · tool=Edit · session=c610b991 · actor=agent · prev=aecd2ab33b101dcf4b9daf382ebc1529982c824cb532 |
| 2026-07-07 13:27:02 | `file.write` | fdk/tools/frame-lint.py · tool=Edit · session=c610b991 · actor=agent · prev=a1d7cff62f322af0798b487bc6553fde384002e02599 |
| 2026-07-07 13:27:12 | `file.write` | fdk/tools/frame-lint.py · tool=Edit · session=c610b991 · actor=agent · prev=e870d5d04d1bcf85624722135c10194944d8a4d6cc43 |
| 2026-07-07 13:27:22 | `file.write` | fdk/tools/frame-lint.py · tool=Edit · session=c610b991 · actor=agent · prev=99fe61eca2df54820ff889a379085f76214ec26b5f47 |
| 2026-07-07 13:27:35 | `file.write` | fdk/tools/frame-lint.py · tool=Edit · session=c610b991 · actor=agent · prev=f741b6823aef162f31109a7c0ecf8939e9d9797b67e3 |
| 2026-07-07 13:27:39 | `file.write` | fdk/tools/frame-lint.py · tool=Edit · session=c610b991 · actor=agent · prev=73e5187e0823047319fdb6bf4daa8596ffa6a6083338 |
| 2026-07-07 13:27:54 | `file.write` | fdk/tools/frame-lint.py · tool=Edit · session=c610b991 · actor=agent · prev=4fd51d724df71e519384d7d700451ae9b7a6b4def00e |
| 2026-07-07 13:28:05 | `file.write` | fdk/tools/frame-lint.py · tool=Edit · session=c610b991 · actor=agent · prev=845997d4b709b8be114e36e63bd4e338600c79049868 |
| 2026-07-07 13:28:44 | `file.write` | fdk/tools/frame-lint.py · tool=Edit · session=c610b991 · actor=agent · prev=f05e5ab35c2152a59d4e279d3ececc1b32a2f01b4ebd |
| 2026-07-07 13:28:45 | `file.write` | fdk/tools/frame-lint.py · tool=Edit · session=c610b991 · actor=agent · prev=6462c8aee9a02c3b9dfc83ed735ac2acf189f87b1f4d |
| 2026-07-07 13:29:15 | `file.write` | skills/br/SKILL.md · tool=Edit · session=c610b991 · actor=agent · prev=9cf6db226f8d8c02e3f5e55aa8719cc664dce9c1e83c77581 |
| 2026-07-07 13:29:20 | `file.write` | skills/br/SKILL.md · tool=Edit · session=c610b991 · actor=agent · prev=4d15eb3bbe40d0281cb72f23aeac26a7d79f2ff0dce61f846 |
| 2026-07-07 23:42:39 | `file.write` | skills/br/assets/design-template.md · tool=Write · session=c610b991 · actor=agent · prev=129f347b07c5ce12945561a9a2c8f7a |
| 2026-07-07 23:42:55 | `file.write` | skills/br/assets/spec-template.md · tool=Edit · session=c610b991 · actor=agent · prev=d9ce80fbdd6da063fa96a8c942557f86ba |
| 2026-07-07 23:43:01 | `file.write` | skills/br/SKILL.md · tool=Edit · session=c610b991 · actor=agent · prev=242fb578350d058b7682b2307a8534d2bc083b32af8b8852e |
| 2026-07-07 23:43:08 | `file.write` | skills/br/SKILL.md · tool=Edit · session=c610b991 · actor=agent · prev=13ffa526d0a956012287ca29da38b09cc863cbb19db825b0d |
| 2026-07-09 07:37:04 | `commit.reconcile` |  · actor=system · agent_n=0 · human_n=1 · human=['llmwiki/wiki/log.md'] · prev=e9cb7301443d40c0c80a22405d5d5dc4b57bbd61d |
| 2026-07-09 07:37:04 | `commit.reconcile` |  · actor=system · agent_n=1 · human_n=0 · prev=e9cb7301443d40c0c80a22405d5d5dc4b57bbd61d179badc406a64569ecf3442 · h=1bb0 |
| 2026-07-09 08:07:13 | `commit.reconcile` |  · actor=system · agent_n=0 · human_n=1 · human=['llmwiki/wiki/log.md'] · prev=1bb0d89229093de847dfed8c5f4498a1d67004eff |
| 2026-07-09 08:11:34 | `file.write` | harness/scripts/loop-runner.py · tool=Edit · session=d99d8818 · actor=agent · prev=0ccfc0ac5555fda80845f2816cc5c76e3dbf0 |
| 2026-07-09 08:12:01 | `commit.reconcile` |  · actor=system · agent_n=1 · human_n=0 · prev=9220bd8ca7c8fdab58bebdb339516426bad74632808522b535eb7a1f26b87202 · h=a44f |
| 2026-07-09 08:12:07 | `commit.reconcile` |  · actor=system · agent_n=0 · human_n=1 · human=['llmwiki/wiki/log.md'] · prev=a44f0f212c8568d75fb669441f32f6ad86fca9da9 |
| 2026-07-09 08:14:56 | `file.write` | harness/scripts/loop-runner.py · tool=Edit · session=d99d8818 · actor=agent · prev=5607d328e7d195db3e582d0c52e6a38c0006b |
| 2026-07-09 08:15:17 | `commit.reconcile` |  · actor=system · agent_n=1 · human_n=0 · prev=aaf55fc682846a0ee5c04c8bcaed34be4198b96c34e6d15f248295dd336d8db9 · h=e71f |
| 2026-07-09 08:15:17 | `commit.reconcile` |  · actor=system · agent_n=0 · human_n=1 · human=['llmwiki/wiki/log.md'] · prev=e71f23bf704f4ee2ae92e20eee10cdf281da532eb |
| 2026-07-09 08:17:17 | `file.write` | harness/scripts/loop-runner.py · tool=Edit · session=d99d8818 · actor=agent · prev=3bd0254d8b8e741ad572ef7bd968f22847b08 |
| 2026-07-09 08:17:43 | `commit.reconcile` |  · actor=system · agent_n=1 · human_n=0 · prev=8ca768cf1cd367e7723247883343e466e95ac813a74c1c2f02de7a60799841f8 · h=0833 |
| 2026-07-09 08:19:44 | `file.write` | fdk/tools/br-queue.py · tool=Edit · session=d99d8818 · actor=agent · prev=083374fd6c3cc216e849ce0a52d5cee685726501a7f971 |
| 2026-07-09 08:19:58 | `commit.reconcile` |  · actor=system · agent_n=1 · human_n=0 · prev=a14c386e5bd66ec6d23eb70af96d000cef492aa0829309b8ef4c5d1049751a8b · h=d92d |
| 2026-07-09 08:41:47 | `file.write` | fdk/tools/br-run.py · tool=Edit · session=d99d8818 · actor=agent · prev=d92d2bba48506a8582bf5a22e383f180e9260797d77845dd |
| 2026-07-09 08:42:09 | `commit.reconcile` |  · actor=system · agent_n=1 · human_n=0 · prev=009dcb09f6f8c312882caa625c436367d0e06d497f2c5e1648ac44a7909eec0e · h=0e53 |
| 2026-07-09 08:44:30 | `commit.reconcile` |  · actor=system · agent_n=0 · human_n=1 · human=['llmwiki/wiki/log.md'] · prev=0e53d94b87667845ac4ed653c7ac4d136f6d58a27 |

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

## 2026-07-02 — propose — council-chon-de-thi-self-index
- Draft: dung app mau NGOAI mau + harass 8 loai vector, de COUNCIL tu chon de thi (chong ludic fallacy ma council seed42 vua neu). T-260702-02. Pair md+seq.html (5 task). Derives-from [[020726-wiki-core-relations]] + [[010726-query-retrieval-eval]].

## 2026-07-03 — council — T1 chọn đề thi self-index
- Council seed42 (roster risk: taleb/ilya/munger/kahneman/aurelius) blind peer-rank → winner Munger (TS plugin-host ~150 file). Đề thi chốt: 10 đòn harass 8 vector + đòn âm tính (chống bịa cạnh) + ca để-trống (đo giới hạn suy-ngầm), ground-truth niêm phong chống ludic fallacy. Report council-report-010-seed42.html. T-260702-02 T1 done.

## 2026-07-03 — last30days+apply — benchmark self-index
- /last30days: cơ chế benchmark chuẩn = gold-edge interval-overlap P/R/F1 (ContextBench), triplet-F1 + hallucination/omission-rate per-triple + held-out fixed-seed (Unified-KG-Benchmark), MRR/Hits@k, LLM-judge-calibrate-với-người. Áp vào scorer plugin-host/score.py (edge P/R/F1 + hallucination-rate + negative-control + limit tách riêng, verdict gate F1>=0.7 & neg=PASS & halluc<=0.15). Kiểm chứng: engine-tốt giả→PASS 1.0, xấu→FAIL. App mẫu T2 42 file reseal hash 65f51295. T-260702-02 T2 done, T5 scorer ready.

## 2026-07-03 — T3/T4 — chạy engine thật self-index
- adapter.py onboard app→wiki-shape, gọi build-wiki-graph.py THẬT (scan+enrich_code), map→engine-edges.json. score.py chấm mù (seal verified): core F1 0.842 (P .889/R .8), hallucination .125, negative PASS. Per-capability: MẠNH đọc 5/5 quan hệ frontmatter khai tường minh + không bịa cạnh negative + không đối-xứng-hóa contradicts; MÙ imports/touches code TS (enrich_code chỉ .py); thiếu cờ cycle/quarantine trong graph-builder; trích [[NotALink]] từ code-fence (1 false-pos). Xác nhận council seed42: robust ở mặt thiết kế, giòn ở đuôi ngoài-mẫu → chưa anti-fragile. 3 defect chờ đẩy failure-flywheel (T5). T-260702-02 T3+T4 done.

## 2026-07-03 — T5 — distill benchmark self-index
- Report HTML 030726-self-index-benchmark-report.html (glass, KPI + bảng năng lực + 3 defect + kết luận robust-chưa-anti-fragile + phạm vi no-silent-cap). 3 defect vào failure-flywheel (coverage-gap ×2: mù code-TS, thiếu cờ cycle/quarantine; hallucination ×1: wikilink không strip code-fence). Cập nhật concept wiki-core-relations mục "Kiểm chứng NGOÀI-MẪU". T-260702-02 T5 done → proposal 5/5 task xong.

## 2026-07-03 — plan Mảnh A-C — engine tự-index self-contained
- Vá 3 defect benchmark KHÔNG phụ thuộc SW ngoài. Mảnh A: fdk/tools/code_imports.py (stdlib-only, EXTRACTORS TS/JS/Go/Rust + Python-ast, resolve relative+tsconfig-alias, dynamic→unresolved không bịa) thay vai code-graph MCP; wire vào enrich_code đa-ngôn-ngữ. Mảnh B: strip code-fence/inline trước WIKILINK_RE. Mảnh C: detect_cycles DFS + _frontmatter_ok quarantine. Chấm lại: recall 1.0 (11/11), provably-false 0, negative PASS, 9/10 đòn full-pass (đòn 8 touches chờ Mảnh D). Đòn 1 1/3→3/3, 2 1/2→2/2, 3 forbid pass, 4 3/4→4/4, 7 2/3→3/3. Smoke graph thật OK 129 node. Grep: 0 dependency ngoài. Scorer sửa: precision không tính từ gold-thưa (import thật vắng gold ≠ bịa); đo recall + provably-false.

## 2026-07-03 — plan Mảnh D — impact touches self-contained
- impact_reverse(target,edges,rel=imports,cap=1) trong build-wiki-graph.py: touches lan-truyền = reverse-imports 1-hop trên import-graph (cùng cap=1 propagate_stale, self-contained, không hook/tool ngoài). Đòn 8 0→1/1 (khớp 3 dependents thật: di/container, index barrel, wiring). Chấm CUỐI: 22/22 check, 10/10 đòn full-pass, recall 1.0, provably-false 0, negative PASS, seal verified. Smoke graph thật OK 129 node 177ms. plan.md A-D done. Ground-truth sửa 2 lần (setup.md link prose không backtick; đòn8 thêm index.ts barrel là dependent thật) — engine đúng, gold thiếu.

## 2026-07-03 — full 1 luồng + graph HTML
- run.sh gói full pipeline: generate → adapter (engine thật scan+enrich_code đa-ngôn-ngữ + cycle + quarantine + impact + RENDER build_static) → score. Graph HTML thật llmwiki/html/030726-plugin-host-graph.html (34 node, đủ 7 loại vector: imports/derives-from/supersedes/contradicts/implements/depends-on/wikilink, offline 0-JS, self-path R16). Chấm: 22/22, 10/10 đòn, recall 1.0, provably-false 0, VERDICT PASS. Link graph vào report 030726-self-index-benchmark-report.html.

## 2026-07-03 — sửa kỷ luật: graph qua CLI thật (như overstack vào project)
- Phá kỷ luật trước đó (hand-render build_static ra doc dated 030726-plugin-host-graph.html) → XOÁ. Thêm 2 flag CLI THẬT vào build-wiki-graph.py: --code-root (seed node code từ thư mục → dựng import-graph đầy đủ, opt-in default OFF nên graph framework không đổi) + --json (dump nodes/edges/cycles cho eval). run.sh giờ: generate → onboard (wiki-shape như overstack) → CHẠY CLI THẬT build-wiki-graph.py sinh plugin-host/wiki-graph.html chuẩn + graph.json → map_score. Vẫn 22/22, 10/10, recall 1.0, VERDICT PASS. Refresh canonical llmwiki/html/wiki-graph.html + wiki-graph-static.html qua CLI (129 node, engine backward-compat). Harness (score.py) tách khỏi plugin-host/ (app pure, tách-1-bản sạch).

## 2026-07-03 — fdk — ràng buộc rồi đo (feedback loop self-index)
- Meadows: biến fix Mảnh A-D từ vá-một-phát thành vòng phản hồi bound+measured. ĐO: baseline.json đóng băng (recall 1.0, provably_false 0, 10/10 đòn, verdict PASS). RÀNG BUỘC: check.py regress bất kỳ chiều (recall↓/provably-false↑/full-pass↓/negative FAIL/seal vỡ) → exit≠0. run.sh xoá result.json+graph.json cũ đầu run (chống gate đọc stale → false-green — lỗ hổng đã phát hiện & vá). CHỨNG MINH cắn thật: bỏ code_imports.py → engine degrade mượt recall 0.8 → check ❌ REGRESS. Vá guard build-wiki-graph --code-root (if code_root and code_imports) cho fail-open đúng. problem-tree p-12 (con p-11) partial 2/3 trụ. CÒN full: promote eval khỏi scratchpad + wire fdk-gate/CI (cần duyệt) + skill bọc.

## 2026-07-03 — fdk — rà rule "có cắn không" + overstack generator
- Câu hỏi "rà tất cả luật có cắn chính xác không": harness-doctor.py ĐÃ tồn tại (fire-drill BAD/GOOD fixture per validator) nhưng chỉ phủ 5/17 rule (R1/R2/R5/R7/R9). 12 rule chưa chứng minh cắn (hook_event/process_gate/repo_gate/deny_write/vài content_check). Chạy NGAY lộ 2 live: proposal_complete.py DRIFT (hooks-copy vs harness-src), pre-commit chưa cài. → problem-tree p-13 (open). overstack.html: build-overstack-docs.py ĐÃ live-from-disk + wired stop.py; fix orca-issue vào LOOP_GROUPS.orchestrate.ops → regen, --check xanh (0 dẫm module cũ). Thiết kế mở rộng harness-doctor 4 tầng phủ 17/17 — chờ duyệt để build.

## 2026-07-03 — fdk — medic (cổng sức khoẻ tổng) + kim chỉ nam hub
- Kim chỉ nam 2 (hub 1-tên/mô-tả-phạm-vi/TL;DR+recap/transparent) ghi vào skills/fdk/SKILL.md (travel, cạnh Meadows) + sync. medic: fdk/tools/medic.py (stdlib, 6 probe compose harness-doctor/build-*.py --check/compileall/policy-live, scope-arg, --ci, --list, output có recap+use-case+cấu-trúc). Gõ toàn cục ~/.local/bin/medic + /medic slash skill (new-skill scaffold → SKILL.md thin → register LOOP_MAP/marketplace/AGENT/CLAUDE/LOOP_GROUPS.fdk → sync-skills+registry ✓ → regen overstack/capabilities). medic tự bắt & tôi sửa: capabilities stale, validator drift; medic bắt cú SYNC SAI HƯỚNG của tôi (R7 rail-đen 4/5) → khôi phục hooks-copy. Verdict KHOẺ (2 warn nợ: coverage 5/17, pre-commit off). Proposal 030726-medic (T1-2 done, T3-5 pending) pair md+seq.html. problem-tree p-13 partial 2/3 trụ. Memory: fdk-hub-ux-principles + medic-last-line-of-defense.

## 2026-07-03 — council — whiteboard skill: embed vs tách (UX)
- Council design roster (rams/ada/linus/taleb/laozi) đánh giá "whiteboard quan hệ skill vào overstack.html hay tách". Winner Linus (embed-block-tự-chứa 1.33), á quân Taleb (tách). Chairman hoà giải: cả hai đồng thuận whiteboard = ARTIFACT TỰ CHỨA sinh từ registry (không nhét logic vào build-overstack-docs). CHỐT: TÁCH file riêng skill-whiteboard.html + link mỏng từ overstack; bắt đầu TỐI GIẢN (sơ đồ tĩnh, cỡ theo cấu trúc/số-skill-con, KHÔNG bịa usage); tái dùng build-wiki-graph.py + LOOP_GROUPS + build-skill-search metadata; nâng tương tác sau khi có log thật (Laozi). Report council-report-012-seed42.html.

## 2026-07-03 — build — skill-whiteboard (bản đồ quan hệ skill, tĩnh)
- Thực thi quyết định council 012: fdk/tools/whiteboard-skill-map.py → llmwiki/html/skill-whiteboard.html (tĩnh, self-contained, 68 skill / 4 loop-hub, cỡ hub theo CẤU TRÚC số-skill-con KHÔNG bịa usage, ◆ đánh dấu skill bao trùm, mô tả phạm vi từ SKILL.md frontmatter LIVE, có --check anti-drift). Link mỏng "🗺️ Xem bản đồ quan hệ skill đầy đủ →" thêm vào overstack qua generator (không hand-edit). Tương tác (tìm/lọc/route) để sau khi có nhu cầu+log (Laozi). Bắt đầu tối giản đúng chốt.

## 2026-07-03 — fix(council) — report hiện tên uỷ viên thay vì seat-N
- Bug: render map author→tên bằng persona-id nhưng author=seat-id → rơi 'seat-N', mất lens (phong cách). Vá gốc council.py _load_persona_meta: index thêm theo seat-id từ config.seats[].persona. selftest OK. Re-render → council-report-013-seed42.html hiện Dieter Rams/Ada Lovelace/Linus/Nassim Taleb/Lão Tử + lens. problem-tree p-14 solved (harness). Mọi report tương lai tự đúng.

## 2026-07-03 — redesign(council-report) + council(release) + patch note v1.0.5
- Redesign template render_report_html (council.py): font Việt-an-toàn (bỏ Iowan/Palatino vỡ dấu → Georgia/Cambria), .plens có style riêng (italic accent, sans Việt), lead nổi bật + border-left accent per-card chống wall-of-text. selftest OK. Re-render → council-report-014-seed42.html.
- Council release (roster taleb/linus/munger/kahneman/rams): đồng thuận GATE = gitignore scratchpad + patch note trung thực (medic 5/17 KHÔNG suy toàn hệ, benchmark N nhỏ) TRƯỚC rồi push. 2 push-after / 3 hoãn-until = cùng gate. .gitignore += scratchpad/ (co-council đã track → cần git rm --cached lúc tag). RELEASE-v1.0.5.md (v1.0.4+1) với Known-limitations thẳng.

## 2026-07-03 — whiteboard-graph + skill /ship + council i18n
- skill-whiteboard: dựng LẠI thành ĐỒ THỊ qua chính engine build-wiki-graph (build_html JS force-layout) thay layout thẻ tĩnh — user muốn giống wiki-graph. Node loop-hub + skill, cạnh contains(loop→skill) + orchestrates(skill-bao-trùm→con), rel màu nhét in-memory. 42KB, 72 node, SVG cạnh.
- skill /ship (dev-loop): workflow chốt push/release — checklist medic-gate/git-sạch/selftest/version-x.x.x+1/patch-note-trung-thực; 2 mức push|release; STOP chờ duyệt trước side-effect. Register đủ mặt (sync-skills+registry ✓).
- council report i18n: KPI "Winner/Most contested"→"Quán quân/Gây tranh cãi nhất"; bảng "Blind/Mean rank/Judge ranks"→"Nhãn ẩn/Điểm hạng TB/Hạng từng GK"; "Reveal map"→"Bản lộ danh"; blindtag/mc/winner cells→Việt. (council.py đang được refactor sang module cor song song.)

## 2026-07-03 — orca-eval — distill phiên phân mảnh làm stress-test /fdk
- Scan session hiện tại (30 prompt, 8 chủ đề, 6 vòng design). Report draft/orca/030726-eval-report.md: 5 best-practice (fix-at-engine, medic-last-line, điểm-trung-thực, council-chọn-đề, kim-chỉ-nam-travel) + 8 friction (F1 hand-author, F2 reinvent, F3 regression, F4 sync-sai-hướng, F5 quên-regen, F6 lẫn-ngôn-ngữ, F7 over-design, F8 quên-verify) + 7 action A1-A7. Council (linus/taleb/munger/rams/laozi) đánh giá: winner Lão Tử — đòn bẩy = medic-GƯƠNG-SOI-cuối-phiên (khi đụng framework), giữ 2 cổng tự-cắn A1+A7, gộp A4/A5, hấp thụ A3 vào A7-coverage, A2/A6 thành phụ lục, KHÔNG 7 luật rời. report council-report-020-seed42.html. Bước tiếp: propose hook framework-touch-detector + mở rộng medic 17/17.

## 2026-07-03 — council(tư vấn) — hạ tầng retrieval có hữu ích nếu agent không query?
- Nghi vấn: agent ít gọi /query (31% edit "mù", cận dưới vì grep không đếm) → hạ tầng vô dụng? Council (kahneman/taleb/munger/ada/linus). Chốt: query-rate là ĐO NHẦM (vanity/Goodhart). Tách 3 lớp: wiki-content=tiền-đề (grep trúng nhờ nó tồn tại) GIỮ; code-graph/quan-hệ-phi-cục-bộ = giá trị BỀN grep-không-thay GIỮ+đầu-tư; /query-skill = lớp-bọc → HẠ xuống optional. ĐO reinvent-rate + cross-break + harm-when-missing + retro-test; BỎ query-rate; KHÔNG ép query (theater). Hành động: retro-test 31% mù trước; code-graph entrypoint rẻ 1-lệnh; retrieval tự-surface (hook pre-edit cảnh báo cross-break). report council-report-022-seed42.html.

## 2026-07-03 — propose — milestone v1.0.6 (mở nợ sau release)
- Sau release v1.0.5, mở milestone sau: proposal 030726-milestone-v106-harden (T-260703-02) gộp 4 nợ thành roadmap 6 task. Context = council-020 (medic gương-soi + A1/A7 + hấp thụ A3) + council-022 (query: đừng ép, đo reinvent/cross-break, hạ /query, code-graph rẻ, tự-surface) + issue #4 (logger). Tasks: T1 medic 17/17, T2 framework-touch hook, T3 A1 generator-probe, T4 code-graph entrypoint rẻ, T5 retrieval tự-surface (pre-edit cross-break), T6 đo reinvent/cross-break (không query-rate) + rà issue #4. Cặp md+seq.html (6 diagram). Bằng chứng cấp thiết: bug R7-f dark-rail vừa lọt medic 5/17 ở release. DỪNG chờ duyệt.

## 2026-07-03 — provenance — bản ghi phiên b73d2c47
- User lo: session mới không tra được chức năng sinh từ phiên nào + context gì. Trace hiện HỞ: ledger.jsonl ghi session cho WIKI-file nhưng code (events.jsonl) KHÔNG có session, không neo context. Giải: sources/030726-session-provenance.md — neo session-id → 7 chức năng → context (council report + proposal) → commit f71e17f. Queryable: query medic → tới đây. Systematic auto-capture = thêm T7 vào milestone v1.0.6.

## 2026-07-03 — last30days+council — bộ nhớ thứ cấp (context vụn)
- Issue #5: wiki chỉ lưu proposal, sửa+context vụn mất. /last30days: cộng đồng dùng markdown-first (AGENTS.md 60k), event-sourced journal (PROJECTMEM), ADR/MADR immutable, bỏ RAG. Council (ada/taleb/linus/rams/munger): kiến trúc 3 tầng THÔ(auto scratch-log.jsonl tách ledger, append-only, vì-sao optional, ngưỡng commit/save) → JOURNAL-DISTILL(markdown-ngày, người promote) → WIKI(curated). Mâu thuẫn rotate-vs-không-mất giải bằng GIT (rotate view, history bất biến). 3 khe Linus: events.jsonl +session, VIEW gom session/feature reuse problem-tree/wiki-graph 2-zoom, chỗ ghi 1-dòng vì-sao. Reuse KHÔNG RAG/SQLite. Judgment-at-READ. report council-report-024-seed42.html.

## 2026-07-03 — propose — bộ nhớ thứ cấp 3-tầng (issue #5)
- Proposal 030726-secondary-memory (T-260703-03) từ council-024 + /last30days + issue #5. 4 task: T1 hook auto scratch-log.jsonl (append-only, why optional, tách ledger), T2 events.jsonl +session, T3 VIEW memory-map 2-zoom reuse build-wiki-graph (không RAG), T4 distill auto session-provenance (hấp thụ T7 v1.0.6, không xoá thô). Nguyên tắc: git=lưới an toàn không-mất, judgment-at-read, reuse không SQLite/RAG. Cặp md+seq.html (4 diagram). DỪNG chờ duyệt.

## 2026-07-03 — implement — secondary-memory T1+T4 (scratch-log)
- harness/scripts/scratch-log.py: T1 note (append context vụn → scratch-log.jsonl TRACKED, git giữ vĩnh viễn, why optional) + T4 distill (gom scratch+ledger theo phiên → sources/DDMMYY-session-provenance.md, KHÔNG xoá thô). Test: ghi 3 why phiên này → distill ra 030726-session-provenance.md (auto thay bản tay; bản tay giàu vẫn trong git ff7c47e — chính nguyên tắc không-mất). CÒN: T2 (events.jsonl +session — cần hook truyền session-id), T3 (memory-map 2-zoom reuse build-wiki-graph). scratch-log.jsonl KHÔNG gitignore (khác events.jsonl).

## 2026-07-03 — propose — narrative-as-data + medic narrative-drift probe

- 2026-07-03 raise-issue x5 (frontier gap) → ledger draft + ISSUES.md + GH#9-13. Concept fdk/wiki/concepts/frontier-gap-scan.md. Report overstack-vs-world-30d.html chuyển vào llmwiki/html/.
- 2026-07-03 bổ sung mục "Repo/paper tham khảo" vào 5 issue frontier gap (ledger + comment GH#9-13).

## 2026-07-04 — fdk issue#9 — memory episodic + vector + temporal (4/4 tầng nhớ)

- mem-rank.py: thêm `episode` subcommand + temporal `ts`/`supersedes` + `--kind-filter`; self-test mở rộng (episodic + supersede).
- Skill mới `record-episode` (wiki-loop) ghi session episode; wire Tầng-0 truy hồi ngữ nghĩa vào `query` + `wiki-room`.
- Eval: `mem-proxy.py` (sinh output episodic tất định, không model) + fixtures + 2 golden episodic + `episodic-baseline.json`, gate qua medic `p_eval`. hit@k 2/2.
- Đăng ký: sync-skills mirror, CAPABILITIES, bảng AGENT/CLAUDE. Problem-tree node p-17 (solved 3/3 trụ).

- 2026-07-04 — plan cho issue #6 Foundation: ghi `030726-foundation-section-PLAN.md` (fable), index-sync.
- 2026-07-04 — GH#6 Foundation: tạo harness/foundation.yaml + template seed; generator tab "Nền tảng" derive; medic probe p_foundation; seed 2 installer; regen overstack.html. Ledger status→done.
## 2026-07-04 — fdk (GH#13) — skill-resolve ambiguity + supply-chain
Giải issue `030726-skill-resolve-supplychain` (trục #5 frontier-gap-scan, Chớm→có cơ chế). 3 cơ chế:
- `new-skill.py`: cảnh báo TRÙNG NĂNG LỰC lúc scaffold — tái dùng BM25 của `build-skill-search.py`, ngưỡng 12.0 (calibrate: biến thể trùng ≈26–44, skill lạ ≈7); flag `--strict` chặn cho CI. Chỉ cảnh báo, không chặn biến thể hợp lệ.
- Golden `skill-resolve-eval.py` + 18 case `sources/evals/skill-resolve/` (cặp nhập nhằng thật) — hit@1 18/18, baseline chốt, `--check` exit 2 khi regress; gắn CI `skills-sync.yml`.
- Skill+tool `skill-provenance` (`fdk/tools/skill-provenance.py`, store `fdk/skills.provenance.json`) — ghi nguồn+sha256, `check --ci` chặn MODIFIED/UNTRACKED; backfill 74 skill = local-authored. Bổ trợ orca-sec-scans.
Đăng ký: LOOP_MAP + marketplace + AGENT/CLAUDE + LOOP_GROUPS mind-map; regen overstack.html + skills.search.json + CAPABILITIES. Ledger status→resolved, index +18, concept trục #5 cập nhật.

## 2026-07-04 — fdk issue#18 — pre-commit chậm >2ph → tách tầng L2/CI

- Gốc (Meadows): 25 hook nhân bản trọn CI mỗi commit → stash + spawn nặng. Đưa L2 về đúng vai (concept enforcement-floor): chỉ content-validator theo file-đổi.
- `.pre-commit-config.yaml`: 25→12 hook nhanh; `pre-commit run` 0.16s (trước >2ph). Fire-drill nặng dời sang CI "repo health" (đã có) + thêm `policy-converters-drift` vào harness.yml (chưa có → không mất phủ).
- Đường cứu index-hỏng-khi-kill ghi vào comment config. Ledger done, problem-tree.

## 2026-07-04 — fdk issue#14 — overstack.html audit (đợt 1+2)

- Mọi fix ở generator build-overstack-docs.py (không sửa tay HTML), --check pass.
- Đợt 1 sự thật: "Bốn lớp"→"Ba lớp CHẶN"+giải thích L3 trống; slogan validator khớp FACT (rule enforce bởi validator+hook); BNAL nhãn tự khớp; bảng rule render 1 lần (bỏ lặp ×2); LOOP_GROUPS +ovs-notes/frontier-scan; GH#8 skill-usage auto-derive.
- Đợt 2 UX: dark mode (prefers-color-scheme), .table-wrap overflow-x (class trước KHÔNG có CSS), mind-map keyboard a11y, skip-link + nav aria-label.
- Problem-tree p-20. Đợt 3 biên tập defer (ngoài DoD).

## 2026-07-06 — fdk — wiki-sync distill openwiki (code→wiki drift)

- Đối chiếu openwiki (langchain-ai): distill 3 cái hay, nấu lại — 4 trục họ hơn nay phủ đủ.
- Mới: harness/scripts/wiki-sync.py (neo .last-sync.json, --check no-op 0 token, cờ code-drift vào stale.json flock; --mark-synced content-hash chống churn) + wiki-sync-test.sh 8/8.
- session_start.wiki_drift nhắc đầu phiên (trước early-exit — downstream v4 nhận); /lint bước 0+9 + kỷ luật surgical; /ingest docs-impact-plan; sync 3 bản.
- gen-converters sinh ci/wiki-refresh.yml (cron→PR, degrade tử tế khi không key); wiki-sync.py vào template-manifest.
- overstack.html mục Wiki viết lại đầy đủ + đối chiếu thẳng thắn openwiki (kèm giới hạn). Problem-tree p-22 (solved 3/3 trụ).
- Draft: sources/draft/060726-wiki-sync-openwiki-distill.md. Điều kiện ship: test 5 project qua orca-cli trước commit.

## 2026-07-06 — fdk — theme toggle sáng/tối cho HTML (feedback nhắc lần 2)

- build-overstack-docs.py: _DARK_RULES một-nguồn emit 2 khối (@media guard :not([data-theme=light]) + [data-theme=dark]), chip toggle ☀️/🌙 góc phải + localStorage + script chống FOUC trong head; regen overstack.html, verify click thật trên Safari (dark→light OK).
- Mã hoá thành LUẬT: docs-site-macos § "Theme Toggle sáng/tối (REQUIRED)" (snippet chuẩn 3 mảnh), /fdk § Rules (HTML cho người xem phải có toggle). Sync canonical+mirror+bản cài; provenance re-record.
- Memory feedback html-theme-toggle-required (user nhắc 2 lần — không tái phạm).

## 2026-07-06 — fdk — theme switch: nút gạt đáy sidebar (feedback vị trí ×2)

- Bỏ chip icon 2 góc → NÚT GẠT track 50×26 (☀️/🌙 hai đầu, knob trượt, role=switch + keyboard), hàng "Giao diện" sticky đáy sidebar, vách ngăn mảnh, glass cả 2 mode.
- Snippet chuẩn trong docs-site-macos viết lại theo dạng gạt-trong-sidebar; /fdk rule + memory ghi rõ "không chip trôi nổi rải góc, không chen dưới logo".
- Verify click thật Safari: light↔dark mượt, persist localStorage. medic XANH.

## 2026-07-06 — fdk — nâng thang cỡ chữ overstack.html (feedback "co nhỏ quá mức")

- 16 cỡ chữ nâng trong build-overstack-docs.py: nav 12.5→14px (padding 5.5→7px), p 14.5→15.5, ul.s 13.5→14.5, .grp/.logo small/.lbl/chip/kpi/pcard/th đều +1px; regen + verify Safari.
- Luật hoá SÀN CỠ CHỮ: docs-site-macos § Best Practices (≥14px text chính, ≥11px nhãn, cấm <10px trừ badge) + /fdk Rules; memory cập nhật.

## 2026-07-06 — fdk — ĐẢO chiều thang cỡ chữ: compact cho màn 13″ (feedback đúng ý)

- Hiểu ngược feedback trước (đã tăng size) → user chỉnh: phải GIẢM. Hạ 22 cỡ dưới cả mức gốc: nav 12px, body 13.5, lead 14, list/bảng 12.5, nhãn 10–10.5, h2 21, hero clamp(26,4vw,40).
- Luật trong docs-site-macos + /fdk + memory VIẾT LẠI đúng chiều: THANG COMPACT 13″, "dễ đọc = line-height/contrast, không phải font to", ghi chú đã-đảo-chiều-một-lần để không lặp.
## 2026-07-05 — planning GH#15 đợt 2: entity map + step Interview (phiên issue-15-br-k)
- Proposal cặp mới: `sources/draft/050726-ralph-interview-pipeline.md` + `html/050726-ralph-interview-pipeline.html` — 9 entity dây chuyền (RAW→SPEC→QUESTIONNAIRE→ANSWERS→BR→FRAMES→LOOP→MONITOR), khung specs chuẩn S1–S10, hub slash `/br` (interview/compile đợt 1), lens-fill đóng dấu assumed + bảng "Giả định đang gánh" (fail-fast). Chờ user duyệt qua /propose.
- Trước đó cùng phiên: council 031/032 (winner Taleb 1.0) duyệt-có-điều-kiện plan loop thin-slice; problem-tree p-22.

## 2026-07-05 — planning GH#15 đợt 3: đủ 4 step dây chuyền (phiên issue-15-br-k)
- 3 cặp proposal mới theo mẫu step-1: `050726-ralph-slice-frames` (frame schema v0 + frame-lint 5 luật + registry truy ngược, slicer người-trong-vòng-lặp), `050726-ralph-loop-gate` (6 phanh: 4 sẵn + diff-jail + test-hash fail-closed; jail 3 tầng cho claude -p; KILL viết trước; dry-run người gác), `050726-ralph-monitor` (build-line-status.py + /br status — lớp đọc tất định, chống Goodhart). Mỗi cặp .md (máy) + .html (người review). Chờ duyệt qua /propose theo thứ tự phụ thuộc 1→2→3→4.

## 2026-07-05 — THI CÔNG GH#15 step 1–4 + docs site (phiên issue-15-br-k)
- Đồ nghề tất định (selftest xanh): frame-lint.py (5 luật, 6 fixture) · loop-runner.py +2 phanh (diff-jail guard5 + test-hash guard6/PROTECT_VIOLATION exit6, selftest 5→7) · build-line-status.py (monitor 5 trạng thái + --check) · spec-template.md S1–S10.
- Hub skill /br (interview·compile·slice·run·status) đăng ký 6 mặt (mirror·marketplace·AGENT·CLAUDE·LOOP_MAP·LOOP_GROUPS) + regen CAPABILITIES/overstack. medic --ci 0 fail.
- Docs site /docs-site-macos: llmwiki/html/050726-ralph-pipeline-docs.html (mind map + 5 diagram kéo-thả + wiki content + nhật ký deviation). Build-report: sources/draft/050726-ralph-pipeline-build.md.
- Deviation: frame-lint fnmatch (không pathlib **); diff-jail tận dụng no-progress (scope==state); monitor đọc BR.clauses.json; đăng ký cần 6 mặt. Việc kế: end-to-end 1 BR thật + wire adapter claude -p.

## 2026-07-05 — docs-site-macos — br-huong-dan-nguoi-moi
- llmwiki/html/050726-br-huong-dan-nguoi-moi.html: hướng dẫn /br cho NGƯỜI MỚI (6 section, mind map, 4 "ảnh chụp" mockup macOS Terminal+browser dựng từ output thật, FAQ collapse, checklist). Bổ trợ bản kỹ thuật 050726-ralph-pipeline-docs.html.

## 2026-07-05 — GH#15: truy vết frame→code (A+B, theo yêu cầu user)
- loop-runner.py: thêm changed_files (file THẬT frame đổi), commit-on-success gắn frame_id vào WORKTREE branch (không main), baseline_ref; hậu-kiểm scope_clean + FINAL SCOPE SWEEP (mọi termination revert sạch file ngoài scope → changed_files LUÔN ⊆ scope_code) + attempted_out_of_scope (lưu vết ghi lậu). Selftest 7→8 (COMMIT_ON_SUCCESS) + bằng chứng scope_clean. E2E chứng minh: frame tham lam ghi other/config.py+test → PROTECT_VIOLATION, sweep revert về gốc, changed_files=['src/auth.py'], commit=None; ca sạch → commit 'frame(...): [S4.1]'.
- build-line-status.py: cột "file thật đã đổi @commit" + badge ✓/⚠ scope; traceback thêm changed/commit/scope_clean.
- SKILL /br run + docs cập nhật. medic --ci 0 fail.

## 2026-07-05 — GH#15: prompt file + queue resumable (theo yêu cầu user)
- skills/br/assets/revise-prompt.md: FILE PROMPT edit được (template placeholder). fdk/tools/br-revise.py: adapter render template → claude -p (tools bó hẹp); --print xem prompt; selftest tất định (không gọi model).
- br/queue.yaml (mẫu skills/br/assets/queue.example.yaml): danh sách frame, mỗi mục prompt_file HOẶC prompt inline. fdk/tools/br-queue.py: chạy tuần tự, ghi status back sau mỗi mục → chạy lại = bỏ qua done, chạy tiếp (resume). selftest chứng minh resume + inline-vs-file. claude -p là ranh giới verified:false (BNAL).
- SKILL /br run cập nhật. medic --ci 0 fail.

## 2026-07-05 — GH#15: /br run tất định (worktree + revise wired)
- fdk/tools/br-run.py: driver /br run — frame-lint → kiểm tree sạch → tạo git worktree branch br-run/<id> từ baseline → loop-runner với revise TRỎ tới br-revise.py → commit-on-success vào branch (không main) → tóm tắt 1 dòng → ghi run_log_ref vào frame. selftest end-to-end 9/9 (stub revise, không cần model): worktree tạo, changed_files ⊆ scope, scope_clean, commit branch gắn frame message, MAIN không đụng.
- harness/loop-runner.config.yaml revise: comment wiring trỏ br-revise (cmd giữ null = no-op an toàn cho raw run; br-run override per-frame). verified:false chỉ còn ở cú gọi claude -p.
- Mắt xích cuối đã nối: chỉ cần `claude` CLI là bấm chạy thật. medic --ci 0 fail; 6 selftest xanh.

## 2026-07-05 — GH#15 PIVOT theo feedback user: in-place là mặc định, bỏ worktree-per-frame
- Lý do (user): N frame = N worktree = N folder ma; luồng người thường = bật app rà lỗi → trỏ khúc lỗi → tìm frame/prompt phụ trách → sửa prompt → chạy lại frame. Kiểm soát không-phạm-scope bằng HARNESS, không bằng cô lập thư mục.
- br-run.py: default IN-PLACE (một cây duy nhất, app thấy ngay; frame xanh → commit nhánh hiện tại gắn frame_id — mốc revert/blame); --worktree thành opt-in. Selftest 12/12 (thêm 3 case in-place).
- br-find.py MỚI: trỏ file/từ khoá → frame + clause + vị trí prompt (inline queue / prompt_file / template) + lệnh re-run. Selftest 5/5.
- frame-lint R6 exclusive-scope MỚI: 2 frame giẫm cùng file thật → FAIL (đảm bảo "1 lỗi → đúng 1 frame"). Selftest 8 fixture xanh.
- SKILL /br: mode run in-place + mode find. Mọi selftest + medic 0 fail.

## 2026-07-05 — GH#15: SỔ PROMPT tổng br/prompts.md (user sửa tay, không qua model)
- fdk/tools/br-prompts.py: MỘT file br/prompts.md, mỗi frame một mục `## <frame_id>` — user mở, tìm, sửa/thêm nội dung prompt bằng tay. `sync` thêm mục cho frame mới, KHÔNG đè mục đã sửa (selftest chứng minh hand-edit sống sót); mồ côi báo không xoá; heading template demote ### để `##` chỉ còn là frame.
- Ưu tiên runtime (br-revise): sổ prompt > queue inline > prompt_file > template mặc định — selftest "sổ thắng template" xanh. br-find giờ trỏ thẳng vào mục sổ. 8/8 tool selftest xanh.

## 2026-07-06 — GH#15 DREAM-RUN: test trọn luồng bằng bản interview "trong mơ"
- br/dream-demo/ (git riêng, gitignored): app Điểm Danh — docs thô → spec-filled S1–S10 đủ (S7.2 lens-assumed) → interview 001 (questions.html + answers điền) → BR.md + clauses.json (bảng Giả định) → slice 3 frame scope độc lập (frame-lint 6 luật xanh, test-first ĐỎ) → prompts.md (user sửa tay 2 mục) → run.
- Kịch bản chạy: frame-001 SUCCESS (2 vòng, commit gắn frame) · frame-002 stub lởm+tham lam → diff-jail revert docs/hack.txt + ESCALATE 3 vòng → NGƯỜI br-find → sửa sổ prompt → re-run SUCCESS · frame-003 SUCCESS. Nghiệm thu S10.1: 6/6 test xanh. git log mỗi frame 1 commit.
- Gap lộ ra & vá: run-log + run_log_ref sinh SAU commit của loop → tree bẩn chặn frame kế → br-run thêm bookkeeping commit (chore(frame): run-log). R1 chặn agent ghi raw/ đúng luật → demo dùng docs/.
- Trang xem: llmwiki/html/060726-dream-line-status.html.

## 2026-07-06 — GH#15 STRESS-TEST 40 STEP: mini-POS 40 frame chạy trọn dây chuyền
- br/dream-40 (git riêng, gitignored): 40 nghiệp vụ POS, 40 frame scope độc lập, frame-lint 40/40 xanh (1.8s, R6 pairwise 780 cặp). Queue 3 hồi: hồi 1 kẹt f13 (kịch bản) → user br-find + sửa → hồi 2 lộ f15 kẹt THẬT (bug banker's rounding trong solution) + gap nghẽn dòng → hồi 3 chạy nốt: 40/40 done, 40 test xanh, 40 commit frame(fNN), ~18s tổng runtime queue.
- 3 GAP QUY MÔ phát hiện & vá (selftest lại xanh): (1) queue write-back làm bẩn tree chặn frame kế → br-queue commit chore(queue) sau mỗi mục; (2) frame FAIL để diff dở → nghẽn 27 frame sau → br-run lưu .failed.patch + revert scope cho dòng chảy tiếp; (3) br-queue trước gọi loop-runner thẳng (thiếu gate/bookkeeping) → giờ delegate br-run.
- build-line-status thêm toggle sáng/tối + localStorage + chống FOUC (feedback html-theme-toggle-required). Trang: llmwiki/html/060726-dream40-line-status.html.

## 2026-07-06 — GH#15 HARASS-TEST 5×30 frame + council test-plan
- Harass: 5 dự án × 30 frame (~150 frame-run) với 11 kiểu revise xấu + cổng bad-frame + resume. Runner harass_gen/harass_run (scratchpad) soi false-green/tree-dirty/tool-crash không thoả hiệp.
- 3 BUG THẬT fixed + regression selftest: (1) stale .pyc → false verdict → PYTHONDONTWRITEBYTECODE trong loop-runner+frame-lint (selftest stale-pyc guard); (2) tree bẩn cộng dồn (1 kẹt chặn 27) → .failed.patch + revert + bookkeeping; (3) FLAKY/false-green "SUCCESS changed_files rỗng" → guard 7 CONFIRM (br-run --confirm 2, verdict FLAKY exit 7, selftest FLAKY_CONFIRM). loop-runner selftest 7→10, tất cả xanh, medic 0 fail.
- Council 033 (Feynman senior-tester · Linus · Socrates, đồng thuận C>B>A): rủi ro #1 = false-GREEN qua oracle non-hermetic. KIỂM CHỨNG GAP test-hash-transitive của council → đã bịt bởi diff-jail blanket-revert (test thật: revise tamper conftest bắc cầu → revert → NO_PROGRESS). Plan /propose: sources/draft/060726-br-test-harness-plan.md (CI 3 tầng, property/mutation/cassette/chaos, test-independence).

## 2026-07-07 — Distill skill checkpoint-trace từ SHEPHERD (reversible traces)
- Nguồn: SHEPHERD "Reversible Agentic Execution Traces" (arxiv 2605.10913, shepherd-agents.ai) — agent-run = git-like trace, mọi state reachable, effect phân 3 reversibility tier, work là held-proposal (fork→merge/discard). Substrate của ta = git.
- fdk/tools/checkpoint.py (selftest 7 check): save (checkpoint + tier vào .checkpoints.jsonl append-only) · list · rollback <seq|hash> về BẤT KỲ mốc (giữ lịch sử, ghi rollback thành step mới) · tier-gate (reversible→0/compensable→3/irreversible→4, gate trước materialize). Bug tự bắt khi làm: checkout cuốn sổ về quá khứ → fix giữ sổ chỉ-tăng.
- skills/checkpoint-trace/SKILL.md — distill self-contained, ghi công nguồn, KHÁC /br (per-frame) và loop-runner (per-iteration): rollback TOÀN LƯỢT + kỷ luật tier. Đăng ký 6 mặt, regen CAPABILITIES/overstack, medic 0 fail. Demo: trace 3 mốc → rollback #1 khôi phục cây + cảnh báo email irreversible.

## 2026-07-07 — Cứu công việc GH#15 + tool upstream-drift (visibility repo gốc)
- Commit 6082a8f: rescue toàn bộ GH#15 (br pipeline + checkpoint-trace + harass fixes + docs), 48 file, medic --ci gate. Branch trước đó UNCOMMITTED trên nền chậm 28 commit sau origin/orca.
- fdk/tools/upstream-drift.py (selftest 6 check): MỘT lệnh thấy local vs repo gốc — behind/ahead, commit gom theo type (feat/fix ⭐), + cờ ĐỤNG file mình đang sửa (upstream-changed ∩ local committed/dirty) = xung đột merge. Không tự pull.
- Chạy thật: chậm 28 (11 feat + 5 fix), đụng 9 file (build-overstack-docs.py, overstack.html, index/log...). Phát hiện: đã build lệch upstream — theme-toggle upstream đã luật-hoá trong docs-site SKILL, ta tự chế trong build-line-status.py; wiki-sync/travel-policy v4/wiki-graph hữu ích chưa kéo.

## 2026-07-07 — Merge origin/orca (28 commit upstream) vào branch, ưu tiên upstream
- Kéo trọn 28 commit; sau merge: ngang upstream (behind 0, ahead 3). 6 xung đột giải: harness.yml/foundation ← upstream; ledger/log union 2 bên; CAPABILITIES+overstack regen; problem-tree lấy upstream + node Ralph đổi p-22→p-23 (đụng p-22 wiki-sync upstream); bỏ dead-link council-report ephemeral (upstream gitignore council).
- Kéo về hữu ích: wiki-sync (code→wiki drift), wiki-graph.html, travel-policy v4 + global-shared engine (ADR-017), feature-inventory, reachability guard skill→tool, theme-toggle+font-floor rule.
- GH#15 giữ nguyên: br + checkpoint-trace + upstream-drift còn đăng ký; 10/10 tool selftest xanh; medic 0 fail. Test-project dirs (br/dream-demo, br/dream-40, br/harass) gitignored, không track.

## 2026-07-07 — Adapt checkpoint-trace (SHEPHERD) vào /br run: per-frame checkpoint + tier-gate
- Chọn kiểu adapt: wire vào /br run per-frame (standalone không ai nhớ gọi; per-iteration thừa vì loop đã có revert/sweep). Nguyên tắc: KHÔNG double-commit — checkpoint.py thêm mode `record` (ghi sổ trỏ commit CÓ SẴN) + rollback theo LABEL (frame_id, không cần nhớ seq/hash). Selftest checkpoint 7→9.
- br-run: (0) TIER-GATE — frame khai `tier: compensable|irreversible` bị chặn (exit 3) tới khi người `--ack-tier` (SHEPHERD gate-before-materialize); (7) sau run record mốc vào .checkpoints.jsonl + commit sổ ngay (né bài học tree-bẩn harass). Selftest br-run 13→17 (ledger có mốc, tree sạch, gate chặn, ack cho qua).
- Demo dream-demo: record không commit mới; `checkpoint.py rollback frame-001` quay pipeline theo TÊN frame. SKILL br + checkpoint-trace cập nhật; medic 0 fail.

## 2026-07-07 — docs-site-macos — huong-dan-repo-files
- llmwiki/html/070726-huong-dan-repo-files.html: bản đồ tương tác file repo (file NGƯỜI sửa / MÁY sinh / sổ append-only + trace, bảng lệnh↔file, luật hàng rào, checklist). Lần đầu áp spec theme NÚT GẠT + font compact từ upstream. Output-report: sources/draft/070726-huong-dan-repo-files.md.

## 2026-07-07 — Chạy APP THẬT từ frames để test chất lượng (dream-demo) — vòng khép kín trọn vẹn
- run_demo.py: mô phỏng 1 buổi sáng điểm danh (login, khoá 5 lần sai, check-in, báo cáo trễ). BẮT ĐƯỢC lỗi chất lượng THẬT ngoài unit test: bấm nhầm check-in 2 lần → ghi 2 bản, vi phạm S5.2 (clause có trong BR nhưng chưa được test).
- Vòng khép kín diễn đúng thiết kế: chạy app thấy lỗi → br-find "check-in" → frame-002 + mục sổ prompt → NGƯỜI thêm acceptance test S5.2 (đỏ, commit) → re-run frame-002 (stub vai claude, 2 vòng + 2 confirm, scope sạch, commit 233dfd5) → chạy lại app: 1 bản ghi/ngày ✓ ĐẠT, 7/7 test xanh. Checkpoint trace ghi mốc #3.
- Finding #2 ghi backlog BR (không lặng lẽ bỏ): S3.3 khoá "15 phút" thực tế khoá VĨNH VIỄN — cần frame-004-unlock + test thời gian.
- Gotcha lộ ra: test main-block nằm GIỮA file → test thêm sau không chạy ("OK 2 test" giả) — main-block phải ở CUỐI; đáng đưa vào spec-template ghi chú viết test.

## 2026-07-07 — Fix app dream-demo tới CHUẨN PRODUCT (goal-driven autonomous loop)
- Audit app Điểm Danh vs BR → 6 finding (br/dream-demo/br/FINDINGS.md): F-01 khoá vĩnh viễn thay 15' (S3.3), F-02 mật khẩu plaintext (S7.2), F-03 thiếu login log, F-04 input validation crash, F-05 data model thiếu ten/phong_ban (S5.1), F-06 boundary is_late chưa test.
- Fix theo dây chuyền (R6 exclusive-scope: auth→frame-001, checkin→frame-002, report→frame-003): mỗi finding = người viết acceptance test (đỏ) → re-run frame (stub vai claude, 2 vòng + confirm hermeticity, scope sạch) → xanh. 6/6 FIXED.
- Nghiệm thu S10.1: 18 unit test xanh (8 auth + 6 checkin + 4 report) + run_demo.py smoke test 11 invariant chất lượng xanh (hash không plaintext, tự mở khoá 15', input bẩn không sập, dedup ngày, báo cáo đúng, data model đủ).
- Gotcha pipeline lộ ra: sửa BR.md (thêm findings) → R4 orphan mọi frame → phải re-anchor parent_br_hash (BR tiến hoá là hợp lệ; findings nên ở FINDINGS.md riêng, không trong BR đã hash). Known-limitation ghi trung thực: in-memory không thread-safe (trong scope demo S8.1).

## 2026-07-07 — Đưa UI vào dây chuyền: frame-004-ui (trả lời "UI xấu vô frame nào sửa")
- Phát hiện gap: serve.py (UI) là ORPHAN — br-find "serve.py" ra "không frame nào khớp" vì UI dựng làm demo-harness NGOÀI dây chuyền, không có kỷ luật/test.
- Fix đúng cách (không sửa lụi): thêm clause S4.4 (màn hình web, chuẩn UI: token/app-bar/responsive/toggle/a11y) vào BR → slice frame-004-ui (scope serve.py, test tests/test_ui.py, R6 không đè frame nào) → re-anchor.
- Người viết test_ui.py chuẩn UI (8 assert: viewport, design-token ≥8 --var, app-bar thương hiệu, @media max-width, data-theme toggle, aria a11y, 3 flow, status pill) → ĐỎ. Re-run frame-004-ui: iter1 escalate (viewport thiếu nháy) → sửa 1 chỗ → SUCCESS 2 vòng + confirm, scope sạch. UI mới: liquid-glass light-blue, app-bar, thẻ, toggle sáng/tối localStorage, responsive.
- Giờ br-find "serve.py" → frame-004-ui. 4/4 file test xanh (auth/checkin/report/ui). App chạy http://localhost:8790 với UI đạt chuẩn.
- Re-scope trang `llmwiki/html/070726-huong-dan-repo-files.html` (ghi đè): từ guide "5 vùng repo" tổng quát → THUẦN dây chuyền loop-engineering (feedback user "cái dây chuyền ấy"). 6 section mới: bản đồ dây chuyền (diagram raw→interview→compile→slice→run→status+checkpoint) · 5 mode /br · loop-runner 6 phanh · checkpoint & 3 tier khả-đảo · file runtime br/ & lệnh · 6 luật dây chuyền + checklist. Giữ nguyên khung theme (nút gạt dark/light, mindmap, draggable diagram). Cập nhật draft provenance khớp.
- Dây chuyền MỚI `br/payroll/` (PRD Payroll & Timesheet Unicons v2.1 từ raw/): PLANNING xong, CHƯA run. Sản phẩm: mockup.html (10 màn hình, data draft nhúng), 15 CSV data-draft (định mức/DM/tờ trình/bảng công mẫu — gap tự bù đánh dấu ASSUMED), BR.md 26 clause + bảng 10 Giả định đang gánh, 28 frame CỠ NGHIỆP VỤ (frame-lint ALL PASS, p22 khóa-kỳ khai tier compensable), queue 28 pending + prompts.md + line-status. Khác att40 (40 frame = 40 hàm stress-test): payroll slice theo nghiệp vụ trọn vẹn. Điều kiện run: HR xác nhận 10 giả định + viết test thật thay stub đỏ.
