---
name: teach-me
description: >-
  Giải thích MỘT thứ (một file, hàm, tính năng, hay hệ thống) theo cấu trúc cố định: cách chạy ở cấp
  HỆ THỐNG (+ sơ đồ) · cách chạy ở cấp CODE (+ sơ đồ) · bộ ba vấn-đề-giải-quyết / workflow / nội-dung-chi-tiết
  (OS · cơ chế · vai trò) · tóm tắt luồng (+ sơ đồ). Điểm phân biệt: CHỨNG phần "nó chạy thế nào" bằng RUNTIME
  thật — chạy code với đầu vào cụ thể, thêm instrument/breakpoint (pdb/debugpy · node --inspect · print/log),
  quan sát state THẬT — thay vì đọc-rồi-đoán, rồi dọn sạch instrument. Gọi khi user nói "teach me", "giải thích",
  "dạy tôi", "cái này chạy thế nào", "sơ đồ hoá", "/teach-me". KHÁC /onboard-codebase và /join-project (cả dự án
  → wiki): teach-me phạm vi MỘT thứ, sâu, có sơ đồ, chứng bằng chạy thật, không ghi wiki.
---

# Skill: teach-me

## When to use
- User muốn hiểu sâu MỘT thứ cụ thể: một file, một hàm, một tính năng, một hệ thống con — "cái này chạy thế nào", "giải thích cho tôi".
- KHÔNG dùng cho: hiểu cả một codebase lạ (đó là `/onboard-codebase` → wiki, hoặc `/join-project` → orient nhanh read-only). teach-me hẹp và sâu, không ghi wiki.

## Bạn ĐƯỢC DÙNG công cụ để CHỨNG, không chỉ đọc
Đây là điểm phân biệt. Câu "nó chạy thế nào" phải được **chứng bằng runtime thật**, không suy đoán từ đọc tĩnh. Công cụ trong môi trường Claude Code:
- **Python:** `python3 -m pdb <file>`, hoặc `import pdb; pdb.set_trace()` / `breakpoint()` tạm, hoặc `debugpy`. Rẻ hơn: chèn `print(...)`/`logging` ở điểm quan tâm rồi chạy.
- **Node/JS:** `node --inspect`, `console.trace()`, `debugger;` tạm, hoặc `console.log` ở điểm quan tâm.
- **Bất kỳ:** built-in `/run` (chạy app thật) và `/verify` (drive flow, quan sát hành vi). Chạy với **đầu vào cụ thể**, quan sát **state thật ở dòng cụ thể**.

"Hàm này chắc trả về X" là phỏng đoán. "Tôi chạy với đầu vào Y, đặt breakpoint ở dòng Z, quan sát state là W" là **dữ kiện**. Luôn ưu tiên dữ kiện.

## Steps
1. **Xác định phạm vi** — user chỉ đích danh thứ cần giải thích. Không rõ → hỏi một câu ("giải thích cái gì?") kèm gợi ý từ context. Đọc code trong phạm vi đó.
2. **DRIVE runtime** (nếu chạy được) — chạy với một đầu vào cụ thể, thêm instrument/breakpoint tạm, quan sát state thật. → Xong khi có ít nhất một quan sát runtime cụ thể (đầu vào → state ở dòng nào). Không chạy được → ghi "giải thích tĩnh" (mục Rules).
3. **Sinh bốn phần** (mục dưới). → Xong khi cả bốn phần có mặt, mỗi phần có sơ đồ.
4. **DỌN SẠCH instrument** — gỡ mọi `print`/`breakpoint`/`debugger` tạm đã chèn; `git diff` xác nhận code người dùng sạch như trước. → Xong khi diff không còn instrument tạm.

## Bốn phần (output cố định)

### 1. Cấp HỆ THỐNG — nó chạy thế nào (+ sơ đồ)
Các thành phần lớn, ai gọi ai, dữ liệu đi đâu, ranh giới process/service/OS. Sơ đồ: các hộp + mũi tên luồng. Nếu drive được: nêu quan sát thật (process nào spawn, file/socket nào mở).

### 2. Cấp CODE — nó chạy thế nào (+ sơ đồ)
Đường thực thi cụ thể: hàm nào gọi hàm nào, state đổi ở đâu, nhánh nào chạy với đầu vào đã thử. Sơ đồ: call flow / sequence. **Neo vào quan sát runtime** (dòng Z, state W) chứ không mô tả chung chung.

### 3. Bộ ba
- **Vấn đề giải quyết** — thứ này tồn tại để giải bài toán gì; không có nó thì sao.
- **Workflow** — các bước dùng/chạy nó, đầu-cuối.
- **Nội dung chi tiết** — **OS** (syscall/process/file/network liên quan) · **cơ chế** (thuật toán/data-structure/giao thức) · **vai trò** (mỗi phần đóng vai gì trong tổng thể).

### 4. Tóm tắt luồng (+ sơ đồ)
Một hình một câu chuyện đầu-cuối: input → các chặng → output. Đọc một lần là nắm được toàn cảnh.

## Sơ đồ — hai đường
- **Mặc định: mermaid inline** — khối ```mermaid``` (flowchart cho cấu trúc, sequenceDiagram cho luồng theo thời gian). Nhanh, đọc-được-dạng-text, render ở surface hỗ trợ. Đủ cho phần lớn "teach me nhanh".
- **Opt-in: HTML explainer** — user muốn GIỮ / chia sẻ / cần hình đẹp thật → render một trang theo `/docs-site-macos` (glass, toggle sáng/tối, in full-path, thang chữ compact 13″) với sơ đồ SVG. Đứng trên nền `[[design-foundation]]`, KHÔNG đẻ theme mới. Hỏi user trước khi ra file, đừng ép.

## Rules
- **Chứng bằng runtime, không đoán:** phần "nó chạy thế nào" ưu tiên DRIVE code thật. Chỉ khi không chạy được (thiếu môi trường, cần prod) mới giải thích tĩnh — và **nói rõ** "đây là giải thích tĩnh, chưa chứng bằng chạy". Nếu một khẳng định phụ thuộc runtime chưa quan sát → ghi nợ `[[150726-unknown-ledger]]`, đừng khẳng định bừa.
- **Instrument tạm → DỌN SẠCH:** mọi `print`/`breakpoint`/`debugger`/`console.log` chèn để quan sát phải gỡ hết; `git diff` xác nhận trước khi kết thúc. Không để rác trong code người dùng (surgical, CLAUDE.md).
- **Phạm vi MỘT thứ:** teach-me không phân tích cả dự án (đó là `/onboard-codebase`/`/join-project`) và không ghi wiki.
- **Không đẻ debugger mới** — dùng công cụ có sẵn (pdb/debugpy · node --inspect · print/log · /run · /verify).

## Origin
- Distill từ yêu cầu user 2026-07-16 (teach-me: 2 cấp + bộ ba + tóm tắt, mỗi phần sơ đồ; skill biết dùng breakpoint/debugger). Grounded-runtime mượn triết lý built-in `/verify`.
- Absorb qua `/propose` → `160726-teach-me-skill`, task `T-260716-01`.
- **Commit:** _(verify-before-commit điền)_
