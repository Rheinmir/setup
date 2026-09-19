# P03 — Pure transformation with validator (pattern)

Nguồn: PRD SWH v1.1 §26.3. Trạng thái: active · `limited_evidence`.

## WHAT
Chuyển dữ liệu có cấu trúc sang dạng khác theo mapping rõ, không cần model phán đoán ở core. Dùng cho JSON → CSV theo schema, render record → Markdown/HTML. Không hứa đúng nghĩa nghiệp vụ của input.

Invariants: giữ đủ ID/field bắt buộc · format tất định đã quy định · từ chối input hỏng · không gọi mạng ngầm.

## HOW
parse → schema check → áp mapping tường minh → kiểm output schema (round-trip khi mapping đảo ngược được) → trả bytes + hash.

- Encoding/newline/escaping là tham số có giới hạn; schema sai thì fail TRƯỚC khi ghi.
- Dùng P03 làm renderer component bên trong P01, không đẻ agent riêng.
- Positive: ký tự `|` được escape đúng trong bảng. Negative: input thiếu ID bắt buộc thì không sinh ID giả cho qua.

Template hiện thực: `templates/T02-pure-transform.md`.
