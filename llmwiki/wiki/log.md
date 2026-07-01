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
| 2026-07-01 23:53:23 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=39dce4ae5901e1736d5f85ffd37ff90cad9e3d36d1763651863ea4a3958210d |
| 2026-07-01 23:53:51 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=950348c615b8539ef9506cf2a72f6426ed9465d0b697d2cc02beef8ab7ccb21 |
| 2026-07-01 23:53:59 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=d34a03fb290cc414f84a703eddf428eed5eb13f389c047d73a92b799b77eb5d |
| 2026-07-01 23:54:03 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=79db94e94f7bbb3c8c4e6a63c683c37d52617dee8940cb8413f441fce5b874c |
| 2026-07-02 00:00:18 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=3f9c7ab6b60164c9080fc77818e0ecc6e7525c83f40888e8736cea07768d |
| 2026-07-02 00:04:42 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=a37e5524efea770b6bf30d9868240e736345b5f387f9868b0c8818ebcf02 |
| 2026-07-02 00:05:02 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=fd231af8e966141d73644c40757c751cdac68159cce6802bf48a7d796dad |
| 2026-07-02 00:05:07 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=09d415e2843fc89bebbebbd374c890ab658ec983f31d2cac1d25daa2d1ea |
| 2026-07-02 00:05:13 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=c68cac58931185df804c0fcc13d550367746cba1863b2abba1010bc2ce14 |
| 2026-07-02 00:05:24 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=7875456ac3c6917b86e7e6ea4b577995c3faf08d67b5e2e69e77129a386a |
| 2026-07-02 00:05:40 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=ff38e0f9d06c489573faf0a438a6cfdf69e53611f46244077275b5398f29 |
| 2026-07-02 00:05:59 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=1863869afb81b40fd7c3915cd9651c659331a2c182d3707829f6ab632dac |
| 2026-07-02 00:06:22 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=8db450f0ec5df6c36476f9b906e696a66a4b8a8c31cff33c708501a7dcd0 |
| 2026-07-02 00:06:51 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=ce369980ffbe8a539a5f2160b2c874413b992a55d13b84e95cf7a71bf05c |
| 2026-07-02 00:08:06 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=4822b5e49fa2a2349962e5f8c422b0bdf388c0a63ba6fa89e5d7216ea06d304 |
| 2026-07-02 00:08:20 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=38f5760cb75f8946ab56d0445ab9f933ee243ba95acdae1acec6a65796a2cd1 |
| 2026-07-02 00:08:26 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=44089e86890811b810be5dacb63f06080d354e2c5d32e87d4ef246b79dfbf9b |
| 2026-07-02 00:08:35 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=fe7f03d663bbbf22b48ac6538ad6df3dd3be92492871a82f8996846d42021eb |
| 2026-07-02 00:09:13 | `file.write` | skills/redesign-existing-projects/SKILL.md · tool=Edit · actor=agent · prev=aa704fa4127eadeca2566e8207cfdb286fa59d1ee8bd |
| 2026-07-02 00:09:24 | `file.write` | llmwiki/skills/utils/redesign-existing-projects.md · tool=Edit · actor=agent · prev=30edb90bcf409463258bffa08a67e1e4c939 |
| 2026-07-02 00:24:50 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=d43b183d235ca0ef60c61e004b82e187c063796aaa484ce6825914e90885 |
| 2026-07-02 00:25:11 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=32469c57995c4de56ca098e49fe5057767a9d0055cfbdeabbe3d38e2a6bc |
| 2026-07-02 00:25:27 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=f75eeeed115eb62cec7c4bdc07eeb27ea42c4eebf71cc06f274084c478c5 |
| 2026-07-02 00:25:55 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=2249d551ea4ff0e740b43365d23f84da7a2a8e689b7e48dddbd92ab2eaaaa96 |
| 2026-07-02 00:26:06 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=6ba523971cb79da97ad8de8a06aa49e2edec4d57d5b0e4f3e7b1c9f62875aa0 |

<!-- log:auto:end -->
## 2026-07-01 — orca-onboard — html-tabs-redesign (propose)
## 2026-07-01 — docs-site-macos — 21-quy-tac-docs

## 2026-07-01 — redesign-existing-projects — council-report-redesign

## 2026-07-02 — build-now-adapt-later+fdk — cor-controlled-output-renderer (council verdict: khả thi/hẹp)
