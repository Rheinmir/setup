---
type: issue
kind: feature-gap
title: "Gold-set + QWK meta-eval: đo độ ĐÚNG của chính grader (ai chấm người-chấm)"
status: open
assignee: "@Rheinmir"
dispatch: Claude
entry: /fdk
priority: P2
tags: [issue, evaluation, meta-eval, gold-set, qwk, wikieval, trace-grader]
timestamp: 2026-07-11
id: 110726-gold-set-meta-eval-grader
source_session: distill từ code thật một plugin học-tập cộng đồng — gold/assessor-gold.jsonl + QWK
---

# Issue: Không ai chấm độ đúng của người-chấm — thiếu gold-set + QWK cho grader

## Vấn đề (một câu)
`wikieval`/`trace-grader`/assessor-agent chấm output của agent khác, nhưng KHÔNG có bộ gold cố định + thước đo (QWK) để trả lời "grader chấm ĐÚNG bao nhiêu" — grader có thể trôi mà không ai biết.

## Bối cảnh & bằng chứng
- Bằng chứng từ code tham khảo (đọc trực tiếp, không kèm tác giả/repo): plugin học-tập cộng đồng ship `gold/assessor-gold.jsonl` (66 mẫu vàng) + đo grader bằng **QWK** (quadratic weighted kappa), và receipt có thể được *weight theo QWK mà grader đó thực đo* — tức grader tự nó là một đối tượng bị đo, không phải trọng tài tuyệt đối.
- Overstack: `wikieval` có baseline hồi-quy cho OUTPUT, nhưng không có gold-set để đo chính GRADER; `trace-grader`/council chairman cũng vậy. Đây là tầng meta-eval còn trống.
- Khớp triết lý "hệ thống cãi lại sự lạc quan của chính nó": đo grader = không cho grader tự phong thánh. Bổ trợ [[110726-eval-blinding-grader-context]] (blinding lo *đầu vào* grader; issue này lo *độ chính xác* grader).

## Phạm vi
- Bộ gold `*.jsonl` (item + rubric + verdict vàng) + scorer QWK tất định + wiring vào wikieval như một probe.
- Universal (chuẩn evaluation).

## Không thuộc phạm vi
- Không xây học-tập/FSRS (sản phẩm gốc).
- Không thay baseline output-eval hiện có — đây là tầng meta bổ sung, không thay thế.

## Hướng gợi ý (không bắt buộc)
- Seed một gold-set nhỏ từ các lần chấm đã có sự đồng thuận người; scorer QWK thuần Python + `--self-test`.
- Thêm probe medic/wikieval: grader mới hoặc prompt-grader đổi → chạy lại gold-set, QWK tụt dưới ngưỡng = cờ.

## Tiêu chí HOÀN THÀNH
- Có gold-set + scorer QWK tất định (self-test xanh).
- Chạy được "đo grader hiện tại" ra một con số QWK, và một ngưỡng regress.

## Assign & lý do
- @Rheinmir / Claude / `/fdk`: chuẩn evaluation cấp framework; cần quyết nguồn gold + ngưỡng.

## Origin
Raised bởi `/raise-issue` (phiên 2026-07-11) khi đọc CODE THẬT (không chỉ bài giới thiệu) của một plugin học-tập cộng đồng: phát hiện gold-set + QWK meta-eval cho grader — gap tầng meta overstack chưa có. Nguồn chỉ tham khảo, không kèm tác giả/repo.
