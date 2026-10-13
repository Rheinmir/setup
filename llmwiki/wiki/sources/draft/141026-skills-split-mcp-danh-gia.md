---
type: draft
title: "ĐÁNH GIÁ — tách hệ skill ra repo riêng (cài qua installer) và đánh giá MCP host trên Cloudflare"
status: proposed
tags: [plan, skills, installer, mcp, cloudflare, ci]
timestamp: 2026-10-14
---

# Đánh giá 141026 — tách skill ra repo riêng · có nên thành MCP trên Cloudflare?

## Origin
User 14/10/2026 (/goal): "tách hoàn toàn hệ thống skill của rheinmir/orca vào 1 repo riêng vẫn kéo về bằng installer
nhưng để flex được việc develop skill và cập nhật không phải chạy full CI và test quá lâu, nhưng cân nhắc từng skill về
bộ tool phụ thuộc. cuối cùng đánh giá nó có nên tách hẳn ra thành 1 mcp server để host lên cloudflared không, nếu có thì
path đặt là skills.giatbh.io.vn".

Số liệu đo ở `~/orca/setup` (orca @ d1ee975) ngày 14/10/2026, cách đo ghi cạnh từng số.

## 1. Hiện trạng (đo được)

| Chỉ số | Giá trị | Nguồn |
|---|---|---|
| Skill canonical | 106 SKILL.md: 83 native `skills/<tên>/` + 23 vendored `skills/external/<tên>/` | `fdk/skills.provenance.json`, đếm đĩa |
| Chỉ có SKILL.md | 81/106; 25 skill có thêm assets (≈17), references (7), scripts (4), vendor (1) | đếm đĩa |
| Dung lượng | `skills/` 21 MB, trong đó `external/` 16 MB (chủ yếu last30days); `.git` 42 MB | `du` |
| Bản mirror | `llmwiki/skills/<loop>/<tên>.md` 106 file byte-identical, sinh bởi `sync-skills.py` | `harness/scripts/sync-skills.py:2-12` |
| Đăng ký | `.claude-plugin/marketplace.json` 3 plugin = 106; `skill-registry.py` kiểm chéo AGENT/CLAUDE/LOOP_MAP; `fdk/skills.search.json` BM25; `capability-stamp` băm bề mặt | file:line trong khảo sát |
| Manifest đồng bộ CŨ | `.template-manifest.json` chỉ liệt kê 23/106 skill → đường `/sync-template` thiếu 83 skill (lỗi sẵn có) | `.template-manifest.json:19-41` |
| Installer | `bootstrap.sh` → `install.sh:450-462`: `SKILLS_REF=rheinmir/setup#orca` → `npx -y skills add … --global --all` vào `~/.claude/skills` và `~/.agents/skills` | `install.sh` |
| Cập nhật riêng skill | KHÔNG có lệnh chính thức; `harness-update` bảo chạy lại bootstrap; tay thì `npx skills add rheinmir/setup#orca --global --all` | `skills/harness-update/SKILL.md:66-70` |
| CI khi đổi 1 skill | `skills-sync.yml` 15 s (sync, registry, resolve-golden, provenance) **cộng** `harness.yml` ~364 s trên push `orca`, **cộng** local `medic --ci` 72 s, pre-push `fdk-gate`, và `/fdk-uat` 2 pha (~5 phút) | `gh run list`, đo tay |
| Ghép đôi lịch sử | 63/68 commit đụng `skills/` (300 commit gần nhất) cũng đụng `harness/` hoặc `fdk/` — một phần vì gate bắt bump stamp | git log |
| Phụ thuộc engine | **40/106** skill gọi ~80 script `harness/scripts`, `fdk/tools`, `harness/validators` (br 15, doyourmagic 11, fdk 8, lint 7, docs-site-macos 7) | grep |
| Không cần binary ngoài | 32 skill (phần lớn taste/caveman external, tour-guide); 5 skill thuần markdown | grep |
| Tool ngoài | python3 ~49 · git 31 · node 24 · Playwright 24 · npx 15 · curl 15 · gh 9 · docker 9 · opencode 7 · agy 5 · orca CLI 4 · LLM API 3 · ffmpeg 1 · ollama 0 | grep SKILL.md + scripts + references |
| MCP đã có | `mcp/` (Node ≥22, @modelcontextprotocol/sdk + hono): stdio + Streamable HTTP :8791 bearer; prompt/skill, resource `overstack://skill|rule|tool|catalog`, 11 tool core (`skill_find` BM25, `tool_run` spawn python3/node/bash cho 146 script); Dockerfile.mcp; RUNBOOK deploy qua devops-agent | `mcp/src/server.ts`, `mcp/RUNBOOK.md` |
| MCP thiếu | chỉ trả SKILL.md — không references/assets/scripts của skill; `gen-catalog --check` chỉ chạy lúc build Docker, không có CI gác catalog lệch | `mcp/src/catalog.ts:36-38` |
| Cloudflare hiện tại | `skills.giatbh.io.vn` và `agentmemory.giatbh.io.vn` đều có bản ghi proxied nhưng trả **530 / error 1033** = hostname tunnel có, tunnel **đang tắt**; máy này không có `cloudflared`, `wrangler`; Vault k8s2 có sẵn `secret/infra/cloudflare` | curl, dig, Vault health |

## 2. Quyết định đề xuất

### 2a. Tách skill ra repo riêng: **NÊN, theo 3 lớp, không tách phẳng**

Vì sao nên: hôm nay đổi một dòng trong một SKILL.md phải trả ~7 phút CI + medic + fdk-uat của cả framework; phần lớn
thời gian đó kiểm harness/engine, không kiểm skill. Tách xong, một skill đổi chỉ chạy cổng của skill (~20 s), và
engine chỉ chạy cổng của engine.

Vì sao không tách phẳng: 40/106 skill gọi engine. Tách văn bản mà không tách hợp đồng thì skill mới sẽ gọi script chưa
có ở máy người dùng, và medic/capability-stamp hiện đếm skill trong cùng repo.

Ba lớp:

| Lớp | Số skill | Ở đâu sau khi tách | Điều kiện |
|---|---|---|---|
| **A — thuần** | ≈66 (23 external trừ find-skills/last30days; blur, lenis, tour-guide, taste, caveman…) | repo `Rheinmir/skills`, `skills/<tên>/` | chỉ khai `requires.bin` nếu cần (node, playwright…) |
| **B — cần engine global** | ≈31 (lint, query, ship, br, council, loop-runner, qc-uiux, hallmark, docs-site-macos, failure-flywheel, orca-graph…) | repo `Rheinmir/skills`, nhưng frontmatter khai `requires.harness: ">=1.3.126"` và danh sách script dùng | installer cài harness TRƯỚC skill (đã đúng thứ tự: `install.sh:399-431` rồi `450-462`); skill tự fallback `~/.claude/harness/...` (đã có ở lint/query/ship) |
| **C — của framework** | 9 (fdk, new-skill, medic, fdk-uat, harness-update, sync-template, skill-provenance, harness-tour, doyourmagic) | **ở lại** `Rheinmir/setup` | chúng sửa chính repo framework, đi cùng CI framework |

Hợp đồng giữa hai repo (thay cho "cùng repo nên tự khớp"):
1. `skills/<tên>/SKILL.md` frontmatter thêm `requires: {harness: ">=x.y.z", bin: [...], scripts: [...]}` — tất định, kiểm bằng
   một validator mới `skill-requires.py` (≤1 s): bin có trong PATH của máy CI, script có trong `~/.claude/harness` đúng
   version floor.
2. Repo skills có `version.json` riêng và `capability-stamp` riêng (băm 106 SKILL.md); repo setup bỏ skill khỏi stamp của
   nó, nhưng `fresh-install-smoke` vẫn đếm LIVE skill giao tới tay (giữ RULE-06 của fdk-uat).
3. `install.sh`: `SKILLS_REF="${SKILLS_REF:-rheinmir/skills#main}"`; thêm lệnh `overstack skills update` = `npx skills add
   <SKILLS_REF> --global --all` không cài lại harness (đóng khoảng trống "không có lệnh cập nhật riêng skill").
4. `llmwiki/skills/` mirror: bỏ (nó chỉ là bản chép byte-identical cho bundle); `.template-manifest.json` ngừng liệt kê
   skill (đang sai 83/106).

CI của repo skills (mục tiêu ≤30 s, đo khi làm): swh-lint, skill-registry (marketplace ↔ bảng), skill-resolve golden,
provenance, `skill-requires`. Không medic, không harness.yml, không fdk-uat. Phát hành skill = push `main` (ratchet bằng
provenance + golden), không cần 2 pha; fdk-uat chỉ còn chạy khi `install.sh` hoặc floor harness đổi.

Chi phí thật của việc tách: (i) 63/68 commit từng đụng cả hai bên → giai đoạn đầu sẽ có PR cặp; floor version là cách
duy nhất để không gãy; (ii) `fdk/CAPABILITIES.md` của dự án downstream được build từ skill ĐÃ CÀI (`build-capabilities`
đọc `~/.claude/skills`), cần kiểm là nó không đọc `skills/` trong repo; (iii) `skills/external/` 16 MB kéo theo clone
chậm → cân nhắc git-lfs hoặc tách last30days thành gói riêng; (iv) marketplace.json tách theo → `.claude-plugin` sang
repo skills.

### 2b. Thành MCP server host trên Cloudflare tại skills.giatbh.io.vn: **CHƯA NÊN**

Ba lý do, theo thứ tự nặng → nhẹ:

1. **Claude Code và các agent dùng skill dưới dạng FILE trên đĩa** (SKILL.md + scripts + references + assets + hook).
   MCP hiện có chỉ trả văn bản SKILL.md (`catalog.ts:36-38`), 25 skill có file kèm bị mất, 4 skill có `scripts/` không
   chạy được. Host lên cloud không làm skill "dùng được" hơn — installer qua GitHub raw đã là đường phân phối đúng.
2. **Cloudflare Workers không chạy được MCP này.** `tool_run` spawn python3/node/bash cho 146 script; Workers không có
   subprocess, không có python. Chỉ phần đọc (`skills_list`, `skill_find`, `skill_get`, resource) là đưa lên Worker được.
   Bản đầy đủ phải chạy container (k8s2 + cloudflared tunnel), tức chính con đường mà **hôm nay đang tắt** (530/1033 ở
   cả hai hostname). Mở `tool_run` ra internet sau một bearer là mở thực thi script tuỳ ý — RUNBOOK tự ghi "không có
   sandbox cho từng lần gọi".
3. **Chưa có người tiêu thụ thứ hai.** Mọi client hiện tại (Claude Code, OpenCode, agy, các agent) đều cài skill bằng
   `npx skills add`. Một MCP chỉ có giá trị khi có agent không truy cập được filesystem nhưng cần tra skill — chưa có
   ai như vậy.

Khi nào xem lại: có ≥2 consumer không dùng filesystem (ví dụ agent chạy trên k8s2 cần `skill_find`), hoặc cần
`rule_check` từ xa cho CI của repo khác. Khi đó làm **bản đọc-only** trên Cloudflare Worker: tĩnh `catalog.json` +
BM25 trong JS (đã có `skills.search.json`), không `tool_run`; sinh catalog trong CI của repo skills và deploy bằng
`wrangler` từ CI, không qua tunnel. Hostname `skills.giatbh.io.vn` giữ cho việc đó.

### 2c. Token Cloudflare
Token "toàn năng" được dán vào prompt → đã nằm trong transcript phiên (`~/.claude/projects/.../*.jsonl`) và trong điều
kiện `/goal`. Chưa dùng. Việc cần làm: **xoay token**, cấp token mới giới hạn (Zone: DNS edit + Workers edit cho
giatbh.io.vn), cất vào Vault k8s2 `secret/infra/cloudflare` (đã có mục), không dán vào chat nữa.

## 3. Việc làm theo thứ tự (chưa làm, chờ duyệt — duyệt rồi mới viết PLAN có Task N cho orca-graph)

- [ ] T1. Thêm `requires` vào frontmatter 106 skill (sinh tự động từ grep hiện có, người soát 40 skill lớp B) + validator `skill-requires.py` + test.
- [ ] T2. Tạo repo `Rheinmir/skills` bằng `git subtree split skills/` (giữ lịch sử), chuyển `.claude-plugin/marketplace.json`, `fdk/skills.provenance.json`, `fdk/skills.search.json`, `skill-registry.py`, `swh-lint.py`, `skill-resolve-eval.py` + golden; CI ≤30 s.
- [ ] T3. Repo setup: `SKILLS_REF` mặc định → repo mới; xoá `skills/` (trừ 9 skill lớp C, dời về `fdk/skills/`), xoá `llmwiki/skills/` mirror; sửa capability-stamp, build-capabilities, fresh-install-smoke, skills-sync.yml; `.template-manifest.json` bỏ skill.
- [ ] T4. Lệnh `overstack skills update` (installer) + skill `harness-update` chỉ cập nhật skill khi harness không đổi.
- [ ] T5. fdk-uat 2 pha cho bản setup mới (floor harness) + đo: CI skill-only, thời gian `npx skills add`, 116 skill LIVE sau cài.
- [ ] T6. (hoãn) MCP đọc-only trên Worker khi có consumer thứ hai.

## 4. Đã kiểm thêm sau khi viết
- `npx -y skills add rheinmir/setup#orca --global --all` hiện mất **45 s** (đo 14/10, 116 skill về `~/.claude/skills`); sau khi tách mỗi lần cập nhật skill là đúng lệnh này, không kéo harness.
- `fdk/tools/build-capabilities.py:58`: có `skills/` trong repo thì đọc đó, downstream không có thì đọc `~/.claude/skills` → sau khi tách, repo setup không còn `skills/` sẽ tự rơi về global, không cần đổi mã; chỉ cần kiểm lại `capability-stamp` và `fresh-install-smoke`.
- Downstream (openship) ghim `SKILLS_REF` mặc định trong bản `install.sh` đã chép vào `.harness/poc-vendor-neutral/` (dòng 455) → đổi mặc định ở upstream rồi re-curl là đủ, không có `.overstack.yaml` nào ghim.
