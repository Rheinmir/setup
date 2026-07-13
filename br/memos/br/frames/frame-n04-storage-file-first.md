---
schema_version: 0
frame_id: frame-n04-storage-file-first
created_by: human
kind: frame
parent_br: br/BR.md
clause_ids: [N04]
parent_br_hash: reverse-no-hash
muc_tieu: "Đổi lưu trữ memos từ DB sang file-first (mỗi memo 1 file .md)"
scope_code: ["store/file/**","scripts/export-md.py"]
scope_test: ["(reverse)"]
acceptance_test: "(reverse)"
ui_role: none
ui_screen: 
---
# frame-n04-storage-file-first

## Nghiệp vụ
Đổi lưu trữ memos từ DB sang file-first (mỗi memo 1 file .md). Giai đoạn 1: PoC export DB→md + thiết kế driver file-first (Driver interface khoá SQL nên swap sống là rewrite lớn).

## Input / Output
- **Input:** memo trong DB / file .md trên đĩa
- **Output:** mỗi memo = 1 file .md (frontmatter+body)

## Tiêu chí nghiệm thu
- Export DB→md không mất dữ liệu; round-trip đọc lại khớp; frontmatter có id/visibility/thời gian.
- Không phá logic component / API memos.

## Ngoài phạm vi
- Chưa swap store.Driver sống (rewrite lớn) — giai đoạn này chỉ PoC export + design.

## UI hoạt động ra sao
- Không UI (backend/storage).
