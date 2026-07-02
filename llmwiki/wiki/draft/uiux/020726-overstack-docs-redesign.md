---
type: draft
title: "Redesign overstack docs site — a11y + mind map reorder"
status: proposed
tags: [redesign-existing-projects, output-report]
proposed: 2026-07-02
id: 020726-overstack-docs-redesign
---

# 020726-overstack-docs-redesign
**Type:** draft
**Status:** proposed
**Tags:** redesign-existing-projects, output-report
**Proposed:** 2026-07-02

## What
Redesign audit + targeted a11y/polish upgrades cho docs site `overstack.html` (sinh từ `build-overstack-docs.py`), kèm reorder khối mind map và reclassify 3 lá skill.

## Output
Docs site đã chỉn chu (glass macOS: off-black, một họ xanh, tinted shadow, grain overlay, mesh gradient, ripple). Audit chỉ ra khoảng trống thật → áp khối "redesign upgrades" additive, guard `prefers-reduced-motion`:
- **a11y:** `:focus-visible` ring cho nav link + mọi button (audit: "not optional"); `:focus:not(:focus-visible)` để không lộ ring khi click chuột.
- **Orphan-fix:** `text-wrap:balance` cho h1/h2/h3; `text-wrap:pretty` cho p/lead.
- **Smooth-scroll:** `scroll-behavior:smooth` (tắt khi reduced-motion).
- **Số liệu:** `tabular-nums` cho `.kpi .n`, count mind map, `td code`.
- **Pressed feedback:** active `translateY`/`scale` cho nav link + nút.

Ngoài ra (cùng phiên, theo yêu cầu user + council):
- Mind map (`reference`) đưa lên nhóm **Tổng quan** (section 02); trong section: **hình mind map trước → 7 nhánh giải thích sau**.
- Fix link nội bộ gãy: sentinel `@sid`→`#s{idx}` (không đè `href="#..."` trong ví dụ `<pre>`).
- Reclassify 3 lá LOOP_GROUPS: `build-now-adapt-later`→edit, `cursor-animated-sites`→docs, `tour-guide-supademo`→taste.
- **Nav polish (feedback trên browser):** bỏ ký tự `★` khỏi nhãn nav (Quickstart, Dev cái mới) — trẻ con so với docs chính thức; bỏ tiền tố `Nền 1/2/3 ·` khỏi nhãn nav Wiki/Harness/Skills (group "3 nền tảng" đã đủ nghĩa).

### Council kỹ — audit từng node mind map (5 ghế: Feynman·Linus·Rams·Munger·Kahneman)
Council 3-ghế lần đầu review bản tóm tắt; user yêu cầu soi từng node. Kết quả 5-ghế:
- **Đồng thuận 5/5 — `tour-guide` đặt sai:** nó là feature UI (spotlight tour cho app user), bị gán nhánh "onboard" chỉ do trùng chữ (Kahneman: halo); tách khỏi anh em ruột `tour-guide-supademo`. → **Áp:** đổi `LOOP_MAP` `tour-guide` dev-loop→utils + LOOP_GROUPS vào lá taste; `sync-skills.py` di chuyển mirror sang `utils/`, xóa bản stale `dev-loop/tour-guide.md`.
- **Không hành động (đích phân tán, ≤2 ghế):** `🔧 tiện ích khác` bị coi lá-rác nhưng mỗi ghế đề xuất tách khác nhau; `computer-use→orchestrate`; `imagegen-*`/`loop-runner`/`build-now-adapt-later` mỗi cái 1 ghế. Ghi nhận minh bạch, không sửa (rủi ro > lợi).

## Files
| File | Action |
|------|--------|
| `fdk/tools/build-overstack-docs.py` | modified |
| `harness/scripts/sync-skills.py` | modified (LOOP_MAP: tour-guide→utils) |
| `llmwiki/skills/utils/tour-guide.md` | added (mirror di chuyển) |
| `llmwiki/skills/dev-loop/tour-guide.md` | deleted (stale) |
| `fdk/skills.search.json` | regenerated |
| `llmwiki/html/overstack.html` | modified (regenerated) |

## Notes
- Invoked via: `/redesign-existing-projects` skill
- Mọi sửa style vào generator (`CSS_BASE`), KHÔNG sửa HTML sinh ra trực tiếp — HTML travel cùng install, luôn regenerate từ đĩa.
- `build --check` khớp đĩa ✓; 65/65 skill có lá, 0 UNCLASSIFIED.

## Origin
- **Draft:** `wiki/draft/uiux/020726-overstack-docs-redesign.md`
- **Commit:** _(filled by verify-before-commit)_
- **Date promoted:** _(filled by verify-before-commit)_
