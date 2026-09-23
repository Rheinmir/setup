---
type: source
title: "Reprise Intent Engine PRD v1.0 — biến yêu cầu mơ hồ thành việc đủ rõ, và cách hệ đó TỰ HỌC: receipts, chỉ số có mẫu số, bộ dữ liệu vàng theo họ, draft probe, tái dùng có hạch toán"
status: ingested
tags: [prd, reprise, intent-engine, self-learning, evolve, telemetry, eval, flywheel]
timestamp: 2026-09-23
id: 230926-reprise-intent-engine-prd
relations:
  - {rel: informs, to: failure-flywheel}
  - {rel: informs, to: orca-graph}
  - {rel: derives-from, to: 120926-reprise-graph-engine-prd}
  - {rel: raw, path: llmwiki/raw/prd/Reprise-Intent-Engine-Product-Grade-PRD.md}
---

# Reprise Intent Engine (RIE) — engine làm rõ ý định, và cơ chế tự học của nó

## Tóm tắt

Tài liệu 1.222 dòng đặc tả một engine đứng TRƯỚC Graph Engine: nhận một yêu cầu mơ hồ của người dùng ("làm cho tôi cái app đặt phòng"), tự tìm hiểu trong phạm vi được phép, chỉ hỏi khi câu hỏi mở được một hành động cụ thể, rồi bàn giao một ExecutionBrief đủ rõ để RGE chạy. Phần đáng học nhất với ta không phải luồng hỏi–đáp, mà là **cách hệ đó cải tiến chính nó mà không tự bịa luật** — user giao đọc ngày 23/09/2026 với câu hỏi "xem PRD này tự học và cải tiến hệ thống bằng cách nào".

## Nguyên tắc nền: tách chạy khỏi cải tiến

RIE không tự sửa mình. Nó chỉ tạo *improvement proposal* và gửi sang RSE (Evolve) — một engine riêng, **không nằm trên đường chạy bắt buộc của mỗi request**. Một câu trả lời riêng của một người dùng không bao giờ được tự đưa vào profile toàn cục; muốn vào thì phải qua vòng đánh giá có tập giữ kín và có người quyết. Đây là hàng rào chống "học vẹt từ một ca lẻ", và nó trùng đúng tinh thần cổng `propose → gate` của ta.

## Năm cơ chế học

**1. Receipts thay cho log.** Mỗi câu hỏi, mỗi default đã chọn, mỗi lần bàn giao, mỗi kết quả đều sinh một biên nhận có scope và nguồn. UI chỉ được nói theo biên nhận, không suy từ trạng thái lạc quan ("đã gửi" khác "đã chạy"). Việc học bắt đầu từ dữ liệu có thật, không từ bản ghi hội thoại.

**2. Chỉ số có mẫu số, kèm cột "không được suy".** Mười chỉ số: độ trung thành ý định, tỷ lệ phạm vi không nguồn, độ hữu ích câu hỏi, tỷ lệ hỏi lặp, thời gian tới tiến triển hữu ích (tách thời gian máy chạy và thời gian chờ người), rework do hiểu sai, tỷ lệ báo-sẵn-sàng-giả, gánh nặng người dùng, chi phí mỗi ca đã giải quyết, lợi ích ròng của tái dùng. Mỗi chỉ số ghi rõ suy diễn bị cấm — "ít câu hỏi hơn không mặc nhiên tốt hơn", "ca bỏ dở vẫn phải có mẫu số", "chi phí không rõ không được tính bằng 0", "người dùng không trả lời không có nghĩa là họ hài lòng".

**3. Bộ dữ liệu vàng chia theo họ tình huống.** 12 họ (yêu cầu nhỏ đã rõ; app mới mơ hồ; tham chiếu nhập nhằng; tiếp việc cũ; bug không tái hiện được; ràng buộc mâu thuẫn; "tự quyết"; không trả lời hoặc trả lời một phần; đổi ý giữa chừng…). Chia 6 phát triển / 3 chọn / 3 giữ kín và **cấm tách các câu cùng một họ sang hai tập**. Chấm bằng cả người (ý định có giữ đúng không, câu hỏi có đáng hỏi không, default có đảo ngược được không) lẫn máy (enum, nguồn, quyền, idempotency). Phải đặt giả thuyết trước khi thử một profile, giữ sàn chất lượng; số phiên nhỏ chỉ phát hiện bug, không chứng minh tổng quát.

**4. Học rẻ trước khi hỏi — draft probe có mục tiêu học.** Khi người dùng chưa có ý thích rõ và phương án biểu diễn được rẻ, hệ dựng một bản nháp nhỏ để họ chọn thay vì hỏi trừu tượng. Mỗi probe khai rõ nó định học điều gì, và tối đa một probe cho mỗi quyết định chưa giải.

**5. Tái dùng có hạch toán.** Template và profile nằm trong registry có version pin và báo cáo conformance. Lợi ích tái dùng phải trừ chi phí thích nghi, đánh giá và bảo trì; PRD đưa ví dụ hoà vốn (tạo template 180 phút, mỗi lần dùng tiết kiệm ròng 6 phút ⇒ hoà vốn sau 30 lần) và cấm kết luận "template tốt hơn vì được dùng nhiều lần". Kịch bản nghiệm thu QA-36 nói thẳng: tái dùng tăng mà chất lượng giảm thì **cấm tự promote**.

## Chống học sai

Câu trả lời có scope và hạn dùng, kèm "decision fingerprint" để phát hiện hỏi lặp cùng một quyết định. Người dùng đổi ý thì sinh change alert và fence công việc đang chạy, không ghi đè bản cũ. Khi chi phí tăng mà không có quyết định mới, hệ dừng episode và chẩn đoán trong phạm vi hẹp, có thể rollback profile. Rollback bằng version đã pin, không bằng cách xoá dữ liệu hay tua ngược hiệu ứng đã xảy ra.

## Đối chiếu với hệ đang có của overstack

| Cơ chế PRD | Ta đã có | Khoảng trống |
|---|---|---|
| Receipts mọi quyết định | `harness/metrics/*.jsonl`, capproof, provenance | Chưa có biên nhận cho **phản hồi UI của user** |
| Đếm lỗi theo lớp rồi mới ra luật | `flywheel` (ghi → đếm → ngưỡng → stub → người duyệt) | Ngưỡng 3 chưa hiệu chỉnh bằng dữ liệu thật |
| Bộ dữ liệu vàng theo họ | `wikieval` | Chưa có họ tình huống cho UI, chưa có tập giữ kín |
| Chỉ số có mẫu số | Cổng đếm FAIL/WARN | Chưa có "tỷ lệ lặp lại cùng một góp ý" |
| Cải tiến qua đề xuất, người duyệt | `/propose` → gate, `/raise-issue` | Đúng hướng, giữ nguyên |

## Cơ chế đã dựng từ tài liệu này: lỗi lặp quá 2 lần thành chỉ dẫn

User giao 23/09/2026: "thêm cơ chế nếu bugs hoặc failed hay error cứ hơn 2 lần thì sẽ được gói lại thành instruction/skill dùng cho lần kế". Đã hiện thực trong `harness/scripts/flywheel.py`:

- **Đếm tất định.** Mỗi lỗi được ghi dưới một lớp taxonomy (`failures.jsonl`, local). Hook `pre_tool_use` tự ghi lớp `spec-violation` mỗi khi một luật cắn, nên không phụ thuộc trí nhớ của agent.
- **Chạm ngưỡng là gói ngay.** `record()` gọi `pack_guardrail()`: lớp nào đạt `recurrence_threshold` (mặc định 3 — tức quá 2 lần) thì sinh một thẻ `harness/metrics/guardrails/failure-<lớp>.md` gồm số lần, triệu chứng lần gần nhất, và bảng "cách sửa đã dùng" của 8 lần gần nhất. Thẻ **chỉ chưng cất từ dữ liệu đã ghi**, không bịa luật mới — đúng ranh giới PRD đặt ra giữa "máy làm phần cơ học" và "người quyết luật là gì".
- **Dùng cho lần kế.** Hook `session_start` in 5 thẻ mới nhất ở đầu mỗi phiên (mục `🧯 [đã học]`) kèm đường dẫn, nên phiên sau đọc trước khi làm việc cùng loại. Thẻ được commit nên phiên khác và máy khác cùng học; lịch sử thô vẫn là file local.
- **Không tự phong luật.** Thẻ mang trạng thái "đã học, chưa duyệt": nó là chỉ dẫn để đọc, không cắn ở CI. Muốn thành luật cắn được thì vẫn `flywheel.py --draft <lớp>` rồi `/propose` — cổng người giữ nguyên (RULE-02 của skill).
- **Gói lại toàn bộ:** `python3 harness/scripts/flywheel.py --kind failure --guardrails`.

Đường dẫn dùng helper `harness_dir()` nên chạy đúng ở máy khách (`.harness/`), đã kiểm bằng `dot-layout-runtime-test.sh`.

**Khoảng trống còn lại, nói thẳng:** mới tự ghi được vi phạm bị hook chặn. Lỗi do test đỏ, cổng đỏ, hoặc do người dùng chỉ ra bằng mắt vẫn phải ghi tay. Muốn kín thì cần ghi tự động khi lệnh test/cổng trả mã lỗi — chưa làm vì dễ gây nhiễu, cần user quyết.

## Bài học tự rút trong chính phiên ingest

Luật "nút đổi giao diện phải là hàng dính đáy sidebar" đã nằm trong bộ nhớ từ 07/2026, nhưng khi dựng trang mới vẫn để viên nổi ở góc và user phải nhắc lại. Theo tinh thần PRD, chữ trong bộ nhớ là một *answer* chưa có *fingerprint* nên không ai kiểm được lúc chạy. Cách chữa đúng là biến nó thành thứ máy kiểm được — chính là việc trang `design-showcase.html` và luật `line-over-text` đã làm trong cùng phiên.

## Origin

- **Nguồn:** `llmwiki/raw/prd/Reprise-Intent-Engine-Product-Grade-PRD.md` (PRD v1.0, 20/09/2026, 1.222 dòng), đọc các mục §1.1 quan hệ với Evolve, §7 chính sách hỏi/tự quyết, §11.3–11.4 template và đo lợi ích tái dùng, §14.2 default profile, §16 RI-23 telemetry, §17.1–17.3 đánh giá và 36 kịch bản nghiệm thu.
- **Yêu cầu user:** 23/09/2026 — "lưu lại các lỗi đã sửa này và xem PRD này tự học và cải tiến hệ thống bằng cách nào", sau đó "viết bản chưng cất vào wiki cả ý nếu có thêm nếu bugs, failed hay errors cứ hơn 2 lần thì sẽ được gói lại thành instruction/skill dùng cho lần tiếp".
- **Code liên quan:** `harness/scripts/flywheel.py` (`pack_guardrail`, `guardrails`, `--guardrails`), `llmwiki/.claude/hooks/session_start.py` (`learned_guardrails`), `llmwiki/.claude/hooks/pre_tool_use.py` (tự ghi khi luật cắn), `harness/failure-flywheel.config.yaml` (ngưỡng và taxonomy).
