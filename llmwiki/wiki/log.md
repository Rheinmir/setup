# Operation Log

## 2026-06-28 — migrate — framework wiki → fdk/wiki
`llmwiki/wiki` giờ là khuôn per-project (chỉ giữ 1 file demo). Wiki riêng của framework
(64 file: ADR-001..008, concepts harness/fdk) chuyển sang `fdk/wiki/` — "the kit". Xem ADR-008.

## 2026-06-30 — redesign-existing-projects — audit-fix-docs-site-macos
Audit skill `docs-site-macos` theo checklist redesign; vá 8 defect (focus-ring, viewport/meta+favicon, collapse-clip, prototype self-contained, Output-Report lặp, shadow tint, smooth-scroll, reduced-motion) + a11y (skip-link/`<main>`/SVG-aria/tabular-nums/text-wrap). Áp cho CẢ 2 bản mirror (`skills/docs-site-macos/SKILL.md` ↔ `llmwiki/skills/utils/docs-site-macos.md`), verify content identical (939 dòng, diff=0). Mở rộng audit sang 3 skill sinh-HTML họ hàng (cursor-animated-sites, md-to-html, uat-nonit-testcase). Quyết định chiến thuật parity: GIỮ committed-mirror + gate (bác generate-at-install vì gây cross-project drift); vá `stop.py` để tự chạy `sync-skills.py` cuối mỗi lượt đụng skill. Toàn bộ 65 cặp canonical↔mirror verify identical.

<!-- log:auto:start -->

### 🤖 Log tự-động (code-logger, không do agent ghi)

| Thời điểm | Event | Chi tiết |
|---|---|---|
| 2026-06-30 14:32:18 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit |
| 2026-06-30 14:32:20 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit |
| 2026-06-30 14:32:27 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit |
| 2026-06-30 14:32:37 | `file.write` | fdk/tools/build-overstack-docs.py · tool=Edit |
| 2026-06-30 14:35:25 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit |
| 2026-06-30 14:35:39 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit |
| 2026-06-30 14:43:52 | `file.write` | harness/scripts/code-logger.py · tool=Edit |
| 2026-06-30 14:47:42 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit |
| 2026-06-30 14:47:56 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit |
| 2026-06-30 14:57:05 | `file.write` | harness/scripts/code-logger.py · tool=Edit |
| 2026-06-30 14:57:18 | `file.write` | harness/scripts/code-logger.py · tool=Edit · prev=genesis · h=352cd192a411afd6b77ce29b0d29dff9be4e112f3d051ac448b46ca3ff |
| 2026-06-30 14:57:36 | `file.write` | harness/scripts/code-logger.py · tool=Edit · prev=352cd192a411afd6b77ce29b0d29dff9be4e112f3d051ac448b46ca3ff089d1a · h=4 |
| 2026-06-30 14:57:42 | `file.write` | harness/scripts/code-logger.py · tool=Edit · prev=489eeb023e5546d71a353664634a15036a8953c8bc67b5b8b1ba89bbd507b995 · h=0 |
| 2026-06-30 14:57:50 | `audit.bootstrap` |  · note=trupillar5 · prev=0c3827f451f185660ffcca363389c7e876ad1e84fd7470f473b1a69414bdf9b4 · h=8df422df15c1bcbf7dcc52679 |
| 2026-06-30 14:57:50 | `test.a` |  · x=1 · prev=8df422df15c1bcbf7dcc526793bdcb584aee0f4e5925dac4e3d63d2013b55d3a · h=f7230740c2723396d122c38d54ba8eea39205 |
| 2026-06-30 14:57:50 | `test.b` |  · y=2 · prev=f7230740c2723396d122c38d54ba8eea39205a856e04396e2dbb333f69aeb5a2 · h=55607a7955791e4beb90b65dccbf24d98e645 |
| 2026-06-30 14:58:41 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · prev=55607a7955791e4beb90b65dccbf24d98e645157dda7bdc3161 |
| 2026-06-30 14:58:52 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · prev=025e7783749ba39f9fcc1cb012a4d6c1b2e78abee37e75ae852 |
| 2026-06-30 15:03:10 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · prev=8e0c1c85cedc7326128f85a595a73ef70006a540ac34093dafe |
| 2026-06-30 15:03:15 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · prev=43c0f440fb8679d1755aeb367ca345cbc41e778e05134f07475 |
| 2026-06-30 15:03:27 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · prev=4ebf813f2b324a12955d9b56e9ce5bf21abf878343d68859040 |
| 2026-06-30 15:03:37 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · prev=808bc354c2dec413f65eb82e27814fc19be9c8fb47bbb26a440 |
| 2026-06-30 15:03:45 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · prev=05d15d8cd023c473a03306a19a623a8c48ff9b414e8dbce13e1 |
| 2026-06-30 15:03:51 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · prev=3fa70c5c4d60e23e177b57f44ffad0eaa51ba3ab819853bc654 |
| 2026-06-30 15:04:52 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · prev=be11a95c831ee0a512ac7655f4b6240e0ec285b1dd9f6d027c0 |
| 2026-06-30 15:08:50 | `file.write` | harness/scripts/code-logger.py · tool=Edit · prev=70dc37554312ba2c43c791ab6615119b67ab525188344edaebcdfc471380b884 · h=9 |
| 2026-06-30 15:08:58 | `file.write` | harness/scripts/code-logger.py · tool=Edit · prev=95f6e8e5b04fbf36bdf9b88c46f309c30c8bbf169dcbc08c58cc7b78aea89091 · h=f |
| 2026-06-30 15:09:07 | `task.new` |  · task=T-260630-01 · title=Wire task-id vào propose→gate · state=proposed · prev=fc2a35f6a239b5b580560a35732709a0c1efc2 |
| 2026-06-30 15:09:08 | `task.set` |  · task=T-260630-01 · state=approved · note=gate duyệt · prev=7f11e2f6eff666d786aab389a49431addb81a70636224650ae4b3f984c |
| 2026-06-30 15:09:08 | `task.set` |  · task=T-260630-01 · state=dispatched · note=giao opencode · prev=b46fc65cbb3b34f3e1c36469af3d806ec1528d47da1215cfc5a20 |
| 2026-06-30 15:09:08 | `task.set` |  · task=T-260630-01 · state=done · note=merged · prev=f4524e11fe0207ae523433909190d5d7915240b9257af5b5f5e0089232615efd · |
| 2026-06-30 15:10:25 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · prev=4dffdb45cb10d83bd5fcf95da2d4d82f10c94e80057c98e8f5c |
| 2026-06-30 15:31:17 | `file.write` | harness/scripts/code-logger.py · tool=Edit · prev=d14c9d65a28c4d25af62d9f8ca9125ae23399285de9619a44884d768708fd85d · h=a |
| 2026-06-30 15:31:29 | `file.write` | harness/scripts/code-logger.py · tool=Edit · prev=a61924f978fc98f5837b32cd8306e0d36facab12f9fc548e159ca35c7e17e0fd · h=0 |
| 2026-06-30 15:33:06 | `file.write` | skills/propose/SKILL.md · tool=Edit · prev=02ecd3f63838db934a096b4576448ba8a0e16eb527d1a991d9c8c94c095ffeab · h=bb0dfb56 |
| 2026-06-30 15:33:13 | `file.write` | skills/propose/SKILL.md · tool=Edit · prev=bb0dfb56982b5025497b64e568bd5b01807615599636384147d9bdd7c696d045 · h=6447a0c7 |
| 2026-06-30 15:33:25 | `file.write` | skills/orca-workflow/SKILL.md · tool=Edit · prev=6447a0c74e07fcee908edd367da249c6ae61303d65a7b59e40cb30a5b122a688 · h=91 |
| 2026-06-30 15:33:35 | `file.write` | skills/verify-before-commit/SKILL.md · tool=Edit · prev=91940769e443b9099958324a8be1326523c2a618afd79dbf3c0706b14a2d2347 |
| 2026-06-30 15:36:33 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · prev=1ac0e76fa84419fc78ec6caf06ebadc9500dd1c8266c6e34fff |
| 2026-06-30 15:36:40 | `file.write` | llmwiki/html/300626-outer-harness-evaluation.html · tool=Edit · prev=cb1b26fbdd573912ab4f8596ec036fe6ef04e132115b0783c03 |

<!-- log:auto:end -->
