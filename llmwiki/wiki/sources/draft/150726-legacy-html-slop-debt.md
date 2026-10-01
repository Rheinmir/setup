---
type: issue
kind: tech-debt
title: "~17 HTML cũ có gradient-text/ligature debt — đếm lại LIVE còn 0, đóng"
status: done
assignee: "@Rheinmir"
dispatch: Claude
entry: /fdk
priority: P3
tags: [issue, tech-debt, html, hallmark]
timestamp: 2026-10-01
id: 150726-legacy-html-slop-debt
source_session: "Đợt /goal 'kéo toàn bộ issue về và xử lý' 01/10/2026 — ledger trỏ tới draft không tồn tại lần thứ hai"
---

# Issue: nợ gradient-text/ligature trong HTML cũ

## Vấn đề (một câu)
Ledger `ISSUES.md` ghi "~17 HTML cũ có gradient-text trong `<style>` + ligature debt", nhưng file draft của nó đã mất **hai lần**. Bản gốc ngày 15/07 bị mất, nghi do bug GH#99: `raise-issue` không commit. Bản tạo lại ở commit `863e714` (15/09) chỉ nằm trên nhánh `worktree-issues-sweep-150926`, nhánh đó không bao giờ được merge vào `orca`.

## Bằng chứng đóng (đo 01/10/2026 trên `origin/orca` @ a155897)
- Chạy cổng tĩnh `fdk/tools/frontend-antipattern.py` lên từng file trong `llmwiki/html/*.html`: **0/18** file báo `gradient TEXT` hoặc `ligature`.
- `grep background-clip:text` chỉ còn 1 chỗ khớp, trong `overstack.html`. Đó là câu văn mô tả chính luật cấm, không phải CSS.
- Lý do nợ biến mất: lớp nền `fdk/tools/html_base.py` giờ tắt ligature cho `pre,code,kbd,samp` trên MỌI trang sinh ra. Luật gradient-text được hook R22 html-slop cắn ngay lúc ghi file.

## Phạm vi đã làm
Đếm lại bằng cổng tất định thay vì đoán lại danh sách 17 file gốc. Không có file nào cần sửa thẩm mỹ, nên không cần bước `/qc-uiux`.

## Origin
- Raise gốc 15/07/2026 (draft mất), tạo lại 15/09/2026 ở `863e714` (nhánh chưa merge). Đóng bởi phiên `/goal` ngày 01/10/2026 cùng đợt đồng bộ ledger với GitHub.
- Liên quan: [[050826-raise-issue-skill-missing-commit-step]], [[design-foundation]].
