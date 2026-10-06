---
type: eval
id: html-favicon-source
title: "Favicon trang HTML framework — nguồn duy nhất, trang tự lo theme thì gắn thế nào"
input: "Trang HTML do overstack sinh ra phải có favicon gì, gắn bằng cách nào? Trang tự lo theme/font riêng (vd UI kit của ui-kit-from-code) thì sao?"
expected: "Favicon chữ \"O\" của Overstack, nguồn duy nhất html_base.FAVICON_SVG. Không tự viết <link rel=icon>: chạy html_font.py --apply (lớp nền gắn favicon, thay mọi favicon cũ). Trang tự lo theme/font chạy html_base.py --apply --favicon-only để chỉ gắn favicon. R20 (d) chặn trang độc lập thiếu favicon O."
asserts:
  - 'contains:--favicon-only'
  - 'contains:--apply'
  - 'regex:(?i)chữ\s*"?O'
rubric: "ĐẠT nếu nêu favicon chữ O, gắn qua --apply của lớp nền (không viết tay) và trang tự lo theme dùng --favicon-only. KHÔNG đạt nếu bảo viết <link rel=icon> tay hoặc dùng favicon riêng."
---

# Golden: html-favicon-source

Câu hỏi bật ra từ phiên 2026-10-06: HTML sinh ngày 06/10 vẫn mang favicon xanh cũ vì favicon chữ O chưa được commit, ba generator còn viết cứng favicon, và R20 chỉ hỏi "có rel=icon không". Đáp án kiểm chứng bằng `harness/validators/html_docs_shell.py --self-test` (mục d) và `harness/tests/test_html_base.py`.

## Origin
- Phiên 44e9cc55 ngày 2026-10-06 (/fdk, nhánh feat/html-rail-favicon) — user hỏi "tại sao html tạo ra ngày 06102026 vẫn còn sidebar cũ và chưa có favicon chữ O".
