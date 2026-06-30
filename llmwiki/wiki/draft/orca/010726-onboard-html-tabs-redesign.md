---
type: draft
title: 010726-onboard-html-tabs-redesign
status: proposed
tags: [orca-onboard, framework-dev, html-report, docs-site-macos]
timestamp: 2026-07-01
---

# 010726-onboard-html-tabs-redesign

**Status:** proposed — STOP, chờ duyệt trước khi code.

## What
Dựng lại tầng báo cáo HTML của skill `orca-onboard` (Phase 3+4) thành một trang
**đủ — khoa học — tuần tự**: khung điều hướng thật (Overview · Architecture · Guided
Tour · Modules), tour-node giàu chi tiết, tab Modules kiểu "DB" cho repo đa-service
(kiến trúc + data lifecycle mỗi container, **tự ẩn nếu mono**), nối ĐÚNG nguồn nội
dung giàu, ép skeleton để hết sơ sài/đứt tương tác. Giữ nguyên phần Overview/
techstack/version/"làm về cái gì" (user xác nhận đã chuẩn).

## Problem (chẩn đoán — vì sao bản hiện tại sơ sài & "ấn không ăn")
1. **Không gọi hẳn `/docs-site-macos`.** Phase 0 chỉ `ls` kiểm tra skill tồn tại;
   Phase 4 chỉ nhét chuỗi *"Apply docs-site-macos style"* vào SPEC cho DeepSeek
   (DeepSeek không đọc skill). Skill thật chỉ chạy ở nhánh fallback khi opencode chết.
2. **Skeleton orphan.** `assets/docs-site-skeleton.html` (525 dòng, CONTRACT fill-token,
   cấm sửa `<style>/<script>`) **không được SKILL.md tham chiếu** (`grep skeleton` = 0).
   Output thật vẫn dính `s-bg`+`initDraggableDiagrams` ⇒ skeleton ĐÃ được dùng ở vài
   run nhưng qua đường không khai báo ⇒ không deterministic (output 173–816 dòng).
3. **"Ấn không hiệu ứng".** Skeleton chỉ có 3 JS: kéo-thả diagram, collapse, copy.
   KHÔNG có tab-switch, KHÔNG có tour-node bấm-ra-panel ⇒ user bấm node tour/tab → im.
4. **Sơ sài.** Phase 4 SPEC chỉ inject md mỏng (`index.md`, `architecture.md`,
   `onboarding-tour.md`). KHÔNG đọc `ONBOARDING.md` (~20k), `domain-graph.json`,
   `knowledge-graph.json` — nơi chứa nội dung giàu ⇒ HTML kế thừa cái mỏng của md.

## Design

### D1 — Khung điều hướng (skeleton v2) — **1 TRANG LIỀN MẠCH, KHÔNG tab-switch**
Theo luật `docs-site-macos`: **sidebar-nav + scroll-spy**, mọi mục hiện cùng lúc trên
MỘT trang cuộn xuyên suốt (tuần tự/khoa học) — KHÔNG ẩn-hiện kiểu tab. Sidebar bấm →
cuộn mượt tới mục + IntersectionObserver tự sáng mục đang xem. 4 mục:
- **Overview** — giữ nguyên: project name, techstack, version, "làm về cái gì", stats.
- **Architecture** — layers (từ `knowledge-graph.json.layers`) + mind-map SVG draggable;
  mỗi layer: mô tả + danh sách node + edges chính (imports/calls/reads_from/writes_to).
- **Guided Tour** — list bước (tour 5–15) ở trái; **bấm 1 bước → panel chi tiết bên phải đổi
  tại-chỗ** (master-detail click-reveal, NẰM TRONG trang cuộn — không rời trang). Mỗi node
  KHÔNG 1–2 dòng mà gồm: vai trò trong flow · `file:line` thật · input/output · phụ thuộc ·
  vì sao "hot" (churn) · trích `ONBOARDING.md`. Nguồn: `tour[]` + `nodes[]` + `ONBOARDING.md`.
  → **Pattern mới "master-detail click-reveal" cần thêm vào skill `docs-site-macos`** (xem D5).
- **Modules** *(optional, auto-skip mono)* — xem D3.

> **Khung CỐ ĐỊNH chỉ là 4 nav anchor** (Overview/Architecture/Guided Tour/Modules) +
> `<style>/<script>` đóng băng. MỌI nội dung con BÊN TRONG là **data-driven, số lượng
> động** theo repo: số layer, số bước tour (5–15), số card module, số node SVG… đều biến
> thiên. Modules ẩn hẳn khi mono. ⛔ KHÔNG hard-code cứng toàn bộ section.
>
> Skeleton BẮT BUỘC kèm **nút collapse sidebar** (docs-site-macos): desktop → icon-rail;
> mobile → overlay mặc-định-đóng + scrim, chọn mục thì tự đóng.

### D2 — Nối đúng nguồn nội dung (chống sơ sài)
Phase 4 SPEC PHẢI inject (thay vì md mỏng):
- `ONBOARDING.md` (full ~20k) — văn bản giàu.
- `domain-graph.json` — domain→flow→step (cho Tour panel + Modules lifecycle).
- `knowledge-graph.json` **chỉ** `layers`/`tour`/node tagged (KHÔNG full — overflow).
Phase 3 (wiki) cũng nâng: mỗi entity/concept page phải có "Vai trò + I/O + liên kết",
không để 1–2 dòng (HTML đọc lại từ đây).

### D3 — Tab Modules (DB-style, auto-skip mono) — *user chốt: tab riêng, ẩn nếu mono*
- **Detect:** đọc `docker-compose.yml`/`compose.*`/`Dockerfile` → liệt kê service/image/
  container. Đếm: **mono** (0–1 service / không docker) ⇒ **bỏ hẳn mục Modules** khỏi
  sidebar. Đa-service ⇒ render.
- **Mỗi module 1 card/panel:** tên image/container · cổng/volume/env tóm tắt · **kiến trúc
  riêng** (SVG node module đó) · **data lifecycle nội bộ**: đọc-từ → xử-lý → ghi-vào
  (suy từ `domain-graph` flow→step + edges `reads_from`/`writes_to`/`depends_on`).

### D5 — Pattern mới đóng góp ngược vào `docs-site-macos` (user yêu cầu)
Skeleton v2 phải áp ĐÚNG recipe glass đang có (base refraction plane: orbs + dot-grid,
3-tier ladder, `--edge-hi`, sidebar sheen, ripple clip-trong-control) — bài học demo:
tự chế CSS ⇒ mất "gương" + ripple lan. NGOÀI ra thêm **1 pattern mới** vào skill
`docs-site-macos` để tái dùng: **"Master-Detail Click-Reveal"** — list mục bên trái,
bấm → panel chi tiết bên phải đổi tại-chỗ trong cùng trang cuộn (không điều hướng, không
ẩn section khác); kèm spec a11y (aria-selected, focus) + ripple chỉ ở control list.

**Pattern #2 — "Sidebar Icon Tiles (macOS)":** mỗi mục nav = tile bo góc đổ gradient/đặc
màu (kiểu macOS System Settings) chứa **SF-Symbols-style line-icon bằng inline SVG**
(stroke trắng, width≈14, round caps) — KHÔNG dùng glyph unicode (◫ ▸ ▤ trông xấu/lệch
baseline). Logo app = icon "display/monitor" SVG trong tile gradient. Map gợi ý:
overview→info.circle · architecture→square.stack.3d · tour→mappin.and.ellipse ·
modules→cube.box. (Self-contained: vẽ lại path SVG, không nhúng font SF Symbols.)
→ Ghi cả 2 pattern vào `skills/docs-site-macos/SKILL.md` + mirror llmwiki.

### D4 — Wire `docs-site-macos` cho đúng
- Phase 4 luồng chính: **đọc & áp skeleton v2** (fill token + vùng SECTIONS), nạp
  `<style>/<script>` đã đóng băng từ skeleton (cấm DeepSeek tự chế JS) ⇒ tương tác ổn định.
- Skeleton v2 tự chứa JS: `switchPanel/scrollSpy`, `renderTourDetail(nodeId)`,
  `initDraggableDiagrams` (giữ), `collapse`, `copy`, water-ripple — đúng REQUIRED của
  docs-site-macos.
- Fallback opencode chết → invoke skill `docs-site-macos` thật trong Claude main thread
  (đang có sẵn, chỉ cần đảm bảo nó cũng nhận nguồn D2).

## Files (dự kiến chạm)
| File | Action |
|------|--------|
| `skills/orca-onboard/assets/docs-site-skeleton.html` | rewrite → skeleton v2 (1 trang liền mạch + scroll-spy + tour master-detail JS, glass đúng recipe) |
| `skills/docs-site-macos/SKILL.md` | thêm pattern "Master-Detail Click-Reveal" (D5) + mirror llmwiki |
| `skills/orca-onboard/SKILL.md` Phase 4 | wire skeleton (fill-token), inject nguồn D2, Modules detect+skip |
| `skills/orca-onboard/SKILL.md` Phase 3 | nâng wiki page: I/O + vai trò mỗi entity (chống mỏng nguồn) |
| `skills/orca-onboard/SKILL.md` Phase 0 | (nhẹ) note dependency skeleton v2 |
| llmwiki mirror của skill (nếu có) | sync byte-identical |
| `llmwiki/wiki/index.md`, `log.md` | append row draft |

## Plan (tuần tự, mỗi bước verify)
1. Skeleton v2 demo data-giả → user xem UX "ấn ra panel" OK (gate phụ).
2. Rewrite Phase 4: detect Modules, build SECTIONS từ nguồn D2, fill skeleton.
3. Nâng Phase 3 wiki richness.
4. Chạy thử trên 1 repo đa-service (vd worldmonitor) + 1 mono → kiểm auto-skip.
5. verify-before-commit → promote → sync push `Rheinmir/setup@orca` + llmwiki mirror.

## Risks / luật
- `docs-site-macos` = **sidebar-only**, nên "tab" hiện thực bằng sidebar-nav + scroll-spy
  (không phá design system). Nếu user muốn tab-bar thật trên đỉnh → cần quyết riêng.
- DeepSeek hay tự chế JS hỏng → BẮT BUỘC cấm sửa `<script>` skeleton (CONTRACT cứng).
- Modules detect chỉ tin file thật (compose/Dockerfile), không bịa container.
- Tuân luật wiki: mọi page có `## Origin`, đúng subfolder, cặp `.md`+`.html` khi promote.

## Origin
- **Draft:** `wiki/draft/orca/010726-onboard-html-tabs-redesign.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
