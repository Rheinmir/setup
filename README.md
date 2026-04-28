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
4. Feed file `02-Setup-Knowledge-Base.md`. Agent tạo cấu trúc: thư mục `skills/`, `commands/`, `raw/`, `wiki/` (gồm `concepts/`, `entities/`, `sources/`), file `AGENT.md`, và `wiki/log.md`.
5. Mở file `.env.cognee` (vừa được tạo ở bước 3) và điền thông tin kết nối Cognee (Azure LLM, Neo4j, Supabase). Sau đó feed file `03-Cognee-MCP-Setup-Check.md`.
6. Feed file `04-Scaffold-Application.md` để Agent scaffold toàn bộ codebase MVP.

## Output sau khi hoàn thành

```
project-root/
├── raw/               # Tài liệu gốc — chỉ human ghi, agent chỉ đọc
├── wiki/              # Knowledge base do agent duy trì
│   ├── concepts/      # Khái niệm, pattern, domain term
│   ├── entities/      # Service, API, component, tool
│   ├── sources/       # Reference ngoài + ADR
│   │   └── draft/     # Proposal chưa implement
│   ├── index.md       # Danh mục toàn bộ wiki
│   └── log.md         # Lịch sử thao tác (append-only)
├── skills/            # Workflow agent tự invoke theo ngữ cảnh
├── commands/          # Lệnh user gọi trực tiếp
├── AGENT.md           # Ground rules + danh sách skills cho AI Agent
├── AGENT-business.md  # Mô tả nghiệp vụ dự án (do Agent tạo ở bước 1)
├── AGENT-code.md      # Tech stack & kiến trúc (do Agent tạo ở bước 1)
├── .env.cognee        # Credentials — KHÔNG commit file này
└── README.md          # Hướng dẫn chạy local (do Agent tạo ở bước 4)
```

> **.env.cognee chứa credentials — thêm vào `.gitignore` ngay sau khi tạo.**

Quá trình này biến AI Agent thành một Tech Lead tự động setup kiến trúc hoàn chỉnh.
