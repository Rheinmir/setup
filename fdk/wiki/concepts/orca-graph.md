---
type: concept
title: "orca-graph — phân việc dạng đồ thị phụ thuộc có khoá, lease, generation và state bền; model trả lời có nhãn và bị audit"
status: implemented
tags: [orca-graph, dag, dispatch, state, lease, generation, evidence, rubric]
timestamp: 2026-09-20
id: orca-graph
relations:
  - {rel: extends, to: orca-workflow}
  - {rel: depends-on, to: plan}
  - {rel: touches, path: harness/scripts/orca-graph.py}
  - {rel: touches, path: fdk/tools/graph-viz.py}
  - {rel: touches, path: fdk/tools/graph-atlas.py}
  - {rel: touches, path: skills/orca-graph/SKILL.md}
  - {rel: touches, path: harness/tests/test_control_room.py}
  - {rel: informed-by, to: 200926-reprise-graph-engine-prd-v11}
---

# orca-graph — phân việc dạng đồ thị phụ thuộc

## Bài toán thật

`/orca-workflow` dispatch theo từng `### Task` trong PLAN.md, nhưng PLAN chỉ có Interfaces Consumes/Produces, không có dòng phụ thuộc. Cái gì chạy song song và cái gì phải chờ do Claude đoán trong đầu, không ai kiểm được, và khi phiên kết thúc thì "đang chạy tới đâu" biến mất cùng context. Sổ task của Orca có `--deps` nhưng là runtime-global, không có trường dự án, nên không dùng làm nguồn chân lý được.

Điểm đòn bẩy được chọn theo Meadows là **đổi luồng thông tin**: biến phụ thuộc thành dữ liệu (graph.json) thay vì suy đoán, và biến trạng thái thành sổ sự kiện append-only thay vì trí nhớ.

## Ba bộ phận

**Runtime** `harness/scripts/orca-graph.py` đọc PLAN.md thành graph có lớp topo, cảnh báo hai node song song ghi cùng file, rồi cho orchestrator chạy vòng `next → lock → dispatched → done`. Khoá là file `O_EXCL` có lease; hết lease thì node về `unknown` chứ không tự thành `failed`. Mỗi lần giao lại tăng `gen`, kết quả mang gen cũ bị chặn. Từ bản v2, graph có cấp chứa mẹ con, deps xuyên graph, kiểm cycle in đường cụ thể, plan version khi build lại, và control pause/cancel phân biệt "đã yêu cầu" với "đã dừng". Sau v2 có thêm ba lớp gác: `watch` chạy nền như daemon và `heartbeat` gia hạn lease cho node đang chạy dài (control-room đọc chung sổ); node khai `**QC:**` cạnh `**Verify:**`, không có vai QC riêng, và đổi lệnh QC cũng làm node mất hiệu lực như đổi verify (GH#163); `enforce_allowed_paths` so file đổi trước/sau lần chạy với `files` của node, mặc định cảnh báo, `--strict` phục hồi cứng (GH#162).

**Hai file vẽ** `fdk/tools/graph-viz.py` (một graph, node hình tròn, bấm ra thẻ, lưới ẩn sau nút) và `fdk/tools/graph-atlas.py` (bản đồ 2D mọi graph, hàng là cấp chứa). Cả hai theo theme docs-site-macos, có toggle sáng tối và in đường dẫn thật.

**Sổ câu trả lời của model.** Năm câu hỏi (cần gì, song song gì, phụ thuộc gì, tồn tại để làm gì, liên hệ graph cũ) được tool trả lời tất định trước. Phần model bổ sung phải ghi qua `answer` kèm nhãn `chắc | gợi-ý | không-biết` và nguồn mở được. `audit` mở lại từng nguồn theo rubric user chốt: đúng 1, sai 0, không biết 0.3, gợi ý có nguồn thật 0.5, **bịa nguồn 0**.

## Vì sao state được thiết kế như vậy

Các luật bền state vay từ hai PRD Reprise ([[120926-reprise-prd-work-continuity]], [[120926-reprise-graph-engine-prd]]) thay vì tự nghĩ: op_key idempotent, CAS revision, generation, lease và reaper về unknown, ba chiều state/verified/fresh tách nhau, ghi cache qua temp và atomic rename, test kill -9 thật. Lý do là những luật này đã trả giá ở một sản phẩm product-grade; tự phát minh lại thì sẽ thiếu đúng những ca hiếm đó.

## Bản v3: topology có lý do, và engine ra ở riêng (20/09/2026)

PRD Reprise lên v1.1 ([[200926-reprise-graph-engine-prd-v11]]) chỉ ra chỗ bản v2 còn mơ hồ: graph biết *ai chờ ai* nhưng không biết *vì sao chờ*. Bản v3 thêm đúng phần đó, trong tầm một tool file-based.

Cạnh phụ thuộc giờ mang lý do: `**Depends:** Task 1 (data), Task 2 (preference)`. Năm lớp cứng (data, contract, acceptance, effect_order, control) không bỏ được dù không truyền artifact, vì cổng duyệt không mang payload vẫn là ràng buộc thật. Lớp `preference` là cạnh chỉ do thứ tự viết. Lệnh `audit-edges` chỉ đọc: cạnh thiếu lý do thì báo `EDGE_UNJUSTIFIED` và giữ nguyên, cạnh preference thì đề xuất bỏ kèm critical path trước và sau, và nếu hai node của một cạnh preference cùng ghi một file thì tool từ chối đề xuất bỏ. Nguyên tắc vay từ PRD: "không tìm thấy dependency" không bằng "đã chứng minh độc lập".

Tranh chấp tài nguyên tách khỏi DAG. Hai task độc lập dùng chung nhánh tích hợp hay schema DB khai `**Resources:** db-migration(exclusive)` và `lock` tuần tự hoá chúng lúc chạy, thay vì người viết PLAN phải thêm một cạnh Depends giả. Key do tool chuẩn hoá để alias khác chữ không lách được; admission lấy hết claim hoặc không lấy gì, dưới một mutex cho cả store. Từ đó `ask <id> waiting` nói được mỗi node đang chờ vì data, gate, resource, queue, control hay retry, tức là phân biệt được *ready* với *admitted*.

Ba lệnh nhỏ chép nguyên hàm mẫu của PRD: `reconcile-items` ghép kết quả theo định danh (đủ ba dòng `{A,A,B}` vẫn thiếu C), `dry-streak` cho vòng discovery, `cost-envelope` đếm tổng lần gọi model thay vì nói "N agent". Và `add-node` cho trường hợp user yêu cầu thêm việc giữa chừng: nó sửa PLAN gốc rồi build lại, nên PLAN vẫn là nguồn và lịch sử không mất.

Thay đổi lớn hơn về tổ chức: **engine rời repo framework sang `Rheinmir/orca-graph`**. Lý do là engine đã đủ lớn để cần lịch sử, test và thước đo riêng. Repo đó mang bộ eval `evals/vt-matrix.json` ánh xạ 28 kịch bản nghiệm thu VT của PRD sang test thật; bản 3.0.0 phủ 15 kịch bản, 13 kịch bản còn lại ghi `out_of_scope` kèm lý do thay vì nhận vơ, và `history.jsonl` giữ một dòng mỗi lần chạy kèm sha của engine. Theo phân loại [[adapt-modes]] đây là kiểu KÉO NGOÀI: framework chỉ giữ bản mirror SKILL.md, provenance, và ba shim ở đúng đường dẫn cũ. Shim chạy engine thật trong globals của chính nó nên `__file__` vẫn là đường shim, nhờ vậy `overstack_paths`, control-room và máy khách không phải đổi gì. Trình cài hiện module này như một option đã tick sẵn; Enter là kéo, `--no-graph` là bỏ.

## Giới hạn nói thẳng

Khoá chỉ kiểm soát dispatch, không kiểm soát side-effect của agent đã chạy. Agent chết nửa chừng chỉ phát hiện qua lease và verify, không rollback tự động. Coupling ngầm không lộ ra file thì không bắt được. Sổ Orca chỉ sync một chiều. Atlas quá vài trăm node cần graphviz. Và graph không sửa được con số "headless giao khoảng một phần năm", nó chỉ làm con số đó nhìn thấy được.

## Origin

- Yêu cầu user 12/09/2026 trong phiên /fdk: dựa trên orca-workflow tạo orca-graph, có rubric chấm câu trả lời của model.
- Proposal: `scratchpad/120926-orca-graph-PROPOSAL.md` (duyệt cùng ngày). PLAN v2: `llmwiki/wiki/sources/draft/120926-orca-graph-v2-PLAN.md`, chạy bằng chính orca-graph.
- Quyết định kiến trúc: [[ADR-018-orca-graph-file-based-graph-engine]]. Test (thời v2): `harness/tests/test_orca_graph.py` 13 ca — từ v3 file này đã chuyển sang repo engine `Rheinmir/orca-graph` (`tests/test_orca_graph.py`).
- Bản v3 (20/09/2026): PLAN `llmwiki/wiki/sources/draft/200926-orca-graph-v3-PLAN.md` chạy bằng chính orca-graph (graph `200926-orca-graph-v3`); nguồn [[200926-reprise-graph-engine-prd-v11]]. Từ bản này test của engine nằm ở repo `Rheinmir/orca-graph` (`tests/`, `evals/`); trong framework còn `harness/tests/test_control_room.py` (shim + cockpit) và `harness/tests/install-graph-option-test.sh` (option cài).
- Bổ sung 2026-09-18 (lint dọn draft): daemon/heartbeat từ `140926-orca-graph-daemon-PLAN`, QC gate và giới hạn ghi từ `170926-orca-graph-no-separate-qc-role` + `170926-orca-graph-no-write-sandbox` (nay trong `draft/archive/`).
