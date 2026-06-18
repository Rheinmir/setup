# wiki/

Knowledge base do AI Agent duy trì. Mỗi file là một trang markdown mô tả một khái niệm, thực thể, hoặc nguồn tham khảo trong dự án.

## Cấu trúc

| Folder | Chứa gì | Ví dụ |
|--------|---------|-------|
| `concepts/` | Khái niệm trừu tượng, pattern, domain term | `rag.md`, `approval-flow.md` |
| `entities/` | Thứ tồn tại cụ thể trong hệ thống: service, API, component, tool | `auth-service.md`, `postgres.md` |
| `sources/` | Tài liệu tham khảo ngoài, ADR, quyết định kỹ thuật đã distill từ `raw/` | `why-postgres.md` |
| `sources/draft/` | Proposal chưa implement (do skill `propose` tạo) — tên file: `DDMMYY-feature-module.md` | `260425-new-approval-button-fe.md` |

## Quy tắc bắt buộc

- Mọi file đều phải có `## Origin` — truy được về nguồn gốc (raw file, commit, hoặc URL)
- Dùng `[[wikilinks]]` để liên kết giữa các trang
- Sau mỗi thao tác: cập nhật `index.md` và append vào `log.md`
- File không có Origin bị coi là chưa hoàn chỉnh và sẽ bị `lint` flag

## File hỗ trợ

- `index.md` — danh mục toàn bộ wiki, cập nhật mỗi khi thêm/xóa file
- `log.md` — lịch sử thao tác append-only: ingest, query, lint, init

## Template

Mỗi folder có `_template.md` — copy ra và điền vào khi tạo entry mới.
