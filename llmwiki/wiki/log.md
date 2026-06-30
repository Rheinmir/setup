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
| 2026-07-01 01:49:44 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=53e768c5c418331840d3e09b9509622fd3895b82e9f034d7b94d3873c9b4b36 |
| 2026-07-01 01:51:02 | `file.write` | llmwiki/wiki/draft/orca/010726-onboard-html-tabs-redesign.md · tool=Edit · actor=agent · prev=34fef36f5c0123c1d881ad9153 |
| 2026-07-01 01:51:16 | `file.write` | llmwiki/wiki/draft/orca/010726-trupillar4-council-persona.md · tool=Write · actor=agent · prev=37771f728213fd335dc4fdf30 |
| 2026-07-01 01:51:35 | `file.write` | llmwiki/wiki/index.md · tool=Edit · actor=agent · prev=b08906e7bdf66c53330d091fd1f0aa4a263631acd573d66488933d388c2f333f  |
| 2026-07-01 01:53:28 | `file.write` | llmwiki/wiki/draft/orca/010726-onboard-html-tabs-redesign.md · tool=Edit · actor=agent · prev=dcbf070a09627a8308d50a0e69 |
| 2026-07-01 01:55:25 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=59c4c96ac9d9b31da36d9dbea582c5c685ee1256bb92a5d2075aa9c65ecc |
| 2026-07-01 01:55:33 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=0df9e71818389b7ef6874c2236b39eb88d32f032fea6f636d0ae13e70dea |
| 2026-07-01 01:55:51 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=8a6d979e86deb183ed49078b4584e5364010f1215d84d805b12ce3b316cf64d |
| 2026-07-01 01:56:30 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=48575ba75eb11f0affeb3baaac16a529f6fa589cf3f4df52aa7dbaefa0da |
| 2026-07-01 01:57:08 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=7092a26e934dfde9a002b02e96ce5786705b79f9e9a86c9e8f57ab1606a3 |
| 2026-07-01 01:57:39 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=18b9f26c39a9ed862c656f22d8ea0a6b43931a1fbdd4be50bdf14b39688f8cd |
| 2026-07-01 02:10:06 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=1acb23c95d81841c184245d7a4634fdeb19055ae7661257ff2b02 |
| 2026-07-01 02:10:15 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=53ec1d825a91908b4d041fe048978b87d50acc5ea9a20aa593159 |
| 2026-07-01 02:10:50 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=74fac91fdc8089fd1044fe35c334e87c03d6dfc7c4473e3341a1c |
| 2026-07-01 02:11:13 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=b913b3688588b6af7c0e453204504b52095039ac34efa06afdd06 |
| 2026-07-01 02:12:39 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=07e7fda6c961ae9fb521a5270bb6dd12a53334f250d222acde6af |
| 2026-07-01 02:13:39 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=c9b21fad8afd2ecc3cb39a11fae57ad6edaaa6d3a5708a2f13755 |
| 2026-07-01 02:15:00 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=3ea83dfda0dff9a3dc1026be2f772a845685a268aae81563b2196 |
| 2026-07-01 02:17:00 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=1cd946031dd75e8476b0b71b9dbebeb452b2073c48d9a3cb7b22e |
| 2026-07-01 02:17:26 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=2caccf23c9b54e792b3472038547059ceabe6845fc72312f63012 |
| 2026-07-01 02:41:44 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=cd62fb586b59e4d4f1726a42cd7610ed943b2981a7b5ddd0b859c |
| 2026-07-01 02:42:30 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=4974e56590e36b8e1e4df8d896c611e2ae6b913b0e77d66c3f232 |
| 2026-07-01 02:42:37 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=87c037417c14c7f75eae6083ab2d2f354c2658cadbea44ba8389c |
| 2026-07-01 02:42:43 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=b58c3dbd499396de9a4ddd3d22e464b02b8761c4a3c02cdd5281b |
| 2026-07-01 02:42:50 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=d4d358e47ce2eca0298d1b721fb6d104f1747eafd74bbb05b24aa |
| 2026-07-01 02:43:07 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=df949dcb9639a6e4fa5cd88053c37beffc8877b322c5d45cbbe3c |
| 2026-07-01 02:43:29 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=0cd9614d0328c8abe1c01dafc9410278d4e84930e36bd430ecc53 |
| 2026-07-01 02:44:05 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=562325a86b23ca44be16bfd794fdfba8870c26badb4dd846c883c |
| 2026-07-01 02:44:47 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=fa1dd7238b1c53947c6f6f5c23dbe1ede0bcbf5f391cc33f3e804 |
| 2026-07-01 02:45:07 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=5cc2942bcb4a1fb167fbc801aafc3eacc0b11113fce26c2a28610 |
| 2026-07-01 02:47:00 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=47ebaea8c2685948d144f6d43460be7e154b2a608a33698b081af |
| 2026-07-01 02:48:18 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=6c4e9ed7f5f7bbfe022a96f2d92ee296fd0eab0ec8fa446afe200 |
| 2026-07-01 02:49:02 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=0d82d121da1a0a896f25b0ed3cf2257f93a99f9a04897303336f6 |
| 2026-07-01 02:49:10 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=03a63b45b62471d6f0bc8f4139356cb61be97bb6ab4481f25566b |
| 2026-07-01 02:50:09 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=5cb5be4bd55760b24cb56c5992769b076c7cdafb59720aa0c11b7 |
| 2026-07-01 02:50:18 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=346efdcf0fbf9b0b5a44448b972e146f8c9ae0b2f4cf782e71aee |
| 2026-07-01 02:52:43 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=0eed2ed9e62c09b3f0395deebcfeaa9761f84b16747cf80c0e75c |
| 2026-07-01 02:59:31 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=055e1f1ddfcd9e61e5b08d03ab3da23aa33fb8fdf8f471d51f84a |
| 2026-07-01 03:00:29 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=4113c1ebe3f66375dc3fdce29edbbddfb61d798d418ef36a8aca1 |
| 2026-07-01 03:02:25 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit · actor=agent · prev=2c8fb36aa1d8720009dc76a5f65e0feaae6a5af111e06a38148fc |

<!-- log:auto:end -->
## 2026-07-01 — orca-onboard — html-tabs-redesign (propose)
