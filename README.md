# Setup AI Agent Project Workflow

Quy trình tự động setup dự án mới qua 4 bước prompt. Thay vì code tay, bạn chỉ cần feed lần lượt các file prompt cho AI Agent (Claude Code, OpenCode, Antigravity — đều có config sẵn trong thư mục này).

## Prerequisites

Trước khi bắt đầu, chuẩn bị sẵn:
- **Azure LLM API Key** (hoặc OpenAI key) — dùng cho Cognee LLM
- **Neo4j** instance (local hoặc cloud) — Cognee Graph Database
- **Supabase** project URL + key — Cognee Vector DB

Bạn sẽ cần điền các thông tin này vào file `.env.cognee` ở bước 3.

## Cách sử dụng

1. Copy thư mục `newProject` sang thư mục gốc của dự án mới.
2. Mở cửa sổ chat với AI Agent (Claude Code, OpenCode, hoặc Antigravity).
3. Feed toàn bộ nội dung file `01-Project-Kickoff.md` cho Agent. Agent sẽ hỏi 3 câu về dự án — trả lời xong, Agent tạo `AGENT-business.md`, `AGENT-code.md`, và `.env.cognee`.
4. Feed file `02-Setup-Knowledge-Base.md`. Agent tạo cấu trúc: thư mục `.agent/`, `wiki/` (gồm `concepts/`, `entities/`, `sources/`), file `AGENT.md`, và `wiki/log.md`.
5. Mở file `.env.cognee` (vừa được tạo ở bước 3) và điền thông tin kết nối Cognee (Azure LLM, Neo4j, Supabase). Sau đó feed file `03-Database-Check.md`.
6. Feed file `04-Scaffold-Application.md` để Agent scaffold toàn bộ codebase MVP.

## Output sau khi hoàn thành

```
project-root/
├── .agent/            # Agent commands & skills
├── wiki/              # Knowledge base
│   ├── concepts/Architecture.md
│   ├── entities/
│   ├── sources/
│   ├── index.md
│   └── log.md
├── AGENT.md           # Ground rules cho AI Agent
├── AGENT-business.md  # Mô tả nghiệp vụ dự án
├── AGENT-code.md      # Tech stack & kiến trúc
├── .env.cognee        # Credentials (không commit)
└── README.md          # Hướng dẫn chạy local (do Agent tạo)
```

Quá trình này biến AI Agent thành một Tech Lead tự động setup kiến trúc hoàn chỉnh.
