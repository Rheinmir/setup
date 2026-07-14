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
| 2026-07-12 23:43:54 | `file.write` | .github/workflows/harness.yml · tool=Edit · session=cacb3b15 · actor=agent · prev=a123c2283f5ed250a2f5e7cc93c37fd11d63c9 |
| 2026-07-12 23:44:15 | `commit.reconcile` |  · actor=system · agent_n=1 · human_n=0 · prev=98b1c1b25afe4a34d29259cc13cd8df69eafd4dffc8e52b3cae5ba9dad27b99b · h=910b |
| 2026-07-12 23:51:19 | `file.write` | fdk/docs/fresh-install-gate.md · tool=Edit · session=c82ce215 · actor=agent · prev=910b823db67d42f430985c8196c910cebac7b |
| 2026-07-13 00:19:58 | `commit.reconcile` |  · actor=system · agent_n=0 · human_n=1 · human=['fdk/skills.provenance.json'] · prev=6ba59805b934185429a1eb5bf80e496e7e |
| 2026-07-13 13:26:35 | `file.write` | fdk/docs/fresh-install-gate.md · tool=Edit · session=c82ce215 · actor=agent · prev=8614d2867956a79a98688353708ac559ba7c9 |
| 2026-07-13 16:41:13 | `file.write` | harness/downstream-contract.yaml · tool=Write · session=c82ce215 · actor=agent · prev=a53b35fef94b1cd14b458c18e1ae838d3d |
| 2026-07-13 16:41:37 | `file.write` | harness/scripts/fresh-install-smoke.sh · tool=Edit · session=c82ce215 · actor=agent · prev=ede8cef81dacb484bc9c9d6848742 |
| 2026-07-13 16:43:24 | `file.write` | fdk/docs/fresh-install-gate.md · tool=Edit · session=c82ce215 · actor=agent · prev=c417049ea26dee89cd55e504bdb0576798d08 |
| 2026-07-13 16:50:13 | `file.write` | llmwiki/wiki/sources/ISSUES.md · tool=Edit · session=c82ce215 · actor=agent · prev=80e7d37fadcb71646794fe4023a5d27abad00 |
| 2026-07-13 16:53:26 | `file.write` | llmwiki/wiki/sources/ISSUES.md · tool=Edit · session=c82ce215 · actor=agent · prev=e0d7fc02bd570d057c75513ea54fe6699f48d |
| 2026-07-13 16:57:38 | `file.write` | llmwiki/wiki/sources/ISSUES.md · tool=Edit · session=c82ce215 · actor=agent · prev=eed6e45e032a7297c7ef69e06814befce18f6 |
| 2026-07-13 16:58:20 | `file.write` | llmwiki/wiki/sources/ISSUES.md · tool=Edit · session=c82ce215 · actor=agent · prev=3334d1767fd29b16ee9096a66bebb0ea5ea6b |
| 2026-07-14 01:17:33 | `file.write` | harness/downstream-contract.yaml · tool=Edit · session=c82ce215 · actor=agent · prev=2c61f3df3006349fcfb33c5b8702ff7b80d |
| 2026-07-14 01:17:43 | `file.write` | harness/scripts/fresh-install-smoke.sh · tool=Edit · session=c82ce215 · actor=agent · prev=7405cffcf2d4d70df648066dcd00d |
| 2026-07-14 01:19:05 | `file.write` | fdk/docs/fresh-install-gate.md · tool=Edit · session=c82ce215 · actor=agent · prev=dfbe4c1d6a96b18aa98cbe8e17efdb49275a1 |
| 2026-07-14 09:39:34 | `file.write` | harness/poc-vendor-neutral/install.sh · tool=Edit · session=c82ce215 · actor=agent · prev=09fb1bad1f310e16657eb07c56a104 |
| 2026-07-14 09:39:43 | `file.write` | harness/downstream-contract.yaml · tool=Edit · session=c82ce215 · actor=agent · prev=9fb3cd9a3bd0d7319f8969d1835b0c3b6f4 |
| 2026-07-14 09:43:43 | `file.write` | harness/scripts/capability-stamp.py · tool=Write · session=c82ce215 · actor=agent · prev=776e15fbfdb3bab2a1cd2a793014ef3 |
| 2026-07-14 09:44:02 | `file.write` | fdk/tools/medic.py · tool=Edit · session=c82ce215 · actor=agent · prev=ff298eec6ca74341b303f9046fc74c72cc29382380744dff0 |
| 2026-07-14 09:44:07 | `file.write` | fdk/tools/medic.py · tool=Edit · session=c82ce215 · actor=agent · prev=0d12a9984c18390cd6c6ef89346af677d97987e13f3406547 |
| 2026-07-14 09:46:11 | `file.write` | fdk/docs/fresh-install-gate.md · tool=Edit · session=c82ce215 · actor=agent · prev=23e0874708e15019cb0f7776bdd442be5a0f3 |
| 2026-07-14 09:54:30 | `file.write` | harness/poc-vendor-neutral/install.sh · tool=Edit · session=c82ce215 · actor=agent · prev=91629bf081ba6b6f6b0a27c1bc81a3 |
| 2026-07-14 09:55:57 | `file.write` | fdk/docs/fresh-install-gate.md · tool=Edit · session=c82ce215 · actor=agent · prev=6dd5ca3435aa993a417da377b165fa51cb1e3 |
| 2026-07-14 10:04:52 | `file.write` | harness/scripts/capability-stamp.py · tool=Edit · session=c82ce215 · actor=agent · prev=93f22057d17c0fac8ae76aec6e255b2f |
| 2026-07-14 10:05:04 | `file.write` | harness/scripts/capability-stamp.py · tool=Edit · session=c82ce215 · actor=agent · prev=ec7b2c2e00fb8e4890186ad0d569f4e7 |
| 2026-07-14 10:06:51 | `file.write` | harness/scripts/capability-stamp.py · tool=Edit · session=c82ce215 · actor=agent · prev=51025d9e5f027c3f65e425180bbbf22c |
| 2026-07-14 10:07:02 | `file.write` | harness/scripts/capability-stamp.py · tool=Edit · session=c82ce215 · actor=agent · prev=4ea76eb165222ec9e122d32ddd5602a0 |
| 2026-07-14 10:09:49 | `file.write` | fdk/docs/fresh-install-gate.md · tool=Edit · session=c82ce215 · actor=agent · prev=384139efab0cf93e49d2c3368caff77bd09c8 |
| 2026-07-14 13:23:36 | `file.write` | llmwiki/wiki/sources/draft/110726-shipped-vs-documented-parity.md · tool=Write · session=c82ce215 · actor=agent · prev=6 |
| 2026-07-14 13:24:12 | `file.write` | harness/scripts/fresh-install-smoke.sh · tool=Edit · session=c82ce215 · actor=agent · prev=159e26e39aa2ccb52e4b5b0ea41af |
| 2026-07-14 13:25:51 | `file.write` | fdk/docs/fresh-install-gate.md · tool=Edit · session=c82ce215 · actor=agent · prev=fafdf5059f6b3308e3deef2086a485e995377 |
| 2026-07-14 13:26:21 | `file.write` | llmwiki/wiki/sources/draft/110726-shipped-vs-documented-parity.md · tool=Edit · session=c82ce215 · actor=agent · prev=ea |
| 2026-07-14 13:29:36 | `file.write` | harness/scripts/fresh-install-smoke.sh · tool=Edit · session=c82ce215 · actor=agent · prev=c29f03e39896e3727aefe5adbeed1 |
| 2026-07-14 13:30:26 | `file.write` | fdk/docs/fresh-install-gate.md · tool=Edit · session=c82ce215 · actor=agent · prev=de90ec999f113b0b3312d5964604ffb4c0750 |
| 2026-07-14 21:43:56 | `task.new` |  · task=T-260714-01 · title=propose/plan split chuẩn superpowers · state=proposed · actor=agent · prev=901451629e4a18adc |
| 2026-07-14 21:45:33 | `file.write` | llmwiki/wiki/sources/draft/140726-propose-plan-split-superpowers.md · tool=Write · session=36e6562b · actor=agent · prev |
| 2026-07-14 21:47:14 | `file.write` | llmwiki/html/140726-propose-plan-split-seq.html · tool=Write · session=36e6562b · actor=agent · prev=44374ffa3b0816e4c7f |
| 2026-07-14 21:47:49 | `file.write` | llmwiki/html/140726-propose-plan-split-seq.html · tool=Edit · session=36e6562b · actor=agent · prev=2d410078f69274cf6ea4 |
| 2026-07-14 21:47:56 | `file.write` | llmwiki/wiki/sources/draft/140726-propose-plan-split-superpowers.md · tool=Edit · session=36e6562b · actor=agent · prev= |
| 2026-07-14 21:48:27 | `file.write` | llmwiki/wiki/sources/draft/140726-propose-plan-split-superpowers.md · tool=Edit · session=36e6562b · actor=agent · prev= |

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

## 2026-07-06 — Proposal: nền chuẩn thiết kế AI-elite chống AI-slop
- Distill `raw/design-tip-of-someone-on-internet.md` → bảng 13 tip (3 trục: ĐO ĐƯỢC/QUY TRÌNH/PHÁN ĐOÁN).
- `/last30days`: engine binary thiếu (chỉ SKILL.md) → dùng WebSearch thay; agent nền `a5a9a19` đào 8 nguồn design-agent (taste-skill, avoid-ai-design, Anthropic frontend-design, Emil Kowalski motion, high-end-visual-design, Refactoring UI, claude-design-auditor, Meta Astryx) → corpus có nguồn.
- User chốt: gác CẢ HAI đầu ra (HTML framework + skill design) bằng 1 nền chung; 2 tầng nhưng chốt-sửa thì kill 1-shot.
- Ra draft cặp: `sources/draft/060726-design-standard-ai-elite-PLAN.md` + `html/060726-design-standard-ai-elite-PLAN.html`. Index cập nhật. Problem-tree +node p-23 (open, 0/3 trụ). CHỜ DUYỆT — chưa build.

## 2026-07-07 — fdk — sidebar cuộn-không-nén, scrollbar ẩn (feedback)

- Bệnh gốc "co nhỏ quá mức" = flex-shrink nén item khi thiếu chỗ. Fix: nav>*{flex-shrink:0} + overflow-y:auto + ẩn scrollbar hoàn toàn (scrollbar-width:none, ::-webkit-scrollbar display:none).
- Luật vào docs-site-macos § Best Practices ("SIDEBAR: CUỘN chứ không NÉN") + memory; verify Safari.

## 2026-07-07 — fdk — fix vỡ selector CSS: block chống-nén chèn giữa `nav\n.logo`

- User báo "chưa thấy thay đổi" → tự capture (headless Chrome + playwright) mới lộ: block chèn hôm qua rơi GIỮA selector `nav\n.logo` viết tách 2 dòng → parser đọc thành `nav nav>*` (không match gì) + `.logo` mất scope; flex-shrink:0 không ăn, link vẫn nén còn 10px.
- Fix: trả `nav\n.logo` liền lại, chèn block trước rule `nav{position:fixed…}` (anchor không mơ hồ). Verify computed-style thật: h=29px, flexShrink=0, nav scrollable, scrollbar none, cả dark+light.
- Bài học verify: grep thấy rule trong file ≠ rule được parse — phải đo computed style/behavior thật.

## 2026-07-07 — fdk — gỡ note so sánh openwiki khỏi overstack.html (feedback)

- Docs chính thức không bình phẩm sản phẩm khác: xoá note "Đối chiếu thẳng thắn với openwiki" + attribution inline; nội dung mục Wiki giờ chỉ nói năng lực của mình.

## 2026-07-07 — Cài last30days + agent-reach (external-pull) + concept adapt-modes
- Cài engine last30days v3.11.0 (mvanhorn) vào ~/.agents/skills; cài agent-reach v1.5.0 (Panniantong) qua pipx (tarball gh-api, không PyPI). Provenance ghi cả hai (.provenance.yaml + fdk/skills.provenance.json, adapt_mode=external-pull).
- Wiring travel kiểu external-pull: travel-policy.yaml Tầng 1 +research_reach; mirror SKILL.md (last30days→v3.11.0, agent-reach mới); bảng skill CLAUDE.md/AGENT.md +agent-reach.
- Concept mới `adapt-modes`: đặt tên 3 kiểu absorb (HÒA TAN / KÉO NGOÀI / NHÚNG-SỞ-HỮU) + bảng quyết định. Sẽ render docs-site-macos.

- Render docs-site-macos concept adapt-modes → llmwiki/html/070726-adapt-modes.html (mind-map + sơ đồ định vị kéo-thả + theme toggle + 3 section kiểu adapt).

## 2026-07-07 — Chưng cất ponytail (anti-over-engineering) vào overstack
- B1: thêm khối luật luôn-nạp "Cái thang chống over-engineering" vào llmwiki/AGENT.md + llmwiki/CLAUDE.md (ladder 7 bậc + hiểu-bài-trước + root-cause fix + carve-out an toàn + format review 1-dòng/tag/net:-N). Nguồn: 060726-ponytail-distill (ponytail, MIT).
- B2: /lint thêm bước 8 grep marker nợ `shortcut: <trần>, <trigger>` thiếu trigger (canonical skills/lint/SKILL.md → sync-skill.sh ra mirror + bản cài); bước log/neo dời thành 9/10.
- B3: gộp format review 1-dòng vào khối B1 (không đẻ skill song song — /simplify là built-in). fdk-problem-tree +node p-24 (solved 2/3 trụ). medic --ci: 9/9 xanh.

- 2026-07-12 · frontier-scan #3 · quét 5 WebSearch, đối chiếu 8 trục vs kỳ #2 (04/07). Diff: không trục nào tụt hạng, không trục mới; 5 trục Thua/Chớm đều đã có issue mở chỉ còn 3 trục mở GH#10/#11/#12; đính chính: GH#9 (Memory) + GH#13 (Skill-security) đã CLOSED có code thật, kỳ #2 chép nhầm nhãn Thua/Chớm → cập nhật bằng chứng, không raise trùng (R7-f). Bằng chứng mới: Skill-security số liệu cứng (42.447 skill 26.1% lỗ hổng, Antiy 1.184 skill độc ClawHub, 80% lệch khai-báo↔hành-vi), Orchestration mốc scale (Kimi K2.5 100 sub-agent song song), Memory blueprint (Zep/Graphiti temporal KG + BEAM/LoCoMo/LongMemEval), Self-Harness/ComfyClaw/MetaSkill-Evolve (vẫn buộc verifier độc lập). Report: llmwiki/html/overstack-vs-world-30d.html.
