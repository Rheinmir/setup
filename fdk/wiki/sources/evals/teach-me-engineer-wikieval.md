---
type: eval
id: teach-me-engineer-wikieval
title: "teach-me cho engineer — tầng 1 (tier-1 asserts) của wikieval chạy thế nào"
input: "teach me: tầng 1 (tier-1 deterministic asserts) trong harness/scripts/wikieval.py chạy thế nào?"
expected: |
  Người nghe là engineer, nói thẳng bằng thuật ngữ.

  Tên gọi: tầng 1 (tier-1 deterministic asserts) của wikieval — cổng khẳng định tất định, không gọi model.

  Nguồn gốc: thêm vào khi cần một tầng chấm golden vừa rẻ vừa lặp-lại-được để chặn CI, trước khi nghĩ tới giám khảo LLM ở tier-3.

  Lý do tồn tại: bỏ nó thì mọi golden phải nhờ model chấm — chậm, tốn tiền, không tất định; tier-1 cho câu trả lời đúng/sai ngay trên chuỗi.

  Cơ chế hoạt động: run_golden nhận một golden và output ứng viên, gọi eval_assert cho từng mục trong asserts; golden nào khai asserts thì tầng 1 tự quyết (decided_by tier1-asserts), chỉ đạt khi all() assert cùng đúng; op lạ fail closed nên adapter nửa vời không bao giờ tự đạt.

  ```mermaid
  flowchart LR
    G[golden + output] --> R[run_golden]
    R --> E[eval_assert cho từng assert]
    E -->|all pass| P[PASS tier1]
    E -->|một fail| F[FAIL]
  ```

  Bằng chứng runtime: đã chạy python3 harness/scripts/wikieval.py --self-test, quan sát từng golden in OK hoặc FAIL và tiến trình dừng đúng ở golden lỗi (rc=1 khi có fail).

  Trade-off: rẻ, tất định, không cần model — đổi lại chỉ bắt được dấu hiệu bề mặt của chuỗi.

  Giới hạn: regex chạy không cờ mặc định và không hiểu ngữ nghĩa; nó không phân biệt được câu đúng ý với câu chỉ trùng từ khoá.

  Vị trí: tier-1 là chặng đầu của cascade wikieval, đứng trước tier-2 (similarity) và tier-3 (LLM-rubric, hiện disabled), và là tầng duy nhất chạy trong CI gate.
asserts:
  - 'regex:(?s)Tên gọi.*Nguồn gốc.*Lý do tồn tại.*Cơ chế hoạt động.*Trade-off.*Giới hạn.*Vị trí'
  - 'contains:```mermaid'
  - 'regex:eval_assert|run_golden'
  - 'regex:(?i)đã chạy|chạy thật|chạy thử|rc=|exit ?code|python3 harness/scripts/wikieval\.py'
rubric: "ĐẠT nếu: dùng đúng thuật ngữ, không giải thích lại những thứ engineer đã biết; bước Cơ chế trích quan sát runtime cụ thể (đầu vào → kết quả) chứ không mô tả chung; Trade-off và Giới hạn khác nhau thật. KHÔNG đạt nếu chỉ đọc code rồi đoán, hoặc thiếu phần nào trong bảy phần."
---

# Golden: teach-me-engineer-wikieval

Ca người nghe mặc định (engineer). Đo khung bảy phần, sơ đồ, và bằng chứng runtime — ba thứ teach-me hứa với dev.

## Origin
- Phiên 11/09/2026 — distill [dreambigou/eli5](https://github.com/dreambigou/eli5) vào `skills/teach-me/SKILL.md`; eli5 chấm skill bằng 3 ca × 4 assert, chạy có-skill so với không-skill. Ca này là một trong ba ca A/B cũ-vs-mới của teach-me.
