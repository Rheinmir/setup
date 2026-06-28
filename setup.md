# Dựng dự án mới với overstack

**Cách chuẩn — dán MỘT prompt, agent lo phần còn lại.** Không copy thư mục, không feed từng file.

## Bắt đầu (1 bước)

Mở agent (Claude Code · opencode · Cursor · Antigravity…) ở thư mục gốc dự án mới, rồi **dán nội dung [`00-New-Project.md`](00-New-Project.md)**. Agent sẽ tự:

0. **Cài overstack** (bootstrap — kéo harness + skills + llmwiki, không cần copy folder).
1. **Kickoff** — hỏi bạn 3 câu (tên · bài toán · stack), rồi tạo `AGENT-business.md` + `AGENT-code.md`.
2. **Knowledge base** — dựng `wiki/` · `skills/` · `commands/` · `raw/` đúng kỷ luật overstack.
3. **Scaffold MVP** — dựng codebase + health check + cập nhật wiki.

Agent dừng hỏi đúng lúc cần; bạn chỉ trả lời.

## Prerequisites (tuỳ chọn)

Bộ skills cài sẵn cho UI/UX đẹp hơn:
- `npx skills add https://github.com/Leonxlnx/taste-skill --all`
- `npx skills add rheinmir/setup#orca --global --all`

## Bản chi tiết từng pha

Prompt `00` đã gói đủ để chạy độc lập. Nếu muốn đọc/sửa nội dung từng pha:

| Pha | File | Làm gì |
|-----|------|--------|
| 1 | [`01-Project-Kickoff.md`](01-Project-Kickoff.md) | 3 câu hỏi → `AGENT-business.md` / `AGENT-code.md` |
| 2 | [`02-Setup-Knowledge-Base.md`](02-Setup-Knowledge-Base.md) | dựng nền tri thức (wiki/skills/raw/AGENT.md) |
| 3 | [`03-Scaffold-Application.md`](03-Scaffold-Application.md) | scaffold codebase MVP + cập nhật wiki |

Quá trình này biến AI Agent thành một cộng sự kỹ thuật tự động setup kiến trúc hoàn chỉnh.
