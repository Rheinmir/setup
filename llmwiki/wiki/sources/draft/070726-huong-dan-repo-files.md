---
type: draft
title: "huong-dan-repo-files — docs site tương tác file trong repo (ai đụng gì, ở đâu)"
status: proposed
tags: [docs-site-macos, output-report, repo-guide]
timestamp: 2026-07-07
---

# 070726-huong-dan-repo-files

**Status:** proposed

## What
Docs site HTML hướng dẫn sử dụng & tương tác với các file trong repo — phân 3 loại chủ quyền: file NGƯỜI sửa tay (raw/, sổ prompt, queue, answers, SKILL.md), file MÁY sinh (CAPABILITIES/overstack/line-status/mirror — sửa qua generator), sổ append-only & trace (log/index/checkpoints/run-log), kèm bảng lệnh↔file và luật hàng rào (R1/R3/R5/R9/R15/R16, diff-jail).

## Output
- `llmwiki/html/070726-huong-dan-repo-files.html` — 6 section: bản đồ 5 vùng repo (diagram kéo-thả) · file BẠN sửa · file MÁY sinh · sổ sách & trace (checkpoint rollback) · lệnh↔file (đọc→ghi) · luật + checklist. Mind map, theme NÚT GẠT dính đáy sidebar (spec mới: 2 khối dark cùng token, chống FOUC, localStorage), thang chữ COMPACT 13″, offline self-contained, R16 full-path.

## Files
| File | Action |
|------|--------|
| `llmwiki/html/070726-huong-dan-repo-files.html` | created |

## Notes
- Invoked via: `/docs-site-macos` skill.
- Áp dụng LẦN ĐẦU spec theme-toggle + font-floor mới kéo về từ upstream (merge orca 2026-07-07) — thay bản toggle tự-chế trước đó.

## Origin
Phiên 2026-07-07 (issue-15-br-k): user yêu cầu trang hướng dẫn tương tác file repo. Nguồn nội dung: cấu trúc repo thật + các tool GH#15 (br-*, checkpoint, upstream-drift) + 17 luật harness.
