# CONTEXT
Mục tiêu của pha này: dựng **nền tri thức (knowledge base)** cho dự án theo chuẩn overstack. Đây là một artifact bền, agent bồi đắp dần theo thời gian — con người bỏ nguồn thô vào, agent tóm tắt, liên kết, bảo trì.

**Quan trọng:** nếu bạn đã chạy PHA 0 (cài overstack), thì khung `llmwiki/` đã có sẵn (đi kèm bản cài) — pha này **kiểm tra + seed nội dung**, không dựng lại từ con số 0. Nếu chưa cài, tạo mới theo đúng cấu trúc dưới.

Ba lớp, tất cả **nằm dưới `llmwiki/`**:
- **`llmwiki/raw/`** — nguồn thô, bất biến. Người viết vào đây, **agent KHÔNG bao giờ ghi** (rule R1).
- **`llmwiki/wiki/`** — trang tri thức agent bảo trì: concepts, entities, sources.
- **`llmwiki/AGENT.md`** + **`llmwiki/CLAUDE.md`** — schema + luật (đi kèm bản cài; KHÔNG viết tay đè).

# INSTRUCTIONS

**Trước khi làm gì:** chỉ các file `.md` sau được phép ở **gốc dự án**: `README.md`, `AGENT-business.md`, `AGENT-code.md`, và file đánh số (`00-*.md`, `01-*.md`…). Mọi tri thức khác phải nằm trong `llmwiki/wiki/` (rule R5).

Kiểm tra/khởi tạo các thao tác sau (đã có thì verify, thiếu thì tạo):

1. **Thư mục dưới `llmwiki/`** (đã có nếu cài overstack):
   - `llmwiki/skills/` — quy trình nhiều bước agent tự gọi (`propose`, `safe-change`…).
   - `llmwiki/raw/` — lớp nguồn bất biến: người bỏ tài liệu gốc (spec, note, paper, data). Agent chỉ ĐỌC khi `ingest`.
   - `llmwiki/html/` — lớp tài liệu trực quan (gồm `overstack.html`).

2. **`llmwiki/wiki/`** — lớp tri thức agent bảo trì. Chọn subfolder:

   | Subfolder | Đặt vào khi… | Ví dụ |
   |-----------|--------------|-------|
   | `concepts/` | Ý tưởng/pattern/thuật ngữ trừu tượng — giải thích cho người mới, không trỏ vào code | `rag.md`, `graph-memory.md` |
   | `entities/` | Thứ cụ thể có tên trong hệ thống — service, model, API, component, config | `auth-service.md`, `postgres.md` |
   | `sources/` | Tham chiếu/quyết định chưng cất từ `raw/` — tóm tắt URL, ADR, takeaway | `why-postgres.md`, `api-docs.md` |
   | `sources/draft/` | Đề xuất chưa làm (do skill `propose` tạo) | `260425-new-approval-button-fe.md` |

   **Mỗi file wiki phải theo OKF v0.1 — frontmatter YAML (rule R9), KHÔNG dùng `**Type:**` bold kiểu cũ:**
   ```
   ---
   type: concept            # concept | entity | source | draft
   title: <Title>
   tags: [tag1, tag2]
   timestamp: YYYY-MM-DD
   ---

   # <Title>

   <mô tả 1–3 câu>

   ## Notes
   <chi tiết, [[wikilinks]] tới trang liên quan>

   ## Origin
   - **Source:** `llmwiki/raw/<file>` | `llmwiki/wiki/sources/draft/<file>` | https://…
   - **Commit:** <hash> (nếu sinh từ một thay đổi code)
   - **Date:** YYYY-MM-DD
   ```
   File wiki thiếu `## Origin` bị coi là chưa hợp lệ (rule R2).

3. **`llmwiki/wiki/index.md`** — thêm/bớt file wiki phải cập nhật (rule R3; có thể tự sửa bằng `index_sync --fix`):
   ```
   # Wiki Index
   | File | Type | Summary |
   |------|------|---------|
   ```

4. **`llmwiki/wiki/log.md`** — append sau mỗi thao tác (nay có code-logger ghi giúp bằng code):
   ```
   # Operation Log
   ## YYYY-MM-DD — <init | ingest | query | lint> — <summary>
   ```
   Log lần khởi tạo hôm nay làm entry đầu.

5. **`llmwiki/AGENT.md` + `llmwiki/CLAUDE.md`** — KHÔNG viết tay. Hai file này đi kèm bản cài overstack, đã chứa đủ luật (R1–R12) + bảng skill. Chỉ cần xác nhận chúng tồn tại; thiếu → chạy lại bootstrap (PHA 0) hoặc `/harness-update`.

6. **Seed nội dung dự án:** tạo `llmwiki/wiki/sources/project-requirements.md` (đúng frontmatter + `## Origin`) tóm tắt câu trả lời PHA 1 (tên, bài toán, stack). Thêm row vào `index.md`, append `log.md`.

7. Quét gốc dự án tìm `.md` lạc (không phải `README.md`/`AGENT-*.md`/file đánh số): phân loại concept/entity/source, chuyển vào `llmwiki/wiki/` đúng subfolder, cập nhật index + log. Không có → bỏ qua.

# ACTION
Với mỗi thư mục/file ở trên:
- Chưa có → tạo đúng đặc tả.
- Đã có (vd từ bản cài) → verify đủ section + đúng frontmatter YAML. Thiếu/sai → chỉ sửa phần thiếu, KHÔNG đè nội dung hợp lệ.

Trả lời bằng checklist: mỗi mục ✅ (đã hợp lệ), 🔧 (tạo/sửa), hoặc ❌ (không tạo được — nêu lý do).
