---
type: issue
kind: feature-gap
title: "Evaluation blinding: che context sinh output khỏi grader để chống mồi/lạc quan"
status: open
assignee: "@Rheinmir"
dispatch: Claude
entry: /fdk
priority: P2
tags: [issue, evaluation, blinding, wikieval, trace-grader, council]
timestamp: 2026-07-11
id: 110726-eval-blinding-grader-context
source_session: distill từ một plugin học-tập cộng đồng (spaced-repetition, n=1) — tách rời tutor↔grader
---

# Issue: Evaluation blinding — grader không được thấy quá trình sinh ra output

## Vấn đề (một câu)
Các grader/evaluator nội bộ (wikieval, trace-grader, và các agent "chấm" khác) hiện có thể nhìn thấy TOÀN BỘ transcript/quá trình sinh ra output khi chấm — bị mồi (anchoring) theo lời tự-biện-hộ của worker, nên điểm có xu hướng lạc quan; cần một chuẩn "blind theo context" tách riêng.

## Bối cảnh & bằng chứng
- Overstack đã có **blinding một phần**: `harness/scripts/council.py` blind peer-rank bằng cách **ẩn DANH TÍNH** giữa các seat + anchor guard (xem [[council]]). Đây là chống "model thiên vị chính nó", KHÔNG phải chống "grader bị mồi bởi quá trình".
- Một loại blinding KHÁC còn thiếu: grader chỉ được nhận **(đáp án chuẩn + câu trả lời)**, KHÔNG được nhận **session/reasoning/quá trình** đã tạo ra câu trả lời. Bằng chứng thực nghiệm từ nguồn tham khảo: khi grader mù được tách hẳn khỏi buổi làm việc, nó bóc được kết quả kém mà bên "làm" tự cho là ngon (1 đúng / 4 lơ mơ / 1 sai vs. tự đánh giá "ngon lành").
- Khớp triết lý overstack sẵn có: "hệ thống biết cãi lại sự lạc quan của chính nó" — anchor guard (council), adversarial verify.

## Bằng chứng code (đọc trực tiếp nguồn tham khảo, 2026-07-11)
Spec assessor của plugin tham khảo hiện thực HÓA đúng ranh giới này ở tầng code/agent-spec:
- grader "receives only items and rubrics", "**Deliberately blind to the tutoring dialogue**", "You never see the lesson, and no context about how the session 'went' may influence you";
- "**Enthusiasm, fluency, and confidence are not evidence**" — high-confidence-but-wrong vẫn là lapsed;
- payload grader là JSON tối thiểu `{items:[{topic,node,rubric,probe,production,confidence,kind}]}` — KHÔNG có trường transcript/quá trình.
→ Xác nhận đây là contract khả-thi, không chỉ khẩu hiệu: một schema đầu vào grader loại trừ tường minh mọi thứ ngoài (đáp-án-chuẩn + output).

## Phạm vi
- `skills/wikieval`, `skills/trace-grader`, và bất kỳ chỗ nào một agent chấm output của agent khác.
- **Thiết kế trước**: định nghĩa grader-payload contract (schema JSON tối thiểu) — đây là việc design-first, không nhồi guard khi format chưa tồn tại.
- Universal (chuẩn evaluation), không local một dự án.

## Không thuộc phạm vi
- Không đụng cơ chế blind-DANH-TÍNH của council (đã có, giải quyết vấn đề khác — đừng gộp).
- Không xây học-tập/spaced-repetition (đó là sản phẩm gốc, ngoài overstack).

## Hướng gợi ý (không bắt buộc)
- Định nghĩa **grader input schema tối thiểu**: `{rubric/đáp_án_chuẩn, output_cần_chấm}` — loại trừ transcript/CoT/self-report của worker.
- Kiểm chứng bằng một assert: nếu payload gửi cho grader chứa trường "process/session/transcript" → fail-fast (contract violation).
- Tuỳ chọn: A/B đo độ lệch điểm giữa grader-thấy-process vs grader-mù trên vài mẫu để chứng minh giá trị.

## Tiêu chí HOÀN THÀNH
- wikieval/trace-grader có ranh giới input tường minh: grader KHÔNG nhận quá trình sinh output.
- Có 1 check tất định fail khi context bị rò vào payload grader.

## Assign & lý do
- @Rheinmir / Claude / `/fdk`: đây là chuẩn evaluation cấp framework, cùng họ với council anchor-guard — nên do người giữ harness quyết wiring.

## Origin
Raised bởi `/raise-issue` (phiên 2026-07-11) khi distill một plugin học-tập cộng đồng (n=1) dùng "grader mù tách khỏi buổi học". Nguồn chỉ để tham khảo ý tưởng; không kèm tác giả/repo. Đối chiếu với `skills/council/SKILL.md` (blind danh-tính) để xác nhận đây là gap KHÁC.
