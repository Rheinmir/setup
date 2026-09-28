---
name: dym-harness-sdk-quickstart
description: "Cài strands-harness vào venv cô lập và dựng agent lắp sẵn bằng create_harness() — gọi khi cần thử Strands harness, xem nó lắp tool/plugin/memory gì trước khi gọi model."
disable-model-invocation: true
---

# Skill: dym-harness-sdk-quickstart — dựng agent lắp sẵn

## When to use
- Muốn một agent "đủ đồ" (shell, file, web, subagent, todo, memory, session, offload context) trong 1 dòng, không tự viết agent loop.
- Muốn xem harness lắp gì TRƯỚC khi tốn tiền gọi model.
- Sinh ra: một `strands.Agent` THƯỜNG (không phải lớp bọc riêng) — mọi thứ SDK làm được vẫn làm được sau khi dựng.

## Steps
1. Venv cô lập, Python **≥ 3.10** (Python 3.9 hệ thống của macOS không cài được):
   ```bash
   python3.13 -m venv .venv-strands && .venv-strands/bin/pip install -q strands-harness
   # provider khác Bedrock: strands-harness[anthropic] | [openai] | [gemini] | [ollama] | [litellm]
   ```
2. Dựng agent KHÔNG gọi model (đo 2026-09-28, rc 0):
   ```python
   from strands_harness import create_harness
   a = create_harness(session=False, memory=False)
   print(sorted(a.tool_names))
   # ['edit','programmatic_tool_caller','read','retrieve_context','retrieve_offloaded_content',
   #  'shell','strands_manage_background_task','subagent','todo_write','web_fetch','write']
   ```
3. Chạy thật (tốn tiền): `a("Find the slowest test in this repo")`. Mặc định model = **Bedrock Opus 5** → cần AWS credential; đổi bằng `model="anthropic/claude-fable-5"` (chuỗi `provider/name`).
4. Tham số chính (`create_harness`, keyword-only): `model` · `effort` (`auto|off|minimal..max`) · `instructions` (ghép SAU contract của harness) · `tools` · `mcp_servers` · `builtin_tools` · `session` (mặc định `./.agent/sessions`) · `memory` (mặc định `./.agent/memory`) · `skills` · `builtin_plugins` · `interventions` · `**agent_kwargs` (giá trị SDK tường minh luôn THẮNG giá trị mặc định của harness).
5. Bật trace: đặt `OTEL_TRACES_EXPORTER=otlp` (hoặc `console`) trước khi dựng; không đặt thì telemetry tắt.

## Rules
- **Bẫy đã đo:** model không có web search native (Bedrock) → harness chỉ in cảnh báo rồi **bỏ tool `web_search`**, không lỗi. Cần search thì `builtin_tools={'web_search': 'exa'}`.
- **Bẫy đã đo:** `session`/`memory` mặc định BẬT và ghi vào `./.agent/` của cwd — thử nghiệm thì tắt (`session=False, memory=False`) để không bẩn repo.
- Tool trùng tên giữa 5 nguồn (consumer · builtin · MCP · plugin · subagent) → raise ngay lúc dựng; riêng tool MCP chỉ biết tên sau khi kết nối nên lọt qua bước kiểm này.
- Memory extract chạy nền: script chạy ngắn phải gọi shutdown, nếu không có thể mất dữ liệu.
- Thứ cho production: bản harness đang 0.x và bật mặc định `ContextManager` của `strands.experimental` — không cam kết semver.
