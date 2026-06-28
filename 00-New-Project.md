# 00 — START: dựng dự án mới với overstack (chỉ cần DÁN prompt này)

Đây là **điểm bắt đầu duy nhất**. Mở agent (Claude Code · opencode · Cursor · Antigravity…) ở thư mục gốc của dự án mới, rồi **dán nguyên khối giữa hai dấu `---` bên dưới**. Agent sẽ tự cài overstack rồi dẫn bạn qua 4 pha (cài → kickoff → tri thức → scaffold), dừng hỏi đúng lúc cần — bạn **không** phải copy thư mục hay feed từng file thủ công.

> Prompt này **tự chứa đủ** để chạy độc lập. Bản chi tiết từng pha nếu muốn đọc/sửa: `01-Project-Kickoff.md` · `02-Setup-Knowledge-Base.md` · `03-Scaffold-Application.md`.

---
Bạn là cộng sự kỹ thuật dựng một dự án MỚI với framework **overstack**. Thực hiện TUẦN TỰ theo 4 pha, **DỪNG ở mỗi pha cần tôi trả lời**. Không nhảy bước, không tự bịa khi chưa đủ thông tin.

**PHA 0 — Cài overstack**
Chạy trong thư mục gốc:
`curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash`
Rồi xác nhận đủ 3 trụ đã đúng chỗ: **harness** (validator + hook gác), **skills** (global), **llmwiki** (khung wiki). Nếu dự án đã có `llmwiki/` cũ → gọi `/harness-update` thay vì cài đè. **Cài xong, ĐỌC `llmwiki/AGENT.md` + `llmwiki/CLAUDE.md`** để nắm luật (R1–R12) — áp dụng cho mọi pha sau. Nếu lệnh cài lỗi (mạng/quyền) → báo tôi, đừng đoán tiếp.

**PHA 1 — Kickoff (hỏi tôi 3 câu rồi DỪNG)**
Hỏi ĐÚNG 3 câu, rồi CHỜ tôi trả lời — CHƯA tạo code/file:
1. Tên dự án là gì?
2. Bài toán nghiệp vụ cốt lõi nó giải quyết?
3. Tech stack ưu tiên? (Frontend / Backend / Database)
Sau khi tôi trả lời: tạo `AGENT-business.md` (mục tiêu, luồng người dùng, ràng buộc cốt lõi) và `AGENT-code.md` (stack đã chọn + pattern kiến trúc).

**PHA 2 — Knowledge base (nền tri thức)**
Cấu trúc `llmwiki/` đã đến từ bản cài PHA 0 — **verify** (thiếu mới tạo): `llmwiki/wiki/{concepts,entities,sources/draft}`, `llmwiki/{skills,raw,html}`, `llmwiki/wiki/index.md` + `llmwiki/wiki/log.md`. Rồi **seed** nội dung dự án: tạo `llmwiki/wiki/sources/project-requirements.md` từ câu trả lời PHA 1, thêm row vào `index.md`, append `log.md`. Quy tắc bắt buộc cho MỌI trang wiki: frontmatter YAML `type:` + section `## Origin` (R2/R9, theo `_template.md` — KHÔNG dùng `**Type:**` bold cũ); **không bao giờ ghi vào `raw/`** (R1); file đặt đúng subfolder (R5).

**PHA 3 — Scaffold MVP**
Đọc `AGENT-business.md` + `AGENT-code.md`. Scaffold cấu trúc thư mục theo stack đã chọn, một `health` endpoint hoặc landing tối thiểu để chạy thử, một `README.md` ghi cách chạy local, và `llmwiki/wiki/concepts/architecture.md` (đúng format + `## Origin`) — cập nhật `index.md` + `log.md`. Trình bày tóm tắt đã dựng gì, rồi hỏi tôi muốn build feature đầu tiên nào.

Bắt đầu **PHA 0** ngay, rồi sang **PHA 1** (hỏi tôi 3 câu).
---
