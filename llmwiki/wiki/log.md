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
| 2026-07-17 23:56:50 | `file.write` | harness/scripts/mem-rank.py · tool=Edit · session=246fa7ac · actor=agent · prev=67be331368b257f8207d25b5d68e07c37728db59 |
| 2026-07-17 23:57:38 | `file.write` | skills/qc-code/SKILL.md · tool=Edit · session=246fa7ac · actor=agent · prev=4a580b967282f1b945d0dcea78bec9849d5ef62551b4 |
| 2026-07-17 23:57:51 | `file.write` | skills/orca-issue/SKILL.md · tool=Edit · session=246fa7ac · actor=agent · prev=1b4b5b175882a98a1e2c80520d6f82c581814a48c |
| 2026-07-17 23:58:09 | `file.write` | skills/qc-code/SKILL.md · tool=Edit · session=246fa7ac · actor=agent · prev=9d822bafa6933f812ba5dbb587e6bbdf8a6c5a600fb9 |
| 2026-07-17 23:58:58 | `task.set` |  · task=T-260717-02 · state=completed · note=6 task xong, medic xanh, 2 commit · actor=agent · prev=6d144a29773173618404 |
| 2026-07-18 00:04:45 | `file.write` | skills/hallmark/SKILL.md · tool=Edit · session=246fa7ac · actor=agent · prev=5f1224ee9c36e11e10c8160c5c7dfb3fdcbe49190c0 |
| 2026-07-18 00:17:03 | `file.write` | skills/hallmark/SKILL.md · tool=Edit · session=246fa7ac · actor=agent · prev=ad8474e5a1a673f77eecf4361bf308f3af1ef33c896 |
| 2026-07-18 00:18:26 | `file.write` | llmwiki/wiki/sources/evals/skill-resolve/design-frontend.md · tool=Write · session=246fa7ac · actor=agent · prev=89049a3 |
| 2026-07-18 00:29:57 | `task.new` |  · task=T-260718-01 · title=capability-proof map — checklist năng lực tự soi + tự cộng · state=proposed · actor=agent ·  |
| 2026-07-18 00:31:32 | `file.write` | llmwiki/wiki/sources/draft/180726-capability-proof-map.md · tool=Write · session=246fa7ac · actor=agent · prev=82b4c86a0 |
| 2026-07-18 00:32:39 | `file.write` | llmwiki/html/180726-capability-proof-map-seq.html · tool=Write · session=246fa7ac · actor=agent · prev=f8713173b8b21d714 |
| 2026-07-18 00:47:21 | `file.write` | llmwiki/wiki/sources/draft/180726-capability-proof-map.md · tool=Edit · session=246fa7ac · actor=agent · prev=604a4bcbae |
| 2026-07-18 00:47:37 | `file.write` | llmwiki/wiki/sources/draft/180726-capability-proof-map.md · tool=Edit · session=246fa7ac · actor=agent · prev=91d4dc4144 |
| 2026-07-18 00:48:02 | `file.write` | llmwiki/html/180726-capability-proof-map-seq.html · tool=Edit · session=246fa7ac · actor=agent · prev=7867dd17b9254da91f |
| 2026-07-18 00:48:13 | `file.write` | llmwiki/wiki/sources/draft/180726-capability-proof-map.md · tool=Edit · session=246fa7ac · actor=agent · prev=47d3bd52b0 |
| 2026-07-18 00:48:18 | `file.write` | llmwiki/wiki/sources/draft/180726-capability-proof-map.md · tool=Edit · session=246fa7ac · actor=agent · prev=61e2165b93 |
| 2026-07-18 00:48:22 | `file.write` | llmwiki/wiki/sources/draft/180726-capability-proof-map.md · tool=Edit · session=246fa7ac · actor=agent · prev=6c4e3c5853 |
| 2026-07-18 00:48:30 | `file.write` | llmwiki/wiki/sources/draft/180726-capability-proof-map.md · tool=Edit · session=246fa7ac · actor=agent · prev=b72f00d58b |
| 2026-07-18 00:48:35 | `file.write` | llmwiki/wiki/sources/draft/180726-capability-proof-map.md · tool=Edit · session=246fa7ac · actor=agent · prev=ef40d7bdaa |
| 2026-07-18 00:48:39 | `file.write` | llmwiki/wiki/sources/draft/180726-capability-proof-map.md · tool=Edit · session=246fa7ac · actor=agent · prev=04425895c0 |
| 2026-07-18 00:48:51 | `file.write` | llmwiki/wiki/sources/draft/180726-capability-proof-map.md · tool=Edit · session=246fa7ac · actor=agent · prev=4ded235897 |
| 2026-07-18 08:51:18 | `task.set` |  · task=T-260718-01 · state=approved · note=gate_bd49612032be duyệt qua /plan · actor=agent · prev=c8f2aed4f667aad290b60 |
| 2026-07-18 08:54:18 | `file.write` | llmwiki/wiki/sources/draft/180726-capability-proof-map-PLAN.md · tool=Write · session=246fa7ac · actor=agent · prev=a34a |
| 2026-07-18 08:54:33 | `task.set` |  · task=T-260718-01 · state=dispatched · note=self-dispatch theo PLAN · actor=agent · prev=97e4682a12cfb731a5f7ed9a4040d |
| 2026-07-18 08:54:44 | `file.write` | fdk/tools/build-capabilities.py · tool=Edit · session=246fa7ac · actor=agent · prev=d35af3055a2edb0ad1552b31ce3238a7eafb |
| 2026-07-18 08:55:09 | `file.write` | fdk/tools/build-capabilities.py · tool=Edit · session=246fa7ac · actor=agent · prev=6b3663da99d9cff3149ae0f7856e11f298c4 |
| 2026-07-18 08:55:21 | `file.write` | fdk/tools/build-capabilities.py · tool=Edit · session=246fa7ac · actor=agent · prev=bc20fbf44b80b3b0663828f761b1ad27dfea |
| 2026-07-18 08:55:25 | `file.write` | fdk/tools/build-capabilities.py · tool=Edit · session=246fa7ac · actor=agent · prev=53b79731c55515e3b7ed87030d3493938bc5 |
| 2026-07-18 08:55:55 | `file.write` | fdk/tools/medic.py · tool=Edit · session=246fa7ac · actor=agent · prev=716e44c40ec7b1b7e5dd4f4fe03fd69ddaf20685184636b98 |
| 2026-07-18 08:55:57 | `file.write` | fdk/tools/medic.py · tool=Edit · session=246fa7ac · actor=agent · prev=a3e889c88682222e85961924da599001d29edeedb39bffdf8 |
| 2026-07-18 08:56:12 | `file.write` | fdk/tools/medic.py · tool=Edit · session=246fa7ac · actor=agent · prev=13e6d27cc2c1017868dd5911e6073db68c919b1767db3dbe3 |
| 2026-07-18 08:57:16 | `file.write` | harness/tests/capproof-test.sh · tool=Write · session=246fa7ac · actor=agent · prev=41e7cea51a45919dff655606c639b7064bd1 |
| 2026-07-18 08:57:29 | `file.write` | .github/workflows/harness.yml · tool=Edit · session=246fa7ac · actor=agent · prev=e9b956e62c254535042d16c54419a949c096bc |
| 2026-07-18 08:58:22 | `file.write` | fdk/tools/build-capabilities.py · tool=Edit · session=246fa7ac · actor=agent · prev=06387a937cc307d0195405e612bcc3e01f7b |
| 2026-07-18 08:59:08 | `file.write` | fdk/tools/build-capabilities.py · tool=Edit · session=246fa7ac · actor=agent · prev=5a9d353138395810ce2836d3f928cfcce077 |
| 2026-07-18 08:59:30 | `file.write` | fdk/tools/build-capabilities.py · tool=Edit · session=246fa7ac · actor=agent · prev=fc6ecb1b0c8c82d28e3f83035f3d49d861fd |
| 2026-07-18 09:00:21 | `task.set` |  · task=T-260718-01 · state=completed · note=4 task xong, medic 13 ok, capproof live: 115/190 proven, 75 no ton, 18 dup  |
| 2026-07-18 09:28:45 | `file.write` | harness/scripts/design-variety.py · tool=Edit · session=246fa7ac · actor=agent · prev=19fc6df058ef2bf15e76a91dd172433de2 |
| 2026-07-18 09:28:55 | `file.write` | harness/scripts/design-variety.py · tool=Edit · session=246fa7ac · actor=agent · prev=22dca199c6a5c2a0ea34bfcad091afbfd8 |
| 2026-07-18 09:29:08 | `file.write` | skills/hallmark/SKILL.md · tool=Edit · session=246fa7ac · actor=agent · prev=1554d632ed9350b2250b2658b92e2feac07b97a2b9a |

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

## 2026-07-14 — R18 plan-executable + /fdk-uat (UAT THẬT, PASS)
- Lỗ: nhánh PLAN của R7 chỉ sống trong validator Python; downstream chạy engine khai báo → luật KHÔNG tới tay người cài. Cổng vẫn xanh vì rule_parity chỉ so danh sách rule id.
- Fix: R18 khai ở cả hai policy (khai báo travel downstream + production gác từng task). Bite-test 2 tầng: doctor 18/18 rails, test-broad 72/72.
- /fdk-uat: skill UAT thật — push trước (đường remote chỉ tồn tại sau push), test sau, không pass thì gỡ commit khỏi remote.
- UAT chạy thật trên dự án TRỐNG cài bằng curl từ GitHub: 3 trụ đủ · test-broad 72/72 · R18 CẮN đúng lý do · 3 skill orchestration reachable · orca runtime UP · 84 skill global · 18 rule. PASS → giữ commit c5efc57.
- UAT HAI PHA chạy thật: pha 1 canary PASS (74/74, luật mới cắn, SKILLS_REF chứng minh cài đúng bản canary chứ không phải orca). Pha 2 main-URL lần đầu ĐỎ (72/74) — điều tra ra raw.githubusercontent propagate TRỄ và KHÔNG ĐỒNG ĐỀU: engine đã mới, policy.yaml còn cũ → bản LAI. Chờ CDN rồi chạy lại: 74/74 PASS. Không phải bug code → không revert. Bài học thành luật: /fdk-uat pha 2 phải poll sentinel trước khi đo (p-29).
- UAT hai pha PASS: canary (3 trụ 5/5, harness 74/74, /wayfinder tới tay, 23 skill tắt model-invocation tới global — cắt token thật) → main-URL smoke (đường mặc định 74/74). Bug lộ ra: sentinel CDN của /fdk-uat viết sai pattern → chờ vô ích 4 phút dù raw đã mới (p-32, đã ghi cảnh báo grep-verify). UAT hai pha PASS (150726).

## 2026-07-15 — hấp thụ hallmark làm nền design chung (T-260715-02, đóng p-23)
- Cài Nutlope/hallmark (Together AI, 106 file, provenance sha256) làm NỀN — 6 discipline + 57 cổng slop-test.
- concept design-foundation: sàn chung; 12 skill taste trỏ tới (flavour trên sàn). docs-site-macos = ngoại lệ artifact nội bộ.
- frontend-antipattern.py +4 cổng UNIVERSAL grep được (gradient-text/italic-header/fake-chrome/số-liệu-marketing), quét trong <style>. --self-test PASS. 0 false-positive trên 30+ seq.html.
- DOGFOOD lộ slop THẬT: overstack.html + index.html + health-dashboard có gradient-text (blue→purple headline) do generator sinh — sửa 3 generator dùng màu đặc.
- /propose fill-default từ catalog hallmark (tag default, ghi ## Assumptions). design-variety.py + .design-log.jsonl: cổng Variety travel-được (phơi bày mọi seq.html là một glass template — nợ đã biết).
- Nợ có sẵn lộ ra (KHÔNG sửa trong SPEC này): ~17 HTML cũ gradient-text + ligature debt.
- UAT hai pha PASS (hallmark): canary (3 trụ 5/5, harness 74/74, hallmark SKILL + 24 references travel tới tay incl slop-test.md) → main-URL smoke (đường mặc định, 74/74, reachable). Raise ledger issue 150726-legacy-html-slop-debt (ready-for-agent) cho nợ ~17 HTML cũ. p-23 đóng.
- /fdk-uat TOÀN DIỆN đường mặc định (curl từ orca, KHÔNG override): 3 trụ 5/5 · harness 74/74 · /wayfinder + /hallmark (129 references incl slop-test.md) tới tay · 23 skill tắt model-invocation · /plan+/propose+/orca-workflow là bản mới · 4 engine tất định ở global harness (frontend-antipattern --self-test PASS, frontier/skill-health/design-variety reachable) · R7-n + R18 CẮN THẬT trong dự án cài mới (exit 2), concept hợp lệ QUA (exit 0) · orchestration-ready 3/3 + orca UP · 86 skill global / 18 rule. UAT toàn diện đường mặc định (150726) PASS.

## 2026-07-15 — sổ nợ unknown: fill-first-find-out-later (T-260715-03)
- Tầng thứ ba giữa (default) và [CẦN LÀM RÕ]: default rủi ro điền để KHÔNG chặn việc, ghi thành nợ có sổ truy được.
- /propose: interview LUÔN có đáp án cuối "điền mặc định bây giờ, tìm hiểu sau"; tag (default, find-out-later → [[unknown-x]] U-NN). + luồng trả nợ.
- Folder llmwiki/wiki/draft/unknown/ + _template.md; harness/scripts/unknown-ledger.py (list/add/resolve/trace, --self-test PASS, audit giữ cả 2 giá trị); /lint 8c hiện nợ (báo cáo không chặn). p-33 solved 3/3.
- UAT hai pha PASS (unknown-ledger): canary (3 trụ 5/5, harness 74/74, /propose fill-first tới tay) → main-URL smoke (đường mặc định, 74/74, /propose reachable, unknown-ledger.py --self-test PASS ở global harness — engine travel thật). p-33 đóng 3/3.

## 2026-07-15 — skill /qc-code: senior review 4 mục + test tái hiện auto-hook (T-260715-04)
- /qc-code: review senior 4 mục (security/performance/naming/logic), điểm/10 + lỗi nặng nhất + fix, verdict PASS/CẦN SỬA. Mục logic sinh test tái hiện qc-*.
- Tách đắt/rẻ (HỎI user → option 3): LLM review gọi tay/workflow; test qc-* auto qua hook tất định 0-token (verify-before-commit 3b), KHÔNG gọi LLM trong hook.
- harness/scripts/qc-regression.py (--self-test PASS, tự phát hiện pytest/vitest/jest, fail-open). /orca-workflow 6b tùy chọn. Verdict advisory; test gác cứng. p-34 solved 3/3.
- UAT hai pha PASS (qc-code): canary (3 trụ 5/5, harness 74/74, /qc-code tới tay) → main-URL smoke (đường mặc định, 74/74, /qc-code reachable, qc-regression.py --self-test PASS ở global harness — engine travel thật). p-34 đóng 3/3.

## 2026-07-16 — skill /teach-me: giải thích 2 cấp + sơ đồ + grounded runtime (T-260716-01)
- /teach-me: giải thích MỘT thứ ở 4 phần cố định (cấp hệ thống +sơ đồ · cấp code +sơ đồ · bộ ba vấn-đề/workflow/chi-tiết os·cơ-chế·vai-trò · tóm tắt luồng +sơ đồ).
- Điểm phân biệt: CHỨNG "nó chạy thế nào" bằng runtime thật — chạy + instrument/breakpoint (pdb/debugpy/node-inspect/print/log) + quan sát state, KHÔNG đọc-rồi-đoán. Mượn triết lý /verify.
- Carve-out cứng: instrument tạm DỌN SẠCH sau (git diff xác nhận); không chạy được → khai "giải thích tĩnh" + ghi nợ unknown nếu khẳng định phụ thuộc runtime chưa thấy.
- Sơ đồ hai đường: mermaid inline (mặc định) / HTML explainer glass docs-site-macos (opt-in khi giữ/chia sẻ). KHÁC /onboard-codebase + /join-project (cả dự án).
- UAT hai pha PASS (teach-me): canary (3 trụ 5/5, harness 74/74, /teach-me tới tay + nội dung grounded-runtime) → main-URL smoke (đường mặc định, 74/74, reachable). Smoke dogfood trên frontier.py chứng bằng chạy thật. p-35 đóng 2/3 trụ (skill-only).

## 2026-07-17 — propose — gộp gitignored-check trùng lặp về canonical (T-260717-01)
- Nguồn: quét vấn đề tồn đọng → flywheel `spec-violation` đã tới ngưỡng 3 (harness-events.py m_stop, audit.py detect, okf-check.py content_files — cùng lỗi "quên skip file gitignored", mỗi lần vá bằng một bản copy logic riêng).
- Điều tra lộ: `harness-lint.py` đã có sẵn meta-guard `WIKI_TREE_SCANNERS` bắt được cả 3 và khiến chúng được vá trong ngày (2026-06-28) — cơ chế phòng-ngừa hệ thống đã chứng minh hoạt động. Phần còn thiếu chỉ là dọn trùng lặp implementation trong `harness/scripts/`.
- SPEC hẹp có chủ ý: chỉ trỏ `okf-check.py` về canonical `index_sync.gitignored()` qua pattern `_load()` mà `audit.py` đã dùng đúng — không file mới. `harness-events.py` giữ nguyên bản tự chứa vì nó là lõi PoC vendor-neutral (cài độc lập qua `curl | bash` vào project khác, không có `harness/scripts/` đi kèm) — Non-goal có lý do kiến trúc, không phải bỏ sót.
- Ghi chú follow-up ngoài phạm vi: `wiki-graph.py`/`wiki-health.py` có `local_only_stem()` trùng lặp verbatim giữa 2 file — khác class lỗi, để dành propose riêng nếu cần.
- Draft: `sources/draft/170726-gitignored-dedupe.md` + `html/170726-gitignored-dedupe-seq.html`. DỪNG chờ duyệt.

## 2026-07-17 — housekeeping — dọn run-council*/ + sửa root cause thói quen output sai chỗ
- Phát hiện: 6 thư mục `run-council`..`run-council6` untracked ở repo root (audit log xác nhận tạo rải từ 2026-07-05 20:10 đến 2026-07-06 11:28 — 6 phiên riêng biệt, mỗi phiên bump số để tránh đè bản trước).
- Root cause: `skills/council/SKILL.md` (canonical) ví dụ Stage 2a/2c dùng `--out run/` — path tương đối trần, không trỏ `scratchpad/`, nên mỗi phiên tự đặt tên khác nhau ở repo root thay vì theo quy ước scratchpad đã có (đối chiếu `scratchpad/co-council/`, `scratchpad/council-eval/` — nhiều lần council TRƯỚC đã làm đúng).
- Fix root: sửa 2 ví dụ lệnh trong canonical thành `--out scratchpad/council-<slug>/` + ghi rõ lý do (bài học 170726), sync ra mirror (`llmwiki/skills/orchestrate/council.md`) + installed (`~/.claude/skills/council/SKILL.md`) qua `fdk/tools/sync-skill.sh council`.
- Dọn: gom 6 thư mục vào `scratchpad/council-archive-170726/` (giữ transcript, không xoá — reversible), không còn xuất hiện trong `git status`.
- Ghi chú phụ, KHÔNG sửa trong lượt này: phát hiện 1 bản `council.md` lạc trong `llmwiki/wiki/skills/orchestrate/council.md` (nằm sai vị trí, wiki content chỉ nên ở concepts/entities/sources/draft/architecture/tours) — nêu ra, chưa dọn vì ngoài phạm vi việc đang làm.

## 2026-07-17 — lint — wiki-sync 11 ngày drift (false-positive) + pattern-health (1 manifest thừa)
- Bước 0 `wiki-sync.py --check`: exit 3, 264 file code/nguồn đổi kể từ neo `2067448d5d` (2026-07-06, 11 ngày). 63 trang wiki bị cờ code-drift (5 concept + 10 draft + 48 source).
- Spot-check 5 trang concept bị cờ (đọc toàn văn): CẢ 5 đều được viết CÙNG LÚC hoặc SAU file code kích hoạt cờ (vd `design-foundation.md` 2026-07-15 cùng ngày `frontend-antipattern.py` được tạo) — nội dung khớp thực tế, không sai. Kết luận: cờ drift ở đây là "chưa đóng vòng review" (11 ngày không ai `--mark-synced`), không phải nội dung sai. 58 trang draft/source còn lại là ghi chép lịch sử tại-thời-điểm-viết, không cần đồng bộ liên tục.
- Bước 1 (orphan, flag không sửa): 3 concept không được trang nào khác trỏ tới — `adapt-modes.md`, `design-foundation.md`, `skill-craft.md`.
- Bước 5 (index gaps): lệnh mẫu trong SKILL.md giả định link dạng `llmwiki/wiki/...` nhưng `index.md` dự án này dùng path tương đối (`concepts/...`) → chạy đúng định dạng thì chỉ có **1 gap thật**: `sources/170726-session-provenance.md` (auto-distill hôm nay) — đã thêm dòng vào index.
- Bước 6 (empty page, flag không sửa): `llmwiki/wiki/draft/orca/README.md` <5 dòng.
- Bước 7/8/8b/8c: 0 file thiếu `## Origin` (2 README loại trừ hợp lệ), 0 marker `shortcut:` thiếu trigger, skill-health 30 skill có cờ description/negation (báo cáo, không chặn — xem `[[skill-craft]]`), 0 nợ unknown mở.
- **Phát hiện mới ngoài checklist chuẩn**: `llmwiki/wiki/skills/` là một cây lạc **68 file** mirror toàn bộ skill docs, nằm sai vị trí (wiki content chỉ được phép ở concepts/entities/sources/draft/architecture/tours theo CLAUDE.md) — cùng gốc thời điểm với stray `council.md` đã ghi ở mục housekeeping trên (commit `0363f5d`, 2026-07-02). KHÔNG dọn trong lượt này (68 file, vượt soft-diff-budget) — khuyến nghị `/raise-issue` riêng.
- Pattern-health (`health-check.py`): 1 file "thiếu" (`llmwiki/skills/README.md`) hoá ra là bị XOÁ CÓ CHỦ Ý ở cùng commit `0363f5d` (33 dòng, thay bằng whiteboard) nhưng `.template-manifest.json` quên gỡ tên — xoá đúng 1 dòng thừa trong manifest (root-cause fix, không phục dựng file đã xoá chủ ý). Sau sửa: 75 pattern, 0 missing; 26 pattern "cũ hơn remote" lộ ra đúng thực chất sau khi bỏ entry ma — khớp `[[framework-multi-session-dev]]` (repo này local-ahead, KHÔNG sync/revert).
- Chốt neo: `wiki-sync.py --mark-synced` sau khi review xong.

## 2026-07-17 — propose — absorb-six-sources
Draft SPEC absorb HÒA TAN 6 nguồn GitHub (gstack review, awesome-skills code-review, everything-claude-code security-review, anthropics frontend-design, claude-mem portability, superpowers receiving-review+systematic-debugging) → nâng qc-code / orca-sec-scans / mem-rank / design-foundation / orca-issue. T-260717-02, chờ gate.

## 2026-07-17 — plan — absorb-six-sources-PLAN
PLAN 6 task thi hành cho T-260717-02 (FR-001..007 phủ đủ, R18 xanh). Executor: Claude in-session.

## 2026-07-18 — propose — capability-proof-map
SPEC checklist năng lực tự soi + tự cộng: proof-resolver 6 tầng trong build-capabilities, medic probe capproof (ratchet), guard fire-drill. T-260718-01, chờ gate.

## 2026-07-18 — plan — capability-proof-map-PLAN
PLAN 4 task (resolver 6 tầng / probe ratchet / guard 4 chiều / dups+mech). Executor: Claude in-session.
