# Setup AI Agent Project Workflow

tự động setup dự án 3 bước prompt, feed lần lượt các file prompt cho AI Agent.

## Prerequisites

Skills:
- ```UI/UX: npx skills add https://github.com/Leonxlnx/taste-skill --all```
- ```Own: npx skills add rheinmir/setup#orca --global --all```

## Cách sử dụng

1. Copy thư mục `llmwiki` sang thư mục gốc của dự án mới.
2. Mở cửa sổ chat với AI Agent (Claude Code, OpenCode, hoặc Antigravity).
3. Feed toàn bộ nội dung file `01-Project-Kickoff.md` cho Agent. Agent sẽ hỏi 3 câu về dự án — trả lời xong, Agent tạo `AGENT-business.md` và `AGENT-code.md`.
4. Feed file `02-Setup-Knowledge-Base.md`. Agent tạo cấu trúc: thư mục `skills/`, `commands/`, `raw/`, `wiki/` (gồm `concepts/`, `entities/`, `sources/`), file `AGENT.md`, và `wiki/log.md`.
5. Feed file `03-Scaffold-Application.md` để Agent scaffold toàn bộ codebase MVP.

Quá trình này biến AI Agent thành một Tech Lead tự động setup kiến trúc hoàn chỉnh.
