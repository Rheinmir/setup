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
| 2026-07-01 08:57:13 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=9088f0eb7763c2de44e004143f305ae43309e226ac603b716abba |
| 2026-07-01 08:57:39 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=002a4d9b125ab27a93ae76c4e5feb8576146f2f185748ab946b44 |
| 2026-07-01 09:01:06 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=a2771cb2d1c455e9b594463ec07d7ed72e7cd367e1c7d32121abb |
| 2026-07-01 09:01:15 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=81d6a5c353e36fff5df5dc265ae35e1b668239154ea931bc17270 |
| 2026-07-01 10:47:30 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=7211adeb485976131372bd81bf4f34e8b904a1037ee491b5162bb |
| 2026-07-01 16:18:14 | `file.write` | llmwiki/wiki/draft/orca/010726-query-retrieval-eval.md · tool=Write · actor=agent · prev=c07c23aeb7adbd9b31e9999415580fc |
| 2026-07-01 16:26:10 | `file.write` | harness/scripts/query-log.py · tool=Write · actor=agent · prev=0aa8b0eba2dd4ba29c2a91541b9c7e0096e2c53c3fc5a22abb40ea0f4 |
| 2026-07-01 16:26:33 | `file.write` | harness/scripts/query-log.py · tool=Edit · actor=agent · prev=2b5d01d3405fdf312cb83753dfd197f65bddd72c3d9ffe3b65ede50405 |
| 2026-07-01 16:26:59 | `file.write` | harness/scripts/query-log.py · tool=Edit · actor=agent · prev=8d6fbf00ac16bfd8c5ab732058c7632fc1c218d751d99f2dcc5b854ba9 |
| 2026-07-01 16:27:05 | `file.write` | harness/scripts/query-log.py · tool=Edit · actor=agent · prev=50dc20b2afc9774a0951cc351168d8439810eb00a59f8823bdf0773698 |
| 2026-07-01 16:28:13 | `file.write` | llmwiki/skills/wiki-loop/query.md · tool=Edit · actor=agent · prev=5a526560815bf8afb8903f422b6ab712ad2a0acdc48851107c407 |
| 2026-07-01 16:28:19 | `query-telemetry` | harness/scripts/query-log.py · state=done · actor=agent · prev=7b5ce0f10fca662738ffa727e8ea83bb1d6df27823047cc7a2ec556f7 |
| 2026-07-01 16:32:19 | `file.write` | harness/scripts/retrieval-eval.py · tool=Write · actor=agent · prev=7304bb785017d21d34ec2e4afc7644f726fbc1b626c8c5198368 |
| 2026-07-01 16:35:04 | `file.write` | harness/scripts/query-proxy.py · tool=Write · actor=agent · prev=7c1e95349dd4c4e60d70b892f5f1ab8ee3ae6105cf0f80216e4c3b4 |
| 2026-07-01 16:35:14 | `file.write` | harness/scripts/query-proxy.py · tool=Edit · actor=agent · prev=d481834faa4368c0f64e5b0553c6b7ad54270d48ee99db82087f9b12 |
| 2026-07-01 16:36:03 | `file.write` | harness/scripts/query-proxy.py · tool=Edit · actor=agent · prev=15e62c0c8a751513ff02c97b5555072de92745f0c47625188be70780 |
| 2026-07-01 16:37:29 | `file.write` | harness/scripts/query-proxy.py · tool=Edit · actor=agent · prev=097e2633f0e078a1d588396f10fc856533f978fe18e47978bafda003 |
| 2026-07-01 16:38:42 | `file.write` | llmwiki/skills/wiki-loop/query.md · tool=Edit · actor=agent · prev=58f172225fc0d81b5ffe8a7181ecbfa20b5895f0d1f984649ac85 |
| 2026-07-01 16:40:21 | `file.write` | llmwiki/wiki/draft/orca/010726-query-retrieval-eval.md · tool=Edit · actor=agent · prev=5ebfb5aa19fd23e08aa547a308abf096 |
| 2026-07-01 16:40:53 | `task.new` |  · task=T-260701-01 · title=Query L0→L1: eval truy-hồi + telemetry + 3-tầng · state=proposed · actor=agent · prev=8a6601 |
| 2026-07-01 16:40:53 | `task.set` |  · task=T-260701-01 · state=approved · note=gate duyệt · actor=agent · prev=f4ae975809f07d0292a4e95edb2102381313a21c1670 |
| 2026-07-01 16:40:53 | `task.set` |  · task=T-260701-01 · state=dispatched · note=claude self-impl mảnh1-3 · actor=agent · prev=16dd1ebcc3db0e8c614eeea06f2b |
| 2026-07-01 16:42:42 | `file.write` | fdk/wiki/concepts/query-retrieval-eval.md · tool=Write · actor=agent · prev=30f7b31cc81c38abe8d9c50588c8d6e3157cadcd3c86 |
| 2026-07-01 16:43:16 | `task.set` |  · task=T-260701-01 · state=done · note=08ebb32 promoted · actor=agent · prev=d636ebc073d71be15e36242f8ac203588d3e767411 |
| 2026-07-01 16:51:21 | `file.write` | .github/workflows/harness.yml · tool=Edit · actor=agent · prev=bd07df84d47a56dffeb73d0c7ed6197931467869493ab99b1df4a7323 |
| 2026-07-01 19:41:16 | `file.write` | llmwiki/html/010726-21-quy-tac.html · tool=Write · actor=agent · prev=7048eaa7ea6f8ef86f3f6f31409e29b3419ebccf25514446b1 |
| 2026-07-01 19:41:42 | `file.write` | llmwiki/wiki/sources/draft/010726-21-quy-tac-docs.md · tool=Write · actor=agent · prev=ece08cab0684b247193dd8946fd5b9ba9 |
| 2026-07-01 19:41:47 | `file.write` | llmwiki/wiki/sources/draft/010726-21-quy-tac-docs.md · tool=Edit · actor=agent · prev=8a56aee52a8d8e5f9d308c9429dcb9b862 |
| 2026-07-01 19:41:53 | `file.write` | llmwiki/wiki/index.md · tool=Edit · actor=agent · prev=b0d99b098e1a10667fdceec29e5e3f8eb711fdf53e421bcd144f4ead0815cdc2  |
| 2026-07-01 19:41:57 | `file.write` | llmwiki/wiki/log.md · tool=Edit · actor=agent · prev=3b599d3a55166adc30bd1c04b2937d82d0fb3efa7e9dacef74cd34749c41c115 ·  |
| 2026-07-01 23:16:12 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=1acea7dec95d2680b634ad1de17a67e2ea510ec70c734cd2196028fa28044c2 |
| 2026-07-01 23:16:30 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=6f45ff140fca16864ebe32cd3947ecca2c7661baafdc49167e5aea967ce0ee9 |
| 2026-07-01 23:27:16 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=fa364b187aa15097fdeb14c97106b790386bf6cefd462ce2620b1596f308ed1 |
| 2026-07-01 23:27:28 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=b7fa950a8483e23edbf3ad225aff95b6c9dc1cf97222d22f48a711f386ab6e6 |
| 2026-07-01 23:27:36 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=d66d662c887fb6d988f8d3db2567c501b42cfe03bf42844dab2d5ebc4f29f4e |
| 2026-07-01 23:48:00 | `file.write` | llmwiki/wiki/draft/uiux/010726-council-report-redesign.md · tool=Write · actor=agent · prev=a55780a39c8189ce3c1180562acb |
| 2026-07-01 23:48:06 | `file.write` | llmwiki/wiki/draft/uiux/010726-council-report-redesign.md · tool=Edit · actor=agent · prev=e0e014a23cf6bf82641a0ec904b3f |
| 2026-07-01 23:50:27 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=c0daeab84d1ca972430698fb484e855f87636f06a9d24a2c72b001d12270 |
| 2026-07-01 23:51:36 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=02de6f1f1aafa4cb1f1ef771b157f5792bcfcd780f7705c9293d64b7dbcf |
| 2026-07-01 23:51:46 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=fc89373c4e61461901fc3b33053ab95274e20051bc888844e43a976f1518 |

<!-- log:auto:end -->
## 2026-07-01 — orca-onboard — html-tabs-redesign (propose)
## 2026-07-01 — docs-site-macos — 21-quy-tac-docs

## 2026-07-01 — redesign-existing-projects — council-report-redesign
