---
# ── frame-template.md — TEMPLATE TẤT ĐỊNH cho mọi frame (/br slice bắt buộc dùng) ──
# frame-lint R1 gác frontmatter, R7 gác NỘI DUNG: muc_tieu phải mô tả nghiệp vụ
# thật (không được generic kiểu "F10 nghiệp vụ"), body phải đủ 4 section dưới.
schema_version: 0
frame_id: frame-NNN-<slug-nói-lên-nghiệp-vụ>   # vd: frame-010-ean13-checksum
created_by: slicer                              # human | slicer
parent_br: br/BR.md
clause_ids: [S?.?]                              # điều khoản BR mà frame này hiện thực
parent_br_hash: <sha256 của br/BR.md lúc slice>
muc_tieu: "<MỘT câu nghiệp vụ người-đọc-hiểu: hệ thống làm GÌ cho AI, vd: Kiểm mã vạch EAN-13 nhập tay — tính checksum digit 13, sai thì chặn lưu phiếu nhập kho>"
scope_code: ["app/<file>.py"]                   # ≤3 file frame ĐƯỢC sửa
scope_test: ["tests/test_<file>.py"]            # test bảo vệ — frame KHÔNG được sửa
acceptance_test: "python3 -m tests.test_<file>"
guards:
  max_iter: 3
  budget_seconds: 60
  no_progress_k: 2
  escalate_after_iter: 3
run_log_ref: br/frames/frame-NNN-<slug>.run.json
---
# frame-NNN-<slug> — <tên nghiệp vụ ngắn>

## Nghiệp vụ
<3–6 câu cho NGƯỜI VỀ SAU đọc: bối cảnh nghiệp vụ, ai dùng, luồng xảy ra khi nào,
vì sao cần. Viết như giải thích cho đồng nghiệp mới — không chép lại frontmatter.>

## Input / Output
- **Input:** <dữ liệu vào — kiểu, nguồn, ví dụ cụ thể (vd: chuỗi 13 chữ số "8934588063050")>
- **Output:** <kết quả — kiểu, ý nghĩa từng giá trị (vd: True = checksum hợp lệ)>

## Tiêu chí nghiệm thu
<liệt kê hành vi acceptance_test kiểm — mỗi dòng một hành vi, gồm cả ca biên:
- <ca thường: ...>
- <ca biên/lỗi: chuỗi ngắn hơn 13 ký tự → ...>>

## Ngoài phạm vi
<những gì frame này CỐ TÌNH không làm (thuộc frame khác hoặc để sau) — chống scope creep.>
