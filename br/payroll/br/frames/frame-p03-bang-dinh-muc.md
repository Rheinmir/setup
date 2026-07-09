---
schema_version: 0
frame_id: frame-p03-bang-dinh-muc
created_by: slicer
parent_br: br/BR.md
clause_ids: [C5.3.2, C5.3.4, C5.3.5, C5.3.6]
parent_br_hash: 19d405e59625a1192e74e53a7e1bc00778cbf92f9fe223f000d8d40994ab610e
muc_tieu: "Kho định mức 4 bảng: điện thoại (ngạch×VP/CT), đi lại (dải×4 nhóm đối tượng), CT+công tác xa (khối×dải×2 đối tượng), CT xa theo dự án×chức danh"
scope_code: ["app/p03_dinhmuc.py"]
scope_test: ["tests/test_p03.py"]
acceptance_test: "python3 -m tests.test_p03"
guards:
  max_iter: 4
  budget_seconds: 120
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-p03-bang-dinh-muc.run.json
---
# frame-p03-bang-dinh-muc

## Nghiệp vụ
PRD cho 4 bảng định mức tĩnh dạng ma trận. Nhóm đối tượng đi lại xác định từ hồ sơ: CHT/CHT ME theo chức danh; còn lại theo trình độ (ĐH+ / CĐ-TC-Nghề) riêng NV.02 là nhóm thứ 4 theo ngạch. Frame này nạp 4 CSV và trả định mức khi biết hồ sơ NV + bộ phận — là 'một nguồn định mức duy nhất' PRD đòi, tách bạch với tờ trình ghi đè (p04).

## Input / Output
- **Input:** 4 CSV định mức trong data-draft/, hồ sơ NV (ngạch, trình độ, chức danh), khối + dải khoảng cách
- **Output:** dinh_muc(loai_pc, ho_so, boi_canh) → số tiền/tháng theo Quy định chung

## Tiêu chí nghiệm thu
- Điện thoại QL.02 tại CT → 1.000.000; tại VP → 800.000; thử việc VP → 0
- Đi lại: CHT + khac_mien → 11.200.000; NV.02 + 30-100 → 250.000
- CT xa Quan Lạn × Thủ kho → 2.000.000
- Nhóm đối tượng: NV.01 trình độ ĐH → nhóm ĐH+ (không phải CĐ)

## Ngoài phạm vi
Không áp pro-rata (p13). Không xử lý tờ trình ghi đè (p04).
