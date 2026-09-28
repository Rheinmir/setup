---
name: dym-harness-sdk
disable-model-invocation: true
domains: [agent-harness, evaluation, guardrail]
source: https://github.com/strands-agents/harness-sdk
description: "Strands harness (strands-agents/harness-sdk) — agent lắp sẵn create_harness() + cách họ test/eval — workflow đã kiểm chứng. Gõ /dym-harness-sdk <slug>. slugs: quickstart · interventions · effect-tests · evals · contributor"
---

# Skill: dym-harness-sdk — hub workflow cho Strands harness

## When to use
- User gõ `/dym-harness-sdk` (không tham số → bảng slug) hoặc `/dym-harness-sdk <slug>`; hoặc `/dym` định tuyến tới đây theo domain.
- Hub chỉ tốn dòng description; thân workflow con chỉ đọc khi được gọi.

## Steps
1. Đọc ARGUMENTS → `<slug>`. Không có slug → in bảng dưới rồi dừng, không đọc file nào.

   | slug | mục đích | loại |
   |---|---|---|
   | `quickstart` | Cài `strands-harness` vào venv cô lập, dựng agent, xem nó lắp gì | shell + python |
   | `interventions` | Gắn chốt chặn tool call: `ask` / `smart` / `.cedar` / chính sách chữ | python |
   | `effect-tests` | Viết test live-model theo kiểu Strands: assert HIỆU ỨNG, không assert lời văn | pytest |
   | `evals` | Chấm agent bằng Strands Evals SDK (repo ngoài) — **chưa kiểm chứng** | python + CLI |
   | `contributor` | Sửa chính harness: chạy unit/integ/selective-test như CI | shell |

2. Tìm file con theo thứ tự, lấy file ĐẦU TIÊN tồn tại rồi đọc ĐÚNG MỘT file:
   (1) `../dym-harness-sdk-<slug>/SKILL.md` (cạnh hub — cài qua `npx skills add rheinmir/dym`);
   (2) `.overstack/doyourmagic/harness-sdk/skills/dym-harness-sdk-<slug>/SKILL.md` (bundle trong dự án);
   (3) `doyourmagic-bundles/harness-sdk/skills/dym-harness-sdk-<slug>/SKILL.md` (clone `rheinmir/dym` cạnh dự án).
   Làm theo Steps/Rules của file đó; không đọc file con khác; không thấy cả 3 → nói rõ, dừng.

## Rules
- Mỗi sub-skill tự chứa; hub không nhồi cả bundle vào context.
- `workflows.md` cạnh bundle là chỉ mục + bảng kiểm chứng + so sánh với overstack, không phải nguồn lệnh.
