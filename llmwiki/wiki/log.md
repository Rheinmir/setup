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
| 2026-07-02 00:26:06 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=6ba523971cb79da97ad8de8a06aa49e2edec4d57d5b0e4f3e7b1c9f62875aa0 |
| 2026-07-02 01:02:37 | `file.write` | harness/scripts/lib/cor.py · tool=Write · actor=agent · prev=9669b9b645bc3cb616a439c1a8361d399fc4fffea464be57d2a1afaec4e |
| 2026-07-02 01:02:54 | `file.write` | harness/scripts/lib/cor.py · tool=Edit · actor=agent · prev=e47e4e75ac9fa27482cc490b1c8d6b7e73cad69175395fffdc029842d84b |
| 2026-07-02 01:03:19 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=2d25c886d8341771a80a7f1e91bfc978cad8f41eaa42d68dd77609a7efaa |
| 2026-07-02 01:03:33 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=a1fc201b76bb0e59f20a429cbf4f8e664050d3b0fe400e71caeadbb66e95 |
| 2026-07-02 01:04:09 | `file.write` | harness/scripts/lib/cor.py · tool=Edit · actor=agent · prev=107b186590c4b5625672595f17a607b8ac744d23f734f9c3a913f6f34023 |
| 2026-07-02 01:04:51 | `file.write` | harness/docs/cor-guide.md · tool=Write · actor=agent · prev=8024b1f2ebe5a2914199bc469d74191210f3af51df5b1a3425e7c4c95b08 |
| 2026-07-02 01:05:19 | `file.write` | llmwiki/wiki/draft/uiux/020726-cor-pattern.md · tool=Write · actor=agent · prev=e730addd20397acf79ea93f69b36e66a96e9b56f |
| 2026-07-02 08:50:41 | `file.write` | skills/fdk/SKILL.md · tool=Edit · actor=agent · prev=8be3161168531ced87cbd154050e2309a90535549009449100a3299abf9c3a93 ·  |
| 2026-07-02 09:02:44 | `file.write` | llmwiki/html/020726-openai-compat-endpoint-pools.html · tool=Write · actor=agent · prev=0b8ae75ca6c5367c6442706afbce2657 |
| 2026-07-02 09:03:07 | `file.write` | llmwiki/wiki/sources/draft/020726-openai-compat-endpoint-pools.md · tool=Write · actor=agent · prev=e204bdabd76f2b2ad3a9 |
| 2026-07-02 09:03:12 | `file.write` | llmwiki/wiki/sources/draft/020726-openai-compat-endpoint-pools.md · tool=Edit · actor=agent · prev=bf4397046029ab6961c25 |
| 2026-07-02 09:05:26 | `file.write` | harness/validators/no_ai_attribution.py · tool=Write · actor=agent · prev=5b5aa6668091f84c52d95ae0d7ec5d9c3f94bac37503d3 |
| 2026-07-02 09:05:42 | `file.write` | harness/poc-vendor-neutral/policy.yaml · tool=Edit · actor=agent · prev=e28ca387186623dd27ca2034ac335ab46e6f2940cde50366 |
| 2026-07-02 09:06:12 | `file.write` | harness/policy.yaml · tool=Edit · actor=agent · prev=44adc464594b3d1dbd5e26040d000f241ab2406801b210d878251a12095e8307 ·  |
| 2026-07-02 09:06:41 | `file.write` | harness/scripts/install-harness.sh · tool=Edit · actor=agent · prev=6ba22d8c2b40a29370fb939a6d7433f0f4a1ff2d58d8ba20ffd2 |
| 2026-07-02 09:07:46 | `file.write` | fdk/wiki/sources/adr/ADR-016-no-ai-attribution-in-commits.md · tool=Write · actor=agent · prev=1229cedb9f0dce29b0f6f09b0 |
| 2026-07-02 09:07:57 | `file.write` | fdk/wiki/sources/adr/ADR-016-no-ai-attribution-in-commits.md · tool=Edit · actor=agent · prev=1eff18fa30f6057e1b0571d346 |
| 2026-07-02 09:08:15 | `file.write` | fdk/wiki/concepts/rule-registry.md · tool=Edit · actor=agent · prev=208a1731fee28365ad7add92996cc0905098fbf4c7460635a496 |
| 2026-07-02 09:08:20 | `file.write` | fdk/wiki/concepts/rule-registry.md · tool=Edit · actor=agent · prev=850588aaedf205427f5a4bba3aa7fbdf0395bb7f67c70d7cabba |
| 2026-07-02 09:08:27 | `file.write` | fdk/wiki/decisions.md · tool=Edit · actor=agent · prev=f2a29cc84a7074a32a1325c681723a10d11ded27f4183a81a4bda853b4145201  |
| 2026-07-02 09:08:45 | `file.write` | fdk/wiki/log.md · tool=Edit · actor=agent · prev=1492b98f339169a551004429f6b93daaa44fa7dc226fab8843fdfa301859f2b3 · h=4f |
| 2026-07-02 09:09:49 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=4f9f982a4cc1aa924551402a1f6996a47eb6d875a8868caced485 |
| 2026-07-02 09:11:19 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=720ea0714b576a46887f5945f7d1062e5c3c78ec9e736784c9183 |
| 2026-07-02 09:13:45 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=69084ef2014b21d0857f2156f183ea33d677f16e926361edcffa0 |
| 2026-07-02 09:13:53 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=508211a83910553b6d7bc4c67e460e72ad8e314fe9b52ae1daaf4 |
| 2026-07-02 09:14:58 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=831cc813f1558290b02507910f9fd988095a6a3f61e7d9d994f3b |
| 2026-07-02 09:15:06 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=9cd295cb33704847739d4e9e28f7e99714cda4b068e62b7360b46 |
| 2026-07-02 09:15:12 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=07cbd502c7f69450ffbd020c02fae95a16a36f80e5eef2cfa1276 |
| 2026-07-02 09:16:56 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=d7c5d9fb8b2324fcf79f077b7a6bd398afb1671da49f5681ca1f9 |
| 2026-07-02 09:17:21 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=d15982646498e4aeca6b97ca6e5dc1fa764ccc2b0451cbd9d5bbb |
| 2026-07-02 09:17:39 | `file.write` | llmwiki/html/020726-adr-015-status.html · tool=Write · actor=agent · prev=14a15504770a699cc5721a8176409264a842f2c746bfc7 |
| 2026-07-02 09:17:53 | `file.write` | llmwiki/wiki/draft/uiux/020726-overstack-docs-redesign.md · tool=Write · actor=agent · prev=28bc720c9f395cbc1260728c507f |
| 2026-07-02 09:18:00 | `file.write` | llmwiki/wiki/sources/draft/020726-adr-015-status.md · tool=Write · actor=agent · prev=9dbd3d5d762297b41a38c25837ee0993ea |
| 2026-07-02 09:18:08 | `file.write` | llmwiki/wiki/draft/uiux/020726-overstack-docs-redesign.md · tool=Edit · actor=agent · prev=a634fc26711b83854215c196eabce |
| 2026-07-02 09:18:09 | `file.write` | llmwiki/wiki/sources/draft/020726-adr-015-status.md · tool=Edit · actor=agent · prev=d823ee3982dbb893c34ddc3f3e05d33cbbe |
| 2026-07-02 09:28:37 | `file.write` | harness/scripts/sync-skills.py · tool=Edit · actor=agent · prev=f2a7b13cc8488a48f6f79edcbfdfcd61b7ee9829b803fc2f8cf2f03b |
| 2026-07-02 09:28:42 | `file.write` | harness/scripts/sync-skills.py · tool=Edit · actor=agent · prev=58b6c6d0ddbda73a84230a7bbab20bc227c78c4f578fe0929d92934e |
| 2026-07-02 09:28:48 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=93ebc2ac88f8ed37095d8a050e8bf9451e864531af8c0578e33a7 |
| 2026-07-02 09:28:58 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=5aec3b12656708f5a428db927388a6e15fbb6fe9b76df18984e3f |

<!-- log:auto:end -->
## 2026-07-01 — orca-onboard — html-tabs-redesign (propose)
## 2026-07-01 — docs-site-macos — 21-quy-tac-docs

## 2026-07-01 — redesign-existing-projects — council-report-redesign

## 2026-07-02 — build-now-adapt-later+fdk — cor-controlled-output-renderer (council verdict: khả thi/hẹp)
## 2026-07-02 — docs-site-macos — openai-compat-endpoint-pools

## 2026-07-02 — docs-site-macos — adr-015-status

## 2026-07-02 — redesign-existing-projects — overstack-docs-redesign
