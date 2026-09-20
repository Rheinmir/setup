---
type: source
title: "Reprise Graph Engine PRD v1.1 — phần bổ sung §22–30: edge có lý do, resource claims, item pipeline, verifier packet, discovery có giới hạn, cost envelope, 4 pattern và 18 ticket GX"
status: ingested
tags: [prd, reprise, graph-engine, topology, edge-audit, resource-claims, verifier, discovery, cost-envelope, orca-graph]
timestamp: 2026-09-20
id: 200926-reprise-graph-engine-prd-v11
relations:
  - {rel: informs, to: orca-graph}
  - {rel: derives-from, to: 120926-reprise-graph-engine-prd}
  - {rel: raw, path: "llmwiki/raw/Reprise-Graph-Engine-Full-Cycle-PRD (1).md"}
---

# Reprise Graph Engine PRD v1.1 — thực thi song song có kiểm chứng

## Tóm tắt

Bản v1.1 dài 2.741 dòng, giữ nguyên nền v1.0 (đã ingest ở [[120926-reprise-graph-engine-prd]]) và thêm chín phần mới từ §22 đến §30. Bản này ra đời sau khi tác giả đối chiếu PRD cũ với một bài thực hành "Graph Engineering" trên X của rvaniaaa và bài multi-agent research của Anthropic. Kết luận ở §22.2 nói thẳng: nền durable engine của v1.0 đủ tốt, không cần viết lại, nhưng còn mơ hồ ở chỗ tối ưu topology và vận hành các tập việc lớn. Tài liệu vẫn là đặc tả, chưa phải engine đã chạy, và tự nhận điều đó ở nhiều chỗ.

Ngoài chín phần mới, v1.1 sửa vài câu ở phần lõi để nhất quán. Câu quan trọng nhất nằm ở §6: **wave là hình chiếu để giải thích plan, không phải rào chắn toàn cục**. Một node đủ dependency và được cấp tài nguyên thì chạy ngay, không chờ mọi việc của wave trước xong.

## Tám điều phải diễn đạt chính xác (§22.3)

Đây là phần đáng đọc nhất vì nó chặn những câu nói quá tay mà tool orchestration hay mắc:

1. Hai node không truyền dữ liệu cho nhau chưa chắc chạy song song được, vì còn ràng buộc phê duyệt hoặc tranh chấp tài nguyên.
2. Code tất định không tốn token nhưng vẫn tốn CPU, I/O và công kiểm thử; không được ghi tổng chi phí bằng 0.
3. Reviewer có context riêng chỉ giảm ảnh hưởng lời của worker. Cùng nguồn sai hoặc cùng model vẫn sinh lỗi tương quan, và biểu quyết đa số không vượt được cổng chứng cứ cứng.
4. Test chạy thật vẫn có thể thiếu coverage hoặc oracle sai. Anchor có phạm vi và hạn dùng, không phải chân lý tuyệt đối.
5. Pipeline giảm chờ thừa ở từng item, không bảo đảm tổng thời gian hoàn tất ngắn hơn.
6. Một vòng discovery không ra finding mới không có nghĩa là đã rà hết. Lỗi hay timeout không được tính là vòng "khô".
7. Số item, số agent, độ song song, số node và số lần gọi model là năm con số khác nhau.
8. Schema đúng chỉ chứng minh hình dạng, chưa chứng minh nội dung. Verifier phải giữ claim ID khi lọc hay sắp lại kết quả.

## Các cơ chế mới

**Edge có lý do (§23.2–23.3).** Mỗi cạnh phụ thuộc mang một `reason_class`: `data`, `contract`, `acceptance`, `effect_order`, `control` là cạnh cứng không bỏ được dù không truyền artifact; `scheduling_preference` là cạnh chỉ do thứ tự viết, có thể đề xuất bỏ. Thuật toán audit không âm thầm xoá gì: cạnh cứng thiếu lý do thì báo `EDGE_UNJUSTIFIED` để người sửa, cạnh preference thì sinh topology diff kèm ước lượng critical path trước và sau. Thiếu dữ liệu thì giữ cạnh, vì "không tìm thấy dependency" không bằng "đã chứng minh độc lập".

**Resource claims (§23.4).** Tranh chấp tài nguyên không phải là cạnh DAG. Mỗi claim có `resource_key`, `mode` (shared, exclusive, capacity) và được cấp lúc admission. Hai worktree git tách nhau vẫn phải khai claim nếu dùng chung nhánh remote, schema DB, cổng test hay quota provider. Admission lấy mọi claim theo thứ tự khoá cố định hoặc nhả hết rồi xếp hàng, không giữ A trong lúc chờ B.

**Item pipeline và completeness (§24).** Phân biệt bốn tập: source universe, selected manifest, expected stage membership, accepted outputs. So **tập định danh**, không so số lượng: `{A,A,B}` và `{A,B,C}` cùng ba phần tử nhưng thiếu C. Kết quả `null` là outcome thiếu có ID, không được `filter(Boolean)` cho biến mất. Bốn chế độ stage: `item_local`, `keyed_reduce`, `sealed_batch`, `final_delivery`. Ví dụ latency §24.7 cho ba item 8/2/2 giây: serial 18 giây, batch 10 giây, pipeline 10 giây nhưng item đầu xong sau 4 giây thay vì 10. Pipeline thắng ở thời gian tới kết quả đầu, không thắng ở makespan.

**Verifier packet và anchors (§25).** Verifier nhận claim, nguồn chính, rubric đã đóng băng; không nhận transcript, lời tự chấm hay chữ "đã pass" của worker. Ba lớp kết luận: shape validation, judgment review, anchor-backed verification. Verdict là `supported`, `refuted`, `inconclusive`, tách khỏi trạng thái hạ tầng (`ok`, `error`, `timeout`, `cancelled`). Lỗi không phải refuted, inconclusive không phải supported. Hàm mẫu `reconcile_verdicts` ghép verdict theo ID chứ không theo vị trí mảng. Luật đóng băng: executor không được tự sửa test hay rubric để biến đỏ thành xanh; sửa hợp lệ đi qua change request có phiên bản.

**Discovery có giới hạn (§26).** Discovery mở rộng tập ứng viên, repair sửa artifact hỏng, replan đổi plan; ba bộ đếm riêng, chung một ngân sách gốc. Seen ledger ghi cả finding bị bác để không phát hiện lại mãi. Dry streak chỉ tăng khi vòng **hoàn tất** và không có ứng viên mới; vòng lỗi đưa streak về 0. Hàm mẫu `next_dry_streak` cho chuỗi (đủ,0) → (thiếu,0) → (đủ,0) ra 1 → 0 → 1, tức chưa hội tụ. Mặc định pilot: tối đa 4 vòng, dừng sau 2 vòng khô liên tiếp, tối đa 20 ứng viên. Khi chạm trần và khô cùng lúc, lý do chính là trần.

**Cost envelope và scale (§27).** Hai mươi item với 1 planner, mỗi item 1 worker và 1 verifier, 1 synthesis là 1 + 20 + 20 + 1 = **42** lần gọi trước retry. Thay bằng 3 reviewer mỗi item thì thành **82**. Không được nói "20 agent" thay cho tổng số lần gọi. Trần phạm vi (20 item) khác trần song song (2 root, 4 leaf trên host). Mở rộng phạm vi và tăng song song là hai thí nghiệm riêng, không tự nhân đôi sau mỗi lần thành công.

**Bốn pattern theo chuẩn SWH (§28.1).** GP-01 review item độc lập, GP-02 tổng hợp chứng cứ, GP-03 discovery có giới hạn, GP-04 giao module app. Cùng topology không bảo đảm cùng ngữ nghĩa; validator và anchor vẫn theo miền. Liên quan [[solid-what-how]].

**UI/API (§28.4).** Người dùng phải thấy node đang "chờ vì data, gate, resource, queue hay budget", thấy "19/20 xong, 1 lỗi" thay cho một báo cáo xanh, và không phải đọc canvas 2.000 node để biết vì sao app chưa xong.

## Backlog và nghiệm thu

Mười tám ticket GX-01 đến GX-18, tổng 42 ngày công, chia năm mốc X1–X5. Hai mươi tám kịch bản nghiệm thu VT-01 đến VT-28 ở §30.1. Tác giả khuyên thứ tự áp dụng đầu tiên ở §30.3: **audit cạnh, item manifest, identity reducer, verifier packet, tất cả trên fixture tất định**, đo lỗi và overhead trước khi mở nhiều model worker. §30.2 ghi rõ không đặt điều kiện "pipeline luôn nhanh hơn" hay "phải chạy nhiều agent".

## Áp vào orca-graph v3 (20/09/2026)

orca-graph là tool file-based một máy ([[ADR-018-orca-graph-file-based-graph-engine]]), nên chỉ nhận phần nằm trong tầm đó. Bảng dưới là kế hoạch của PLAN `200926-orca-graph-v3-PLAN`; trạng thái thực thi xem graph cùng tên và concept [[orca-graph]].

| Mục PRD | Vào orca-graph thế nào | Kịch bản VT |
|---|---|---|
| §23.2–23.3 edge có lý do, audit | `**Depends:** Task 1 (data), Task 2 (preference)`; lệnh `audit-edges` chỉ đọc, báo `EDGE_UNJUSTIFIED`, đề xuất bỏ cạnh preference, critical path trước và sau | VT-01, VT-02 |
| §23.4 resource claims | `**Resources:** db-migration(exclusive), api-x(shared)`; `lock` từ chối khi claim xung đột đang được giữ | VT-03, VT-04 |
| §28.4 lý do chờ | `ask <id> waiting` phân loại data, gate, resource, queue, control | QA-GX-15 |
| §25.5, §24.1 ghép theo định danh | lệnh `reconcile-items` dùng nguyên hàm `reconcile_verdicts` | VT-09, VT-10, VT-17 |
| §26.4 dry streak | hàm `next_dry_streak` kèm lệnh `dry-streak` | VT-19 |
| §27.2 cost envelope | lệnh `cost-envelope` đếm planner, worker, reviewer, synthesis và trần retry | VT-23 |
| §30.1 ma trận VT | `evals/vt-matrix.json` ánh xạ từng VT sang test hoặc ghi rõ ngoài phạm vi | toàn bộ |

Ngoài phạm vi và nói thẳng: item pipeline bền với outbox và backpressure (§24.3), layered fan-in theo token (§24.6), anchor registry, routing model theo eval floor, scale proposal. Những thứ này cần ledger giao dịch và scheduler thật, tức là engine khác.

## Origin

- Nguồn thô: `llmwiki/raw/Reprise-Graph-Engine-Full-Cycle-PRD (1).md` (user đưa ngày 20/09/2026 thay cho bản v1.0 cùng tên, yêu cầu ingest phần mới rồi nâng cấp orca-graph bằng chính orca-graph).
- Bản trước: [[120926-reprise-graph-engine-prd]] (v1.0, §1–21). Trang này chỉ ghi phần chênh §22–30 và các câu sửa ở lõi, không lặp lại nội dung cũ.
