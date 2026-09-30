---
name: dym-harness-sdk-interventions
description: "Gắn chốt chặn cho tool call của Strands harness qua tham số interventions (ask · smart · file .cedar · chính sách chữ · handler tự viết) — gọi khi cần human-in-the-loop, phân loại rủi ro, hoặc policy Cedar."
disable-model-invocation: true
---

# Skill: dym-harness-sdk-interventions — chốt chặn tool call

## When to use
- Cần agent hỏi người trước khi chạy tool nguy hiểm, hoặc tự phân loại rủi ro, hoặc tuân policy Cedar.
- Khác hook chặn thường: handler **trả về QUYẾT ĐỊNH có kiểu** (Proceed · Deny · Guide · Interrupt · Transform), registry gộp theo ưu tiên **Deny > Interrupt > Transform > Guide > Proceed**; Deny cắt ngắn chuỗi, Guide cộng dồn phản hồi, có audit log chung (design `team/designs/0007-intervention-primitive.md`).

## Steps
1. Grammar chuỗi là TẤT ĐỊNH, không đoán nội dung (`harness-py/src/strands_harness/interventions.py`):
   | giá trị | thành |
   |---|---|
   | `"off"` / `None` | không có handler |
   | `"ask"` | `HumanInTheLoop(ask=...)` — hỏi người mỗi call |
   | `"smart"` | `HumanInTheLoop(classifier=True)` — LLM phân loại rủi ro, chỉ hỏi call bị cờ |
   | chuỗi kết thúc `.cedar` | `CedarAuthorization(policies=<file>)` — cần `pip install 'strands-agents[cedar]'` |
   | chuỗi khác | chính sách chữ → prompt của bộ phân loại rủi ro |
   | instance `InterventionHandler` | đi thẳng, không đổi |
2. Ghép nhiều lớp khác loại:
   ```python
   create_harness(interventions=["policies/tools.cedar", "smart"])
   ```
3. Kiểm hành vi lỗi (đo 2026-09-28, rc 0):
   ```python
   create_harness(session=False, memory=False, interventions=["ask", "ask"])
   # ValueError: Two interventions share the handler name 'strands:human-in-the-loop' ...
   create_harness(session=False, memory=False, interventions=123)
   # ValueError: Invalid interventions value 123; expected a preset name, ...
   ```

## Rules
- Hai handler CÙNG loại → raise (SDK chỉ giữ một handler mỗi `name`); ghép KHÁC loại (Cedar + một preset người duyệt) thì được.
- Policy Cedar viết inline KHÔNG được tự nhận diện (trông như văn xuôi) → truyền `CedarAuthorization(policies=...)` trực tiếp.
- Subagent con **kế thừa** interventions của cha; lời gọi tool bên trong `programmatic_tool_caller` vẫn đi qua interventions — không lách được bằng cách gọi gián tiếp.
- Xếp handler rẻ trước (Cedar → dịch vụ → LLM) vì Deny cắt ngắn chuỗi.
- `"ask"` với `ask=None` dùng stdio — chạy headless/CI sẽ kẹt chờ input; truyền callback hoặc dùng interrupt/resume.
