---
schema_version: 0
frame_id: frame-f14-snapshot-diff
created_by: slicer
parent_br: br/BR.md
clause_ids: [C16.1, C16.2]
parent_br_hash: 5aa1c47fb9bc720f40479854a5a5f1bdd49da2a2366b9fdbe72b8bacf59d1d95
muc_tieu: "Mỗi lần chạy ghi một bản chụp bất biến, không đè lên bản cũ; và so hai bản chụp để chỉ ra ai lệch, field nào lệch, lệch bao nhiêu đồng — đây chính là công cụ chạy song song đối chiếu với Excel"
scope_code: ["app/snapshot.py"]
scope_test: ["tests/test_f14.py"]
acceptance_test: "python3 -m tests.test_f14"
ui_role: none
ui_screen: 
guards:
  max_iter: 4
  budget_seconds: 300
  no_progress_k: 2
  escalate_after_iter: 4
run_log_ref: br/frames/frame-f14-snapshot-diff.run.json
---
# frame-f14-snapshot-diff

## Nghiệp vụ

HR tự viết trong file bàn giao rằng họ KHÔNG có môi trường thử nghiệm, KHÔNG có bộ test, và KHÔNG có nhật ký lỗi — kèm câu hỏi cay đắng: *'khi bảng lương ra số sai thì làm sao ai biết?'*. Đây là câu trả lời tối thiểu.

Mỗi lần chạy engine ghi ra một thư mục mới có dấu thời gian, không bao giờ ghi đè. Muốn biết bản mới có làm hỏng gì không thì so hai bản chụp: nó in ra đúng người, đúng field, đúng số tiền lệch. Đây cũng là cách duy nhất để HR dám cắt Excel — chạy song song hai bên vài kỳ, diff rỗng thì mới tin.

## Input / Output

- **Input:** kỳ lương, danh sách dòng kết quả, thư mục gốc
- **Output:** `write_run` → đường dẫn thư mục chụp (mới mỗi lần); `diff(a, b)` → danh sách `{employee_id, code, delta}`

## Tiêu chí nghiệm thu

- Chạy hai lần → hai thư mục KHÁC nhau, không đè
- Hai lần chạy cùng dữ liệu → diff rỗng
- Lương lệch 200.000 → diff chỉ ra đúng người, đúng mã field, đúng 200.000
- Người có ở bản này mà thiếu ở bản kia → diff bắt được

## Ngoài phạm vi

Không có giao diện xem diff (in ra dòng lệnh). Không quản lý phiên bản tham số (đã có trong params).
