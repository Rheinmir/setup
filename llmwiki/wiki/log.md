# Operation Log

## 2026-06-28 — migrate — framework wiki → fdk/wiki
`llmwiki/wiki` giờ là khuôn per-project (chỉ giữ 1 file demo). Wiki riêng của framework
(64 file: ADR-001..008, concepts harness/fdk) chuyển sang `fdk/wiki/` — "the kit". Xem ADR-008.

## 2026-06-30 — redesign-existing-projects — audit-fix-docs-site-macos
Audit skill `docs-site-macos` theo checklist redesign; vá 8 defect (focus-ring, viewport/meta+favicon, collapse-clip, prototype self-contained, Output-Report lặp, shadow tint, smooth-scroll, reduced-motion) + a11y (skip-link/`<main>`/SVG-aria/tabular-nums/text-wrap). Áp cho CẢ 2 bản mirror (`skills/docs-site-macos/SKILL.md` ↔ `llmwiki/skills/utils/docs-site-macos.md`), verify content identical (939 dòng, diff=0). Mở rộng audit sang 3 skill sinh-HTML họ hàng (cursor-animated-sites, md-to-html, uat-nonit-testcase). Quyết định chiến thuật parity: GIỮ committed-mirror + gate (bác generate-at-install vì gây cross-project drift); vá `stop.py` để tự chạy `sync-skills.py` cuối mỗi lượt đụng skill. Toàn bộ 65 cặp canonical↔mirror verify identical.

## 2026-07-01 — build-now-adapt-later — trupillar4-council-persona
Chốt cứng Trụ 4 bằng cổng CI tất định không-LLM (`code_health.py`: mọi .py compile sạch, wire fdk-gate+CI; lint sâu advisory — BNAL). Triển khai persona-lens council: 18 vĩ nhân + 13 cặp đối-trọng + lệnh `council.py roster --case` (thuần lookup, ép ≥1 cặp). Commit 490df16 + 04b3fcd, fdk-gate 20/20.

<!-- log:auto:start -->

### 🤖 Log tự-động (code-logger, không do agent ghi)

| Thời điểm | Event | Chi tiết |
|---|---|---|
| 2026-06-30 23:21:43 | `file.write` | harness/validators/task_lifecycle.py · tool=Write · actor=agent · prev=0b33f389d2c176689f2dc086213d5c170197908639b8b8e7c |
| 2026-06-30 23:22:26 | `file.write` | harness/scripts/fdk-gate.py · tool=Edit · actor=agent · prev=d7c969ba50db2cf2a6ac7d60d97aac27cf751b93fe466d7b5bd67cc9658 |
| 2026-06-30 23:22:47 | `file.write` | skills/verify-before-commit/SKILL.md · tool=Edit · actor=agent · prev=939c09e5cecfd780aae51af48ba746d324642a6083ca701f8e |
| 2026-06-30 23:23:10 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · actor=agent · prev=d911afaa594077cca770775c1e35e3eb996ee |
| 2026-06-30 23:41:03 | `file.write` | harness/scripts/code-logger.py · tool=Edit · actor=agent · prev=d0c2e8a21875b2c46529069bf8817a298d3172568ef2d8f12507be70 |
| 2026-06-30 23:41:16 | `file.write` | harness/scripts/code-logger.py · tool=Edit · actor=agent · prev=5d11fe8da2159391e4cf73280489302fd775ae59a8716511bb0619d8 |
| 2026-06-30 23:41:24 | `file.write` | harness/scripts/code-logger.py · tool=Edit · actor=agent · prev=3ba1a4e6c20cf62c5ecd1507e4c4bd570a4bfd379eac809bceb01e69 |
| 2026-06-30 23:42:45 | `file.write` | harness/scripts/fdk-gate.py · tool=Edit · actor=agent · prev=f2941209278bc831c1c6426988366ae49a8ad05ca696c1f2efa864472c8 |
| 2026-06-30 23:43:00 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · actor=agent · prev=8390a52a0eb4f4c37866ee807c06fea47e3dd |
| 2026-07-01 00:13:08 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · actor=agent · prev=8a9dda638a6a6295c2919a9d77a6f54ea5b20 |
| 2026-07-01 00:13:22 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · actor=agent · prev=8081a9dc7d708c652f8a892bc015b0ad91425 |
| 2026-07-01 00:13:34 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · actor=agent · prev=9deddeb55ca361516cfd62794effeaedd229e |
| 2026-07-01 00:24:33 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · actor=agent · prev=36e9e7ac3b6156cd6f6fff25312a4fb1ef73d |
| 2026-07-01 00:24:49 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · actor=agent · prev=49a0a0bf90dec6f40e5f6fbdf7126db0ec707 |
| 2026-07-01 01:15:44 | `file.write` | llmwiki/wiki/draft/orca/010726-onboard-html-tabs-redesign.md · tool=Write · actor=agent · prev=5f12fd4b3d62bbc42e8bf2b1f |
| 2026-07-01 01:17:14 | `file.write` | skills/orca-dispatch-reference/SKILL.md · tool=Edit · actor=agent · prev=970ba07c7c54d338eedf649b0bb68a510c19ecc893f3f81 |
| 2026-07-01 01:17:48 | `file.write` | skills/orca-workflow/SKILL.md · tool=Edit · actor=agent · prev=6a3d4caeaf1635fde0fd66f3035c367f03b5c7432e92499b97df17242 |
| 2026-07-01 01:17:54 | `file.write` | skills/orca-onboard/SKILL.md · tool=Edit · actor=agent · prev=264d3adb37904f8ab9ce82155216e20010df5795f7df174d0617e64c22 |
| 2026-07-01 01:17:59 | `file.write` | skills/orca-cli/SKILL.md · tool=Edit · actor=agent · prev=fa879ee0b3197e49a4b9191c2a72f46b89d9816f5ff444091e87a6a71f46ac |
| 2026-07-01 01:18:04 | `file.write` | skills/orchestration/SKILL.md · tool=Edit · actor=agent · prev=6033175d3339901fdf34275600809f7aa21b60603cab098292268cb21 |
| 2026-07-01 01:18:10 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=892a543eed1a9d8a2d68dca13816ad329fe046ddf7debe774054790bac13f4f |
| 2026-07-01 01:41:40 | `file.write` | harness/validators/code_health.py · tool=Write · actor=agent · prev=a49a518fadd1b1fc3a427116a30185eeae46affa502c7204baab |
| 2026-07-01 01:42:01 | `file.write` | harness/scripts/fdk-gate.py · tool=Edit · actor=agent · prev=d2d5b3fbc8667f694b49a06aeb6b342ee0e9bc301996a9da02b956e1c98 |
| 2026-07-01 01:42:15 | `file.write` | .github/workflows/harness.yml · tool=Edit · actor=agent · prev=f68d4bf17b449d93d84afb5802555b094a8f7196b84bd2aff223acad4 |
| 2026-07-01 01:43:22 | `file.write` | harness/validators/code_health.py · tool=Edit · actor=agent · prev=1495d6c5f25d700139c7f0eb045c1ab25ad1ce27a2703b64b6a61 |
| 2026-07-01 01:43:39 | `file.write` | harness/validators/code_health.py · tool=Edit · actor=agent · prev=89ead82105ee2406ef3f835ab2b5c170c64051e9609157cd45c07 |
| 2026-07-01 01:44:35 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · actor=agent · prev=d397178ceffa3e932bd98e842ee3fda926574 |
| 2026-07-01 01:45:50 | `file.write` | llmwiki/wiki/draft/orca/010726-onboard-html-tabs-redesign.md · tool=Edit · actor=agent · prev=d46bbbc206266c29d90db37734 |
| 2026-07-01 01:46:01 | `file.write` | llmwiki/wiki/draft/orca/010726-onboard-html-tabs-redesign.md · tool=Edit · actor=agent · prev=b949d2ca2f9bb7aa545014ae0e |
| 2026-07-01 01:46:12 | `file.write` | llmwiki/wiki/draft/orca/010726-onboard-html-tabs-redesign.md · tool=Edit · actor=agent · prev=a2a185bbd36ace06a769c0c6e1 |
| 2026-07-01 01:46:19 | `file.write` | llmwiki/wiki/draft/orca/010726-onboard-html-tabs-redesign.md · tool=Edit · actor=agent · prev=b998b1d86c924106ed204602ac |
| 2026-07-01 01:46:45 | `file.write` | harness/council.personas.yaml · tool=Write · actor=agent · prev=c73dc04564f811e22688a8539ec9fc6db466d113a8f947e304697ef5 |
| 2026-07-01 01:47:31 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=86e08f35b0dbcd5f558c13f64ae30c3d41be9fb2fd81399add48c56d36cd |
| 2026-07-01 01:47:33 | `file.write` | llmwiki/wiki/draft/orca/010726-onboard-html-tabs-redesign.md · tool=Edit · actor=agent · prev=bf2d97841fca180f919d66ec17 |
| 2026-07-01 01:47:40 | `file.write` | harness/scripts/council.py · tool=Edit · actor=agent · prev=07f11224264c59b97a4588c935ecb4c83041b5bda6daa64b572d86ab2a37 |
| 2026-07-01 01:48:45 | `file.write` | harness/council.config.yaml · tool=Edit · actor=agent · prev=bf822ee5552255673da7b0fa6bccbd4134af3baa35b1dd31a636238ba52 |
| 2026-07-01 01:49:29 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=248e564234013aabd1557d6cfae41cc9306939655f8ad0701676c98dedaa6fc |
| 2026-07-01 01:49:44 | `file.write` | skills/council/SKILL.md · tool=Edit · actor=agent · prev=53e768c5c418331840d3e09b9509622fd3895b82e9f034d7b94d3873c9b4b36 |
| 2026-07-01 01:51:02 | `file.write` | llmwiki/wiki/draft/orca/010726-onboard-html-tabs-redesign.md · tool=Edit · actor=agent · prev=34fef36f5c0123c1d881ad9153 |
| 2026-07-01 01:51:16 | `file.write` | llmwiki/wiki/draft/orca/010726-trupillar4-council-persona.md · tool=Write · actor=agent · prev=37771f728213fd335dc4fdf30 |

<!-- log:auto:end -->
## 2026-07-01 — orca-onboard — html-tabs-redesign (propose)
