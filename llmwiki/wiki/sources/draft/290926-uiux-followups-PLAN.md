---
type: draft
title: "PLAN — dọn việc dở sau semantic search: cổng eye-rest báo nhầm details đóng · tự nạp chỉ mục khi deploy · CI harness · commit/push"
status: in-progress
tags: [plan, orca-graph, html-visual-gate, uiux-asset, ship]
timestamp: 2026-09-29
---

# PLAN 290926 — việc dở sau semantic search

## Origin
User 29/09/2026: "plan và làm chưa làm xong đi thì commit" + goal "tự hành tới khi xong". Việc dở gom từ các lượt trước
([[290926-uiux-semantic-search-PLAN]]): (1) PLAN/graph semantic search chưa commit; (2) chỉ mục tìm kiếm chưa tự nạp khi
deploy; (3) CI `harness` đỏ bước html-slop từ 27/09; (4) trang chip còn cảnh báo eye-rest 584px chưa rõ gốc.

Chẩn đoán đã làm trước khi viết PLAN (tái hiện, không đoán):
- (4) gốc ở CỔNG, không ở trang: `html-visual-gate.mjs` đếm chữ trong `<details>` ĐANG ĐÓNG là "mực" — Chromium vẫn trả
  `getClientRects` cho nội dung details đóng. Fixture `eye-rest-details` đỏ (báo 800px) trước khi sửa.
- (3) tái hiện trọn bước CI trong container `mcr.microsoft.com/playwright:v1.55.0-noble` (sinh lại trang + cổng): 26/26 đạt
  → lỗi chỉ ở runner GitHub. Upstream đã sửa song song (`77f7810` phục vụ trang qua http://127.0.0.1, `ea1c467`), CI
  `harness` trên `orca` xanh từ `0343556` — không làm lại, chỉ xác nhận.

## Global constraints
- Repo framework: gate trên checkout sạch từ `origin/orca` (có 10 commit mới của phiên khác), không đè thay đổi upstream —
  chỉ áp đúng hunk của mình; `ci-local` xanh mới push; commit không AI-attribution (R15).
- Repo uiux-asset: không token nào vào git (`.env.local`, `.search-uploaded` gitignore); gói Upstash free giữ nguyên.

### Task 1: cổng eye-rest bỏ qua nội dung details đang đóng
**Thoả:** — (PLAN vận hành; nguồn ở ## Origin)
**Kind:** fix
**Depends:** —
**Files:**
- Sửa: `fdk/tools/html-visual-gate.mjs`
- Test: `harness/tests/html-visual-gate-test.sh`
**Interfaces:**
- Consumes: —
- Produces: fixture `eye-rest-details` (trang có details đóng dài phải qua sạch)
```js
const shut = el.closest('details:not([open])'); if (shut && shut !== el && !el.closest('summary')) continue;
```
**Verify:** `bash harness/tests/html-visual-gate-test.sh .`

### Task 2: uiux-asset tự nạp chỉ mục tìm kiếm khi deploy
**Thoả:** — (PLAN vận hành; nguồn ở ## Origin)
**Kind:** build
**Depends:** —
**Files:**
- Sửa: `~/orca/setup/uiux-asset/tools/upload-search.mjs`, `~/orca/setup/uiux-asset/package.json`
**Interfaces:**
- Consumes: `search-index.json`, env Upstash Search
- Produces: `npm run deploy` (build chỉ mục → nạp nếu đổi → vercel deploy); `--if-changed`; xoá mục đã gỡ
```json
"deploy": "python3 tools/build-search-index.py && node tools/upload-search.mjs --if-changed && vercel deploy --prod --yes"
```
**Verify:** `cd ~/orca/setup/uiux-asset && npm test && node tools/upload-search.mjs --if-changed`

### Task 3: CI harness đỏ bước html-slop — xác nhận đã xanh
**Thoả:** — (PLAN vận hành; nguồn ở ## Origin)
**Kind:** research
**Depends:** —
**Files:**
- Đọc: `.github/workflows/harness.yml`
**Interfaces:**
- Consumes: lịch sử `gh run list -w harness`
- Produces: kết luận: sửa upstream `77f7810`, không làm lại
```bash
gh run list -w harness -b orca -L 1 --json conclusion -q '.[0].conclusion'
```
**Verify:** `gh run list -w harness -b orca -L 1 --json conclusion -q '.[0].conclusion' | grep -qx success`

### Task 4: commit + push framework (cổng eye-rest, PLAN/graph semantic search + PLAN này)
**Thoả:** — (PLAN vận hành; nguồn ở ## Origin)
**Kind:** ship
**Depends:** Task 1, Task 3
**Files:**
- Sửa: `llmwiki/wiki/index.md`, `llmwiki/wiki/log.md`
- Tạo: `llmwiki/wiki/sources/draft/290926-uiux-semantic-search-PLAN.md`, `llmwiki/graph/290926-uiux-semantic-search.graph.json`
**Interfaces:**
- Consumes: Task 1
- Produces: commit trên `origin/orca`
```bash
python3 fdk/tools/ci-local.py && git push origin HEAD:orca
```
**Verify:** `git fetch -q origin && git log origin/orca -8 --format=%s | grep -q "eye-rest"`

### Task 5: commit + push + deploy uiux-asset
**Thoả:** — (PLAN vận hành; nguồn ở ## Origin)
**Kind:** ship
**Depends:** Task 2
**Files:**
- Sửa: `~/orca/setup/uiux-asset/.gitignore` (thêm `.search-uploaded`)
**Interfaces:**
- Consumes: Task 2
- Produces: `main` trên GitHub khớp local; production deploy
```bash
git add -A && git commit -m "search: npm run deploy tự nạp chỉ mục khi đổi + xoá mục đã gỡ" && git push origin main && npm run deploy
```
**Verify:** `cd ~/orca/setup/uiux-asset && git fetch -q && test -z "$(git log origin/main..HEAD)" && test -z "$(git status --porcelain)"`
