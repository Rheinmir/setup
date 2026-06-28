# Architecture Decision Records

> ADR ghi lại các quyết định kiến trúc quan trọng, lý do chọn giải pháp.

## Template
```markdown
# ADR-<số>: <Tiêu đề>

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
Vấn đề cần giải quyết, các ràng buộc.

## Decision
Giải pháp được chọn.

## Consequences
Tác động tích cực/tiêu cực.
```

## Vòng đời ADR (gate R13 — `decision_adr.py`)
- **Tạo (ép):** mọi quyết định `Type=architecture` trong `decisions.md` PHẢI trỏ một `ADR-N` (hoặc khai `(no-adr: <lý do>)`). Tạo qua `/docs-curate` (promote draft) hoặc viết tay theo Template trên.
- **Sửa (tự do):** edit nội dung/status ADR thoải mái — gate KHÔNG chặn sửa.
- **Xóa (chỉ khi bị đè):** muốn `git rm` một ADR thì nó phải đã bị ĐÈ — đặt `## Status: Superseded by ADR-M` ở bản cũ, **hoặc** ghi `supersedes ADR-N` ở bản mới, rồi mới xóa. Xóa ADR còn LIVE bị chặn (`adr-delete-guard`).
