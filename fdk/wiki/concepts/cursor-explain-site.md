---
type: concept
title: Explain & clone a site (extract-site Mode 3)
tags: [extract-site, clone, reverse-engineer, methodology]
timestamp: 2026-06-25
id: cursor-explain-site
---

# Explain & clone a site (extract-site Mode 3)

How-to tái dùng để **đọc-hiểu rồi dựng lại một website thành code chạy được**, distilled từ
`ai-website-cloner-template` (MIT) và gộp vào skill [[extract-site]] làm Mode 3. Đây là phần
"explain the site" — đọc nó trước khi chạy một lần clone. Không phải báo cáo một lần; là quy trình.

## Khi nào dùng
- extract-site **Mode 1-2** = bắt *design system* (token → DESIGN.md/css/json). Dừng ở tài liệu.
- extract-site **Mode 3** (trang này) = *rebuild* nguyên trang thành code (vd Next.js + shadcn), pixel-perfect.
- Cùng một cửa "trỏ vào 1 website", chỉ khác độ cao đầu ra — 1 skill để nhớ.

## Foreman pipeline (cốt lõi)
Không phải "inspect xong rồi build". Là **đốc công đi từng hạng mục**: vừa soi từng section vừa
viết spec, rồi giao spec cho builder. Extraction và build chồng nhau.

```
recon → spec-file (mỗi section) → dispatch builder song song → merge → visual QA
```

- **Browser:** dùng `computer-use` (đã có sẵn trong stack, KHÔNG cần cài Chrome MCP) — hoặc Chrome MCP nếu thích.
- **Builder:** Agent tool `isolation:"worktree"` (mỗi builder 1 worktree, không đụng nhau) hoặc `cavecrew-builder` cho component 1-2 file.
- **Spec = hợp đồng:** mỗi section có `*.spec.md` trước khi dispatch; builder nhận **inline**, không đọc doc ngoài.

## Nguyên tắc bất di bất dịch (mỗi cái từng tốn nhiều giờ rework)
1. **Xác định interaction model TRƯỚC khi build** — scroll-driven vs click-driven. Sai = viết lại, không phải sửa CSS. Đắt nhất. Đừng click trước; cuộn chậm xem cái gì tự đổi đã.
2. **Giá trị computed chính xác** (`getComputedStyle`), không ước lượng.
3. **Mọi state**, không chỉ default — diff state-A vs state-B = đặc tả hành vi.
4. **Asset thật**, kể cả ảnh overlay xếp lớp (1 section "nhìn như 1 ảnh" thường là background + foreground + overlay).
5. **Foundation first** — token/font/type tuần tự; phần sau mới song song.
6. **Build luôn compile** — builder chạy `tsc --noEmit` trước khi xong.
7. **Spec >150 dòng → tách nhỏ section** (kiểm tra cơ học).

## Assets (trong `skills/extract-site/assets/`)
- `extract-component-styles.js` — DOM-walker dump computed CSS mỗi node (depth ≤4), lọc giá trị mặc định.
- `enumerate-assets.js` — liệt kê img/video/bg/svg/font/favicon, phát hiện overlay xếp lớp qua zIndex/siblings.
- `component-spec-template.md` — mẫu hợp đồng builder.
- `inspection-checklist.md` — checklist reverse-engineer 5 phase (token → inventory → layout → stack → output).

## Xem dạng đẹp (animated)
Trang này là **markdown nguồn**. Bản hiển thị macOS-chrome + flow animation **sinh ra lúc render**,
không bake sẵn — muốn xem thì móc theme từ skill [[docs-site-macos-skill]] (hoặc `md-to-html`) render
on-demand. Không giữ HTML tĩnh trong repo.

## Notes
- [[extract-site]] — skill chứa Mode 3 này
- [[docs-site-macos-skill]] — theme render on-demand
- Quyết định tinh gọn: KHÔNG tạo skill `clone-website` riêng (trùng cửa "trỏ vào website" của extract-site); KHÔNG tạo skill `agent-rules-sync` (trùng vai trò [[sync-template]]).

## Origin
- **Source:** `ai-website-cloner-template` (JCodesMore, MIT) — distilled qua /orca-onboard
- **Commit:** _(if created from code change)_
- **Date:** 2026-06-25
