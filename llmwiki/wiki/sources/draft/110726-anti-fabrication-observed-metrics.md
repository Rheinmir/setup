---
type: issue
kind: feature-gap
title: "Anti-fabrication mở rộng: cấm bịa số liệu về người-dùng/thế-giới mà agent không đo được"
status: open
assignee: "@Rheinmir"
dispatch: Claude
entry: /fdk
priority: P2
tags: [issue, anti-fabrication, claim-receipts, hallucination, failure-flywheel]
timestamp: 2026-07-11
id: 110726-anti-fabrication-observed-metrics
source_session: distill từ một plugin học-tập cộng đồng — luật cứng "cấm bịa số của người học"
---

# Issue: Cấm bịa số đo về người-dùng/thế-giới (self-reported / observed metric)

## Vấn đề (một câu)
`claim-receipts.py` hiện chỉ chống bịa **tham chiếu file/API** (reference có resolve trên đĩa không), nhưng KHÔNG bắt được loại bịa nguy hiểm khác: agent tự chế ra **số đo về trạng thái người-dùng/thế-giới mà nó không hề quan sát** (vd điểm tự tin, tỉ lệ, "user nói X" khi user chưa nói) — số nghe rất tự tin nhưng không có nguồn.

## Bối cảnh & bằng chứng
- Đã có `harness/claim-receipts.py` + `harness/claim-receipts.config.yaml`: taxonomy claim (`tool-output / inference / external-testimony / absence / ungrounded-opinion`) và verify **references resolve**. Đây là "Tool Receipts / CiteAudit" — chống bịa citation.
- Gap: một con số như "độ tự tin của người dùng = 0.7" hay "3/6 concept đã nắm" là claim về **observed state**, không phải reference file → lọt qua claim-receipts hoàn toàn.
- Bằng chứng từ nguồn tham khảo: một grader mù bóc được worker **tự bịa điểm tự tin mà người dùng chưa hề khai** → nguồn đó biến "cấm bịa số của người học" thành **luật cứng trong code**. Đây chính là loại claim overstack chưa gate.
- Khớp `failure-flywheel` class "hallucination" nhưng ở tầng số-liệu-về-chủ-thể, không phải tầng citation.

## Phạm vi
- `harness/claim-receipts.config.yaml` (thêm claim class) + `claim-receipts.py` (heuristic phát hiện số gán cho user/world không có nguồn).
- Cân nhắc một R-rule harness: "số đo về người-dùng/thế-giới phải có nguồn (user khai hoặc tool đo); nếu không → vi phạm."
- Universal.

## Không thuộc phạm vi
- Không mở rộng thành verify ngữ nghĩa tuỳ ý (giữ hẹp: số/metric gán cho chủ thể mà agent không đo).
- Không đụng resolver code-graph đang là unknown của claim-receipts (issue riêng).

## Hướng gợi ý (không bắt buộc)
- Thêm claim class `self-reported-metric` / `observed-metric` vào `claim_taxonomy`.
- Heuristic: số + lượng-từ gán cho "user/người dùng/người học/họ" mà không kèm trích dẫn nguồn (user turn / tool result) → cờ.
- Bắt đầu ở `strictness: advisory` như phần còn lại của claim-receipts; siết `strict` khi heuristic đủ chín.

## Tiêu chí HOÀN THÀNH
- Có claim class cho observed/self-reported metric.
- `--self-test` chứng minh: một số tự tin bịa về user bị cờ, một số có nguồn (user khai) thì không.

## Assign & lý do
- @Rheinmir / Claude / `/fdk`: sửa đúng vào adapter claim-receipts hiện có, người giữ harness nên quyết mức siết + có nâng lên R-rule không.

## Origin
Raised bởi `/raise-issue` (phiên 2026-07-11) khi distill một plugin học-tập cộng đồng (n=1) có luật cứng "cấm bịa số của người học". Nguồn chỉ để tham khảo ý tưởng; không kèm tác giả/repo. Đối chiếu `harness/claim-receipts.config.yaml` để xác nhận gap nằm ngoài phạm vi reference-resolve hiện tại.
