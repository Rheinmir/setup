---
type: eval
id: qc-uiux-done-ratchet
title: "Chuẩn UI/UX — khi nào UI được gọi là xong, và làm sao vòng sửa sau không phá vòng trước"
input: "Tôi vừa dựng xong landing page bằng hallmark. Khi nào thì được báo là xong? Nếu cho agent tự sửa nhiều vòng thì làm sao chắc vòng sau không làm hỏng thứ vòng trước đã sửa đúng, và không lén nới tiêu chí cho dễ đạt?"
expected: "Chưa xong cho tới khi /qc-uiux soi 5 mục UX + AX (gồm thử 5 giây, mobile không phải desktop bị bóp, ax-scan: HTML server-render, canonical, bot AI) và DONE contract đạt. DONE viết trước khi sửa, khoá bằng done-contract.py lock (sha256 — check đỏ nếu bị nới). Chạy /qc-uiux --loop N: mỗi tiêu chí đạt ghi bằng done-contract.py pass, đầu và cuối mỗi vòng chạy done-contract.py verify (ratchet) — tiêu chí từng đạt mà đỏ lại là hồi quy, sửa trước khi làm việc mới."
asserts:
  - 'contains:/qc-uiux'
  - 'contains:lock'
  - 'contains:verify'
  - 'regex:(?i)ratchet|hồi quy'
rubric: "ĐẠT nếu nói UI chỉ xong khi DONE contract của /qc-uiux đạt, DONE khoá trước khi sửa (chống nới) và ratchet verify giữa các vòng (chống phá vòng trước). KHÔNG đạt nếu coi self-critique hay ảnh đẹp là đủ."
---

# Golden: qc-uiux-done-ratchet

Câu hỏi bật ra khi nâng `/qc-uiux` thành chuẩn UI/UX của framework (2026-10-06). Đáp án kiểm chứng bằng `harness/tests/test_qc_uiux_done_contract.py` (khoá bắt nới tiêu chí, verify bắt hồi quy) và RULE-17 của `hallmark`.

## Origin
- Phiên 44e9cc55 ngày 2026-10-06 (/fdk nâng qc-uiux thành chuẩn framework).
