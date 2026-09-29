---
type: draft
title: "PLAN — semantic search cho uiux-asset (Upstash Search free, fallback từ khoá)"
status: in-progress
tags: [plan, orca-graph, uiux-asset, search, upstash]
timestamp: 2026-09-29
---

# PLAN 290926 — semantic search uiux-asset

## Origin
User 29/09/2026: "có thêm elastic search cho nó được không" → "vậy semantic search thì sao" → duyệt cách 1 (Upstash Search gói free,
tắt tự nâng gói), "ok làm đi" + goal "tự hành tới khi xong". Ràng buộc cứng của user: **không tốn tiền**.

Repo làm việc: `~/orca/setup/uiux-asset` (Rheinmir/uiux-asset, host Vercel `uiux-asset.giatbh.io.vn`). Chỉ mục ~94 mục:
65 hiệu ứng `scroll-effects/manifest.json` + 29 hình chip `tools/build-chips.py`.

## Global constraints
- Upstash Search: `--plan free`, `autoUpgrade=false`; không gói trả phí nào.
- Không đổi code gốc nguyên văn các pen scroll-effects (chỉ đọc manifest).
- Token Upstash chỉ nằm trong env Vercel/`.env.local` (gitignore) — không commit, không lộ ra client.
- Search lỗi/hết hạn mức → ô tìm tự rơi về tìm từ khoá phía client, trang không bao giờ trắng.
- Cổng: `html-visual-gate` 0 FAIL cho trang đụng tới; `node tools/test-stats.js` + `node tools/test-search.js` xanh.

### Task 1: cài Upstash Search gói free vào project Vercel uiux-asset
**Thoả:** — (PLAN vận hành; nguồn ở ## Origin)
**Kind:** infra
**Depends:** —
**Files:**
- Sửa: `.vercel/project.json` (resource nối vào project) · `.env.local` gitignore qua `vercel env pull`
**Interfaces:**
- Consumes: —
- Produces: env `UPSTASH_SEARCH_REST_URL`, `UPSTASH_SEARCH_REST_TOKEN` (tên thật đọc từ `vercel env ls`)
```bash
vercel integration add upstash/upstash-search -n uiux-asset-search --plan free -m primaryRegion=us-central1 --no-env-pull
vercel env pull .env.local --yes
```
**Verify:** `cd ~/orca/setup/uiux-asset && vercel env ls 2>&1 | grep -q SEARCH`

### Task 2: sinh chỉ mục search-index.json từ manifest + khối chip
**Thoả:** — (PLAN vận hành; nguồn ở ## Origin)
**Kind:** build
**Depends:** —
**Files:**
- Tạo: `tools/build-search-index.py`, `search-index.json`
**Interfaces:**
- Consumes: `scroll-effects/manifest.json`, `tools/build-chips.py` (SECTIONS)
- Produces: `search-index.json` = [{id, title, kind, text, url, tags}]
```python
items = [dict(id=f"se-{m['slug']}", kind="scroll-effect", title=m["title"], text=" · ".join(filter(None, [m["title"], m.get("desc"), m.get("tech"), m.get("author")])), url=m["url"]) for m in manifest]
items += [dict(id=f"chip-{no}", kind="chip", title=title, text=f"{title} · {cap}", url=f"/components/chip.html#f{no.split('–')[0]}") for group, figs in SECTIONS for no, title, cap, _ in figs]
```
**Verify:** `cd ~/orca/setup/uiux-asset && python3 tools/build-search-index.py --check`

### Task 3: nạp chỉ mục lên Upstash Search + đo 10 truy vấn Việt/Anh
**Thoả:** — (PLAN vận hành; nguồn ở ## Origin)
**Kind:** research
**Depends:** Task 1, Task 2
**Files:**
- Tạo: `tools/upload-search.mjs`
**Interfaces:**
- Consumes: `search-index.json`, env Search
- Produces: index `uiux` trên Upstash Search; bảng đo precision@3 cho 10 truy vấn
```js
const idx = new Search({ url, token }).index('uiux');
await idx.upsert(items.map(i => ({ id: i.id, content: { title: i.title, text: i.text }, metadata: { kind: i.kind, url: i.url } })));
const hits = await idx.search({ query: q, limit: 3 });
```
**Verify:** `cd ~/orca/setup/uiux-asset && node tools/upload-search.mjs --eval`

### Task 4: API /api/search (semantic) + fallback từ khoá
**Thoả:** — (PLAN vận hành; nguồn ở ## Origin)
**Kind:** build
**Depends:** Task 2
**Files:**
- Tạo: `api/search.js`, `tools/test-search.js`
**Interfaces:**
- Consumes: env Search, `search-index.json`
- Produces: `GET /api/search?q=` → {mode: "semantic"|"keyword", hits: [{id,title,kind,url,score}]}
```js
module.exports = async (req, res) => {
  const q = String(req.query.q || '').trim().slice(0, 120);
  try { res.json({ mode: 'semantic', hits: await semantic(q) }); }
  catch { res.json({ mode: 'keyword', hits: keyword(q, INDEX) }); }
};
```
**Verify:** `cd ~/orca/setup/uiux-asset && node tools/test-search.js`

### Task 5: ô tìm kiếm ở trang chủ (phím /) + ghi từ khoá vào stats
**Thoả:** — (PLAN vận hành; nguồn ở ## Origin)
**Kind:** design
**Depends:** Task 4
**Files:**
- Tạo: `search.js`
- Sửa: `index.html`, `api/search.js` (ZINCRBY s:queries), `api/stats.js`, `tools/build-stats.py`
**Interfaces:**
- Consumes: `/api/search`
- Produces: ô tìm trang chủ; panel "Từ khoá hay tìm" trên /stats.html
```js
document.addEventListener('keydown', e => { if (e.key === '/' && document.activeElement.tagName !== 'INPUT') { e.preventDefault(); box.focus(); } });
box.addEventListener('input', debounce(async () => render(await (await fetch('/api/search?q=' + encodeURIComponent(box.value))).json()), 200));
```
**Verify:** `cd ~/orca/setup/uiux-asset && node ../setup/fdk/tools/html-visual-gate.mjs index.html stats.html`

### Task 6: deploy + kiểm trên domain thật + commit/push
**Thoả:** — (PLAN vận hành; nguồn ở ## Origin)
**Kind:** ship
**Depends:** Task 3, Task 5
**Files:**
- Sửa: `api/search.js` (bản deploy) · `README.md` (thêm mục search)
**Interfaces:**
- Consumes: mọi task trên
- Produces: production có search; `git push` main
```bash
vercel deploy --prod --yes && git add -A && git commit -m "search: semantic search (Upstash Search free) + fallback từ khoá" && git push origin main
```
**Verify:** `cd ~/orca/setup/uiux-asset && git status --short | wc -l | grep -q '^ *0$'`
