---
type: eval
id: ui-kit-hero
title: "ui-kit-from-code — màn đại diện đặt ở đâu, làm sao không nhân đôi markup"
input: "Khi dựng UI kit bằng ui-kit-from-code, màn hình đại diện của app đặt ở đâu và làm sao để nó không thành bản markup thứ hai phải giữ đồng bộ?"
expected: "Đặt ở phần 3 (intro), cột phải, trong khung nhìn đầu tiên (RULE-13). Đánh dấu màn đó ở phần màn mẫu bằng data-kit-rep; script clone nó vào khung data-kit-hero nên chỉ có một nguồn markup. Cổng discover.mjs --coverage rc 1 khi thiếu hero hoặc hero đứng sau nội dung."
asserts:
  - 'contains:data-kit-rep'
  - 'contains:data-kit-hero'
  - 'regex:(?i)(intro|khung nhìn đầu|trên đầu)'
rubric: "ĐẠT nếu đặt màn đại diện cạnh intro ở đầu trang và dùng clone từ data-kit-rep vào data-kit-hero (một nguồn markup). KHÔNG đạt nếu để màn mẫu ở cuối hoặc chép markup lần hai."
---

# Golden: ui-kit-hero

User yêu cầu 2026-10-06: "luôn đẩy 1 màn hình đại diện cho UIKIT này lên phần preview trên đầu". Đáp án kiểm chứng bằng `node skills/ui-kit-from-code/references/discover.mjs --coverage` (4 ca: đủ / thiếu hero / thiếu rep / hero đứng sau) và Playwright đo hero nằm trong khung 1440×900.

## Origin
- Phiên 44e9cc55 ngày 2026-10-06 (/fdk sửa skill ui-kit-from-code, RULE-13).
