---
name: web-clone
description: >-
  Clone a website — two modes. SNAPSHOT = a faithful, self-contained offline copy of a page
  (HTML+CSS+JS+images in one file, exact bytes, SingleFile-style). RECONSTRUCT = AI reverse-
  engineer the page into a clean editable Next.js/Tailwind codebase (design tokens → component
  specs → parallel builders → visual-diff QA, the ai-website-cloner-template method). Use when
  the user wants to "clone this site", copy a page's design/UI + interactions, mirror a layout,
  save offline, or rebuild a site as editable code. Built-now-adapt-later: snapshot builtin works
  now; faithful live capture + the reconstruct pipeline are one-config engine adapters.
metadata:
  design-standard: "solid-what-how/1"
  contract-version: "1.0.0"
---

# Skill: web-clone

Two honestly-different jobs. Pick the mode first.

| Mode | Output | Use when | Engine |
|------|--------|----------|--------|
| **snapshot** | ONE self-contained `.html` (exact bytes, offline) | archive / faithful copy / "lưu y hệt offline" | builtin inliner · SingleFile CLI · monolith |
| **reconstruct** | clean **Next.js + Tailwind** codebase (editable) | "rebuild as code I can edit" / "clone giao diện thành code" | the ai-website-cloner-template pipeline |

Mode + engine live in `harness/web-clone.config.yaml` (`verified:false` — the live-capture engine
and reconstruct fidelity are the quarantined unknowns).

## WHAT

### Purpose và context
- **Purpose:** clone một website theo một trong hai mode trung thực khác nhau — SNAPSHOT (bản offline tự chứa, đúng byte) hoặc RECONSTRUCT (dựng lại thành codebase Next.js/Tailwind sửa được).
- **Trigger (when to use):** user muốn "clone this site", copy design/UI + interactions của một trang, mirror a layout, save offline, hoặc rebuild site thành code sửa được.
- **Non-goals:** không cam kết pixel+behavior hoàn hảo; không clone để republish site người khác; không phải page → markdown text (đó là `/web-crawl`).

### Mental model
`URL hoặc page.html → chọn mode → snapshot: engine (builtin inliner · SingleFile CLI · monolith) → clone.html` / `reconstruct: recon → foundation → component spec → parallel builders → assembly → visual-QA diff → Next.js codebase`. Mode + engine là adapter trong `harness/web-clone.config.yaml` (`verified:false`).

### Input và output contract
| | Field | Required? | Ý nghĩa |
|---|---|---|---|
| In | mode | có | snapshot hoặc reconstruct — chọn trước |
| In | page.html local hoặc URL live | có | local → builtin inliner offline; live → cần engine |
| In | engine trong config | khi snapshot live | `singlefile-cli` hoặc `monolith` |
| Out | `clone.html` | mode snapshot | một file tự chứa HTML+CSS+JS+ảnh |
| Out | codebase Next.js + Tailwind | mode reconstruct | component spec `docs/research/components/<name>.spec.md` + `app/page.tsx` build được |

### Rules và capabilities
- RULE-01 (MUST): State the mode + be honest: snapshot builtin = LOCAL resources only; faithful live capture needs an
  engine; reconstruct fidelity depends on extraction quality — never claim pixel+behavior perfection.
- RULE-02 (MUST): Respect copyright / Terms — clone for reference/offline/learning, not to republish someone's site.
- RULE-03 (MUST): Self-test (snapshot core): `python3 harness/scripts/web-clone.py --self-test`.
- Capabilities: đọc trang (file local hoặc tải live qua engine đã cấu hình); điều khiển trình duyệt để recon; dispatch builder song song; ghi file clone/codebase cục bộ.

### Failure boundaries
- Live URL mà engine chưa cấu hình → builtin chỉ inline tài nguyên LOCAL → **partial**, nói rõ.
- JS interactions ở mọi engine snapshot = best-effort → không claim đầy đủ hành vi.
- Reconstruct: builder `npx tsc --noEmit` hoặc `npm run build` đỏ → **failed** cho merge đó, sửa rồi chạy lại.
- Mục đích republish vi phạm copyright/Terms → **cancelled**.

## HOW

### Main workflow
| Step | Type | Inputs | Action | Outputs/exit | Failure/next |
|---|---|---|---|---|---|
| W01 | judgment | yêu cầu user | Chọn mode (bảng mode ở trên) + nói rõ giới hạn trung thực | mode | lưu offline → B01; code sửa được → B02 |
| W02 | deterministic | — | Self-test lõi snapshot `web-clone.py --self-test` | rc 0 | đỏ → dừng, báo |
| W03 | effect | mode | Chạy nhánh mode A (snapshot) hoặc B (reconstruct) | `clone.html` hoặc codebase | xem nhánh |
| W04 | judgment | output | Báo kết quả + phần best-effort (JS interactions, fidelity) | báo cáo trung thực | — |

Chi tiết từng bước (nguồn chân lý cho W03, theo mode):

#### Mode A — snapshot (faithful 1-file copy)
1. **Local page already downloaded:** offline, no key —
   `python3 harness/scripts/web-clone.py inline <page.html> --out clone.html`
   (inlines local `<link>` CSS, `<script src>` JS, images as data-URI → one file).
2. **Live URL, faithful:** set `engine: singlefile-cli` (`npm i -g single-file-cli`, keeps scripts)
   or `monolith` (Rust), then `web-clone.py url "<URL>" --out clone.html`.
3. **JS interactions = best-effort** across all snapshot engines (the quarantined unknown).

#### Mode B — reconstruct (→ editable Next.js, the ai-website-cloner-template method)
This is NOT a byte-copy — it reverse-engineers the page into a fresh, clean codebase. Method
(distilled from JCodesMore's `ai-website-cloner-template`, ~6k★; see Related):
1. **Reconnaissance** — browser-MCP/Computer-Use: full-page screenshots @desktop 1440 + mobile 390;
   extract global design tokens (fonts, colors, favicons); sweep scroll/click/hover to find every
   interactive behavior; map page topology.
2. **Foundation** — `layout.tsx` fonts, `globals.css` color tokens + animations, TS interfaces,
   inline SVGs → React icon components, Node asset-download script → `public/`.
3. **Component spec & dispatch** — per section: read EXACT `getComputedStyle()` values (never
   estimate) → write `docs/research/components/<name>.spec.md` (the builder contract: DOM, computed
   styles, state transitions, verbatim content, asset paths, breakpoints) → dispatch **parallel
   builder subagents** (one per sub-component for complex sections; ≤~150 lines spec each).
4. **Assembly** — import components into `app/page.tsx`; wire scroll-snap / Lenis / IntersectionObserver.
5. **Visual-QA diff** — compare clone vs original @desktop+mobile, test every interactive state, fix
   discrepancies by re-extracting. Builders verify `npx tsc --noEmit`; main `npm run build` per merge.

Stack: Next.js + TypeScript + Tailwind v4 + shadcn/ui. Dispatch builders via overstack `/orchestration`
or the Agent tool.

### Branches
| ID | Kind | Guard | Hành vi | Skip / failure | Rejoin |
|---|---|---|---|---|---|
| B01 | user_optional | mode = snapshot | Mode A: page local → `inline`; live URL → engine `singlefile-cli`/`monolith` + `url` | engine chưa có → chỉ tài nguyên local, báo partial | W04 |
| B02 | user_optional | mode = reconstruct | Mode B 5 pha, builder song song qua `/orchestration` hoặc Agent tool | build đỏ → re-extract, sửa | W04 |
| B03 | capability_optional | live capture trung thực cần engine ngoài | set `engine:` trong `harness/web-clone.config.yaml` | không cài → builtin | B01 |

### Validation và stopping
Tất định: `python3 harness/scripts/web-clone.py --self-test`; builders `npx tsc --noEmit`, main `npm run build` mỗi lần merge. Cần review: visual-QA diff clone vs gốc @desktop+mobile và mọi trạng thái tương tác. Dừng khi output có và giới hạn đã nói rõ; không lặp re-extract vô hạn — báo phần còn lệch.

### Examples
- **Positive:** "lưu y hệt offline trang này" với `page.html` đã tải → `python3 harness/scripts/web-clone.py inline page.html --out clone.html` → một file mở offline được, CSS/JS/ảnh inline data-URI.
- **Boundary/failure:** đưa URL live nhưng config chưa đặt engine → chỉ inline được tài nguyên local, báo partial và gợi ý `npm i -g single-file-cli`; tương tác JS ghi rõ best-effort, không claim hoàn hảo.

### Related
- `harness/scripts/web-clone.py` + `harness/web-clone.config.yaml` (engine/mode adapter).
- **Reconstruct method:** `github.com/JCodesMore/ai-website-cloner-template` (the 5-phase pipeline above).
- **Snapshot engines:** SingleFile (`github.com/gildas-lormeau/SingleFile`), monolith.
- `/web-crawl` (page → markdown text), `/computer-use` + `/orchestration` (recon + parallel builders).
