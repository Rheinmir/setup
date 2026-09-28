---
name: dym-harness-sdk-effect-tests
description: "Viết test live-model cho agent theo kiểu Strands — assert hiệu ứng quan sát được (tool gọi thành công, file trên đĩa, cache token tăng) thay vì lời văn của model. Gọi khi cần test agent/harness chạy model thật mà không flaky."
disable-model-invocation: true
---

# Skill: dym-harness-sdk-effect-tests — test hiệu ứng, không test lời văn

## When to use
- Có agent chạy model thật và cần test không vỡ vì model trả lời khác chữ.
- Nguyên tắc gốc (`harness-py/tests_integ/conftest.py:7-8`): *"Assertions check observable side effects (a file created, a tool blocked), never the model's exact prose — the model is non-deterministic, the effect is not."*
- Sinh ra: bộ pytest nằm NGOÀI `testpaths` (unit run mặc định không gom), chạy tường minh bằng `pytest tests_integ`.

## Steps
1. Fixture dựng agent tối giản — model nhỏ, tắt reasoning, tắt plugin, tắt session — để test chỉ đo đúng thứ nó dựng:
   ```python
   INTEG_MODEL = os.environ.get("STRANDS_INTEG_MODEL", "bedrock/global.anthropic.claude-haiku-4-5-20251001-v1:0")
   def build_agent(**o):
       return create_harness(**{"model": INTEG_MODEL, "effort": "off", "builtin_plugins": [], "session": False, **o})
   ```
2. Cwd tạm cho mỗi test (`monkeypatch.chdir(tmp_path)`) — tool file/shell của agent phân giải theo cwd.
3. Ba predicate đọc **lịch sử hội thoại** (`agent.messages`), không đọc câu trả lời cuối:
   - `tool_succeeded(agent, name)` — có `toolUse` tên đó VÀ `toolResult` cùng `toolUseId` với `status == "success"`.
   - `tool_attempted(agent, name)` — có `toolUse` tên đó bất kể kết quả → chống **pass giả** khi assert "tool bị chặn" (chứng minh nó đã THỬ rồi bị deny, không phải bị bỏ qua).
   - `tool_result_contains(agent, name, needle)` — output CỦA TOOL chứa `needle`.
4. Một lượt model phủ nhiều tool để rẻ (e2e của họ: 7 tool/1 lượt, rồi assert file trên đĩa + kết quả subagent chứa `"333"`).
5. Kiểm cơ chế qua số đo hạ tầng, ví dụ cache: `result.metrics.accumulated_usage["cacheReadInputTokens"]` phải > 0 và **tăng mọi lượt**.
6. Chạy: `pytest tests_integ --reruns 2` (cần `pytest-rerunfailures`, credential model).

## Rules
- Không assert chuỗi model nói; assert trạng thái (file, tool result, metric).
- Mọi assert "không làm X" phải đi kèm `tool_attempted` — nếu không sẽ pass khi model đơn giản là không thử.
- `--reruns 2` che độ flaky thật: nếu muốn biết tỉ lệ ổn định thì chạy N lần không rerun và ghi pass@k — repo gốc KHÔNG làm việc này.
- **Chưa kiểm chứng ở đây:** 11 test integ chỉ được `--collect-only` (rc 0), chưa chạy vì cần AWS Bedrock.
