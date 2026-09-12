---
type: concept
title: "orca-graph — phân việc dạng đồ thị phụ thuộc có khoá, lease, generation và state bền; model trả lời có nhãn và bị audit"
status: implemented
tags: [orca-graph, dag, dispatch, state, lease, generation, evidence, rubric]
timestamp: 2026-09-12
id: orca-graph
relations:
  - {rel: extends, to: orca-workflow}
  - {rel: depends-on, to: plan}
  - {rel: touches, path: harness/scripts/orca-graph.py}
  - {rel: touches, path: fdk/tools/graph-viz.py}
  - {rel: touches, path: fdk/tools/graph-atlas.py}
  - {rel: touches, path: skills/orca-graph/SKILL.md}
  - {rel: touches, path: harness/tests/test_orca_graph.py}
---

# orca-graph — phân việc dạng đồ thị phụ thuộc

## Bài toán thật

`/orca-workflow` dispatch theo từng `### Task` trong PLAN.md, nhưng PLAN chỉ có Interfaces Consumes/Produces, không có dòng phụ thuộc. Cái gì chạy song song và cái gì phải chờ do Claude đoán trong đầu, không ai kiểm được, và khi phiên kết thúc thì "đang chạy tới đâu" biến mất cùng context. Sổ task của Orca có `--deps` nhưng là runtime-global, không có trường dự án, nên không dùng làm nguồn chân lý được.

Điểm đòn bẩy được chọn theo Meadows là **đổi luồng thông tin**: biến phụ thuộc thành dữ liệu (graph.json) thay vì suy đoán, và biến trạng thái thành sổ sự kiện append-only thay vì trí nhớ.

## Ba bộ phận

**Runtime** `harness/scripts/orca-graph.py` đọc PLAN.md thành graph có lớp topo, cảnh báo hai node song song ghi cùng file, rồi cho orchestrator chạy vòng `next → lock → dispatched → done`. Khoá là file `O_EXCL` có lease; hết lease thì node về `unknown` chứ không tự thành `failed`. Mỗi lần giao lại tăng `gen`, kết quả mang gen cũ bị chặn. Từ bản v2, graph có cấp chứa mẹ con, deps xuyên graph, kiểm cycle in đường cụ thể, plan version khi build lại, và control pause/cancel phân biệt "đã yêu cầu" với "đã dừng".

**Hai file vẽ** `fdk/tools/graph-viz.py` (một graph, node hình tròn, bấm ra thẻ, lưới ẩn sau nút) và `fdk/tools/graph-atlas.py` (bản đồ 2D mọi graph, hàng là cấp chứa). Cả hai theo theme docs-site-macos, có toggle sáng tối và in đường dẫn thật.

**Sổ câu trả lời của model.** Năm câu hỏi (cần gì, song song gì, phụ thuộc gì, tồn tại để làm gì, liên hệ graph cũ) được tool trả lời tất định trước. Phần model bổ sung phải ghi qua `answer` kèm nhãn `chắc | gợi-ý | không-biết` và nguồn mở được. `audit` mở lại từng nguồn theo rubric user chốt: đúng 1, sai 0, không biết 0.3, gợi ý có nguồn thật 0.5, **bịa nguồn 0**.

## Vì sao state được thiết kế như vậy

Các luật bền state vay từ hai PRD Reprise ([[120926-reprise-prd-work-continuity]], [[120926-reprise-graph-engine-prd]]) thay vì tự nghĩ: op_key idempotent, CAS revision, generation, lease và reaper về unknown, ba chiều state/verified/fresh tách nhau, ghi cache qua temp và atomic rename, test kill -9 thật. Lý do là những luật này đã trả giá ở một sản phẩm product-grade; tự phát minh lại thì sẽ thiếu đúng những ca hiếm đó.

## Giới hạn nói thẳng

Khoá chỉ kiểm soát dispatch, không kiểm soát side-effect của agent đã chạy. Agent chết nửa chừng chỉ phát hiện qua lease và verify, không rollback tự động. Coupling ngầm không lộ ra file thì không bắt được. Sổ Orca chỉ sync một chiều. Atlas quá vài trăm node cần graphviz. Và graph không sửa được con số "headless giao khoảng một phần năm", nó chỉ làm con số đó nhìn thấy được.

## Origin

- Yêu cầu user 12/09/2026 trong phiên /fdk: dựa trên orca-workflow tạo orca-graph, có rubric chấm câu trả lời của model.
- Proposal: `scratchpad/120926-orca-graph-PROPOSAL.md` (duyệt cùng ngày). PLAN v2: `llmwiki/wiki/sources/draft/120926-orca-graph-v2-PLAN.md`, chạy bằng chính orca-graph.
- Quyết định kiến trúc: [[ADR-018-orca-graph-file-based-graph-engine]]. Test: `harness/tests/test_orca_graph.py` 13 ca.
