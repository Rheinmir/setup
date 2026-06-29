---
type: concept
title: "Boris Cherny — 5 agent role trong Claude Code (scope deep-dive)"
status: implemented
tags: [boris-cherny, claude-code, subagent, roles, workflow, reference]
timestamp: 2026-06-29
---

# Boris Cherny — 5 agent role (deep-dive scope)

> **Nguồn:** `.claude/agents` của Boris Cherny (creator + Head of Claude Code) — site chính chủ
> [howborisusesclaudecode.com](https://howborisusesclaudecode.com/) + [Pragmatic Engineer interview](https://newsletter.pragmaticengineer.com/p/building-claude-code-with-boris-cherny).
> ⚠️ Boris **không** chốt "bộ 5 role chuẩn" — đây là 5 agent ông kể cùng nhau trong `.claude/agents`.
> Nếu ảnh của bạn liệt kê 5 cái KHÁC, sửa lại danh sách + tôi deep-dive theo đúng ảnh.

## Triết lý nền (vì sao có role)
Boris coi Claude Code là **hạ tầng, không phải phép màu**: ông dựng hệ thống quanh nó (memory file,
permission config, **verification loop**, formatting hook) rồi **điều phối nhiều subagent như một
hạm trưởng** — mỗi agent một role hẹp, một bộ tool/permission riêng, chạy đúng một khúc của vòng đời.
Role = **ranh giới trách nhiệm + bộ quyền** đóng gói trong một file `.claude/agents/<name>.md`
(custom name, color, tool set, pre-allowed/disallowed tools, permission mode, model).

## 5 role — scope từng cái

### 1. code-architect — *thiết kế TRƯỚC khi code*
- **Scope:** chuyển một yêu cầu mơ hồ thành **kế hoạch/kiến trúc** rõ ràng: chia module, chọn
  ranh giới, nêu trade-off — TRƯỚC khi viết dòng code nào.
- **Khi chạy:** đầu vòng đời, lúc nhận task mới hoặc thay đổi lớn.
- **Ranh giới (KHÔNG làm):** không implement, không sửa file sản phẩm — chỉ ra "bản thiết kế".
- **Vì sao hẹp:** tách "quyết định kiến trúc" khỏi "gõ code" để không vừa nghĩ vừa làm (giảm
  over-engineer + sai hướng từ gốc).
- **Tool/permission điển hình:** read-heavy (đọc codebase), không cần write rộng.

### 2. code-simplifier — *dọn SAU khi xong*
- **Scope:** chạy **sau khi Claude hoàn thành** một task → gỡ abstraction thừa, siết logic, cải
  thiện readability mà **không đổi hành vi**.
- **Khi chạy:** cuối vòng, trước khi mở PR.
- **Ranh giới:** không thêm tính năng, không đổi behavior — chỉ làm code gọn hơn (diff phải an toàn).
- **Vì sao hẹp:** "viết cho chạy" và "viết cho gọn" là hai não trạng khác nhau; tách ra để bản
  cuối không phình. (Khớp `/simplify` của overstack.)

### 3. verify-app — *chứng minh thay đổi CHẠY ĐÚNG*
- **Scope:** chứa **hướng dẫn e2e test cụ thể** cho app → chạy thật, quan sát hành vi, **xác minh
  thay đổi đúng** trước khi PR mở.
- **Khi chạy:** sau implement, trước PR.
- **Ranh giới:** không sửa code để "làm cho test xanh" — chỉ kiểm chứng + báo cáo pass/fail thật.
- **Vì sao hẹp:** chống "corrupt success" (claim done mà chưa chạy). Đây là **verification loop**
  Boris nhấn mạnh. (Khớp `verify-before-commit` + `trace-grader` của overstack.)

### 4. build-validator — *cổng build phải xanh*
- **Scope:** validate **build/compile/lint** của toàn dự án sau mỗi thay đổi (vd `npm run build`,
  `tsc --noEmit`) — bắt lỗi tích hợp mà unit test bỏ sót.
- **Khi chạy:** sau mỗi merge/builder, deterministic.
- **Ranh giới:** không phán xét logic nghiệp vụ — chỉ "build có dựng được không".
- **Vì sao hẹp:** một cổng tất định, rẻ, chạy liên tục = sàn chất lượng. (Khớp tinh thần
  "CI là sàn" + fdk-gate của overstack.)

### 5. oncall-guide — *runbook khi prod đau*
- **Scope:** **runbook oncall** — khi có sự cố/lỗi production, hướng dẫn chẩn đoán + xử lý theo
  bước. Hay đi kèm **`sentry-errors`** (agent thứ 6): kéo lỗi gần đây từ Sentry → đề xuất fix,
  cho đường "một lệnh: từ lỗi prod → PR".
- **Khi chạy:** lúc vận hành/incident, không phải lúc dev tính năng.
- **Ranh giới:** không refactor lan man — chỉ đưa hệ thống về trạng thái lành, ghi lại nguyên nhân.
- **Vì sao hẹp:** incident cần đường đi NGẮN + an toàn, không cần sáng tạo.

## Bản đồ sang overstack (role ↔ đồ ta đã có)
| Boris role | Tương đương trong overstack |
|---|---|
| code-architect | `propose` + `impact-check` (thiết kế + map caller trước khi sửa) |
| code-simplifier | `/simplify` + Karpathy "simplicity first" (CLAUDE.md §2) |
| verify-app | `verify-before-commit` + `trace-grader` (chấm đường đi, chống corrupt success) |
| build-validator | CI "là sàn" + `fdk-gate` (cổng tất định mọi bước) |
| oncall-guide | `orca-sec-scans` + runbook; `claim-receipts` (verify reference) cho khâu chẩn đoán |

## Bài học rút ra (cho framework)
- **Role = ranh giới quyền + một khúc vòng đời**, đóng gói thành file khai báo (name/tool/permission/
  model) — đúng mô hình `scoped-hooks` (guard theo component) ta vừa làm.
- **Tách "làm" và "kiểm"**: architect (trước) · simplifier/verify/build (sau) — không để một agent
  vừa code vừa tự chấm mình (chống confirmation bias) — đúng tinh thần `trace-grader`/`council`.
- **Hạ tầng > phép màu:** memory + permission + verification loop + hook = cách Boris (và overstack)
  biến agent thành đáng tin.

## Origin
- **Source:** research site chính chủ [howborisusesclaudecode.com](https://howborisusesclaudecode.com/)
  + [Pragmatic Engineer](https://newsletter.pragmaticengineer.com/p/building-claude-code-with-boris-cherny),
  theo goal-set 2026-06-29 ("tạo file .md của boris cherny về 5 role, deep dive scope"). Ảnh user đính kèm
  là nguồn xác thực — nếu khác 5 role trên, cập nhật theo ảnh.
- **Liên quan:** `scoped-hooks` (role = component-scoped guard), [[harness-enforcement-floor]], pattern library `llmwiki/patterns/` (BA/tester/PM roles).
- **Date:** 2026-06-29
