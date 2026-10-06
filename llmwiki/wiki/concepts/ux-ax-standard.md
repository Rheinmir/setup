---
type: concept
title: Chuẩn UI/UX của framework — UX + AX, DONE contract, ratchet
tags: [ui, ux, ax, qc-uiux, done-contract, standard]
timestamp: 2026-10-06
---

# Chuẩn UI/UX của framework — UX + AX, DONE contract, ratchet

AI dựng website rất nhanh, nhưng code xong chưa phải website ngon: đọc 5 giây không hiểu bán gì, mobile là bản desktop bị bóp nhỏ, headline sáo rỗng, máy tìm kiếm và agent AI đọc không ra, share link trông trơ trọi. Framework vì vậy có MỘT chuẩn cho câu hỏi "UI thế nào mới gọi là xong", thực thi bằng skill `/qc-uiux`. Mọi việc dựng hay sửa UI (`hallmark`, `design-prim`, frame UI của `/br`, sửa tay) kết thúc bằng nó.

## Ba ý của chuẩn
1. **Soi cả UX lẫn AX.** UX là người đọc: a11y, phân cấp và ấn tượng (thử 5 giây, CTA, mobile thật sự), nhất quán, antipattern. AX (AI-experience) là máy đọc: crawler và bot AI vào được, HTML server-render có nội dung, canonical, JSON-LD, OG card, sitemap. Nền tảng nhàm chán thắng mẹo: `llms.txt` chỉ là ghi chú, không phải đường tắt lên top.
2. **DONE viết trước, khoá lại.** Đề xuất xếp Must/Should/Could, mỗi dòng có bằng chứng và tiêu chí nghiệm thu; khối DONE khoá sha256 trước khi sửa (`done-contract.py lock`) nên không nới được tiêu chí cho dễ đạt.
3. **Ratchet.** Tiêu chí đã đạt thành cổng hồi quy cho mọi vòng sau (`done-contract.py verify`): vòng sau không được phá thứ vòng trước đã làm đúng.

## Phần máy làm (0-token)
- Engine `visual-qa` — contrast, tap-target, overlap, tràn ngang, ở 3 khổ 1440 · 768 · 375 (`--viewports`).
- `skills/qc-uiux/scripts/ax-scan.py` — AX đọc HTML thô như crawler; rc 0 sạch · 1 FAIL · 2 WARN · 3 không với tới (không bao giờ là PASS).
- `skills/qc-uiux/scripts/done-contract.py` — `lock · check · pass · verify · status`.

## Notes
- [[adapt-modes]]

## Origin
- **Source:** yêu cầu user 2026-10-06 — nâng `/qc-uiux` thành chuẩn chung của framework thay vì thêm skill mới.
- **Date:** 2026-10-06
